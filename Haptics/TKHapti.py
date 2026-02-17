import tkinter as tk
import time

class Simulation:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=400, height=400)
        self.canvas.pack()
        self.capstan = self.canvas.create_arc(100, 100, 300, 300, start=0, extent=0, fill="blue")
        self.motor_power = 0.0
        self.rpm = 0.0
        self.power_label = tk.Label(root, text=f"Motor Power: {self.motor_power:.2f}")
        self.power_label.pack()
        self.update_simulation()

    def update_simulation(self):
        self.motor_power += 1.0  # Example update
        self.rpm = self.motor_power * 10  # Example calculation
        self.power_label.config(text=f"Motor Power: {self.motor_power:.2f}")

        # Simulate capstan rotation
        angle = (self.rpm / 60) * 360  # Degrees per second
        self.canvas.itemconfig(self.capstan, start=0, extent=angle)

        self.root.update()
        self.root.after(100, self.update_simulation)  # Schedule next update

# Run the Tkinter GUI
root = tk.Tk()
root.title("Tape Motion Simulation")
sim = Simulation(root)
root.mainloop()