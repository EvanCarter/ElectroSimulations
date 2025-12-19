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
        ).set_color(RED)

        helix_2 = ParametricFunction(
            lambda t: axes.c2p(*func2(t)),
            t_range=(0, 18),
        ).set_color(BLUE)

        self.add(axes)

        self.begin_ambient_camera_rotation(rate=0.05)

        self.play(
            Create(helix, run_time=10),
            Create(helix_2, run_time=10),
            rate_func=linear,
        )

        # self.play(Create(helix, run_time=10), rate_func=linear)
