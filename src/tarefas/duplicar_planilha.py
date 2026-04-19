import time

from src.servicos.google_drive_servico import GoogleDriveServico
from datetime import datetime, timedelta
import locale


def navegar_no_drive():
    try:
        drive = GoogleDriveServico()

        raiz = "root"

        freelas = drive.get_folder_id("Freelas", raiz)
        silvia = drive.get_folder_id("Silvia", freelas)
        controle = drive.get_folder_id("Controle interno", silvia)
        mes_ano = drive.get_folder_id("Mês/Ano", controle)
        pasta = drive.get_folder_id("2026", mes_ano)

        if not pasta:
            raise Exception("Pasta 2026 não encontrada")

        files = drive.listar_arquivos()

        if not isinstance(files, list):
            raise Exception(f"files inválido: {type(files)}")

        return pasta, files
    except Exception as e:
        print(f"Erro em navegar_no_drive em duplicar_planilha.py: {e}")


def duplicar_planilha_mes():
    try:
        locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

        drive = GoogleDriveServico()

        # 🔥 pega dados do drive corretamente
        pasta, files = navegar_no_drive()

        files = list(files)
        files.sort(key=lambda x: x.get("createdTime", ""), reverse=True)

        # 🔥 primeiro calcula datas (OBRIGATÓRIO vir antes de usar)
        hoje = datetime.today()

        mes_atual = hoje.strftime("%B").capitalize()

        primeiro_dia = hoje.replace(day=1)
        mes_anterior = (primeiro_dia - timedelta(days=1)).strftime("%B").capitalize()

        # 🔥 busca arquivos depois de definir variáveis
        arquivo_mes_anterior = drive.buscar_arquivo_na_pasta(mes_anterior, pasta)
        arquivo_mes_atual = drive.buscar_arquivo_na_pasta(mes_atual, pasta)

        print(" ⏳Validando existência da planilha do mês atual...")
        print(f"    ➡️Mês atual: {mes_atual}")

        if arquivo_mes_atual:
            print(f" 📢Arquivo do mês '{mes_atual}' já existe.")
            return arquivo_mes_atual["id"]

        # 🔥 validação obrigatória
        if not arquivo_mes_anterior:
            raise Exception("❌ Mês anterior não encontrado")

        # 🔥 duplicação
        novo_id = drive.copiar_arquivo(arquivo_mes_anterior["id"])
        drive.renomear_arquivo(novo_id, mes_atual)

        time.sleep(10)
        print(" ✅Duplicado com sucesso")

        return novo_id

    except Exception as e:
        print(f"Erro em duplicar_planilha_mes: {e}")
