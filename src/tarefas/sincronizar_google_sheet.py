from src.servicos.google_sheets_servico import GoogleSheetsServico


def sincronizar(sheet_id_mes, sheet_id_controle):
    sheets = GoogleSheetsServico() 

    df_controle = sheets.ler_aba(sheet_id_controle, "Alunos")
    df_mes = sheets.ler_aba(sheet_id_mes, "Total")

    coluna = "Nome"

    set_controle = set(df_controle[coluna])
    set_mes = set(df_mes[coluna])

    adicionar = set_controle - set_mes
    remover = set_mes - set_controle

    # ➕ adicionar
    for aluno in adicionar:
        sheets.criar_aba(sheet_id_mes, aluno)
        sheets.adicionar_linha(sheet_id_mes, "Total", [aluno])

    # ❌ remover
    for aluno in remover:
        sheets.deletar_aba(sheet_id_mes, aluno)
        sheets.deletar_linha(sheet_id_mes, "Total", aluno)
