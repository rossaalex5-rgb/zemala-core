# ZEMALA Core v1.0.0-rc1

## Release Candidate — Stufe 100

### 1. Release Identity & Remote Parity

The release candidate is versioned and synchronized across the configured remote targets.

- **Commit (`main`):** `c3d25a8299f80646e42a8d8042b5bd1cfa006bf6e`
- **Annotated tag (`v1.0.0-rc1`) object:** `f6738aef3291edb8fa75a1c1fdbf12e94e87c381`
- **Tag target:** commit `c3d25a8299f80646e42a8d8042b5bd1cfa006bf6e`
- **Remote parity:** `origin/main` and `hf/main` point to the same commit.

### 2. Verified Execution Chain

**Input → Authorization → Canonical Event → SHA-256 → Verification → Failure Propagation → Downstream Enforcement**

The implementation separates authorization, integrity verification, and downstream execution control.

### 3. Empirical Test Matrix

- **Green Path — PASS:** Valid execution produces a valid ledger event and passes verification.
- **Tamper Detection — PASS:** Controlled ledger modification is detected by the canonical SHA-256 verification path.
- **Exit-Code Enforcement — PASS:** Verification failure propagates as a non-zero exit status (`RC=1`).
- **Downstream Enforcement — PASS:** Failed verification prevents downstream side effects such as notifications and clipboard writes.
- **Remote Code Identity — PASS:** The release candidate is versioned and the configured remotes resolve to the same code commit.

### 4. Scope Boundary

> A successful cryptographic integrity check proves the integrity agreement of the specific state that was checked. It does not, by itself, establish universal authorization of every possible runtime action, nor does it constitute a complete runtime sandbox.

The integrity layer complements, rather than replaces, authorization controls, execution policy, and runtime isolation.

### 5. Reproduction

```bash
git clone [https://github.com/rossaalex5-rgb/zemala-core.git](https://github.com/rossaalex5-rgb/zemala-core.git)
cd zemala-core
git checkout v1.0.0-rc1
bash scripts/verify.sh
