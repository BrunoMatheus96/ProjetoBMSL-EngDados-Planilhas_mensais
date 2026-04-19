import pandas as pd


def processar_arquivo():
    try:
        df = pd.read_excel("Alunos.xlsm")

        df = df.dropna(how="all")  # Remove linhas completamente vazias
        df = df.dropna(axis=1, how="all")  # Remove colunas completamente vazias
        df = df.apply(
            lambda x: x.apply(lambda y: y.strip() if isinstance(y, str) else y)
        )

        return df
    except Exception as e:
        print(f"Erro em processar_arquivo em processar_excel.py: {e}")
