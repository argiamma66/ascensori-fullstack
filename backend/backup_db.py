import os
import zipfile
from datetime import datetime

DB_NAME = "manutenzione.db"

# Cartella chiavetta USB
USB_BACKUP_DIR = r"F:\BackupAscensori"

# Crea cartella sulla chiavetta se non esiste
if not os.path.exists(USB_BACKUP_DIR):
    os.makedirs(USB_BACKUP_DIR)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
zip_filename = f"manutenzione_backup_{timestamp}.zip"
zip_path = os.path.join(USB_BACKUP_DIR, zip_filename)

if os.path.exists(DB_NAME):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(DB_NAME)
    print(f"Backup ZIP creato su chiavetta: {zip_path}")
else:
    print("Database non trovato!")