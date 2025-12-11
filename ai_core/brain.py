import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os

class EvolutionaryBrain(nn.Module):
    def __init__(self, input_size=8, hidden_size=16, output_size=8):
        super(EvolutionaryBrain, self).__init__()
        # A simple Neural Network that evolves over time
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()

        self.optimizer = optim.Adam(self.parameters(), lr=0.01)
        self.loss_fn = nn.MSELoss()

        self.memory = [] # Short-term memory of actions

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
        If the quantum state has high entropy or novelty, we consider it a 'success'
        in this context (finding something complex).
        """
        # Convert quantum bitstring state '101' to a float target
        # In a real scenario, this 'target' comes from validating the solution.
        # Here, we treat the integer value of the bitstring as a target metric to match/predict.
        target_val = int(quantum_result_state, 2) / 8.0 # Normalize 3 bits (0-7)
        target_vector = torch.full((8,), target_val)

        input_tensor = torch.FloatTensor(input_vector)

        # Training Step
        self.optimizer.zero_grad()
        prediction = self.forward(input_tensor)
        loss = self.loss_fn(prediction, target_vector)
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def save_state(self, filepath="brain_state.pth"):
        torch.save(self.state_dict(), filepath)

    def load_state(self, filepath="brain_state.pth"):
        if os.path.exists(filepath):
            self.load_state_dict(torch.load(filepath))
            print("[Brain] Loaded previous evolutionary state.")
        else:
            print("[Brain] Starting fresh evolution.")

if __name__ == "__main__":
    brain = EvolutionaryBrain()
    dummy_in = np.random.rand(8)

    # Decision
    action = brain.decide_action(dummy_in)
    print("Brain Decision:", action)

    # Learning
    loss = brain.learn(dummy_in, "101")
    print("Learning Loss:", loss)
