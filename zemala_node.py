import json
import time
from pathlib import Path
from zemala_core import ZemalaLedger, ZemalaMCPBridge, ZemalaA2AMessage
from zemala_hooks import ZemalaHookManager

class ZemalaNode:
    def __init__(self, node_id: str = "node_alpha"):
        self.node_id = node_id
        self.ledger = ZemalaLedger("zemala_node.jsonl")
        self.mcp = ZemalaMCPBridge(self.ledger)
        self.hooks = ZemalaHookManager(self.ledger)
        
        # Standard-Hooks registrieren
        self.hooks.register_hook("A2A_COMMUNICATION", self._handle_a2a_event)
        self.hooks.register_hook("GENESIS", lambda e: print(f"[{self.node_id}] Genesis-Zustand verifiziert."))

    def _handle_a2a_event(self, entry):
        data = entry.get("data", {})
        print(f"[{self.node_id}] A2A-Event erkannt! Intent: {data.get('intent')} | Sender: {data.get('sender')}")

    def send_agent_message(self, receiver_id: str, intent: str, payload: dict):
        """Sendet eine deterministische A2A-Nachricht und triggert sofort die Hooks."""
        a2a = ZemalaA2AMessage(
            sender_id=self.node_id,
            receiver_id=receiver_id,
            intent=intent,
            payload=payload,
            ledger=self.ledger
        )
        msg = a2a.create_message()
        print(f"[{self.node_id}] Nachricht gesendet & in Kette geschrieben. Hash: {msg['message_hash'][:12]}...")
        
        # Lokale Hooks direkt über den neuen Zustand laufen lassen
        self.hooks.process_latest()
        return msg

    def get_status(self):
        """Gibt die aktuellen MCP-Ressourcen des Nodes aus."""
        return self.mcp.get_mcp_resources()

if __name__ == "__main__":
    print("--- ZEMALA EDGE NODE START ---")
    node = ZemalaNode("flip3_edge_node")
    
    # Test-Interaktion ausführen
    node.send_agent_message(
        receiver_id="smart_home_controller",
        intent="EXECUTE_LOCAL_STATE",
        payload={"device": "ambient_light", "state": "secured_sync"}
    )
    
    print("--- MCP Ressource Export ---")
    print(json.dumps(node.get_status(), indent=2))
