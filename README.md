# 🚀 Kubernetes Failure Predictor & Auto-Remediation Agent

An AI-assisted Kubernetes reliability system that combines **failure prediction, explainability, and automated remediation workflows**.

The project was developed in **two stages**:

- **Stage 1 — Failure Prediction & Explainability:** XGBoost-based Kubernetes failure prediction with SHAP explainability and an interactive Streamlit dashboard.
- **Stage 2 — Auto-Remediation:** extension of the project using a local Minikube Kubernetes environment, rule-based YAML remediation, and an LLM fallback mechanism for uncovered failure scenarios.

> **Current scope:** The Stage 1 Streamlit application is deployed on Streamlit Community Cloud. Stage 2 was developed and tested separately in a local Minikube environment. Docker, Kubernetes deployment YAMLs, and Helm configurations are included in the repository as deployment/packaging artifacts, but their complete end-to-end deployment was not successfully validated.

[![Streamlit App](https://img.shields.io/badge/Live_App-Streamlit-blue?logo=streamlit)](https://kubernetes-failure-predictor-8xw3pfjyjtucudpiyqwmgd.streamlit.app/)

---

## 📌 Project Overview

Kubernetes workloads can fail because of different resource, workload, or configuration conditions. Detecting a potential failure is only one part of the problem; understanding the prediction and deciding how to respond are also important.

This project explores a two-stage approach:

```text
Stage 1
Kubernetes Failure Data
        ↓
Preprocessing
        ↓
XGBoost Failure Prediction
        ↓
Failure Probability / Risk
        ↓
SHAP Explanation
        ↓
Remediation Recommendation
        ↓
Streamlit Dashboard
```

The second stage extends the idea toward an automated Kubernetes response workflow:

```text
Stage 2
Minikube Cluster
      ↓
Failure Scenario
      ↓
Logs / Pod Status
      ↓
Failure Diagnosis
      ↓
Rule-Based YAML Remediation
      ↓
If no suitable rule
      ↓
LLM Fallback (Ollama)
      ↓
Command Validation
      ↓
Remediation
      ↓
Health Verification
```

The two stages are **not a single continuously connected production deployment**.

---

# 📂 Repository Structure

```text
/
├── src/
│   ├── streamlit_app.py
│   ├── label_encoders.pkl
│   └── feature_columns.pkl
│
├── models/
│   ├── xgb_model.pkl
│   └── scaler.pkl
│
├── dataset_used/
│   ├── podfailpred_dataset.csv
│   └── dataset-generation code
│
├── presentation/
│   ├── documentation.docx
│   ├── k8sppt.pptx
│   └── demo material
│
├── deployment/
│   └── Kubernetes YAMLs
│
├── helm_chart/
│   └── Helm chart
│
├── sample_data_for_streamlit/
│   └── Sample failure data
│
├── docker/
│   └── Dockerfile
│
└── autofixerai/
    └── Stage 2 auto-remediation workflow
```

---

## 📦 Deliverables Overview

| Deliverable | GitHub Location | External Link |
|---|---|---|
| 📊 Dataset | `/dataset_used/podfailpred_dataset.csv` | [Google Drive](https://drive.google.com/file/d/1wI5EKYUI9vUA4-dKeoJCAQ0GwO-ZfYc2/view?usp=sharing) |
| 📦 Trained Model (`xgb_model.pkl`) | `/models/xgb_model.pkl` | [Google Drive](https://drive.google.com/file/d/18LwKsjhjExsiWggYnVB4Lbs-BgtHdec1/view?usp=drive_link) |
| 🔧 Scaler (`scaler.pkl`) | `/models/scaler.pkl` | [Google Drive](https://drive.google.com/file/d/1EWZfqkyWfY4uPBpxtFEU0_vl8258panz/view?usp=drive_link) |
| 🔤 Label Encoders (`label_encoders.pkl`) | `/src/label_encoders.pkl` | [Google Drive](https://drive.google.com/file/d/1afYmZAhPiAPso1e74FLcRsyeqfA9OpUu/view?usp=drive_link) |
| 🧩 Feature Columns (`feature_columns.pkl`) | `/src/feature_columns.pkl` | [Google Drive](https://drive.google.com/file/d/1eAfztkKG0PJUPKkATsYgtfhmSWveNa40/view?usp=drive_link) |
| 🧾 Project Documentation | `/presentation/documentation.docx` | [Google Drive](https://docs.google.com/document/d/1qBCNQ-q9bsVLexPCD3Q09sT3c98OtbRH/edit?usp=drive_link&ouid=117645952678248031987&rtpof=true&sd=true) |
| 🎞️ Demo Presentation | `/presentation/k8sppt.pptx` | [Google Drive](https://docs.google.com/presentation/d/1WfDEnlqzpwwHreRkCUS0pmLiPo8_Y6su/edit?usp=drive_link&ouid=117645952678248031987&rtpof=true&sd=true) |
| ▶️ Recorded Demo Video | — | [Google Drive](https://drive.google.com/file/d/1Bhciz16XNsNhGD476EVuqyqcB8HlRuzG/view?usp=drive_link) |
| 📦 Streamlit UI Code | `/src/streamlit_app.py` | Included |
| 📦 Dockerfile | `/docker/Dockerfile` | Included |
| 📦 Kubernetes Deployment YAMLs | `/deployment/` | Included |
| 📦 Helm Chart | `/helm_chart/` | Included |
| 🛠️ Auto-Remediation Stage | `/autofixerai/` | Included |

---

# 1️⃣ Stage 1 — Failure Prediction & Explainability

## 🤖 XGBoost Failure Prediction

The first stage uses an **XGBoost Classifier** to predict Kubernetes-related failure conditions from structured input data.

XGBoost is a gradient-boosted decision-tree algorithm used for classification in this project.

The model produces a failure probability, which is then used by the application for risk classification.

The Streamlit application also provides a configurable prediction threshold.

---

## 🔍 SHAP Explainability

**SHAP (SHapley Additive exPlanations)** is used to explain individual model predictions.

Instead of showing only:

```text
Failure = YES
```

the application can show which features contributed to the prediction.

Conceptually:

```text
Input Features
      ↓
XGBoost
      ↓
Prediction
      ↓
SHAP
      ↓
Feature Contributions
```

---

## 📊 Dataset

The project uses a Kubernetes failure dataset generated using a **chaos-engineering-inspired approach**.

The dataset is available at:

```text
/dataset_used/podfailpred_dataset.csv
```

The repository also contains code used to generate the dataset.

The dataset is used as the basis for training the Stage 1 failure prediction model.

---

## 🧹 Preprocessing

The ML pipeline uses saved preprocessing artifacts:

```text
/models/scaler.pkl
/src/label_encoders.pkl
/src/feature_columns.pkl
```

The overall inference flow is:

```text
Raw Input
   ↓
Categorical Encoding
   ↓
Feature Scaling
   ↓
Feature Ordering
   ↓
XGBoost
```

The exact feature definitions and preprocessing operations are documented in the training notebook/source code.

---

# 2️⃣ Streamlit Application

The trained model is exposed through a Streamlit application.

### Features

- Interactive prediction from form input
- CSV-based prediction/testing
- Failure probability
- Risk classification
- Prediction threshold tuning
- SHAP explainability
- Remediation suggestions
- Exporting results and explanations

### Live Application

[![Streamlit App](https://img.shields.io/badge/Live_App-Streamlit-blue?logo=streamlit)](https://kubernetes-failure-predictor-8xw3pfjyjtucudpiyqwmgd.streamlit.app/)

The live application demonstrates the **Stage 1 prediction and explainability functionality**.

---

# 3️⃣ Stage 2 — Auto-Remediation

The second stage extends the project from prediction/recommendation toward Kubernetes remediation.

A local **Minikube** cluster is used as the controlled Kubernetes environment for testing.

The workflow uses Kubernetes information such as pod status and logs to determine the failure scenario and select a remediation path.

```text
Minikube
   ↓
Kubernetes Workload
   ↓
Failure
   ↓
Logs / Status
   ↓
Diagnosis
   ↓
Remediation
   ↓
Verification
```

---

## 📜 Rule-Based YAML Remediation

Known failure scenarios are handled using predefined YAML-based rules.

```text
Failure Information
        ↓
Rule Matching
        ↓
Known Scenario?
    /       \
  YES       NO
   ↓         ↓
Predefined  LLM
Remediation Fallback
```

The rule-based approach is deterministic and is preferred for known failure scenarios.

---

## 🤖 LLM Fallback

When a suitable predefined rule is unavailable, the Stage 2 workflow can use an LLM as a fallback remediation-planning component.

The local setup uses **Ollama** with the configured Code Llama model.

```text
Uncovered Failure
       ↓
Failure Context
       ↓
Ollama / Code Llama
       ↓
Candidate Remediation
       ↓
Validation
       ↓
Execution
```

The LLM is used for **remediation assistance** and is separate from the XGBoost failure prediction model.

---

## 🛡️ Command Validation

LLM-generated commands should not be executed blindly.

The workflow includes a validation step before remediation is performed.

```text
Candidate Command
       ↓
Validation
   /       \
Valid     Invalid
 ↓           ↓
Execute    Reject
```

---

## 🔄 Health Verification

After a remediation action, the Kubernetes workload is checked again.

```text
Remediation
    ↓
Check Workload State
    ↓
Recovered?
  /      \
YES       NO
 ↓         ↓
Success   Further Handling /
          Escalation
```

---

# 4️⃣ Docker

A Dockerfile is included for packaging the Streamlit application:

```text
/docker/Dockerfile
```

The intended local workflow is:

```bash
cd docker
docker build -t kubefail-predictor .
docker run -p 8501:8501 kubefail-predictor
```

The Dockerfile is retained as part of the project's containerization work.

> **Status:** Docker packaging was created, but the complete end-to-end Docker deployment was not successfully validated. The project therefore does not claim a successful production Docker deployment.

---

# 5️⃣ Kubernetes Deployment

Kubernetes deployment YAMLs are included under:

```text
/deployment/
```

They contain the project's Kubernetes deployment configuration.

> **Status:** The complete application deployment using these manifests was not successfully validated end-to-end. They are included as deployment artifacts.

---

# 6️⃣ Helm

A Helm chart is included under:

```text
/helm_chart/
```

The chart represents the project's attempt to package the Kubernetes deployment configuration using Helm.

> **Status:** The complete Helm deployment was not successfully validated end-to-end. The chart is included as a project artifact and is not presented as a successfully deployed production system.

---

# 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python |
| Machine Learning | XGBoost |
| ML Utilities | scikit-learn |
| Explainability | SHAP |
| UI | Streamlit |
| Kubernetes | Kubernetes |
| Local Kubernetes | Minikube |
| Kubernetes CLI | kubectl |
| Remediation | Python + YAML rules |
| LLM Fallback | Ollama + Code Llama |
| Containerization | Docker |
| Kubernetes Packaging | Helm |

---

# 💡 Key Features

### Stage 1 — Prediction & Explainability

- XGBoost-based failure prediction
- SHAP-based prediction explanations
- Configurable prediction threshold
- Risk classification
- Streamlit dashboard
- Chaos-engineering-inspired dataset generation

### Stage 2 — Auto-Remediation

- Local Minikube Kubernetes environment
- Kubernetes failure diagnosis
- YAML-based deterministic remediation
- LLM fallback for uncovered cases
- Command validation
- Post-remediation health verification
- Escalation/further handling when remediation does not resolve the failure

---

# 🔄 Complete Project Workflow

```text
                    DATA GENERATION
                           ↓
                    DATA PREPROCESSING
                           ↓
                     XGBOOST TRAINING
                           ↓
                      TRAINED MODEL
                           ↓
                   FAILURE PREDICTION
                           ↓
                    SHAP EXPLANATION
                           ↓
                    STREAMLIT DASHBOARD
                           ↓
                STREAMLIT COMMUNITY CLOUD
                           │
                           │
                    PROJECT EXTENSION
                           │
                           ↓
                    MINIKUBE CLUSTER
                           ↓
                 FAILURE / LOG ANALYSIS
                           ↓
                RULE-BASED REMEDIATION
                           │
                    ┌──────┴──────┐
                    ↓             ↓
                  Known        Unknown
                    ↓             ↓
                 YAML Fix     LLM Fallback
                    │             │
                    └──────┬──────┘
                           ↓
                    COMMAND VALIDATION
                           ↓
                       REMEDIATION
                           ↓
                    HEALTH VERIFICATION
                           ↓
                    SUCCESS / ESCALATION
```

---

# ⚠️ Limitations

- The ML dataset is generated using a controlled, chaos-engineering-inspired approach and may not represent every real-world Kubernetes failure.
- The public Streamlit deployment is not connected to the local Minikube auto-remediation environment.
- Stage 2 was tested in a controlled local Kubernetes environment rather than a production cluster.
- Rule-based remediation only covers failure scenarios represented by the configured rules.
- LLM-generated remediation can be incorrect and therefore requires validation.
- Docker packaging was created but was not fully validated end-to-end.
- Kubernetes deployment manifests were created but were not fully validated end-to-end.
- Helm packaging was created but was not fully validated end-to-end.
- Production deployment would require stronger RBAC, security controls, auditing, monitoring, command policies, and extensive testing.

---

# 🚀 Future Work

Potential future improvements include:

- Integrate the ML prediction stage directly with a Kubernetes monitoring pipeline.
- Add Prometheus and centralized logging for richer observability.
- Expand the rule-based remediation library.
- Improve LLM command validation and safety controls.
- Add Kubernetes RBAC with least-privilege permissions.
- Add human approval for high-risk remediation actions.
- Improve the model using larger and more representative real-world Kubernetes datasets.
- Add comprehensive remediation audit logs.
- Validate and productionize the Docker/Kubernetes/Helm deployment workflow.
- Build a fully integrated:

```text
Detect → Predict → Explain → Diagnose → Remediate → Verify
```

pipeline.

---

# 📎 Notes

Large files such as `.csv`, `.pkl`, `.pptx`, `.docx`, and demo videos may not be suitable for direct GitHub rendering.

The external Google Drive links above are provided for accessing the corresponding project resources.

---

# 🎤 Project Summary

> **Kubernetes Failure Predictor & Auto-Remediation Agent is a two-stage Kubernetes reliability project. The first stage uses XGBoost to predict Kubernetes-related failures and SHAP to explain the predictions through a Streamlit dashboard. The second stage extends the project toward auto-remediation using a local Minikube cluster, predefined YAML-based remediation rules, and an LLM fallback for failure scenarios that are not covered by the rules.**

---

## 👤 Project

**Bhavani Thantanapalli**

*Building intelligent and safer Kubernetes reliability workflows.*
