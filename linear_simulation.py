# 2d magnet
# magnetic field work

from typing import List
import matplotlib.pyplot as plt
import random
import math


COIL_X_1 = 0.5
COIL_WIDTH = 1
COIL_X_2 = COIL_X_1 + COIL_WIDTH

VELOCITY = 1

POINTS = 10000
MAGNET_RADIUS = 0.5
MAGNET_DECAY_RADIUS_ON = False
DECAY_TOLERANCE = 1.1


def get_point(radius):
    return random.random() * 2 * radius - radius


def get_random_valid_points() -> tuple[int, int]:
    radius = MAGNET_RADIUS

    if MAGNET_DECAY_RADIUS_ON:
        random_x = get_point(DECAY_TOLERANCE * radius)
        random_y = get_point(DECAY_TOLERANCE * radius)
        # not in circle so get new point
        while (
            math.sqrt(random_x * random_x + random_y * random_y)
            > DECAY_TOLERANCE * radius
        ):
            random_x = get_point(DECAY_TOLERANCE * radius)
            random_y = get_point(DECAY_TOLERANCE * radius)

        return (random_x, random_y)

    random_x = get_point(radius)
    random_y = get_point(radius)
    # not in circle so get new point
    while math.sqrt(random_x * random_x + random_y * random_y) > radius:
        random_x = get_point(radius)
        random_y = get_point(radius)

    return (random_x, random_y)


class Magnet:
    _inital_x = 0
    _initial_y = 0
    # velocity in the x direction
    velocity = 1
    # assuming constant in the y direction ( not moving up or down)
    # assuming north facing into plane for now

    # asssuming we just have a disk that is a radius of r
    # and that the field is emitted straight out from every point on magnet
    polarity = 1

    def __init__(self, inital_x=0, inital_y=0, polarity=1, velocity=1):
        self._inital_x = inital_x
        self._initial_y = inital_y
        self.velocity = velocity
        self.polarity = polarity

        # this represents the collections of 25 points to represent the magnet
        # field that is a random samply from within r

        self.positions = [(0, 0)] * POINTS
        for i in range(0, POINTS):
            random_x, random_y = get_random_valid_points()
            self.positions[i] = (self._inital_x + random_x, self._initial_y + random_y)

    # streghth being emitted from the radius.
    # let's assume there are var "POINTS" points right now on the radius
    # which we can compute at Magnet() into of a random samply of points from (-r,r)

    def field_emitted(self, x_1, x_2, y_1, y_2, t):
        # first find the current positions of all the random field samples

        flux = 0

        for i in range(POINTS):
            current_x = self.positions[i][0] + self.velocity * t
            current_y = self.positions[i][1]

            x_satisifed = x_1 <= current_x <= x_2
            y_satisified = y_1 <= current_y <= y_2
            if x_satisifed and y_satisified:
                flux += self.polarity
            else:

                ## DEPRECATED RIGHT NOW

                # let's assume that x is not satifisfed in this case and that from the radius of the magnet
                # the field drops off from Strenght ( 1 to 0 ) ( squared it to half )
                # IDK if this square dimihshed clamped to radius amount is accurate but let's go with it for now
                # changing it to max distance based on half radius
                # TODO DELETE BC THIS SHOULD BE PART OF THE MAGNET GRAPH NOT PART OF FIELD CALCULATION ON COIL
                if MAGNET_DECAY_RADIUS_ON:
                    distance_from_edge = min(abs(current_x - x_1), abs(current_x - x_2))
                    valid_external_mag_distance = MAGNET_RADIUS / 2
                    if distance_from_edge < (valid_external_mag_distance):
                        # since we're less than valid mag distance this will always be less than 1
                        normalized_distance_away = (
                            distance_from_edge / valid_external_mag_distance
                        )
                        flux += (1 - normalized_distance_away) ** 2

        return flux / POINTS


magnets: List[Magnet] = []


NUM_MAGNETS = 7
MAGNET_SPACING_GAP = 0
ALTERNATE_POLARITY = True
START_POSITION = (0, 0)


def magnet_factory():
    for i in range(NUM_MAGNETS):
        polarity = 1
        if ALTERNATE_POLARITY:
            polarity = (i % 2) * 2 - 1
        x_displacement = i * ((MAGNET_RADIUS * 2) + MAGNET_SPACING_GAP)
        mag = Magnet(
            START_POSITION[0] - x_displacement, START_POSITION[1], polarity, VELOCITY
        )

        magnets.append(mag)


magnet_factory()

# right now let's assume there is some sort of coil from 1.5 to 2.5 and we want to calculate flux
#  with a .1 step time increment
# assume it's always in the y for now


FINISH_LINE_X = 8

time_delta = 0.15
current_t = 0
STEPS = math.ceil(FINISH_LINE_X / time_delta)

# MAGNETS X NUMBERS OF STEPS SIZE ARRAYS

times = []
voltages = [[0 for _ in range(STEPS)] for _ in range(NUM_MAGNETS)]
fluxes = [[0 for _ in range(STEPS)] for _ in range(NUM_MAGNETS)]

print(len(voltages))


for i in range(STEPS):

    current_flux = 0
    # for magnet in magnets:

    previous_flux = 0 
    for k_prime in range(NUM_MAGNETS):
        magnet = magnets[k_prime]
        current_flux += magnet.field_emitted(COIL_X_1, COIL_X_2, -100, 100, current_t)

        current_voltage = 0
        if i > 0:
            last_flux = fluxes[k_prime][i - 1]
            current_voltage = (current_flux - last_flux) / time_delta
        fluxes[k_prime][i] = current_flux
        voltages[k_prime][i] = current_voltage

    # add vars:
    times.append(current_t)

    ## end of steps
    current_t += time_delta


rms_container = []
for w in range(NUM_MAGNETS):
    rms = 0
    for volt in voltages[w]:
        rms = rms + volt**2
    rms = math.sqrt(rms / len(voltages))
    print("ITER: ", w, " RMS:  ", rms)
    rms_container.append(rms)


# number of magnets vs RMS voltage

print( len(times))
print(len(fluxes[-1]))



plt.figure(figsize=(12, 8))  # Width, Height in inches
plt.subplot(3, 1, 1)  # 2 rows, 1 column, first plot
plt.plot(times, fluxes[-1])
plt.ylabel("Flux")
plt.title("Flux vs Time")

plt.subplot(3, 1, 2)  # 2 rows, 1 column, second plot
plt.plot(times, voltages[-1])
plt.xlabel("Time")
plt.ylabel("Voltage")
plt.title("Voltage vs Time")

plt.subplot(3, 1, 3)
plt.plot([*range(1,NUM_MAGNETS+1)], rms_container)
plt.title("Magnets vs RMS Voltage")



# Create parameter text
param_text = (
    f"Parameters:\n"
    f"Coil Width: {COIL_WIDTH}\n"
    f"Coil Position: [{COIL_X_1}, {COIL_X_2}]\n"
    f"Magnets: {len(magnets)}\n"
    f"Magnet Spacing: {MAGNET_SPACING_GAP}\n"
    f"Magnet Radius: {MAGNET_RADIUS}\n"
    f"Velocity: {VELOCITY}\n"
    f"Alternating Polarity: {ALTERNATE_POLARITY}\n"
    f"Points: {POINTS}\n"
    f"Δt: {time_delta}\n"
    f"RMS: {rms:.4f}V"
)

# # Adjust layout FIRST to make room
plt.tight_layout(rect=[0, 0, 0.75, 1])  # [left, bottom, right, top]

# Add text box to the right side AFTER adjusting layout
plt.figtext(
    0.78,
    0.5,
    param_text,
    fontsize=10,
    bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    verticalalignment="center",
)
plt.show()
