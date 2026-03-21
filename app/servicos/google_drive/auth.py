"""
Responsável por:
- Ler credentials.json
- Fazer login (OAuth)
- Gerar token.json
- Retornar credenciais válidas
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CREDENCIAIS = os.getenv("GOOGLE_CREDENTIALS")

SCOPES = ["https://www.googleapis.com/auth/drive"]


def get_credenciais():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_CREDENCIAIS, SCOPES)
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds
