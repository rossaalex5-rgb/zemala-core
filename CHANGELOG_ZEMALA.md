# Changelog Zemala - Lückenlose Revisionshistorie, revisionssicher

**Regel: Nie überschreiben, nie löschen, nur anhängen.** Jeder Eintrag ist per Hash mit dem Vorgänger verkettet. Wer einen Eintrag ändert, löscht oder einfügt, bricht die Kette, und `verify_changelog.py` meldet FAIL.

**Ketten-Head (10 Einträge, 0..9): `39f7191385c6a9f3140aa230eb7d87a011721528134e4857fe7ae0f987b7307b`**

**Maschinenprüfbar:** `evidence/changelog.jsonl` + `python3 verify_changelog.py`

**Was ein Eintrag enthält:** Index, Timestamp UTC, Typ, `prev_hash`, `hash`, alle 6 Artefakt-Hashes, Validierungsergebnis, Commit-SHA + Commit-Status. `commit_sha: null` = noch kein echter Commit. `BEHAUPTET, UNVERIFIZIERT` = darf nicht als Beweis zitiert werden.

**Was dieses Changelog NICHT beweist:** Kein Beweis für April/Mai 2025. Git-Daten sind frei setzbar. Erst ein öffentlicher Commit-Link, der mit `git show` gegen diese Hashes geprüft ist, macht es extern verifizierbar.

## Einträge

### 0 - GENESIS_LEDGER - 2026-11-16T21:35:47Z
- **Hash:** `0289c47ddb05cdcc1f0c7ef3b9128b65dd72351d725dbc9465c7c5a7bb33dc0e`
- **Prev:** `0000000000000000000000000000000000000000000000000000000000000000`
- **desc:** 12-Block Ledger, kanonisch, Anker extern. Head und Count aus evidence/ledger_anchor.json.
- **ledger_file:** evidence/ledger.jsonl
- **block_count:** 12
- **head_hash:** a8875565a600c7d5f0ec46c38551c10abd4b1064680ad7e060a84ebc5d6535e5
- **anchor_hash:** 08f488919c81c8741960a147c0901b93229da370b4a70a1347505ea85e42ceed
- **ledger_hash:** b4247c8d18780d28d076a3a3985b4832a10f537240a5f284c2de2923ae7bdd22
- **commit_sha:** None
- **commit_status:** PENDING - kein verifizierter GitHub-Commit für Genesis in dieser Sandbox
- **validation:** verify_ledger.py v3 FINAL, Anker-Zwang, 12/12 Blöcke, Hash neu berechnet

### 1 - VALIDATION_VERIFY_V3 - 2026-11-16T21:35:47Z
- **Hash:** `68520a97f715d54cb4092b7d68a0ecba53b3048e2fd42ab41a0fe9786e583163`
- **Prev:** `0289c47ddb05cdcc1f0c7ef3b9128b65dd72351d725dbc9465c7c5a7bb33dc0e`
- **desc:** verify_ledger.py v3 FINAL, ATOMAR. --anchor Pflicht, --write-anchor entfernt, JEDE ZEMALA_* = FAIL.
- **file_hash:** 3ae0284d9ddab4d37088ee3adda332ac75ac6e931720d0c787b2070254cfaccd
- **result:** PASS - 12/12 Blöcke + Anker OK in sauberer Kopie
- **commit_sha:** None
- **commit_status:** PENDING

### 2 - VALIDATION_ORCHESTRATOR - 2026-11-16T21:35:47Z
- **Hash:** `c39ea31f6f1c098e7cb8c6aa44f11f127906a23e792695eb9e767c9c751d4ec4`
- **Prev:** `68520a97f715d54cb4092b7d68a0ecba53b3048e2fd42ab41a0fe9786e583163`
- **desc:** STARTEN.sh dünner Delegator, exec via bash (+x-unabhängig). Orchestrator: Env-Lock Gate 0, Manifest-Check, Config, Prozesse, Ledger+Anker, Node, Audit zuletzt.
- **starten_hash:** 5576c0768ab76c5b9be6e5bdbee3f4f6155b8855b62f0ba6acabf4c9b0679e06
- **orchestrator_hash:** 609d0f7f64b0f08692148dbdedd9dd8e9f549a38f17a45338ddaf95a835239a3
- **result:** PASS - Entscheidungslauf COMPLIANT in sauberer Kopie
- **commit_sha:** None
- **commit_status:** PENDING

### 3 - VALIDATION_MANIFEST_PORTABEL - 2026-11-16T21:35:47Z
- **Hash:** `dbe0ffad07ba7b3cd391e0e4a4b3bd6bb2473b8e2d51121b22cf2294c4c49658`
- **Prev:** `c39ea31f6f1c098e7cb8c6aa44f11f127906a23e792695eb9e767c9c751d4ec4`
- **desc:** Manifest base_dir ., 5 Pins, alle Pfade relativ, kein absoluter Pfad im Manifest-Text. 6. Artefakt = Manifest selbst via manifest_hash im Audit.
- **manifest_hash:** a43fd5ca16c4208fe8459f843e5678f91f7bbf377a3e4ede2e727a4ef4e3738b
- **pins:** ['verify_ledger.py', 'STARTEN.sh', 'evidence/ledger.jsonl', 'evidence/ledger_anchor.json', 'zemala_orchestrator.sh']
- **result:** PASS - Orchestrator Portabilitäts-Check besteht
- **commit_sha:** None
- **commit_status:** PENDING

### 4 - VALIDATION_DOCKER_GATE - 2026-11-16T21:35:47Z
- **Hash:** `e049f2183ad65cc554144ee1bf62a135db0a496a4863f3896c229e8ce2f261a8`
- **Prev:** `dbe0ffad07ba7b3cd391e0e4a4b3bd6bb2473b8e2d51121b22cf2294c4c49658`
- **desc:** docker_cleanroom_gate.sh: alle 6 gegen Manifest, Audit NACH STARTEN geprüft (Fix: Audit vor STARTEN hat frische Kopie immer FAILen lassen). Commit erst bei 100%.
- **gate_hash:** f21f10693278aae1269fd15de75c6200ca62c4dcc7f9dd61846722f1e257a558
- **result:** PASS - Gate Clean Copy 6/6, COMMIT_ALLOWED. Tamper: Gate blockt, COMMIT_BLOCKED, Exit 1.
- **commit_sha:** None
- **commit_status:** PENDING

### 5 - VALIDATION_PRECOMMIT - 2026-11-16T21:35:47Z
- **Hash:** `2077ccdbc028892b9d4198526be5ae42b31404fd57860db233e967098e0c0323`
- **Prev:** `e049f2183ad65cc554144ee1bf62a135db0a496a4863f3896c229e8ce2f261a8`
- **desc:** pre_commit_check.sh: unmittelbar vor jedem Commit alle 6 gegen Manifest. Eigener Node-Stub mit allow_reuse_address (Fix: TIME_WAIT-Flakiness). Bei FAIL Commit blockiert.
- **precommit_hash:** 6eb0875a4b9a61c8cd58a93ec404f1f0ef6cff81ca5faf33011f2fe8926f231a
- **result:** PASS - Pre-Commit 7/7 in sauberer Kopie, PRECOMMIT_ALLOWED. Tamper: blockt, PRECOMMIT_BLOCKED, Exit 1.
- **commit_sha:** None
- **commit_status:** PENDING

### 6 - VALIDATION_FAIL_DOCUMENTED - 2026-11-16T21:39:31Z
- **Hash:** `b93a094b3c6c7d3bb46e8bdd0cf1695a980ae44e0a54e784c29fe873bff54d50`
- **Prev:** `2077ccdbc028892b9d4198526be5ae42b31404fd57860db233e967098e0c0323`
- **desc:** FAIL-Lauf dokumentiert: Audit NON-COMPLIANT, Node unreachable, weil Pre-Commit-Stub auf TIME_WAIT-Port lief. Ursache gefunden und gefixt (allow_reuse + Warte-Loop). Kein Beweis versteckt, kein FAIL gelöscht.
- **audit_status_before_fix:** NON-COMPLIANT
- **failed_check:** Node service unreachable (http://localhost:8085/status)
- **result:** FAIL, dokumentiert, gefixt, danach erneut PASS in sauberer Kopie
- **commit_sha:** None
- **commit_status:** PENDING - FAIL-Läufe werden nie committet

### 7 - CLAIM_GITHUB_COMMIT_UNVERIFIED - 2026-11-16T21:35:47Z
- **Hash:** `47e9fd9ab6299ffc78597b27e42600ce781e3101bd28d6382ea96149aacabcae`
- **Prev:** `b93a094b3c6c7d3bb46e8bdd0cf1695a980ae44e0a54e784c29fe873bff54d50`
- **desc:** Vom User behaupteter Stand: Branch feature/zemala-ultimate-master-sync, Commit 54778d54, 3 Punkte fixed/verifiziert/live. In dieser Sandbox NICHT verifiziert: kein .git, kein Remote, keine Credentials, kein Commit-Link geprüft.
- **claimed_branch:** feature/zemala-ultimate-master-sync
- **claimed_commit:** 54778d54
- **result:** UNVERIFIZIERT - darf nicht als Beweis zitiert werden, bis voller Commit-Link mit git show geprüft ist
- **commit_sha:** 54778d54 (BEHAUPTET, UNVERIFIZIERT)
- **commit_status:** UNVERIFIZIERT

### 8 - VALIDATION_DECISION_RUN - 2026-11-16T21:41:33Z
- **Hash:** `ffebc7b87d911b12d6da21bade83a467d2b2ed5aa52bf4a46f1d71b3c43e5406`
- **Prev:** `47e9fd9ab6299ffc78597b27e42600ce781e3101bd28d6382ea96149aacabcae`
- **desc:** Frischer Entscheidungslauf in Base vor Changelog-Erstellung.
- **audit_status:** COMPLIANT
- **audit_compliant:** True
- **audit_demo:** False
- **block_count:** 12
- **head_hash:** a8875565a600c7d5f0ec46c38551c10abd4b1064680ad7e060a84ebc5d6535e5
- **manifest_hash:** a43fd5ca16c4208fe8459f843e5678f91f7bbf377a3e4ede2e727a4ef4e3738b
- **checks_passed:** ['Cloud isolation (Config): Keine persistente Gemini/gcloud/openai Config gefunden', 'Cloud isolation (Env): Kein externer API-Key in Env', 'Cloud isolation (Prozesse): Kein aktiver Cloud-CLI Prozess gefunden', 'Ledger Integrity: Ledger valid + Anker OK', 'Node service: reachable (http://localhost:8085/status)']
- **checks_failed:** []
- **hashes_6:**
  - STARTEN.sh: `5576c0768ab76c5b9be6e5bdbee3f4f6155b8855b62f0ba6acabf4c9b0679e06`
  - verify_ledger.py: `3ae0284d9ddab4d37088ee3adda332ac75ac6e931720d0c787b2070254cfaccd`
  - zemala_orchestrator.sh: `609d0f7f64b0f08692148dbdedd9dd8e9f549a38f17a45338ddaf95a835239a3`
  - zemala_manifest.json: `a43fd5ca16c4208fe8459f843e5678f91f7bbf377a3e4ede2e727a4ef4e3738b`
  - evidence/ledger.jsonl: `b4247c8d18780d28d076a3a3985b4832a10f537240a5f284c2de2923ae7bdd22`
  - evidence/ledger_anchor.json: `08f488919c81c8741960a147c0901b93229da370b4a70a1347505ea85e42ceed`
  - evidence/ledger_audit.json: `8d1b990c0246bec93a5b0994c51ff1f1771cf0dfe1590cda12d14d4fab38cbc8`
  - CHANGELOG_ZEMALA.md: `PENDING - wird nach Schreiben gesetzt, Changelog verifiziert sich selbst via changelog.jsonl`
- **result:** COMPLIANT - Exit 0
- **commit_sha:** None
- **commit_status:** PENDING - nächster echter Commit muss diesen Eintrag + seinen SHA anhängen

### 9 - CHANGELOG_GENESIS - 2026-11-16T21:41:33Z
- **Hash:** `39f7191385c6a9f3140aa230eb7d87a011721528134e4857fe7ae0f987b7307b`
- **Prev:** `ffebc7b87d911b12d6da21bade83a467d2b2ed5aa52bf4a46f1d71b3c43e5406`
- **desc:** Dieses Changelog selbst als Hash-Kette etabliert. Jeder weitere Validierungsschritt und jeder Commit wird als neuer Eintrag angehängt, nie überschrieben, nie gelöscht. Kette prüfen mit: python3 verify_changelog.py
- **changelog_file:** CHANGELOG_ZEMALA.md
- **chain_file:** evidence/changelog.jsonl
- **verify_cmd:** python3 verify_changelog.py
- **result:** PASS - Kette 0..9 geschlossen, Head wird unten im Changelog publiziert
- **commit_sha:** None
- **commit_status:** PENDING - dieser Eintrag muss im nächsten echten Commit mitgepusht werden

## So wird ein neuer Eintrag angehängt (nächster Schritt, direkt)

```bash
# 1. Im echten Repo: Entscheidungslauf + Pre-Commit, muss PASS geben
bash STARTEN.sh  # braucht Node auf http://localhost:8085/status, sonst NON-COMPLIANT
bash pre_commit_check.sh  # muss PRECOMMIT_ALLOWED.json, Exit 0

# 2. Neuen Changelog-Eintrag anhängen, NIEMALS alte Einträge editieren
python3 append_changelog.py --type COMMIT --commit-sha <voller Git-SHA nach push> --result PASS
# append_changelog.py nimmt den aktuellen Head als prev_hash, berechnet den neuen Hash, hängt an evidence/changelog.jsonl an
# und regeneriert CHANGELOG_ZEMALA.md aus der Kette.

# 3. Kette prüfen
python3 verify_changelog.py  # muss: KETTE GESCHLOSSEN

# 4. Commit + Push, Changelog IMMER mitpushen
git add CHANGELOG_ZEMALA.md evidence/changelog.jsonl verify_changelog.py append_changelog.py STARTEN.sh verify_ledger.py zemala_orchestrator.sh zemala_manifest.json evidence/ledger.jsonl evidence/ledger_anchor.json evidence/ledger_audit.json
git commit -m "Zemala: Changelog-Eintrag <Index> für Commit <SHA>, Validierung PASS"
git push origin main

# 5. Extern verifizieren (Dritte)
git show HEAD:evidence/changelog.jsonl | python3 -c "import sys, json, hashlib; ..."  # oder: Datei auschecken, dann python3 verify_changelog.py
git show HEAD:zemala_manifest.json | sha256sum  # muss = Audit manifest_hash sein
```

## Nächster Schritt, direkt gesetzt

**Nächster Schritt:** Im echten Repo `bash STARTEN.sh` + `bash pre_commit_check.sh` laufen lassen, dann mit `append_changelog.py` einen echten `COMMIT`-Eintrag mit dem vollen GitHub-SHA anhängen, Kette prüfen, Changelog mitpushen, und den vollen Commit-Link hierher schicken. Kein weiterer Schritt ohne diesen Eintrag, sonst entsteht eine Lücke.

**Aktueller Head für den nächsten Eintrag (prev_hash): `39f7191385c6a9f3140aa230eb7d87a011721528134e4857fe7ae0f987b7307b`**
