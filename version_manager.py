import json
import os
from datetime import datetime

def manage_version():
    version_file = "version_manifest.json"
    current_version = {"major": 1, "minor": 0, "patch": 100}
    
    if os.path.exists(version_file):
        try:
            with open(version_file, "r") as f:
                current_version = json.load(f)
            current_version["patch"] += 1
        except Exception:
            pass
    else:
        current_version["patch"] = 101

    current_version["last_update"] = datetime.utcnow().isoformat() + "Z"
    current_version["frequency"] = "3.47s"

    with open(version_file, "w") as f:
        json.dump(current_version, f, indent=2)

    v_str = f"{current_version['major']}.{current_version['minor']}.{current_version['patch']}"
    print(f"[ZEMALA Version] System-Release stabil auf Version v{v_str} gesetzt.")

if __name__ == "__main__":
    manage_version()
