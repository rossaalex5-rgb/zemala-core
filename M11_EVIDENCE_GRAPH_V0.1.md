ZEMALA — M₁₁ Evidence Graph v0.1

Status
- M₇–M₁₀: EMPIRICALLY CLOSED
- Historischer M₁₁-Mechanismus: SOURCE-EVIDENCE BELEGT
- M₁₁ Live-Replikation: NOT EXECUTED
- M₁₁ Execution Gate: BLOCKED
- Reproduktionsclaim: NOT RELEASED

Evidence Graph
[SOURCE EVIDENCE]
master_history.jsonl
        │
        ▼
scripts/replay.sh
        │
        └── Event-Streaming / JSON-Parsing
              [BELEGT]
              
verify.sh / core/verify.sh
        │
        └── Canonical serialization / SHA-256 comparison
              [BELEGT]

[EXECUTION EVIDENCE]
Independent replication context
        │
        ├── Byte invariance
        ├── RC=0 / RC=1 behavior
        ├── Exit-code propagation
        └── Output-state invariant
              [NOT EXECUTED]

[CAUSAL EVIDENCE]
Reconstructed state
        │
        ▼
Integrity verdict
        │
        ▼
Downstream gate
        │
        ▼
Reachable / blocked output
        │
        └── M₁₁ reproduction
              [BLOCKED UNTIL EXECUTION]

Epistemic Boundary
- Source-code existence and source-code semantics constitute source evidence.
- Source evidence does not constitute execution evidence.
- Execution evidence does not automatically constitute universal causal evidence.
- Therefore this document deliberately makes no claim that M₁₁ has been empirically closed.

Architectural Principle
- The verifier is the authority for the integrity verdict.
- Downstream components consume that verdict; they do not independently determine integrity.
- The historical replay and verification mechanisms are documented as source evidence only until an independent execution reproduces the specified invariants.

Release Boundary
The following claim is explicitly withheld:
“M₁₁ proves universal reproducibility.”
The currently supported claim is narrower:
“The historical ZEMALA source tree contains a documented replay and verification path whose semantics are available for independent execution validation.”

Freeze Rule
- No M₁₁ execution, new replication directory, core modification, or modification of the M₇–M₁₀ baseline is implied or authorized by this document.
- This document is an evidence projection, not a proof source.
- The authoritative evidence remains the executable artifacts and their independently observed execution results.
