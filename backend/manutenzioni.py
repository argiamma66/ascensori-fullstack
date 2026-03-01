from fastapi import APIRouter
import sqlite3

router = APIRouter()


def get_db_connection():
    conn = sqlite3.connect("manutenzione.db")
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/manutenzioni")
def lista_manutenzioni():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, impianto, frequenza_mesi,
               ultima_esecuzione, prossima_scadenza,
               tecnico, attiva
        FROM manutenzioni_programmate
    """)

    rows = cur.fetchall()
    conn.close()

    manutenzioni = []
    for row in rows:
        manutenzioni.append({
            "id": row["id"],
            "impianto": row["impianto"],
            "frequenza_mesi": row["frequenza_mesi"],
            "ultima_esecuzione": row["ultima_esecuzione"],
            "prossima_scadenza": row["prossima_scadenza"],
            "tecnico": row["tecnico"],
            "attiva": bool(row["attiva"])
        })

    return {"manutenzioni": manutenzioni}