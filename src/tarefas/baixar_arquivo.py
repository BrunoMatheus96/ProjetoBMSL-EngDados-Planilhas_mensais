from src.servicos.google_drive_servico import GoogleDriveServico


def baixar_alunos():
    try:
        drive = GoogleDriveServico()

        file_id = "1ILmNbWWKHAWOg_hDpD-GTN8qAvuw0DDmbp-TxHT5AYI"  # ID do Alunos.xlsm

        drive.download_arquivo(file_id, "Alunos.xlsm")
    except Exception as e:
        print(f"Erro no baixar_alunos.py em tarefas: {e}")
