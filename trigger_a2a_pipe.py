import json
import sys

payload = {
    "jsonrpc": "2.0",
    "method": "a2a_hello",
    "params": {},
    "id": 1
}

print(json.dumps(payload))
