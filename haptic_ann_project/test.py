import pygame
from controllers.interaction2 import InteractionController
import numpy as np

# Dummy neural network for testing
class DummyNeuralNet:
    def predict(self, input_vector):
        return np.argmax(np.random.rand(10))  # Random digit prediction (0-9)

# Initialize Pygame and components
pygame.init()
screen = pygame.display.set_mode((400, 400))
pygame.display.set_caption("Touchpad Gesture Test")
clock = pygame.time.Clock()

# Initialize InteractionController
neural_net = DummyNeuralNet()
interaction_controller = InteractionController(neural_net_model=neural_net)

# Variables for testing
running = True
drawing = False
last_pos = None

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Start drawing
            drawing = True
            last_pos = pygame.mouse.get_pos()

        elif event.type == pygame.MOUSEBUTTONUP:
            # Stop drawing and process collected data
            drawing = False
            prediction = interaction_controller.preprocess_and_infer()
            print("Predicted Label:", prediction)
            interaction_controller.reset_interaction()

        elif event.type == pygame.MOUSEMOTION and drawing:
            # Record gesture while drawing
            current_pos = pygame.mouse.get_pos()
            pressure = 100  # Simulated constant pressure (can vary dynamically)
            interaction_controller.collect_raw_data((*current_pos, pressure))

            # Draw on the screen
            pygame.draw.line(screen, (0, 0, 255), last_pos, current_pos, 3)
            last_pos = current_pos

    # Update the display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
