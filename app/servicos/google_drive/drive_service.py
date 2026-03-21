"""
Aqui você usa o google drive e executa ações como:
- Upload
- Download
- Listar arquivos
"""

from googleapiclient.discovery import build
from app.servicos.google_drive.auth import get_credenciais

class GoogleDriveServico:

    def __init__(self):
        creds = get_credenciais()
        self.service = build("drive", "v3", credentials=creds)

    def listar_arquivos(self):
        results = self.service.files().list(
            pageSize=10,
            fields="files(id, name)"
        ).execute()

        return results.get("files", [])