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
