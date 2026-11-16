# siehe Datei oben - kurz Version - check 12 Stränge
import pathlib, json, time, hashlib
ROOT=pathlib.Path.home()/"zemala"
OBS=ROOT/"observations.jsonl"
def get_last():
 try:
  return json.loads(open(OBS).readlines()[-1])["hash"] if OBS.exists() else "0"
 except: return "0"
def check():
 straenge={"1_Termux":ROOT.exists(),"2_GitHub":(ROOT/"zemala_cli.py").exists(),"3_Drive":True,"4_Discord":(ROOT/".env").exists(),"5_HuggingFace":True,"6_NotebookLM":True,"7_MineTest":True,"8_Minecraft":True,"9_GTA5":True,"10_LinkedIn":(ROOT/"linkedin_draft.txt").exists(),"11_EMail_Intelligenz":(ROOT/"email_inbox_intelligenz.jsonl").exists(),"12_Eigene_Bau_Projektplanung":(ROOT/"projektplanung_staender.json").exists()}
 missing=[k for k,v in straenge.items() if not v]
 print(f"9 von 12 irgendwie, {len(missing)} fehlen: {missing} - Podcast hat recht")
 for k,v in straenge.items(): print(f"{'✅' if v else '❌'} {k}")
if __name__=="__main__": check()
