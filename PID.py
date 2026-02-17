# reacting to current error, predicting future error, accounting for accumulated error over time

class PIDController:
    def __init__(self, kp, ki, kd):
        """
        Initializes the PID controller with gains for proportional, integral, and derivative terms.
        """
        self.kp = kp  # Proportional gain
        self.ki = ki  # Integral gain
        self.kd = kd  # Derivative gain
        
        self.prev_error = 0  # Store the previous error
        self.integral = 0    # Accumulated integral term
    
    def compute(self, setpoint, measured_value, dt):
        """
        Compute the control output based on the setpoint, measured value, and time step.
        
        :param setpoint: Desired target value.
        :param measured_value: Current measured value.
        :param dt: Time step since the last computation.
        :return: Control output.
        """
        # Calculate the error
        error = setpoint - measured_value
        
        # Proportional term
        p_term = self.kp * error
        
        # Integral term
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        # Derivative term
        derivative = (error - self.prev_error) / dt
        d_term = self.kd * derivative
        
        # Update the previous error
        self.prev_error = error
        
        # Compute the output
        output = p_term + i_term + d_term
        return output



import time

# Simulated system (e.g., a motor) and PID parameters
current_position = 0
target_position = 10
kp = 1.0
ki = 0.5
kd = 0.1

# Initialize the PID controller
pid = PIDController(kp, ki, kd)

# Simulated control loop
for step in range(100):
    # Time step (simulate a fixed interval)
    dt = 0.1  # 100ms
    time.sleep(dt)
    
    # Compute the control signal
    control_signal = pid.compute(target_position, current_position, dt)
    
    # Simulate the system's response (for simplicity, we directly add the control signal)
    current_position += control_signal * dt  # Basic integration for motion
    
    # Print the current state
    print(f"Step {step + 1}: Target = {target_position:.2f}, Position = {current_position:.2f}, Control Signal = {control_signal:.2f}")


