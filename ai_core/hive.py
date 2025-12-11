from flask import Flask, request, jsonify
import threading
import time

class HiveMind:
    def __init__(self, port=5000):
        self.app = Flask(__name__)
        self.port = port
        self.drones = {}
        self.jobs = []
        self.results = []

        # Define routes
        self.app.route('/join', methods=['POST'])(self.join)
        self.app.route('/job', methods=['GET'])(self.get_job)
        self.app.route('/submit', methods=['POST'])(self.submit_result)

        # Start server in thread
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        print(f"[Hive] Queen Server listening on port {self.port}")

    def _run_server(self):
        # Suppress Flask logs
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        self.app.run(host='0.0.0.0', port=self.port)

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
        # print(f"[Hive] Received result from {data.get('drone_id')}")
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
