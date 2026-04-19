from datetime import datetime
import locale

from src.tarefas.duplicar_planilha import duplicar_planilha_mes, navegar_no_drive


def listar_arquivos():
    try:
        pasta, files = navegar_no_drive()

        if not isinstance(files, list):
            raise Exception(f"files inválido: {type(files)}")

        files = [f for f in files if f.get("name")]

        files.sort(key=lambda x: x.get("createdTime", ""), reverse=True)

        try:
            locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
        except:
            pass

        mes_atual = datetime.today().strftime("%B").lower()

        for arq in files:
            nome = arq.get("name", "").strip().lower()

            if nome == mes_atual:
                sheet_mes_id = arq.get("id")
                break

        sheet_controle_id = "1ILmNbWWKHAWOg_hDpD-GTN8qAvuw0DDmbp-TxHT5AYI"

        if not sheet_mes_id:
            raise Exception(f" ❌Não encontrou planilha do mês: {mes_atual}")

        return sheet_mes_id, sheet_controle_id

    except Exception as e:
        raise Exception(f"Erro em listar_arquivos: {e}")
