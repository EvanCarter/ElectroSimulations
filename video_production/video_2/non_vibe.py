from manim import *


import math


def my_func(t):
    z = t / 3
    x = math.cos(2 * t)
    y = math.sin(2 * t)
    return [x, y, z]


def func2(t):
    z = t / 3
    x = math.cos(2 * t - PI)
    y = math.sin(2 * t - PI)
    return [x, y, z]


def update_vec_field(pos):
    x, y, z = pos

    magnitude = 0.5 * z + 2
    return np.array([0, 0, magnitude])


class TestScene(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(
            x_range=(-5, 5, 1),
            y_range=(-5, 5, 1),
            z_range=(-2, 5, 1),
            x_length=8,
            y_length=8,
            z_length=3,
        )

        # self.set_camera_orientation(phi=60 * DEGREES, theta=5 * DEGREES)
        self.set_camera_orientation(
            phi=60 * DEGREES,
            theta=5 * DEGREES,
        )

        # axes.shift(DOWN * 1)
        helix = ParametricFunction(
            lambda t: axes.c2p(*my_func(t)),
            t_range=(0, 18),
            color=RED,
        ).set_shade_in_3d(True)

        helix_2 = ParametricFunction(
            lambda t: axes.c2p(*func2(t)),
            t_range=(0, 18),
        ).set_color(BLUE)

        vector_field = ArrowVectorField(
            update_vec_field,
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            z_range=[-2, 5, 1],
            length_func=lambda norm: 0.45 * 0.5,
            colors=[GREEN, YELLOW],
        )

        self.add(vector_field)

        self.add(axes)

        self.play(Create(vector_field), run_time=2)

        self.begin_ambient_camera_rotation(rate=0.05)

        self.play(
            Create(helix, run_time=10),
            Create(helix_2, run_time=10),
            rate_func=linear,
        )

        # self.play(Create(helix, run_time=10), rate_func=linear)
