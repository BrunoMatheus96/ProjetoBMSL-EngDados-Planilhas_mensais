import time
from src.utils.api_retry import retry_em_quota

class LeituraAbaMixin:
    @retry_em_quota()
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
                    raise Exception(f" ❌404: sem acesso ou ID errado: {spreadsheet_id}")

                time.sleep(2)

        raise Exception(" ❌Falhou após várias tentativas")
