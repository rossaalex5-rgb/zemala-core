import re

with open("status_server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Import des Guards einfügen falls noch nicht da
if "from zemala_runtime_guard import check_ingress, check_singleton, release_lock" not in code:
    code = "from zemala_runtime_guard import check_ingress, check_singleton, release_lock\n" + code

# Ingress-Prüfung im Handler verankern
target_pattern = 'def do_POST\(self\):'
replacement = '''def do_POST(self):
        if not check_ingress({"source": "HMI_POST"}):
            self.send_response(429)
            self.end_headers()
            self.wfile.write(b"<h1>[BLOCKED] C-INGRESS-01: Pending Collision</h1>")
            return'''

if target_pattern in code and "check_ingress" not in code.split("def do_POST(self):")[1][:200]:
    code = re.sub(target_pattern, replacement, code, count=1)

with open("status_server.py", "w", encoding="utf-8") as f:
    f.write(code)

print("[+] status_server.py erfolgreich mit Runtime Guard patchen lassen.")
