import py_compile, sys, json, os

try:
    py_compile.compile("zemala_cockpit_server.py", doraise=True)
    py_compile.compile("zemala_sigil.py", doraise=True); py_compile.compile("zemala_sensor_bridge.py", doraise=True)
    if os.path.exists("core/ledger.jsonl"):
        with open("core/ledger.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    json.loads(line)
    print("ZEMALA INTEGRITY CHECK PASSED")
    sys.exit(0)
except Exception as e:
    print(f"INTEGRITY ERROR: {e}")
    sys.exit(1)
