import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Create a 3D figure
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the Sun at the origin (0,0,0)
ax.scatter(0, 0, 0, color='yellow', s=200, label='Sun')

# Exoplanet positions relative to the Sun (in arbitrary units, e.g., light-years or AU)
# Format: (x, y, z)
exoplanets = {
    'Planet A': (4, 3, 5),
    'Planet B': (7, -2, 8),
    'Planet C': (-6, 1, -4),
    'Planet D': (2, -5, 2),
}

# Plot each exoplanet
for planet, (x, y, z) in exoplanets.items():
    ax.scatter(x, y, z, label=planet)



# Set labels and title
ax.set_xlabel('X axis (Distance)')
ax.set_ylabel('Y axis (Distance)')
ax.set_zlabel('Z axis (Distance)')
ax.set_title('Exoplanets Relative to the Sun')

# Display legend and plot
ax.legend()
plt.show()