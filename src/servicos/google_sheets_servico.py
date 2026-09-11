import os
import time
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from src.tarefas.adicionar_linhas import AdicionarLinhaMixin
from src.tarefas.atualizar_referencia import AtualizarReferenciaMixin
from src.tarefas.criar_aba import CriarAbaMixin
from src.tarefas.deletar_abas import DeletarAbaMixin
from src.tarefas.deletar_linha import DeletarLinhaMixin
from src.tarefas.ler_abas import LeituraAbaMixin


class GoogleSheetsServico(
    LeituraAbaMixin,
    CriarAbaMixin,
    AdicionarLinhaMixin,
    DeletarAbaMixin,
    DeletarLinhaMixin,
    AtualizarReferenciaMixin
):

    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        ROOT_DIR = os.path.dirname(BASE_DIR)

        JSON_DIR = os.path.join(ROOT_DIR, "autenticacoes", "arquivos_json")

        CREDENCIAIS_PATH = os.path.join(JSON_DIR, "google_sheets_credenciais.json")
        TOKEN_PATH = os.path.join(JSON_DIR, "token.json")

        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

        if not os.path.exists(CREDENCIAIS_PATH):
            raise Exception(f"Arquivo não encontrado: {CREDENCIAIS_PATH}")

        creds = None

        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENCIAIS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        self.client = gspread.authorize(creds)

    def esperar_planilha(self, spreadsheet_id):
        try:
            if not hasattr(self, "_cache"):
                self._cache = {}

            if spreadsheet_id in self._cache:
                return self._cache[spreadsheet_id]

            planilha = self.client.open_by_key(spreadsheet_id)
            self._cache[spreadsheet_id] = planilha

            return planilha

        except Exception as e:
            print(f" ⌛Erro ao acessar planilha: {e}")
            time.sleep(2)
