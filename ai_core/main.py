import time
import os
import sys
import numpy as np
from ai_core.web_sensor import WebSensor
from ai_core.quantum_processor import QuantumCluster
from ai_core.brain import EvolutionaryBrain

def life_loop():
    print("Initializing Quantum-Parallel Autonomous Agent...")

    # Initialize Components
    sensor = WebSensor()
    quantum_engine = QuantumCluster(use_real_hardware=False)
    brain = EvolutionaryBrain()

    # Load previous state if exists
    # We save in the current directory for simplicity in the zip distribution
    brain.load_state("brain_state.pth")

    iteration = 0

    try:
        while True:
            iteration += 1
            print(f"\n--- Cycle {iteration} ---")

            # 1. Sense: Gather data from the web
            problem_vector, source_url = sensor.explore()
            if problem_vector is None:
                print("Sleeping...")
                time.sleep(2)
                continue

            print(f"[Input] Processed data from {source_url}")

            # 2. Think: Brain decides how to approach this problem
            # It modifies the vector slightly based on what it learned before
            brain_modification = brain.decide_action(problem_vector)

            # Combine raw data with brain's intuition
            # We average them for the quantum input
            quantum_input = (problem_vector + brain_modification) / 2.0

            # 3. Process: Unleash the Quantum Cluster
            print("[Process] Dispatching to Quantum Cluster...")
            start_time = time.time()
            result = quantum_engine.run_parallel_task(quantum_input)
            duration = time.time() - start_time

            print(f"[Result] Quantum State '{result['state']}' found in {duration:.4f}s")
            print(f"         Confidence: {result['confidence']*100:.2f}% (Unit: {result['backend']})")

            # 4. Evolve: Brain learns from the result
            loss = brain.learn(problem_vector, result['state'])
            print(f"[Evolve] Brain updated neural weights. Loss: {loss:.6f}")

            # 5. Neuroevolution Check
            # Every 10 cycles, check if we are ready to grow a bigger brain
            if iteration % 10 == 0:
                evolved, message = brain.attempt_neuroevolution()
                if evolved:
                    print(f"*** EVOLUTIONARY EVENT *** {message}")

                brain.save_state("brain_state.pth")
                print("[System] Brain state saved.")

            # Brief pause to mimic "thought" and be polite to web servers
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[System] Saving state and shutting down...")
        brain.save_state("brain_state.pth")
        sys.exit(0)

if __name__ == "__main__":
    life_loop()
