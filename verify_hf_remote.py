#!/usr/bin/env python3

import subprocess
import sys
from huggingface_hub import HfApi

GITHUB_REPO = "rossaalex5-rgb/zemala-core"
HF_REPO = "Lofoworld/zemala-core"

def github_sha():
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True
    ).strip()

def huggingface_sha():
    api = HfApi()
    refs = api.list_repo_refs(HF_REPO)

    for branch in refs.branches:
        if branch.name == "main":
            return branch.target_commit

    raise RuntimeError("HF main branch not found")

gh = github_sha()
hf = huggingface_sha()

print("=== ZEMALA REMOTE INTEGRITY CHECK ===")
print(f"GitHub        : {gh}")
print(f"Hugging Face  : {hf}")
print()

if gh == hf:
    print("== {ZEMALA CORE} GITHUB ↔ HF: PASS ==")
    print("Remote commit identity verified.")
    sys.exit(0)
else:
    print("== {ZEMALA CORE} GITHUB ↔ HF: FAIL ==")
    print("Remote commit identities differ.")
    sys.exit(1)
