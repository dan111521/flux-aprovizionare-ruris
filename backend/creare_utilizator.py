
import getpass
import sqlite3

from .database import get_connection, init_db
from .securitate import protejeaza_parola


def creare_utilizator():
    init_db()

    nume = input("Nume angajat: ").strip()
    username = input("Username: ").strip()
    rol = input("Rol (achizitii/depozit/contabilitate): ").strip().lower()
    parola = getpass.getpass("Parola: ")

    if not nume or not username:
        print("Numele si username-ul sunt obligatorii.")
        return

    if rol not in ("achizitii", "depozit", "contabilitate"):
        print("Rol invalid.")
        return

    if len(parola) < 12:
        print("Parola trebuie sa aiba minimum 12 caractere.")
        return

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO utilizatori
                (nume, username, parola_hash, rol)
                VALUES (?, ?, ?, ?)
                """,
                (nume, username, protejeaza_parola(parola), rol)
            )
    except sqlite3.IntegrityError:
        print("Username-ul exista deja.")
        return

    print("Utilizator creat cu succes!")


if __name__ == "__main__":
    creare_utilizator()
