import math

# Define the Capstan class
class Capstan:
    def __init__(self, diameter):
        self.diameter = diameter  # Diameter of the capstan in meters
        self.rpm = 0  # Rotational speed in revolutions per minute

    def get_linear_speed(self):
        # Linear speed = Circumference × RPM / 60
        circumference = math.pi * self.diameter
        return (circumference * self.rpm) / 60

# Define the Tape class
class Tape:
    def __init__(self, length):
        self.length = length  # Length of the tape in meters
        self.position = 0  # Current position of the tape in meters

    def move(self, speed, time):
        # Update tape position based on speed and time
        self.position += speed * time
        if self.position > self.length:
            self.position = self.length  # Stop at the end

# Define the Motor class
class Motor:
    def __init__(self, max_torque):
        self.max_torque = max_torque  # Maximum torque in Nm
        self.power = 0  # Power level (0 to 1)

    def set_power(self, power):
        self.power = max(0, min(power, 1))  # Clamp power between 0 and 1

    def get_torque(self):
        return self.power * self.max_torque

# Define the Sensor class
class Sensor:
    def __init__(self):
        self.speed = 0  # Measured speed in m/s

    def measure_speed(self, capstan):
        self.speed = capstan.get_linear_speed()

# Define the Controller class
class Controller:
    def __init__(self, target_speed):
        self.target_speed = target_speed  # Desired tape speed in m/s
        self.error = 0

    def adjust_motor(self, sensor, motor):
        # Proportional control for simplicity
        self.error = self.target_speed - sensor.speed
        motor.set_power(motor.power + 0.1 * self.error)

# Main simulation
if __name__ == "__main__":
    # Initialize components
    capstan = Capstan(diameter=0.05)  # 5 cm diameter
    tape = Tape(length=10)  # 10 m tape
    motor = Motor(max_torque=0.2)  # 0.2 Nm max torque
    sensor = Sensor()
    controller = Controller(target_speed=0.5)  # 0.5 m/s target speed

    # Simulation parameters
    time_step = 0.1  # Time step in seconds
    total_time = 10  # Total simulation time in seconds

    for t in range(int(total_time / time_step)):
        # Measure speed
        sensor.measure_speed(capstan)

        # Adjust motor based on feedback
        controller.adjust_motor(sensor, motor)

        # Update capstan RPM
        capstan.rpm = (motor.get_torque() * 100)  # Simplified relation

        # Move the tape
        tape.move(capstan.get_linear_speed(), time_step)

        # Print state
        print(
            f"Time: {t * time_step:.2f}s, Tape Position: {tape.position:.2f}m, Speed: {sensor.speed:.2f}m/s"
        )
