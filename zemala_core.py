from datetime import datetime
import hashlib
import json
from pathlib import Path

class ZemalaLedger:
    def __init__(self, ledger_path: str = "zemala_core.jsonl"):
        self.ledger_path = Path(ledger_path)
        self._initialize_ledger()

    def _initialize_ledger(self):
        """Sorgt dafür, dass das Ledger existiert; bei Bedarf mit Genesis-Block."""
        if not self.ledger_path.exists():
            self.append({
                "event": "GENESIS",
                "payload": "ZEMALA-CORE INITIALIZATION",
                "status": "SECURED"
            })

    def _get_last_hash(self) -> str:
        """Liest den SHA-256-Hash des letzten Eintrags aus der Kette."""
        if not self.ledger_path.exists() or self.ledger_path.stat().st_size == 0:
            return "0" * 64
        
        last_line = ""
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line
                    
        if not last_line:
            return "0" * 64
            
        try:
            last_entry = json.loads(last_line)
            return last_entry.get("hash", "0" * 64)
        except json.JSONDecodeError:
            return "0" * 64

    def append(self, data: dict) -> dict:
        """Fügt einen neuen Zustand fälschungssicher per SHA-256-Kettung hinzu."""
        prev_hash = self._get_last_hash()
        timestamp = datetime.utcnow().isoformat()
        
        entry = {
            "timestamp": timestamp,
            "prev_hash": prev_hash,
            "data": data
        }
        
        canonical_string = json.dumps(entry, sort_keys=True, separators=(',', ':'))
        current_hash = hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()
        
        final_entry = {**entry, "hash": current_hash}
        
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(final_entry, sort_keys=True) + "\n")
            
        return final_entry

class ZemalaMCPBridge:
    def __init__(self, ledger: ZemalaLedger):
        self.ledger = ledger

    def get_mcp_resources(self) -> list:
        """Exponiert den aktuellen Systemzustand als MCP-Ressource für Agenten."""
        latest_entry = self._get_latest_entry()
        return [{
            "uri": "zemala://core/ledger/latest",
            "name": "Zemala Deterministic Root State",
            "mimeType": "application/json",
            "description": "Der unvergängliche, SHA-256-gesicherte letzte Zustand des Edge-Ledgers.",
            "text": json.dumps(latest_entry, sort_keys=True)
        }]

    def _get_latest_entry(self) -> dict:
        if not self.ledger.ledger_path.exists():
            return {"status": "EMPTY"}
            
        last_line = ""
        with open(self.ledger.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    last_line = line
                    
        if not last_line:
            return {"status": "EMPTY"}
            
        try:
            return json.loads(last_line)
        except json.JSONDecodeError:
            return {"error": "CORRUPTED_LEDGER_STATE"}

class ZemalaA2AMessage:
    def __init__(self, sender_id: str, receiver_id: str, intent: str, payload: dict, ledger: ZemalaLedger):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.intent = intent
        self.payload = payload
        self.ledger = ledger

    def create_message(self) -> dict:
        prev_hash = self.ledger._get_last_hash()
        timestamp = datetime.utcnow().isoformat()
        
        message = {
            "sender": self.sender_id,
            "receiver": self.receiver_id,
            "intent": self.intent,
            "payload": self.payload,
            "parent_ledger_hash": prev_hash,
            "timestamp": timestamp
        }
        
        canonical_str = json.dumps(message, sort_keys=True, separators=(',', ':'))
        msg_hash = hashlib.sha256(canonical_str.encode('utf-8')).hexdigest()
        
        signed_message = {**message, "message_hash": msg_hash}
        
        self.ledger.append({
            "event_type": "A2A_COMMUNICATION",
            "sender": self.sender_id,
            "receiver": self.receiver_id,
            "intent": self.intent,
            "message_hash": msg_hash
        })
        
        return signed_message

if __name__ == "__main__":
    print("Initializing ZEMALA-Core Edge Node...")
    ledger = ZemalaLedger("zemala_test.jsonl")
    mcp = ZemalaMCPBridge(ledger)
    
    a2a = ZemalaA2AMessage(
        sender_id="agent_alpha",
        receiver_id="agent_omega",
        intent="SYNCHRONIZE_STATE",
        payload={"action": "verify_edge_node"},
        ledger=ledger
    )
    msg = a2a.create_message()
    print("A2A Message generated & chained:", json.dumps(msg, indent=2))
    
    resources = mcp.get_mcp_resources()
    print("MCP Resources exposed:", json.dumps(resources, indent=2))
