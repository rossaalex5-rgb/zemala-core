import urllib.request, json, os

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GEMINI_API_KEY is not set.")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(f"=== AVAILABLE MODELS FOR KEY ===")
        for m in data.get("models", []):
            name = m.get("name", "").replace("models/", "")
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" in methods:
                print(f"  [✔] {name} (supports generateContent)")
            else:
                print(f"  [ ] {name} (other methods: {methods})")
except Exception as e:
    print(f"[ERROR] Failed to fetch models: {e}")
