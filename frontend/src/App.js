import React, { useEffect, useState } from "react";

function App() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState(null);
  const [loginError, setLoginError] = useState(false);
  
  const [chiamate, setChiamate] = useState([]);
  const [soloAperte, setSoloAperte] = useState(false);
  const [soloMie, setSoloMie] = useState(false);
  const [cercaAscensore, setCercaAscensore] = useState("");
  const [impiantoSelezionato, setImpiantoSelezionato] = useState(null);
  const [storico, setStorico] = useState([]);
  const [storicoImpianto, setStoricoImpianto] = useState([]);
  const [impianti, setImpianti] = useState([]);
  const [impiantoId, setImpiantoId] = useState("");
  const [descrGuasto, setDescrGuasto] = useState("");
  const [nuovoImpiantoId, setNuovoImpiantoId] = useState(null);
  const [mostraStorico, setMostraStorico] = useState(false);


  

  const [newUsername, setNewUsername] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRuolo, setNewRuolo] = useState("tecnico");
  const [userMsg, setUserMsg] = useState("");
  const [nuovoAscensore, setNuovoAscensore] = useState("");
  const [nuovaDescrizione, setNuovaDescrizione] = useState("");
  const [msgChiamata, setMsgChiamata] = useState("");
  const [mostraChiuse, setMostraChiuse] = useState(false);
  const [debugImpiantiCalls, setDebugImpiantiCalls] = useState(0);

  
  
  // ✅ Ripristina utente da localStorage al primo caricamento (F5 non ti “sloga”)
  useEffect(() => {
  if (!user) return;

  // carica subito
  caricaChiamate();
  caricaImpianti();

  // poi ogni 10 secondi (solo chiamate)
  const timer = setInterval(() => {
    caricaChiamate();
  }, 10000);

  return () => clearInterval(timer);
}, [user]);


  function login() {
    fetch("/login", {


      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username.trim().toLowerCase(), password: password.trim() }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.ok) {
          setUser(data.user);
          localStorage.setItem("user", JSON.stringify(data.user));
          setLoginError(false);
        } else {
          setUser(null);
          localStorage.removeItem("user");
          setLoginError(true);
        }
      })
      .catch(() => {
        setLoginError(true);
      });
  }
function creaUtente() {
  setUserMsg("");

  fetch("/utenti", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Admin-Key": "giammarco-2026", // <-- deve combaciare col backend
    },
    body: JSON.stringify({
      username: newUsername.trim(),
      password: newPassword.trim(),
      ruolo: newRuolo,
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.ok) {
        setUserMsg("✅ Utente creato!");
        setNewUsername("");
        setNewPassword("");
        setNewRuolo("tecnico");
      } else {
        setUserMsg("❌ " + (data.error || "Errore"));
      }
    })
    .catch(() => setUserMsg("❌ Errore di rete"));
}

  function logout() {
    localStorage.removeItem("user");
    setUser(null);
    setUsername("");
    setPassword("");
    setChiamate([]);
    setLoginError(false);
  }

  function caricaChiamate() {
    fetch("/chiamate")
      .then((res) => res.json())
      .then((data) => setChiamate(data))
      .catch(() => setChiamate([]));
  }
  function creaChiamataDaImpianto() {
  setMsgChiamata("");

  if (!impiantoId) {
    setMsgChiamata("Seleziona un impianto");
    return;
  }
  if (!descrGuasto.trim()) {
    setMsgChiamata("Inserisci una descrizione del guasto");
    return;
  }

  fetch("http://127.0.0.1:8000/chiamate-da-impianto", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      impianto_id: Number(impiantoId),
      descrizione: descrGuasto.trim(),
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (!data.ok) {
        setMsgChiamata(data.error || "Errore");
        return;
      }
      setMsgChiamata("✅ Chiamata creata");
      setImpiantoId("");
      setDescrGuasto("");
      caricaChiamate();
    })
    .catch(() => setMsgChiamata("Errore di rete"));
}


 function caricaImpianti() {
  fetch("http://127.0.0.1:8000/impianti")
    .then((res) => res.json())
    .then((data) => setImpianti(data))
    .catch(() => setImpianti([]));
}

 function caricaStoricoImpianto(id) {
  fetch(`http://127.0.0.1:8000/impianti/${id}/chiamate`)
    .then((res) => res.json())
    .then((data) => {
      setStoricoImpianto(data);
      setImpiantoSelezionato(id);
      setMostraStorico(true);   // 👈 MOSTRA POPUP
    })
    .catch(() => alert("Errore fetch storico"));
}
 function scaricaPdfImpianto(id) {
   window.open(`http://127.0.0.1:8000/impianti/${id}/report-pdf`, "_blank");
 }

  function creaChiamata() {
  // Se non selezionato impianto o descrizione vuota, non fare nulla
  if (!nuovoImpiantoId || !nuovaDescrizione.trim()) return;

  fetch("http://127.0.0.1:8000/chiamate-da-impianto", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      impianto_id: nuovoImpiantoId,
      descrizione: nuovaDescrizione.trim(),
    }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (!data.ok) {
        alert(data.error || "Errore creazione chiamata");
        return;
      }

      // reset campi
      setNuovoImpiantoId(null);
      setNuovaDescrizione("");

      // ricarica lista
      caricaChiamate();
    })
    .catch(() => {
      alert("Errore di rete");
    });
}



 





  // ✅ Il tecnico che prende la chiamata è SEMPRE l’utente loggato
  function prendiChiamata(id) {
    if (!user) return;

    fetch(`/chiamate/${id}/assegna-tecnico`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tecnico: user.username }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (!data.ok) {
          alert(data.error || "Errore durante la presa in carico");
          return;
        }
        caricaChiamate();
      })
      .catch(() => alert("Errore di rete"));
  }

  // ✅ Il backend vuole: /chiudi?tecnico=<username>
  function chiudiChiamata(id) {
    if (!user) return;
    if (!window.confirm("Confermi di chiudere questa chiamata?")) return;

    fetch(
  `/chiamate/${id}/chiudi?tecnico=${encodeURIComponent(user.username)}`,
  { method: "PUT" }
)
      .then((res) => res.json())
      .then((data) => {
        if (!data.ok) {
          alert(data.error || "Errore durante la chiusura");
          return;
        }
        caricaChiamate();
      })
      .catch(() => alert("Errore di rete"));
  }
  const short = (s) => (s ? s.slice(0, 16) : "-");
  const statusRank = (stato) => {
    if (stato === "aperta") return 0;
    if (stato === "in lavorazione") return 1;
    if (stato === "chiusa") return 2;
    return 9;
};

const dtKey = (s) => (s ? s.replace(" ", "T") : "");
const chiamateVisibili = chiamate
  .filter((c) => (soloAperte ? c.stato === "aperta" : true))
  .filter((c) =>
    user?.ruolo === "tecnico"
      ? (mostraChiuse ? true : c.stato !== "chiusa")
      : true
  )
  .filter((c) => (soloMie ? c.tecnico === user?.username : true))
  .filter((c) => {
    const q = cercaAscensore.trim().toLowerCase();
    if (!q) return true;
    return (c.ascensore || "").toLowerCase().includes(q);
  })
  .sort((a, b) => {
  // 1) stato: aperta -> in lavorazione -> chiusa
  const ra = statusRank(a.stato);
  const rb = statusRank(b.stato);
  if (ra !== rb) return ra - rb;

  // 2) più recente prima (data apertura)
  const da = dtKey(a.data_apertura);
  const db = dtKey(b.data_apertura);
  if (da < db) return 1;
  if (da > db) return -1;

  // 3) fallback: id desc
  return (b.id || 0) - (a.id || 0);
})
  const mostrate = chiamate
  .filter((c) => (soloAperte ? c.stato === "aperta" : true))
  .filter((c) =>
    user?.ruolo === "tecnico"
      ? (mostraChiuse ? true : c.stato !== "chiusa")
      : true
  )
  .filter((c) => (soloMie ? c.tecnico === user?.username : true))
  .filter((c) => {
    const q = cercaAscensore.trim().toLowerCase();
    if (!q) return true;
    return (c.ascensore || "").toLowerCase().includes(q);
  }).length;


    return (
  <div style={{ padding: "20px" }}>
    <h1>Ufficio Manutenzione Ascensori</h1>

    {/* LOGIN */}
    {!user && (
      <div style={{ maxWidth: "320px", marginBottom: "20px" }}>
        <h3>Login</h3>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={{ width: "100%", marginBottom: "8px" }}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{ width: "100%", marginBottom: "8px" }}
        />

        <button onClick={login}>Accedi</button>

        {loginError && <p style={{ color: "red" }}>Credenziali non valide</p>}
      </div>
    )}

    {/* CONTENUTO */}
    {user && (
      <>
        {/* Header */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "15px",
            marginBottom: "10px",
          }}
        >
          <p style={{ margin: 0 }}>
            👋 Benvenuto <strong>{user.username}</strong> ({user.ruolo})
          </p>

          <button onClick={logout}>Logout</button>
          <button onClick={caricaChiamate}>Aggiorna</button>
        </div>

        {/* Debug (puoi toglierlo dopo) */}
        <div style={{ marginTop: 8, fontSize: 12, opacity: 0.8 }}>
          caricaImpianti chiamata: {debugImpiantiCalls} volte — impianti:{" "}
          {Array.isArray(impianti) ? impianti.length : "NON ARRAY"}
        </div>

        {/* ✅ SEGNALA GUASTO (TUTTI) */}
        <div
          style={{
            border: "1px solid #ddd",
            padding: 12,
            marginTop: 12,
            marginBottom: 12,
          }}
        >
          <h3 style={{ marginTop: 0 }}>Segnala guasto</h3>

          <div
            style={{
              display: "flex",
              gap: 8,
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >
            <select
              value={impiantoId}
              onChange={(e) => setImpiantoId(e.target.value)}
              style={{ padding: 8, minWidth: 260 }}
            >
              <option value="">Seleziona impianto…</option>
              {Array.isArray(impianti) &&
                impianti.map((i) => (
                  <option key={i.id} value={i.id}>
                    {i.codice} — {i.cliente} ({i.citta})
                  </option>
                ))}
            </select>

            <input
              placeholder="Descrizione guasto"
              value={descrGuasto}
              onChange={(e) => setDescrGuasto(e.target.value)}
              style={{ padding: 8, minWidth: 320, flex: "1 1 320px" }}
            />

            <button
              onClick={creaChiamataDaImpianto}
              disabled={!impiantoId || !descrGuasto.trim()}
              style={{ padding: "8px 12px" }}
            >
              Crea chiamata
            </button>
          </div>

          {msgChiamata && <div style={{ marginTop: 8 }}>{msgChiamata}</div>}
        </div>

        {/* ✅ CREA UTENTE (solo admin) */}
        {user.ruolo === "admin" && (
          <div style={{ border: "1px solid #ddd", padding: 12, marginBottom: 12 }}>
            <h3 style={{ marginTop: 0 }}>Crea utente</h3>

            <input
              placeholder="Username (es. luigi)"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              style={{ marginRight: 8 }}
            />

            <input
              placeholder="Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              style={{ marginRight: 8 }}
            />

            <select value={newRuolo} onChange={(e) => setNewRuolo(e.target.value)}>
              <option value="tecnico">tecnico</option>
              <option value="admin">admin</option>
            </select>

            <button style={{ marginLeft: 8 }} onClick={creaUtente}>
              Crea
            </button>

            {userMsg && <div style={{ marginTop: 8 }}>{userMsg}</div>}
          </div>
        )}

        {/* ✅ NUOVA CHIAMATA (solo admin) */}
        {user.ruolo === "admin" && (
          <div style={{ border: "1px solid #ddd", padding: 12, marginBottom: 12 }}>
            <h3 style={{ marginTop: 0 }}>Nuova chiamata</h3>

            <select
              value={nuovoImpiantoId ?? ""}
              onChange={(e) => {
                const val = e.target.value;
                setNuovoImpiantoId(val ? Number(val) : null);
              }}
              style={{ marginRight: 8, width: 320, maxWidth: "100%" }}
             >
              <option value="">Seleziona impianto</option>

              {Array.isArray(impianti) &&
                impianti.map((imp) => (
                  <option key={imp.id} value={imp.id}>
                    {imp.codice} — {imp.cliente} — {imp.citta}
                  </option>
                ))}
            </select>




            <input
              placeholder="Descrizione"
              value={nuovaDescrizione}
              onChange={(e) => setNuovaDescrizione(e.target.value)}
              style={{ marginRight: 8, width: 320, maxWidth: "100%" }}
            />

            <button
              onClick={creaChiamata}
              disabled={!nuovoImpiantoId || !nuovaDescrizione.trim()}
            >
              Crea chiamata
            </button>

            {msgChiamata && <div style={{ marginTop: 8 }}>{msgChiamata}</div>}
          </div>
        )}

        {/* Switch: Solo aperte (tutti) */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 6 }}>
          <span>Mostra solo chiamate aperte</span>

          <label style={{ position: "relative", display: "inline-block", width: 46, height: 26 }}>
            <input
              type="checkbox"
              checked={soloAperte}
              onChange={(e) => setSoloAperte(e.target.checked)}
              style={{ opacity: 0, width: 0, height: 0 }}
            />
            <span
              style={{
                position: "absolute",
                cursor: "pointer",
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                backgroundColor: soloAperte ? "#4caf50" : "#ccc",
                transition: "0.2s",
                borderRadius: 26,
              }}
            />
            <span
              style={{
                position: "absolute",
                height: 20,
                width: 20,
                left: soloAperte ? 24 : 3,
                top: 3,
                backgroundColor: "white",
                transition: "0.2s",
                borderRadius: "50%",
              }}
            />
          </label>
        </div>

        {/* Switch: Solo mie (solo tecnico) */}
        {user.ruolo === "tecnico" && (
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 10 }}>
            <span>Mostra solo le mie chiamate</span>

            <label style={{ position: "relative", display: "inline-block", width: 46, height: 26 }}>
              <input
                type="checkbox"
                checked={soloMie}
                onChange={(e) => setSoloMie(e.target.checked)}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span
                style={{
                  position: "absolute",
                  cursor: "pointer",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: soloMie ? "#4caf50" : "#ccc",
                  transition: "0.2s",
                  borderRadius: 26,
                }}
              />
              <span
                style={{
                  position: "absolute",
                  height: 20,
                  width: 20,
                  left: soloMie ? 24 : 3,
                  top: 3,
                  backgroundColor: "white",
                  transition: "0.2s",
                  borderRadius: "50%",
                }}
              />
            </label>
          </div>
        )}

        {/* Switch: Mostra anche chiuse (solo tecnico) */}
        {user.ruolo === "tecnico" && (
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 10 }}>
            <span>Mostra anche chiuse</span>

            <label style={{ position: "relative", display: "inline-block", width: 46, height: 26 }}>
              <input
                type="checkbox"
                checked={mostraChiuse}
                onChange={(e) => setMostraChiuse(e.target.checked)}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span
                style={{
                  position: "absolute",
                  cursor: "pointer",
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: mostraChiuse ? "#4caf50" : "#ccc",
                  transition: "0.2s",
                  borderRadius: 26,
                }}
              />
              <span
                style={{
                  position: "absolute",
                  height: 20,
                  width: 20,
                  left: mostraChiuse ? 24 : 3,
                  top: 3,
                  backgroundColor: "white",
                  transition: "0.2s",
                  borderRadius: "50%",
                }}
              />
            </label>
          </div>
        )}

        {/* Ricerca ascensore */}
        <div
          style={{
            marginTop: 12,
            marginBottom: 12,
            display: "flex",
            gap: 8,
            alignItems: "center",
          }}
        >
          <input
            type="text"
            placeholder="Cerca ascensore (es. scala A, condominio Rossi...)"
            value={cercaAscensore}
            onChange={(e) => setCercaAscensore(e.target.value)}
            style={{ width: "100%", maxWidth: 420, padding: 8 }}
          />

          <button onClick={() => setCercaAscensore("")}>Pulisci</button>
        </div>

        <table border="1" cellPadding="8">
          <thead>
            <tr>
              <th>ID</th>
              <th>Ascensore</th>
              <th>Descrizione</th>
              <th>Stato</th>
              <th>Tecnico</th>
              <th>Apertura</th>
              <th>Chiusura</th>
              <th>Azioni</th>
            </tr>
          </thead>

          <tbody>
            {chiamate
              .filter((c) => (soloAperte ? c.stato === "aperta" : true))
              .filter((c) => (soloMie ? c.tecnico === user.username : true))
              .filter((c) => {
                const q = cercaAscensore.trim().toLowerCase();
                if (!q) return true;
                return (c.ascensore || "").toLowerCase().includes(q);
              })
              .sort((a, b) => {
                const ra = statusRank(a.stato);
                const rb = statusRank(b.stato);
                if (ra !== rb) return ra - rb;

                const da = dtKey(a.data_apertura);
                const db = dtKey(b.data_apertura);
                if (da < db) return 1;
                if (da > db) return -1;

                return (b.id || 0) - (a.id || 0);
              })
              .map((c) => (
                <tr
                  key={c.id}
                  style={{
                    backgroundColor:
                      c.stato === "aperta"
                        ? "#fbe9e7"
                        : c.stato === "in lavorazione"
                        ? "#fff8e1"
                        : "#e8f5e9",
                  }}
                >
                  <td>{c.id}</td>
                  <td>{c.ascensore}</td>
                  <td>{c.descrizione}</td>

                  <td>
                    <span
                      style={{
                        padding: "4px 8px",
                        borderRadius: "8px",
                        color: "white",
                        fontWeight: "bold",
                        backgroundColor:
                          c.stato === "aperta"
                            ? "#d9534f"
                            : c.stato === "in lavorazione"
                            ? "#f0ad4e"
                            : "#5cb85c",
                      }}
                    >
                      {c.stato}
                    </span>
                  </td>

                  <td>{c.tecnico || "-"}</td>
                  <td>{short(c.data_apertura)}</td>
                  <td>{short(c.data_chiusura)}</td>

                  <td style={{ display: "flex", gap: "8px" }}>
                    {user.ruolo === "tecnico" && c.stato === "aperta" && !c.tecnico && (
                      <button onClick={() => prendiChiamata(c.id)}>Prendi chiamata</button>
                    )}

                    {user.ruolo === "tecnico" &&
                      c.stato !== "chiusa" &&
                      c.tecnico === user.username && (
                        <button onClick={() => chiudiChiamata(c.id)}>Chiudi</button>
                      )}
                      {c.impianto_id && (
                        <button
                          onClick={() => caricaStoricoImpianto(c.impianto_id)}
                          style={{ backgroundColor: "#1976d2", color: "white" }}
                        >
                          Storico
                        </button>
                      )}
                    {c.ascensore && (
                     <button
                       onClick={() => {
                         const parts = (c.ascensore || "").split(" — ");
                         const cliente = encodeURIComponent(parts[1] || "");
                         window.open(
        `                   http://127.0.0.1:8000/clienti/${cliente}/report-pdf`,
                           "_blank"
                          );
                        }}
                        style={{ backgroundColor: "#6a1b9a", color: "white" }}
                       >
                        PDF
                       </button>
                     )}

                    </td>
                </tr>
              ))}
          </tbody>
        </table>
        <div
  style={{
    marginTop: 20,
    padding: 20,
    border: "2px solid #1976d2",
    background: "#e3f2fd",
    borderRadius: 8
  }}
>

    <h3>Storico impianto</h3>
    <div style={{ marginBottom: 10 }}>
      <button
        onClick={() => scaricaPdfImpianto(impiantoSelezionato)}
        style={{
          backgroundColor: "#2e7d32",
          color: "white",
          padding: "6px 12px",
          border: "none",
          borderRadius: 4,
          cursor: "pointer"
        }}
      >
        📄 Scarica PDF impianto
    </button>
  </div>


    <table border="1" cellPadding="6">
      <thead>
        <tr>
          <th>ID</th>
          <th>Descrizione</th>
          <th>Stato</th>
          <th>Tecnico</th>
          <th>Apertura</th>
          <th>Chiusura</th>
        </tr>
      </thead>
      <tbody>
        {storicoImpianto.map(s => (
          <tr key={s.id}>
            <td>{s.id}</td>
            <td>{s.descrizione}</td>
            <td>{s.stato}</td>
            <td>{s.tecnico || "-"}</td>
            <td>{s.data_apertura}</td>
            <td>{s.data_chiusura || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>

    <button
      style={{ marginTop: 10 }}
      onClick={() => setStoricoImpianto([])}
    >
      Chiudi storico
    </button>
  </div>
)}


        <div style={{ marginTop: 8, fontSize: 24, fontWeight: "bold" }}>
          Mostrate: {mostrate} su {chiamate.length}
        </div>

        <p style={{ marginTop: "10px", fontSize: "12px", opacity: 0.8 }}>
          Nota: la logica “chi può prendere/chiudere” viene controllata dal backend; qui
          nascondiamo solo i bottoni per comodità.
        </p>

        {/* 👇 QUI INCOLLI IL POPUP MODALE 👇 */}

        {mostraStorico && (
  <div
    onClick={() => setMostraStorico(false)}
    style={{
      position: "fixed",
      top: 0,
      left: 0,
      width: "100%",
      height: "100%",
      backgroundColor: "rgba(0,0,0,0.5)",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      zIndex: 1000
    }}
  >
    <div
      onClick={(e) => e.stopPropagation()}
      style={{
        background: "white",
        padding: 25,
        borderRadius: 10,
        width: "80%",
        maxWidth: 800,
        maxHeight: "80%",
        overflowY: "auto",
        boxShadow: "0 10px 30px rgba(0,0,0,0.3)"
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h3 style={{ margin: 0 }}>Storico Impianto #{impiantoSelezionato}</h3>
        <button
          onClick={() => setMostraStorico(false)}
          style={{
            background: "transparent",
            border: "none",
            fontSize: 20,
            cursor: "pointer"
          }}
        >
          ✖
        </button>
      </div>

      <hr />

      {storicoImpianto.length === 0 ? (
        <p>Nessuna chiamata per questo impianto.</p>
      ) : (
        <table border="1" cellPadding="6" style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Descrizione</th>
              <th>Stato</th>
              <th>Tecnico</th>
              <th>Apertura</th>
              <th>Chiusura</th>
            </tr>
          </thead>
          <tbody>
            {storicoImpianto.map((s) => (
              <tr key={s.id}>
                <td>{s.id}</td>
                <td>{s.descrizione}</td>
                <td>{s.stato}</td>
                <td>{s.tecnico || "-"}</td>
                <td>{s.data_apertura}</td>
                <td>{s.data_chiusura || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  </div>
)}

      </>
    )}
  </div>
);

}

export default App;
