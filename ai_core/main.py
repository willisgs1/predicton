import time
import os
import sys
import numpy as np
from ai_core.web_sensor import WebSensor
from ai_core.vision_sensor import VisionSensor
from ai_core.quantum_processor import QuantumCluster
from ai_core.brain import EvolutionaryBrain
from ai_core.memory import LongTermMemory
from ai_core.action import ActionModule

def life_loop():
    print("Initializing Quantum-Parallel Autonomous Agent (Generation 2 - Multimodal)...")

    # Initialize Components
    web_sensor = WebSensor()
    vision_sensor = VisionSensor()
    quantum_engine = QuantumCluster(use_real_hardware=False)
    brain = EvolutionaryBrain(input_size=16) # 8 Text + 8 Vision
    memory = LongTermMemory("memory.json")
    action_mod = ActionModule("workspace")

    # Load previous state
    brain.load_state("brain_state.pth")

    iteration = 0

    try:
        while True:
            iteration += 1
            print(f"\n--- Cycle {iteration} ---")

            # 1. Sense (Multimodal)
            text_vector, source_url = web_sensor.explore()
            if text_vector is None:
                time.sleep(2)
                continue

            print(f"[Input] Reading {source_url}")

            # Try to see
            visual_vector = vision_sensor.scan_page_for_images(source_url)
            if np.any(visual_vector):
                print(f"[Vision] Analyzed visual data from page.")

            # Combine Senses
            combined_input = np.concatenate((text_vector, visual_vector))

            # 2. Think
            decision_vector = brain.decide_action(combined_input)

            # 3. Act (External)
            # The brain might decide to write a file based on what it saw
            action_result = action_mod.execute_action(decision_vector, context_text=source_url)
            if "ACTION:" in action_result:
                print(f"[Action] {action_result}")

            # 4. Process (Quantum Internal)
            # We use the decision to guide the quantum search
            # We fold the 16-dim input back to 8-dim for the current 3-qubit circuit
            # (or we could upgrade the quantum circuit to 4 qubits, but let's fold for now)
            quantum_input = (combined_input[:8] + combined_input[8:]) / 2.0
            perturbation = decision_vector # Use brain output to perturb

            final_q_input = (quantum_input + perturbation) / 2.0

            print("[Process] Dispatching to Quantum Cluster...")
            start_time = time.time()
            result = quantum_engine.run_parallel_task(final_q_input)
            duration = time.time() - start_time

            print(f"[Result] Quantum State '{result['state']}' found in {duration:.4f}s")

            # 5. Memorize
            if result['confidence'] > 0.15: # Threshold for "interesting"
                memory.add_observation(source_url, result['state'], result['confidence'])
                memory.associate_concept("WebData", result['state'])

            # 6. Evolve
            loss = brain.learn(combined_input, result['state'])
            print(f"[Evolve] Loss: {loss:.6f}")

            if iteration % 10 == 0:
                evolved, message = brain.attempt_neuroevolution()
                if evolved:
                    print(f"*** EVOLUTIONARY EVENT *** {message}")
                brain.save_state("brain_state.pth")
                memory.save_memory()
                print("[System] State saved.")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[System] Saving state and shutting down...")
        brain.save_state("brain_state.pth")
        memory.save_memory()
        sys.exit(0)

if __name__ == "__main__":
    life_loop()
