import gspread
from datetime import datetime

from src.utils.api_retry import retry_em_quota
from src.utils.dias_semana import dias_da_semana


class VerificarValoresMixin:
    """
    Confere, aula a aula, se o Valor gravado na aba do aluno bate com o valor
    cadastrado na planilha de controle (por dia da semana) e corrige só a
    célula divergente.

    Só mexe em linhas com Status "Pendente" — aulas "Concluída" (ou qualquer
    outro status) nunca têm o Valor alterado, mesmo que esteja diferente.

    Diferente de `editar_datas`, essa função NUNCA mexe em Status, Data ou
    Hora — só na coluna Valor.

    Depende de `_parece_data` e `_parse_valor_brl`, já definidos em
    `EditarDatasMixin`. Se `GoogleSheetsServico` já herda esse mixin, os
    métodos ficam disponíveis via `self` automaticamente.
    """

    STATUS_VERIFICAVEL = "pendente"

    @retry_em_quota()
    def verificar_valores(
        self, spreadsheet_id_mes, spreadsheet_id_controle, nome_aba, coluna_data
    ):
        try:
            if nome_aba.strip().lower() == "total":
                print("    📢Aba 'Total' não é alterada por verificar_valores")
                return

            # 1) valor esperado por dia da semana, vindo da planilha de controle
            entradas = self.ler_aba(spreadsheet_id_controle, "Alunos")
            entradas_aluno = [
                e
                for e in entradas
                if e.get("Nome", "").strip().lower() == nome_aba.strip().lower()
            ]

            if not entradas_aluno:
                print(
                    f"    📢Aluno '{nome_aba}' não encontrado na planilha de controle"
                )
                return

            mapa_dias = dias_da_semana()

            valor_por_dia_semana = {}
            for entrada in entradas_aluno:
                nome_dia = entrada.get("Dia", "").strip().lower()
                dia_semana = mapa_dias.get(nome_dia)

                if dia_semana is None:
                    print(
                        f"    ⚠️Dia '{entrada.get('Dia')}' não reconhecido para '{nome_aba}'"
                    )
                    continue

                valor_por_dia_semana[dia_semana] = entrada.get("Valor", "")

            if not valor_por_dia_semana:
                print(
                    f"    📢Nenhum dia válido encontrado para '{nome_aba}' na planilha de controle"
                )
                return

            # 2) localiza a aba do aluno e as colunas pelo cabeçalho
            planilha = self.esperar_planilha(spreadsheet_id_mes)
            aba = planilha.worksheet(nome_aba)

            dados = aba.get_all_values()
            if not dados or len(dados) < 2:
                print(f"    📢Aba '{nome_aba}' vazia, nada para verificar")
                return

            cabecalho = dados[0]
            if "Valor" not in cabecalho or coluna_data not in cabecalho:
                print(
                    f"    ⚠️Colunas 'Valor'/'{coluna_data}' não encontradas em '{nome_aba}'"
                )
                return

            col_valor = cabecalho.index("Valor")
            col_data = cabecalho.index(coluna_data)
            col_status = (
                cabecalho.index("Status da aula")
                if "Status da aula" in cabecalho
                else None
            )

            # 3) percorre as linhas de aula (para antes de chegar em Total/Chave Pix)
            atualizacoes = []
            for i, linha in enumerate(dados[1:], start=2):
                data_str = linha[col_data] if len(linha) > col_data else ""

                if not self._parece_data(data_str):
                    break  # chegou nas linhas fixas do final

                # só corrige aulas ainda Pendentes — "Concluída" fica intocada
                if col_status is not None:
                    status_atual = (
                        linha[col_status].strip().lower()
                        if len(linha) > col_status
                        else ""
                    )
                    if status_atual != self.STATUS_VERIFICAVEL:
                        continue

                dia_semana = (
                    datetime.strptime(data_str.strip(), "%d/%m/%Y").date().weekday()
                )

                if dia_semana not in valor_por_dia_semana:
                    continue

                valor_esperado = self._parse_valor_brl(valor_por_dia_semana[dia_semana])
                valor_atual_bruto = linha[col_valor] if len(linha) > col_valor else ""
                valor_atual = self._parse_valor_brl(valor_atual_bruto)

                if valor_atual != valor_esperado and valor_esperado != "":
                    atualizacoes.append(
                        {
                            "range": gspread.utils.rowcol_to_a1(i, col_valor + 1),
                            "values": [[valor_esperado]],
                        }
                    )

            # 4) aplica só o que realmente mudou
            if atualizacoes:
                aba.batch_update(atualizacoes, value_input_option="USER_ENTERED")
                print(
                    f"    ✅{len(atualizacoes)} valor(es) corrigido(s) em '{nome_aba}'"
                )
            else:
                print(f"    📢Valores de '{nome_aba}' já estão corretos")

        except Exception as e:
            print(f"Erro ao verificar valores de '{nome_aba}': {e}")
