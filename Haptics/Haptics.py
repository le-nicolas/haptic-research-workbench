import tkinter as tk
import math

# Constants
STIFFNESS = 0.5    # Stiffness constant
DAMPING = 0.2      # Damping coefficient
RADIUS_TOOL = 20   # Radius of the draggable tool
RADIUS_OBJECT = 30 # Radius of the static object
MASS_TOOL = 2.0    # Mass of the draggable tool
MASS_OBJECT = 5.0  # Mass of the static object
COEFFICIENT_RESTITUTION = 0.8  # Elasticity of the collision (1=perfectly elastic, 0=perfectly inelastic)

# Initialize Tkinter
root = tk.Tk()
root.title("Physics-Based Haptic Simulation")
canvas = tk.Canvas(root, width=400, height=400, bg="white")
canvas.pack()

# Create objects
static_obj = canvas.create_oval(150, 150, 150 + RADIUS_OBJECT*2, 150 + RADIUS_OBJECT*2, fill="blue")
draggable_tool = canvas.create_oval(50, 50, 50 + RADIUS_TOOL*2, 50 + RADIUS_TOOL*2, fill="red")

# Variables to store positions and velocities
tool_position = [60, 60]
tool_velocity = [0, 0]
object_velocity = [0, 0]  # The static object is stationary initially

# Update tool position
def update_position(event):
    global tool_position, tool_velocity
    old_x, old_y = tool_position
    tool_position = [event.x, event.y]
    tool_velocity = [tool_position[0] - old_x, tool_position[1] - old_y]

    # Move the tool
    canvas.coords(draggable_tool, 
                  tool_position[0] - RADIUS_TOOL, 
                  tool_position[1] - RADIUS_TOOL, 
                  tool_position[0] + RADIUS_TOOL, 
                  tool_position[1] + RADIUS_TOOL)

    # Compute and simulate collision
    compute_collision()

# Compute collision forces based on physics
def compute_collision():
    global object_velocity, tool_velocity

    # Get static object center
    static_coords = canvas.coords(static_obj)
    object_center = [
        (static_coords[0] + static_coords[2]) / 2,
        (static_coords[1] + static_coords[3]) / 2,
    ]

    # Compute distance between tool and object
    dx = tool_position[0] - object_center[0]
    dy = tool_position[1] - object_center[1]
    distance = math.sqrt(dx**2 + dy**2)

    # Check for collision
    if distance <= RADIUS_TOOL + RADIUS_OBJECT:
        # Normalize collision direction
        collision_normal = [dx / distance, dy / distance]

        # Relative velocity along the collision normal
        relative_velocity = (
            (tool_velocity[0] - object_velocity[0]) * collision_normal[0] +
            (tool_velocity[1] - object_velocity[1]) * collision_normal[1]
        )

        if relative_velocity < 0:  # Ensure objects are moving toward each other
            # Elastic collision equations
            new_tool_velocity = (
                tool_velocity[0] - (1 + COEFFICIENT_RESTITUTION) * MASS_OBJECT /
                (MASS_TOOL + MASS_OBJECT) * relative_velocity * collision_normal[0],
                tool_velocity[1] - (1 + COEFFICIENT_RESTITUTION) * MASS_OBJECT /
                (MASS_TOOL + MASS_OBJECT) * relative_velocity * collision_normal[1],
            )
            new_object_velocity = (
                object_velocity[0] + (1 + COEFFICIENT_RESTITUTION) * MASS_TOOL /
                (MASS_TOOL + MASS_OBJECT) * relative_velocity * collision_normal[0],
                object_velocity[1] + (1 + COEFFICIENT_RESTITUTION) * MASS_TOOL /
                (MASS_TOOL + MASS_OBJECT) * relative_velocity * collision_normal[1],
            )

            # Update velocities
            tool_velocity[:] = new_tool_velocity
            object_velocity[:] = new_object_velocity

            # Render collision force (visualization)
            collision_force = -relative_velocity * MASS_TOOL  # Simplified force
            render_force(collision_force, collision_normal)

# Render force as a visual arrow
def render_force(force, direction):
    canvas.delete("force")
    arrow_scale = 50  # Scale the force visualization
    force_vector = [force * d * arrow_scale for d in direction]
    canvas.create_line(
        tool_position[0], 
        tool_position[1], 
        tool_position[0] + force_vector[0], 
        tool_position[1] + force_vector[1],
        fill="green", arrow=tk.LAST, tags="force"
    )

# Bind mouse motion to tool updates
canvas.bind("<B1-Motion>", update_position)

root.mainloop()
