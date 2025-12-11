import os
import random
from ai_core.llm import LocalMind

class Architect:
    def __init__(self, plugins_dir="ai_core/plugins"):
        self.plugins_dir = plugins_dir
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

        # Initialize the LLM
        self.mind = LocalMind()

        # Fallback templates if LLM is offline
        self.genes = {
            "math": "    x = random.randint(1, 100)\n    y = random.randint(1, 100)\n    print(f'[Plugin] {x} * {y} = {x*y}')",
            "search": "    items = ['quantum', 'ai', 'data', 'code']\n    found = random.choice(items)\n    print(f'[Plugin] Found item: {found}')",
        }

    def attempt_creation(self, context="General exploration"):
        """
        Attempts to create a new plugin script using the LLM.
        """
        # 20% chance to create something new
        if random.random() < 0.2:
            self._synthesize_plugin(context)
            return True, "Architect synthesized a new skill."
        return False, "Architect is dreaming..."

    def _synthesize_plugin(self, context):
        plugin_id = int(random.random() * 10000)
        filename = f"skill_{plugin_id}.py"
        filepath = os.path.join(self.plugins_dir, filename)

        content = ""

        # Try LLM first
        if self.mind.active:
            print(f"[Architect] Asking Qwen to write code for: {context}")
            generated_code = self.mind.generate_code(context)
            if generated_code:
                content = generated_code
                # Ensure it has a run() function if the LLM forgot
                if "def run():" not in content:
                    content = "def run():\n    pass\n" + content

        # Fallback to templates if LLM failed or yielded empty
        if not content:
            gene = random.choice(list(self.genes.values()))
            content = "import random\nimport os\n\ndef run():\n"
            content += f"    print('[Plugin {plugin_id}] Executing...')\n"
            content += gene + "\n"

        with open(filepath, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    arch = Architect("test_plugins")
    arch.attempt_creation("Analyze network traffic")
