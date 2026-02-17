from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _build_time_vector(duration: float, dt: float) -> np.ndarray:
    if duration <= 0:
        raise ValueError("duration must be > 0")
    if dt <= 0:
        raise ValueError("dt must be > 0")
    steps = int(duration / dt)
    return np.linspace(0.0, steps * dt, steps + 1)


@dataclass
class PIDController:
    kp: float
    ki: float
    kd: float
    integral_limit: float | None = None
    output_limit: float | None = None

    def __post_init__(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0

    def update(self, setpoint: float, measurement: float, dt: float) -> float:
        if dt <= 0:
            raise ValueError("dt must be > 0")

        error = setpoint - measurement
        self._integral += error * dt

        if self.integral_limit is not None:
            limit = abs(self.integral_limit)
            self._integral = float(np.clip(self._integral, -limit, limit))

        derivative = (error - self._prev_error) / dt
        output = self.kp * error + self.ki * self._integral + self.kd * derivative

        if self.output_limit is not None:
            limit = abs(self.output_limit)
            output = float(np.clip(output, -limit, limit))

        self._prev_error = error
        return output


@dataclass
class AdmittanceController:
    stiffness: float
    damping: float
    mass: float = 1.0
    position: float = 0.0
    velocity: float = 0.0

    def step(self, external_force: float, dt: float) -> tuple[float, float]:
        if dt <= 0:
            raise ValueError("dt must be > 0")
        if self.mass <= 0:
            raise ValueError("mass must be > 0")

        acceleration = (
            external_force
            - self.damping * self.velocity
            - self.stiffness * self.position
        ) / self.mass
        self.velocity += acceleration * dt
        self.position += self.velocity * dt
        return self.position, self.velocity


def simulate_pid(
    kp: float = 12.0,
    ki: float = 1.2,
    kd: float = 0.4,
    target: float = 0.15,
    duration: float = 5.0,
    dt: float = 0.01,
    plant_mass: float = 1.0,
    plant_damping: float = 5.0,
    plant_stiffness: float = 20.0,
) -> dict[str, np.ndarray]:
    if plant_mass <= 0:
        raise ValueError("plant_mass must be > 0")

    time = _build_time_vector(duration, dt)
    pid = PIDController(kp=kp, ki=ki, kd=kd, output_limit=120.0, integral_limit=10.0)

    position = np.zeros_like(time)
    velocity = np.zeros_like(time)
    control_signal = np.zeros_like(time)

    x = 0.0
    v = 0.0
    for idx, _ in enumerate(time):
        u = pid.update(target, x, dt)
        a = (u - plant_damping * v - plant_stiffness * x) / plant_mass
        v += a * dt
        x += v * dt

        position[idx] = x
        velocity[idx] = v
        control_signal[idx] = u

    target_vector = np.full_like(time, target)
    return {
        "time": time,
        "position": position,
        "velocity": velocity,
        "control": control_signal,
        "target": target_vector,
    }


def simulate_admittance(
    stiffness: float = 45.0,
    damping: float = 14.0,
    mass: float = 1.0,
    force_amplitude: float = 12.0,
    force_frequency_hz: float = 0.6,
    duration: float = 5.0,
    dt: float = 0.01,
) -> dict[str, np.ndarray]:
    time = _build_time_vector(duration, dt)
    controller = AdmittanceController(stiffness=stiffness, damping=damping, mass=mass)

    position = np.zeros_like(time)
    velocity = np.zeros_like(time)
    force = np.zeros_like(time)

    for idx, t in enumerate(time):
        f_ext = force_amplitude * np.sin(2.0 * np.pi * force_frequency_hz * t)
        pos, vel = controller.step(f_ext, dt)
        position[idx] = pos
        velocity[idx] = vel
        force[idx] = f_ext

    return {
        "time": time,
        "position": position,
        "velocity": velocity,
        "force": force,
    }
