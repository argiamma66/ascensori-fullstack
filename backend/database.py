import sqlite3

DB_NAME = "manutenzione.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, timeout=30, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn



def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # tabella chiamate
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chiamate (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ascensore TEXT,
        descrizione TEXT,
        stato TEXT,
        tecnico TEXT
    )
    """)

    # tabella utenti
    cur.execute("""
    CREATE TABLE IF NOT EXISTS utenti (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        ruolo TEXT
    )
    """)

    # utenti di default
    cur.execute(
        "INSERT OR IGNORE INTO utenti (username, password, ruolo) VALUES (?, ?, ?)",
        ("admin", "admin123", "admin")
    )

    cur.execute(
        "INSERT OR IGNORE INTO utenti (username, password, ruolo) VALUES (?, ?, ?)",
        ("mario", "mario123", "tecnico")
    )

    # tabella manutenzioni programmate
    cur.execute("""
    CREATE TABLE IF NOT EXISTS manutenzioni_programmate (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        impianto TEXT NOT NULL,
        frequenza_mesi INTEGER NOT NULL,
        ultima_esecuzione TEXT,
        prossima_scadenza TEXT,
        tecnico TEXT,
        attiva INTEGER DEFAULT 1
    )
    """)
    print("TEST TABELLE")


    conn.commit()
    conn.close()
