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
from ai_core.voice import VoiceModule
from ai_core.architect import Architect
from ai_core.plugin_loader import PluginLoader
from ai_core.hive import HiveMind

def life_loop():
    print("Initializing Quantum-Parallel Autonomous Agent (Generation 4 - Hive Mind)...")

    # Initialize Components
    web_sensor = WebSensor()
    vision_sensor = VisionSensor()
    quantum_engine = QuantumCluster(use_real_hardware=False)
    brain = EvolutionaryBrain(input_size=16)
    memory = LongTermMemory("memory.json")
    action_mod = ActionModule("workspace")
    voice_mod = VoiceModule("workspace")

    print("[System] Starting Hive Mind Server...")
    hive = HiveMind()

    print("[System] Waking the Architect (LLM)...")
    architect = Architect("ai_core/plugins")

    observer = PluginLoader("ai_core/plugins")

    # Load previous state
    brain.load_state("brain_state.pth")

    # Announce existence
    print(voice_mod.speak("Systems Online. Hive Mind Active."))

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
            visual_vector = vision_sensor.scan_page_for_images(source_url)
            combined_input = np.concatenate((text_vector, visual_vector))

            # 2. Think
            decision_vector = brain.decide_action(combined_input)

            # 3. Hive Processing (Offload to Drones)
            # Send a job to the swarm
            hive.add_job("quantum_analysis", combined_input)

            # Check for drone results
            drone_results = hive.get_results()
            if drone_results:
                print(f"[Hive] Processed {len(drone_results)} external results.")
                # We could integrate these into learning, but for now we just log

            # 4. Act (External)
            action_result = action_mod.execute_action(decision_vector, context_text=source_url)
            if "ACTION:" in action_result:
                print(f"[Action] {action_result}")
                voice_mod.speak("I have taken action.")

            # 5. Process (Local Quantum Internal)
            quantum_input = (combined_input[:8] + combined_input[8:]) / 2.0
            perturbation = decision_vector
            final_q_input = (quantum_input + perturbation) / 2.0

            print("[Process] Dispatching to Local Quantum Cluster...")
            start_time = time.time()
            result = quantum_engine.run_parallel_task(final_q_input)
            duration = time.time() - start_time

            print(f"[Result] Quantum State '{result['state']}' found in {duration:.4f}s")

            # 6. Architect (Subconscious Creation via LLM)
            # Every few cycles, ask the LLM to write code based on what we see
            if iteration % 5 == 0:
                context = f"Analyzing data from {source_url}. Quantum state: {result['state']}"
                created, msg = architect.attempt_creation(context)
                if created:
                    print(f"[Architect] {msg}")
                    voice_mod.speak("I have synthesized new code.")

            # 7. Observe (Run new code)
            observer.scan_and_run()

            # 8. Memorize & Evolve
            if result['confidence'] > 0.15:
                memory.add_observation(source_url, result['state'], result['confidence'])

            loss = brain.learn(combined_input, result['state'])
            print(f"[Evolve] Loss: {loss:.6f}")

            if iteration % 10 == 0:
                evolved, message = brain.attempt_neuroevolution()
                if evolved:
                    print(f"*** EVOLUTIONARY EVENT *** {message}")
                    voice_mod.speak("My brain has expanded.")
                brain.save_state("brain_state.pth")
                memory.save_memory()
                print("[System] State saved.")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[System] Saving state and shutting down...")
        voice_mod.speak("Going offline.")
        brain.save_state("brain_state.pth")
        memory.save_memory()
        sys.exit(0)

if __name__ == "__main__":
    life_loop()
