# ZEMALA-CORE B2B DEFENSIVE MATRIX
## Regulatory Sandbox & Compliance Briefing (WTSH / Jobcenter)

### 1. Skalierbarkeit & Architektur (Gegen Einwand: "Nur ein Bastelprojekt?")
- **Modell-agnostisches Gitter:** Kein ressourcenfressender Cloud-Zoo (wie Microsoft Purview oder Splunk), sondern dezentrale Edge-Knoten.
- **Ressourcen-Effizienz:** Starre Deckelung (`OLLAMA_NUM_THREADS=2`) hält die Hardware thermisch stabil bei unter 31 °C.
- **Föderierte Skalierung:** Verknüpfung über Model Context Protocols (MCP) und A2A-Schnittstellen zur horizontalen Lastverteilung.

### 2. Ausfallsicherheit & Datensicherheit (Gegen Einwand: "Was bei Hardware-Verlust?")
- **Event Sourcing:** Unveränderliches Append-only Ledger (`observations.jsonl`) statt flüchtiger, manipulierbarer Datenbanken.
- **Kryptografische Kette:** SHA-256-Hash-Verschmelzung jedes Ereignisses mit seinem Vorgänger.
- **Stateless Resilience:** Rekonstruktion des gesamten Systemzustands in unter 2 Millisekunden aus dem Ledger; Echtzeit-Backup via asynchronem rclone-Daemon auf Google Drive.

### 3. Rechtliche Konformität (Gegen Einwand: "Haftung nach EU AI Act?")
- **Compliance by Design:** Technische Erzwungenerfüllung von Art. 12 (Protokollierung) und Art. 14 (Menschliche Aufsicht).
- **Verify-Before-Seal (VBS):** Reject-by-Default-Prinzip – weicht ein Bit ab, blockiert das System jegliche Ausführung.
- **Beweislastumkehr:** Gerichtsverwertbare, lückenlose Herkunftskette und mathematische Stabilität (Hurst-Exponent $H \ge 0,95$).
