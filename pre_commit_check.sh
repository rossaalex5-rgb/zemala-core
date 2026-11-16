#!/bin/bash
# pre_commit_check.sh - Automatisierte Pre-Commit-Prüfroutine, letzter Schritt vor jedem Git Commit
# Stellt sicher: Unmittelbar vor jedem Commit werden alle 6 Kernartefakte gegen das Manifest validiert.
# So wird Auseinanderdriften von Code und Dokumentation im letzten Moment ausgeschlossen.
# 6 Kernartefakte: STARTEN.sh, verify_ledger.py, zemala_orchestrator.sh, zemala_manifest.json, evidence/ledger.jsonl, evidence/ledger_anchor.json
# Ergebnis: PASS -> Commit wird freigegeben (PRECOMMIT_ALLOWED.json), Exit 0
#           FAIL -> Commit wird BLOCKIERT (PRECOMMIT_BLOCKED.json), Exit 1, kein Commit
# Aufruf: Manuell: bash pre_commit_check.sh
#        Automatisch: als .git/hooks/pre-commit (siehe install_precommit.sh)
# Kein Secret wird geloggt, nur Pfade, Check-Namen, Hashes.
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Wenn als .git/hooks/pre-commit aufgerufen, ist SCRIPT_DIR = .git/hooks -> Repo-Root finden
if [ "$(basename "$SCRIPT_DIR")" = "hooks" ]; then SCRIPT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"; fi
MANIFEST_FILE="$SCRIPT_DIR/zemala_manifest.json"
AUDIT_FILE="$SCRIPT_DIR/evidence/ledger_audit.json"
ALLOWED_FILE="$SCRIPT_DIR/PRECOMMIT_ALLOWED.json"
BLOCKED_FILE="$SCRIPT_DIR/PRECOMMIT_BLOCKED.json"
rm -f "$ALLOWED_FILE" "$BLOCKED_FILE"
TOTAL=0; PASSED=0
fail_pre() {
  echo "❌ PRE-COMMIT BLOCKIERT: $1"
  python3 - "$BLOCKED_FILE" "$1" <<'PYEOF'
import sys, json, pathlib, datetime
p=pathlib.Path(sys.argv[1]); p.write_text(json.dumps({"timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "commit_allowed": False, "reason": sys.argv[2]}, indent=2)+"\n"); print(f"PRECOMMIT_BLOCKED: {p}")
PYEOF
  echo "Commit wird NICHT freigegeben. Fixe den Fehler, dann erneut versuchen. Kein Commit mit Drift."
  exit 1
}
check() { TOTAL=$((TOTAL+1)); if [ "$1" -eq 0 ]; then PASSED=$((PASSED+1)); echo "✅ [$PASSED/$TOTAL] $2"; else fail_pre "$2"; fi; }
echo "=== ZEMALA Pre-Commit-Prüfung - Alle 6 gegen Manifest, unmittelbar vor Commit ==="
echo "Repo: $SCRIPT_DIR"
# 0. Env-Lock
ZEMALA_SET="$(compgen -e 2>/dev/null | grep '^ZEMALA_' || true)"; if [ -n "$ZEMALA_SET" ]; then fail_pre "Env-Lock: ZEMALA_* gesetzt: $ZEMALA_SET"; fi; check 0 "Env-Lock: keine ZEMALA_*"
# 1. Git-Status: Wenn eines der 6 im Staging ist, muss Manifest mitgestaged sein, sonst Drift
if command -v git >/dev/null 2>&1 && [ -d "$SCRIPT_DIR/.git" ]; then
  echo "--- Git-Check: Staged-Dateien gegen Manifest ---"
  STAGED="$(cd "$SCRIPT_DIR" && git diff --cached --name-only || true)"
  echo "Staged: ${STAGED:-<keine, manueller Lauf>}"
  if echo "$STAGED" | grep -q "verify_ledger.py\|STARTEN.sh\|zemala_orchestrator.sh\|evidence/ledger"; then
    if ! echo "$STAGED" | grep -q "zemala_manifest.json"; then fail_pre "Git-Drift: Kernartefakt gestaged, aber zemala_manifest.json nicht mitgestaged - Manifest-Hash waere stale"; fi
  fi
  check 0 "Git-Check: Manifest mitgestaged, wenn Kernartefakt gestaged"
else
  echo "--- Git-Check: Kein .git, übersprungen (manueller Lauf) ---"; check 0 "Git-Check: kein .git, manuell"
fi
# 2. Manifest portabel
if [ ! -f "$MANIFEST_FILE" ]; then fail_pre "Manifest fehlt"; fi
if grep -q "/mnt/" "$MANIFEST_FILE" || grep -q "/home/" "$MANIFEST_FILE"; then fail_pre "Manifest enthaelt absoluten Pfad - nicht portabel"; fi
python3 - "$MANIFEST_FILE" <<'PYEOF'
import sys, json, pathlib
m=json.loads(pathlib.Path(sys.argv[1]).read_text()); assert m.get("base_dir")=="."; assert len(m["files"])==5
for rel,info in m["files"].items(): assert not pathlib.Path(info["path"]).is_absolute()
print("Manifest portabel: base_dir ., 5 Pins, alle relativ")
PYEOF
check $? "Manifest portabel"
# 3. Hashes der 5 Pins
python3 - "$MANIFEST_FILE" <<'PYEOF'
import sys, json, hashlib, pathlib
m=json.loads(pathlib.Path(sys.argv[1]).read_text()); d=pathlib.Path(sys.argv[1]).parent
for rel,info in m["files"].items():
 p=d/info["path"]; assert p.exists(); h=hashlib.sha256(p.read_bytes()).hexdigest(); assert h==info["sha256"], f"Hash-Mismatch {info['path']}"
 print(f"OK {info['path']} {h[:16]}...")
print("Alle 5 Pins stimmen")
PYEOF
check $? "Hashes: alle 5 Pins stimmen"
# 4. Verifier + Anker
python3 "$SCRIPT_DIR/verify_ledger.py" "$SCRIPT_DIR/evidence/ledger.jsonl" --anchor "$SCRIPT_DIR/evidence/ledger_anchor.json" > /tmp/zemala_precommit_verify.txt 2>&1
VERIFY_RC=$?; cat /tmp/zemala_precommit_verify.txt | tail -n 3
check $VERIFY_RC "Verifier: 12 Bloecke + Anker-Zwang"
# 5. Orchestrator Voll-Lauf mit ephemerem Node-Stub (kein Skip)
echo "--- Orchestrator Voll-Lauf mit ephemerem Node-Stub ---"
cat > /tmp/zemala_precommit_stub.py <<'PYEOF'
import http.server, socketserver
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=="/status":
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404); self.end_headers()
    def log_message(self,*a,**k): pass
socketserver.TCPServer(("127.0.0.1",8085),H).serve_forever()
PYEOF
python3 /tmp/zemala_precommit_stub.py & STUB_PID=$!; sleep 1
for _i in 1 2 3 4 5; do if curl -s --max-time 1 http://localhost:8085/status > /dev/null 2>&1; then echo "Node-Stub erreichbar (Versuch $_i)"; break; fi; echo "Warte auf Node-Stub (Versuch $_i)..."; sleep 1; done
(cd "$SCRIPT_DIR" && bash STARTEN.sh > /tmp/zemala_precommit_starten.txt 2>&1); STARTEN_RC=$?
kill $STUB_PID 2>/dev/null || true
cat /tmp/zemala_precommit_starten.txt | tail -n 8
check $STARTEN_RC "Orchestrator Voll-Lauf: COMPLIANT"
# 6. Audit gegen Manifest + Anker
MANIFEST_HASH="$(sha256sum "$MANIFEST_FILE" | cut -d' ' -f1)"
python3 - "$AUDIT_FILE" "$MANIFEST_HASH" "$SCRIPT_DIR/evidence/ledger_anchor.json" <<'PYEOF'
import sys, json, pathlib
a=json.loads(pathlib.Path(sys.argv[1]).read_text()); an=json.loads(pathlib.Path(sys.argv[3]).read_text())
assert a.get("manifest_hash")==sys.argv[2]; assert a.get("status")=="COMPLIANT"; assert a.get("compliant") is True; assert a.get("demo") is False; assert a.get("checks_failed")==[]; assert a["head_hash"]==an["head_hash"]; assert a["block_count"]==an["block_count"]
print(f"Audit OK: COMPLIANT, manifest_hash + Anker stimmen")
PYEOF
check $? "Audit gegen Manifest + Anker"
echo "=== PRE-COMMIT: $PASSED/$TOTAL ==="
if [ "$PASSED" -eq "$TOTAL" ] && [ "$TOTAL" -ge 6 ]; then
 python3 - "$ALLOWED_FILE" "$MANIFEST_HASH" <<'PYEOF'
import sys, json, pathlib, datetime, hashlib
p=pathlib.Path(sys.argv[1]); base=p.parent; hashes={rel: hashlib.sha256((base/rel).read_bytes()).hexdigest() for rel in ["STARTEN.sh","verify_ledger.py","zemala_orchestrator.sh","zemala_manifest.json","evidence/ledger.jsonl","evidence/ledger_anchor.json"]}
p.write_text(json.dumps({"timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "commit_allowed": True, "validation": "100%", "checks_passed": "6/6", "manifest_hash": sys.argv[2], "hashes": hashes}, indent=2)+"\n"); print(f"PRECOMMIT_ALLOWED: {p}")
PYEOF
 echo "PRE-COMMIT FREIGABE: JA - 100%, Commit darf jetzt laufen"; exit 0; else fail_pre "Nicht alle Checks: $PASSED/$TOTAL"; fi
