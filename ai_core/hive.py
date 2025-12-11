from flask import Flask, request, jsonify
import threading
import time
import zipfile
import os
import io

class HiveMind:
    def __init__(self, port=5000):
        self.app = Flask(__name__)
        self.port = port
        self.drones = {}
        self.jobs = []
        self.results = []

        self.app.route('/join', methods=['POST'])(self.join)
        self.app.route('/job', methods=['GET'])(self.get_job)
        self.app.route('/submit', methods=['POST'])(self.submit_result)

        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        print(f"[Hive] Queen Server listening on port {self.port}")

        self.generate_drone_bundle()

    def _run_server(self):
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.app.run(host='0.0.0.0', port=self.port)

    def generate_drone_bundle(self):
        if not os.path.exists("workspace"):
            os.makedirs("workspace")

        zip_path = "workspace/drone_deploy.zip"
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                if os.path.exists("drone.py"):
                    zf.write("drone.py")

                readme = """
                HIVE MIND DRONE DEPLOYMENT
                --------------------------
                1. Extract this zip.
                2. Run 'python drone.py' on any machine.
                3. Ensure the machine can reach the Queen IP (edit drone.py if needed).
                """
                zf.writestr("README.txt", readme)

            print(f"[Hive] Drone Deployment Bundle created at {zip_path}")
        except Exception as e:
            print(f"[Hive] Failed to bundle drone: {e}")

    def join(self):
        data = request.json
        drone_id = data.get('id')
        self.drones[drone_id] = time.time()
        print(f"[Hive] Drone {drone_id} connected.")
        return jsonify({"status": "accepted"})

    def get_job(self):
        if self.jobs:
            job = self.jobs.pop(0)
            return jsonify(job)
        return jsonify({"task": "wait"})

    def submit_result(self):
        data = request.json
        self.results.append(data)
        return jsonify({"status": "ok"})

    def add_job(self, task_type, data):
        self.jobs.append({"type": task_type, "data": data.tolist() if hasattr(data, 'tolist') else data})

    def get_results(self):
        res = list(self.results)
        self.results = []
        return res

if __name__ == "__main__":
    hive = HiveMind()
    while True:
        time.sleep(1)
