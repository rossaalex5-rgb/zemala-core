#!/usr/bin/env python3
import sys
import json
import subprocess

def main():
    try:
        raw_input = sys.stdin.read()
        req = json.loads(raw_input) if raw_input.strip() else {}
    except Exception:
        req = {}

    method = req.get("method")
    req_id = req.get("id", 1)

    if method != "a2a_hello":
        resp = {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": req_id
        }
        print(json.dumps(resp, indent=2))
        sys.exit(1)

    # Delegiere ausschließlich an das bestehende Verify-Gate
    try:
        res = subprocess.run(["bash", "scripts/verify.sh"], capture_output=True, text=True)
        rc = res.returncode
    except Exception:
        rc = 1

    if rc == 0:
        result_payload = {
            "status": "HELLO_FROM_ZEMALA",
            "integrity": "PASS",
            "logic_seed": "verified",
            "human_gate": "ACTIVE"
        }
        subprocess.run(["bash", "scripts/emit_event.sh", "A2A", "HELLO_SUCCESS", "a2a_handler"])
    else:
        result_payload = {
            "status": "HELLO_FROM_ZEMALA",
            "integrity": "FAIL"
        }
        subprocess.run(["bash", "scripts/emit_event.sh", "A2A", "HELLO_FAIL", "a2a_handler"])

    resp = {
        "jsonrpc": "2.0",
        "result": result_payload,
        "id": req_id
    }
    print(json.dumps(resp, indent=2))
    sys.exit(0 if rc == 0 else 1)

if __name__ == "__main__":
    main()
