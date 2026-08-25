import os

def eliminate_friction():
    try:
        cleaned = 0
        for root, dirs, files in os.walk("."):
            for file in files:
                if file.endswith((".pyc", ".tmp")) or file == ".DS_Store":
                    path = os.path.join(root, file)
                    os.remove(path)
                    cleaned += 1
        print(f"[ZEMALA Clean] Systemhygiene Stufe 100: {cleaned} temporäre Artefakte bereinigt.")
    except Exception as e:
        print(f"[ZEMALA Clean] Fehler bei der Bereinigung: {e}")

if __name__ == "__main__":
    eliminate_friction()
