import gspread
from datetime import datetime

from src.utils.api_retry import retry_em_quota


class AtualizarStatusMixin:
    """
    Marca como "Concluída" a(s) linha(s) da coluna 'Status da aula' cuja data
    seja EXATAMENTE hoje. Datas passadas e futuras não são tocadas.

    Não mexe em Data, Valor ou Horarios — só na coluna Status da aula, e só
    na(s) linha(s) de hoje.
    """

    @retry_em_quota()
    def marcar_concluida_hoje(self, spreadsheet_id_mes, nome_aba, coluna_data):
        try:
            if nome_aba.strip().lower() == "total":
                print("    📢Aba 'Total' não é alterada por marcar_concluida_hoje")
                return

            hoje = datetime.now().date()

            planilha = self.esperar_planilha(spreadsheet_id_mes)
            aba = planilha.worksheet(nome_aba)

            dados = aba.get_all_values()
            if not dados or len(dados) < 2:
                print(f"    📢Aba '{nome_aba}' vazia, nada para marcar")
                return

            cabecalho = dados[0]
            if "Status da aula" not in cabecalho or coluna_data not in cabecalho:
                print(
                    f"    ⚠️Colunas 'Status da aula'/'{coluna_data}' não encontradas em '{nome_aba}'"
                )
                return

            col_status = cabecalho.index("Status da aula")
            col_data = cabecalho.index(coluna_data)

            encontrou_aula_hoje = False
            status_hoje = None
            atualizacoes = []

            for i, linha in enumerate(dados[1:], start=2):
                data_str = linha[col_data] if len(linha) > col_data else ""

                if not self._parece_data(data_str):
                    break  # chegou nas linhas fixas do final (Total, Chave Pix etc.)

                data = datetime.strptime(data_str.strip(), "%d/%m/%Y").date()

                if data != hoje:
                    continue  # só mexe na linha de hoje — passado e futuro ficam intocados

                encontrou_aula_hoje = True
                status_atual = linha[col_status] if len(linha) > col_status else ""
                status_hoje = status_atual.strip().lower()

                if status_hoje == "pendente":
                    atualizacoes.append(
                        {
                            "range": gspread.utils.rowcol_to_a1(i, col_status + 1),
                            "values": [["Concluída"]],
                        }
                    )

            if atualizacoes:
                aba.batch_update(atualizacoes, value_input_option="USER_ENTERED")
                print(f"    ✅Status de hoje marcado como 'Concluída' em '{nome_aba}'")
            elif encontrou_aula_hoje:
                print(
                    f"    📢Na aba '{nome_aba}' a aula de hoje já não está mais 'Pendente' (está '{status_hoje}')"
                )
            else:
                print(f"    📢'{nome_aba}' não tem aula hoje")

        except Exception as e:
            print(f"Erro ao marcar status de hoje em '{nome_aba}': {e}")
