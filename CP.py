import matplotlib.pyplot as plt
import numpy as np
import time

# PID Controller class
class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, setpoint, measured_value, dt):
        error = setpoint - measured_value
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative

# Virtual spring-damper system simulation
class VirtualSpringDamper:
    def __init__(self, stiffness, damping):
        self.stiffness = stiffness  # Spring constant (N/m)
        self.damping = damping      # Damping coefficient (Ns/m)
        self.position = 0.0         # Current position (m)
        self.velocity = 0.0         # Current velocity (m/s)

    def apply_force(self, external_force, dt):
        # Update position and velocity based on external force
        acceleration = (external_force - self.stiffness * self.position - self.damping * self.velocity)
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        return self.position

# Feedback-based actuator simulation
class Actuator:
    def __init__(self):
        self.output_force = 0.0

    def update_force(self, control_signal):
        self.output_force = control_signal

# Main simulation
def simulate_haptic_system():
    # Initialize components
    spring_damper = VirtualSpringDamper(stiffness=50, damping=10)
    actuator = Actuator()
    pid = PIDController(kp=10, ki=1, kd=0.5)

    # Simulation parameters
    target_position = 0.1  # Target position (m)
    time_step = 0.01       # Time step (s)
    total_time = 5.0       # Total simulation time (s)
    time_points = np.arange(0, total_time, time_step)

    # Data storage for visualization
    positions = []
    forces = []
    errors = []

    # Run simulation
    for t in time_points:
        # Simulate user applying a varying force (sinusoidal input)
        user_force = 20 * np.sin(2 * np.pi * 0.5 * t)

        # Compute actuator response using PID
        position = spring_damper.apply_force(user_force + actuator.output_force, time_step)
        control_signal = pid.compute(target_position, position, time_step)
        actuator.update_force(control_signal)

        # Store data
        positions.append(position)
        forces.append(actuator.output_force)
        errors.append(target_position - position)

        # Simulate a delay to match real-time operation
        time.sleep(time_step)

    # Visualize the results
    plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(time_points, positions, label="Position")
    plt.axhline(target_position, color="r", linestyle="--", label="Target")
    plt.ylabel("Position (m)")
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(time_points, forces, label="Actuator Force")
    plt.ylabel("Force (N)")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(time_points, errors, label="Error")
    plt.xlabel("Time (s)")
    plt.ylabel("Error (m)")
    plt.legend()

    plt.tight_layout()
    plt.show()

# Run the simulation
simulate_haptic_system()
