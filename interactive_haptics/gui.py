from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .control import simulate_admittance, simulate_pid


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
