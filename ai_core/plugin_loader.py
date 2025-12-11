import os
import importlib.util
import sys

class PluginLoader:
    def __init__(self, plugins_dir="ai_core/plugins"):
        self.plugins_dir = plugins_dir
        self.loaded_plugins = {}

    def scan_and_run(self):
        """
        Scans the plugins directory for new files and executes them.
        """
        if not os.path.exists(self.plugins_dir):
            return

        files = [f for f in os.listdir(self.plugins_dir) if f.endswith(".py")]

        for f in files:
            if f not in self.loaded_plugins:
                print(f"[Observer] Found new skill: {f}")
                try:
                    self._load_and_execute(f)
                    self.loaded_plugins[f] = True
                except Exception as e:
                    print(f"[Observer] Failed to run {f}: {e}")

    def _load_and_execute(self, filename):
        filepath = os.path.join(self.plugins_dir, filename)
        module_name = filename[:-3]

        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        if hasattr(module, 'run'):
            module.run()

if __name__ == "__main__":
    loader = PluginLoader("test_plugins")
    loader.scan_and_run()
