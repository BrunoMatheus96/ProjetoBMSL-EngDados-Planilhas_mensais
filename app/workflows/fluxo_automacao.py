from app.tarefas.baixar_arquivo import baixar_alunos
from app.tarefas.processar_excel import ler_arquivo_alunos

def run():
    print("🚀 Iniciando automação...")

    baixar_alunos()          # baixa do Google Drive
    ler_arquivo_alunos()     # lê o Excel

    print("Finalizado ✅")
