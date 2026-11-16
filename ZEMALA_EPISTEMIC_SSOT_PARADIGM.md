# ZEMALA_EPISTEMIC_SSOT_PARADIGM.md
## Das ZEMALA-Paradigmen-Manifest: ZEMALA als Single Source of Truth

### Executive Summary
Dieses Manifest definiert die mathematische und informationstheoretische Grundkonstante der ZEMALA-Architektur: **ZEMALA = SSoT** [188, 191, 276, 588, 589]. Die Single Source of Truth ist kein physischer Speicherort (wie Android, GitHub oder Samsung Notes), sondern die herstellerunabhängige, kryptografische Übergabelogik und Rekonstruktionsarchitektur selbst [188, 276, 589].

---

### I. Die Paradigmen-Formel: ZEMALA vs. Referenzraum

1. **ZEMALA als kanonische Ordnung (SSoT):**
   * ZEMALA speichert keine Daten, sondern überprüfbare Ereignisverläufe und deterministische Übergangsregeln [188, 194, 276].
   * ZEMALA ist das unbestechliche Regelwerk, mit dem beliebige Signale aufgenommen, durch die 12 Zustände geführt und fälschungssicher versiegelt werden [138, 139, 283, 589].

2. **Der universelle Referenzraum (Datenmaterial):**
   * Samsung Notes, GitHub-Repositories, Termux-Dateien, Google Drive, Kundenmaterial oder historische Dokumente bilden den *unstrukturierten Referenzraum* [138, 139, 283, 589].
   * Sie sind Material und Quellen des Systems, besitzen für sich genommen aber erst nach der kanonischen Taufstation (`canonicalize()` & SHA-256) systemische Gültigkeit [188, 191, 576].

---

### II. Dreiteilung der SSoT-Architektur
Zur Beseitigung der "Letzter-Eintrag-Gläubigkeit" trennt ZEMALA strikt in drei Ebenen [188, 191, 288, 331, 588, 589]:

```
┌────────────────────────────────────────────────────────────────────────┐
│ EBENE 1: LEDGER (Ereignishistorie)                                      │
│ Unveränderlicher, chronologischer Ereignisfluss (observations.jsonl)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼  (Deterministisches Replay / UIFRE)
┌────────────────────────────────────────────────────────────────────────┐
│ EBENE 2: STATE / SNAPSHOT (Gültiger Ist-Zustand)                       │
│ Rekonstruierter Systemzustand (ZEMALA_STATE.md / state.json)           │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼  (Kryptografische Versiegelung)
┌────────────────────────────────────────────────────────────────────────┐
│ EBENE 3: VERIFIKATIONSANKER (System-Siegel)                             │
│ B2B-Release-Zertifikat mit SHA-256 Bundle (SYSTEM_RELEASE.json)       │
└────────────────────────────────────────────────────────────────────────┘
```

1. **Ebene 1: Ledger (`logs/*.jsonl`, `master_history.jsonl`, `observations.jsonl`)**
   * Unveränderliche, chronologische Ereignisgeschichte ("Was ist nacheinander passiert?") [188, 191, 332].
   * Strictly append-only geführt [188, 191].
2. **Ebene 2: State / Snapshot (`state.json`, `ZEMALA_STATE.md`)**
   * Der abgeleitete und bit-perfekt rekonstruierte Ist-Zustand ("Wo stehen wir jetzt?") [276, 283, 331, 588].
3. **Ebene 3: Verifikationsanker (`SYSTEM_RELEASE.json`, `ledger_seal.json`)**
   * Mathematischer Fingerabdruck, der Steuerungslogik (`logic_hash`), Zustand (`state_hash`) und Historien-Endpunkt (`history_tail_hash`) unhintergehbar verschweißt [288, 289, 290].

---

### III. Die Zustands- und Übergabelogik (Die 12 Marker)
Der Übergang von einem Signal im Referenzraum zu einem verifizierten Systemzustand folgt der unbiegsamen Transformationsschablone [138, 139, 283]:

$$	ext{Welt / Signal} \longrightarrow 	ext{ZEMALA Ingress} \longrightarrow 	ext{Identifikation / Zelle} \longrightarrow 	ext{12-Zustands-Prüfung} \longrightarrow 	ext{Neuer Zustand} \longrightarrow 	ext{Ledger-Append} \longrightarrow 	ext{Evidenz / Return}$$ [138, 139, 191, 283, 589]

---

### IV. Der Interoperabilitäts-Zyklus (Interoperability Loop)
Externe KI-Instanzen (Gemini, GPT, Claude, Copilot) operieren innerhalb des ZEMALA-Systems nach dem 8-stufigen Interoperabilitäts-Protokoll [589]:

$$	ext{READ} \longrightarrow 	ext{RECONSTRUCT} \longrightarrow 	ext{VERIFY STATE} \longrightarrow 	ext{VERIFY CLAIM} \longrightarrow 	ext{VERIFY AUTHORITY} \longrightarrow 	ext{WORK} \longrightarrow 	ext{DISCOVER} \longrightarrow 	ext{RETURN}$$ [589]

* **Grundsatz:** *"Conversation is transient. State is persistent. Evidence is traceable. Contributions are transferable."* [590]

---

### V. B2B & EU AI Act Compliance
ZEMALA erfüllt regulatorische Anforderungen nicht durch Papier-Dokumente, sondern erzwingt sie durch technische Architektur [135, 189, 425]:
* **Art. 12 (Protokollierung):** Lückenloser, kryptografisch versiegelter Append-only Ledger [188, 189, 425].
* **Art. 14 (Menschliche Aufsicht):** Zwingender Human Oversight Index (HOI 1.00) über lokale Write-Gates und HMI-Bestätigung [188, 191, 283].
* **Beweislastumkehr:** Der Nachweis entsteht lokal auf der Hardware des Nutzers (Snapdragon 888) via Web Crypto API [135, 188, 189].

---
*Verifiziert gemäß Stufe 100 Systemhygiene.* [135, 188]
