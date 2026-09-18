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
        existentes = set_controle & set_mes  # alunos que já estavam no mês

        for aluno in adicionar:
            sheets.criar_aba(sheet_id_mes, aluno)
            sheets.adicionar_linha(sheet_id_mes, "Total", [aluno])

        for aluno in remover:
            sheets.deletar_aba(sheet_id_mes, aluno)
            sheets.deletar_linha(sheet_id_mes, "Total", aluno)

        # se o arquivo do mês já existia, só mexe nas abas recém-criadas agora.
        # se o arquivo é novo, recalcula todo mundo (datas duplicadas ainda são do mês anterior)
        # -> é aqui que a coluna Valor é preenchida para os alunos NOVOS
        alunos_para_editar_datas = set_controle if arquivo_novo else adicionar

        for aluno in alunos_para_editar_datas:
            sheets.editar_datas(sheet_id_mes, sheet_id_controle, aluno, "Datas")

        # alunos ANTIGOS (já existiam no mês e não passaram por editar_datas
        # agora) só têm a coluna Valor conferida e corrigida se estiver
        # diferente do cadastrado na planilha de controle. Isso não mexe em
        # Status/Data/Hora, então não afeta aulas já marcadas como Concluída.
        alunos_para_verificar_valor = existentes - alunos_para_editar_datas

        for aluno in alunos_para_verificar_valor:
            sheets.verificar_valores(sheet_id_mes, sheet_id_controle, aluno, "Datas")
            sheets.editar_horario(sheet_id_mes, sheet_id_controle, aluno, "Datas")

        print('\n')
        for aluno in set_controle:
            sheets.marcar_concluida_hoje(sheet_id_mes, aluno, "Datas")

    except Exception as e:
        print(f"Erro em sincronizar: {e}")
