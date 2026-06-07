
# ⚙️ KubeIQ — Kubernetes Ops Intelligence Agent

> An AI-powered Site Reliability Engineering assistant that detects anomalous pods,
> retrieves relevant runbooks, and generates root cause analysis using LLM reasoning —
> all from live Kubernetes cluster metrics.

---

## 🏗️ Architecture

```
Live Kubernetes Cluster (Kind)
         │
         ▼
  Prometheus Metrics
  (CPU · Memory · Restarts)
         │
         ▼
 ┌───────────────────┐
 │  Isolation Forest │  → Flags statistically anomalous pods
 │  Anomaly Detector │
 └────────┬──────────┘
          │ anomalies
          ▼
 ┌───────────────────┐
 │   TF-IDF RAG      │  → Retrieves relevant runbooks per anomaly
 │  Runbook Retrieval│
 └────────┬──────────┘
          │ context
          ▼
 ┌───────────────────┐
 │  LLM Reasoning    │  → Root Cause · Evidence · Recommended Action
 │  Groq LLaMA 3.3   │
 └────────┬──────────┘
          │
          ▼
   Streamlit Dashboard
```

---

## ✨ Features

- **Real-time anomaly detection** using Isolation Forest on live Prometheus metrics
- **RAG-augmented analysis** — TF-IDF retrieval over 10 SRE runbooks per anomaly
- **LLM root cause reasoning** — structured diagnosis with evidence and remediation steps
- **Adjustable sensitivity** — contamination slider to control anomaly threshold
- **Stress test suite** — fault injection to trigger real CPU/memory/crash anomalies
- **Color-coded anomaly scores** — visual severity ranking across all monitored pods

---

## 📸 Screenshots

### Anomaly Detection Dashboard
![Dashboard](assets/dashboard.png)

### AI Root Cause Analysis
![RCA](assets/rca.png)

---

## 🧪 Stress Test Demo

```bash
# Inject real anomalies
python3 stress_test.py all

# Scan cluster in UI — cpu-stress flags at ~1.3 cores
# LLM diagnoses: "runaway process consuming excessive CPU"

# Cleanup
python3 stress_test.py clean
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Cluster | Kind (Kubernetes in Docker) |
| Metrics | Prometheus + kube-prometheus-stack |
| Anomaly Detection | Isolation Forest (scikit-learn) |
| Runbook Retrieval | TF-IDF + Cosine Similarity |
| LLM Reasoning | Groq · LLaMA 3.3 70B |
| LLM Framework | LangChain |
| Frontend | Streamlit + Plotly |

---

## 🚀 Run Locally

### Prerequisites
- Docker + Kind
- Python 3.12+
- Helm 3+
- Groq API key (free at console.groq.com)

```bash
git clone https://github.com/RenoX23/kubeiq-ops-agent.git
cd kubeiq-ops-agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### Start cluster + Prometheus

```bash
kind create cluster --name kubeiq
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set alertmanager.enabled=false \
  --set grafana.enabled=false
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &
```

### Configure `.env`

```env
GROQ_API_KEY=your_groq_key_here
PROMETHEUS_URL=http://localhost:9090
```

### Launch

```bash
streamlit run app.py
```

---

## 🗂️ Project Structure

```
kubeiq-ops-agent/
├── agents/
│   └── reasoning.py      # LLM root cause + remediation via Groq
├── detector/
│   └── anomaly.py        # Isolation Forest on Prometheus time-series
├── rag/
│   └── runbooks.py       # TF-IDF retrieval over SRE runbook corpus
├── utils/
│   └── metrics.py        # Prometheus API client + feature engineering
├── stress_test.py        # Fault injection: CPU · memory · crash loop
├── app.py                # Streamlit dashboard
└── requirements.txt
```

---

## 👤 Author

**Renold Stephen** — M.Tech CS · Christ University Bangalore
Microsoft Learn Student Ambassador · Published Researcher (IJIRT 2025)

[![GitHub](https://img.shields.io/badge/GitHub-RenoX23-181717?style=flat&logo=github)](https://github.com/RenoX23)
