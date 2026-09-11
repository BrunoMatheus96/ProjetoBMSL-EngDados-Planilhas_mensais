from src.servicos.google_sheets_servico import GoogleSheetsServico


def sincronizar(sheet_id_mes, sheet_id_controle):
    try:

        if not sheet_id_mes or not sheet_id_controle:
            raise Exception(" ❌IDs inválidos na sincronização")

        sheets = GoogleSheetsServico()

        df_controle = sheets.ler_aba(sheet_id_controle, "Alunos")
        df_mes = sheets.ler_aba(sheet_id_mes, "Total")

        # cabeçalhos diferentes em cada planilha
        coluna_controle = "Nome"
        coluna_mes = "Alunos"

        set_controle = set(
            linha[coluna_controle]
            for linha in df_controle
            if linha.get(coluna_controle)
        )
        set_mes = set(linha[coluna_mes] for linha in df_mes if linha.get(coluna_mes))

        adicionar = set_controle - set_mes
        remover = set_mes - set_controle

        for aluno in adicionar:
            sheets.criar_aba(sheet_id_mes, aluno)
            sheets.adicionar_linha(sheet_id_mes, "Total", [aluno])

        for aluno in remover:
            sheets.deletar_aba(sheet_id_mes, aluno)
            sheets.deletar_linha(sheet_id_mes, "Total", aluno)

    except Exception as e:
        print(f"Erro em sincronizar: {e}")
