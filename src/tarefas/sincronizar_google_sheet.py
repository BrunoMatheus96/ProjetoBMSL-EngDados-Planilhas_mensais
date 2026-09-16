from src.servicos.google_sheets_servico import GoogleSheetsServico


def sincronizar(sheet_id_mes, sheet_id_controle, arquivo_novo=False):
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

        # se o arquivo do mês já existia, só mexe nas abas recém-criadas agora.
        # se o arquivo é novo, recalcula todo mundo (datas duplicadas ainda são do mês anterior)
        alunos_para_editar_datas = set_controle if arquivo_novo else adicionar

        for aluno in alunos_para_editar_datas:
            sheets.editar_datas(sheet_id_mes, sheet_id_controle, aluno, "Datas")

    except Exception as e:
        print(f"Erro em sincronizar: {e}")
