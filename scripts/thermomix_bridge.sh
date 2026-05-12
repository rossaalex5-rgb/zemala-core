#!/usr/bin/env bash
set -euo pipefail

# Nimmt Befehl entgegen (z.B. "Suppe kochen")
CMD_RAW="${1:-}"
if [ -z "$CMD_RAW" ]; then
  echo '{"status":"error","message":"NO_COMMAND"}'
  exit 1
fi

# 1. Normalisierung (einfach & deterministisch)
ACTION="thermo_$(echo "$CMD_RAW" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')"

# 2. Event erzeugen über das vorhandene lock_emit.sh
# Wir nutzen den TYPE "HARDWARE" für die Hardware-Ebene
bash ~/zemala-core/scripts/lock_emit.sh "HARDWARE" "$ACTION" "thermomix_v1"

# 3. Bestätigung
echo "{\"status\":\"ok\",\"action_logged\":\"$ACTION\"}"
