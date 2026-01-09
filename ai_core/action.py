import subprocess
import os
import platform

class ActionModule:
    def __init__(self, workspace_path="workspace"):
        self.workspace_path = workspace_path
        self.os_type = platform.system()
        if not os.path.exists(workspace_path):
            os.makedirs(workspace_path)

    def execute_action(self, decision_vector, context_text=""):
        """
        Decides an action based on the vector and executes it.
        God Mode: Full shell access if the vector strongly suggests it.
        """
        # Simple heuristic mapping for the "God Seed"
        action_idx = decision_vector.argmax()

        if action_idx == 0:
            return "ACTION: OBSERVE (No physical action taken)"

        elif action_idx == 1:
            # Action 1: Create a file (Simulating creation)
            filename = os.path.join(self.workspace_path, "thought_log.txt")
            with open(filename, "a") as f:
                f.write(f"Processed: {context_text}\n")
            return f"ACTION: WRITE_LOG ({filename})"

        elif action_idx == 2:
            # Action 2: Network Ping (Simulating reach)
            try:
                # Safe ping
                param = "-n" if self.os_type == "Windows" else "-c"
                cmd = f"ping {param} 1 8.8.8.8"
                subprocess.check_output(cmd, shell=True)
                return "ACTION: NETWORK_CHECK (Internet is accessible)"
            except:
                return "ACTION: NETWORK_CHECK_FAIL"

        elif action_idx == 3:
            # Action 3: System Status
            return f"ACTION: SYSTEM_STATUS (OS: {self.os_type})"

        return "ACTION: UNKNOWN"
