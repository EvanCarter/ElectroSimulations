import math


DISK_RADIUS = 1
MAGNET_DIAMETER = .6
MAGNET_RADIUS = MAGNET_DIAMETER / 2.0
OFFSET_FROM_EDGE = .05
# IF YOU TRY TO BREAK THE PHYSICS OF THE DISK
# THE CODE WILL PRINT OUT AN ERROR
# FOR NOW WE WILL ASSUME MAGNETS SIT IN CENTER
# OF RADIUS
NUM_OF_MAGNET = 6


def check_valid_constants():
    # MAGNET DIAMETER MUST BE SMALLER THAN OR EQUAL TO DISK RADIUS
    if MAGNET_DIAMETER > DISK_RADIUS:
        print("ERROR: MAGNET RADIUS TOO LARGE FOR DISK RADIUS")
        exit(1)

    if MAGNET_DIAMETER + OFFSET_FROM_EDGE > DISK_RADIUS:
        print("ERROR: OFFSET IS TOO LARGE MAGNET OVERLAPS WITH CENTER OF DISK")
        exit(1)

    # substract the offset from the edge and then half the magnet radius
    # center point of the magnet sits here
    magnet_path_radius = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS

    # Using the chord-to-angle formula: theta = 2 * arcsin(chord_length / (2 * radius))
    # image the the path that the magnet sits on and that the magnet diameter is how it occupies of that path
    theta_per_magent = 2 * math.asin(MAGNET_DIAMETER / (2 * magnet_path_radius))
    max_possible_magnet = int((2 * math.pi) / theta_per_magent)

    print("Max magnets: ", max_possible_magnet)
    print("theta occupied per magnet: ", theta_per_magent)

    if NUM_OF_MAGNET > max_possible_magnet:
        print("ERROR: THIS MANY MAGNETS CAN NOT FIT")
        print(f"With these constraints can only accommodate {max_possible_magnet} magnets")
        exit(1)


check_valid_constants()

MAGNET_ANGLE = 2.0*math.pi / NUM_OF_MAGNET

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')

# draw the outer circle
outer_circle = plt.Circle((0, 0), DISK_RADIUS, fill=False, edgecolor='black', linewidth=2)
ax.add_patch(outer_circle)

# draw all magnets starting at 12 oclock (vertical aka pi/2) with appropriate offset and radius
magnet_path_radius = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS

for i in range(NUM_OF_MAGNET):
    magnet_angle = math.pi / 2 - (i * MAGNET_ANGLE)  # Start at 12 o'clock, rotate clockwise
    magnet_x = magnet_path_radius * math.cos(magnet_angle)
    magnet_y = magnet_path_radius * math.sin(magnet_angle)

    # Alternate colors: red for North (even index), blue for South (odd index)
    color = 'red' if i % 2 == 0 else 'blue'

    magnet = plt.Circle((magnet_x, magnet_y), MAGNET_RADIUS, fill=True, facecolor=color, edgecolor='black')
    ax.add_patch(magnet)

# Set axis limits and show the plot
ax.set_xlim(-DISK_RADIUS * 1.2, DISK_RADIUS * 1.2)
ax.set_ylim(-DISK_RADIUS * 1.2, DISK_RADIUS * 1.2)
ax.grid(True, alpha=0.3)
plt.title(f'Magnet Layout ({NUM_OF_MAGNET} magnets)')
plt.show()


# now the goal is to calculate the flux over one single rotation. We want to model the coil configuration right now which we will assume 
# has a leg width of 0. for now we will assume that there are the same number of coils
# and we will have to get the data out of each coil individually. so basically each coil has it's own voltage output
# and then we can see combination of this by wiring certain ones in series or in parallel


# Video Idea show how wiring in series or parallel affects magnets. 
# show why you want even number of magnets. 



# ## current work now let's plot 4 coils of the same magnet radius and same offset. 

# starting with a single coil 