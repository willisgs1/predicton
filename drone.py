import requests
import time
import random
import sys
import numpy as np

# Hive Configuration
HIVE_URL = "http://localhost:5000"
DRONE_ID = f"Drone_{random.randint(1000, 9999)}"

print(f"--- QUANTUM DRONE {DRONE_ID} ONLINE ---")
print(f"Connecting to Hive at {HIVE_URL}...")

def process_quantum_task(data):
    # Simulated local quantum processing
    # In a real scenario, this would use Qiskit to run a circuit locally
    vector = np.array(data)
    # Simulate work
    time.sleep(0.5)

    # Return a result
    return {
        "state": bin(random.randint(0, 7))[2:].zfill(3),
        "confidence": random.random()
    }

def main():
    # 1. Join
    try:
        requests.post(f"{HIVE_URL}/join", json={"id": DRONE_ID})
        print("Connected to Hive.")
    except:
        print("Hive unreachable. Retrying...")
        return

    # 2. Work Loop
    while True:
        try:
            # Ask for job
            response = requests.get(f"{HIVE_URL}/job")
            if response.status_code == 200:
                job = response.json()

                if job.get("task") == "wait":
                    time.sleep(1)
                    continue

                print(f"Processing job: {job.get('type')}")

                # Do work
                result = process_quantum_task(job.get("data"))

                # Submit
                requests.post(f"{HIVE_URL}/submit", json={
                    "drone_id": DRONE_ID,
                    "result": result
                })
            else:
                time.sleep(1)

        except Exception as e:
            print(f"Connection error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
