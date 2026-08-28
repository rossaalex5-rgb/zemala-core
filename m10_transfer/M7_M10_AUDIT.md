# ZEMALA M₇–M₁₀ — Evidenz- und Architektur-Baseline

> **Wichtiger Hinweis:** Dieses Dokument ist eine rein lesende Projektion des bereits empirisch ermittelten Evidenzstands. Es ist keine eigenständige Beweisquelle. Die materielle Wahrheit liegt ausschließlich in den ausführbaren Artefakten und ihren gemessenen Ergebnissen im Test-Workspace.

---

## 1. EMPIRICALLY CLOSED (Empirisch geschlossene Vektoren)

* **M₇ / M₈:** Integritätsprüfung und Reproduktion (Determinismus auf dem Root-Ledger bewiesen).
* **M₉:** Outbound-Blockade (Nachgewiesenes Stoppen von Prozessen bei Integritätsfehlern).
* **M₁₀.1:** Isolierter Transfer (Unveränderter Core läuft in getrennter Domänen-Sandbox bei Byte-Invarianz des Roots; RC=0).
* **M₁₀.2:** Drift-Erkennung (Byte-Mutation am Domänen-Ledger führt deterministisch zu `HASH_MISMATCH` und RC=1).
* **M₁₀.3:** Kausale RC $\rightarrow$ Output-Wirkung (Im getesteten Wrapper nachgewiesen: RC=0 erzeugt `output_metadata.json`, RC=1 blockiert die Artefakt-Erzeugung).

---

## 2. ARCHITECTURAL CONTRACT (Definierte Systemgrenzen)

* **Single Authority:** Der Verifier ist die alleinige Autorität für das Integritätsurteil.
* **Fail-Closed (Geprüfter Umfang):** Reagiert auf die konkret getesteten Exit-Codes des Verifiers (keine universelle, systemweite Garantie für alle denkbaren Fehlerzustände).
* **Domänenisolierung:** Die Integritätslogik arbeitet unabhängig von spezifischen Inhalten und ist auf getrennte Datenströme portierbar.
* **Trennungsgebot:** Integritätsurteil und nachgelagerte Ausführung (Transformation) sind streng entkoppelt. Downstream-Code entscheidet nicht über Wahrheit.

---

## 3. OPEN (Noch offene Hypothesen / Nicht bewiesene Garantien)

* **Universelle Downstream-Garantie:** Noch kein Beweis für *jede* beliebige, unvorhergesehene Downstream-Komponente außerhalb des Test-Wrappers.
* **Produktions-Komplexität:** Übertragung auf hochkomplexe, reale Produktionsprozesse mit stark verschränkten Abhängigkeiten steht aus.
* **Parallelität & Mehrprozessbetrieb:** Getestete Concurrency- und Race-Condition-Fälle außerhalb der sequenziellen Sandbox-Ausführung sind nicht abschließend validiert.
