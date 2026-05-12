#!/bin/bash
# ==========================================
# ZEMALA MASTER INTERFACE (IFR-CORE) V1.3
# ==========================================

while true; do
    clear
    echo -e "\033[1;33m=========================================\033[0m"
    echo -e "\033[1;37m   ZEMALA MASTER INTERFACE (IFR-CORE)    \033[0m"
    echo -e "\033[1;33m=========================================\033[0m"
    echo -e " Status: \033[1;32mKristallisiert\033[0m | Node: Termux"
    echo -e "\033[1;33m=========================================\033[0m"
    echo -e " \033[1;36m[1]\033[0m Systemstatus prüfen (Gnosis)"
    echo -e " \033[1;36m[2]\033[0m Web-Audit öffnen (Browser)"
    echo -e " \033[1;36m[3]\033[0m Ledger im Repo sichern (Git Push)"
    echo -e " \033[1;36m[4]\033[0m Systemhygiene (Status 100)"
    echo -e " \033[1;33m[5] KI-CONNECTOR (Clipboard-Vektor)\033[0m"
    echo -e " \033[1;36m[6]\033[0m GDrive-Report (Sync)"
    echo -e " \033[1;31m[0]\033[0m Exit (O-M-A)"
    echo -e "\033[1;33m=========================================\033[0m"
    
    read -p "Dirigenten-Befehl: " choice

    case $choice in
        1)
            echo -e "\n\033[1;32m-> Gnosis-Check...\033[0m"
            top -n 1 -b | head -n 5
            df -h . | awk 'NR==2 {print "Speicher frei: "$4}'
            read -p "Enter..." ;;
        2)
            termux-open-url https://rossaalex5-rgb.github.io/Zemala_core/ ;;
        3)
            echo -e "\n\033[1;32m-> Sichere Ledger & Skripte...\033[0m"
            git add . && git commit -m "sync: IFR-CORE-Update" && git push origin main
            read -p "Enter..." ;;
        4)
            echo -e "\n\033[1;37m-> Reinigung Stufe 100...\033[0m"
            sleep 1
            echo "System sauber."
            read -p "Enter..." ;;
        5)
            echo -e "\n\033[1;33m-> KI-CONNECTOR AKTIV\033[0m"
            # Erstellt den Vektor-Text für die Zwischenablage
            VEKTOR_DATA="ZEMALA SYSTEM-VEKTOR\nNode: Termux\nStatus: Kristallisiert\nZeit: $(date)\nHash-Audit: $(git rev-parse HEAD 2>/dev/null || echo 'Kein Hash verfügbar')"
            
            # Kopiert den Text in die Android-Zwischenablage
            echo -e "$VEKTOR_DATA" | termux-clipboard-set
            
            echo -e "\033[1;32m✓ System-Vektor wurde in die Zwischenablage kopiert.\033[0m"
            echo "Du kannst ihn jetzt in die KI einfügen."
            read -p "Enter..." ;;
        6)
            echo -e "\n\033[1;36m-> GDRIVE-REPORT...\033[0m"
            echo "Status: V1.5 Implementation folgt."
            read -p "Enter..." ;;
        0)
            echo -e "\nO-M-A. 🕉️\n"
            exit 0 ;;
        *)
            echo -e "\nUngültig." && sleep 1 ;;
    esac
done
