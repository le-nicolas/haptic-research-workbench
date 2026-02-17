import pygame
import math

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Constants
GRAVITY = 9.8  # Gravitational acceleration (m/s^2)
TIME_STEP = 0.02  # Time step for simulation
ARM_LENGTH = 200  # Length of the pendulum arm (pixels)
PIVOT = (WIDTH // 2, HEIGHT // 4)  # Pivot point of the hinge

# Pendulum properties
angle = math.pi / 4  # Initial angle (45 degrees)
angular_velocity = 0  # Initial angular velocity
angular_acceleration = 0  # Initial angular acceleration
damping = 0.99  # Damping factor to simulate friction

# Convert from polar to Cartesian
def polar_to_cartesian(angle, length):
    x = length * math.sin(angle)
    y = length * math.cos(angle)
    return x, y

# Main simulation loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Physics update
    angular_acceleration = -(GRAVITY / ARM_LENGTH) * math.sin(angle)
    angular_velocity += angular_acceleration * TIME_STEP
    angular_velocity *= damping  # Apply damping
    angle += angular_velocity * TIME_STEP

    # Calculate pendulum position
    bob_x, bob_y = polar_to_cartesian(angle, ARM_LENGTH)
    bob_x += PIVOT[0]
    bob_y += PIVOT[1]

    # Rendering
    screen.fill((255, 255, 255))
    pygame.draw.line(screen, (0, 0, 0), PIVOT, (bob_x, bob_y), 2)  # Pendulum arm
    pygame.draw.circle(screen, (255, 0, 0), (int(bob_x), int(bob_y)), 15)  # Bob
    pygame.draw.circle(screen, (0, 0, 255), PIVOT, 5)  # Pivot

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
