import os
import random
from ai_core.llm import LocalMind

class Architect:
    def __init__(self, plugins_dir="ai_core/plugins"):
        self.plugins_dir = plugins_dir
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)

        self.mind = LocalMind()
        self.genes = {
            "math": "    x = random.randint(1, 100)\n    y = random.randint(1, 100)\n    print(f'[Plugin] {x} * {y} = {x*y}')",
            "search": "    items = ['quantum', 'ai', 'data', 'code']\n    found = random.choice(items)\n    print(f'[Plugin] Found item: {found}')",
        }

    def attempt_creation(self, context="General exploration"):
        # 20% chance to create/refine
        if random.random() < 0.2:
            # 50/50 chance to Create New vs Refine Existing
            if random.random() < 0.5:
                self._synthesize_plugin(context)
                return True, "Architect synthesized a NEW skill."
            else:
                return self._refine_plugin()
        return False, "Architect is dreaming..."

    def _synthesize_plugin(self, context):
        plugin_id = int(random.random() * 10000)
        filename = f"skill_{plugin_id}.py"
        filepath = os.path.join(self.plugins_dir, filename)

        content = ""
        if self.mind.active:
            print(f"[Architect] Asking Qwen to write code for: {context}")
            content = self.mind.generate_code(context)
            if content and "def run():" not in content:
                content = "def run():\n    pass\n" + content

        if not content:
            gene = random.choice(list(self.genes.values()))
            content = "import random\nimport os\n\ndef run():\n"
            content += f"    print('[Plugin {plugin_id}] Executing...')\n"
            content += gene + "\n"

        with open(filepath, 'w') as f:
            f.write(content)

    def _refine_plugin(self):
        """
        Reads an existing plugin and asks the LLM to improve it.
        """
        if not self.mind.active:
            return False, "Architect cannot refine (LLM offline)."

        files = [f for f in os.listdir(self.plugins_dir) if f.endswith(".py") and "v2" not in f]
        if not files:
            return False, "No skills to refine."

        target_file = random.choice(files)
        filepath = os.path.join(self.plugins_dir, target_file)

        with open(filepath, 'r') as f:
            original_code = f.read()

        print(f"[Architect] Refining {target_file}...")
        prompt = f"Optimize and improve this Python code. Add error handling and comments.\n\nCode:\n{original_code}"
        new_code = self.mind.generate_code(prompt)

        if new_code:
            new_filename = target_file.replace(".py", "_v2.py")
            new_filepath = os.path.join(self.plugins_dir, new_filename)
            with open(new_filepath, 'w') as f:
                f.write(new_code)
            return True, f"Architect REFINED {target_file} into {new_filename}."

        return False, "Architect failed to refine."

if __name__ == "__main__":
    arch = Architect("test_plugins")
    arch.attempt_creation()
