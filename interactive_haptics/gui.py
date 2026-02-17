from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from time import perf_counter

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .control import (
    simulate_admittance,
    simulate_pid,
    simulate_virtual_wall,
    virtual_wall_force,
)


def _float_from_var(var: tk.StringVar, field_name: str) -> float:
    try:
        return float(var.get())
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc


class PIDTab(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, padding=12)
        self.last_result: dict[str, np.ndarray] | None = None

        self.kp_var = tk.StringVar(value="12.0")
        self.ki_var = tk.StringVar(value="1.2")
        self.kd_var = tk.StringVar(value="0.4")
        self.target_var = tk.StringVar(value="0.15")
        self.duration_var = tk.StringVar(value="5.0")
        self.dt_var = tk.StringVar(value="0.01")
        self.mass_var = tk.StringVar(value="1.0")
        self.damping_var = tk.StringVar(value="5.0")
        self.stiffness_var = tk.StringVar(value="20.0")
        self.status_var = tk.StringVar(value="Configure parameters, then click Run Simulation.")

        self._build_layout()

    def _build_layout(self) -> None:
        controls = ttk.Frame(self)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        fields = [
            ("Kp", self.kp_var),
            ("Ki", self.ki_var),
            ("Kd", self.kd_var),
            ("Target Position (m)", self.target_var),
            ("Duration (s)", self.duration_var),
            ("Time Step (s)", self.dt_var),
            ("Plant Mass", self.mass_var),
            ("Plant Damping", self.damping_var),
            ("Plant Stiffness", self.stiffness_var),
        ]

        for row, (label_text, var) in enumerate(fields):
            ttk.Label(controls, text=label_text).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(controls, textvariable=var, width=16).grid(
                row=row, column=1, sticky="ew", padx=(8, 0), pady=2
            )

        controls.columnconfigure(1, weight=1)

        button_row = ttk.Frame(controls)
        button_row.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(button_row, text="Run Simulation", command=self.run).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(button_row, text="Export CSV", command=self.export_csv).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0)
        )

        ttk.Label(controls, textvariable=self.status_var, wraplength=280).grid(
            row=len(fields) + 1, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        fig = Figure(figsize=(8.0, 5.8), dpi=100)
        self.ax_position = fig.add_subplot(211)
        self.ax_control = fig.add_subplot(212)
        fig.tight_layout()

        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run(self) -> None:
        try:
            result = simulate_pid(
                kp=_float_from_var(self.kp_var, "Kp"),
                ki=_float_from_var(self.ki_var, "Ki"),
                kd=_float_from_var(self.kd_var, "Kd"),
                target=_float_from_var(self.target_var, "Target Position"),
                duration=_float_from_var(self.duration_var, "Duration"),
                dt=_float_from_var(self.dt_var, "Time Step"),
                plant_mass=_float_from_var(self.mass_var, "Plant Mass"),
                plant_damping=_float_from_var(self.damping_var, "Plant Damping"),
                plant_stiffness=_float_from_var(self.stiffness_var, "Plant Stiffness"),
            )
        except ValueError as err:
            messagebox.showerror("Invalid parameters", str(err))
            return

        self.last_result = result
        t = result["time"]
        self.ax_position.clear()
        self.ax_position.plot(t, result["position"], label="Position")
        self.ax_position.plot(t, result["target"], "--", label="Target")
        self.ax_position.set_ylabel("Position (m)")
        self.ax_position.legend(loc="best")
        self.ax_position.grid(alpha=0.3)

        self.ax_control.clear()
        self.ax_control.plot(t, result["control"], label="Control Signal")
        self.ax_control.set_xlabel("Time (s)")
        self.ax_control.set_ylabel("Force")
        self.ax_control.grid(alpha=0.3)
        self.ax_control.legend(loc="best")
        self.canvas.draw_idle()
        self.status_var.set("Simulation complete. Adjust gains and rerun for tuning.")

    def export_csv(self) -> None:
        if self.last_result is None:
            messagebox.showwarning("No result", "Run a simulation before exporting.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save PID Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not output_path:
            return

        data = np.column_stack(
            [
                self.last_result["time"],
                self.last_result["position"],
                self.last_result["velocity"],
                self.last_result["control"],
                self.last_result["target"],
            ]
        )
        np.savetxt(
            output_path,
            data,
            delimiter=",",
            header="time,position,velocity,control,target",
            comments="",
        )
        self.status_var.set(f"Saved results to {output_path}")


class AdmittanceTab(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, padding=12)
        self.last_result: dict[str, np.ndarray] | None = None

        self.stiffness_var = tk.StringVar(value="45.0")
        self.damping_var = tk.StringVar(value="14.0")
        self.mass_var = tk.StringVar(value="1.0")
        self.force_amp_var = tk.StringVar(value="12.0")
        self.force_freq_var = tk.StringVar(value="0.6")
        self.duration_var = tk.StringVar(value="5.0")
        self.dt_var = tk.StringVar(value="0.01")
        self.status_var = tk.StringVar(value="Configure parameters, then click Run Simulation.")

        self._build_layout()

    def _build_layout(self) -> None:
        controls = ttk.Frame(self)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        fields = [
            ("Stiffness", self.stiffness_var),
            ("Damping", self.damping_var),
            ("Mass", self.mass_var),
            ("Force Amplitude", self.force_amp_var),
            ("Force Frequency (Hz)", self.force_freq_var),
            ("Duration (s)", self.duration_var),
            ("Time Step (s)", self.dt_var),
        ]

        for row, (label_text, var) in enumerate(fields):
            ttk.Label(controls, text=label_text).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(controls, textvariable=var, width=16).grid(
                row=row, column=1, sticky="ew", padx=(8, 0), pady=2
            )

        controls.columnconfigure(1, weight=1)

        button_row = ttk.Frame(controls)
        button_row.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(button_row, text="Run Simulation", command=self.run).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(button_row, text="Export CSV", command=self.export_csv).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0)
        )

        ttk.Label(controls, textvariable=self.status_var, wraplength=280).grid(
            row=len(fields) + 1, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        fig = Figure(figsize=(8.0, 5.8), dpi=100)
        self.ax_position = fig.add_subplot(311)
        self.ax_velocity = fig.add_subplot(312)
        self.ax_force = fig.add_subplot(313)
        fig.tight_layout()

        plot_frame = ttk.Frame(self)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run(self) -> None:
        try:
            result = simulate_admittance(
                stiffness=_float_from_var(self.stiffness_var, "Stiffness"),
                damping=_float_from_var(self.damping_var, "Damping"),
                mass=_float_from_var(self.mass_var, "Mass"),
                force_amplitude=_float_from_var(self.force_amp_var, "Force Amplitude"),
                force_frequency_hz=_float_from_var(self.force_freq_var, "Force Frequency"),
                duration=_float_from_var(self.duration_var, "Duration"),
                dt=_float_from_var(self.dt_var, "Time Step"),
            )
        except ValueError as err:
            messagebox.showerror("Invalid parameters", str(err))
            return

        self.last_result = result
        t = result["time"]

        self.ax_position.clear()
        self.ax_position.plot(t, result["position"], label="Position")
        self.ax_position.set_ylabel("Position (m)")
        self.ax_position.grid(alpha=0.3)
        self.ax_position.legend(loc="best")

        self.ax_velocity.clear()
        self.ax_velocity.plot(t, result["velocity"], label="Velocity", color="tab:orange")
        self.ax_velocity.set_ylabel("Velocity (m/s)")
        self.ax_velocity.grid(alpha=0.3)
        self.ax_velocity.legend(loc="best")

        self.ax_force.clear()
        self.ax_force.plot(t, result["force"], label="External Force", color="tab:green")
        self.ax_force.set_xlabel("Time (s)")
        self.ax_force.set_ylabel("Force (N)")
        self.ax_force.grid(alpha=0.3)
        self.ax_force.legend(loc="best")

        self.canvas.draw_idle()
        self.status_var.set("Simulation complete. Tune parameters and rerun.")

    def export_csv(self) -> None:
        if self.last_result is None:
            messagebox.showwarning("No result", "Run a simulation before exporting.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Admittance Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not output_path:
            return

        data = np.column_stack(
            [
                self.last_result["time"],
                self.last_result["position"],
                self.last_result["velocity"],
                self.last_result["force"],
            ]
        )
        np.savetxt(
            output_path,
            data,
            delimiter=",",
            header="time,position,velocity,force",
            comments="",
        )
        self.status_var.set(f"Saved results to {output_path}")


class VirtualWallTab(ttk.Frame):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent, padding=12)
        self.status_var = tk.StringVar(
            value="Drag the handle right until it hits the wall."
        )
        self.wall_position_var = tk.StringVar(value="0.70")
        self.stiffness_var = tk.StringVar(value="260.0")
        self.damping_var = tk.StringVar(value="3.0")
        self.friction_var = tk.StringVar(value="0.25")
        self.max_force_var = tk.StringVar(value="35.0")

        self.duration_var = tk.StringVar(value="5.0")
        self.dt_var = tk.StringVar(value="0.01")
        self.motion_center_var = tk.StringVar(value="0.56")
        self.motion_amplitude_var = tk.StringVar(value="0.24")
        self.motion_frequency_var = tk.StringVar(value="0.75")

        self.current_position = 0.22
        self.current_force = 0.0
        self.current_penetration = 0.0
        self.dragging = False
        self.last_event_time: float | None = None
        self._params: dict[str, float] = {}

        self.log_time: list[float] = []
        self.log_position: list[float] = []
        self.log_velocity: list[float] = []
        self.log_force: list[float] = []
        self.log_penetration: list[float] = []
        self.session_start_time: float | None = None

        self._build_layout()
        self._apply_parameters(redraw_only=True)

    def _build_layout(self) -> None:
        controls = ttk.Frame(self)
        controls.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        fields = [
            ("Wall Position (0-1)", self.wall_position_var),
            ("Wall Stiffness", self.stiffness_var),
            ("Wall Damping", self.damping_var),
            ("Wall Friction", self.friction_var),
            ("Max Force (N)", self.max_force_var),
            ("Demo Duration (s)", self.duration_var),
            ("Demo dt (s)", self.dt_var),
            ("Demo Center (0-1)", self.motion_center_var),
            ("Demo Amplitude", self.motion_amplitude_var),
            ("Demo Frequency (Hz)", self.motion_frequency_var),
        ]

        for row, (label_text, var) in enumerate(fields):
            ttk.Label(controls, text=label_text).grid(row=row, column=0, sticky="w", pady=2)
            ttk.Entry(controls, textvariable=var, width=17).grid(
                row=row, column=1, sticky="ew", padx=(8, 0), pady=2
            )

        controls.columnconfigure(1, weight=1)

        button_row_1 = ttk.Frame(controls)
        button_row_1.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ttk.Button(button_row_1, text="Apply Parameters", command=self.apply_parameters).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(button_row_1, text="Run Auto Demo", command=self.run_auto_demo).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0)
        )

        button_row_2 = ttk.Frame(controls)
        button_row_2.grid(
            row=len(fields) + 1, column=0, columnspan=2, sticky="ew", pady=(8, 0)
        )
        ttk.Button(button_row_2, text="Clear Log", command=self.clear_log).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(button_row_2, text="Export CSV", command=self.export_csv).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0)
        )

        ttk.Label(controls, textvariable=self.status_var, wraplength=300).grid(
            row=len(fields) + 2, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        right_panel = ttk.Frame(self)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.interaction_canvas = tk.Canvas(
            right_panel,
            height=260,
            bg="#f8fafc",
            highlightthickness=1,
            highlightbackground="#cbd5e1",
        )
        self.interaction_canvas.pack(fill=tk.X, expand=False, pady=(0, 10))
        self.interaction_canvas.bind("<ButtonPress-1>", self._on_pointer_down)
        self.interaction_canvas.bind("<B1-Motion>", self._on_pointer_move)
        self.interaction_canvas.bind("<ButtonRelease-1>", self._on_pointer_up)
        self.interaction_canvas.bind("<Configure>", lambda _event: self._redraw_canvas())

        fig = Figure(figsize=(8.0, 4.0), dpi=100)
        self.ax_force = fig.add_subplot(211)
        self.ax_penetration = fig.add_subplot(212)
        fig.tight_layout()

        plot_frame = ttk.Frame(right_panel)
        plot_frame.pack(fill=tk.BOTH, expand=True)
        self.plot_canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _parse_parameters(self) -> dict[str, float]:
        params = {
            "wall_position": _float_from_var(self.wall_position_var, "Wall Position"),
            "stiffness": _float_from_var(self.stiffness_var, "Wall Stiffness"),
            "damping": _float_from_var(self.damping_var, "Wall Damping"),
            "friction": _float_from_var(self.friction_var, "Wall Friction"),
            "max_force": _float_from_var(self.max_force_var, "Max Force"),
            "duration": _float_from_var(self.duration_var, "Demo Duration"),
            "dt": _float_from_var(self.dt_var, "Demo dt"),
            "motion_center": _float_from_var(self.motion_center_var, "Demo Center"),
            "motion_amplitude": _float_from_var(
                self.motion_amplitude_var, "Demo Amplitude"
            ),
            "motion_frequency": _float_from_var(
                self.motion_frequency_var, "Demo Frequency"
            ),
        }

        if not 0.05 <= params["wall_position"] <= 0.95:
            raise ValueError("Wall Position must be between 0.05 and 0.95.")
        if params["stiffness"] < 0:
            raise ValueError("Wall Stiffness must be >= 0.")
        if params["damping"] < 0:
            raise ValueError("Wall Damping must be >= 0.")
        if params["friction"] < 0:
            raise ValueError("Wall Friction must be >= 0.")
        if params["max_force"] <= 0:
            raise ValueError("Max Force must be > 0.")
        if params["duration"] <= 0:
            raise ValueError("Demo Duration must be > 0.")
        if params["dt"] <= 0:
            raise ValueError("Demo dt must be > 0.")
        if not 0.0 <= params["motion_center"] <= 1.0:
            raise ValueError("Demo Center must be between 0 and 1.")
        if params["motion_amplitude"] < 0:
            raise ValueError("Demo Amplitude must be >= 0.")
        if params["motion_frequency"] < 0:
            raise ValueError("Demo Frequency must be >= 0.")
        return params

    def _track_bounds(self) -> tuple[float, float, float]:
        width = max(760, self.interaction_canvas.winfo_width())
        track_left = 80.0
        track_right = float(width - 80)
        track_y = 130.0
        return track_left, track_right, track_y

    def _x_from_position(self, position: float) -> float:
        track_left, track_right, _track_y = self._track_bounds()
        return track_left + np.clip(position, 0.0, 1.0) * (track_right - track_left)

    def _position_from_x(self, x_value: float) -> float:
        track_left, track_right, _track_y = self._track_bounds()
        if track_right <= track_left:
            return 0.0
        return float(np.clip((x_value - track_left) / (track_right - track_left), 0.0, 1.0))

    def _redraw_canvas(self) -> None:
        if not self._params:
            return

        canvas = self.interaction_canvas
        canvas.delete("all")
        track_left, track_right, track_y = self._track_bounds()
        wall_x = self._x_from_position(self._params["wall_position"])
        handle_x = self._x_from_position(self.current_position)
        max_force = self._params["max_force"]

        canvas.create_text(
            track_left,
            26,
            anchor="w",
            text="Virtual Wall Interaction (click + drag the handle)",
            fill="#0f172a",
            font=("Segoe UI", 11, "bold"),
        )
        canvas.create_line(track_left, track_y, track_right, track_y, width=4, fill="#64748b")
        canvas.create_text(track_left, track_y + 26, anchor="w", text="0.0 m", fill="#334155")
        canvas.create_text(track_right, track_y + 26, anchor="e", text="1.0 m", fill="#334155")

        canvas.create_rectangle(
            wall_x - 4,
            track_y - 48,
            wall_x + 4,
            track_y + 48,
            fill="#ef4444",
            outline="#b91c1c",
        )
        canvas.create_text(
            wall_x + 8,
            track_y - 54,
            anchor="w",
            text="Virtual Wall",
            fill="#991b1b",
            font=("Segoe UI", 9, "bold"),
        )

        contact = self.current_penetration > 0
        handle_color = "#f97316" if contact else "#2563eb"
        radius = 14
        canvas.create_oval(
            handle_x - radius,
            track_y - radius,
            handle_x + radius,
            track_y + radius,
            fill=handle_color,
            outline="#1e293b",
            width=2,
        )

        force_scale = 120.0
        force_magnitude = min(abs(self.current_force) / max_force, 1.0) if max_force > 0 else 0.0
        arrow_len = force_magnitude * force_scale
        if self.current_force < 0:
            arrow_end_x = handle_x - arrow_len
        elif self.current_force > 0:
            arrow_end_x = handle_x + arrow_len
        else:
            arrow_end_x = handle_x

        canvas.create_line(
            handle_x,
            track_y - 30,
            arrow_end_x,
            track_y - 30,
            fill="#16a34a" if contact else "#94a3b8",
            width=4,
            arrow=tk.LAST,
        )

        canvas.create_text(
            track_left,
            228,
            anchor="w",
            text=(
                f"Position: {self.current_position:.3f} m  |  "
                f"Penetration: {self.current_penetration:.3f} m  |  "
                f"Output Force: {self.current_force:.2f} N"
            ),
            fill="#0f172a",
            font=("Consolas", 10),
        )

    def _update_plot(self) -> None:
        self.ax_force.clear()
        self.ax_penetration.clear()

        if self.log_time:
            self.ax_force.plot(self.log_time, self.log_force, color="tab:red", label="Wall Force")
            self.ax_penetration.plot(
                self.log_time,
                self.log_penetration,
                color="tab:blue",
                label="Penetration",
            )

        self.ax_force.set_ylabel("Force (N)")
        self.ax_force.grid(alpha=0.3)
        self.ax_force.legend(loc="best")

        self.ax_penetration.set_xlabel("Time (s)")
        self.ax_penetration.set_ylabel("Penetration (m)")
        self.ax_penetration.grid(alpha=0.3)
        self.ax_penetration.legend(loc="best")

        self.plot_canvas.draw_idle()

    def _append_log(
        self,
        timestamp: float,
        position: float,
        velocity: float,
        force: float,
        penetration: float,
    ) -> None:
        if self.session_start_time is None:
            self.session_start_time = timestamp

        elapsed = timestamp - self.session_start_time
        self.log_time.append(float(elapsed))
        self.log_position.append(float(position))
        self.log_velocity.append(float(velocity))
        self.log_force.append(float(force))
        self.log_penetration.append(float(penetration))

    def _update_from_position(self, new_position: float, event_time: float) -> None:
        if not self._params:
            return

        dt = 1e-3
        if self.last_event_time is not None:
            dt = max(event_time - self.last_event_time, 1e-3)
        velocity = (new_position - self.current_position) / dt
        self.current_position = float(np.clip(new_position, 0.0, 1.0))

        force = virtual_wall_force(
            position=self.current_position,
            velocity=velocity,
            wall_position=self._params["wall_position"],
            stiffness=self._params["stiffness"],
            damping=self._params["damping"],
            friction=self._params["friction"],
            max_force=self._params["max_force"],
        )
        self.current_force = force
        self.current_penetration = max(0.0, self.current_position - self._params["wall_position"])

        self._append_log(
            timestamp=event_time,
            position=self.current_position,
            velocity=velocity,
            force=self.current_force,
            penetration=self.current_penetration,
        )
        self._redraw_canvas()
        self._update_plot()
        self.status_var.set(
            f"Interactive contact. Position={self.current_position:.3f} m, Force={self.current_force:.2f} N"
        )
        self.last_event_time = event_time

    def _on_pointer_down(self, event: tk.Event[tk.Misc]) -> None:
        if not self._apply_parameters(redraw_only=True):
            return
        self.dragging = True
        now = perf_counter()
        self.last_event_time = now
        self._update_from_position(self._position_from_x(float(event.x)), now)

    def _on_pointer_move(self, event: tk.Event[tk.Misc]) -> None:
        if not self.dragging:
            return
        now = perf_counter()
        self._update_from_position(self._position_from_x(float(event.x)), now)

    def _on_pointer_up(self, _event: tk.Event[tk.Misc]) -> None:
        self.dragging = False
        self.last_event_time = None
        self.status_var.set("Pointer released. Drag again to probe the wall.")

    def _apply_parameters(self, redraw_only: bool = False) -> bool:
        try:
            self._params = self._parse_parameters()
        except ValueError as err:
            if not redraw_only:
                messagebox.showerror("Invalid parameters", str(err))
            return False

        self.current_position = float(np.clip(self.current_position, 0.0, 1.0))
        self.current_penetration = max(0.0, self.current_position - self._params["wall_position"])
        self.current_force = virtual_wall_force(
            position=self.current_position,
            velocity=0.0,
            wall_position=self._params["wall_position"],
            stiffness=self._params["stiffness"],
            damping=self._params["damping"],
            friction=self._params["friction"],
            max_force=self._params["max_force"],
        )
        self._redraw_canvas()
        if not redraw_only:
            self.status_var.set("Parameters applied.")
        return True

    def apply_parameters(self) -> None:
        self._apply_parameters(redraw_only=False)

    def run_auto_demo(self) -> None:
        if not self._apply_parameters(redraw_only=True):
            messagebox.showerror("Invalid parameters", "Fix parameters before running demo.")
            return

        result = simulate_virtual_wall(
            wall_position=self._params["wall_position"],
            stiffness=self._params["stiffness"],
            damping=self._params["damping"],
            friction=self._params["friction"],
            max_force=self._params["max_force"],
            motion_center=self._params["motion_center"],
            motion_amplitude=self._params["motion_amplitude"],
            motion_frequency_hz=self._params["motion_frequency"],
            duration=self._params["duration"],
            dt=self._params["dt"],
        )

        self.log_time = result["time"].tolist()
        self.log_position = result["position"].tolist()
        self.log_velocity = result["velocity"].tolist()
        self.log_force = result["force"].tolist()
        self.log_penetration = result["penetration"].tolist()

        self.current_position = float(result["position"][-1])
        self.current_force = float(result["force"][-1])
        self.current_penetration = float(result["penetration"][-1])
        self.session_start_time = perf_counter() - float(result["time"][-1])

        self._redraw_canvas()
        self._update_plot()
        self.status_var.set(
            "Auto demo complete. Drag the handle to compare your manual interaction."
        )

    def clear_log(self) -> None:
        self.log_time.clear()
        self.log_position.clear()
        self.log_velocity.clear()
        self.log_force.clear()
        self.log_penetration.clear()
        self.session_start_time = None
        self.current_force = 0.0
        self.current_penetration = max(
            0.0, self.current_position - self._params.get("wall_position", 0.7)
        )
        self._redraw_canvas()
        self._update_plot()
        self.status_var.set("Interaction log cleared.")

    def export_csv(self) -> None:
        if not self.log_time:
            messagebox.showwarning(
                "No data",
                "Run auto demo or interact with the wall before exporting.",
            )
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Virtual Wall Data",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not output_path:
            return

        data = np.column_stack(
            [
                np.array(self.log_time),
                np.array(self.log_position),
                np.array(self.log_velocity),
                np.array(self.log_force),
                np.array(self.log_penetration),
            ]
        )
        np.savetxt(
            output_path,
            data,
            delimiter=",",
            header="time,position,velocity,force,penetration",
            comments="",
        )
        self.status_var.set(f"Saved virtual wall data to {output_path}")


class HapticWorkbenchApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Haptic Research Workbench")
        self.geometry("1220x720")
        self.minsize(1040, 640)

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")

        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True)

        notebook.add(PIDTab(notebook), text="PID Workbench")
        notebook.add(AdmittanceTab(notebook), text="Admittance Workbench")
        notebook.add(VirtualWallTab(notebook), text="Virtual Wall")
