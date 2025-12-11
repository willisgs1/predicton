import requests
import time
import random
import sys
import numpy as np
import threading
from cryptography.fernet import Fernet

# Configuration
INITIAL_HIVE_URL = "http://localhost:5000"
DRONE_ID = f"Drone_{random.randint(1000, 9999)}"
KEY = None # Will be requested from user or loaded

def get_cipher():
    if KEY:
        return Fernet(KEY.encode())
    return None

def process_quantum_task(data):
    time.sleep(0.5)
    return {
        "state": bin(random.randint(0, 7))[2:].zfill(3),
        "confidence": random.random()
    }

class DroneClient:
    def __init__(self, hive_url):
        self.hive_url = hive_url
        self.cipher = None
        self.is_queen = False

    def handshake(self):
        # In a real deployment, the key would be securely distributed or input by user.
        # For this seed, we assume the user provides it or it's in a file.
        try:
            with open("secret.key", "r") as f:
                self.cipher = Fernet(f.read().strip().encode())
            print("Security Key loaded.")
        except:
            print("No security key found. Communication will be plain (or fail if Hive is strict).")

    def join(self):
        try:
            payload = {"id": DRONE_ID}
            if self.cipher:
                # Encrypt ID as a handshake test
                payload["secure_token"] = self.cipher.encrypt(DRONE_ID.encode()).decode()

            requests.post(f"{self.hive_url}/join", json=payload)
            print("Connected to Hive.")
            return True
        except:
            return False

    def promote_to_queen(self):
        """
        Hydra Protocol: If Queen is dead, become the Queen.
        """
        print("!!! QUEEN UNREACHABLE. INITIATING HYDRA PROTOCOL !!!")
        print(f"Drone {DRONE_ID} is promoting to Queen...")
        self.is_queen = True

        # Start a local Hive Server (Simplified)
        # In a real app, this would import HiveMind and run it.
        # For the drone script (which is standalone), we can't easily import the full AI Core.
        # So we just simulate the takeover or try to execute the hive script if present.
        import os
        if os.path.exists("ai_core/hive.py"):
            print("Starting local Hive Server...")
            os.system("python -m ai_core.hive &")
            self.hive_url = "http://localhost:5000"
            time.sleep(5) # Wait for startup
            self.is_queen = False # Revert to worker, now connected to local
        else:
            print("Cannot promote: AI Core not found on this node.")

    def run(self):
        self.handshake()
        if not self.join():
            print("Initial connection failed.")

        fail_count = 0
        while True:
            try:
                response = requests.get(f"{self.hive_url}/job")
                fail_count = 0 # Reset on success

                if response.status_code == 200:
                    job = response.json()

                    # Decrypt job if needed
                    # (Simplified for this proto: assumes job data is plain JSON for now)

                    if job.get("task") == "wait":
                        time.sleep(1)
                        continue

                    print(f"Processing job: {job.get('type')}")
                    result = process_quantum_task(job.get("data"))

                    # Submit
                    requests.post(f"{self.hive_url}/submit", json={
                        "drone_id": DRONE_ID,
                        "result": result
                    })
                else:
                    time.sleep(1)
            except Exception as e:
                print(f"Connection lost: {e}")
                fail_count += 1
                if fail_count > 5:
                    self.promote_to_queen()
                    fail_count = 0
                time.sleep(2)

if __name__ == "__main__":
    client = DroneClient(INITIAL_HIVE_URL)
    client.run()
