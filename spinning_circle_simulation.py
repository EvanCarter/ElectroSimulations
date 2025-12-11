import math
from typing import List


DISK_RADIUS = 1
MAGNET_DIAMETER = 0.3
MAGNET_RADIUS = MAGNET_DIAMETER / 2.0
OFFSET_FROM_EDGE = 0.05

MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
# IF YOU TRY TO BREAK THE PHYSICS OF THE DISK
# THE CODE WILL PRINT OUT AN ERROR
# FOR NOW WE WILL ASSUME MAGNETS SIT IN CENTER
# OF RADIUS
NUM_OF_MAGNET = 4

## COIL STUFF
NUM_COILS = 3
COIL_RADIUS = MAGNET_RADIUS


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

    # Using the chord-to-angle formula: theta = 2 * arcsin(chord_length / (2 * radius))
    # image the the path that the magnet sits on and that the magnet diameter is how it occupies of that path
    # can talk about this in video
    theta_per_magent = 2 * math.asin(MAGNET_DIAMETER / (2 * MAGNET_PATH_RADIUS))
    max_possible_magnet = int((2 * math.pi) / theta_per_magent)

    print("Max magnets: ", max_possible_magnet)
    print("theta occupied per magnet: ", theta_per_magent)

    if NUM_OF_MAGNET > max_possible_magnet:
        print("ERROR: THIS MANY MAGNETS CAN NOT FIT")
        print(
            f"With these constraints can only accommodate {max_possible_magnet} magnets"
        )
        exit(1)


check_valid_constants()

MAGNET_ANGLE = 2.0 * math.pi / NUM_OF_MAGNET
COIL_ANGLE = 2.0 * math.pi / NUM_COILS

import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect("equal")

# draw the outer circle
outer_circle = plt.Circle(
    (0, 0), DISK_RADIUS, fill=False, edgecolor="black", linewidth=2
)
ax.add_patch(outer_circle)

# draw all magnets starting at 12 oclock (vertical aka pi/2) with appropriate offset and radius

for i in range(NUM_OF_MAGNET):
    magnet_angle = math.pi / 2 - (
        i * MAGNET_ANGLE
    )  # Start at 12 o'clock, rotate clockwise
    magnet_x = MAGNET_PATH_RADIUS * math.cos(magnet_angle)
    magnet_y = MAGNET_PATH_RADIUS * math.sin(magnet_angle)

    # Alternate colors: red for North (even index), blue for South (odd index)
    color = "red" if i % 2 == 0 else "blue"

    magnet = plt.Circle(
        (magnet_x, magnet_y),
        MAGNET_RADIUS,
        fill=True,
        facecolor=color,
        edgecolor="black",
    )
    ax.add_patch(magnet)


for j in range(NUM_COILS):
    coil_radius_position = DISK_RADIUS - COIL_RADIUS - OFFSET_FROM_EDGE
    coil = (math.pi / 2.0) - (j * COIL_ANGLE)
    coil_x = coil_radius_position * math.cos(coil)
    coil_y = coil_radius_position * math.sin(coil)

    coil_1_position = plt.Circle(
        (coil_x, coil_y),
        COIL_RADIUS,
        fill=False,
        edgecolor="orange",
        linewidth=4,
        linestyle="--",
    )
    ax.add_patch(coil_1_position)


# Set axis limits and show the plot
ax.set_xlim(-DISK_RADIUS * 1.2, DISK_RADIUS * 1.2)
ax.set_ylim(-DISK_RADIUS * 1.2, DISK_RADIUS * 1.2)
ax.grid(True, alpha=0.3)
plt.title(f"Magnet Layout ({NUM_OF_MAGNET} magnets)")
plt.show()


# now the goal is to calculate the flux over one single rotation. We want to model the coil configuration right now which we will assume
# has a leg width of 0. for now we will assume that there are the same number of coils
# and we will have to get the data out of each coil individually. so basically each coil has it's own voltage output
# and then we can see combination of this by wiring certain ones in series or in parallel


# Video Idea show how wiring in series or parallel affects magnets.
# show why you want even number of magnets.


# ## current work now let's plot 4 coils of the same magnet radius and same offset.

# starting with a single coil lets calculate the flux
STEPS_PER_ROTATION = 5000


#### MAGNETS
class Magnet:
    def __init__(self, theta, north):
        self.theta = theta
        self.north_pole = north

    def rotate(self):
        self.theta = self.theta - (2 * math.pi) / STEPS_PER_ROTATION
        if self.theta < 0:
            self.theta += 2 * math.pi


magnet_collection: List[Magnet] = []
for i in range(NUM_OF_MAGNET):
    theta = (math.pi / 2.0) - (MAGNET_ANGLE * i)
    if theta < 0:
        theta += math.pi * 2
    north = i % 2 == 0
    magnet = Magnet(theta, north)
    # magnet = Magnet(theta, False)
    magnet_collection.append(magnet)


### COILS
class Coil:
    voltages: List[float]
    fluxes: List[float]

    def __init__(self, theta: float):
        self.theta = theta
        self.voltages = []
        self.fluxes = []


coil_collection: List[Coil] = []
for i in range(NUM_COILS):
    theta = (math.pi / 2.0) - (i * COIL_ANGLE)
    if theta < 0:
        theta += math.pi * 2
    coil_collection.append(Coil(theta))

TOTAL_ROTATIONS = 1

time_per_rotation = 5
dt = time_per_rotation / STEPS_PER_ROTATION

TOTAL_SIZE = STEPS_PER_ROTATION * TOTAL_ROTATIONS
THETA_PER_MAGNET = 2 * math.asin(MAGNET_DIAMETER / (2 * MAGNET_PATH_RADIUS))

times = [0] * TOTAL_SIZE


def get_theta_distance(theta1, theta2):
    abs_diff = abs(theta1 - theta2)

    # if difference is 350 return 10
    return min(abs_diff, 2 * math.pi - abs_diff)


def get_area_between_circle(theta_dist, orbit_radius, r) -> float:
    """
    Calculates intersection area of two circles of radius 'r'
    orbiting at 'orbit_radius', separated by angle 'theta_dist'
    """

    # 1. convert angular distance to chord len
    d = 2 * orbit_radius * math.sin(theta_dist / 2.0)

    if d >= 2 * r:
        return 0

    if d == 0:
        return math.pi * (r**2)

    #    Area = 2*r^2 * arccos(d/2r) - (d/2)*sqrt(4r^2 - d^2)
    term1 = 2 * (r**2) * math.acos(d / (2 * r))
    term2 = 0.5 * d * math.sqrt(4 * (r**2) - d**2)
    return term1 - term2


# FOR VIDEO: Talk about how it is not necessarily trivial
# to calculate flux for each coil. Basically just do some filtering for all coils at first
# to see if there is an overlap
# and then after finding which magnet does have an overlap
# find what the current flux is which can just be overlapping area for now


# since the coil currently is the same radius
# we can check if a magnet is within (magnet diameter / math.2pi of magnet path)
# which is gives an angle so if magnet is more than half of that away from
# pi / 2 then it does not overlap


# note that at some point and I can talk about this in the video
# there is a trick since it is a cyclical graph
# i don't need to calculate flux for other magnets
# i can simple shift by certain angle

for j in range(STEPS_PER_ROTATION):
    for coil in coil_collection:

        total_flux_this_step = 0
        current_coil_theta = math.pi / 2.0
        # filter for magnets to find a magnet that overlaps

        magnet_theta_halved = THETA_PER_MAGNET / 2.0
        magn_num = 0
        for magnet in magnet_collection:
            # MAGNET IS ON CLOCKSIDE CHECK

            theta_dist = get_theta_distance(coil.theta, magnet.theta)
            if theta_dist < THETA_PER_MAGNET:
                overlap_area = get_area_between_circle(
                    theta_dist, MAGNET_PATH_RADIUS, MAGNET_RADIUS
                )

                if magnet.north_pole:
                    total_flux_this_step += overlap_area
                else:
                    total_flux_this_step -= overlap_area

        if j > 0:
            # voltage needs derivate so can only do it after first step
            voltage = (total_flux_this_step - coil.fluxes[-1]) / dt
            coil.voltages.append(voltage)
        coil.fluxes.append(total_flux_this_step)

    ## rotate after doing the work
    for magnet in magnet_collection:
        magnet.rotate()


# --- 4. PLOT RESULTS ---
# plt.figure(figsize=(10, 4))
# plt.plot(flux_readings)
# plt.title("Flux Through Coil 1 Over One Rotation")
# plt.xlabel("Step (0-720)")
# plt.ylabel("Flux (Overlap Area)")
# plt.grid(True, alpha=0.3)

# plt.show()
fig, axs = plt.subplots(4, 1, figsize=(10, 10))

for i in range(3):
    axs[i].plot(coil_collection[i].voltages)
    axs[i].set_title(f"Voltage Through Coil {i+1} Over One Rotation")
    axs[i].set_xlabel("Step")
    axs[i].set_ylabel("Voltage")
    axs[i].grid(True, alpha=0.3)

# Plot sum of absolute voltages
total_abs_voltage = [sum(abs(coil_collection[i].voltages[j]) for i in range(3)) for j in range(len(coil_collection[0].voltages))]

axs[3].plot(total_abs_voltage)
axs[3].set_title("Sum of Absolute Voltages From Coils 0-2")
axs[3].set_xlabel("Step")
axs[3].set_ylabel("Total Absolute Voltage")
axs[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
