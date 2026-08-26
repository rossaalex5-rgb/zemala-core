import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def read_system_state():
    state_path = ROOT_DIR / "ZEMALA_STATE.md"
    if state_path.exists():
        content = state_path.read_text(encoding="utf-8")
        return content.splitlines()[0] if content else None
    return None

def read_ledger_tail(n=5):
    ledger_path = ROOT_DIR / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            all_lines = [line.strip() for line in f if line.strip()]
        return all_lines[-n:] if all_lines else []
    except Exception:
        return []

def read_seal():
    seal_path = ROOT_DIR / "ledger_seal.json"
    if not seal_path.exists():
        return None
    try:
        with open(seal_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def get_raw_data():
    return {
        "state_content": read_system_state(),
        "ledger_tail": read_ledger_tail(),
        "seal_data": read_seal(),
        "ledger_exists": (ROOT_DIR / "ledger.jsonl").exists(),
        "state_exists": (ROOT_DIR / "ZEMALA_STATE.md").exists(),
        "seal_exists": (ROOT_DIR / "ledger_seal.json").exists()
    }
