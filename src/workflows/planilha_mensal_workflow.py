from src.tarefas.duplicar_planilha import duplicar_planilha_mes
from src.tarefas.listar_arquivos import listar_arquivos
from src.tarefas.sincronizar_google_sheet import sincronizar


def workflow_automacao_mensal():
    try:
        print("▶️Iniciando automação...")
        print("⚫Duplicação")
        duplicar_planilha_mes()

        # Passa os IDs para a função
        print('\n⚫Validação e sincronização da planilhas')
        # Pega os IDs dinamicamente
        sheet_id_mes, sheet_id_controle = listar_arquivos()
        sincronizar(sheet_id_mes, sheet_id_controle)

        print("\n✅Finalizado")
    except Exception as e:
        print(f"Erro em no workflow planilha_mensal_workflow: {e}")
