import os
import shutil
from datetime import datetime

# Percorso database
DB_NAME = "manutenzione.db"

# Cartella backup
BACKUP_DIR = "backup"

# Crea cartella backup se non esiste
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# Data e ora per il nome file
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Nome file backup
backup_filename = f"manutenzione_backup_{timestamp}.db"

# Percorso completo
source_path = DB_NAME
backup_path = os.path.join(BACKUP_DIR, backup_filename)

# Copia file
if os.path.exists(source_path):
    shutil.copy2(source_path, backup_path)
    print(f"Backup creato con successo: {backup_path}")
else:
    print("Database non trovato!")