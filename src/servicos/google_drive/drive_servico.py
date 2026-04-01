"""
Aqui você usa o google drive e executa ações como:
- Upload
- Download
- Listar arquivos
"""

from googleapiclient.discovery import build
from src.servicos.google_drive.autenticacao import get_credenciais
from googleapiclient.http import MediaIoBaseDownload
import io


class GoogleDriveServico:

    def __init__(self):
        creds = get_credenciais()
        self.service = build("drive", "v3", credentials=creds)

    def listar_arquivos(self):
        results = (
            self.service.files()
            .list(pageSize=10, fields="files(id, name, createdTime, mimeType)")
            .execute()
        )

        return results.get("files", [])

    def download_arquivo(self, file_id, file_name):
        file = self.service.files().get(fileId=file_id, fields="mimeType").execute()
        mime_type = file["mimeType"]

        if "google-apps" in mime_type:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            request = self.service.files().get_media(fileId=file_id)

        fh = io.FileIO(file_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            done = downloader.next_chunk()

        print("Download concluído ✅")

    # Função para buscar pasta por nome + pai (Me dá o ID da pasta X dentro da pasta Y)
    def get_folder_id(self, nome_pasta, parent_id=None):
        query = f"name='{nome_pasta}' and mimeType='application/vnd.google-apps.folder'"

        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(q=query, fields="files(id, name)").execute()

        files = results.get("files", [])
        return files[0]["id"] if files else None
    
    def get_file_in_folder(self, nome, folder_id):
        results = self.service.files().list(
            q=f"name contains '{nome}' and '{folder_id}' in parents",
            fields="files(id, name)"
        ).execute()

        files = results.get("files", [])
        return files[0] if files else None

    def copiar_arquivo(self, file_id):
        copia = self.service.files().copy(
            fileId=file_id
        ).execute()

        return copia["id"]
    
    def renomear_arquivo(self, file_id, novo_nome):
        self.service.files().update(
            fileId=file_id,
            body={"name": novo_nome}
        ).execute()