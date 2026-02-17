import pygame
import numpy as np

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Constants
GRAVITY = np.array([0, 0.5])  # Gravity force
DAMPING = 0.98  # Damping factor for velocity
SPRING_CONSTANT = 0.1
NODE_MASS = 1.0

# Create nodes (masses) for a grid
GRID_SIZE = 10
SPACING = 50
nodes = []
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        nodes.append({
            'pos': np.array([SPACING * i + 100, SPACING * j + 50]),
            'prev_pos': np.array([SPACING * i + 100, SPACING * j + 50]),
            'fixed': j == 0  # Fix the top row
        })

# Create springs connecting adjacent nodes
springs = []
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        idx = i * GRID_SIZE + j
        if j < GRID_SIZE - 1:  # Horizontal spring
            springs.append((idx, idx + 1))
        if i < GRID_SIZE - 1:  # Vertical spring
            springs.append((idx, idx + GRID_SIZE))

def update_springs():
    for idx1, idx2 in springs:
        node1 = nodes[idx1]
        node2 = nodes[idx2]
        displacement = node2['pos'] - node1['pos']
        distance = np.linalg.norm(displacement)
        if distance == 0:
            continue
        force = SPRING_CONSTANT * (distance - SPACING) * (displacement / distance)
        if not node1['fixed']:
            node1['pos'] += force / NODE_MASS
        if not node2['fixed']:
            node2['pos'] = node2['pos'].astype(np.float64) #since subtraction of float from int is not allowed
            node2['pos'] -= force / NODE_MASS

def update_nodes():
    for node in nodes:
        if not node['fixed']:
            # Verlet integration for smooth motion
            temp = node['pos'].copy()
            velocity = (node['pos'] - node['prev_pos']) * DAMPING
            node['pos'] += velocity + GRAVITY
            node['prev_pos'] = temp

def draw():
    screen.fill((255, 255, 255))
    # Draw springs
    for idx1, idx2 in springs:
        pygame.draw.line(screen, (0, 0, 0), nodes[idx1]['pos'], nodes[idx2]['pos'], 1)
    # Draw nodes
    for node in nodes:
        color = (255, 0, 0) if node['fixed'] else (0, 0, 255)
        pygame.draw.circle(screen, color, node['pos'].astype(int), 5)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_springs()
    update_nodes()
    draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
