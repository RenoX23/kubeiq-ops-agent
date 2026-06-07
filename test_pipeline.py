# Save as test_pipeline.py in project root via VS Code
from detector.anomaly import detect_anomalies
from agents.reasoning import analyze

result = detect_anomalies()
print(f"Anomalies: {len(result['anomalies'])}")

report = analyze(result["anomalies"])
print("\n=== SUMMARY ===")
print(report["summary"])
print("\n=== FINDINGS ===")
for f in report["findings"]:
    print(f"\nPod: {f['pod']}")
    print(f["analysis"])
print("\n=== RUNBOOKS USED ===")
for r in report["runbooks"]:
    print("-", r["title"])
