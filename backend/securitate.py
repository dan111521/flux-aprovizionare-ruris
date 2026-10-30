
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def protejeaza_parola(parola: str) -> str:
    return password_hash.hash(parola)


def verifica_parola(parola: str, hash_salvat: str) -> bool:
    return password_hash.verify(parola, hash_salvat)
