import time
import functools
import gspread


def retry_em_quota(tentativas=5, espera_inicial=10):
    """Reexecuta a função em caso de erro 429 (cota excedida),
    esperando um tempo crescente entre as tentativas."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for tentativa in range(tentativas):
                try:
                    return func(*args, **kwargs)
                except gspread.exceptions.APIError as e:
                    if "429" in str(e) or "Quota exceeded" in str(e):
                        espera = espera_inicial * (2**tentativa)
                        print(
                            f"    ⏳Cota excedida, aguardando {espera}s "
                            f"(tentativa {tentativa + 1}/{tentativas})"
                        )
                        time.sleep(espera)
                    else:
                        raise

            raise Exception(
                f"Falhou após {tentativas} tentativas por causa de cota excedida"
            )

        return wrapper

    return decorator