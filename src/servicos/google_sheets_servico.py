import os

import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

class GoogleSheetsServico:

    def __init__(self):
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_file(
            os.getenv("GOOGLE_CREDENCIAIS"),
            scopes=scope
        )

        self.client = gspread.authorize(creds)

    def ler_aba(self, spreadsheet_id, aba_nome):
        sheet = self.client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(aba_nome)

        dados = worksheet.get_all_records()
        return pd.DataFrame(dados)

    def adicionar_linha(self, spreadsheet_id, aba_nome, linha):
        sheet = self.client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(aba_nome)

        worksheet.append_row(linha)

    def deletar_linha(self, spreadsheet_id, aba_nome, valor, coluna=1):
        sheet = self.client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(aba_nome)

        cell = worksheet.find(valor)
        worksheet.delete_rows(cell.row)

    def criar_aba(self, spreadsheet_id, nome_aba):
        sheet = self.client.open_by_key(spreadsheet_id)
        sheet.add_worksheet(title=nome_aba, rows="100", cols="20")

    def deletar_aba(self, spreadsheet_id, nome_aba):
        sheet = self.client.open_by_key(spreadsheet_id)
        worksheet = sheet.worksheet(nome_aba)
        sheet.del_worksheet(worksheet)