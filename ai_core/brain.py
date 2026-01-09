import json
import torch
import torch.nn as nn
import torch.optim as optim
import random
import os
import numpy as np

class SimpleNetwork(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(SimpleNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x

class EvolutionaryBrain:
    def __init__(self, input_size=16, hidden_size=64, output_size=4):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = SimpleNetwork(input_size, hidden_size, output_size).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()

        self.training_file = "training_data.jsonl"
        self.state_file = "brain_state.pth"

    def load_state(self, filepath):
        if os.path.exists(filepath):
            try:
                self.model.load_state_dict(torch.load(filepath, map_location=self.device))
                print(f"[Brain] Loaded neural state from {filepath}")
            except Exception as e:
                print(f"[Brain] Failed to load state: {e}. Starting fresh.")
        else:
            print("[Brain] No previous state found. Starting fresh.")

    def save_state(self, filepath):
        torch.save(self.model.state_dict(), filepath)

    def decide_action(self, input_vector):
        """
        Forward pass to make a decision.
        input_vector: numpy array
        Returns: numpy array (probabilities/activations)
        """
        # Ensure input is the right size (pad or trim)
        if len(input_vector) != self.input_size:
            # Simple resizing logic for robustness
            if len(input_vector) > self.input_size:
                input_vector = input_vector[:self.input_size]
            else:
                input_vector = np.pad(input_vector, (0, self.input_size - len(input_vector)), 'constant')

        state_tensor = torch.FloatTensor(input_vector).to(self.device)
        with torch.no_grad():
            output = self.model(state_tensor)
        return output.cpu().numpy()

    def learn(self, input_vector, result_state_str):
        """
        Updates weights based on the outcome.
        result_state_str: string like '000' from quantum processor
        """
        # Convert result string to a reward signal
        # '000' might be "good", '111' might be "bad".
        # This is a simplification.
        try:
            target_val = int(result_state_str, 2) / 8.0 # Normalize 0-7 to 0-1
        except:
            target_val = 0.5

        # Create a dummy target tensor
        target = torch.full((self.output_size,), target_val).to(self.device)

        # Ensure input sizing
        if len(input_vector) != self.input_size:
            if len(input_vector) > self.input_size:
                input_vector = input_vector[:self.input_size]
            else:
                input_vector = np.pad(input_vector, (0, self.input_size - len(input_vector)), 'constant')

        state_t = torch.FloatTensor(input_vector).to(self.device)

        prediction = self.model(state_t)
        loss = self.criterion(prediction, target)

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def attempt_neuroevolution(self):
        """
        Simulates structural change (neuroevolution).
        In a real scenario, this might add neurons or layers.
        Here, we introduce random mutation to weights to escape local minima.
        """
        mutation_rate = 0.01
        with torch.no_grad():
            for param in self.model.parameters():
                if random.random() < 0.1: # 10% chance to mutate a layer
                    noise = torch.randn_like(param) * mutation_rate
                    param.add_(noise)
        return True, "Neural weights mutated for adaptation."

    def export_training_data(self):
        """
        Called to dump memory to disk for the LLM fine-tuner.
        """
        # In this loop, we just ensure the file exists or rotate it.
        # The actual data logging happens in 'learn' or via memory module.
        pass
