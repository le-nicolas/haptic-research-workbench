#admittance control
import matplotlib.pyplot as plt
import numpy as np
import time

# Admittance control system
class AdmittanceControl:
    def __init__(self, desired_stiffness, desired_damping, mass=1.0):
        self.k = desired_stiffness  # Desired stiffness (N/m)
        self.b = desired_damping    # Desired damping (Ns/m)
        self.m = mass               # Mass of the system (kg)
        self.position = 0.0         # Current position (m)
        self.velocity = 0.0         # Current velocity (m/s)

    def apply_force(self, external_force, dt):
        # Admittance dynamics: F = m*a + b*v + k*x
        acceleration = (external_force - self.b * self.velocity - self.k * self.position) / self.m
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        return self.position, self.velocity

# Simulating an external user input force
def generate_user_force(t):
    # Example: A sinusoidal user-applied force
    return 10 * np.sin(2 * np.pi * 0.5 * t)  # Amplitude of 10N, frequency 0.5Hz

# Simulation parameters
def simulate_admittance_control():
    desired_stiffness = 50  # Stiffness (N/m)
    desired_damping = 20    # Damping (Ns/m)
    mass = 1.0              # Mass (kg)
    time_step = 0.01        # Time step (s)
    total_time = 5.0        # Total simulation time (s)
    time_points = np.arange(0, total_time, time_step)

    # Initialize the admittance control system
    admittance_system = AdmittanceControl(desired_stiffness, desired_damping, mass)

    # Data storage for visualization
    positions = []
    velocities = []
    forces = []

    # Simulate the system
    for t in time_points:
        external_force = generate_user_force(t)  # Get user-applied force
        position, velocity = admittance_system.apply_force(external_force, time_step)

        # Store data for analysis
        positions.append(position)
        velocities.append(velocity)
        forces.append(external_force)

        # Simulate real-time operation
        time.sleep(time_step)

    # Visualization
    plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(time_points, positions, label="Position")
    plt.ylabel("Position (m)")
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(time_points, velocities, label="Velocity")
    plt.ylabel("Velocity (m/s)")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(time_points, forces, label="External Force")
    plt.xlabel("Time (s)")
    plt.ylabel("Force (N)")
    plt.legend()

    plt.tight_layout()
    plt.show()

# Run the simulation
simulate_admittance_control()
