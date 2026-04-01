import pandas as pd

def ler_arquivo_alunos():
    df = pd.read_excel("Alunos.xlsm")
    
    print(df.head())

    return df