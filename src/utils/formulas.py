import re

def referencia_aba(nome):
    """Formata o nome da aba como o Sheets exige dentro de uma fórmula
    (com aspas simples se tiver espaço ou caractere especial)."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", nome):
        return nome
    return f"'{nome}'"