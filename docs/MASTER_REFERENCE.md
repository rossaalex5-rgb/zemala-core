# ZEMALA-CORE Master Reference & Architecture SSoT

## 1. Separation of Concerns: Vision vs. Technical SSoT
Following rigorous system verification, we strictly separate external market positioning from internal technical architecture. Marketing claims must never be confused with mathematical and architectural guarantees.

| Dimension | Vision & Positioning (External) | Technical SSoT (Internal & Audit) |
| :--- | :--- | :--- |
| **Core Focus** | Cutting through legacy cloud/SAP noise with a hard, uncompromising stance. | Precise deterministic execution, canonicalization, and verifiable ledger integrity. |
| **Integrity Framing** | "Tamper-resistant edge architecture." | Append-only JSONL event ledger with SHA-256 cryptographic chaining. |
| **Compliance Framing** | "Designed for EU AI Act alignment." | Technical auditability and transparent local state trails reducing compliance friction. |

## 2. Tier 1: Strategic Vision & Positioning (Market Edge)
The market is saturated with heavy, cloud-dependent, stateful monoliths that introduce massive latency, security surface area, and regulatory vulnerability. ZEMALA-Core shifts the paradigm from cloud dependency to autonomous edge sovereignty.
- **Legacy Model:** High dependency on external APIs, unpredictable network jitter, protocol bloat, and opaque server-side processing.
- **ZEMALA Model:** Minimalist local execution, zero latency, absolute hardware control via Termux, and sovereign state-management.

## 3. Tier 2: Evidence-Graded Technical SSoT

### 3.1. The Deterministic State-Transition Engine (The "Logiksamen")
The core logic is not an endless loop or a chaotic chat interface, but a pure, stateless-to-stateful transition function:
`State_{t+1} = Transition_Function(State_t, Event_Input)`
Properties of this execution path:
- **Determinism:** Given identical input and initial state hashes, output execution paths are mathematically identical.
- **Isolation:** No implicit external network calls during core evaluation; external I/O is strictly handled via explicit, gated bridge connectors.

### 3.2. Cryptographic Ledger & Canonicalization
To ensure evidentiary integrity without invoking naïve "absolute immunity" claims:
1. **Canonicalization:** Prior to hashing, payload objects undergo strict key-sorting and deterministic serialization to prevent serialization-order drift.
2. **Chaining:** Each event record includes the SHA-256 hash of the preceding ledger entry, forming an append-only verifiable chain stored locally in JSONL format.
3. **Verification Scope:** The ledger proves chronological order and structural integrity of recorded events; authorization gates determine whether an action is permitted before it is committed.

### 3.3. Scoped EU AI Act Alignment
Compliance is an architectural byproduct, not an automatic legal certification:
- Local data residency eliminates third-party cloud data exposure.
- Cryptographic audit trails provide automated transparency logs required for high-risk system evaluations.

## 4. Execution Methodology: RIFRE
System consistency is maintained through the **RIFRE** method (Rekonstruktion, Integration, Fortführung, Rekursion, Erweiterung), ensuring that every code iteration and state change builds recursively on verified predecessors without drift.
