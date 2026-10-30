
import sqlite3
from pathlib import Path

DATABASE = Path(__file__).resolve().parent / "aprovizionare.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS furnizori (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT NOT NULL,
            cui TEXT UNIQUE,
            email TEXT
        );

        CREATE TABLE IF NOT EXISTS produse (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            denumire TEXT NOT NULL,
            unitate_masura TEXT NOT NULL DEFAULT 'buc'
        );

        CREATE TABLE IF NOT EXISTS comenzi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            furnizor_id INTEGER NOT NULL,
            data_comanda TEXT NOT NULL,
            data_livrare TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'plasata',
            FOREIGN KEY (furnizor_id) REFERENCES furnizori(id)
        );

        CREATE TABLE IF NOT EXISTS pozitii_comanda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comanda_id INTEGER NOT NULL,
            produs_id INTEGER NOT NULL,
            cantitate REAL NOT NULL CHECK(cantitate > 0),
            pret_unitar REAL NOT NULL CHECK(pret_unitar >= 0),
            FOREIGN KEY (comanda_id) REFERENCES comenzi(id),
            FOREIGN KEY (produs_id) REFERENCES produse(id)
        );

        CREATE TABLE IF NOT EXISTS receptii (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comanda_id INTEGER,
            data_receptie TEXT NOT NULL,
            FOREIGN KEY (comanda_id) REFERENCES comenzi(id)
        );

        CREATE TABLE IF NOT EXISTS pozitii_receptie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receptie_id INTEGER NOT NULL,
            produs_id INTEGER NOT NULL,
            cantitate REAL NOT NULL CHECK(cantitate > 0),
            FOREIGN KEY (receptie_id) REFERENCES receptii(id),
            FOREIGN KEY (produs_id) REFERENCES produse(id)
        );

        CREATE TABLE IF NOT EXISTS facturi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            comanda_id INTEGER NOT NULL,
            numar TEXT NOT NULL,
            data_factura TEXT NOT NULL,
            moneda TEXT NOT NULL CHECK(moneda IN ('RON', 'EUR')),
            valoare REAL NOT NULL CHECK(valoare >= 0),
            status TEXT NOT NULL DEFAULT 'in_verificare',
            FOREIGN KEY (comanda_id) REFERENCES comenzi(id)
        );
        
CREATE TABLE IF NOT EXISTS utilizatori (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nume TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    parola_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (
        rol IN ('achizitii', 'depozit', 'contabilitate')
    ),
    activ INTEGER NOT NULL DEFAULT 1
);

      CREATE TABLE IF NOT EXISTS jurnal_activitate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilizator_id INTEGER,
    actiune TEXT NOT NULL,
    tip_obiect TEXT NOT NULL,
    obiect_id INTEGER,
    detalii TEXT,
    data_ora TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (utilizator_id) REFERENCES utilizatori(id)
); 

CREATE TABLE IF NOT EXISTS produse_necomandate (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comanda_id INTEGER,
    produs_id INTEGER NOT NULL,
    cantitate REAL NOT NULL CHECK(cantitate > 0),
    data_primire TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'in_verificare',
    observatii TEXT,
    FOREIGN KEY (comanda_id) REFERENCES comenzi(id),
    FOREIGN KEY (produs_id) REFERENCES produse(id)
);
 """)


if __name__ == "__main__":
    init_db()
    print("Baza de date a fost creata cu succes!")
