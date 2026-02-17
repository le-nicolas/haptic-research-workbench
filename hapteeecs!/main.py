import pygame
import tkinter as tk
from tkinter import messagebox
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 280, 280
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Create the Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Draw a Digit")

# Canvas settings
screen.fill(WHITE)

# Load pre-trained model
model = load_model(r"C:\Users\User\hapteeecs!\mnist_model.h5")

def preprocess(canvas):
    """Convert the Pygame canvas to a format suitable for the MNIST model."""
    data = pygame.surfarray.array3d(canvas)
    gray = np.mean(data, axis=2)  # Convert to grayscale
    scaled = np.transpose(gray, axes=(1, 0))  # Correct orientation
    resized = pygame.transform.scale(pygame.surfarray.make_surface(scaled), (28, 28))
    array = pygame.surfarray.array3d(resized).mean(axis=2) / 255.0  # Normalize
    return array.reshape(1, 28, 28, 1)

def show_prediction(prediction):
    """Display the model's prediction using Tkinter."""
    root = tk.Tk()
    root.withdraw()  # Hide main window
    guessed_number = np.argmax(prediction)
    probability = np.max(prediction)
    messagebox.showinfo("Prediction", f"I think the digit is {guessed_number} with {probability:.2%} confidence.")
    root.destroy()

# Drawing loop
running = True
drawing = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            drawing = True

        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:  # Clear the screen
                screen.fill(WHITE)

            elif event.key == pygame.K_p:  # Predict digit
                canvas = screen.copy()
                processed = preprocess(canvas)
                prediction = model.predict(processed)
                show_prediction(prediction)

    if drawing:
        pygame.draw.circle(screen, BLACK, pygame.mouse.get_pos(), 8)

    pygame.display.flip()

pygame.quit()
