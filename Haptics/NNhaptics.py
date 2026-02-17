import torch
import torch.nn as nn

class HapticModel(nn.Module):
    def __init__(self):
        super(HapticModel, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(3, 64),  # Input layer: 3D position -> 64 neurons
            nn.ReLU(),         # Activation function
            nn.Linear(64, 32), # Hidden layer: 64 -> 32 neurons
            nn.ReLU(),         # Activation function
            nn.Linear(32, 3)   # Output layer: 32 -> 3 forces (fx, fy, fz)
        )

    def forward(self, x):
        return self.fc(x)

model = HapticModel()
