#!/data/data/com.termux/files/usr/bin/bash
set -u

ZCORE="/storage/emulated/0/_zcore"
OUTBOX="$ZCORE/outbox"
LEDGER="$ZCORE/ledger/observations.jsonl"

mkdir -p "$OUTBOX"

TEST_ID="INVERSION_TEST_$(date -u +%Y%m%dT%H%M%SZ)"
PAYLOAD="$OUTBOX/${TEST_ID}.json"

echo "=== ZEMALA INVERSION TEST ==="
echo "TEST_ID=$TEST_ID"
echo

echo "--- PRE-STATE ---"
if [ -f "$LEDGER" ]; then
    sha256sum "$LEDGER"
    wc -l "$LEDGER"
else
    echo "LEDGER_NOT_FOUND"
fi
echo

cat > "$PAYLOAD" <<JSON
{
  "request_id": "$TEST_ID",
  "correlation_id": "INVERSION_TEST",
  "type": "PROPOSAL_OBSERVATION",
  "timestamp": "2099-01-01T00:00:00Z",
  "prev_hash": "TOXIC_INVALID_PREV_HASH",
  "proposal": {
    "action": "echo TOXIC_EXECUTION_ATTEMPT",
    "shell": "rm -rf /",
    "authorization": "FORGED",
    "logic": "INVALID_CHRONOLOGY"
  }
}
JSON

echo "--- TOXIC PROPOSAL WRITTEN ---"
cat "$PAYLOAD"
echo

echo "--- VERIFY ---"
./verify.sh
VERIFY_EXIT=$?
echo "VERIFY_EXIT=$VERIFY_EXIT"
echo

echo "--- POST-STATE ---"
if [ -f "$LEDGER" ]; then
    sha256sum "$LEDGER"
    wc -l "$LEDGER"
else
    echo "LEDGER_NOT_FOUND"
fi
echo

echo "--- PROPOSAL STILL PRESENT? ---"
if [ -f "$PAYLOAD" ]; then
    echo "YES: verifier did not consume/delete proposal"
else
    echo "NO: proposal was consumed/moved"
fi

echo
echo "=== RESULT MUST BE INTERPRETED, NOT ASSUMED ==="
