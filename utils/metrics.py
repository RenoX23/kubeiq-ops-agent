import requests
import pandas as pd
from datetime import datetime, timedelta

PROMETHEUS_URL = "http://localhost:9090"

def query(promql: str) -> list:
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": promql})
    r.raise_for_status()
    return r.json()["data"]["result"]

def query_range(promql: str, minutes: int = 30) -> pd.DataFrame:
    end = datetime.utcnow()
    start = end - timedelta(minutes=minutes)
    r = requests.get(f"{PROMETHEUS_URL}/api/v1/query_range", params={
        "query": promql,
        "start": start.isoformat() + "Z",
        "end": end.isoformat() + "Z",
        "step": "30s"
    })
    r.raise_for_status()
    results = r.json()["data"]["result"]
    if not results:
        return pd.DataFrame()
    rows = []
    for series in results:
        labels = series["metric"]
        for ts, val in series["values"]:
            rows.append({
                "timestamp": datetime.utcfromtimestamp(float(ts)),
                "value": float(val),
                **{k: v for k, v in labels.items()}
            })
    return pd.DataFrame(rows)

def get_cluster_snapshot() -> dict:
    return {
        "cpu_usage": query(
            'sum(rate(container_cpu_usage_seconds_total{container!=""}[2m])) by (pod)'
        ),
        "memory_usage": query(
            'sum(container_memory_working_set_bytes{container!=""}) by (pod)'
        ),
        "pod_restarts": query(
            'sum(kube_pod_container_status_restarts_total) by (pod)'
        ),
        "pods_not_running": query(
            'kube_pod_status_phase{phase!="Running",phase!="Succeeded"}'
        )
    }
