#!/usr/bin/env bash
# Telemetrie als strukturiertes JSON - robust gegen API-Fehler
BATT=$(termux-battery-status 2>/dev/null | jq -r '.percentage // "unknown"' 2>/dev/null || echo "unknown")
DISK=$(df -h /data 2>/dev/null | awk 'NR==2 {print $4}' || echo "unknown")
GIT_REV=$(git rev-parse --short HEAD 2>/dev/null || echo "unversioned")

jq -n \
  --arg date "$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
  --arg disk "$DISK" \
  --arg batt "$BATT" \
  --arg git "$GIT_REV" \
  '{
    type: "TELEMETRY",
    timestamp: $date,
    payload: {
      disk_available: $disk,
      battery: $batt,
      git_revision: $git
    }
  }'
