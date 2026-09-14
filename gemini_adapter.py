#!/usr/bin/env python3
import os
import json
import sys
from datetime import datetime, timezone
import urllib.request
import urllib.error

ZCORE_INBOX = "/storage/emulated/0/_zcore/inbox"
ZCORE_OUTBOX = "/storage/emulated/0/_zcore/outbox"

GEMINI_MODEL = "gemini-3.6-flash"
GEMINI_ENDPOINT = (
    f"https://generativelanguage.googleapis.com/v1beta/"
    f"models/{GEMINI_MODEL}:generateContent"
)

def ensure_dirs():
    os.makedirs(ZCORE_INBOX, exist_ok=True)
    os.makedirs(ZCORE_OUTBOX, exist_ok=True)

def write_response(payload, req_id):
    out_file = os.path.join(
        ZCORE_OUTBOX,
        f"proposal_{req_id}.json"
    )
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[+] Structured proposal written to ZEMALA outbox: {out_file}")

def process_request(mock=False):
    ensure_dirs()

    input_files = [
        f for f in os.listdir(ZCORE_INBOX)
        if os.path.isfile(os.path.join(ZCORE_INBOX, f))
        and not f.endswith(".done")
    ]

    req_id = "req_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    corr_id = "corr_zemala_001"
    prompt = "Evaluate system proposal safely."

    if input_files:
        target_file = os.path.join(ZCORE_INBOX, input_files[0])
        print(f"[+] Reading from real ZEMALA inbox path: {target_file}")

        try:
            with open(target_file, "r", encoding="utf-8") as f:
                content = f.read()

            try:
                req_data = json.loads(content)
                req_id = req_data.get("request_id", req_id)
                corr_id = req_data.get("correlation_id", corr_id)
                prompt = req_data.get("prompt", content)
            except json.JSONDecodeError:
                prompt = content

        except Exception as e:
            print(f"[!] Input read error: {e}", file=sys.stderr)

    else:
        print(f"[-] No active file in {ZCORE_INBOX}. Creating baseline payload.")

        sample = {
            "request_id": req_id,
            "correlation_id": corr_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt": "ZEMALA core status check and safe proposal generation."
        }

        sample_path = os.path.join(
            ZCORE_INBOX,
            "zemala_bridge_request.json"
        )

        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(sample, f, indent=2, ensure_ascii=False)

        prompt = sample["prompt"]

    print(f"[+] Processing Request ID: {req_id} (Correlation: {corr_id})")

    response_payload = {
        "request_id": req_id,
        "correlation_id": corr_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "Gemini Adapter (Fall 3)",
        "model": GEMINI_MODEL,
        "type": "PROPOSAL_OBSERVATION",
        "proposal": None,
        "status": "PENDING"
    }

    if mock:
        print("[*] Running in MOCK mode.")
        response_payload["proposal"] = (
            f"[MOCK PROPOSAL] Safe evaluation of prompt: "
            f"'{prompt}'. No core mutation executed."
        )
        response_payload["status"] = "SUCCESS_MOCK"
        write_response(response_payload, req_id)
        return

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("[ERROR] GEMINI_API_KEY is missing!", file=sys.stderr)
        response_payload["status"] = "ERROR_MISSING_API_KEY"
        response_payload["error"] = "GEMINI_API_KEY is not set."
        write_response(response_payload, req_id)
        sys.exit(1)

    print(f"[*] Calling Gemini API ({GEMINI_MODEL}) via x-goog-api-key header...")

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        data_bytes = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(
            GEMINI_ENDPOINT,
            data=data_bytes,
            headers=headers,
            method="POST"
        )

        with urllib.request.urlopen(req, timeout=60) as resp:
            res_body = json.loads(
                resp.read().decode("utf-8")
            )

        candidates = res_body.get("candidates", [])

        if not candidates:
            raise RuntimeError("Gemini response contains no candidates.")

        parts = candidates[0].get("content", {}).get("parts", [])

        text_parts = [
            p.get("text", "")
            for p in parts
            if p.get("text")
        ]

        if not text_parts:
            raise RuntimeError("Gemini response contains no text output.")

        response_payload["proposal"] = "\n".join(text_parts)
        response_payload["status"] = "SUCCESS_API"

        print("[+] Gemini API response received successfully.")

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] HTTP {e.code}: {error_body}", file=sys.stderr)
        response_payload["status"] = "ERROR_API_FAILED"
        response_payload["error"] = error_body

    except urllib.error.URLError as e:
        print(f"[ERROR] Network/API connection failed: {e}", file=sys.stderr)
        response_payload["status"] = "ERROR_API_FAILED"
        response_payload["error"] = str(e)

    except Exception as e:
        print(f"[ERROR] General API call failed: {e}", file=sys.stderr)
        response_payload["status"] = "ERROR_API_FAILED"
        response_payload["error"] = str(e)

    write_response(response_payload, req_id)

if __name__ == "__main__":
    process_request(
        mock=(
            "--mock" in sys.argv
            or os.environ.get("GEMINI_MODE") == "mock"
        )
    )
