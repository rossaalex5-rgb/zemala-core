import streamlit as st
from reader import get_observer_metrics

st.set_page_config(
    page_title="ZEMALA CORE // OBSERVER",
    page_icon="🛡️",
    layout="centered"
)

st.title("ZEMALA CORE // OBSERVER")
st.caption("Read-Only Beobachtungszelle — Stufe 100 Systemhygiene")

metrics = get_observer_metrics()

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("STATE & INVARIANTS")
    st.text(f"STATE:      {metrics['state']}")
    st.text(f"INVARIANTS: {metrics['invariants']}")
    st.text(f"TAKT:       {metrics['takt']}")

with col2:
    st.subheader("SEAL & IDENTITY")
    seal_status = metrics['seal']['seal_present']
    st.text(f"SEAL:       {seal_status}")
    if seal_status == "PASS":
        st.json(metrics['seal']['data'], expanded=False)
    else:
        st.text("Seal-Daten: UNKNOWN")

st.divider()

st.subheader("LEDGER INTEGRITY METADATA")
ledger = metrics['ledger']
st.text(f"  readable:     {ledger['readable']}")
st.text(f"  tail_valid:   {ledger['tail_valid']}")
st.text(f"  chain_status: {ledger['chain_status']}")
st.text(f"  Total Lines:  {ledger.get('total_lines', 'UNKNOWN')}")

st.markdown("### LEDGER TAIL (Letzte Events)")
if ledger['last_lines']:
    for line in ledger['last_lines']:
        st.code(line, language="json")
else:
    st.warning("Keine Ledger-Events verfügbar oder Status UNKNOWN.")

st.divider()
st.caption("ZEMALA Observer Zelle v1.0 — Request-Driven Read-Only Pipeline. O-M-A. 🕉️")
