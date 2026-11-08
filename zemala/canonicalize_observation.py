import hashlib
import json
import subprocess
import os

_MAX_DEPTH = 64

def _validate(obj: object, path: str = "$", depth: int = 0) -> None:
    if depth > _MAX_DEPTH:
        raise ValueError(f"{path}: Verschachtelungstiefe > {_MAX_DEPTH}")
    t = type(obj)
    if obj is None or t is bool or t is int:
        return
    if t is str:
        try:
            obj.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError(f"{path}: ungültiger Unicode-Wert (Surrogat)") from exc
        return
    if t is list:
        for i, item in enumerate(obj):
            _validate(item, f"{path}[{i}]", depth + 1)
        return
    if t is dict:
        for k, v in obj.items():
            if type(k) is not str:
                raise TypeError(f"{path}: Schlüssel ({k}) ist kein str")
            _validate(v, f"{path}[{k}]", depth + 1)
        return
    raise TypeError(f"{path}: nicht kanonisierbarer Typ ({t.__name__})")

def canonicalize_and_hash(payload: dict) -> tuple[str, str]:
    if type(payload) is not dict:
        raise TypeError("Payload muss ein dict sein.")
    _validate(payload)
    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False
    )
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return canonical_json, digest

def trigger_async_sync():
    zemala_dir = os.path.expanduser("~/zemala")
    try:
        subprocess.Popen(
            ["rclone", "sync", zemala_dir, "gdrive:zemala_sync"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass
