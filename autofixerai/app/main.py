import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from collections import Counter

st.set_page_config(page_title="AutoFixerAI Dashboard", layout="wide")
st.title("⚙️ AutoFixerAI DevOps Agent")
st.caption("Diagnoses and fixes broken deployments using logs + LLMs")

# === Agent Status Control ===
status_path = "agent_status.json"
if os.path.exists(status_path):
    with open(status_path, "r") as f:
        status_data = json.load(f)
else:
    status_data = {"running": True, "simulate": False}

agent_status = st.sidebar.toggle("Agent Status", value=status_data["running"])
status_data["running"] = agent_status
st.sidebar.write(f"Status: {'🟢 Running' if agent_status else '🔴 Paused'}")

# Dropdown for simulate mode
mode = st.sidebar.selectbox("Execution Mode", ["🧠 Auto", "🛠 Simulate"], index=0 if not status_data.get("simulate") else 1)
status_data["simulate"] = (mode == "🛠 Simulate")

# Save status
with open(status_path, "w") as f:
    json.dump(status_data, f)

# === Fix History ===
history_file = "history/fix_history.json"
if os.path.exists(history_file):
    with open(history_file, "r") as f:
        history = json.load(f)
    history = list(reversed(history))
else:
    history = []

# === Display Fix Summary Stats ===
st.subheader(f"🛠 Fix History ({len(history)} total)")
if history:
    df = pd.DataFrame(history)

    # Fix source breakdown
    st.markdown("### 🤖 Fix Source Distribution")
    source_counts = df["source"].value_counts()
    st.bar_chart(source_counts)

    # Latest Fixes
    for i, entry in enumerate(history[:10]):
        with st.expander(f"🔧 Pod: `{entry['pod']}` | Source: `{entry['source']}`", expanded=(i == 0)):
            st.write(f"🕒 `{entry['timestamp']}`")
            st.markdown(f"**🔨 Command Used:** `{entry['command']}`")
            st.markdown(f"**🧠 Source:** `{entry['source']}`")

else:
    st.info("No fix history yet.")

# === Learning Analytics ===
st.subheader("📊 Learning & Intelligence Stats")

learning_log = "app/data/learning_log.json"
if os.path.exists(learning_log):
    with open(learning_log, "r") as f:
        learning_data = json.load(f)

    df_learn = pd.DataFrame(learning_data)
    
    # Fix Success Rate per Issue
    st.markdown("### ✅ Fix Success Rate by Issue Type")
    success_stats = df_learn.groupby("issue_type")["success"].agg(["count", "sum"])
    success_stats.columns = ["Total Fixes", "Successful"]
    success_stats["Success Rate"] = (success_stats["Successful"] / success_stats["Total Fixes"] * 100).round(2).astype(str) + "%"
    st.dataframe(success_stats)

    # LLM vs Fallback Count
    st.markdown("### 🧠 Fix Source (Learning Log)")
    src_counts = df_learn["source"].value_counts()
    st.bar_chart(src_counts)

else:
    st.warning("No learning data available yet.")

# Optional: Auto-refresh every 15 seconds
st.experimental_rerun()
