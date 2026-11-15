#!/data/data/com.termux/files/usr/bin/bash
cd ~/zemala-core || exit 1

echo "[ZEMALA] Bereinige alte Prozesse..."
kill -9 $(pgrep -f "zemala_cockpit_server.py") 2>/dev/null
kill -9 $(pgrep -f "zemala_sensor_bridge.py") 2>/dev/null
kill -9 $(pgrep -f "a2a_server.py") 2>/dev/null
sleep 1

# Verhindert, dass Android die CPU im Standby drosselt
termux-wake-lock 2>/dev/null

echo "[ZEMALA] Starte Auto-Cockpit (Port 5000)..."
nohup python3 zemala_cockpit_server.py > cockpit.log 2>&1 &

echo "[ZEMALA] Starte Sensor-Daemon (5s Delta-Trigger)..."
nohup python3 zemala_sensor_bridge.py --daemon > sensor.log 2>&1 &

echo "[ZEMALA] Starte A2A-Server (Port 8080)..."
nohup python3 a2a_server.py > a2a.log 2>&1 &

sleep 1
echo "✅ ALLE DIENSTE AKTIV | Cockpit: http://localhost:5000/cockpit | A2A: http://localhost:8080/status"
