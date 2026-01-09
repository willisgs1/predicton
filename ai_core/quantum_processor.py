import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

class QuantumCluster:
    def __init__(self, use_real_hardware=False, api_token=None):
        self.use_real_hardware = use_real_hardware
        self.backends = []

        if self.use_real_hardware and api_token:
            try:
                print("[QuantumCluster] connecting to IBM Quantum Cloud...")
                from qiskit_ibm_runtime import QiskitRuntimeService
                service = QiskitRuntimeService(channel="ibm_quantum", token=api_token)
                real_backends = service.backends(min_num_qubits=5, simulator=False)

                if real_backends:
                    self.backends = real_backends[:4]
                    print(f"[QuantumCluster] Connected to {len(self.backends)} REAL quantum computers.")
                else:
                    print("[QuantumCluster] No real backends available. Falling back to simulator.")
                    self.backends = [AerSimulator() for _ in range(4)]

            except Exception as e:
                print(f"[QuantumCluster] Error connecting to IBM Quantum: {e}")
                print("[QuantumCluster] Falling back to Internal Quantum Simulator.")
                self.backends = [AerSimulator() for _ in range(4)]
        else:
            print("[QuantumCluster] Using Internal Quantum Simulator (Aer).")
            self.backends = [AerSimulator() for _ in range(4)]

        print(f"[QuantumCluster] Initialized with {len(self.backends)} processing units.")

    def run_parallel_task(self, problem_vector):
        results = []
        for i, backend in enumerate(self.backends):
            perturbation = np.random.rand() * 0.1
            result = self._execute_circuit(backend, problem_vector, perturbation)
            results.append(result)
        best_result = max(results, key=lambda x: x['confidence'])
        return best_result

    def _execute_circuit(self, backend, vector, perturbation):
        num_qubits = 3
        qc = QuantumCircuit(num_qubits)

        for j in range(num_qubits):
            val = vector[j] if j < len(vector) else 0
            val2 = vector[j+3] if (j+3) < len(vector) else 0
            qc.rx(val * np.pi + perturbation, j)
            qc.ry(val2 * np.pi, j)

        qc.cz(0, 1)
        qc.cz(1, 2)
        qc.cz(2, 0)
        qc.measure_all()

        try:
            transpiled_qc = transpile(qc, backend)
            job = backend.run(transpiled_qc, shots=1024)
            result = job.result()
            counts = result.get_counts()
            most_frequent_state = max(counts, key=counts.get)
            confidence = counts[most_frequent_state] / 1024.0

            return {
                'state': most_frequent_state,
                'confidence': confidence,
                'backend': str(backend)
            }
        except Exception as e:
            print(f"[QuantumCluster] Error on backend {backend}: {e}")
            return {'state': '000', 'confidence': 0.0, 'backend': 'ERROR'}

if __name__ == "__main__":
    engine = QuantumCluster(use_real_hardware=False)
    dummy_input = np.random.rand(8)
    print("Input Vector:", dummy_input)
    result = engine.run_parallel_task(dummy_input)
    print("Quantum Result:", result)
