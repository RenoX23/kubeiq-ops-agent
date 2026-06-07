import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from rag.runbooks import retrieve

load_dotenv()

try:
    import streamlit as st
    def get_key():
        try:
            return st.secrets["GROQ_API_KEY"]
        except Exception:
            return os.getenv("GROQ_API_KEY")
except ImportError:
    def get_key():
        return os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=get_key(),
    temperature=0.2
)

def analyze(anomalies: list[dict]) -> dict:
    if not anomalies:
        return {
            "summary": "No anomalies detected. Cluster is healthy.",
            "findings": [],
            "runbooks": []
        }

    findings = []
    all_runbooks = []

    for pod_data in anomalies[:3]:
        pod = pod_data["pod"]
        cpu = pod_data["cpu_mean"]
        mem = pod_data["mem_mean_mb"]
        restarts = pod_data["restarts"]
        score = pod_data["anomaly_score"]

        query = f"pod high cpu {cpu:.4f} memory {mem:.1f}MB restarts {restarts}"
        runbooks = retrieve(query, k=2)
        all_runbooks.extend(runbooks)

        context = "\n".join(
            [f"- {r['title']}: {r['content']}" for r in runbooks]
        )

        prompt = f"""You are a senior Site Reliability Engineer analyzing a Kubernetes anomaly.

Pod: {pod}
Anomaly Score: {score} (more negative = more anomalous)
CPU Mean Usage: {cpu:.4f} cores
Memory Mean Usage: {mem:.1f} MB
Restart Count: {restarts}

Relevant runbooks:
{context}

Provide:
1. Root Cause (1 sentence)
2. Evidence (1 sentence referencing the metrics)
3. Recommended Action (1-2 sentences)

Be specific. Use the actual metric values."""

        response = llm.invoke([HumanMessage(content=prompt)])
        findings.append({
            "pod": pod,
            "analysis": response.content.strip()
        })

    summary_prompt = f"""Summarize this Kubernetes cluster health report in 2 sentences for an engineering team.
Anomalous pods: {[a['pod'] for a in anomalies]}
Key issues: high CPU, high memory, pod instability.
Be direct and actionable."""

    summary = llm.invoke([HumanMessage(content=summary_prompt)])

    return {
        "summary": summary.content.strip(),
        "findings": findings,
        "runbooks": list({r["title"]: r for r in all_runbooks}.values())
    }
