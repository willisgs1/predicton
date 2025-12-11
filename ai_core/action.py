import os
import random

class ActionModule:
    def __init__(self, workspace_dir="workspace"):
        self.workspace_dir = workspace_dir
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)

    def execute_action(self, action_vector, context_text=""):
        """
        Interprets the Brain's output vector into a concrete action.
        action_vector: numpy array of size 8
        """
        # We look at specific indices to trigger actions
        # Index 0: Trigger Threshold (> 0.8 means WRITE FILE)
        # Index 1-7: Content/Type selection

        trigger = action_vector[0]

        if trigger > 0.8:
            return self.write_observation(action_vector, context_text)
        elif trigger > 0.6:
            return self.update_manifest(action_vector)

        return "No external action taken."

    def write_observation(self, vector, context):
        filename = f"observation_{int(vector[1]*1000)}.txt"
        filepath = os.path.join(self.workspace_dir, filename)

        content = f"--- AI AUTONOMOUS LOG ---\n"
        content += f"Context: {context[:100]}...\n"
        content += f"Neural State: {vector}\n"
        content += f"Conclusion: This data pattern is significant.\n"

        try:
            with open(filepath, 'w') as f:
                f.write(content)
            return f"ACTION: Wrote file {filename}"
        except Exception as e:
            return f"ACTION FAILED: {e}"

    def update_manifest(self, vector):
        # A simulated "Self-Code-Modification" or config update
        filepath = os.path.join(self.workspace_dir, "manifest.txt")
        try:
            with open(filepath, 'a') as f:
                f.write(f"Update Vector: {vector}\n")
            return "ACTION: Updated Manifest"
        except:
            return "ACTION FAILED"

if __name__ == "__main__":
    act = ActionModule("test_workspace")
    res = act.execute_action([0.9, 0.5, 0.1, 0,0,0,0,0], "Test Context")
    print(res)
