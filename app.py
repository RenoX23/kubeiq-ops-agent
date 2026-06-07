import streamlit as st
import pandas as pd
import plotly.express as px
from detector.anomaly import detect_anomalies
from agents.reasoning import analyze

st.set_page_config(
    page_title="KubeIQ",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ KubeIQ — Kubernetes Ops Intelligence Agent")
st.caption("Isolation Forest anomaly detection · TF-IDF RAG runbook retrieval · Groq LLaMA 3.3 root cause analysis")

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("🔧 Controls")
    contamination = st.slider("Anomaly Sensitivity", 0.05, 0.40, 0.15, 0.05,
                              help="Higher = more pods flagged as anomalous")
    run_btn = st.button("🔍 Scan Cluster", type="primary", use_container_width=True)
    st.markdown("---")
    st.markdown("**Stress Test Commands**")
    st.code("python3 stress_test.py all\npython3 stress_test.py clean", language="bash")

with col1:
    if run_btn:
        with st.spinner("Collecting metrics from Prometheus..."):
            result = detect_anomalies(contamination=contamination)

        total = len(result["all_pods"])
        anomalies = len(result["anomalies"])

        m1, m2, m3 = st.columns(3)
        m1.metric("Pods Monitored", total)
        m2.metric("Anomalies Detected", anomalies,
                  delta=f"{anomalies} flagged", delta_color="inverse")
        m3.metric("Cluster Health",
                  "⚠️ Degraded" if anomalies > 0 else "✅ Healthy")

        if result["anomalies"]:
            st.markdown("---")
            st.subheader("📊 Anomaly Scores by Pod")
            scores_df = pd.DataFrame([
                {"pod": p, "score": s}
                for p, s in result["scores"].items()
            ]).sort_values("score")

            fig = px.bar(
                scores_df, x="score", y="pod",
                orientation="h",
                color="score",
                color_continuous_scale=["red", "orange", "green"],
                title="Isolation Forest Scores (more negative = more anomalous)"
            )
            fig.update_layout(
                plot_bgcolor="#0f1117",
                paper_bgcolor="#0f1117",
                font_color="#ffffff",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")
            st.subheader("🧠 AI Root Cause Analysis")
            with st.spinner("Analyzing anomalies with LLaMA 3.3..."):
                report = analyze(result["anomalies"])

            st.info(f"**Cluster Summary:** {report['summary']}")

            for finding in report["findings"]:
                with st.expander(f"🔴 {finding['pod']}", expanded=True):
                    st.markdown(finding["analysis"])

            if report["runbooks"]:
                st.markdown("---")
                st.subheader("📖 Referenced Runbooks")
                for rb in report["runbooks"]:
                    with st.expander(rb["title"]):
                        st.write(rb["content"])
        else:
            st.success("✅ All pods within normal parameters. No anomalies detected.")
    else:
        st.info("👈 Click **Scan Cluster** to analyse your Kubernetes cluster.")
