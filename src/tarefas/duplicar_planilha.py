from src.servicos.google_drive_servico import GoogleDriveServico
from datetime import datetime, timedelta
import locale


def navegar_ate_2026():
    try:
        drive = GoogleDriveServico()

        raiz = "root"  # Meu Drive

        freelas = drive.get_folder_id("Freelas", raiz)
        silvia = drive.get_folder_id("Silvia", freelas)
        controle = drive.get_folder_id("Controle interno", silvia)
        mes_ano = drive.get_folder_id("Mês/Ano", controle)
        pasta_2026 = drive.get_folder_id("2026", mes_ano)

        return pasta_2026
    except Exception as e:
        print(f"Erro em navegar_ate_2026 em duplicar_planilha.py: {e}")


def duplicar_planilha_mes():
    try:
        # Define idioma PT-BR
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

        drive = GoogleDriveServico()
        pasta_2026 = navegar_ate_2026()

        hoje = datetime.today()

        # Mês atual
        mes_atual = hoje.strftime("%B").capitalize()

        # Mês anterior
        primeiro_dia_mes = hoje.replace(day=1)
        ultimo_dia_mes_anterior = primeiro_dia_mes - timedelta(days=1)
        mes_anterior = ultimo_dia_mes_anterior.strftime("%B").capitalize()

        print(f" ➡️Mês anterior: {mes_anterior}")
        print(f" ➡️Mês atual: {mes_atual}")

        # Busca mês anterior
        arquivo_mes_anterior = drive.buscar_arquivo_na_pasta(mes_anterior, pasta_2026)

        # Busca mês atual
        arquivo_mes_atual = drive.buscar_arquivo_na_pasta(mes_atual, pasta_2026)

        if arquivo_mes_atual:
            print(f" 📢Arquivo do mês '{mes_atual}' já existe.")
            return arquivo_mes_atual["id"]  # 🔥 ESSENCIAL

        # Duplica
        novo_id = drive.copiar_arquivo(arquivo_mes_anterior["id"])

        # Renomeia com mês atual
        drive.renomear_arquivo(novo_id, mes_atual)

        print(" ✅Duplicado com sucesso")
        return novo_id
    except Exception as e:
        print(f"Erro em duplicar_mes em duplicar_planilha.py: {e}")
