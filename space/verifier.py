from reader import get_raw_data

def verify_observer_data():
    raw = get_raw_data()
    
    state_status = "PASS" if raw["state_exists"] and raw["state_content"] else "UNKNOWN"
    
    ledger_status = "UNKNOWN"
    if raw["ledger_exists"]:
        if len(raw["ledger_tail"]) > 0:
            ledger_status = "PASS"
        else:
            ledger_status = "FAIL"
    
    seal_status = "PASS" if raw["seal_exists"] and raw["seal_data"] is not None else "UNKNOWN"
    
    if state_status == "PASS" and ledger_status == "PASS" and seal_status == "PASS":
        chain_status = "VERIFIED"
    else:
        chain_status = "UNKNOWN"

    return {
        "state_status": state_status,
        "state_content": raw["state_content"] or "KEINE EVIDENZ",
        "ledger_status": ledger_status,
        "ledger_tail": raw["ledger_tail"],
        "seal_status": seal_status,
        "seal_data": raw["seal_data"],
        "chain_status": chain_status
    }
