import pygame
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 400, 400
CAPSTAN_RADIUS = 100
FPS = 60  # Frames per second

class Simulation:
    def __init__(self, screen):
        self.screen = screen
        self.capstan_center = (WIDTH // 2, HEIGHT // 2)
        self.capstan_angle = 0  # Initial angle of rotation
        self.motor_power = 0.0
        self.rpm = 0.0
        self.font = pygame.font.SysFont('Arial', 20)

    def update_simulation(self):
        # Update motor power and RPM
        self.motor_power += 0.1  # Example update, you can adjust this
        self.rpm = self.motor_power * 10  # Example calculation, RPM = motor_power * factor

        # Calculate rotation angle
        angle = (self.rpm / 60) * 360  # Degrees per second
        self.capstan_angle = (self.capstan_angle + angle) % 360  # Keep the angle between 0 and 360

    def draw(self):
        # Clear screen
        self.screen.fill((255, 255, 255))

        # Draw capstan (circle with rotating arc)
        pygame.draw.circle(self.screen, (0, 0, 255), self.capstan_center, CAPSTAN_RADIUS)
        
        # Draw rotation arc for capstan
        pygame.draw.arc(self.screen, (255, 0, 0), 
                        (self.capstan_center[0] - CAPSTAN_RADIUS, self.capstan_center[1] - CAPSTAN_RADIUS,
                         2 * CAPSTAN_RADIUS, 2 * CAPSTAN_RADIUS), 
                        math.radians(0), math.radians(self.capstan_angle), 3)  # 3 is thickness of the arc

        # Render motor power text
        power_text = self.font.render(f"Motor Power: {self.motor_power:.2f}", True, (0, 0, 0))
        self.screen.blit(power_text, (10, 10))

    def run(self):
        clock = pygame.time.Clock()

        # Game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update simulation
            self.update_simulation()

            # Draw everything
            self.draw()

            # Update the display
            pygame.display.flip()

            # Cap the frame rate
            clock.tick(FPS)

        pygame.quit()

# Create the Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tape Motion Simulation")

# Create and run the simulation
sim = Simulation(screen)
sim.run()
