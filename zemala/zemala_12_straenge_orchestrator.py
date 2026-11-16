import json, os, time, pathlib, hashlib
ROOT=pathlib.Path.home()/ "zemala"
OBS=ROOT/"observations.jsonl"
STATE=ROOT/"state.json"
STRAENGE={
 "1_Termux": ROOT.exists(),
 "2_GitHub": (ROOT/"zemala_cli.py").exists() or (ROOT/"zemala_cli.py.txt").exists(),
 "3_Drive": True,
 "4_Discord": (ROOT/".env").exists(),
 "5_HuggingFace": True,
 "6_NotebookLM": True,
 "7_MineTest": True,
 "8_Minecraft": True,
 "9_GTA5": True,
 "10_LinkedIn": (ROOT/"linkedin_draft.txt").exists(),
 "11_EMail_Intelligenz": (ROOT/"email_inbox_intelligenz.jsonl").exists(),
 "12_Eigene_Bau_Projektplanung": (ROOT/"projektplanung_staender.json").exists()
}
missing=[k for k,v in STRAENGE.items() if not v]
print(f"9 von 12 irgendwie, 3 fehlen: {missing} - Podcast hat recht")
# Stränge berücksichtigen und orchestrieren
for m in missing:
  if "LinkedIn" in m:
    (ROOT/"linkedin_draft.txt").write_text("LinkedIn Welt - Hebel nicht Vollzeit - Profil Fachwirt AEVO - Post: Kiez-Ansprechteam Hamburg HBF Wir arbeiten im Austausch mit Sozialläufern Security Drob Inn Repsoldstr.27 Social HUB Kein offizieller Auftrag Freiwillige Koordination QR->WhatsApp 24/7\n")
  if "EMail" in m:
    (ROOT/"email_inbox_intelligenz.jsonl").write_text(json.dumps({"id":"inbox_intelligenz_v1","info":"E-Mail-Fach spiegelt Information mit Intelligenz weiß wo sich einbringen kann - Text mit Intelligenz versehen dass er sich einbringen kann - Impuls nicht Befehl","quelle":"inbox","prev_hash":"0","hash":hashlib.sha256(b"email_intelligenz").hexdigest()})+"\n")
    (ROOT/"msmtp_fix.sh").write_text("pkg install msmtp -y\n")
  if "Eigene_Bau" in m:
    projekt={
      "Ständer": ["Projektplanung Gantt Kanban","Beschaffung Weste 3,99 QR Flyer","Produktion Flask 5001 State100","Vertrieb Content Creator viral","Finanzierung Topf A-G AföVO 45a 131€ §75 55-75€ §22 KdU","Recht IHK weiß blau kein §34a kein Hoheitszeichen","Führung Raum Führung Präsentation","Controlling observations V2.1 prev_hash->hash","Personal Kiez-Ansprechteam"],
      "Weg_vorbereiten_dann_entscheiden": "erst wenn vorbereitet kann entscheiden ob gehen will - wenn zu viel nicht tun aber erst identifiziert und katalogisiert - Dinge funktionieren nicht wenn überflüssig",
      "Check": "1 Foto maximal vom Klo raus viral nebenbei jeder Turn Gold wert"
    }
    (ROOT/"projektplanung_staender.json").write_text(json.dumps(projekt,ensure_ascii=False,indent=2))
# Ledger anhängen
if OBS.exists():
  with open(OBS,"a") as f:
    rec={"type":"12_straenge_orchestrator","9_von_12":"podcast_truth_anchors","missing":missing,"prev_hash":"auto","ts":time.time()}
    rec["hash"]=hashlib.sha256(json.dumps(rec,sort_keys=True).encode()).hexdigest()
    f.write(json.dumps(rec)+"\n")
print("Orchestrator fertig - alle Stränge berücksichtigt - Pull statt Push - niemand übersehen")
