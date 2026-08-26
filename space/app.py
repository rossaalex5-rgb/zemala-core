import streamlit as st
from verifier import verify_observer_data

st.set_page_config(
    page_title="ZEMALA CORE // OBSERVER",
    page_icon="🛡️",
    layout="centered"
)

st.title("ZEMALA CORE // OBSERVER")
st.caption("Unabhängige Audit-Zelle — Read-Only (READ → VERIFY → RENDER)")

data = verify_observer_data()

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("STATE & INVARIANTS")
    st.text(f"Zustand:    {data['state_status']}")
    st.text(f"Chain:      {data['chain_status']}")
    st.text(f"Takt:       3.47 s (Dokumentiert)")

with col2:
    st.subheader("SEAL & EVIDENZ")
    st.text(f"Seal-Status: {data['seal_status']}")
    st.text(f"Ledger:      {data['ledger_status']}")

st.divider()

st.subheader("ZUSTANDS-ANKER (ZEMALA_STATE.md)")
st.code(data['state_content'], language="markdown")

st.subheader("KRYPTOGRAFISCHES SEAL")
if data['seal_status'] == "PASS" and data['seal_data']:
    st.json(data['seal_data'], expanded=False)
else:
    st.warning("Seal-Evidenz nicht vollständig oder UNKNOWN.")

st.subheader("LEDGER-TAIL (Letzte Events)")
if data['ledger_tail']:
    for line in data['ledger_tail']:
        st.code(line, language="json")
else:
    st.warning("Keine Ledger-Events verfügbar oder Evidenz fehlt (UNKNOWN).")

st.divider()
st.caption("ZEMALA Observer v1.0 — Keine Schreibrechte, keine Ausführung. O-M-A. 🕉️")
