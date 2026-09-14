#!/usr/bin/env python3

import os
import json
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone

MODEL = "gemini-3.6-flash"
API_KEY = os.environ.get("GEMINI_API_KEY")

ROOT = "/storage/emulated/0"
OUTBOX = "/storage/emulated/0/_zcore/outbox"
WORK = "/storage/emulated/0/_zcore/reconstruction"

SEARCH_ROOTS = [
    "/storage/emulated/0/_zcore",
    "/storage/emulated/0/Zemala",
    "/storage/emulated/0/ZELLE",
    "/storage/emulated/0/minetest",
    "/storage/emulated/0/Download/hmi_bridge",
    "/storage/emulated/0/Download/Meta AI",
]

ALLOWED = {
    ".py", ".sh", ".lua", ".json", ".jsonl",
    ".md", ".txt", ".yaml", ".yml",
    ".toml", ".cfg", ".conf"
}

MAX_FILE = 256 * 1024
MAX_PACKAGE = 250 * 1024
MAX_PACKAGES = 200

if not API_KEY:
    raise SystemExit("ERROR: GEMINI_API_KEY ist nicht gesetzt.")

os.makedirs(WORK, exist_ok=True)
os.makedirs(OUTBOX, exist_ok=True)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def collect():
    result = []
    seen = set()

    for base in SEARCH_ROOTS:
        if not os.path.isdir(base):
            continue

        for root, dirs, files in os.walk(base):
            dirs[:] = [
                d for d in dirs
                if d not in {".git", "__pycache__", "node_modules"}
            ]

            for name in files:
                path = os.path.abspath(os.path.join(root, name))

                if path in seen:
                    continue

                if os.path.splitext(name)[1].lower() not in ALLOWED:
                    continue

                try:
                    stat = os.stat(path)
                except OSError:
                    continue

                if stat.st_size > MAX_FILE:
                    continue

                try:
                    with open(path, "rb") as f:
                        raw = f.read()
                except (OSError, PermissionError):
                    continue

                result.append({
                    "absolute_path": path,
                    "size_bytes": stat.st_size,
                    "modified_time": datetime.fromtimestamp(
                        stat.st_mtime,
                        timezone.utc
                    ).isoformat(),
                    "sha256": sha256(raw),
                    "content": raw.decode("utf-8", errors="replace")
                })

                seen.add(path)

    result.sort(key=lambda x: x["absolute_path"])
    return result


def make_packages(files):
    packages = []
    current = []
    current_size = 0

    for item in files:
        encoded = json.dumps(
            item,
            ensure_ascii=False
        ).encode("utf-8")

        size = len(encoded)

        if current and current_size + size > MAX_PACKAGE:
            packages.append(current)
            current = []
            current_size = 0

        current.append(item)
        current_size += size

    if current:
        packages.append(current)

    return packages


def api_call(prompt):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        f"models/{MODEL}:generateContent"
    )

    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2
        }
    }

    body = json.dumps(
        payload,
        ensure_ascii=False
    ).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.HTTPError as e:
        detail = e.read().decode(
            "utf-8",
            errors="replace"
        )
        raise RuntimeError(
            f"Gemini HTTP {e.code}: {detail}"
        )


def text_from_response(response):
    try:
        return response["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return json.dumps(
            response,
            ensure_ascii=False,
            indent=2
        )


BASE_PROMPT = r"""
ZEMALA — UNABHÄNGIGE FORENSISCHE REKONSTRUKTION

Du bist ein unabhängiger Beobachter.

Du erhältst einen Teil eines READ-ONLY-Snapshots des realen
Android-Dateibestands.

Keine Bestätigung unserer bisherigen Geschichte.

Keine Reparatur.
Keine Mutation.
Keine Implementierung.
Keine Commit-/Push-Empfehlung.

Arbeite ausschließlich mit den gelieferten Daten.

Trenne strikt:

BEOBACHTUNG
= direkt im Artefakt sichtbar

ABLEITUNG
= logisch aus Beobachtungen folgend

HYPOTHESE
= plausible, aber unbewiesene Erklärung

SPEKULATION
= schwache mögliche Erklärung

UNKNOWN
= nicht entscheidbar

Behandle Begriffe wie PASS, FAIL, VERIFIED, GOLD,
CANONICAL, INTEGRITY, AUTHORIZATION oder STATE
niemals selbst als Beweis.

Untersuche insbesondere:

WRITER → TARGET → SCHEMA → PERSISTENCE → READER
→ VERIFIER → TEST → FUNCTION

und soweit belegbar:

STATE → OBSERVATION → EVIDENCE → VERIFICATION
→ DECISION → AUTHORIZATION → ACTION → NEW STATE

Suche aktiv nach:

- Pfadkonflikten
- Schema-Konflikten
- mehreren Ledgern
- mehreren Generationen
- parallelen Entwicklungssträngen
- verschiedenen Repositories
- Snapshots
- Worktrees
- toten Komponenten
- nicht gestarteten Komponenten
- Code ohne erkennbare Aufrufer
- Dokumentation ohne entsprechenden Mechanismus
- Tests, die selbst Zustand verändern
- Fehlern, die fälschlich als Integritätsbeweis interpretiert werden

Für jeden wichtigen Befund:

BEOBACHTUNG
→ ABLEITUNG
→ ALTERNATIVE ERKLÄRUNG
→ GEGENHYPOTHESE
→ WELCHE EVIDENZ WÜRDE DIESE ERKLÄRUNG WIDERLEGEN?

Wenn du etwas siehst, wonach wir nicht gefragt haben:
LEGE ES AUF DEN TISCH.

Erzeuge keine erfundenen Messwerte.

OUTPUT:

1. Direkte Befunde
2. Belastbare Rekonstruktion
3. Risse/Widersprüche
4. Alternative Erklärungen
5. Nicht bewiesene Behauptungen
6. Fehlende Evidenz
7. Wichtigster nächster Test
8. Neue Erkenntnisse
9. Was fällt dir selbst auf, das niemand gefragt hat?

Maximiere Erkenntnisgewinn, nicht Textmenge.
"""


def investigate_package(package, index, total):
    prompt = (
        BASE_PROMPT
        + f"""

DIES IST EVIDENZPAKET {index} VON {total}.

Wichtig:
Ein einzelnes Paket stellt NICHT notwendigerweise das gesamte
System dar.

Ziehe deshalb keine globalen Schlussfolgerungen, wenn die
vorliegenden Daten dafür nicht ausreichen.

=== EVIDENCE ===

"""
        + json.dumps(
            package,
            ensure_ascii=False,
            indent=2
        )
    )

    return text_from_response(
        api_call(prompt)
    )


def synthesize(results, inventory):
    prompt = r"""
ZEMALA — SYNTHese unabhängiger Evidenzpakete

Du erhältst mehrere vorher getrennt untersuchte Evidenzpakete
desselben physischen Android-Snapshots.

Die Einzelanalysen sind NICHT automatisch wahr.

Vergleiche sie.

Suche insbesondere:

- echte Übereinstimmungen
- voneinander abhängige Annahmen
- Widersprüche zwischen Paketen
- unterschiedliche Erklärungen desselben Artefakts
- Befunde, die erst durch Kombination mehrerer Pakete sichtbar werden
- Behauptungen, die von keinem Artefakt getragen werden

Rekonstruiere anschließend den kleinsten gemeinsamen,
tatsächlich belegbaren ZEMALA-Mechanismus.

Wichtig:

Mehrere KI-Analysen mit derselben Schlussfolgerung sind
keine unabhängige Evidenz, wenn sie auf denselben Artefakten
und denselben Annahmen beruhen.

Trenne deshalb:

KONSENS
≠
BEWEIS

Gib aus:

A. GEMEINSAM BELEGT
B. WIDERSPRÜCHE
C. KONKURRIERENDE MODELLE
D. KLEINSTER BELEGTER MECHANISMUS
E. NICHT BEWIESEN
F. ENTSCHEIDENDE FEHLENDE EVIDENZ
G. NÄCHSTER HÖCHSTWERTIGER TEST
H. WAS HAT SICH DURCH DIE ZUSAMMENSCHAU ERST GEZEIGT?
I. WAS FÄLLT DIR SELBST AUF, DAS WIR NICHT GEFRAGT HABEN?

Keine Reparatur.
Keine Mutation.
Keine Implementierung.
"""
    payload = {
        "inventory": inventory,
        "package_analyses": results
    }

    return text_from_response(
        api_call(
            prompt
            + "\n\n=== DATA ===\n"
            + json.dumps(
                payload,
                ensure_ascii=False,
                indent=2
            )
        )
    )


def main():
    print("=== ZEMALA / GEMINI FORENSIC RECONSTRUCTION ===")
    print("MODE: READ-ONLY")
    print(f"ROOT: {ROOT}")
    print(f"MODEL: {MODEL}")

    print("\n[1] Physical collection...")
    files = collect()

    print(f"[+] Files collected: {len(files)}")

    packages = make_packages(files)

    if len(packages) > MAX_PACKAGES:
        raise SystemExit(
            f"ERROR: {len(packages)} Pakete > Maximum {MAX_PACKAGES}."
        )

    print(f"[+] Evidence packages: {len(packages)}")

    results = []

    for i, package in enumerate(
        packages,
        start=1
    ):
        print(
            f"\n[2] Gemini package {i}/{len(packages)}..."
        )

        analysis = investigate_package(
            package,
            i,
            len(packages)
        )

        result = {
            "package": i,
            "file_count": len(package),
            "analysis": analysis
        }

        results.append(result)

        package_file = os.path.join(
            WORK,
            f"package_{i:02d}.json"
        )

        with open(
            package_file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                result,
                f,
                ensure_ascii=False,
                indent=2
            )

        print("[+] Package analysis stored.")

    print("\n[3] Gemini cross-package synthesis...")

    inventory = {
        "root": ROOT,
        "created_at": now(),
        "file_count": len(files),
        "package_count": len(packages)
    }

    def hierarchical_merge(items):
        if len(items) == 1:
            return items[0]["analysis"] if isinstance(items[0], dict) else items[0]

        groups = []
        current = []
        chars = 0
        limit = 140000

        for item in items:
            text = json.dumps(item, ensure_ascii=False)
            if current and chars + len(text) > limit:
                groups.append(current)
                current = []
                chars = 0
            current.append(item)
            chars += len(text)

        if current:
            groups.append(current)

        merged = []

        for n, group in enumerate(groups, 1):
            print(f"[+] Hierarchical merge {n}/{len(groups)}")

            prompt = r"""
ZEMALA — HIERARCHISCHE EVIDENZ-SYNTHESE

Führe diese unabhängigen Teilanalysen zusammen.

Wichtig:
Übereinstimmung zwischen KI-Analysen ist KEIN neuer Beweis.

Bewahre:
- direkte Befunde
- Widersprüche
- Unsicherheiten
- konkurrierende Hypothesen
- fehlende Evidenz

Trenne strikt:
BEFUND
ABLEITUNG
HYPOTHESE
SPEKULATION
UNKNOWN

Erfinde keine Tatsachen.
Verwechsle keine Statusbezeichnung mit technischem Nachweis.

Suche insbesondere nach:
- parallelen Generationen
- mehreren Repositories
- Pfadkonflikten
- Schema-Konflikten
- Migrationen
- Snapshots
- toten Komponenten
- nicht gestarteten Komponenten
- Writer/Reader/Verifier-Brüchen
- Dokumentation ohne entsprechenden Mechanismus
- Tests, die Zustand verändern

Und lege ausdrücklich Erkenntnisse auf den Tisch,
nach denen bisher niemand gefragt hat.

=== TEILANALYSEN ===
""" + json.dumps(group, ensure_ascii=False, indent=2)

            merged.append({
                "analysis": gemini(prompt)
            })

        return hierarchical_merge(merged)

    synthesis = hierarchical_merge(results)

    final = {
        "request_id": (
            "zemala_forensic_"
            + datetime.now(timezone.utc).strftime(
                "%Y%m%d_%H%M%S"
            )
        ),
        "timestamp": now(),
        "source": "physical Android snapshot",
        "model": MODEL,
        "type": "INDEPENDENT_FORENSIC_RECONSTRUCTION",
        "read_only": True,
        "inventory": inventory,
        "package_analyses": results,
        "synthesis": synthesis,
        "status": "SUCCESS_API"
    }

    output = os.path.join(
        OUTBOX,
        f"{final['request_id']}.json"
    )

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            final,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("\n=== COMPLETE ===")
    print(output)


if __name__ == "__main__":
    main()
