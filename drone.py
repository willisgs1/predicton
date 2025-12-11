import requests
import time
import random
import sys
import numpy as np
from cryptography.fernet import Fernet

INITIAL_HIVE_URL = "http://localhost:5000"
DRONE_ID = f"Drone_{random.randint(1000, 9999)}"
KEY = None

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
                payload["secure_token"] = self.cipher.encrypt(DRONE_ID.encode()).decode()

            requests.post(f"{self.hive_url}/join", json=payload)
            print("Connected to Hive.")
            return True
        except:
            return False

    def promote_to_queen(self):
        print("!!! QUEEN UNREACHABLE. INITIATING HYDRA PROTOCOL !!!")
        print(f"Drone {DRONE_ID} is promoting to Queen...")
        self.is_queen = True

        import os
        if os.path.exists("ai_core/hive.py"):
            print("Starting local Hive Server...")
            os.system("python -m ai_core.hive &")
            self.hive_url = "http://localhost:5000"
            time.sleep(5)
            self.is_queen = False
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
                fail_count = 0

                if response.status_code == 200:
                    job = response.json()

                    if job.get("task") == "wait":
                        time.sleep(1)
                        continue

                    print(f"Processing job: {job.get('type')}")
                    result = process_quantum_task(job.get("data"))

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
