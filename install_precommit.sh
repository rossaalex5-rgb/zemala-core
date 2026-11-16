#!/bin/bash
# install_precommit.sh - Installiert pre_commit_check.sh als .git/hooks/pre-commit
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ ! -d "$SCRIPT_DIR/.git" ]; then echo "Kein .git in $SCRIPT_DIR - erst 'git init' oder Repo clonen, dann erneut."; echo "Manueller Check bis dahin: bash pre_commit_check.sh"; exit 1; fi
cp "$SCRIPT_DIR/pre_commit_check.sh" "$SCRIPT_DIR/.git/hooks/pre-commit"
chmod +x "$SCRIPT_DIR/.git/hooks/pre-commit"
echo "✅ Pre-Commit-Hook installiert: .git/hooks/pre-commit -> pre_commit_check.sh"
echo "Jeder 'git commit' läuft jetzt zuerst die 6-Artefakt-Prüfung. Bei FAIL wird der Commit blockiert."
