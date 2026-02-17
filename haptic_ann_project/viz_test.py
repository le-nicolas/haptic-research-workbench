import pygame
import numpy as np
import math

# Neural Network Visualization
class NeuralNetVisualizer:
    def __init__(self, screen, model, input_size=(400, 400)):
        self.screen = screen
        self.model = model
        self.input_size = input_size
        self.layers = [3, 64, 32, 10]  # Example architecture
        self.positions = self._calculate_positions()

    def draw_network(self, activations):
        for layer_idx, layer_activations in enumerate(activations):
            for neuron_idx, activation in enumerate(layer_activations):
                color = (255, 0, 0) if activation > 0 else (0, 0, 255)  # Example color logic
                pos = (50 + neuron_idx * 20, 50 + layer_idx * 50)
                pygame.draw.circle(self.screen, color, pos, 10) 

    def _calculate_positions(self):
        """Calculate positions of neurons for each layer."""
        positions = []
        spacing_x = self.input_size[0] // (len(self.layers) + 1)
        for i, neurons in enumerate(self.layers):
            layer_positions = []
            spacing_y = self.input_size[1] // (neurons + 1)
            for j in range(neurons):
                x = spacing_x * (i + 1)
                y = spacing_y * (j + 1)
                layer_positions.append((x, y))
            positions.append(layer_positions)
        return positions

    def draw_network(self, activations=None):
        """Draw the network and update activations."""
        for i, layer in enumerate(self.positions):
            for j, pos in enumerate(layer):
                color = (0, 0, 255) if activations is None else self._get_activation_color(activations[i][j])
                pygame.draw.circle(self.screen, color, pos, 10)
                if i < len(self.positions) - 1:
                    # Draw connections to the next layer
                    for next_pos in self.positions[i + 1]:
                        pygame.draw.line(self.screen, (200, 200, 200), pos, next_pos, 1)

    def _get_activation_color(self, activation):
        """Map activation to a color (blue to red)."""
        value = int(max(0, min(activation * 255, 255)))  # Normalize activation to 0–255
        return (value, 0, 255 - value)

    def update_activations(self, input_vector):
        """Perform forward pass and return activations."""
        activations = []
        x = input_vector
        for layer in self.model.fc:
            if isinstance(layer, pygame.nn.Linear):
                x = layer(x)
            elif isinstance(layer, pygame.nn.ReLU):
                x = np.maximum(0, x)
            activations.append(x)
        return activations

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Neural Network Visualization")
clock = pygame.time.Clock()

# Dummy Neural Network
class DummyNeuralNet:
    def __init__(self):
        self.fc = [
            lambda x: x @ np.random.rand(3, 64),
            lambda x: np.maximum(0, x),
            lambda x: x @ np.random.rand(64, 32),
            lambda x: np.maximum(0, x),
            lambda x: x @ np.random.rand(32, 10)
        ]

    def forward(self, x):
        activations = []
        for layer in self.fc:
            x = layer(x)
            activations.append(x)
        return activations

# Initialize components
model = DummyNeuralNet()
visualizer = NeuralNetVisualizer(screen, model)
running = True
input_vector = np.random.rand(3)

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill((30, 30, 30))

    # Update and draw network
    activations = model.forward(input_vector)
    visualizer.draw_network(activations)

    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
