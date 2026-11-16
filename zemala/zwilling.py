import time, json, os, glob, datetime
base = os.path.expanduser("~/zemala")
print("Zwilling aktiv - Handlung Bewegung Ergebnisse - Port 5001")
log_path = os.path.join(base, "zwilling_log.jsonl")
while True:
    print("Kaskade - jede weitere Information - Ledger - unvorstellbar viele - aber nur hash")
    print("Zwilling fragt: Soll ich E1 Hotel 10 Zimmer abschicken?")
    with open(log_path, "a") as log:
        log.write(json.dumps({"time": datetime.datetime.utcnow().isoformat()+"Z", "event":"Kaskade Handlung"})+"\n")
    time.sleep(10)
