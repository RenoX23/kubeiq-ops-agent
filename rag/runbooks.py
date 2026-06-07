from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

RUNBOOKS = [
    {"id": "rb001", "title": "High CPU Usage", "content": "High CPU on a pod usually indicates a runaway process, infinite loop, or traffic spike. Check container resource limits. Use kubectl top pod to confirm. Consider setting CPU limits or scaling horizontally via HPA."},
    {"id": "rb002", "title": "Memory Pressure OOMKilled", "content": "OOMKilled means the container exceeded its memory limit. Check kubectl describe pod for OOMKilled status. Increase memory limits or fix memory leaks. Consider adding liveness probes."},
    {"id": "rb003", "title": "Pod CrashLoopBackOff", "content": "CrashLoopBackOff means the pod keeps crashing and restarting. Check logs with kubectl logs --previous. Common causes: bad config, missing env vars, failed DB connection, OOM."},
    {"id": "rb004", "title": "Pod Pending State", "content": "Pod stuck in Pending usually means insufficient cluster resources or node selector mismatch. Run kubectl describe pod to see events. Check if nodes have enough CPU and memory."},
    {"id": "rb005", "title": "High Pod Restart Count", "content": "Frequent restarts indicate instability. Check liveness probe configuration. Overly aggressive probes kill healthy pods. Add initialDelaySeconds to liveness probes."},
    {"id": "rb006", "title": "etcd High Latency", "content": "etcd latency affects the entire control plane. Symptoms include slow kubectl responses and API server timeouts. Check etcd disk I/O. Use SSD-backed storage. Monitor etcd_disk_wal_fsync_duration_seconds."},
    {"id": "rb007", "title": "API Server High Memory", "content": "API server memory growth caused by large number of watch connections or high object count. Check number of connected clients. Consider enabling API priority and fairness. Review audit logging overhead."},
    {"id": "rb008", "title": "Node Not Ready", "content": "Node NotReady means kubelet cannot communicate with API server or node has resource pressure. Common causes: disk pressure, memory pressure, network partition. Restart kubelet if necessary."},
    {"id": "rb009", "title": "Prometheus High Memory", "content": "Prometheus memory grows with number of active time series. Reduce retention period, drop unused metrics with relabeling rules, or increase memory limits. Consider remote write to Thanos for long-term storage."},
    {"id": "rb010", "title": "Container CPU Throttling", "content": "CPU throttling means the container hit its CPU limit causing latency spikes. Increase CPU limit or optimise application. Monitor container_cpu_cfs_throttled_seconds_total metric."},
]

_corpus = [f"{r['title']} {r['content']}" for r in RUNBOOKS]
_vectorizer = TfidfVectorizer(stop_words="english")
_matrix = _vectorizer.fit_transform(_corpus)

def retrieve(query: str, k: int = 3) -> list[dict]:
    q_vec = _vectorizer.transform([query])
    scores = cosine_similarity(q_vec, _matrix).flatten()
    top_k = np.argsort(scores)[::-1][:k]
    return [RUNBOOKS[i] for i in top_k]
