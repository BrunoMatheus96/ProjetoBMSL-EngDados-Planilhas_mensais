from src.utils.api_retry import retry_em_quota

class DeletarAbaMixin:
    @retry_em_quota()
    def deletar_aba(self, spreadsheet_id, nome_aba):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            worksheets = planilha.worksheets()
 
            aba = next((ws for ws in worksheets if ws.title == nome_aba), None)
 
            if not aba:
                print(f"    📢Aba '{nome_aba}' não existe, nada para remover")
                return
 
            if len(worksheets) == 1:
                print(f"    ⚠️Não é possível remover '{nome_aba}': é a única aba da planilha")
                return
 
            planilha.del_worksheet(aba)
            print(f"    ✅Aba '{nome_aba}' removida")
 
        except Exception as e:
            print(f"Erro ao deletar aba: {e}")