import os
import json
from datetime import datetime

def audit_system():
    required_files = [
        "ledger.jsonl", "ledger_seal.json", "daemon.py", 
        "pulse.py", "analyzer.py", "matrix.py", "clean.py", 
        "inference_hook.py", "agent_loop.py", "telemetry.py", 
        "metadata_optimizer.py", "ledger_analytics.py", "sealer.py", 
        "backup.py", "status_server.py", "renderer.py", "sync.sh"
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    status = "Optimal" if not missing else "Degraded"
    
    audit_report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "auditor_status": status,
        "missing_elements": missing,
        "level": "100"
    }
    
    with open("ledger_audit.json", "w") as f:
        json.dump(audit_report, f, indent=2)
        
    print(f"[ZEMALA Auditor] Audit abgeschlossen. Feldstatus: {status} (Fehlend: {len(missing)})")

if __name__ == "__main__":
    audit_system()
