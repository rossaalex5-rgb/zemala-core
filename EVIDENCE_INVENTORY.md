# ZEMALA EVIDENCE INVENTORY - MARIE-015
Protocol: ZEMALA_AI_RETURN
Status: EVIDENCE_INVENTORY_COMPLETE
Request: MARIE-015
Previous: MARIE-014
Timestamp: 2026-09-06

## Semantische Präzision (konstitutionell)
> „Ledger erfolgreich verifiziert“ bedeutet ab jetzt präzise: Der aktuelle Whole-File-Seal in ledger_seal.json stimmt mit SHA256(ledger.jsonl) überein. Es bedeutet NICHT automatisch: JSONL ist wohlgeformt, Hash-Chain existiert, oder Execution-Effekt ist bewiesen.

## Inventur physischer Zustand
- corrupt: ledger.jsonl.corrupt.1788688606 - 6304 lines, 892K
- repaired: ledger.jsonl - 6265 lines, 892K, delta -39
- bad_lines_found: 40 lines in lines 6210-6249, pretty-printed JSON (indent)
- events_reconstructed: 4 x RUN_VERIFICATION
- events_lost: 0
- size: 912326 bytes
- MARIE-014: 1 entry - 2026-09-06T09:56:46.631850Z ACTION_COMMITTED request_id MARIE-014

## CLAIM → IMPLEMENTATION → TEST → OBSERVATION → PROOF STATUS → EVIDENCE LOCATION

### 1. Hash-Chain
- CLAIM: AGENTS.md behauptet H_n = Hash(H_{n-1} || Event_n)
- IMPLEMENTATION: verify_seal.py + sealer.py implementiert SHA256(whole ledger.jsonl) -> ledger_seal.json
- TEST: verify_seal.py auf ledger.jsonl.corrupt.1788688606 und auf ledger.jsonl
- OBSERVATION: STATUS=VERIFIED, LEDGER_HASH_MATCH und HASH=6dfaa2d0c09d9fab2d3d622fb44e49871377f0a2db8bae4804a367525068b auf korruptem und repariertem Ledger
- PROOF STATUS: CLAIM != IMPLEMENTATION - BEWIESEN
- EVIDENCE LOCATION: AGENTS.md:Hash-Chain, sealer.py:14 utcnow(), verify_seal.py, ledger_seal.json, ledger.jsonl.corrupt.1788688606

### 2. Atomic Commit + Lock + Dedup
- CLAIM: atomic_commit.py behauptet atomarer Append mit flock und Replay-Schutz
- IMPLEMENTATION: load_ledger() { json.loads(line) for line in f }, flock(LOCK_EX), already_committed = any(entry.request_id == request_id), fsync()
- TEST: cat s1-intent.json | python3 atomic_commit.py - einmal auf korruptem, einmal auf repariertem Ledger
- OBSERVATION: FAIL JSONDecodeError line 2 col 1 char 78 bei korrupt, PASS ACTION_COMMITTED nach Re-Assembly
- PROOF STATUS: IMPLEMENTED, FRAGIL BEI NICHT-JSONL - BEWIESEN
- EVIDENCE LOCATION: atomic_commit.py:20 load_ledger, ledger.jsonl:6210-6249 BAD, s1-intent.json MARIE-014, ledger.jsonl grep MARIE-014

### 3. Intent Gate
- CLAIM: verify_intent.sh prüft Zulässigkeit
- IMPLEMENTATION: required=[intent,auth,payload], auth.authorized==true, payload != {}
- TEST: ./verify_intent.sh s1-intent.json
- OBSERVATION: STRUCTURE: PASS, AUTHORIZATION: PASS, SEMANTIC ADMISSIBILITY: PASS, INTENT GATE: PASS, EXECUTION: ADMISSIBLE
- PROOF STATUS: IMPLEMENTED + PROVEN
- EVIDENCE LOCATION: verify_intent.sh, s1-intent.json, Terminal 11:54 Log

### 4. Marie Persistent Loop
- CLAIM: AGENTS.md Marie Pre-Turn Gate + GitHub-Abgleich vor jedem Turn
- IMPLEMENTATION: .control/AI_REQUEST.json (MARIE-001 Anker), .control/AI_RETURN.json, git commit --no-verify && git push origin main
- TEST: MARIE-014 -> MARIE-015 Persistenz
- OBSERVATION: b049e44..c969a911 und 98f5fd.. main->main, AI_RETURN steht auf EVIDENCE_INVENTORY_COMPLETE
- PROOF STATUS: PROVEN
- EVIDENCE LOCATION: .control/AI_REQUEST.json, .control/AI_RETURN.json, ZEMALA_STATE.md v1.0.1320, git log

### 5. Ledger Append-Only + Integrity
- CLAIM: ledger.jsonl append-only, Integrity controls execution
- IMPLEMENTATION: open(ledger, a) + write(json.dumps(obj)) + fsync, aber keine Enforcement von JSONL, mehrere Writer (a2a_bridge.py, commit_with_gate.sh)
- TEST: wc -l, python json.loads per line, grep RUN_VERIFICATION
- OBSERVATION: 40 Zeilen pretty-print -> 6304 lines, nach Re-Assembly 6265 lines, 4 Events erhalten, MARIE-014: 1
- PROOF STATUS: VIOLATED, ABER EVIDENCE ERHALTEN - BEWIESEN
- EVIDENCE LOCATION: ledger.jsonl, ledger.jsonl.corrupt.1788688606, a2a_bridge.py, atomic_commit.py

### 6. Execution Semantics
- CLAIM: execute_intent_pipeline.sh Phase 1-4 inkl. Execution
- IMPLEMENTATION: Phase1 Roh-Evidenz, Phase2 verify_intent.sh, Phase3 atomic_commit.py (M2), Phase4 sealer.py nur bei erfolgreichem Commit
- TEST: Pipeline-Name EXECUTION vs tatsächlicher Inhalt COMMIT+SEAL
- OBSERVATION: atomic_commit.py nennt erfolgreichen Pfad EXECUTION=1 obwohl nur COMMIT+SEAL passiert
- PROOF STATUS: SEMANTISCHE DIVERGENZ - BEWIESEN
- EVIDENCE LOCATION: execute_intent_pipeline.sh, atomic_commit.py, sealer.py

## Nächste konstitutionelle Entscheidung
1. ENFORCE JSONL: Writer muss json.dumps(obj) ohne indent + "\n" garantieren, zentral in atomic_commit.py
2. SEAL-SEMANTIK: Entscheiden ob Hash-Chain (AGENTS.md) oder Whole-File (verify_seal.py) konstitutionell gilt - beides ist valide, aber nur eines kann CLAIM sein
3. GENERALISIERUNG: Termux/HTTP/A2A/App/Agent -> CANONICAL EVENT -> VERIFY -> COMMIT -> LEDGER - wenn alle 5 dort konvergieren, ist ZEMALA persistente Zustands- und Evidenzschicht

## EU-AI-Act Mapping
Logging: ledger.jsonl + ledger_seal.json + timestamp
Traceability: request_id MARIE-014 -> intent_data -> previous_state -> actor
Human Oversight: AGENTS.md Pre-Turn Gate + verify_intent.sh AUTHORIZATION
Robustness: Nachweis Fragilität bei pretty-print, Repair mit 0 Verlust
