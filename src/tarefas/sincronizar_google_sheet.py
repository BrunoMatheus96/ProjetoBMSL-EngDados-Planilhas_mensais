from src.servicos.google_sheets_servico import GoogleSheetsServico


def sincronizar(sheet_id_mes, sheet_id_controle):
    try:
        sheets = GoogleSheetsServico()

        print("ID que estou usando:", sheet_id_mes)
        df_controle = sheets.ler_aba(sheet_id_controle, "Alunos")
        df_mes = sheets.ler_aba(sheet_id_mes, "Total")

        coluna = "Nome"
        
        set_controle = set(linha[coluna] for linha in df_controle if linha.get(coluna))

        set_mes = set(linha[coluna] for linha in df_mes if linha.get(coluna))

        adicionar = set_controle - set_mes
        remover = set_mes - set_controle

        # ➕Adicionar
        for aluno in adicionar:
            sheets.criar_aba(sheet_id_mes, aluno)
            sheets.adicionar_linha(sheet_id_mes, "Total", [aluno])

        # ❌Remover
        for aluno in remover:
            sheets.deletar_aba(sheet_id_mes, aluno)
            sheets.deletar_linha(sheet_id_mes, "Total", aluno)

    except Exception as e:
        print(f"Erro em sincronizar: {e}")