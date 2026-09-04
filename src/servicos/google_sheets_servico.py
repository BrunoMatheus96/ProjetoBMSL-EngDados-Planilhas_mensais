import os
import time
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import re


class GoogleSheetsServico:

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ROOT_DIR = os.path.dirname(BASE_DIR)

        JSON_DIR = os.path.join(ROOT_DIR, "autenticacoes", "arquivos_json")

        CREDENCIAIS_PATH = os.path.join(JSON_DIR, "google_sheets_credenciais.json")
        TOKEN_PATH = os.path.join(JSON_DIR, "token.json")

        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        if not os.path.exists(CREDENCIAIS_PATH):
            raise Exception(f"Arquivo não encontrado: {CREDENCIAIS_PATH}")

        creds = None

        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENCIAIS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        self.client = gspread.authorize(creds)

    def esperar_planilha(self, spreadsheet_id):
        try:
            if not hasattr(self, "_cache"):
                self._cache = {}

            if spreadsheet_id in self._cache:
                return self._cache[spreadsheet_id]

            planilha = self.client.open_by_key(spreadsheet_id)
            self._cache[spreadsheet_id] = planilha

            return planilha

        except Exception as e:
            print(f" ⌛Erro ao acessar planilha: {e}")
            time.sleep(2)

    def ler_aba(self, spreadsheet_id, nome_aba, tentativas=5):

        if not spreadsheet_id or not isinstance(spreadsheet_id, str):
            raise Exception(f" ❌spreadsheet_id inválido: {spreadsheet_id}")

        if len(spreadsheet_id) < 20:
            raise Exception(f" ❌ID suspeito: {spreadsheet_id}")

        self.esperar_planilha(spreadsheet_id)

        for tentativa in range(tentativas):
            try:
                planilha = self.client.open_by_key(spreadsheet_id)

                abas = planilha.worksheets()

                nomes_abas = [a.title for a in abas]
                # print(" ➡️Abas encontradas:", nomes_abas)

                aba = next(
                    (
                        a
                        for a in abas
                        if a.title.strip().lower() == nome_aba.strip().lower()
                    ),
                    None,
                )

                if not aba:
                    raise Exception(f"Aba '{nome_aba}' não encontrada")

                dados = aba.get_all_values()

                if not dados or len(dados) < 2:
                    return []

                header = dados[0]
                linhas = dados[1:]

                return [dict(zip(header, linha)) for linha in linhas if any(linha)]

            except Exception as e:
                print(f" 🔁Tentativa {tentativa+1} falhou: {e}")

                if "404" in str(e):
                    raise Exception(
                        f" ❌404: sem acesso ou ID errado: {spreadsheet_id}"
                    )

                time.sleep(2)

        raise Exception(" ❌Falhou após várias tentativas")

    def adicionar_linha(
        self, spreadsheet_id, nome_aba, valores, linhas_fixas_no_final=1
    ):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            aba = planilha.worksheet(nome_aba)
            sheet_id = aba.id

            dados = aba.get_all_values()
            if dados:
                existentes = [linha[0] for linha in dados if linha]
                if valores[0] in existentes:
                    print(f"    📢Linha '{valores[0]}' já existe")
                    return

            nome_aluno = valores[0]
            ref = self._referencia_aba(nome_aluno)

            formula_total_a_receber = (
                f'=SOMA.SE({ref}!$A$2:$A$6;"Concluída";{ref}!$B$2:$B$6)'
                f'+SOMA.SE({ref}!$A$2:$A$6;"Pendente";{ref}!$B$2:$B$6)'
            )
            formula_vai_receber = (
                f'=SOMA.SE({ref}!$A$2:$A$6;"Pendente";{ref}!$B$2:$B$6)'
            )

            valores = list(valores)  # não mexe na lista original do chamador
            while len(valores) < 3:
                valores.append("")
            valores[1] = formula_total_a_receber
            valores[2] = formula_vai_receber

            meta = planilha.fetch_sheet_metadata(
                params={"fields": "sheets(properties(sheetId,title),tables)"}
            )
            sheet_meta = next(
                (s for s in meta["sheets"] if s["properties"]["sheetId"] == sheet_id),
                None,
            )
            tabelas = (sheet_meta or {}).get("tables", [])

            if not tabelas:
                print(
                    f"    ⚠️Nenhuma tabela nativa encontrada em '{nome_aba}', usando append_row normal"
                )
                aba.append_row(valores, value_input_option="USER_ENTERED")
                return

            tabela = tabelas[0]
            range_tabela = tabela["range"]
            end_row = range_tabela["endRowIndex"]
            start_col = range_tabela["startColumnIndex"]

            indice_insercao = end_row - linhas_fixas_no_final

            requests = [
                {
                    "insertDimension": {
                        "range": {
                            "sheetId": sheet_id,
                            "dimension": "ROWS",
                            "startIndex": indice_insercao,
                            "endIndex": indice_insercao + 1,
                        },
                        "inheritFromBefore": True,
                    }
                }
            ]

            planilha.batch_update({"requests": requests})

            linha_1_indexed = indice_insercao + 1
            col_letra = gspread.utils.rowcol_to_a1(1, start_col + 1)[:-1]
            a1_range = f"{col_letra}{linha_1_indexed}"

            aba.update(a1_range, [valores], value_input_option="USER_ENTERED")

            print(
                f"    ✅Linha '{valores[0]}' inserida antes da linha de total, com fórmulas de '{nome_aluno}'"
            )

        except Exception as e:
            print(f"Erro ao inserir linha antes do total: {e}")

    def _referencia_aba(self, nome):
        """Formata o nome da aba como o Sheets exige dentro de uma fórmula
        (com aspas simples se tiver espaço ou caractere especial)."""

        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
            return nome
        return f"'{nome}'"

    def atualizar_referencias_formula(self, spreadsheet_id, nome_aba, nome_antigo):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            aba = planilha.worksheet(nome_aba)

            formulas = aba.get(
                value_render_option="FORMULA"
            )  # <- usando .get() em vez de .get_values()

            # DEBUG temporário: mostra tudo que começa com "="
            for i, linha in enumerate(formulas, start=1):
                for j, valor in enumerate(linha, start=1):
                    if isinstance(valor, str) and valor.startswith("="):
                        print(
                            f"      [DEBUG] {gspread.utils.rowcol_to_a1(i, j)} -> {valor!r}"
                        )

            ref_nova = self._referencia_aba(nome_aba)
            padrao = re.compile(
                r"(?:'"
                + re.escape(nome_antigo)
                + r"'|"
                + re.escape(nome_antigo)
                + r")(?=[!\[])"
            )

            atualizacoes = []
            for i, linha in enumerate(formulas, start=1):
                for j, valor in enumerate(linha, start=1):
                    if (
                        isinstance(valor, str)
                        and valor.startswith("=")
                        and nome_antigo in valor
                    ):
                        novo_valor = padrao.sub(ref_nova, valor)
                        if novo_valor != valor:
                            atualizacoes.append(
                                {
                                    "range": gspread.utils.rowcol_to_a1(i, j),
                                    "values": [[novo_valor]],
                                }
                            )

            if atualizacoes:
                aba.batch_update(atualizacoes, value_input_option="USER_ENTERED")
                print(
                    f"    ✅{len(atualizacoes)} fórmula(s) atualizada(s) de '{nome_antigo}' para '{nome_aba}'"
                )
            else:
                print(
                    f"    📢Nenhuma fórmula com referência a '{nome_antigo}' encontrada"
                )

        except Exception as e:
            print(f"Erro ao atualizar referências de fórmula: {e}")

    def criar_aba(self, spreadsheet_id, nome_aba):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            worksheets = planilha.worksheets()

            for ws in worksheets:
                if ws.title == nome_aba:
                    print(f"    📢Aba '{nome_aba}' já existe")
                    return ws.id

            ultima_aba = worksheets[-1]
            nome_antigo = ultima_aba.title  # <- guarda o nome do modelo

            nova_aba = ultima_aba.duplicate(new_sheet_name=nome_aba)

            worksheets = planilha.worksheets()
            nova_ws = next(ws for ws in worksheets if ws.title == nome_aba)

            planilha.reorder_worksheets(
                worksheets_in_desired_order=[
                    ws for ws in worksheets if ws.title != nome_aba
                ]
                + [nova_ws]
            )

            print(f"    ✅Aba '{nome_aba}' criada e movida para última posição")

            # corrige as fórmulas que ainda referenciam a aba-modelo
            self.atualizar_referencias_formula(spreadsheet_id, nome_aba, nome_antigo)

            return nova_ws.id

        except Exception as e:
            print(f"Erro ao criar aba: {e}")
