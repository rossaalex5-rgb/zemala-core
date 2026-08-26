#!/data/data/com.termux/files/usr/bin/bash
set -u

# ZEMALA INTENT & AUTH GATE
# Pre-Ledger admissibility verification

INTENT_FILE="${1:-intent.json}"

fail() {
    echo "[-] INTENT GATE: FAIL"
    echo "[-] REASON: $1"
    echo "[-] EXECUTION: BLOCKED"
    exit 1
}

echo "=== {ZEMALA CORE} INTENT & AUTH GATE ==="

[ -f "$INTENT_FILE" ] || fail "Intent file not found"

command -v python3 >/dev/null 2>&1 \
    || fail "python3 unavailable"

python3 - "$INTENT_FILE" <<'PY'
import json
import sys

path = sys.argv[1]

try:
    with open(path, encoding="utf-8") as f:
        intent = json.load(f)
except Exception as e:
    print(f"INVALID_JSON: {e}")
    sys.exit(2)

required = ["intent", "auth", "payload"]

for key in required:
    if key not in intent:
        print(f"MISSING_FIELD: {key}")
        sys.exit(3)

if not isinstance(intent["intent"], str) or not intent["intent"].strip():
    print("INVALID_INTENT")
    sys.exit(4)

auth = intent["auth"]

if not isinstance(auth, dict):
    print("INVALID_AUTH_STRUCTURE")
    sys.exit(5)

if auth.get("authorized") is not True:
    print("AUTHORIZATION_FAILED")
    sys.exit(6)

payload = intent["payload"]

if not isinstance(payload, dict) or not payload:
    print("SEMANTIC_PAYLOAD_INVALID")
    sys.exit(7)

print("STRUCTURE: PASS")
print("AUTHORIZATION: PASS")
print("SEMANTIC ADMISSIBILITY: PASS")
PY

RC=$?

if [ "$RC" -ne 0 ]; then
    fail "Pre-ledger admissibility check rejected intent"
fi

echo "[+] INTENT GATE: PASS"
echo "[+] EXECUTION: ADMISSIBLE"
exit 0
