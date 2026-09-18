import calendar
import gspread
from datetime import date, datetime

from src.utils.api_retry import retry_em_quota
from src.utils.dias_semana import dias_da_semana


class EditarDatasMixin:
    @retry_em_quota()
    def editar_datas(
        self, spreadsheet_id_mes, spreadsheet_id_controle, nome_aba, coluna_data
    ):
        try:
            if nome_aba.strip().lower() == "total":
                print("    📢Aba 'Total' não é alterada por editar_datas")
                return

            hoje = datetime.now()
            ano, mes = hoje.year, hoje.month

            # 1) pega o(s) dia(s)/valor/hora desse aluno na planilha de controle
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

            # 2) calcula as ocorrências reais do mês atual A PARTIR DE HOJE
            #    (dias que já passaram no mês não entram na agenda)
            agenda = []
            ultimo_dia_mes = calendar.monthrange(ano, mes)[1]

            for entrada in entradas_aluno:
                nome_dia = entrada.get("Dia", "").strip().lower()
                dia_semana = mapa_dias.get(nome_dia)

                if dia_semana is None:
                    print(
                        f"    ⚠️Dia '{entrada.get('Dia')}' não reconhecido para '{nome_aba}'"
                    )
                    continue

                for dia in range(hoje.day, ultimo_dia_mes + 1):
                    data = date(ano, mes, dia)
                    if data.weekday() == dia_semana:
                        agenda.append(
                            {
                                "data": data,
                                "valor": entrada.get("Valor", ""),
                                "hora": entrada.get("Hora", ""),
                            }
                        )

            # ordenar por data já intercala automaticamente quando há mais de um dia da semana
            agenda.sort(key=lambda item: item["data"])

            if not agenda:
                print(
                    f"    📢Nenhuma ocorrência encontrada para '{nome_aba}' em {mes:02d}/{ano}"
                )
                return

            # 3) localiza a aba e as colunas pelo cabeçalho (não por posição fixa)
            planilha = self.esperar_planilha(spreadsheet_id_mes)
            aba = planilha.worksheet(nome_aba)

            cabecalho = aba.row_values(1)
            col_status = (
                cabecalho.index("Status da aula")
                if "Status da aula" in cabecalho
                else None
            )
            col_valor = cabecalho.index("Valor") if "Valor" in cabecalho else None
            col_data = cabecalho.index(coluna_data)
            col_hora = cabecalho.index("Horarios") if "Horarios" in cabecalho else None

            # 4) descobre quantas linhas de aula existem hoje (para antes do "Total"/"Chave Pix")
            valores_col_data = aba.col_values(col_data + 1)[1:]  # ignora cabeçalho
            linhas_atuais = 0
            for valor in valores_col_data:
                if self._parece_data(valor):
                    linhas_atuais += 1
                else:
                    break

            # 5) ajusta só a diferença de linhas (nunca apaga tudo de uma vez —
            # isso quebraria a fórmula de SOMA da linha "Total", que perde a
            # referência quando o intervalo inteiro é esvaziado)
            quantidade_nova = len(agenda)

            if quantidade_nova > linhas_atuais:
                diferenca = quantidade_nova - linhas_atuais
                linha_insercao = 2 + linhas_atuais
                aba.insert_rows(
                    [["" for _ in cabecalho] for _ in range(diferenca)],
                    row=linha_insercao,
                )
            elif quantidade_nova < linhas_atuais:
                diferenca = linhas_atuais - quantidade_nova
                linha_inicio = 2 + quantidade_nova
                linha_fim = 2 + linhas_atuais - 1
                aba.delete_rows(linha_inicio, linha_fim)

            # 6) agora a aba tem exatamente `quantidade_nova` linhas de aula —
            # sobrescreve os valores de todas elas (sem tocar na estrutura de novo)
            atualizacoes = []
            for i, item in enumerate(agenda):
                linha = 2 + i

                if col_status is not None:
                    atualizacoes.append(
                        {
                            "range": gspread.utils.rowcol_to_a1(linha, col_status + 1),
                            "values": [["Pendente"]],
                        }
                    )
                if col_valor is not None:
                    atualizacoes.append(
                        {
                            "range": gspread.utils.rowcol_to_a1(linha, col_valor + 1),
                            "values": [[self._parse_valor_brl(item["valor"])]],
                        }
                    )
                atualizacoes.append(
                    {
                        "range": gspread.utils.rowcol_to_a1(linha, col_data + 1),
                        "values": [[item["data"].strftime("%d/%m/%Y")]],
                    }
                )
                if col_hora is not None:
                    atualizacoes.append(
                        {
                            "range": gspread.utils.rowcol_to_a1(linha, col_hora + 1),
                            "values": [[item["hora"]]],
                        }
                    )

            aba.batch_update(atualizacoes, value_input_option="USER_ENTERED")

            print(
                f"    ✅Datas de '{nome_aba}' recalculadas para {mes:02d}/{ano} "
                f"({len(agenda)} aula(s))"
            )

        except Exception as e:
            print(f"Erro ao editar datas de '{nome_aba}': {e}")

    def _parece_data(self, valor):
        try:
            datetime.strptime(valor.strip(), "%d/%m/%Y")
            return True
        except (ValueError, AttributeError):
            return False

    def _parse_valor_brl(self, valor):
        """Converte 'R$300,00' (texto vindo do get_all_values) em 300.0 (número),
        pra bater com a validação de coluna do tipo moeda no Sheets."""
        if not valor:
            return ""

        limpo = str(valor).replace("R$", "").strip()
        limpo = limpo.replace(".", "").replace(",", ".")

        try:
            return float(limpo)
        except ValueError:
            return valor  # não parece número, deixa como veio pra não travar tudo