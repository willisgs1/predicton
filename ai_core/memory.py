import json
import os
import time

class LongTermMemory:
    def __init__(self, filepath="memory.json"):
        self.filepath = filepath
        self.knowledge_graph = {
            "concepts": {},      # e.g., "Quantum" -> {related_to: ["Physics", "Computing"]}
            "observations": [],  # Log of interesting findings
            "stats": {"cycles": 0, "successful_mutations": 0}
        }
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.knowledge_graph = json.load(f)
                print(f"[Memory] Loaded {len(self.knowledge_graph['concepts'])} concepts.")
            except:
                print("[Memory] Corrupted memory file. Starting fresh.")

    def save_memory(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.knowledge_graph, f, indent=2)
        except Exception as e:
            print(f"[Memory] Failed to save: {e}")

    def add_observation(self, source_url, quantum_state, confidence):
        """
        Stores a high-confidence observation.
        """
        entry = {
            "timestamp": time.time(),
            "source": source_url,
            "state": quantum_state,
            "confidence": confidence
        }
        self.knowledge_graph["observations"].append(entry)

        # Keep size manageable
        if len(self.knowledge_graph["observations"]) > 1000:
            self.knowledge_graph["observations"].pop(0)

    def associate_concept(self, keyword, related_term):
        """
        Builds the graph. simple co-occurrence logic for this seed.
        """
        if keyword not in self.knowledge_graph["concepts"]:
            self.knowledge_graph["concepts"][keyword] = {"related": [], "weight": 0}

        if related_term not in self.knowledge_graph["concepts"][keyword]["related"]:
            self.knowledge_graph["concepts"][keyword]["related"].append(related_term)
            self.knowledge_graph["concepts"][keyword]["weight"] += 1

if __name__ == "__main__":
    mem = LongTermMemory("test_mem.json")
    mem.add_observation("http://google.com", "101", 0.99)
    mem.associate_concept("AI", "Quantum")
    mem.save_memory()
    print("Memory saved.")
