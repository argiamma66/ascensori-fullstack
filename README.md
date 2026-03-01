# Ascensori Fullstack App

Applicazione gestionale per manutenzione ascensori.

---

## 📦 Struttura progetto

```
ascensori-fullstack
│
├── backend/   → FastAPI (API + database SQLite)
└── frontend/  → React (interfaccia utente)
```

---

## 🚀 Avvio Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend disponibile su:  
http://127.0.0.1:8000/docs

---

## 🌐 Avvio Frontend

```bash
cd frontend
npm install
npm start
```

Frontend disponibile su:  
http://localhost:3000

---

## 🔒 Note importanti

- NON caricare il database su GitHub
- NON caricare venv
- NON caricare node_modules

---

## 👨‍💻 Tecnologie utilizzate

- FastAPI
- SQLite
- React
- Git & GitHub