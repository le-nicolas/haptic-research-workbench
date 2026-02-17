# spherical five-bar mechanism 

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Define the mechanism parameters
r = 1.0  # Radius of the sphere
theta1 = np.radians(30)  # Fixed angle for link 1
phi1 = np.radians(45)    # Fixed angle for link 2

# Function to compute the endpoint of a link on the sphere
def spherical_to_cartesian(theta, phi, radius):
    x = radius * np.sin(theta) * np.cos(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(theta)
    return np.array([x, y, z])

# Define the link angles
theta2 = np.linspace(0, 2 * np.pi, 100)  # Variable angle for link 3
phi2 = np.linspace(0, 2 * np.pi, 100)    # Variable angle for link 4

# Calculate positions of links
points = [spherical_to_cartesian(theta1, phi1, r)]
for t, p in zip(theta2, phi2):
    points.append(spherical_to_cartesian(t, p, r))

# Convert to numpy array for plotting
points = np.array(points)

# Plot the mechanism
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, projection='3d')
ax.plot(points[:, 0], points[:, 1], points[:, 2], label="Link Path")
ax.scatter(0, 0, 0, c="red", label="Sphere Center")
ax.set_title("Spherical Five-Bar Mechanism")
ax.legend()
plt.show()
