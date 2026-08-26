#!/usr/bin/env bash
OUTPUT_FILE="MASTER_BUNDLE.md"
GENERATED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SOURCE_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "UNKNOWN_COMMIT")

{
  echo "# ZEMALA CORE // MASTER BUNDLE"
  echo ""
  echo "---"
  echo "### METADATEN & HERKUNFT (SSOT PROJEKTOR)"
  echo "- **SOURCE_COMMIT:** \`$SOURCE_COMMIT\`"
  echo "- **GENERATED_AT:** \`$GENERATED_AT\`"
  echo "- **SOURCE_STATE_HASH:** \`$(git rev-parse HEAD:ZEMALA_STATE.md 2>/dev/null || echo 'N/A')\`"
  echo "---"
  echo ""
  echo "## 1. STATE"
  echo "### ZEMALA_STATE.md"
  echo '```markdown'
  cat ZEMALA_STATE.md 2>/dev/null || echo "[Fehlt]"
  echo '```'
  echo ""
  echo "### AGENTS.md"
  echo '```markdown'
  cat AGENTS.md 2>/dev/null || echo "[Fehlt]"
  echo '```'
  echo ""
  echo "## 2. CONTROL"
  for file in zentrale.sh verify_intent.sh execute_intent_pipeline.sh verify_gates.sh; do
    if [ -f "$file" ]; then
      echo "### $file"
      echo '```bash'
      cat "$file"
      echo '```'
      echo ""
    fi
  done
  echo "## 3. EVIDENCE"
  echo '```jsonl'
  tail -n 50 ledger.jsonl 2>/dev/null || echo "{}"
  echo '```'
  echo ""
  echo "## 4. RETURN CONTRACT"
  echo "READ -> RECONSTRUCT -> WORK -> DISCOVER -> RETURN"
} > "$OUTPUT_FILE"
echo "Bundle generiert."
