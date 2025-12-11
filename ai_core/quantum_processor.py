import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

class QuantumCluster:
    def __init__(self, use_real_hardware=False, api_token=None):
        """
        Initializes the Quantum Cluster.
        If use_real_hardware is True and api_token is provided, it attempts to connect to IBM Quantum.
        Otherwise, it defaults to a local high-performance simulator.
        """
        self.use_real_hardware = use_real_hardware
        self.backends = []

        if self.use_real_hardware and api_token:
            try:
                print("[QuantumCluster] connecting to IBM Quantum Cloud...")
                # Import here to keep it optional for simulator users
                from qiskit_ibm_runtime import QiskitRuntimeService

                # Connect to the service
                service = QiskitRuntimeService(channel="ibm_quantum", token=api_token)

                # Fetch real backends (least busy ones)
                # We try to get backends with at least 5 qubits
                real_backends = service.backends(min_num_qubits=5, simulator=False)

                if real_backends:
                    # Select up to 4 backends to mimic our parallel cluster
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
            # Default Simulator Mode
            print("[QuantumCluster] Using Internal Quantum Simulator (Aer).")
            self.backends = [AerSimulator() for _ in range(4)]

        print(f"[QuantumCluster] Initialized with {len(self.backends)} processing units.")

    def run_parallel_task(self, problem_vector):
        """
        Distributes the task across the available backends.
        """
        results = []

        for i, backend in enumerate(self.backends):
            # Each backend tries a slightly different configuration (perturbation)
            perturbation = np.random.rand() * 0.1
            result = self._execute_circuit(backend, problem_vector, perturbation)
            results.append(result)

        # Aggregating results: We take the 'best' result
        best_result = max(results, key=lambda x: x['confidence'])
        return best_result

    def _execute_circuit(self, backend, vector, perturbation):
        """
        Constructs and runs a quantum circuit.
        """
        num_qubits = 3
        qc = QuantumCircuit(num_qubits)

        # 1. State Preparation
        for j in range(num_qubits):
            val = vector[j] if j < len(vector) else 0
            val2 = vector[j+3] if (j+3) < len(vector) else 0
            qc.rx(val * np.pi + perturbation, j)
            qc.ry(val2 * np.pi, j)

        # 2. Entanglement
        qc.cz(0, 1)
        qc.cz(1, 2)
        qc.cz(2, 0)

        # 3. Measurement
        qc.measure_all()

        # Execute
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
