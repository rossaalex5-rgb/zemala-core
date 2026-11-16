# FINALER PUSH - Push-fertig, Zyklus-Abschluss

Exzellente Arbeit: atomare v3, portables Manifest, Docker Gate, Pre-Commit scharf. Lückenlos.

## Verifizierter Zustand (in sauberer Kopie, mit +x-unabhängigem STARTEN via bash)

- Entscheidungslauf: Exit 0, Status COMPLIANT
- Audit: COMPLIANT, compliant true, demo false, block_count 12, head_hash a8875565a600c7d5f0ec46c38551c10abd4b1064680ad7e060a84ebc5d6535e5
- Audit manifest_hash: 85b652936ef1011d3514a4ac69016f4af498adc625942a31f3130dfed3e1b971 (muss exakt SHA256 von zemala_manifest.json im Push sein)
- Pre-Commit scharf: Exit 0, PRECOMMIT_ALLOWED = True
- 6 Kernartefakte: STARTEN.sh, verify_ledger.py, zemala_orchestrator.sh, zemala_manifest.json, evidence/ledger.jsonl, evidence/ledger_anchor.json
- Manifest: base_dir ., 5 Pins, alle Pfade relativ, kein absoluter Pfad im Manifest-Text
- STARTEN.sh: exec via bash, damit ein verlorenes +x nach Git-Sync den Push nie blockiert

## Ehrlich: Warum der Push nicht aus dieser Sandbox kam

In /mnt/data/zemala_fix gibt es kein .git, kein Remote und keine Credentials.
Ein `git push` von hier wäre ein behaupteter Push, kein echter.
Der Push muss in deinem Repo laufen, wo die 6 Dateien Source of Truth sind.

## Exakte Push-Befehle (in deinem Repo)

```bash
# 1. In dein Repo wechseln, Dateien dorthin kopieren (die 6 + Gate + Pre-Commit + Dockerfile)
# 2. Pre-Commit scharf schalten
bash install_precommit.sh
# oder, wenn du .githooks nutzt:
# git config core.hooksPath .githooks

# 3. Pre-Commit manuell einmal laufen lassen (muss PASS geben)
bash pre_commit_check.sh
# Erwartet: PRECOMMIT_ALLOWED.json, Exit 0

# 4. Stagen - Manifest IMMER mitstagen, wenn ein Kernartefakt gestaged ist
git add STARTEN.sh verify_ledger.py zemala_orchestrator.sh zemala_manifest.json evidence/ledger.jsonl evidence/ledger_anchor.json pre_commit_check.sh docker_cleanroom_gate.sh Dockerfile install_precommit.sh
git status

# 5. Commit - der Hook läuft automatisch nochmals alle 6 gegen das Manifest
# Bei FAIL wird der Commit blockiert, kein Commit mit Drift
git commit -m "Zemala: verify_ledger v3 FINAL, portables Manifest, Docker Gate + Pre-Commit scharf, Audit COMPLIANT"

# 6. Push - erst jetzt
git push origin main
# Danach: vollen Commit-Link hierher, z.B.
# https://github.com/<owner>/<repo>/commit/<voller SHA>
```

## Nach dem Push sofort prüfen (Dritte können das verifizieren)

```bash
git show --stat HEAD
git show HEAD:zemala_manifest.json | sha256sum
# muss = Audit manifest_hash sein
git show HEAD:evidence/ledger_audit.json
# muss COMPLIANT, demo false, head + count = Anker sein
```

## Was der Push NICHT beweist

- Audit beweist nur den Zustand zum Timestamp des Laufs.
- Kein Beweis für April/Mai 2025. Git-Daten sind frei setzbar.
- Erst der öffentliche Commit-Link macht es für Dritte verifizierbar.
