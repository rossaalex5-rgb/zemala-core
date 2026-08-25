#!/usr/bin/env python3
"""
ZEMALA Core - Autonomous Agent Loop mit lokalem LLM (Stufe 100)
Verbindet den Event-Stream direkt mit dem OpenAI-kompatiblen llama-server.
"""

import time
import json
import urllib.request
from datetime import datetime, timezone
from zemala_bridge import emit_event

# OpenAI-kompatibles Endpoint von llama-server
LLAMA_URL = "http://127.0.0.1:8080/v1/completions"

def query_local_llm(prompt_text):
    payload = {
        "model": "small.gguf",
        "prompt": prompt_text,
        "max_tokens": 100,
        "temperature": 0.7
    }
    req = urllib.request.Request(
        LLAMA_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            # OpenAI Format extrahieren
            text = result.get("choices", [{}])[0].get("text", "Keine Antwort im Choice-Stream.")
            return text
    except Exception as e:
        return f"[ZEMALA Offline-Modus] llama-server nicht erreichbar ({e}). Fallback aktiv."

def run_agent_cycle():
    emit_event("Agenten-Loop mit lokalem LLM-Stream gestartet.")
    
    prompt = "Zemala Core Stufe 100: Bestätige die System-Integrität in einem Satz."
    print(f"[ZEMALA Agent] Sende Prompt an lokales Modell: {prompt}")
    
    model_response = query_local_llm(prompt)
    emit_event(f"LLM-Response: {model_response.strip()}")
    
    emit_event("Agenten-Zyklus mit lokalem Modell erfolgreich abgeschlossen.")

if __name__ == "__main__":
    print("[ZEMALA Agent] Starte autonomen Loop...")
    run_agent_cycle()
