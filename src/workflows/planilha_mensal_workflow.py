from src.tarefas import listar_arquivos
from src.tarefas.baixar_arquivo import baixar_arquivo_principal
from src.tarefas.duplicar_planilha import duplicar_planilha_mes
from src.tarefas.processar_excel import processar_arquivo
from src.tarefas.listar_arquivos import listar_arquivos
from src.tarefas.sincronizar_google_sheet import sincronizar


def rodar_automacao_mensal():
    try:
        print("Iniciando automação...")

        print('⚫Download de Alunos.xlsm')
        baixar_arquivo_principal()
        processar_arquivo()

        print("\n⚫Validação")
        duplicar_planilha_mes()

        # Pega os IDs dinamicamente
        sheet_id_mes, sheet_id_controle = listar_arquivos()

        # Passa os IDs para a função
        print('\n⚫Validação e sincronizando planilhas')
        sincronizar(sheet_id_mes, sheet_id_controle)

        print("\n✅Finalizado")
    except Exception as e:
        print(f"Erro em no workflow planilha_mensal_workflow: {e}")
