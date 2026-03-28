print("CARICATO QUESTO MAIN")
from manutenzioni import router as manutenzioni_router
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
ESITI_VALIDI = [
    "risolto",
    "temporaneo",
    "serve_ricambio",
    "da_ritornare",
    "impianto_fermo"
]
import sqlite3
conn = sqlite3.connect("manutenzione.db")
cur = conn.cursor()


conn.commit()
conn.close()
from datetime import date
from dateutil.relativedelta import relativedelta
def get_db_connection():
    conn = sqlite3.connect("manutenzione.db")
    conn.row_factory = sqlite3.Row
    return conn
app = FastAPI()
app.include_router(manutenzioni_router)

class ManutenzioneCreate(BaseModel):
    impianto: str
    frequenza_mesi: int
    tecnico: str | None = None


@app.post("/manutenzioni")
def crea_manutenzione(data: ManutenzioneCreate):
    conn = sqlite3.connect("manutenzione.db")
    cur = conn.cursor()

    oggi = date.today()
    prossima = oggi + relativedelta(months=data.frequenza_mesi)

    cur.execute("""
        INSERT INTO manutenzioni_programmate
        (impianto, frequenza_mesi, ultima_esecuzione, prossima_scadenza, tecnico, attiva)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (
        data.impianto,
        data.frequenza_mesi,
        None,
        prossima.isoformat(),
        data.tecnico
    ))

    conn.commit()
    conn.close()

    return {"message": "Manutenzione programmata creata"}
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import init_db, get_connection

print("### BACKEND AVVIATO: main.py MODIFICATO ###")

# simulazione utente loggato (temporanea)
utente_corrente = {
    "username": "mario",
    "ruolo": "TECNICO"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# inizializza database
init_db()

# ---------------- HOME ----------------

@app.get("/")
def home():
    return {"messaggio": "Backend ascensori attivo 🚀"}

# ---------------- LOGIN ----------------

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/login")
def login(body: LoginRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, username, ruolo FROM utenti WHERE username=? AND password=?",
        (body.username, body.password)
    )

    user = cur.fetchone()
    conn.close()

    if not user:
        return {"ok": False}
    global utente_corrente
    utente_corrente = {
        "username": user[1],
        "ruolo": user[2]
    }

    return {
        "ok": True,
        "user": {
            "id": user[0],
            "username": user[1],
            "ruolo": user[2]
        }
    }
from fastapi import Header

class CreaUtenteRequest(BaseModel):
    username: str
    password: str
    ruolo: str  # "admin" o "tecnico"
from pydantic import BaseModel

class CreaImpiantoRequest(BaseModel):
    codice: str
    cliente: str
    indirizzo: str
    citta: str
    note: str | None = None

@app.post("/utenti")
def crea_utente(body: CreaUtenteRequest, x_admin_key: str = Header(default="")):
    # ✅ protezione semplice per pilot (poi faremo JWT)
    if x_admin_key != "giammarco-2026":
        return {"ok": False, "error": "Non autorizzato"}

    username = body.username.strip().lower()
    password = body.password.strip()
    ruolo = body.ruolo.strip().lower()

    if ruolo not in ["admin", "tecnico"]:
        return {"ok": False, "error": "Ruolo non valido"}

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO utenti (username, password, ruolo) VALUES (?, ?, ?)",
            (username, password, ruolo),
        )
        conn.commit()
    except Exception as e:
        conn.close()
        # spesso è username duplicato
        return {"ok": False, "error": "Username già esistente o errore DB"}

    conn.close()
    return {"ok": True}

# ---------------- CHIAMATE ----------------

@app.post("/chiamate")
def crea_chiamata(
    impianto_id: int =Query(...),
    descrizione: str = Query(...),
    priorita: str = Query("media")
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
    """
    INSERT INTO chiamate
    (impianto_id, descrizione, stato, tecnico,
     data_apertura, data_chiusura, priorita)
    VALUES (?, ?, ?, ?, datetime('now','localtime'), NULL, ?)
    """,
    (
        dati.impianto_id,
        dati.descrizione.strip(),
        "aperta",
        None,
        dati.priorita
    )
)

    conn.commit()
    conn.close()

    return {"ok": True}




@app.get("/chiamate")
def lista_chiamate():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT
      c.id,
      c.ascensore,
      c.descrizione,
      c.stato,
      c.tecnico,
      c.data_apertura,
      c.data_chiusura,
      c.impianto_id,
      c.note_tecnico,
      c.materiali,
      c.esito,
      c.priorita,
      i.codice,
      i.cliente,
      i.indirizzo,
      i.citta,
      i.note
    FROM chiamate c
    LEFT JOIN impianti i ON i.id = c.impianto_id
    ORDER BY c.data_apertura DESC
    """)

    rows = cur.fetchall()
    conn.close()

    chiamate = []
    for row in rows:
        chiamate.append({
            "id": row["id"],
            "descrizione": row["descrizione"],
            "stato": row["stato"],
            "tecnico": row["tecnico"],
            "data_apertura": row["data_apertura"],
            "data_chiusura": row["data_chiusura"],
            "impianto_id": row["impianto_id"],
            "note_tecnico": row["note_tecnico"],
            "materiali": row["materiali"],
            "esito": row["esito"],
            "priorita": row["priorita"],
            "impianto": {
                "codice": row["codice"],
                "cliente": row["cliente"],
                "indirizzo": row["indirizzo"],
                "citta": row["citta"],
                "note": row["note"],
            } if row["codice"] else None
        })

    return chiamate
# -----------------------------
# STORICO CHIAMATE PER IMPIANTO
# -----------------------------
@app.get("/impianti/{impianto_id}/chiamate")
def storico_impianto(impianto_id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            ascensore,
            descrizione,
            stato,
            tecnico,
            data_apertura,
            data_chiusura
        FROM chiamate
        WHERE impianto_id = ?
        ORDER BY id DESC
    """, (impianto_id,))

    rows = cur.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "ascensore": r[1],
            "descrizione": r[2],
            "stato": r[3],
            "tecnico": r[4],
            "data_apertura": r[5],
            "data_chiusura": r[6],
        })

    return result



@app.get("/impianti")
def lista_impianti():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, codice, cliente, indirizzo, citta, note, scheda_tecnica
        FROM impianti
        WHERE attivo = 1
        ORDER BY cliente
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "codice": r[1],
            "cliente": r[2],
            "indirizzo": r[3],
            "citta": r[4],
            "note": r[5],
            "scheda_tecnica": r[6],
        }
        for r in rows
    ]


    return {"manutenzioni": manutenzioni}
from datetime import date
from dateutil.relativedelta import relativedelta
@app.put("/chiamate/{chiamata_id}/prendi")
def prendi_chiamata(chiamata_id: int, tecnico: str = Query(...)):
    conn = get_db_connection()
    cur = conn.cursor()

    # Verifico che sia ancora aperta
    cur.execute("SELECT stato FROM chiamate WHERE id = ?", (chiamata_id,))
    result = cur.fetchone()

    if not result:
        conn.close()
        return {"errore": "Chiamata non trovata"}

    if result["stato"] != "aperta":
        conn.close()
        return {"errore": "Chiamata già presa"}

    # Aggiorno stato e tecnico
    cur.execute("""
        UPDATE chiamate
        SET tecnico = ?, stato = ?
        WHERE id = ?
    """, (tecnico.strip(), "in_intervento", chiamata_id))

    conn.commit()
    conn.close()

    return {"ok": True}
# ---------------- RILASCIA CHIAMATA ----------------

@app.put("/chiamate/{chiamata_id}/rilascia")
def rilascia_chiamata(chiamata_id: int, tecnico: str = Query(...)):

    conn = get_connection()
    cur = conn.cursor()

    # Verifica esistenza chiamata
    cur.execute(
        "SELECT tecnico, stato FROM chiamate WHERE id = ?",
        (chiamata_id,)
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return {"ok": False, "error": "Chiamata non trovata"}

    # Solo il tecnico assegnato può rilasciare
    if row[0] != tecnico:
        conn.close()
        return {"ok": False, "error": "Non sei il tecnico assegnato"}

    # Solo se in lavorazione
    if row[1] != "in lavorazione":
        conn.close()
        return {"ok": False, "error": "La chiamata non è in lavorazione"}

    # Ripristina stato
    cur.execute(
        """
        UPDATE chiamate
        SET stato = 'aperta',
            tecnico = NULL
        WHERE id = ?
        """,
        (chiamata_id,)
    )

    conn.commit()
    conn.close()

    return {"ok": True}

@app.post("/impianti")
def crea_impianto(body: CreaImpiantoRequest):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO impianti (codice, cliente, indirizzo, citta, note, attivo)
        VALUES (?, ?, ?, ?, ?, 1)
        """,
        (
            body.codice.strip(),
            body.cliente.strip(),
            body.indirizzo.strip(),
            body.citta.strip(),
            body.note.strip() if body.note else None,
        )
    )

    conn.commit()
    conn.close()

    return {"ok": True, "messaggio": "Impianto creato con successo"}

@app.put("/manutenzioni/{manutenzione_id}/esegui")
def esegui_manutenzione(manutenzione_id: int):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT frequenza_mesi
        FROM manutenzioni_programmate
        WHERE id = ?
    """, (manutenzione_id,))

    result = cur.fetchone()

    if not result:
        conn.close()
        return {"errore": "Manutenzione non trovata"}

    frequenza_mesi = result["frequenza_mesi"]

    from datetime import date
    from dateutil.relativedelta import relativedelta

    oggi = date.today()
    nuova_scadenza = oggi + relativedelta(months=frequenza_mesi)

    cur.execute("""
        UPDATE manutenzioni_programmate
        SET ultima_esecuzione = ?,
            prossima_scadenza = ?
        WHERE id = ?
    """, (
        oggi.isoformat(),
        nuova_scadenza.isoformat(),
        manutenzione_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Manutenzione registrata come eseguita"}
@app.get("/manutenzioni/in-scadenza")
def manutenzioni_in_scadenza(giorni: int = 30):

    from datetime import date, timedelta

    conn = sqlite3.connect("manutenzione.db")
    cur = conn.cursor()

    oggi = date.today()
    limite = oggi + timedelta(days=giorni)

    cur.execute("""
        SELECT id, impianto, prossima_scadenza, tecnico
        FROM manutenzioni_programmate
        WHERE attiva = 1
        AND prossima_scadenza IS NOT NULL
        AND date(prossima_scadenza) <= date(?)
    """, (limite.isoformat(),))

    rows = cur.fetchall()
    conn.close()

    risultati = []
    for row in rows:
        risultati.append({
            "id": row[0],
            "impianto": row[1],
            "prossima_scadenza": row[2],
            "tecnico": row[3]
        })

    return {"in_scadenza": risultati}






# ---------------- ASSEGNA TECNICO ----------------

class AssegnaTecnicoRequest(BaseModel):
    tecnico: str

@app.put("/chiamate/{chiamata_id}/assegna-tecnico")
def assegna_tecnico(chiamata_id: int, body: AssegnaTecnicoRequest):
    conn = get_connection()
    cur = conn.cursor()

    # controllo che l'utente sia un tecnico
    cur.execute(
        "SELECT ruolo FROM utenti WHERE username = ?",
        (body.tecnico,)
    )
    user = cur.fetchone()

    if not user or user[0] != "tecnico":
        conn.close()
        return {"ok": False, "error": "Solo un tecnico può prendere la chiamata"}

    # assegno la chiamata al tecnico
    cur.execute(
        "UPDATE chiamate SET tecnico = ?, stato = 'in lavorazione' WHERE id = ?",
        (body.tecnico, chiamata_id)
    )

    conn.commit()
    conn.close()

    return {"ok": True}




# ---------------- CHIUDI CHIAMATA ----------------

@app.put("/chiamate/{chiamata_id}/chiudi")
def chiudi_chiamata(
    chiamata_id: int,
    tecnico: str = Query(...),
    note_tecnico: str = Query(...),
    esito: str = Query(...),
    materiali: str = Query("")
):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT tecnico FROM chiamate WHERE id = ?",
        (chiamata_id,)
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return {"ok": False, "error": "Chiamata non trovata"}

    if row["tecnico"] != tecnico:
        conn.close()
        return {"ok": False, "error": "Non sei il tecnico assegnato"}
    if not note_tecnico or note_tecnico.strip() == "":
        conn.close()
        return {"ok": False, "error": "Descrizione intervento obbligatoria"}
    # Validazione esito
    if esito not in ESITI_VALIDI:
        conn.close()
        return {
            "ok": False,
            "error": f"Esito non valido. Valori ammessi: {ESITI_VALIDI}"
        }
    cur.execute(
        """
        UPDATE chiamate
        SET stato = 'chiusa',
            data_chiusura = datetime('now','localtime'),
            note_tecnico = ?,
            esito = ?,
            materiali = ?
        WHERE id = ?
        """,
    (note_tecnico.strip(), esito, materiali.strip(), chiamata_id)
    )

    conn.commit()
    conn.close()

    return {"ok": True}
from pydantic import BaseModel

class ChiamataCreate(BaseModel):
    impianto_id: int
    descrizione: str
    priorita: str = "media"


@app.post("/chiamate-da-impianto")
def crea_chiamata(dati: ChiamataCreate):
    print("PRIORITA ARRIVATA AL BACKEND:", dati.priorita)
    
    conn = get_connection()
    cur = conn.cursor()

    # Verifica impianto esiste ed è attivo
    cur.execute(
        "SELECT id FROM impianti WHERE id = ? AND attivo = 1",
        (dati.impianto_id,)
    )
    if not cur.fetchone():
        conn.close()
        return {"ok": False, "error": "Impianto non trovato o non attivo"}

    cur.execute(
    """
    INSERT INTO chiamate
    (impianto_id, descrizione, stato, tecnico, data_apertura, data_chiusura, priorita)
    VALUES (?, ?, ?, ?, datetime('now','localtime'), NULL, ?)
    """,
    (
        dati.impianto_id,
        dati.descrizione.strip(),
        "aperta",
        None,
        dati.priorita
    )
)

    conn.commit()
    conn.close()

    return {"ok": True}
# -----------------------------
# REPORT PDF PER CLIENTE
# -----------------------------
from fastapi.responses import FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import cm
import os
@app.get("/chiamate/{chiamata_id}/bolla-pdf")
def genera_bolla_pdf(chiamata_id: int):

    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT c.*, i.cliente, i.indirizzo, i.citta
        FROM chiamate c
        LEFT JOIN impianti i ON i.id = c.impianto_id
        WHERE c.id = ?
    """, (chiamata_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return {"ok": False, "error": "Chiamata non trovata"}

    # Nome file
    filename = f"bolla_chiamata_{chiamata_id}.pdf"
    filepath = os.path.join("bolle", filename)

    os.makedirs("bolle", exist_ok=True)

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>BOLLA DI LAVORAZIONE</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Cliente: {row['cliente']}", styles["Normal"]))
    elements.append(Paragraph(f"Indirizzo: {row['indirizzo']} - {row['citta']}", styles["Normal"]))
    elements.append(Paragraph(f"Tecnico: {row['tecnico']}", styles["Normal"]))
    elements.append(Paragraph(f"Data intervento: {row['data_chiusura']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Descrizione intervento:</b>", styles["Normal"]))
    elements.append(Paragraph(row["note_tecnico"] or "-", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("<b>Materiali utilizzati:</b>", styles["Normal"]))
    elements.append(Paragraph(row["materiali"] or "-", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"<b>Esito:</b> {row['esito']}", styles["Normal"]))
    elements.append(Spacer(1, 24))

    elements.append(Paragraph("Firma Cliente: ___________________________", styles["Normal"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Firma Tecnico: ___________________________", styles["Normal"]))

    doc.build(elements)

    return FileResponse(filepath, media_type="application/pdf", filename=filename)

@app.get("/clienti/{cliente}/report-pdf")
def report_pdf_cliente(cliente: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            i.codice,
            i.cliente,
            i.indirizzo,
            i.citta,
            c.id,
            c.descrizione,
            c.stato,
            c.tecnico,
            c.data_apertura,
            c.data_chiusura
        FROM chiamate c
        JOIN impianti i ON i.id = c.impianto_id
        WHERE i.cliente = ?
        ORDER BY c.id DESC
    """, (cliente,))

    rows = cur.fetchall()
    conn.close()

    if not rows:
        return {"errore": "Nessuna chiamata trovata per questo cliente"}

    file_path = f"report_{cliente.replace(' ', '_')}.pdf"

    doc = SimpleDocTemplate(
        file_path,
        pagesize=pagesizes.A4
    )

    elements = []

    title_style = ParagraphStyle(
        name='TitleStyle',
        fontSize=16,
        spaceAfter=10
    )

    elements.append(Paragraph(f"Report interventi - {cliente}", title_style))
    elements.append(Spacer(1, 0.5 * cm))

    data = [["ID", "Descrizione", "Stato", "Tecnico", "Apertura", "Chiusura"]]

    for r in rows:
        data.append([
            str(r[4]),
            r[5] or "",
            r[6] or "",
            r[7] or "",
            r[8] or "",
            r[9] or "",
        ])

    table = Table(data, repeatRows=1)
    table.setStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ])

    elements.append(table)

    doc.build(elements)

    return FileResponse(file_path, filename=file_path, media_type='application/pdf')
@app.put("/impianti/{impianto_id}/scheda")
def aggiorna_scheda_tecnica(impianto_id: int, scheda_tecnica: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE impianti SET scheda_tecnica = ? WHERE id = ?",
        (scheda_tecnica, impianto_id)
    )

    conn.commit()
    conn.close()

    return {"ok": True}
