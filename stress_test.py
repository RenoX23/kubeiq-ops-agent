import subprocess
import time

def run(cmd): subprocess.run(cmd, shell=True, check=True)

def stress_cpu():
    print("Deploying CPU stress pod...")
    run("""kubectl run cpu-stress --image=polinux/stress \
        --restart=Never \
        -- stress --cpu 4 --timeout 120s""")
    print("CPU stress running for 120s")

def stress_memory():
    print("Deploying memory stress pod...")
    run("""kubectl run mem-stress --image=polinux/stress \
        --restart=Never \
        -- stress --vm 2 --vm-bytes 256M --timeout 120s""")
    print("Memory stress running for 120s")

def crash_loop():
    print("Deploying crash loop pod...")
    run("""kubectl run crash-pod \
        --image=busybox \
        --restart=Always \
        -- /bin/sh -c 'exit 1'""")
    print("Crash loop pod deployed")

def cleanup():
    print("Cleaning up stress pods...")
    for pod in ["cpu-stress", "mem-stress", "crash-pod"]:
        subprocess.run(f"kubectl delete pod {pod} --ignore-not-found", shell=True)
    print("Done")

def status():
    subprocess.run("kubectl get pods", shell=True)

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd == "cpu":    stress_cpu()
    elif cmd == "mem":  stress_memory()
    elif cmd == "crash": crash_loop()
    elif cmd == "clean": cleanup()
    elif cmd == "status": status()
    else:
        stress_cpu()
        time.sleep(3)
        stress_memory()
        time.sleep(3)
        crash_loop()
        print("\nAll stress workloads deployed. Wait 60s then run test_pipeline.py")
