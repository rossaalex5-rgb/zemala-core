#!/bin/bash
# docker_cleanroom_gate.sh - Docker Clean Room Gate, alle 6 gegen Manifest, Commit erst bei 100%
# Reihenfolge FIX: Audit wird NACH dem Orchestrator-Lauf geprüft, nicht davor. Frische Kopie hat kein Audit.
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_FILE="$SCRIPT_DIR/zemala_manifest.json"
AUDIT_FILE="$SCRIPT_DIR/evidence/ledger_audit.json"
ALLOWED_FILE="$SCRIPT_DIR/COMMIT_ALLOWED.json"
BLOCKED_FILE="$SCRIPT_DIR/COMMIT_BLOCKED.json"
rm -f "$ALLOWED_FILE" "$BLOCKED_FILE"
TOTAL=0; PASSED=0
fail_gate() { echo "❌ GATE FAIL: $1"; python3 - "$BLOCKED_FILE" "$1" <<'PYEOF'
import sys, json, pathlib, datetime
p=pathlib.Path(sys.argv[1]); p.write_text(json.dumps({"timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "commit_allowed": False, "reason": sys.argv[2]}, indent=2)+"\n"); print(f"COMMIT_BLOCKED: {p}")
PYEOF
 echo "COMMIT FREIGABE: NEIN"; exit 1; }
check() { TOTAL=$((TOTAL+1)); if [ "$1" -eq 0 ]; then PASSED=$((PASSED+1)); echo "✅ [$PASSED/$TOTAL] $2"; else fail_gate "$2"; fi; }
echo "=== ZEMALA Docker Clean Room Gate - Alle 6 gegen Manifest ==="
ZEMALA_SET="$(compgen -e 2>/dev/null | grep '^ZEMALA_' || true)"; if [ -n "$ZEMALA_SET" ]; then fail_gate "Env-Lock: ZEMALA_* gesetzt"; fi; check 0 "Env-Lock: keine ZEMALA_*"
if [ ! -f "$MANIFEST_FILE" ]; then fail_gate "Manifest fehlt"; fi
if grep -q "/mnt/" "$MANIFEST_FILE" || grep -q "/home/" "$MANIFEST_FILE"; then fail_gate "Manifest enthaelt absoluten Pfad"; fi
python3 - "$MANIFEST_FILE" <<'PYEOF'
import sys, json, pathlib
m=json.loads(pathlib.Path(sys.argv[1]).read_text()); assert m.get("base_dir")=="."; assert len(m["files"])==5
for rel,info in m["files"].items(): assert not pathlib.Path(info["path"]).is_absolute()
print("Manifest portabel: base_dir ., 5 Pins, alle relativ")
PYEOF
check $? "Manifest portabel"
python3 - "$MANIFEST_FILE" <<'PYEOF'
import sys, json, hashlib, pathlib
m=json.loads(pathlib.Path(sys.argv[1]).read_text()); d=pathlib.Path(sys.argv[1]).parent
for rel,info in m["files"].items():
 p=d/info["path"]; assert p.exists(); h=hashlib.sha256(p.read_bytes()).hexdigest(); assert h==info["sha256"], f"Hash-Mismatch {info['path']}"
 print(f"OK {info['path']} {h[:16]}...")
print("Alle 5 Pins stimmen")
PYEOF
check $? "Hashes: alle 5 Pins stimmen"
MANIFEST_HASH="$(sha256sum "$MANIFEST_FILE" | cut -d' ' -f1)"; echo "Manifest-Hash: $MANIFEST_HASH"
python3 "$SCRIPT_DIR/verify_ledger.py" "$SCRIPT_DIR/evidence/ledger.jsonl" --anchor "$SCRIPT_DIR/evidence/ledger_anchor.json"
check $? "Verifier: 12 Bloecke + Anker-Zwang"
echo "--- Orchestrator Voll-Lauf (STARTEN.sh) erzeugt frisches Audit ---"
(cd "$SCRIPT_DIR" && bash STARTEN.sh)
check $? "Orchestrator Voll-Lauf: COMPLIANT"
echo "--- Audit gegen Manifest + Anker (NACH Orchestrator) ---"
python3 - "$AUDIT_FILE" "$MANIFEST_HASH" "$SCRIPT_DIR/evidence/ledger_anchor.json" <<'PYEOF'
import sys, json, pathlib
a=json.loads(pathlib.Path(sys.argv[1]).read_text()); an=json.loads(pathlib.Path(sys.argv[3]).read_text())
assert a.get("manifest_hash")==sys.argv[2], "Audit manifest_hash mismatch"; assert a.get("status")=="COMPLIANT"; assert a.get("compliant") is True; assert a.get("demo") is False; assert a.get("checks_failed")==[]
assert a["head_hash"]==an["head_hash"]; assert a["block_count"]==an["block_count"]; assert a["ledger_file"]=="evidence/ledger.jsonl"
print(f"Audit OK: COMPLIANT, manifest_hash + Anker stimmen, head {an['head_hash'][:16]}..., count {an['block_count']}")
PYEOF
check $? "Audit gegen Manifest + Anker: COMPLIANT, Hashes stimmen"
echo "=== GATE: $PASSED/$TOTAL ==="
if [ "$PASSED" -eq "$TOTAL" ] && [ "$TOTAL" -ge 6 ]; then
 python3 - "$ALLOWED_FILE" "$MANIFEST_HASH" <<'PYEOF'
import sys, json, pathlib, datetime, hashlib
p=pathlib.Path(sys.argv[1]); base=p.parent; hashes={rel: hashlib.sha256((base/rel).read_bytes()).hexdigest() for rel in ["STARTEN.sh","verify_ledger.py","zemala_orchestrator.sh","zemala_manifest.json","evidence/ledger.jsonl","evidence/ledger_anchor.json"]}
p.write_text(json.dumps({"timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "commit_allowed": True, "validation": "100%", "checks_passed": "6/6", "manifest_hash": sys.argv[2], "hashes": hashes}, indent=2)+"\n"); print(f"COMMIT_ALLOWED: {p}")
PYEOF
 echo "COMMIT FREIGABE: JA - 100%"; exit 0; else fail_gate "Nicht alle Checks: $PASSED/$TOTAL"; fi
