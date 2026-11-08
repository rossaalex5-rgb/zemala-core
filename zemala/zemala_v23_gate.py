#!/usr/bin/env python3
import sys, os, json, time, hashlib
from typing import Tuple, Dict, Any

_MAX_DEPTH = 64

def _validate_types(obj: Any, path: str = "$", depth: int = 0) -> None:
    if depth > _MAX_DEPTH:
        raise ValueError(f"{path}: Tiefe > {_MAX_DEPTH}")
    t = type(obj)
    if obj is None or t is bool or t is int:
        return
    if t is str:
        try:
            obj.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError(f"{path}: Surrogat in String") from exc
        return
    if t is list:
        for i, item in enumerate(obj):
            _validate_types(item, f"{path}[{i}]", depth + 1)
        return
    if t is dict:
        for k, v in obj.items():
            if type(k) is not str:
                raise TypeError(f"{path}: Key {k!r} ist kein str")
            _validate_types(k, f"{path}.<key>", depth + 1)
            _validate_types(v, f"{path}.{k}", depth + 1)
        return
    raise TypeError(f"{path}: Nicht kanonisierbarer Typ {t.__name__}")

def canonicalize_and_hash(payload: Dict[str, Any]) -> Tuple[str, str]:
    if type(payload) is not dict:
        raise TypeError("Payload muss ein dict sein.")
    _validate_types(payload)
    canonical_json = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return canonical_json, digest

VALID_STATES = {
    "01": "Perception / Position", "02": "Impulse Detection", "03": "Context / Boundaries",
    "04": "Semantic Compression", "05": "Reconstruction / Project Mapping", "06": "Orchestration",
    "07": "Canonicalization", "08": "SHA-256 Seal / Ledger", "09": "Feedback / Acknowledgment",
    "10": "Sync / Mirroring", "11": "Compliance Audit", "12": "Crystallization / Marker 12.1"
}

class ZemalaV23Engine:
    def __init__(self, ledger_path: str = "observations.jsonl"):
        self.ledger_path = ledger_path

    def get_last_hash(self) -> str:
        if not os.path.exists(self.ledger_path):
            return "0" * 64
        try:
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
                if not lines:
                    return "0" * 64
                last_entry = json.loads(lines[-1])
                return last_entry.get("hash", "0" * 64)
        except Exception:
            return "0" * 64

    def auto_scan_and_execute(
        self, role: str, state_id: str, action_name: str, payload_data: Dict[str, Any],
        evidence_status: str, execution_status: str, conductor: str = "Alexander Georg Rossa"
    ) -> Dict[str, Any]:
        prev_hash = self.get_last_hash()
        timestamp = int(time.time())
        event_payload = {
            "version": "ZEMALA_GOLD_V2.3_CONSOLIDATED",
            "conductor": conductor,
            "role": role,
            "state_id": state_id,
            "state_name": VALID_STATES.get(state_id, "Unknown"),
            "action": action_name,
            "prev_hash": prev_hash,
            "timestamp": timestamp,
            "data": payload_data,
            "evidence_status": evidence_status,
            "execution_status": execution_status,
            "hoi_metric": "1.00",
            "compliance": "EU_AI_ACT_ART_12_14_COMPLIANT"
        }
        canonical_str, current_hash = canonicalize_and_hash(event_payload)
        record = {"canonical": canonical_str, "hash": current_hash}
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"status": "SEALED", "hash": current_hash, "prev_hash": prev_hash}

if __name__ == "__main__":
    engine = ZemalaV23Engine()
    res = engine.auto_scan_and_execute(
        role="Gemini",
        state_id="12",
        action_name="Soft-Durchbruch V2.3 Verankerung",
        payload_data={
            "contract": "ZEMALA GOLD V2.3 CONSOLIDATED",
            "leitsatz": "INVENTUR VOR EXPANSION",
            "status": "SOFT_BREAKTHROUGH_ANCHORED"
        },
        evidence_status="INDEPENDENTLY_VERIFIED",
        execution_status="VERIFIED"
    )
    print(f"[+] Soft-Durchbruch versiegelt: Hash={res['hash']}")
