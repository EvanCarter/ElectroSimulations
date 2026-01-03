"""
Scene 0: Recap - Linear to Circular Transition

Shows the transition from Video 1's linear track concept to Video 2's rotating generator:
1. Linear track with N/S magnets moving past a coil
2. Pause after magnets pass
3. Draw a circle
4. Move coil and magnets onto the circle (coil at 12, N at 9, S at 3 o'clock)
5. One full clockwise rotation of the rotor
"""
from manim import *
import numpy as np


class LinearToCircularScene(Scene):
    """
    Transition scene showing why we bend the line into a circle.

    Visual sequence:
    1. Linear track with coil, N and S magnets move past (left to right)
    2. Pause for 1 second after magnets pass
    3. Circle fades in
    4. Coil moves to top of circle (12 o'clock)
    5. Magnets move to 9 o'clock (N) and 3 o'clock (S)
    6. One full clockwise rotation
    """

    def construct(self):
        # ============================================================
        # CONSTANTS
        # ============================================================
        MAGNET_RADIUS = 0.5

        # Linear track parameters
        TRACK_Y = 0.5
        COIL_X = 0
        MAGNET_START_X = -6.0
        MAGNET_END_X = 6.0
        MAGNET_SPACING = 2.5

        # Circular generator parameters
        DISK_RADIUS = 2.5
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        CIRCLE_CENTER = ORIGIN

        # Coil dimensions (rectangle - matches smooth sine physics model)
        COIL_WIDTH = MAGNET_RADIUS * 1.5
        COIL_HEIGHT = MAGNET_RADIUS * 2.0

        # Timing
        LINEAR_DURATION = 3.0
        PAUSE_DURATION = 1.0
        TRANSITION_DURATION = 2.0

        # ============================================================
        # LINEAR TRACK ELEMENTS
        # ============================================================

        track = Line(
            start=LEFT * 7,
            end=RIGHT * 7,
            color=GREY,
            stroke_width=3
        ).shift(UP * TRACK_Y)

        coil = Rectangle(
            width=COIL_WIDTH,
            height=COIL_HEIGHT,
            color=ORANGE,
            stroke_width=6
        ).move_to([COIL_X, TRACK_Y, 0])

        # North magnet (red)
        north_magnet = Circle(
            radius=MAGNET_RADIUS,
            color=RED,
            fill_opacity=0.8
        ).set_fill(RED)
        north_label = Text("N", font_size=36, color=WHITE).move_to(north_magnet)
        north_group = VGroup(north_magnet, north_label)
        north_group.move_to([MAGNET_START_X, TRACK_Y, 0])

        # South magnet (blue)
        south_magnet = Circle(
            radius=MAGNET_RADIUS,
            color=BLUE,
            fill_opacity=0.8
        ).set_fill(BLUE)
        south_label = Text("S", font_size=36, color=WHITE).move_to(south_magnet)
        south_group = VGroup(south_magnet, south_label)
        south_group.move_to([MAGNET_START_X - MAGNET_SPACING, TRACK_Y, 0])

        magnets_group = VGroup(north_group, south_group)

        # ============================================================
        # CIRCULAR GENERATOR ELEMENTS
        # ============================================================

        stator = Circle(
            radius=DISK_RADIUS + 0.3,
            color=GRAY,
            stroke_width=8,
            stroke_opacity=0.5
        ).move_to(CIRCLE_CENTER)

        disk = Circle(
            radius=DISK_RADIUS,
            color=WHITE,
            stroke_opacity=0.5,
            stroke_width=2
        ).set_fill(GREY, opacity=0.1).move_to(CIRCLE_CENTER)

        # Target positions on circle
        COIL_ANGLE = PI / 2   # 12 o'clock
        NORTH_ANGLE = PI      # 9 o'clock
        SOUTH_ANGLE = 0       # 3 o'clock

        coil_circle_pos = CIRCLE_CENTER + np.array([
            MAGNET_PATH_RADIUS * np.cos(COIL_ANGLE),
            MAGNET_PATH_RADIUS * np.sin(COIL_ANGLE),
            0
        ])

        north_circle_pos = CIRCLE_CENTER + np.array([
            MAGNET_PATH_RADIUS * np.cos(NORTH_ANGLE),
            MAGNET_PATH_RADIUS * np.sin(NORTH_ANGLE),
            0
        ])

        south_circle_pos = CIRCLE_CENTER + np.array([
            MAGNET_PATH_RADIUS * np.cos(SOUTH_ANGLE),
            MAGNET_PATH_RADIUS * np.sin(SOUTH_ANGLE),
            0
        ])

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # Phase 1: Show linear track setup
        self.add(track)
        self.play(FadeIn(coil), run_time=0.5)
        self.play(FadeIn(magnets_group), run_time=0.5)
        self.wait(0.5)

        # Phase 2: Magnets move across (left to right)
        self.play(
            magnets_group.animate.shift(RIGHT * (MAGNET_END_X - MAGNET_START_X)),
            run_time=LINEAR_DURATION,
            rate_func=linear
        )

        # Phase 3: Pause after magnets pass
        self.wait(PAUSE_DURATION)

        # Phase 4: Fade out track, draw circle
        self.play(FadeOut(track), run_time=0.8)
        self.play(
            Create(stator),
            FadeIn(disk),
            run_time=1.5
        )

        # Phase 5: Move coil and magnets to circle positions
        self.play(
            coil.animate.move_to(coil_circle_pos),
            north_group.animate.move_to(north_circle_pos),
            south_group.animate.move_to(south_circle_pos),
            run_time=TRANSITION_DURATION
        )

        self.wait(0.5)

        # Phase 6: One full clockwise rotation of the rotor
        rotor = VGroup(north_group, south_group)
        self.play(
            Rotate(rotor, angle=-2*PI, about_point=CIRCLE_CENTER),
            run_time=3.0,
            rate_func=smooth
        )

        self.wait(1)
