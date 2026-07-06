from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = ROOT / "experiments" / "results" / "m7_api_dashboard_demo.json"

st.set_page_config(page_title="FailSafeML-X Dashboard", layout="wide")
st.title("FailSafeML-X Reliability Dashboard")
st.caption("Milestone 7 demo dashboard for trust scores, failure signals, repair actions, and router decisions.")

if not DEFAULT_RESULTS.exists():
    st.warning("Run `python scripts/run_m7_api_dashboard_demo.py` first to generate demo results.")
    st.stop()

payload = json.loads(DEFAULT_RESULTS.read_text())
summary = payload["serving_demo_summary"]
responses = payload["sample_responses"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Requests", summary["num_requests"])
col2.metric("Mean trust", summary["mean_trust_score"])
col3.metric("Auto-accept rate", summary["auto_accept_rate"])
col4.metric("Review/defer rate", summary["review_or_defer_rate"])

st.subheader("Router action mix")
st.bar_chart(pd.Series(summary["router_action_counts"]).sort_index())

st.subheader("Top failure IDs")
st.bar_chart(pd.Series(summary["top_failure_ids"]).sort_values(ascending=False))

st.subheader("Sample scored requests")
rows = []
for response in responses:
    rows.append(
        {
            "request_id": response["request_id"],
            "domain": response["domain"],
            "trust_score": response["trust"]["trust_score"],
            "risk_level": response["trust"]["risk_level"],
            "router_action": response["router"]["action"],
            "num_failures": response["trust"]["num_failures"],
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True)
