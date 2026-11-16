#!/usr/bin/env python3
"""
verify_ledger.py - Fail-Closed Ledger Verifikation, v3 FINAL, ATOMAR
Eine einzige Datei. Kein Patch, keine Duplikate, keine zwei Regeln.
FINAL: Synchron mit STARTEN.sh / zemala_orchestrator.sh / zemala_manifest.json / TAMPER_TEST.md.
EINE Regel: JEDE ZEMALA_* = FAIL. --anchor Pflicht. --write-anchor restlos entfernt.

EINE Regel für alle Zemala-Dateien (bidirektional zu STARTEN.sh / zemala_orchestrator.sh / zemala_manifest.json / TAMPER_TEST.md):
  JEDE Variable mit Prefix ZEMALA_ = FAIL + Exit 1. Auch leer, auch ZEMALA_PROD=1, auch ZEMALA_DEMO=1.
  Prod ist Default und braucht kein Env. Kein Demo-Modus.
  Nur Variablennamen werden geloggt, nie Werte.

ANKER-ZWANG (Tor 3):
  --anchor <anker.json> ist PFLICHT. Kein Anker = KEIN PASS, KEIN COMPLIANT.
  --write-anchor, --expected-head, --expected-count, --anchor-head sind ENTFERNT.
  Aufruf mit einem dieser Flags = FAIL + Exit 1.
  Anker darf NIE aus der geprüften Datei regeneriert werden.
  --anchor-file ist nur ein Alias für --anchor.
  Anker muss enthalten: head_hash, block_count, ledger_file. Erlaubt zusätzlich: note.
  Prüfung: 1) block_count == Blockzahl, 2) head_hash == neu berechneter Head, 3) ledger_file Basename == geprüfte Datei.

KETTENPRÜFUNG, lückenlos:
  Datei-Reihenfolge = Ketten-Reihenfolge, keine Sortierung.
  Pro Block: exakte 5 Felder, strikte Typen, Timestamp ISO-8601 UTC, prev_hash/hash 64x Kleinbuchstaben-Hex,
  Index-Kontinuität, prev_hash gegen echten Vorgänger, Hash NEU berechnet (nicht ausgelesen),
  keine Leerzeilen, kein BOM, keine doppelten JSON-Keys, kein UTF-8-Fehler.
  Jeder Fehler = sofort FAIL mit Blocknummer (oder Block ANKER) + Exit 1. Kein Weiterlaufen.

Hash-Input = kanonisches JSON von {index, timestamp, data, prev_hash}, sort_keys=True, separators=(',', ':')
Kein Secret wird je geloggt: nur Pfade, Check-Namen, Blocknummern, Hashes.
"""
import sys
import json
import hashlib
import pathlib
import re
import os

HEX64 = re.compile(r"^[0-9a-f]{64}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
EXPECTED_KEYS = {"index", "timestamp", "data", "prev_hash", "hash"}
ANCHOR_KEYS = {"head_hash", "block_count", "ledger_file", "note"}
ANCHOR_REQUIRED = {"head_hash", "block_count", "ledger_file"}
GENESIS_PREV = "0" * 64
FORBIDDEN_FLAGS = {"--write-anchor", "--expected-head", "--expected-count", "--anchor-head", "--expected-hash"}

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def compute_hash(block):
    content = {
        "index": block["index"],
        "timestamp": block["timestamp"],
        "data": block["data"],
        "prev_hash": block["prev_hash"],
    }
    return hashlib.sha256(canonical(content).encode("utf-8")).hexdigest()

def fail(block_no, reason, expected="", got=""):
    print(f"❌ [FAIL-CLOSED] Block {block_no}: {reason}")
    if expected or got:
        print(f"   erwartet: {expected}")
        print(f"   gefunden: {got}")
    print("   Kette abgebrochen. Kein Block nach diesem Punkt ist vertrauenswuerdig.")
    sys.exit(1)

def fail_anchor(reason, expected="", got=""):
    print(f"❌ [FAIL-CLOSED] Block ANKER: {reason}")
    if expected or got:
        print(f"   erwartet: {expected}")
        print(f"   gefunden: {got}")
    print("   Ohne gueltigen externen Anker gibt es KEIN PASS, KEIN COMPLIANT.")
    sys.exit(1)

def no_dup_object(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError(f"Doppelter JSON-Key: {k!r}")
        obj[k] = v
    return obj

def enforce_env_lock():
    overrides = sorted(n for n in os.environ if n.startswith("ZEMALA_"))
    if overrides:
        print("❌ [FAIL-CLOSED] Env-Override-Sperre (Prod): ZEMALA_*-Vars gesetzt (JEDE = FAIL):")
        for n in overrides:
            print(f"   - {n} (nur Name geloggt, kein Wert)")
        print("   Status: FAIL + NON-COMPLIANT. Prod ist Default, braucht kein Env.")
        sys.exit(1)

def parse_args(argv):
    for a in argv:
        if a in FORBIDDEN_FLAGS:
            fail_anchor(f"Verbotenes Flag: {a} - Anker darf nie aus der geprueften Datei regeneriert werden.")
    path = None
    anchor_file = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--anchor", "--anchor-file"):
            if i + 1 >= len(argv):
                fail_anchor(f"Flag {a} braucht einen Wert: --anchor <anker.json>")
            anchor_file = argv[i + 1]
            i += 2
        elif a.startswith("-"):
            fail_anchor(f"Unbekannte Option: {a}")
        else:
            if path is not None:
                print(f"❌ [FAIL-CLOSED] Zu viele Positionsargumente: {a}")
                sys.exit(1)
            path = a
            i += 1
    if path is None:
        print("❌ [FAIL-CLOSED] Kein Ledger-Pfad angegeben. Nutzung: python3 verify_ledger.py <ledger.jsonl> --anchor <anker.json>")
        sys.exit(1)
    if anchor_file is None:
        fail_anchor("Kein --anchor uebergeben. Ohne gueltigen externen Anker (evidence/ledger_anchor.json) ist Neuverkettung / Tail-Truncation / Append NICHT erkennbar.")
    try:
        raw = pathlib.Path(anchor_file).read_bytes()
        text = raw.decode("utf-8")
    except Exception as e:
        fail_anchor(f"Anker-Datei nicht lesbar: {anchor_file} ({e})")
    if text.startswith("\ufeff"):
        fail_anchor("Anker-Datei beginnt mit BOM - nicht erlaubt.")
    try:
        anchor = json.loads(text, object_pairs_hook=no_dup_object)
    except Exception as e:
        fail_anchor(f"Anker-Datei ist kein gueltiges JSON / doppelter Key: {e}")
    if not isinstance(anchor, dict):
        fail_anchor("Anker-Datei ist kein JSON-Objekt.")
    extra = set(anchor) - ANCHOR_KEYS
    if extra:
        fail_anchor(f"Anker enthaelt unzulaessige Felder: {sorted(extra)}")
    missing = ANCHOR_REQUIRED - set(anchor)
    if missing:
        fail_anchor(f"Anker muss enthalten: head_hash, block_count, ledger_file. Fehlt: {sorted(missing)}")
    head = anchor["head_hash"]
    count = anchor["block_count"]
    ledger_file = anchor["ledger_file"]
    if not isinstance(head, str) or not HEX64.match(head):
        fail_anchor("Anker head_hash muss 64x Kleinbuchstaben-Hex sein.")
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        fail_anchor("Anker block_count muss int >= 0 sein (kein bool/String).")
    if not isinstance(ledger_file, str) or not ledger_file.strip():
        fail_anchor("Anker ledger_file muss ein nicht-leerer String sein.")
    return path, anchor_file, head, count, ledger_file

def main():
    enforce_env_lock()
    path_s, anchor_file, expected_head, expected_count, expected_ledger_file = parse_args(sys.argv[1:])
    path = pathlib.Path(path_s)
    if not path.exists():
        print(f"❌ [FAIL-CLOSED] Ledger-Datei nicht gefunden: {path}")
        sys.exit(1)
    try:
        text = path.read_bytes().decode("utf-8")
    except Exception as e:
        print(f"❌ [FAIL-CLOSED] Ledger nicht lesbar / kein UTF-8: {e}")
        sys.exit(1)
    if text.startswith("\ufeff"):
        print("❌ [FAIL-CLOSED] Ledger beginnt mit BOM - nicht erlaubt.")
        sys.exit(1)
    raw_lines = text.splitlines()
    if not raw_lines or all(not l.strip() for l in raw_lines):
        print("❌ [FAIL-CLOSED] Ledger ist leer.")
        sys.exit(1)
    blocks = []
    for lineno, line in enumerate(raw_lines, start=1):
        if not line.strip():
            fail(lineno, "Leerzeile in Ledger - nicht erlaubt (koennte Loeschung verschleiern).")
        try:
            obj = json.loads(line, object_pairs_hook=no_dup_object)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ [FAIL-CLOSED] Ungueltiges JSON / doppelter Key in Zeile {lineno}: {e}")
            print("   Kette abgebrochen.")
            sys.exit(1)
        if not isinstance(obj, dict):
            fail(lineno, f"Block ist kein JSON-Objekt, sondern {type(obj).__name__}")
        idx0 = obj.get("index", lineno)
        if isinstance(idx0, bool) or not isinstance(idx0, int):
            fail(f"Zeile {lineno}", f"index muss int sein, ist {type(idx0).__name__}: {idx0!r}")
        extra = set(obj) - EXPECTED_KEYS
        if extra:
            fail(obj.get("index", lineno), f"Unerlaubtes Extra-Feld: {sorted(extra)} - Hash deckt dieses Feld nicht ab.")
        missing = EXPECTED_KEYS - set(obj)
        if missing:
            fail(obj.get("index", lineno), f"Fehlendes Pflichtfeld: {sorted(missing)}")
        idx = obj["index"]
        if not isinstance(obj["timestamp"], str) or not obj["timestamp"]:
            fail(idx, "timestamp muss ein nicht-leerer String sein.")
        if not TS_RE.match(obj["timestamp"]):
            fail(idx, f"timestamp muss ISO-8601 UTC sein (YYYY-MM-DDTHH:MM:SSZ), ist: {obj['timestamp']!r}")
        for f in ("prev_hash", "hash"):
            v = obj[f]
            if not isinstance(v, str) or not HEX64.match(v):
                fail(idx, f"{f} muss 64x Kleinbuchstaben-Hex sein, ist: {v!r}")
        blocks.append(obj)
    expected_prev = GENESIS_PREV
    for pos, block in enumerate(blocks):
        idx = block["index"]
        if idx != pos:
            fail(idx, f"Index-Luecke oder falsche Reihenfolge. Erwartet Index {pos} an Position {pos}, gefunden {idx} (Datei-Reihenfolge beachten).", expected=str(pos), got=str(idx))
        if block["prev_hash"] != expected_prev:
            fail(idx, "prev_hash stimmt nicht mit Hash des Vorgaengerblocks ueberein.", expected=expected_prev, got=block["prev_hash"])
        try:
            recomputed = compute_hash(block)
        except Exception as e:
            fail(idx, f"Hash konnte nicht berechnet werden: {e}")
        if recomputed != block["hash"]:
            fail(idx, "Hash-Mismatch. Inhalt wurde veraendert oder Hash ist gefaelscht.", expected=recomputed, got=block["hash"])
        print(f"✅ Block {idx} verified successfully. Hash: {block['hash'][:16]}...")
        expected_prev = block["hash"]
    head = expected_prev
    if expected_count != len(blocks):
        fail_anchor("Blockzahl stimmt nicht mit externem Anker ueberein - Bloecke geloescht oder angehaengt.", expected=str(expected_count), got=str(len(blocks)))
    if expected_head != head:
        fail_anchor("Head-Hash stimmt nicht mit externem Anker ueberein - Kette wurde neuverkettet, gekuerzt oder verlaengert.", expected=expected_head, got=head)
    if pathlib.Path(expected_ledger_file).name != pathlib.Path(path).name:
        fail_anchor("Anker ledger_file (Basename) stimmt nicht mit gepruefter Datei ueberein.", expected=expected_ledger_file, got=str(path))
    print(f"✅ Anker OK: head_hash, block_count ({len(blocks)}) und ledger_file stimmen mit externem Anker ueberein. Anker: {anchor_file}")
    print(f"✅ VERIFICATION PASSED. Alle {len(blocks)} Bloecke kryptografisch verifiziert + Anker-Zwang bestanden. Head Hash: {head}")
    sys.exit(0)

if __name__ == "__main__":
    main()
