from src.servicos.google_drive.drive_servico import GoogleDriveServico


def baixar_alunos():
    drive = GoogleDriveServico()

    file_id = "1ILmNbWWKHAWOg_hDpD-GTN8qAvuw0DDmbp-TxHT5AYI"  # ID do Alunos.xlsm

    drive.download_arquivo(file_id, "Alunos.xlsm")