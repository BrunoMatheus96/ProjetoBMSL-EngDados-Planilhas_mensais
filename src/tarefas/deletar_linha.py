class DeletarLinhaMixin:
    def deletar_linha(self, spreadsheet_id, nome_aba, valor, coluna_busca=0):
        try:
            planilha = self.client.open_by_key(spreadsheet_id)
            aba = planilha.worksheet(nome_aba)
 
            dados = aba.get_all_values()
 
            if not dados or len(dados) < 2:
                print(f"    📢Aba '{nome_aba}' vazia, nada para remover")
                return
 
            linhas = dados[1:]  # ignora cabeçalho
 
            indice_relativo = next(
                (
                    i
                    for i, linha in enumerate(linhas)
                    if len(linha) > coluna_busca and linha[coluna_busca] == valor
                ),
                None,
            )
 
            if indice_relativo is None:
                print(f"    📢Linha '{valor}' não encontrada em '{nome_aba}'")
                return
 
            # +1 pelo cabeçalho, +1 porque o Sheets é 1-indexed
            linha_na_planilha = indice_relativo + 2
 
            aba.delete_rows(linha_na_planilha)
            print(f"    ✅Linha '{valor}' removida de '{nome_aba}'")
 
        except Exception as e:
            print(f"Erro ao deletar linha: {e}")