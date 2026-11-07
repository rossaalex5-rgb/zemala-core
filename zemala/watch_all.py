import time, json, os, glob, datetime, re
base = os.path.expanduser("~/zemala")
print("Zwilling macht alles - keine bloede Frage - alle Content Creator nach Prioritaet")
log_path = os.path.join(base, "zwilling_log.jsonl")
prioritaeten = [
    "Prio1 E1 Hotel 10 Zimmer",
    "Prio2 E2 Sozialamt Diakonie Puff->Heim §75",
    "Prio3 E3 LAsD AföVO §45a",
    "Prio4 E4 Content Creator ALLE TikTok YouTuber 【entity-Discord¦canonical_name=Discord】 Wikipedia Reddit",
]
while True:
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for prio in prioritaeten:
        print(f"{now} - Zwilling macht: {prio}")
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(json.dumps({"time": now, "prio": prio})+"\n")
        time.sleep(1)
