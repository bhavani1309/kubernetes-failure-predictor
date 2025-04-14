import streamlit as st
import joblib
import numpy as np
import pandas as pd
import requests
import os

# -------- Load saved artifacts --------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
MODEL_DIR = os.path.join(ROOT_DIR, 'models')
SRC_DIR = os.path.join(ROOT_DIR, 'src')

model = joblib.load(os.path.join(MODEL_DIR, 'xgb_model.pkl'))
scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
label_encoders = joblib.load(os.path.join(SRC_DIR, 'label_encoders.pkl'))
feature_columns = joblib.load(os.path.join(SRC_DIR, 'feature_columns.pkl'))

# -------- Sidebar settings --------
st.sidebar.markdown("## ⚙️ Settings")
threshold = st.sidebar.slider(
    "Set Prediction Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.35,
    step=0.01,
    help="Adjust model sensitivity"
)

# -------- Optional webhook function --------
def send_alert(message):
    try:
        webhook_url = "https://webhook.site/your-unique-url"  # Replace with your own
        requests.post(webhook_url, json={"text": message})
    except:
        pass

# -------- Risk level assignment --------
def assign_risk_label(prob):
    if prob > 0.60:
        return "🔴 High"
    elif 0.45 < prob <= 0.60:
        return "🟠 Medium"
    elif 0.25 < prob <= 0.45:
        return "🟡 Low"
    else:
        return "🟢 None"

# -------- Remediation logic --------
def remediation_action(row):
    if row['prediction'] == 0:
        return "No action needed"
    
    failure_type_map = {
        'pod_stuck': "Restart pod",
        'cpu_throttle': "Scale up pod CPU",
        'memory_leak': "Increase memory allocation",
        'image_pull_error': "Check image repo/auth",
        'disk_full': "Clear disk or increase storage"
    }
    
    try:
        decoded_ft = label_encoders['failure_type'].inverse_transform([row['failure_type']])[0]
    except:
        return "Alert admin"

    return failure_type_map.get(decoded_ft, "Alert admin")

# -------- UI Title --------
st.title("Kubernetes Failure Predictor 🤖")
st.markdown("Predict failures, explain causes, and recommend/simulate remediation actions.")

# ---------------- CSV Upload ----------------
uploaded_file = st.file_uploader("📁 Upload sample pod data (.csv)", type="csv")

if uploaded_file:
    sample_df = pd.read_csv(uploaded_file)
    st.markdown("### 📊 Preview of Uploaded Data")
    st.write(sample_df.head())

    if st.button("Predict on Uploaded Data"):
        sample_scaled = scaler.transform(sample_df[feature_columns])
        probs = model.predict_proba(sample_scaled)[:, 1]
        preds = (probs > threshold).astype(int)

        sample_df['failure_probability'] = probs
        sample_df['prediction'] = preds
        sample_df['risk_level'] = sample_df['failure_probability'].apply(assign_risk_label)

        # XAI explanations
        def explain_reason(row):
            reasons = []
            if row['cpu_usage_cores'] > 0.9 * row['node_cpu_allocatable_cores']:
                reasons.append("high CPU usage")
            if row['memory_usage_bytes'] > 0.9 * row['node_memory_allocatable_bytes']:
                reasons.append("high memory usage")
            if row['restart_count'] > 3:
                reasons.append("too many restarts")
            if not row['container_ready']:
                reasons.append("container is not ready")
            if not row['pod_scheduled']:
                reasons.append("pod not scheduled")
            if row['oom_killed']:
                reasons.append("OOM kill occurred")
            return "Likely failure due to " + ", ".join(reasons) if reasons else "Failure risk present, but not dominated by any single issue — recommend full pod diagnostics"

        sample_df['shap_reason'] = sample_df.apply(
            lambda row: explain_reason(row) if row['prediction'] == 1 else "No failure predicted", axis=1)

        sample_df['remediation_action'] = sample_df.apply(remediation_action, axis=1)

        st.markdown("### 🔮 Prediction Results + Remediation")
        st.write(sample_df[['prediction', 'failure_probability', 'risk_level', 'shap_reason', 'remediation_action']])

        st.markdown("### 🤖 Simulated Auto-Remediation for Affected Pods")
        for idx, row in sample_df.iterrows():
            if row['prediction'] == 1:
                st.markdown(f"**Pod #{idx} → {row['remediation_action']}**")
                if row['remediation_action'] == "Restart pod":
                    st.code("kubectl delete pod <pod-name>", language="bash")
                elif row['remediation_action'] == "Scale up pod CPU":
                    st.code("kubectl scale deployment <deployment-name> --replicas=3", language="bash")
                elif row['remediation_action'] == "Increase memory allocation":
                    st.code("Edit memory limits in pod YAML spec", language="yaml")
                else:
                    st.code("Sending alert to admin... (simulated webhook)", language="bash")
                send_alert(f"[Auto-Remediation] Pod #{idx}: {row['remediation_action']}")

        st.download_button(
            label="📥 Download Results as CSV",
            data=sample_df.to_csv(index=False),
            file_name='pod_failure_predictions.csv',
            mime='text/csv'
        )

# ---------------- Manual Prediction ----------------
st.markdown("---")
st.header("🔧 Predict a Single Pod Failure")

user_input = {}
for col in feature_columns:
    if "cpu" in col or "cores" in col:
        user_input[col] = st.slider(f"{col}", 0.0, 10.0, 1.0)
    elif "memory" in col or "bytes" in col:
        user_input[col] = st.slider(f"{col}", 0.0, 2e10, 1e9)
    elif "restart_count" in col:
        user_input[col] = st.slider(f"{col}", 0, 20, 0)
    elif "latency" in col:
        user_input[col] = st.slider(f"{col}", 0.0, 1000.0, 100.0)
    elif "bool" in col or col in ["oom_killed", "container_ready", "pod_scheduled"]:
        user_input[col] = st.selectbox(f"{col}", [False, True])
    elif col in ["namespace", "failure_type"]:
        classes = label_encoders[col].classes_.tolist()
        selected = st.selectbox(f"{col}", classes)
        user_input[col] = label_encoders[col].transform([selected])[0]
    else:
        user_input[col] = st.number_input(f"{col}", value=0.0)

input_df = pd.DataFrame([user_input])[feature_columns]
scaled_input = scaler.transform(input_df)

if st.button("Predict Failure (Manual Entry)"):
    prob = model.predict_proba(scaled_input)[0][1]
    pred = int(prob > threshold)

    st.markdown(f"### 🧠 Prediction: {'⚠️ Will Fail Soon' if pred == 1 else '✅ No Failure Expected'}")
    st.markdown(f"**Failure Probability:** {prob:.2%} (Threshold = {threshold:.0%})")
    st.markdown(f"**Risk Level:** {assign_risk_label(prob)}")

    # XAI Reasoning
    reasons = []
    if user_input['cpu_usage_cores'] > 0.9 * user_input.get('node_cpu_allocatable_cores', 1):
        reasons.append("high CPU usage")
    if user_input['memory_usage_bytes'] > 0.9 * user_input.get('node_memory_allocatable_bytes', 1):
        reasons.append("high memory usage")
    if user_input['restart_count'] > 3:
        reasons.append("too many restarts")
    if not user_input.get('container_ready', True):
        reasons.append("container is not ready")
    if not user_input.get('pod_scheduled', True):
        reasons.append("pod not scheduled")
    if user_input.get('oom_killed', False):
        reasons.append("OOM kill occurred")

    reason_summary = ", ".join(reasons) if reasons else "Failure risk present, but not dominated by any single issue — recommend full pod diagnostics"
    st.markdown(f"**Top Reason(s):** {reason_summary}")

    # Remediation
    mock_row = {'prediction': pred, 'failure_type': int(user_input['failure_type'])}
    rem_action = remediation_action(mock_row)

    if pred == 1:
        st.success(f"✅ Suggested Remediation: **{rem_action}**")

        if rem_action == "Restart pod":
            st.code("kubectl delete pod <pod-name>", language="bash")
        elif rem_action == "Scale up pod CPU":
            st.code("kubectl scale deployment <deployment-name> --replicas=3", language="bash")
        elif rem_action == "Increase memory allocation":
            st.code("Edit memory limits in pod YAML spec", language="yaml")
        else:
            st.code("Sending alert to admin... (simulated webhook)", language="bash")

        send_alert(f"[Auto-Remediation] Predicted Failure. Action: {rem_action}")
    else:
        st.info("No action needed at this time.")

