import gspread
import re
from src.utils.formulas import referencia_aba
from src.utils.api_retry import retry_em_quota


class AtualizarReferenciaMixin:
    @retry_em_quota()
    def atualizar_referencias_formula(self, spreadsheet_id, nome_aba, nome_antigo):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            aba = planilha.worksheet(nome_aba)

            formulas = aba.get(value_render_option="FORMULA")

            for i, linha in enumerate(formulas, start=1):
                for j, valor in enumerate(linha, start=1):
                    if isinstance(valor, str) and valor.startswith("="):
                        print(
                            f"      [DEBUG] {gspread.utils.rowcol_to_a1(i, j)} -> {valor!r}"
                        )

            ref_nova = referencia_aba(nome_aba)
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
