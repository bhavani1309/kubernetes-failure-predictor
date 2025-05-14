# 🚀 Kubernetes Failure Predictor & Auto-Remediation Agent

An AI-powered, proactive failure detection and self-healing system for Kubernetes clusters — combining real-time prediction, explainability, and remediation in a single tool. Built with XGBoost, SHAP, Streamlit, and deployed using Helm & Docker.

---

## 📂 Repository Structure

📁 /src → Codebase (model training, Streamlit app, utilities) 📁 /models → Trained models (*.pkl files) 📁 /dataset_used → Dataset used for training and python code we used to generate the dataset using chaos engineering inspired technique 📁 /presentation → Slides, documentation & recorded demo 📁 /deployment → YAMLs for K8s deployment 📁 /helm_chart → Helm chart for production-style packaging 📁 /sample_data_for_streamlit → sample dataset of failures for testing in streamlit 📁 /docker → Dockerfile for the Streamlit app container

---

## 📦 Deliverables Overview

| Deliverable                          | GitHub Location                        | External Link                        |
|-------------------------------------|----------------------------------------|--------------------------------------|
| 📊 Dataset                          | `/dataset_used/podfailpred_dataset.csv` | [Google Drive](https://drive.google.com/file/d/1wI5EKYUI9vUA4-dKeoJCAQ0GwO-ZfYc2/view?usp=sharing) |
| 📦 Trained Model (`xgb_model.pkl`)  | `/models/xgb_model.pkl`               | [Google Drive](https://drive.google.com/file/d/18LwKsjhjExsiWggYnVB4Lbs-BgtHdec1/view?usp=drive_link) |
| 🔧 Scaler (`scaler.pkl`)            | `/models/scaler.pkl`                  | [Google Drive](https://drive.google.com/file/d/1EWZfqkyWfY4uPBpxtFEU0_vl8258panz/view?usp=drive_link) |
| 🔤 Label Encoders (`label_encoders.pkl`) | `/src/label_encoders.pkl`         | [Google Drive](https://drive.google.com/file/d/1afYmZAhPiAPso1e74FLcRsyeqfA9OpUu/view?usp=drive_link) |
| 🧩 Feature Columns (`feature_columns.pkl`) | `/src/feature_columns.pkl`       | [Google Drive](https://drive.google.com/file/d/1eAfztkKG0PJUPKkATsYgtfhmSWveNa40/view?usp=drive_link) |
| 🧾 Project Documentation             | `/presentation/documentation.docx`    | [Google Drive](https://docs.google.com/document/d/1qBCNQ-q9bsVLexPCD3Q09sT3c98OtbRH/edit?usp=drive_link&ouid=117645952678248031987&rtpof=true&sd=true) |
| 🎞️ Demo Presentation (Slides)       | `/presentation/devtrails.pptx`        | [Google Drive](https://docs.google.com/presentation/d/1WfDEnlqzpwwHreRkCUS0pmLiPo8_Y6su/edit?usp=drive_link&ouid=117645952678248031987&rtpof=true&sd=true) |
| ▶️ Recorded Demo Video              | (Too large for GitHub)                | [Google Drive](https://drive.google.com/file/d/1Bhciz16XNsNhGD476EVuqyqcB8HlRuzG/view?usp=drive_link) |
| 📦 Streamlit UI Code                | `/src/streamlit_app.py`               | ✅ Included |
| 📦 Dockerfile for App Packaging     | `/docker/Dockerfile`                  | ✅ Included |
| 📦 K8s Deployment YAMLs             | `/deployment/`                        | ✅ Included |
| 📦 Helm Chart                       | `/helm_chart/`                        | ✅ Included |

---

## 🐳 Docker Container

The Streamlit-based failure prediction app is fully containerized and can be run in any Docker-supported environment. The Dockerfile is located in the `/docker/` directory.

### Docker Features:
- Uses an official Python base image with Streamlit
- Installs all dependencies via `requirements.txt`
- Exposes port `8501` (Streamlit default)
- Entry point automatically runs the app

### Build and Run Locally:
 
From the project root, navigate to the Docker folder:
cd docker

Build the Docker image:
docker build -t kubefail-predictor 

Run the container:
docker run -p 8501:8501 kubefail-predictor

After running the container, open your browser and go to:
http://localhost:8501

You should see the Kubernetes Failure Predictor Streamlit UI

---

## Access Streamlit via Kubernetes (Port Forward)

After deploying your app in Kubernetes:
kubectl port-forward pod/my-k8s-app-xxxx 8080:8501
➡️ Then open your browser at:
http://localhost:8080

Replace my-k8s-app-xxxx with the actual pod name.

---

## 🌐 Streamlit App Features

- Real-time prediction from form input or CSV
- Risk scoring (🔴 High, 🟠 Medium, 🟡 Low, 🟢 None)
- SHAP explainability (XAI)
- Threshold tuning slider
- Auto-generated remediation suggestions (`kubectl`, YAML)
- Export results with explanations

---

## ⚙️ Tech Stack

- **ML**: XGBoost Classifier, SHAP
- **UI**: Streamlit
- **Packaging**: Docker, Helm
- **Deployment**: Kubernetes YAMLs (Minikube tested)

---

## 💡 Unique Features

Full AI-Ops loop: predict → explain → remediate
Chaos engineering for data generation
Threshold-tuned predictions optimized for recall
Cluster-ready deployment using Helm + Docker
Webhooks & command generation for auto-remediation

---

## 📎 Note

 Files like .csv, .pkl, .pptx, .docx are large and may not render in GitHub.
 📥 Please use the Google Drive links above to view/download them.
 Demo video is hosted externally due to GitHub size limits.

 ---

 [![Streamlit App](https://img.shields.io/badge/Live_App-Streamlit-blue?logo=streamlit)](https://kubernetes-failure-predictor-8xw3pfjyjtucudpiyqwmgd.streamlit.app/)


---

## Bhavani Thantanapalli 
 — Building self-healing Kubernetes clusters for the future.







