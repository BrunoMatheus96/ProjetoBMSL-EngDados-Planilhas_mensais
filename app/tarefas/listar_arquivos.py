from app.servicos.google_drive.drive_service import GoogleDriveServico

def listar_arquivos():
    drive = GoogleDriveServico()
    files = drive.listar_arquivos()

    for f in files:
        print(f["name"])