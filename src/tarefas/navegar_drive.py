from src.servicos.google_drive_servico import GoogleDriveServico

def navegar_no_drive():
    try:
        drive = GoogleDriveServico()

        raiz = "root"

        freelas = drive.get_folder_id("Freelas", raiz)
        silvia = drive.get_folder_id("Silvia", freelas)
        controle = drive.get_folder_id("Controle interno", silvia)
        mes_ano = drive.get_folder_id("Mês/Ano", controle)
        pasta = drive.get_folder_id("2026", mes_ano)

        if not pasta:
            raise Exception("Pasta 2026 não encontrada")

        files = drive.listar_arquivos()

        if not isinstance(files, list):
            raise Exception(f"files inválido: {type(files)}")

        return pasta, files
    except Exception as e:
        print(f"Erro em navegar_no_drive em duplicar_planilha.py: {e}")