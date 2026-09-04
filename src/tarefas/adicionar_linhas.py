import gspread

def adicionar_linha(self, spreadsheet_id, nome_aba, valores, linhas_fixas_no_final=1):
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
        ref = self.referencia_aba(nome_aluno)

        formula_total_a_receber = (
            f'=SOMA.SE({ref}!$A$2:$A$6;"Concluída";{ref}!$B$2:$B$6)'
            f'+SOMA.SE({ref}!$A$2:$A$6;"Pendente";{ref}!$B$2:$B$6)'
        )
        formula_vai_receber = f'=SOMA.SE({ref}!$A$2:$A$6;"Pendente";{ref}!$B$2:$B$6)'

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
