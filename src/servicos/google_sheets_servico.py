import os
import time
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class GoogleSheetsServico:

    def __init__(self):
        try:
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

            # 🔹 Carrega token
            if os.path.exists(TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

            # 🔹 Se inválido, autentica
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENCIAIS_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)

                with open(TOKEN_PATH, "w") as token:
                    token.write(creds.to_json())

            # 🔹 cria client do gspread usando OAuth
            self.client = gspread.authorize(creds)

        except Exception as e:
            print(f"Erro no __init__ em google_sheets_servico.py: {e}")

    def ler_aba(self, spreadsheet_id, nome_aba, tentativas=5):
        if not spreadsheet_id:
            raise Exception("❌ spreadsheet_id inválido")

        for tentativa in range(tentativas):
            try:
                print(f"🔍 Tentando acessar planilha: {spreadsheet_id}")

                planilha = self.client.open_by_key(spreadsheet_id)

                abas = planilha.worksheets()

                aba = next(
                    (
                        a
                        for a in abas
                        if a.title.strip().lower() == nome_aba.strip().lower()
                    ),
                    None,
                )

                if not aba:
                    print(f"⚠️ Aba '{nome_aba}' não encontrada")
                    return []

                dados = aba.get_all_values()

                if not dados or len(dados) < 2:
                    return []

                header = dados[0]
                linhas = dados[1:]

                return [dict(zip(header, linha)) for linha in linhas if any(linha)]

            except Exception as e:
                print(f"🔁 Tentativa {tentativa+1} falhou: {e}")

                # Se for 404, provavelmente ID errado → não adianta retry infinito
                if "404" in str(e):
                    raise Exception(
                        f"❌ ERRO 404: Planilha não encontrada ou sem acesso. ID usado: {spreadsheet_id}"
                    )

                time.sleep(2)

        raise Exception("❌ Falhou após várias tentativas")

    def criar_aba(self, spreadsheet_id, nome_aba):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)

            try:
                planilha.worksheet(nome_aba)
                print(f"Aba '{nome_aba}' já existe")
            except:
                planilha.add_worksheet(title=nome_aba, rows="100", cols="20")
                print(f"✅ Aba '{nome_aba}' criada")

        except Exception as e:
            print(f"Erro ao criar aba: {e}")

    def deletar_aba(self, spreadsheet_id, nome_aba):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            aba = planilha.worksheet(nome_aba)
            planilha.del_worksheet(aba)

            print(f"🗑️ Aba '{nome_aba}' deletada")

        except Exception as e:
            print(f"Erro ao deletar aba: {e}")

    def adicionar_linha(self, spreadsheet_id, nome_aba, valores):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            aba = planilha.worksheet(nome_aba)

            aba.append_row(valores)

        except Exception as e:
            print(f"Erro ao adicionar linha: {e}")

    def deletar_linha(self, spreadsheet_id, nome_aba, valor_nome):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            aba = planilha.worksheet(nome_aba)

            dados = aba.get_all_values()

            for i, linha in enumerate(dados):
                if linha and linha[0] == valor_nome:
                    aba.delete_rows(i + 1)
                    print(f"🗑️ Linha '{valor_nome}' removida")
                    break

        except Exception as e:
            print(f"Erro ao deletar linha: {e}")

    def esperar_planilha(sheets, spreadsheet_id, tentativas=5):
        for i in range(tentativas):
            try:
                planilha = sheets.client.open_by_key(spreadsheet_id)
                planilha.worksheets()
                return
            except:
                time.sleep(2)
        raise Exception("Planilha não ficou disponível a tempo")
