from manim import *
from generator import build_rotor
import math
import numpy as np


class FinalProductScene(Scene):
    """
    Clean "Thank You" end card with slowly spinning 12/9 generator.

    Visual Elements:
    - 12-magnet / 9-coil generator on LEFT side
      - Slow rotation: 1 full rotation over 18 seconds
      - Phase-colored coils (Blue/Green/Orange)
    - "Thank You" text on RIGHT side
      - Large, bold, white text
      - Slightly right of center to balance with generator

    Animation Sequence (~12 seconds):
    1. [0.0s] Generator fades in, starts slow spin
    2. [1.0s] "Thank You" text fades in
    3. [1.0s-12.0s] Hold - slow elegant rotation continues
    4. [12.0s] End
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 2.2
        MAGNET_RADIUS = 0.25  # Smaller to fit 12 magnets
        OFFSET_FROM_EDGE = 0.15
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS

        NUM_MAGNETS = 12
        NUM_COILS = 9

        # Phase colors
        PHASE_A_COLOR = BLUE    # Coils 0, 3, 6
        PHASE_B_COLOR = GREEN   # Coils 2, 5, 8
        PHASE_C_COLOR = ORANGE  # Coils 1, 4, 7

        # Phase pattern: A, C, B, A, C, B, A, C, B
        # Indices 0,3,6 = A/BLUE; 1,4,7 = C/ORANGE; 2,5,8 = B/GREEN
        coil_colors = [
            PHASE_A_COLOR,  # 0
            PHASE_C_COLOR,  # 1
            PHASE_B_COLOR,  # 2
            PHASE_A_COLOR,  # 3
            PHASE_C_COLOR,  # 4
            PHASE_B_COLOR,  # 5
            PHASE_A_COLOR,  # 6
            PHASE_C_COLOR,  # 7
            PHASE_B_COLOR,  # 8
        ]

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        ROTATION_SPEED = 2 * PI / 18.0  # 1 rotation in 18 seconds (very slow)
        TOTAL_SCENE_TIME = 12.0

        # ============================================================
        # BUILD GENERATOR
        # ============================================================

        # Rotor with 12 magnets
        rotor = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

        # Stator ring outside magnets
        stator = Circle(
            radius=DISK_RADIUS + 0.25,
            color=GRAY,
            stroke_width=6,
            stroke_opacity=0.5
        )

        # 9 coils at magnet path radius
        coils = VGroup()
        for i in range(NUM_COILS):
            coil_angle = (PI / 2.0) - (i * (2 * PI / NUM_COILS))

            coil_pos = np.array([
                MAGNET_PATH_RADIUS * math.cos(coil_angle),
                MAGNET_PATH_RADIUS * math.sin(coil_angle),
                0
            ])

            # Square coil matching magnet diameter
            coil = Rectangle(
                width=MAGNET_RADIUS * 2.0,
                height=MAGNET_RADIUS * 2.0,
                color=coil_colors[i],
                stroke_width=5
            )
            # Rotate to be tangent to circle
            coil.rotate(coil_angle - PI / 2)
            coil.move_to(coil_pos)
            coils.add(coil)

        # Assemble generator
        generator = VGroup(stator, rotor, coils)
        generator.scale(0.9)
        generator.to_edge(LEFT, buff=0.8)

        rotor_center = rotor.get_center()

        # ============================================================
        # TEXT - "Thank You"
        # ============================================================

        thank_you = Text("Thank You", font_size=72, weight=BOLD, color=WHITE)
        # Position slightly right of center to balance with generator on left
        thank_you.move_to(RIGHT * 2.0)

        # ============================================================
        # ROTOR UPDATER
        # ============================================================
        time_tracker = ValueTracker(0)
        last_t = [0.0]

        def update_rotor(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t[0]
            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=rotor_center)
                last_t[0] = t_now

        rotor.add_updater(update_rotor)

        # ============================================================
        # ANIMATION SEQUENCE (~12 seconds)
        # ============================================================

        # [0.0s] Generator fades in, starts slow spin
        self.play(
            FadeIn(generator),
            time_tracker.animate.set_value(1.0),
            run_time=1.0,
            rate_func=linear
        )

        # [1.0s] "Thank You" fades in
        self.play(
            FadeIn(thank_you),
            time_tracker.animate.set_value(2.0),
            run_time=1.0,
            rate_func=linear
        )

        # [2.0s-12.0s] Hold - slow elegant rotation continues
        self.play(
            time_tracker.animate.set_value(TOTAL_SCENE_TIME),
            run_time=10.0,
            rate_func=linear
        )

        # Clean up updater
        rotor.remove_updater(update_rotor)

        # [12.0s] End
