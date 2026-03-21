from app.workflows.fluxo_automacao import run

def main():
    try:
        print("🚀 Iniciando projeto...")
        run()
    except Exception as e:
        print("Erro:", e)


if __name__ == "__main__":
    main()
