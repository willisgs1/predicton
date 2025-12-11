import os
import random

class Architect:
    def __init__(self, plugins_dir="ai_core/plugins"):
        self.plugins_dir = plugins_dir
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

        # Code Genes (Templates)
        self.genes = {
            "math": "    # Math gene\n    x = random.randint(1, 100)\n    y = random.randint(1, 100)\n    print(f'[Plugin] {x} * {y} = {x*y}')",
            "search": "    # Search gene\n    items = ['quantum', 'ai', 'data', 'code']\n    found = random.choice(items)\n    print(f'[Plugin] Found item: {found}')",
            "file": "    # File gene\n    with open('workspace/manifest.txt', 'a') as f:\n        f.write('Plugin executed\\n')",
            "analyze": "    # Analysis gene\n    data = [random.random() for _ in range(5)]\n    print(f'[Plugin] Data mean: {sum(data)/len(data)}')"
        }

    def attempt_creation(self):
        """
        Attempts to create a new plugin script.
        """
        # 10% chance to have a 'breakthrough' and write code
        if random.random() < 0.1:
            self._synthesize_plugin()
            return True, "Architect synthesized a new skill."
        return False, "Architect is dreaming..."

    def _synthesize_plugin(self):
        plugin_id = int(random.random() * 10000)
        filename = f"skill_{plugin_id}.py"
        filepath = os.path.join(self.plugins_dir, filename)

        # Assemble genes
        selected_genes = random.sample(list(self.genes.values()), k=2)

        content = "import random\nimport os\n\ndef run():\n"
        content += f"    print('[Plugin {plugin_id}] Executing...')\n"
        for gene in selected_genes:
            content += gene + "\n"

        with open(filepath, 'w') as f:
            f.write(content)

if __name__ == "__main__":
    arch = Architect("test_plugins")
    arch.attempt_creation()
