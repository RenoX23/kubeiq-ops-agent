import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from utils.metrics import query_range, get_cluster_snapshot

def build_feature_matrix(minutes: int = 30) -> pd.DataFrame:
    cpu_df = query_range(
        'sum(rate(container_cpu_usage_seconds_total{container!=""}[2m])) by (pod)',
        minutes=minutes
    )
    mem_df = query_range(
        'sum(container_memory_working_set_bytes{container!=""}) by (pod)',
        minutes=minutes
    )

    if cpu_df.empty or mem_df.empty:
        return pd.DataFrame()

    cpu_agg = cpu_df.groupby("pod")["value"].agg(["mean", "max", "std"]).add_prefix("cpu_")
    mem_agg = mem_df.groupby("pod")["value"].agg(["mean", "max", "std"]).add_prefix("mem_")

    features = cpu_agg.join(mem_agg, how="inner").fillna(0)
    return features

def detect_anomalies(contamination: float = 0.15) -> dict:
    features = build_feature_matrix()

    if features.empty or len(features) < 3:
        return {"anomalies": [], "all_pods": [], "scores": {}}

    model = IsolationForest(contamination=contamination, random_state=42)
    preds = model.fit_predict(features)
    scores = model.score_samples(features)

    anomaly_pods = features.index[preds == -1].tolist()
    score_map = dict(zip(features.index, scores.round(4)))

    snapshot = get_cluster_snapshot()
    restart_data = {
        item["metric"].get("pod", ""): float(item["value"][1])
        for item in snapshot["pod_restarts"]
    }

    enriched = []
    for pod in anomaly_pods:
        enriched.append({
            "pod": pod,
            "anomaly_score": score_map.get(pod, 0),
            "cpu_mean": round(features.loc[pod, "cpu_mean"], 6),
            "cpu_max": round(features.loc[pod, "cpu_max"], 6),
            "mem_mean_mb": round(features.loc[pod, "mem_mean"] / 1e6, 2),
            "restarts": int(restart_data.get(pod, 0))
        })

    enriched.sort(key=lambda x: x["anomaly_score"])
    return {
        "anomalies": enriched,
        "all_pods": features.index.tolist(),
        "scores": score_map
    }
