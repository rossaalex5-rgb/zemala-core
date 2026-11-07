#!/usr/bin/env python3
"""
ZEMALA V1 Connector v2 - korrigiert nach GPT Review 4 Punkte
Kette: Observation -> Proposal -> Command -> Event
"""
import json
from pathlib import Path
import datetime
from typing import Dict, Any, List

COMMON_MODEL_VERSION = "v1.1-corrected"

def load_json_with_bom_handling(p: Path) -> Dict[str, Any]:
    try:
        text = p.read_bytes().decode('utf-8-sig')
        return json.loads(text)
    except FileNotFoundError:
        raise
    except Exception as e:
        return {"_error": str(e), "_path": str(p)}

def load_proposals(proposals_path: str = "~/proposals.json") -> Dict[str, Any]:
    p = Path(proposals_path).expanduser()
    ts = datetime.datetime.utcnow().isoformat()+"Z"
    if not p.exists():
        return {
            "_meta": {"source": str(p), "read_at": ts, "version": COMMON_MODEL_VERSION, "status": "missing", "error": "proposals.json not found - run: python evolution_manager.py --json > ~/proposals.json"},
            "inventory": [], "proposals": [],
            "verification": {"status": "missing", "verified": None, "checks": 0, "errors": ["file not found"], "path": None},
            "cockpit": {"to": []}, "capabilities_discovered": []
        }
    try:
        data = load_json_with_bom_handling(p)
        if "_error" in data:
            return {"_meta": {"source": str(p), "read_at": ts, "version": COMMON_MODEL_VERSION, "status": "error", "error": data["_error"]}, "inventory": [], "proposals": [], "verification": {"status": "error", "verified": None, "checks": 0, "errors": [data["_error"]]}, "cockpit": {"to": []}}
        data["_meta"] = {"source": str(p), "read_at": ts, "version": COMMON_MODEL_VERSION, "status": "ok"}
        return data
    except FileNotFoundError:
        return {"_meta": {"source": str(p), "read_at": ts, "version": COMMON_MODEL_VERSION, "status": "missing", "error": "not found"}, "inventory": [], "proposals": [], "verification": {"status": "missing", "verified": None, "checks": 0, "errors": ["not found"]}, "cockpit": {"to": []}}

def to_common_state(raw: Dict[str, Any]) -> Dict[str, Any]:
    meta = raw.get("_meta", {})
    inventory = raw.get("inventory", [])
    proposals = raw.get("proposals", [])
    verification = raw.get("verification", {})
    cockpit_cfg = raw.get("cockpit", {})
    capabilities = raw.get("capabilities_discovered", [])
    missing_info = []
    if not inventory:
        missing_info.append("inventory empty - scan_roots did not run or no files found")
    if verification.get("status") == "missing":
        missing_info.append("verification missing - ledger check not executed")
    if not proposals:
        missing_info.append("proposals empty - no development need derived or file missing")
    observations = []
    for item in inventory:
        basis = f"first_keys={item.get('first_keys', [])} size={item.get('size')} lines={item.get('lines')}"
        observations.append({
            "content": {"path": item.get("path"), "format": item.get("format"), "exists": item.get("exists")},
            "source": item.get("path"),
            "context": {"env": "termux" if "com.termux" in item.get("path","") else "cloud", "state": item.get("format"), "read_at": meta.get("read_at"), "version": meta.get("version")},
            "capabilities": [f"detect_{item.get('format','unknown')}"] if item.get("exists") else [],
            "relations": {"basis": basis},
            "constraints": {"read_only": True},
            "evidence": {"size": item.get("size"), "lines": item.get("lines"), "first_keys": item.get("first_keys", []), "reason": item.get("reason","")},
            "actions": {"allowed": ["read","classify"], "basis": basis}
        })
    common_proposals = []
    for prop in proposals:
        proposed_actions: List[str] = []
        ns = prop.get("next_step")
        if ns and isinstance(ns, str) and ns.strip():
            proposed_actions.append(ns.strip())
        basis = f"format={prop.get('format')} size={prop.get('size')} path={prop.get('path')}"
        common_proposals.append({
            "content": {"title": prop.get("title"), "prio": prop.get("prio"), "path": prop.get("path"), "format": prop.get("format")},
            "source": meta.get("source", "evolution_manager.py --json"),
            "context": {"prio": prop.get("prio"), "risk": prop.get("risk"), "read_at": meta.get("read_at"), "version": COMMON_MODEL_VERSION, "basis": basis},
            "capabilities": ["adapter","dry-run","common-model-v1"],
            "relations": {"origin": prop.get("path"), "target": "twin_v1", "origin_format": prop.get("format")},
            "constraints": {"read_only": True, "must_not_auto_import_as_event": True, "requires_explicit_orchestration": True},
            "evidence": {"size": prop.get("size"), "action": prop.get("action"), "basis": basis},
            "actions": {"proposed": proposed_actions, "allowed": ["read","verify","propose"], "blocked": ["auto_import_as_event","write_ledger"], "basis": basis}
        })
    verification_block = {
        "content": {"verified": verification.get("verified"), "checks": verification.get("checks"), "status": verification.get("status","unknown")},
        "source": verification.get("path"),
        "context": {"tool": "verify_ledger_chain", "read_at": meta.get("read_at"), "version": COMMON_MODEL_VERSION, "limit": 1000},
        "capabilities": ["verify_ledger_chain","sha256_seal_check"],
        "relations": {"ledger": verification.get("path")},
        "constraints": {"read_only": True, "must_not_simulate_verified_true": True},
        "evidence": verification,
        "actions": {"allowed": ["read","verify"], "proposed": ["GET /api/verify"] if verification.get("status")=="ok" else [], "basis": f"checks={verification.get('checks')}"}
    }
    state = {
        "common_model_version": COMMON_MODEL_VERSION,
        "meta": meta,
        "observations": observations,
        "proposals": common_proposals,
        "commands": [],
        "events": [],
        "verification": verification_block,
        "missing_info": missing_info,
        "cockpit": {
            "existing": "http://127.0.0.1:5001/board - bestehendes Board - kein Ersatz-Cockpit",
            "integration": {
                "type": "readable JSON + optional Flask adapter - lesend",
                "files": ["~/zemala_common_state.json"],
                "api_endpoints": ["GET /api/status -> observations", "GET /api/capabilities -> capabilities_discovered", "GET /api/verify -> verification", "GET /api/proposals -> proposals", "GET /api/common_state -> full state"],
                "note": "python -m http.server stellt Dateien bereit, implementiert aber keine /api/... Endpunkte - deshalb zunächst JSON als lesbare Schnittstelle, echter Adapter liest JSON und stellt unter /api/* bereit ohne Ledger zu schreiben"
            },
            "visible_cycle": "Zustand erkennen (Observation) -> Bedarf ableiten (Proposal) -> Orchestrator Freigabe (Command) -> Ausführung -> Event im Ledger -> sichtbar machen"
        },
        "arch_rules": {
            "chain": "Observation -> Proposal -> Command -> Event",
            "observations": "festgestellter Zustand - CQRS Query",
            "proposals": "vorgeschlagene Veränderung - weder Command noch Event",
            "commands": "ausdrücklich erteilter Änderungsauftrag - nur Orchestrator",
            "events": "tatsächlich eingetretene dokumentierte Zustandsänderung - Ledger mit prev_hash+sha256_seal",
            "must_not_simulate": "fehlender Datensatz darf niemals durch plausibel aussehenden Erfolgsdatensatz ersetzt werden",
            "read_only_connector": True
        },
        "capabilities_discovered": capabilities or ["detect_plain_text","detect_genesis","detect_allein_start","expanduser","bom_handling","proposals_duplicates","verify_ledger_chain","common_model_v1.1-corrected"]
    }
    return state

def write_common_state(state, out_path="~/zemala_common_state.json"):
    p = Path(out_path).expanduser()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Common State geschrieben: {p} {p.stat().st_size} Bytes - status={state.get('meta',{}).get('status')}")
        return str(p)
    except Exception as e:
        fallback = Path("/tmp/zemala_common_state.json")
        fallback.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Fallback {fallback} {e}")
        return str(fallback)

def test_missing_not_simulated_as_verified_true():
    raw = load_proposals("/nonexistent_xyz_12345.json")
    assert raw["_meta"]["status"] == "missing"
    assert raw["verification"]["verified"] is None
    state = to_common_state(raw)
    assert state["verification"]["content"]["verified"] is None
    assert len(state["missing_info"]) > 0
    print("PASS test_missing_not_simulated_as_verified_true")

def test_utf8_sig_handling():
    tmp = Path("/tmp/test_bom.json")
    tmp.write_text(chr(0xfeff) + '{"inventory": [], "proposals": []}', encoding='utf-8')
    data = load_json_with_bom_handling(tmp)
    assert "_error" not in data
    print("PASS test_utf8_sig_handling")

def test_actions_proposed_no_none():
    raw = {"_meta": {"source": "test", "read_at": "now", "version": "v1.1"}, "inventory": [], "proposals": [{"prio":1, "title":"test", "path":"/x", "format":"dirigent", "size":1, "next_step": None}, {"prio":2, "title":"test2", "path":"/y", "format":"dirigent", "size":1, "next_step": "  "}, {"prio":3, "title":"test3", "path":"/z", "format":"dirigent", "size":1, "next_step": "GET /api/status"}], "verification": {}}
    state = to_common_state(raw)
    for prop in state["proposals"]:
        assert None not in prop["actions"]["proposed"]
        for a in prop["actions"]["proposed"]:
            assert isinstance(a, str) and a.strip()
    assert state["proposals"][0]["actions"]["proposed"] == []
    assert state["proposals"][1]["actions"]["proposed"] == []
    assert state["proposals"][2]["actions"]["proposed"] == ["GET /api/status"]
    print("PASS test_actions_proposed_no_none")

def test_observation_proposal_command_event_separated():
    raw = load_proposals("/nonexistent_xyz_12345.json")
    state = to_common_state(raw)
    assert len(state["events"]) == 0
    assert len(state["commands"]) == 0
    print("PASS test_observation_proposal_command_event_separated")

def run_tests():
    tests = [test_missing_not_simulated_as_verified_true, test_utf8_sig_handling, test_actions_proposed_no_none, test_observation_proposal_command_event_separated]
    ok = 0
    for t in tests:
        try:
            t()
            ok+=1
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
        except Exception as e:
            print(f"ERROR {t.__name__}: {e}")
    print(f"{ok}/{len(tests)} Connector v2 Tests bestanden")
    return ok==len(tests)

if __name__ == "__main__":
    raw = load_proposals("~/proposals.json")
    state = to_common_state(raw)
    write_common_state(state)
    try:
        Path("/tmp/zemala_common_state.json").write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    except:
        pass
    run_tests()
    print(f"Version {COMMON_MODEL_VERSION} - read_only={state['arch_rules']['read_only_connector']} - missing_info={state.get('missing_info')}")
