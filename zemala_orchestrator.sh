#!/bin/bash
# zemala_orchestrator.sh - Zentraler Zemala Master-Orchestrator, fail-closed, Prod-only.
# STARTEN.sh ist nur ein duenner Delegator (exec zemala_orchestrator.sh) und enthaelt
# KEINE eigenen Checks. Der Orchestrator ruft STARTEN.sh NICHT auf (sonst Rekursion).
# Dadurch gilt: STARTEN laeuft nur, wenn Env-Lock + Manifest-Check bestehen - sonst gar nichts.
# Fest verdrahtet an zemala_manifest.json. Kein manueller Eingriff, keine weichen Env-Variablen.
# Reihenfolge: 0 env_lock (Gate, VOR jedem anderen Check), 1 manifest_hash_check,
#   2 config_scan, 3 process_scan, 4 ledger_anchor, 5 node, 6 audit_write (+ Audit-Nachpruefung).
# Harte Regel: JEDE gesetzte ZEMALA_* (auch leer, auch ZEMALA_DEMO=1, auch ZEMALA_PROD=1)
#   = FAIL + NON-COMPLIANT + Exit 1. Nur Variablennamen geloggt, nie Werte.
# Kein Secret, kein Cloud-Key. Kein Netzwerk ausser lokalem Node-Check.
# Bidirektional: Manifest nennt SHA256 von verify + STARTEN + Ledger + Anker.
#   Audit nennt SHA256 des Manifests zurueck (manifest_hash). Stimmt eines nicht -> FAIL.
# Stale Audit: wird zu Laufbeginn geloescht. Bei FAIL ein frisches NON-COMPLIANT-Audit als Spur.
set -u
if [ "$#" -gt 0 ]; then echo "❌ FAIL: Orchestrator nimmt keine Argumente: $*"; echo "Status: NON-COMPLIANT"; echo "NON-COMPLIANT"; exit 1; fi
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MANIFEST_FILE="$SCRIPT_DIR/zemala_manifest.json"
VERIFY_FILE="$SCRIPT_DIR/verify_ledger.py"
LEDGER_FILE="$SCRIPT_DIR/evidence/ledger.jsonl"
ANCHOR_FILE="$SCRIPT_DIR/evidence/ledger_anchor.json"
AUDIT_FILE="$SCRIPT_DIR/evidence/ledger_audit.json"
NODE_URL="http://localhost:8085/status"
MANIFEST_HASH=""; FAILURES=(); PASSES=()
add_fail() { FAILURES+=("$1"); echo "❌ $1"; }
add_pass() { PASSES+=("$1"); echo "✅ $1"; }
TMP_OUT="$(mktemp /tmp/zemala_orch_XXXXXX)"; trap 'rm -f "$TMP_OUT"' EXIT

# Frisches NON-COMPLIANT-Audit (Spur). $1 = Grund.
write_fail_audit() {
  python3 - "$AUDIT_FILE" "$1" "$MANIFEST_HASH" > "$TMP_OUT" 2>&1 <<'PYEOF' || rm -f "$AUDIT_FILE"
import sys, json, pathlib, datetime
audit_file, reason, mh = sys.argv[1:4]
data = {"timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "status": "NON-COMPLIANT", "compliant": False, "demo": False, "mode": "prod",
  "env_overrides": [], "ledger_file": "evidence/ledger.jsonl", "verify_script": "verify_ledger.py",
  "block_count": 0, "head_hash": "", "manifest_hash": mh, "checks_passed": [], "checks_failed": [reason],
  "method": "fail-closed: Orchestrator FAIL, frisches NON-COMPLIANT-Audit als Spur.",
  "note": "Dieser Report beweist keine historische Existenz vor dem Timestamp."}
p = pathlib.Path(audit_file); p.parent.mkdir(parents=True, exist_ok=True)
tmp = p.with_suffix(".json.tmp"); tmp.write_text(json.dumps(data, indent=2) + "\n"); tmp.replace(p)
print("Audit-Report geschrieben: " + audit_file)
PYEOF
}
fail_exit() { echo "❌ FAIL: $1"; write_fail_audit "$1"; echo "Status: NON-COMPLIANT"; echo "NON-COMPLIANT"; exit 1; }
echo "=== ZEMALA Master-Orchestrator (Prod) ==="
echo "Manifest: $MANIFEST_FILE"; echo "Node-URL (gepinnt): $NODE_URL"; echo ""
# --- 0. Env-Lock (Gate), VOR jedem anderen Check. Nur Namen, nie Werte. ---
echo "--- 0. Env-Lock (Gate) ---"
ZEMALA_SET=()
while IFS= read -r _v; do case "$_v" in ZEMALA_*) ZEMALA_SET+=("$_v");; esac; done < <(compgen -e 2>/dev/null || true)
if [ -f "$MANIFEST_FILE" ]; then MANIFEST_HASH="$(sha256sum "$MANIFEST_FILE" 2>/dev/null | cut -d' ' -f1)"; fi
rm -f "$AUDIT_FILE"; echo "Stale Audit zu Laufbeginn geloescht: $AUDIT_FILE"
if [ "${#ZEMALA_SET[@]}" -gt 0 ]; then echo "❌ ZEMALA_* gesetzt (nur Namen): ${ZEMALA_SET[*]}"; fail_exit "Env-Lock: ZEMALA_* in Prod verboten - gesetzt: ${ZEMALA_SET[*]} (nur Namen geloggt, kein Wert)"; fi
echo "✅ Env-Lock: keine ZEMALA_* gesetzt"
# --- 1. Manifest-Hash-Check ---
echo ""; echo "--- 1. Manifest-Hash-Check ---"
if [ ! -f "$MANIFEST_FILE" ]; then fail_exit "Manifest fehlt: $MANIFEST_FILE"; fi
if [ -z "$MANIFEST_HASH" ]; then fail_exit "Manifest-Hash konnte nicht berechnet werden"; fi
python3 - "$MANIFEST_FILE" > "$TMP_OUT" 2>&1 <<'PYEOF'
import sys, json, hashlib, pathlib
m = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
files = m["files"]
assert isinstance(files, dict) and len(files) == 5, "Manifest muss exakt 5 Dateien pinnen (6. ist Manifest selbst via manifest_hash)"
assert m.get("node_url") == "http://localhost:8085/status", "Manifest node_url falsch"
assert m.get("allowed_env_zemala") == [], "Manifest allowed_env_zemala muss [] sein"
assert m.get("execution_order") == ["env_lock","manifest_hash_check","config_scan","process_scan","ledger_anchor","node","audit_write"], "Manifest execution_order falsch"
assert m.get("base_dir") == ".", "Manifest base_dir muss \".\" sein (portabel, kein absoluter Pfad)"
# Portabel: Kein absoluter Pfad im Manifest - weder in files noch in Textfeldern
manifest_text = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
assert "/mnt/" not in manifest_text and "/home/" not in manifest_text and "C:\\" not in manifest_text, "Manifest enthaelt absoluten Pfad - nicht portabel"
for rel, info in files.items():
    assert not pathlib.Path(info["path"]).is_absolute(), "Manifest-Pfad muss relativ sein: " + info["path"]
    assert not info["path"].startswith("/"), "Manifest-Pfad darf nicht mit / beginnen: " + info["path"]
import os
script_dir = os.environ.get("ZEMALA_SCRIPT_DIR", "")
# SCRIPT_DIR wird vom Orchestrator nicht via Env gesetzt (JEDE ZEMALA_* = FAIL), deshalb Manifest-Pfad relativ zum Manifest-File auflösen
manifest_dir = pathlib.Path(sys.argv[1]).parent
for rel, info in files.items():
    raw = info["path"]
    p = pathlib.Path(raw)
    if not p.is_absolute():
        p = manifest_dir / raw
    assert p.exists(), "Datei fehlt: " + info["path"]
    assert hashlib.sha256(p.read_bytes()).hexdigest() == info["sha256"], "Hash-Mismatch: " + info["path"]
print("MANIFEST_OK")
PYEOF
if [ "$?" -ne 0 ]; then cat "$TMP_OUT"; fail_exit "Manifest-Hash-Check: eine gepinnte Datei wurde geaendert / fehlt / Manifest manipuliert"; fi
cat "$TMP_OUT"; echo "✅ Manifest-Hash-Check: alle 5 Dateien stimmen (6. = Manifest selbst via manifest_hash, Manifest-Hash: $MANIFEST_HASH)"
# --- 2. Config-Scan (nur Pfade, kein Inhalt, kein Secret) ---
echo ""; echo "--- 2. Persistente Config / Credentials ---"
CONFIG_FAIL=0
for REL in ".gemini" ".gemini.json" ".config/gemini" ".config/gcloud" ".config/google" ".config/google-cloud-sdk" ".config/openai" ".openai" ".anthropic" ".config/anthropic" ".config/Code/User/globalStorage" ".cache/gemini"; do
  if [ -e "$HOME/$REL" ]; then echo "❌ Persistente Cloud-Config gefunden: $REL"; CONFIG_FAIL=1; fi
done
if [ -d "$HOME/.config" ]; then
  FOUND="$(find "$HOME/.config" -maxdepth 3 \( -name "*gemini*" -o -name "*gcloud*" -o -name "application_default_credentials.json" -o -name "oauth_creds*" -o -name "*openai*" \) 2>/dev/null | head -n 20)"
  if [ -n "$FOUND" ]; then echo "❌ Persistente Credentials im Scan gefunden:"; echo "$FOUND" | sed 's/^/   - /'; CONFIG_FAIL=1; fi
fi
if [ "$CONFIG_FAIL" -eq 1 ]; then add_fail "Cloud isolation: Persistente Cloud-Credentials / Config auf dem Geraet gefunden"; else add_pass "Cloud isolation (Config): Keine persistente Gemini/gcloud/openai Config gefunden"; fi
# Cloud-Keys in Env (nur Namen)
ENV_FAIL=0
for VAR in GEMINI_API_KEY GOOGLE_API_KEY GOOGLE_GENAI_API_KEY GEMINI_API_KEYS OPENAI_API_KEY ANTHROPIC_API_KEY CLAUDE_API_KEY AZURE_OPENAI_API_KEY GROQ_API_KEY MISTRAL_API_KEY; do
  if [ -n "${!VAR:-}" ]; then echo "❌ Env-Key gesetzt: $VAR (Wert wird NICHT ausgegeben)"; ENV_FAIL=1; fi
done
if [ "$ENV_FAIL" -eq 1 ]; then add_fail "Cloud isolation: Externer API-Key in Umgebungsvariablen gefunden"; else add_pass "Cloud isolation (Env): Kein externer API-Key in Env"; fi
# --- 3. Prozess-Scan (/proc, nur PID + Token, nie volle Args) ---
echo ""; echo "--- 3. Laufende Cloud-Prozesse ---"
python3 - > "$TMP_OUT" 2>&1 <<'PYEOF'
import os
BLOCK = {"gemini","gemini-cli","gemini_cli","google-gemini","gcloud","openai","openai-cli","claude","anthropic","copilot","codex","cursor"}
INTERP = {"node","nodejs","bun","deno","ruby","perl","python","python3"}
def norm(n):
    b = os.path.basename(n or "").lower()
    for s in (".exe",".js",".mjs",".cjs",".py"):
        if b.endswith(s): b = b[:-len(s)]; break
    return b
self_pid = os.getpid(); parent_pid = os.getppid(); hits = []
for name in os.listdir("/proc"):
    if not name.isdigit(): continue
    pid = int(name)
    if pid in (self_pid, parent_pid): continue
    try:
        with open(f"/proc/{pid}/cmdline","rb") as f: args = [a.decode("utf-8","ignore") for a in f.read().split(b"\x00") if a]
        with open(f"/proc/{pid}/comm") as f: comm = f.read().strip()
    except Exception: continue
    if not args: continue
    if "zemala_orchestrator.sh" in " ".join(args) or "STARTEN.sh" in " ".join(args): continue
    cands = [(norm(args[0]), "argv0"), (norm(comm), "comm")]
    if norm(args[0]) in INTERP and len(args) > 1: cands.append((norm(args[1]), "interpreter-arg"))
    for tok, via in cands:
        if tok in BLOCK: hits.append(f"HIT pid={pid} token={tok} via={via}"); break
print("\n".join(hits) if hits else "PROC_OK")
PYEOF
PROC_RC=$?
cat "$TMP_OUT"
if grep -q "^HIT " "$TMP_OUT"; then add_fail "Cloud isolation: Aktiver Cloud-CLI Prozess laeuft auf diesem Geraet"; else add_pass "Cloud isolation (Prozesse): Kein aktiver Cloud-CLI Prozess gefunden"; fi
# --- 4. Ledger + Anker (verify_ledger.py v3, Anker Pflicht) ---
echo ""; echo "--- 4. Ledger-Verifikation ---"
LEDGER_OUT=""; LEDGER_CODE=1; BLOCK_COUNT=0; HEAD_HASH=""
if [ ! -f "$ANCHOR_FILE" ]; then add_fail "Ledger Integrity: Externer Anker fehlt ($ANCHOR_FILE) - Neuverkettung/Truncation/Append nicht erkennbar"
elif [ -f "$VERIFY_FILE" ] && [ -f "$LEDGER_FILE" ]; then
  LEDGER_OUT="$(python3 "$VERIFY_FILE" "$LEDGER_FILE" --anchor-file "$ANCHOR_FILE" 2>&1)"; LEDGER_CODE=$?
  echo "$LEDGER_OUT"
  if [ "$LEDGER_CODE" -eq 0 ]; then add_pass "Ledger Integrity: Ledger valid + Anker OK"; else add_fail "Ledger Integrity: verify_ledger.py FAILED (Exit $LEDGER_CODE)"; fi
else add_fail "Ledger Integrity: verify_ledger.py oder Ledger-Datei fehlt ($VERIFY_FILE / $LEDGER_FILE)"; fi
if [ "$LEDGER_CODE" -eq 0 ]; then
  BLOCK_COUNT="$(printf '%s' "$LEDGER_OUT" | python3 -c "import sys,re; m=re.search(r'Alle (\d+) Bloecke', sys.stdin.read()); print(m.group(1) if m else '0')" 2>/dev/null || echo "0")"
  HEAD_HASH="$(printf '%s' "$LEDGER_OUT" | python3 -c "import sys,re; m=re.search(r'Head Hash: ([0-9a-f]{64})', sys.stdin.read()); print(m.group(1) if m else '')" 2>/dev/null || echo "")"
  if [ -z "$HEAD_HASH" ] || [ "$BLOCK_COUNT" = "0" ]; then
    for _i in "${!PASSES[@]}"; do if [ "${PASSES[$_i]}" = "Ledger Integrity: Ledger valid + Anker OK" ]; then unset "PASSES[$_i]"; fi; done
    add_fail "Ledger Integrity: Verifier-Output ohne verifizierten Head/Count - Fake-Verifier nicht ausgeschlossen"; BLOCK_COUNT=0; HEAD_HASH=""
  fi
fi
# --- 5. Node (Pflichtdienst, KEIN Skip) ---
echo ""; echo "--- 5. Pflichtdienst Node Service ---"
if curl -s --max-time 2 -o /dev/null -w "%{http_code}" "$NODE_URL" 2>/dev/null | grep -q "200"; then add_pass "Node service: reachable ($NODE_URL)"; else add_fail "Node service unreachable ($NODE_URL)"; fi
# --- 6. Gesamt + Audit schreiben (immer letzter Schritt) ---
echo ""; echo "=== GESAMTSTATUS ==="
if [ "${#FAILURES[@]}" -eq 0 ]; then STATUS="COMPLIANT"; COMPLIANT_BOOL="true"; echo "Status: COMPLIANT"; echo "Alle Checks gruen."
else STATUS="NON-COMPLIANT"; COMPLIANT_BOOL="false"; echo "Status: NON-COMPLIANT"; echo "Fehlgeschlagene Checks (${#FAILURES[@]}):"; for f in "${FAILURES[@]}"; do echo " - $f"; done; fi
TIMESTAMP="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"; SEP="$(printf '\x1f')"
FAILED_JOINED=""; PASSED_JOINED=""
if [ "${#FAILURES[@]}" -gt 0 ]; then FAILED_JOINED="$(IFS="$SEP"; printf '%s' "${FAILURES[*]}")"; fi
if [ "${#PASSES[@]}" -gt 0 ]; then PASSED_JOINED="$(IFS="$SEP"; printf '%s' "${PASSES[*]}")"; fi
python3 - "$AUDIT_FILE" "$TIMESTAMP" "$STATUS" "$COMPLIANT_BOOL" "$BLOCK_COUNT" "$HEAD_HASH" "$FAILED_JOINED" "$PASSED_JOINED" "$LEDGER_FILE" "$MANIFEST_HASH" > "$TMP_OUT" 2>&1 <<'PYEOF'
import sys, json, pathlib
if len(sys.argv) != 11:
    print("FEHLER Audit: falsche Argumentzahl", file=sys.stderr); sys.exit(2)
audit_file, ts, status, comp, blocks, head, fails_raw, passes_raw, ledger_file, mh = sys.argv[1:11]
# Audit ledger_file immer relativ (evidence/ledger.jsonl), nie absoluter lokaler Pfad
if ledger_file.endswith("evidence/ledger.jsonl"):
    ledger_file = "evidence/ledger.jsonl"
assert status in ("COMPLIANT", "NON-COMPLIANT") and comp in ("true", "false")
compliant = (comp == "true")
assert (status == "COMPLIANT") == compliant, "Status/compliant Widerspruch"
block_count = int(blocks)
assert block_count >= 0
if head: assert len(head) == 64 and all(c in "0123456789abcdef" for c in head)
if mh: assert len(mh) == 64 and all(c in "0123456789abcdef" for c in mh)
assert not (compliant and (block_count == 0 or not head)), "COMPLIANT ohne Head unmoeglich"
SEP = "\x1f"
fails = [s for s in fails_raw.split(SEP) if s] if fails_raw else []
passes = [s for s in passes_raw.split(SEP) if s] if passes_raw else []
assert not (compliant and fails), "COMPLIANT mit failed-Liste"
assert not ((not compliant) and not fails), "NON-COMPLIANT ohne failed-Liste"
for c in passes: assert "uebersprungen" not in c and "Skip" not in c, "Node-Skip als Pass"
data = {"timestamp": ts, "status": status, "compliant": compliant, "demo": False, "mode": "prod",
  "env_overrides": [], "ledger_file": ledger_file, "verify_script": "verify_ledger.py",
  "block_count": block_count, "head_hash": head, "manifest_hash": mh,
  "checks_passed": passes, "checks_failed": fails,
  "method": "fail-closed: COMPLIANT nur wenn alle Checks gruen. EINE Regel: JEDE ZEMALA_* = FAIL. Prod ist Default, kein Demo-Modus. Env-Lock + Manifest + Config + Prozesse + Ledger/Anker + Node.",
  "note": "Dieser Report beweist keine historische Existenz vor dem Timestamp. Er beweist nur den Zustand zum Zeitpunkt des Laufs."}
p = pathlib.Path(audit_file); p.parent.mkdir(parents=True, exist_ok=True)
tmp = p.with_suffix(".json.tmp"); tmp.write_text(json.dumps(data, indent=2) + "\n"); tmp.replace(p)
print("Audit-Report geschrieben: " + audit_file)
PYEOF
AUDIT_RC=$?
cat "$TMP_OUT"
if [ "$AUDIT_RC" -ne 0 ]; then echo "❌ Audit-Report konnte nicht geschrieben werden"; rm -f "$AUDIT_FILE"; echo "Status: NON-COMPLIANT"; echo "NON-COMPLIANT"; exit 1; fi
if [ ! -f "$AUDIT_FILE" ]; then echo "❌ Audit fehlt nach dem Schreiben"; echo "Status: NON-COMPLIANT"; echo "NON-COMPLIANT"; exit 1; fi
# --- Audit-Nachpruefung: COMPLIANT trotz rotem Check muss hier sterben. ---
python3 - "$AUDIT_FILE" "$MANIFEST_HASH" "$ANCHOR_FILE" > "$TMP_OUT" 2>&1 <<'PYEOF'
import sys, json, pathlib
a = json.loads(pathlib.Path(sys.argv[1]).read_text())
anchor = json.loads(pathlib.Path(sys.argv[3]).read_text())
assert a.get("status") in ("COMPLIANT", "NON-COMPLIANT")
assert a.get("compliant") == (a["status"] == "COMPLIANT")
assert a.get("demo") is False, "demo muss false sein"
assert a.get("manifest_hash") == sys.argv[2], "manifest_hash mismatch"
if a["status"] == "COMPLIANT":
    assert a.get("checks_failed") == [], "COMPLIANT mit failed-Liste"
    assert a.get("block_count") == anchor["block_count"], "block_count != Anker"
    assert a.get("head_hash") == anchor["head_hash"], "head_hash != Anker"
else:
    assert a.get("checks_failed"), "NON-COMPLIANT ohne failed-Liste"
print("AUDIT_OK")
PYEOF
if [ "$?" -ne 0 ]; then cat "$TMP_OUT"; echo "❌ Audit-Nachpruefung FAILED"; rm -f "$AUDIT_FILE"; echo "Status: NON-COMPLIANT"; echo "NON-COMPLIANT"; exit 1; fi
cat "$TMP_OUT"; echo "✅ Audit-Nachpruefung: status + demo=false + manifest_hash + Anker stimmen"
echo ""; echo "Status: $STATUS"; echo "$STATUS"
if [ "$STATUS" = "COMPLIANT" ]; then exit 0; else exit 1; fi
