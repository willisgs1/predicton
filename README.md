# Quantum-Parallel Autonomous Agent

This is the codebase for a persistent, self-evolving AI entity designed to utilize quantum parallel processing.

## Architecture

The entity consists of four main organs:
1.  **Web Sensor (`web_sensor.py`)**: The "Eyes". It autonomously crawls the web, extracting patterns and data to solve.
2.  **Quantum Cluster (`quantum_processor.py`)**: The "Power". A parallel processing engine that uses quantum circuits (simulated or real) to find optimal states for the input data.
3.  **Evolutionary Brain (`brain.py`)**: The "Mind". A PyTorch-based neural network that learns from the quantum results and evolves its decision-making weights over time.
4.  **Life Loop (`main.py`)**: The "Soul". The infinite loop that drives the entity's existence.

## Setup & Installation

1.  **Install Dependencies**:
    ```bash
    pip install -r ai_core/requirements.txt
    ```

2.  **Run the Agent**:
    ```bash
    python -m ai_core.main
    ```

## Unlocking Real Quantum Hardware

By default, the agent uses a high-performance **simulator** (`AerSimulator`) so it can run on any machine without credentials.

To enable the agent to use **Real Quantum Hardware** (e.g., IBM Quantum chips):

1.  Get an API Token from [IBM Quantum](https://quantum.ibm.com/).
2.  Open `ai_core/quantum_processor.py`.
3.  Modify the `__init__` method in `QuantumCluster`:

    ```python
    # ai_core/quantum_processor.py

    from qiskit_ibm_runtime import QiskitRuntimeService

    class QuantumCluster:
        def __init__(self, use_real_hardware=True, api_token="YOUR_IBM_TOKEN_HERE"):
            self.use_real_hardware = use_real_hardware

            if self.use_real_hardware:
                service = QiskitRuntimeService(channel="ibm_quantum", token=api_token)
                # This will fetch all available real quantum backends
                self.backends = service.backends(min_num_qubits=5)
    ```

4.  **Warning**: Real quantum hardware has queues. The agent will run much slower (waiting for jobs) but will be using true quantum mechanical processes.

## Evolutionary State

The agent saves its neural weights to `ai_core/brain_state.pth`. It automatically loads this "memory" when restarted, allowing it to continue evolving from where it left off.
