#!/bin/bash
echo "--- Zemala Core: Auto-Sync gestartet ---"

# 1. Lokale Änderungen temporär sichern
git stash

# 2. Aktuellen Stand vom Remote holen
git pull origin main --rebase

# 3. Gesicherte Änderungen wieder einspielen
git stash pop

# 4. Alle Änderungen hinzufügen
git add .

# 5. Commit erstellen (Nutzt das erste Argument als Nachricht oder Standardtext)
COMMIT_MSG="${1:-Zemala Core: Automatisierter Sync}"
git commit -m "$COMMIT_MSG"

# 6. Auf GitHub pushen
git push origin main

echo "--- Sync erfolgreich abgeschlossen ---"
