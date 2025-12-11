import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

class EvolutionaryBrain(nn.Module):
    def __init__(self, input_size=8, hidden_size=16, output_size=8):
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

    def decide_action(self, problem_vector):
        """
        Decides how to perturb the quantum circuit based on the input problem.
        Returns a modification vector.
        """
        # Convert numpy to torch tensor
        input_tensor = torch.FloatTensor(problem_vector)

        with torch.no_grad():
            decision = self.forward(input_tensor)

        return decision.numpy()

    def learn(self, input_vector, quantum_result_state):
        """
        The brain learns from the Quantum Result.
        """
        target_val = int(quantum_result_state, 2) / 8.0
        target_vector = torch.full((8,), target_val)

        input_tensor = torch.FloatTensor(input_vector)

        # Training Step
        self.optimizer.zero_grad()
        prediction = self.forward(input_tensor)
        loss = self.loss_fn(prediction, target_vector)
        loss.backward()
        self.optimizer.step()

        # Track loss for Evolution trigger
        loss_val = loss.item()
        self.memory_loss.append(loss_val)
        if len(self.memory_loss) > 50:
            self.memory_loss.pop(0)

        return loss_val

    def attempt_neuroevolution(self):
        """
        Checks if the brain has plateaued (mastered current level).
        If so, it grows new neurons (Neuroevolution).
        """
        if len(self.memory_loss) < 50:
            return False, "Not enough data to evolve yet."

        avg_loss = sum(self.memory_loss) / len(self.memory_loss)

        # If loss is very low, we have mastered this complexity level.
        # Time to grow!
        if avg_loss < 0.005:
            self._grow_hidden_layer()
            self.memory_loss = [] # Reset memory after growth
            return True, "Brain Expanded: Added neurons to hidden layer!"

        return False, f"Stable. Avg Loss: {avg_loss:.4f}"

    def _grow_hidden_layer(self):
        """
        Physically increases the size of the hidden layer.
        """
        new_hidden_size = self.hidden_size + 8
        print(f"[Neuroevolution] Growing hidden layer from {self.hidden_size} to {new_hidden_size}...")

        # Create new layers with larger size
        new_fc1 = nn.Linear(self.input_size, new_hidden_size)
        new_fc2 = nn.Linear(new_hidden_size, self.output_size)

        # Copy old weights to new layers (Knowledge Transfer)
        with torch.no_grad():
            new_fc1.weight[:self.hidden_size, :] = self.fc1.weight
            new_fc1.bias[:self.hidden_size] = self.fc1.bias

            new_fc2.weight[:, :self.hidden_size] = self.fc2.weight
            # We don't change fc2 bias as output size matches
            new_fc2.bias[:] = self.fc2.bias

        # Replace layers
        self.fc1 = new_fc1
        self.fc2 = new_fc2
        self.hidden_size = new_hidden_size

        # Re-initialize optimizer with new parameters
        self.optimizer = optim.Adam(self.parameters(), lr=0.01)

    def save_state(self, filepath="brain_state.pth"):
        state = {
            'state_dict': self.state_dict(),
            'hidden_size': self.hidden_size
        }
        torch.save(state, filepath)

    def load_state(self, filepath="brain_state.pth"):
        if os.path.exists(filepath):
            checkpoint = torch.load(filepath)

            # If the saved brain is bigger than current code, we must grow first
            saved_hidden = checkpoint.get('hidden_size', 16)
            if saved_hidden != self.hidden_size:
                print(f"[Brain] Adapting to saved brain size: {saved_hidden} neurons")
                self.hidden_size = saved_hidden
                self.fc1 = nn.Linear(self.input_size, self.hidden_size)
                self.fc2 = nn.Linear(self.hidden_size, self.output_size)
                self.optimizer = optim.Adam(self.parameters(), lr=0.01)

            self.load_state_dict(checkpoint['state_dict'])
            print("[Brain] Loaded previous evolutionary state.")
        else:
            print("[Brain] Starting fresh evolution.")

if __name__ == "__main__":
    brain = EvolutionaryBrain()
    dummy_in = np.random.rand(8)
    brain.attempt_neuroevolution()
