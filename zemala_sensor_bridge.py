import json
import os
import sys
import time
import hashlib
import subprocess
from datetime import datetime, timezone

LEDGER_PATH = "core/ledger.jsonl"

def get_device_telemetry() -> dict:
    try:
        out = subprocess.check_output(["termux-battery-status"], timeout=2)
        data = json.loads(out.decode("utf-8"))
        return {
            "source": "android_battery_sensor",
            "percentage": data.get("percentage", 100),
            "plugged": data.get("plugged", "UNKNOWN"),
            "temperature_c": data.get("temperature", 25.0)
        }
    except Exception:
        pass

    cap_path = "/sys/class/power_supply/battery/capacity"
    stat_path = "/sys/class/power_supply/battery/status"
    if os.path.exists(cap_path):
        with open(cap_path, "r") as f:
            cap = int(f.read().strip())
        status = "UNKNOWN"
        if os.path.exists(stat_path):
            with open(stat_path, "r") as f:
                status = f.read().strip()
        return {
            "source": "kernel_power_supply",
            "percentage": cap,
            "plugged": status,
            "temperature_c": 26.5
        }

    load1, _, _ = os.getloadavg()
    return {
        "source": "system_telemetry_node",
        "percentage": 100,
        "cpu_load": round(load1, 2),
        "temperature_c": 25.0
    }

def append_sensor_block(force: bool = False):
    blocks = []
    if os.path.exists(LEDGER_PATH):
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    blocks.append(json.loads(line))

    prev_block = blocks[-1] if blocks else {}
    telemetry = get_device_telemetry()
    battery = telemetry.get("percentage", 100)
    temp = telemetry.get("temperature_c", 25.0)

    if battery < 15 or temp > 45.0:
        contract_state = "contradiction"
        note = f"Widerspruch: Kritischer Hardware-Zustand (Akku {battery}%, Temp {temp}C)"
    else:
        contract_state = "VERIFIED_OK"
        note = f"Hardware-Telemetrie innerhalb der Contract-Grenzen (Akku {battery}%, Temp {temp}C)"

    # Nur schreiben, wenn sich Zustand/Akku geaendert hat oder force=True
    last_tel = prev_block.get("telemetry", {})
    if not force and last_tel.get("percentage") == battery and prev_block.get("contract_state") == contract_state:
        return False

    prev_hash = hashlib.sha256(json.dumps(prev_block, sort_keys=True).encode("utf-8")).hexdigest()
    next_index = len(blocks) + 1

    new_block = {
        "index": next_index,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prev_hash": prev_hash,
        "telemetry": telemetry,
        "contract_state": contract_state,
        "note": note
    }
    new_block["hash"] = hashlib.sha256(json.dumps(new_block, sort_keys=True).encode("utf-8")).hexdigest()

    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(new_block) + "\n")

    print(f"[ZEMALA SENSOR] Block #{next_index} -> {contract_state} | Akku: {battery}% | Hash: {new_block['hash'][:12]}...")
    return True

if __name__ == "__main__":
    if "--daemon" in sys.argv:
        print("[ZEMALA SENSOR DAEMON] Aktiv (Pruef-Intervall: 5.0s, Delta-Trigger aktiv)...")
        append_sensor_block(force=True)
        while True:
            time.sleep(5)
            append_sensor_block(force=False)
    else:
        append_sensor_block(force=True)
