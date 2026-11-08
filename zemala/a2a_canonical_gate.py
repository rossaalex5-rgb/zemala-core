#!/usr/bin/env python3
"""ZEMALA A2A Canonical Gate: strikte Kanonisierung + SHA-256 (Fail-Closed)."""
import json
import sys

from canonicalize_observation import canonicalize_and_hash


def _no_const(name):
    raise ValueError(f"nicht erlaubte Konstante: {name}")


def _no_dupes(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError(f"doppelter Schluessel: {k}")
        d[k] = v
    return d


def gate(raw: str) -> dict:
    try:
        data = json.loads(raw, parse_constant=_no_const, object_pairs_hook=_no_dupes)
        canon, digest = canonicalize_and_hash(data)
    except (ValueError, TypeError) as exc:
        return {"status": "REJECT", "reason": str(exc)}
    return {"status": "PASS", "canonical": canon, "sha256": digest}


VECTORS = [
    ('{"b":1,"a":2}', "PASS", "d3626ac30a87e6f7a6428233b3c68299976865fa5508e4267c5415c76af7a772"),
    ("{}", "PASS", "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"),
    ('{"a":1.5}', "REJECT", None),
    ('{"a":NaN}', "REJECT", None),
    ("[1]", "REJECT", None),
    ('{"a":1,"a":2}', "REJECT", None),
    ('{"a":', "REJECT", None),
]


def selftest() -> int:
    bad = 0
    for raw, want, want_hash in VECTORS:
        r = gate(raw)
        ok = r["status"] == want and (want_hash is None or r.get("sha256") == want_hash)
        print(("PASS " if ok else "FAIL ") + raw)
        bad += 0 if ok else 1
    print(f"GATE SELFTEST: {'PASS' if bad == 0 else 'FAIL'} ({len(VECTORS) - bad}/{len(VECTORS)})")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-":
        r = gate(sys.stdin.read())
        print(json.dumps(r, ensure_ascii=False))
        sys.exit(0 if r["status"] == "PASS" else 1)
    sys.exit(selftest())
