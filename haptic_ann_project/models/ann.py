import torch
import torch.nn as nn

class ANN(nn.Module):
    def __init__(self, input_size=2, hidden_size=50, output_size=10):
        super(ANN, self).__init__()

        # Define layers
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Softmax(dim=1)  # For classification tasks
        )

    def forward(self, x):
        return self.network(x)

if __name__ == "__main__":
    # Example: Creating and testing the model
    input_size = 2  # (e.g., x, y coordinates from touchpad)
    hidden_size = 50
    output_size = 10  # Digits 0-9

    model = ANN(input_size, hidden_size, output_size)

    # Create a dummy input (batch of 5 samples, each with 2 features)
    dummy_input = torch.rand((5, input_size))

    # Perform forward pass
    output = model(dummy_input)

    print("Input:", dummy_input)
    print("Output:", output)
