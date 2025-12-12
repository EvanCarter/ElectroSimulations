"""
Shared utilities for video animations - DRY principle
"""
from manim import *
import numpy as np


def create_bar_magnet(length=1.6, width=0.6, label_size=20):
    """Create a bar magnet with N and S halves."""
    magnet = VGroup()

    north = Rectangle(
        width=width,
        height=length/2,
        fill_color=RED,
        fill_opacity=0.9,
        stroke_width=2
    )
    north.shift(UP * length/4)

    south = Rectangle(
        width=width,
        height=length/2,
        fill_color=BLUE,
        fill_opacity=0.9,
        stroke_width=2
    )
    south.shift(DOWN * length/4)

    n_text = Text("N", font_size=label_size, color=WHITE, weight=BOLD).move_to(north)
    s_text = Text("S", font_size=label_size, color=WHITE, weight=BOLD).move_to(south)

    magnet.add(north, south, n_text, s_text)
    return magnet


def create_3d_bar_magnet(height=1.6, radius=0.3):
    """Create 3D bar magnet with N and S halves."""
    magnet = VGroup()

    north = Cylinder(
        radius=radius,
        height=height/2,
        direction=UP,
        fill_color=RED,
        fill_opacity=0.9,
        checkerboard_colors=False
    ).set_color(RED)
    north.move_to([0, height/4, 0])

    south = Cylinder(
        radius=radius,
        height=height/2,
        direction=UP,
        fill_color=BLUE,
        fill_opacity=0.9,
        checkerboard_colors=False
    ).set_color(BLUE)
    south.move_to([0, -height/4, 0])

    magnet.add(north, south)
    return magnet


def flux_function(position, peak_position=0, width=2.0):
    """
    Gaussian-like flux function for magnet passing through coil.
    position: current position
    peak_position: where flux is maximum
    width: how wide the flux peak is
    """
    return np.exp(-((position - peak_position) ** 2) / (2 * width ** 2))


def voltage_function(position, peak_position=0, width=2.0, velocity=1.0):
    """
    Voltage is derivative of flux.
    For Gaussian flux: V = -dΦ/dt = -dΦ/dx * dx/dt = -flux' * velocity
    """
    x = position
    x0 = peak_position
    sigma_sq = width ** 2

    flux_derivative = -((x - x0) / sigma_sq) * np.exp(-((x - x0) ** 2) / (2 * sigma_sq))
    return -flux_derivative * velocity


def create_field_arrows_3d(num_arrows=5, color=BLUE_C, arrow_length=1.0):
    """Create a VGroup of downward-pointing 3D field arrows."""
    arrows = VGroup()

    # Grid of arrows
    positions = []
    for dx in np.linspace(-0.3, 0.3, 3):
        for dy in np.linspace(-0.2, 0.2, 2):
            positions.append((dx, dy))

    for dx, dy in positions[:num_arrows]:
        arrow = Arrow3D(
            start=np.array([dx, dy, 0.6]),
            end=np.array([dx, dy, -0.4]),
            color=color,
            thickness=0.02
        )
        arrows.add(arrow)

    return arrows
