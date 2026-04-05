from src.servicos.google_drive_servico import GoogleDriveServico
from datetime import datetime
import locale


def listar_arquivos():
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

        drive = GoogleDriveServico()
        files = drive.listar_arquivos()

        # 🔥 garante ordenação segura
        files.sort(key=lambda x: x.get("createdTime") or "", reverse=True)

        mes_atual = datetime.today().strftime("%B").capitalize()

        sheet_mes_id = None
        sheet_controle_id = None

        for arq in files:
            nome = arq.get("name", "")

            if nome == mes_atual and sheet_mes_id is None:
                sheet_mes_id = arq.get("id")

            if nome == "Alunos":
                sheet_controle_id = arq.get("id")

        return sheet_mes_id, sheet_controle_id
    except Exception as e:
        print(f"Erro em listar_arquivos em listar_arquivos.py: {e}")
