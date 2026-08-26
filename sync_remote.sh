#!/usr/bin/env bash
# ==============================================================================
# ZEMALA CORE // Dual Remote Sync (GitHub & Hugging Face)
# ==============================================================================

echo "[*] Starte ZEMALA Remote-Sync..."

# 1. GitHub Sync (SSOT & Master Bundle)
echo "[+] Pushe Code und Master Bundle zu GitHub..."
git add .
git commit -m "sync: automatisierter Remote-Abgleich [Stufe 100]" 2>/dev/null || echo "Nichts zu committen."
git push origin main

# 2. Hugging Face Sync (Modell-Artefakte / Gewichte falls konfiguriert)
if command -v huggingface-cli &> /dev/null; then
    echo "[+] Hugging Face CLI detektiert. Synchronisiere Artefakte..."
    # Beispiel für HF-Upload (anpassen an dein Repository, falls gewünscht):
    # huggingface-cli upload dein-hf-repo ./models /models --repo-type model
else
    echo "[i] Hugging Face CLI nicht aktiv. Überspringe Model-Push (lokaler Edge-Betrieb)."
fi

echo "== [ZEMALA CORE] REMOTE SYNC ABGESCHLOSSEN =="
