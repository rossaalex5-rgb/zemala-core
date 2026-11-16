#!/data/data/com.termux/files/usr/bin/bash
set -e
cd ~/zemala
rclone copy zemala_live_state.json gdrive_zemala:REKONSTRUKTION/2026-11-06T04-41/ --checksum -P
echo "SYNC DONE $(date) - WATCHER $(pgrep -f watch_all) BRIDGE $(pgrep -f bridge)"
