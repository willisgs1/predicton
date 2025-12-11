import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

class EvolutionaryBrain(nn.Module):
    def __init__(self, input_size=16, hidden_size=32, output_size=8):
        # Increased Input Size (8 Text + 8 Vision = 16)
        super(EvolutionaryBrain, self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        # Defining layers
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()

        self.optimizer = optim.Adam(self.parameters(), lr=0.01)
        self.loss_fn = nn.MSELoss()

        self.memory_loss = []

    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return self.sigmoid(out)

    def decide_action(self, combined_vector):
        """
        Decides how to perturb the quantum circuit AND what external action to take.
        """
        # Convert numpy to torch tensor
        input_tensor = torch.FloatTensor(combined_vector)

        with torch.no_grad():
            decision = self.forward(input_tensor)

        return decision.numpy()

    def learn(self, input_vector, quantum_result_state):
        target_val = int(quantum_result_state, 2) / 8.0
        target_vector = torch.full((8,), target_val)

        input_tensor = torch.FloatTensor(input_vector)

        self.optimizer.zero_grad()
        prediction = self.forward(input_tensor)
        loss = self.loss_fn(prediction, target_vector)
        loss.backward()
        self.optimizer.step()

        loss_val = loss.item()
        self.memory_loss.append(loss_val)
        if len(self.memory_loss) > 50:
            self.memory_loss.pop(0)

        return loss_val

    def attempt_neuroevolution(self):
        if len(self.memory_loss) < 50:
            return False, "Not enough data to evolve yet."

        avg_loss = sum(self.memory_loss) / len(self.memory_loss)

        if avg_loss < 0.005:
            self._grow_hidden_layer()
            self.memory_loss = []
            return True, "Brain Expanded: Added neurons to hidden layer!"

        return False, f"Stable. Avg Loss: {avg_loss:.4f}"

    def _grow_hidden_layer(self):
        new_hidden_size = self.hidden_size + 8
        print(f"[Neuroevolution] Growing hidden layer from {self.hidden_size} to {new_hidden_size}...")

        new_fc1 = nn.Linear(self.input_size, new_hidden_size)
        new_fc2 = nn.Linear(new_hidden_size, self.output_size)

        with torch.no_grad():
            # Copy weights carefully
            # Input dimension might match or be smaller/larger if we changed architecture recently
            # Here we assume input dimension is consistent for this session.
            new_fc1.weight[:self.hidden_size, :] = self.fc1.weight
            new_fc1.bias[:self.hidden_size] = self.fc1.bias

            new_fc2.weight[:, :self.hidden_size] = self.fc2.weight
            new_fc2.bias[:] = self.fc2.bias

        self.fc1 = new_fc1
        self.fc2 = new_fc2
        self.hidden_size = new_hidden_size
        self.optimizer = optim.Adam(self.parameters(), lr=0.01)

    def save_state(self, filepath="brain_state.pth"):
        state = {
            'state_dict': self.state_dict(),
            'hidden_size': self.hidden_size,
            'input_size': self.input_size # Save input size too
        }
        torch.save(state, filepath)

    def load_state(self, filepath="brain_state.pth"):
        if os.path.exists(filepath):
            try:
                checkpoint = torch.load(filepath)

                # Dynamic architecture adaptation
                saved_input = checkpoint.get('input_size', 16)
                saved_hidden = checkpoint.get('hidden_size', 32)

                if saved_input != self.input_size:
                    print(f"[Brain] Architecture mismatch (Saved Input: {saved_input}, Current: {self.input_size}). Resetting Brain to match new senses.")
                    # If input size changed (e.g. added Vision), we can't easily load old weights
                    # for the input layer without complex mapping.
                    # For this 'Seed', we accept a reset or we could try to pad.
                    # Let's pad/prune for robustness.
                    self.input_size = self.input_size
                    # We start fresh if senses change to avoid shape errors,
                    # or we could implement advanced surgery.
                    # Reset is safer for the user.
                    return

                if saved_hidden != self.hidden_size:
                    print(f"[Brain] Adapting to saved brain size: {saved_hidden} neurons")
                    self.hidden_size = saved_hidden
                    self.fc1 = nn.Linear(self.input_size, self.hidden_size)
                    self.fc2 = nn.Linear(self.hidden_size, self.output_size)
                    self.optimizer = optim.Adam(self.parameters(), lr=0.01)

                self.load_state_dict(checkpoint['state_dict'])
                print("[Brain] Loaded previous evolutionary state.")
            except Exception as e:
                print(f"[Brain] Error loading state: {e}. Starting fresh.")
        else:
            print("[Brain] Starting fresh evolution.")

if __name__ == "__main__":
    brain = EvolutionaryBrain()
    print("Brain initialized with Vision-Ready inputs.")
