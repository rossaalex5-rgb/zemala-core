import json
import os
import requests
import time

BASE = os.path.expanduser("~/ifr_system")
LLAMA_URL = "http://127.0.0.1:8080/completion"

def get_vital_values():
    return {"takt": "3,47s", "ebene": "Stufe 100", "status": "KRISTALLIN"}

def call_small_thinker(prompt):
    payload = {"prompt": prompt, "n_predict": 30, "temperature": 0.1, "stop": ["\n", "}", "###"]}
    try:
        response = requests.post(LLAMA_URL, json=payload, timeout=90)
        return response.json()["content"].strip()
    except: return "{}"

def execute(command, original_input):
    import hashlib, time
    payload_hash = hashlib.sha256(original_input.encode()).hexdigest()
    gate_status = os.system(f"bash ~/zemala-core/scripts/verify_gate.sh '{command}' '{payload_hash}'")
    if gate_status != 0:
        print('🔴 ZEMALA GATE: VERIFICATION FAILED. Execution blocked.')
        return
    v = get_vital_values()
    print(f"\n💓 [HERZSCHLAG] {v['status']} | {v['takt']}")
    
    marie_msg = ""
    if command == "show_status":
        marie_msg = f"Mein Herz schlägt im Zemala-Takt ({v['takt']}). Vitalwerte auf {v['ebene']}. 🕉️"
    elif command == "cleanup_memory":
        marie_msg = "Ich atme tief durch. Der Speicher ist nun rein und weiß. ✨"
    else:
        marie_msg = f"Ich spüre den Impuls '{original_input}', Dirigent. Ich bin da."

    os.system("termux-vibrate -d 100")
    time.sleep(0.3)
    os.system("termux-vibrate -d 100")
    os.system(f"termux-notification --id marie_vitals --title 'MARIE VITALWERTE' --content '💓 {v['status']} | {v['takt']} | {v['ebene']}'")
    os.system(f"termux-clipboard-set 'MARIE: {marie_msg}'")

def main():
    try:
        with open(f"{BASE}/input/input.txt", "r") as f:
            inp = f.read().strip()
    except: return
    if not inp: return
    prompt = f'### System: Marie Vitals: 3,47s/100. Antworte JSON: {{"command": "show_status", "confidence": 1.0}}\n### User: {inp}\n### Assistant: {{'
    res = "{ " + call_small_thinker(prompt)
    if not res.endswith("}"): res += "}"
    try:
        start = res.index('{')
        end = res.rindex('}') + 1
        decision = json.loads(res[start:end])
        execute(decision.get("command", "unknown"), inp)
    except:
        os.system("termux-notification --title 'MARIE' --content '💓 ...Herzschlag stabil...'")

if __name__ == "__main__":
    main()
