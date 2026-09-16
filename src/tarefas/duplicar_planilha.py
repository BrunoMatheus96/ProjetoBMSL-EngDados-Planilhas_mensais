import time
import locale
from src.servicos.google_drive_servico import GoogleDriveServico
from datetime import datetime, timedelta
from src.tarefas.navegar_drive import navegar_no_drive


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

        print("    ⏳Validando existência da planilha do mês atual...")
        print(f"      ➡️Mês atual: {mes_atual}")

        if arquivo_mes_atual:
            print(f"    📢Arquivo do mês '{mes_atual}' já existe.")
            return arquivo_mes_atual["id"], False

        # 🔥 validação obrigatória
        if not arquivo_mes_anterior:
            raise Exception("    ❌Mês anterior não encontrado")

        # 🔥 duplicação
        novo_id = drive.copiar_arquivo(arquivo_mes_anterior["id"])
        drive.renomear_arquivo(novo_id, mes_atual)

        time.sleep(10)
        print("    ✅Duplicado com sucesso")

        return novo_id, True

    except Exception as e:
        print(f"Erro em duplicar_planilha_mes: {e}")
