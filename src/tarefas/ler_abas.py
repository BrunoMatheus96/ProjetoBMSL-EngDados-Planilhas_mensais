import time
from src.utils.api_retry import retry_em_quota


class LeituraAbaMixin:
    @retry_em_quota()
    def ler_aba(self, spreadsheet_id, nome_aba, tentativas=5):

        if not spreadsheet_id or not isinstance(spreadsheet_id, str):
            raise Exception(f" ❌spreadsheet_id inválido: {spreadsheet_id}")

        if len(spreadsheet_id) < 20:
            raise Exception(f" ❌ID suspeito: {spreadsheet_id}")

        # cache simples por execução: a mesma aba (ex: "Alunos" na planilha de
        # controle) é pedida de novo por vários alunos/funções na mesma
        # rodada, mas o conteúdo dela não muda durante a execução — então lê
        # uma vez só e reaproveita. Isso é o que estava estourando a quota de
        # leitura do Sheets (429).
        if not hasattr(self, "_cache_abas"):
            self._cache_abas = {}

        chave_cache = (spreadsheet_id, nome_aba.strip().lower())
        if chave_cache in self._cache_abas:
            return self._cache_abas[chave_cache]

        # reaproveita a planilha já aberta (evita um open_by_key extra a cada
        # chamada, que antes era feito aqui de novo mesmo com esperar_planilha
        # já tendo cacheado o objeto)
        planilha = self.esperar_planilha(spreadsheet_id)

        for tentativa in range(tentativas):
            try:
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
                    raise Exception(f"Aba '{nome_aba}' não encontrada")

                dados = aba.get_all_values()

                if not dados or len(dados) < 2:
                    resultado = []
                else:
                    header = dados[0]
                    linhas = dados[1:]
                    resultado = [
                        dict(zip(header, linha)) for linha in linhas if any(linha)
                    ]

                self._cache_abas[chave_cache] = resultado
                return resultado

            except Exception as e:
                print(f" 🔁Tentativa {tentativa+1} falhou: {e}")

                if "404" in str(e):
                    raise Exception(
                        f" ❌404: sem acesso ou ID errado: {spreadsheet_id}"
                    )

                time.sleep(2)

        raise Exception(" ❌Falhou após várias tentativas")
