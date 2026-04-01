from app.tarefas import listar_arquivos
from app.tarefas.baixar_arquivo import baixar_alunos
from app.tarefas.duplicar_planilha import duplicar_mes
from app.tarefas.processar_excel import ler_arquivo_alunos
from app.tarefas.listar_arquivos import listar_arquivos
from app.tarefas.sincronizar_google_sheet import sincronizar


def run():
    print("🚀 Iniciando automação...")

    baixar_alunos()
    ler_arquivo_alunos()
    duplicar_mes()

    # 🔥 pega os IDs dinamicamente
    sheet_id_mes, sheet_id_controle = listar_arquivos()

    # 🔥 passa os IDs para a função
    sincronizar(sheet_id_mes, sheet_id_controle)

    print("Finalizado ✅")
