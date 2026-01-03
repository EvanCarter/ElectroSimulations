from manim import *
import math
import numpy as np


class ForceBalanceScene(Scene):
    """
    Demonstrates why 3-phase generators have no shaft wobble - forces cancel perfectly.

    Visual elements:
    - Simple generator circle with 3 coils at 120 degrees apart (A, B, C)
    - Three force vectors of EQUAL magnitude that ROTATE together
    - Vectors stay 120 degrees apart at all times (rotating directions, not pulsing magnitudes)
    - Tip-to-tail addition showing closed equilateral triangle that rotates but always closes
    - "Net Force = 0" label

    Animation sequence:
    1. Show generator with labeled coils A, B, C
    2. Draw force vectors from center - these ROTATE (not pulse)
    3. Animate vectors rotating together, always 120 degrees apart
    4. Transform vectors to tip-to-tail arrangement forming closed triangle
    5. Show net force = 0 with the triangle always closing perfectly
    6. Brief contrast with 2-phase showing non-closure

    Key physics insight: For 3-phase forces to cancel, they must be three unit vectors
    at 0, 120, and 240 degrees that ROTATE together. The sum of three unit vectors
    at these angles is exactly zero at all times:
    - F_A = (cos(wt), sin(wt))
    - F_B = (cos(wt + 120), sin(wt + 120))
    - F_C = (cos(wt + 240), sin(wt + 240))
    These form a closed equilateral triangle that rotates but ALWAYS closes.
    """

    def construct(self):
        # ============================================================
        # PARAMETERS
        # ============================================================
        GENERATOR_RADIUS = 2.0
        COIL_RADIUS = 0.3
        MAX_FORCE_LENGTH = 1.8  # Maximum arrow length
        ROTATION_SPEED = PI / 2  # rad/s for force oscillation

        # Phase angles for 3-phase (120 degrees apart)
        PHASE_A = 0
        PHASE_B = 2 * PI / 3
        PHASE_C = 4 * PI / 3

        # Coil positions (angular position from top, clockwise)
        COIL_A_ANGLE = PI / 2  # 12 o'clock (top)
        COIL_B_ANGLE = PI / 2 - 2 * PI / 3  # 4 o'clock
        COIL_C_ANGLE = PI / 2 - 4 * PI / 3  # 8 o'clock

        # Colors
        COLOR_A = BLUE
        COLOR_B = ORANGE
        COLOR_C = GREEN

        # ============================================================
        # FORCE CALCULATION FUNCTIONS (ROTATING VECTORS)
        # ============================================================
        def get_rotating_force_vector(t, phase_offset, magnitude):
            """
            Get a force vector that ROTATES with time.

            For 3-phase balance, we need three vectors of EQUAL magnitude
            that rotate together, staying 120 degrees apart.

            The direction rotates: angle = wt + phase_offset
            The magnitude stays CONSTANT.

            This gives:
            - F_A = magnitude * (cos(wt), sin(wt))
            - F_B = magnitude * (cos(wt + 2pi/3), sin(wt + 2pi/3))
            - F_C = magnitude * (cos(wt + 4pi/3), sin(wt + 4pi/3))

            Sum of these three = 0 at all times (they form a closed triangle).
            """
            angle = ROTATION_SPEED * t + phase_offset
            return magnitude * np.array([np.cos(angle), np.sin(angle), 0])

        # ============================================================
        # VISUAL ELEMENTS - GENERATOR
        # ============================================================
        # Generator circle (stator)
        generator_circle = Circle(
            radius=GENERATOR_RADIUS,
            color=GREY,
            stroke_width=4,
            stroke_opacity=0.7
        )

        # Center dot
        center_dot = Dot(ORIGIN, color=WHITE, radius=0.08)

        # Coils at 120 degree positions
        coil_positions = [
            np.array([GENERATOR_RADIUS * np.cos(COIL_A_ANGLE), GENERATOR_RADIUS * np.sin(COIL_A_ANGLE), 0]),
            np.array([GENERATOR_RADIUS * np.cos(COIL_B_ANGLE), GENERATOR_RADIUS * np.sin(COIL_B_ANGLE), 0]),
            np.array([GENERATOR_RADIUS * np.cos(COIL_C_ANGLE), GENERATOR_RADIUS * np.sin(COIL_C_ANGLE), 0]),
        ]

        coil_a = Circle(radius=COIL_RADIUS, color=COLOR_A, stroke_width=4, fill_opacity=0.3, fill_color=COLOR_A)
        coil_a.move_to(coil_positions[0])
        label_a = Text("A", font_size=28, color=COLOR_A).next_to(coil_a, UP, buff=0.1)

        coil_b = Circle(radius=COIL_RADIUS, color=COLOR_B, stroke_width=4, fill_opacity=0.3, fill_color=COLOR_B)
        coil_b.move_to(coil_positions[1])
        label_b = Text("B", font_size=28, color=COLOR_B).next_to(coil_b, DOWN + RIGHT, buff=0.1)

        coil_c = Circle(radius=COIL_RADIUS, color=COLOR_C, stroke_width=4, fill_opacity=0.3, fill_color=COLOR_C)
        coil_c.move_to(coil_positions[2])
        label_c = Text("C", font_size=28, color=COLOR_C).next_to(coil_c, DOWN + LEFT, buff=0.1)

        generator_group = VGroup(generator_circle, center_dot, coil_a, coil_b, coil_c, label_a, label_b, label_c)
        generator_group.to_edge(LEFT, buff=1.5)
        gen_center = generator_circle.get_center()

        # ============================================================
        # FORCE VECTORS (ROTATING from center)
        # ============================================================
        time_tracker = ValueTracker(0)

        # Create arrows with updaters - all have EQUAL magnitude, different phase
        def create_force_arrow(phase_offset, color):
            """Create an arrow that ROTATES based on time."""
            arrow = Arrow(
                start=gen_center,
                end=gen_center + get_rotating_force_vector(0, phase_offset, MAX_FORCE_LENGTH),
                color=color,
                buff=0,
                stroke_width=6,
                max_tip_length_to_length_ratio=0.25
            )
            arrow.phase_offset = phase_offset
            return arrow

        arrow_a = create_force_arrow(PHASE_A, COLOR_A)
        arrow_b = create_force_arrow(PHASE_B, COLOR_B)
        arrow_c = create_force_arrow(PHASE_C, COLOR_C)

        def update_arrow(arrow):
            t = time_tracker.get_value()
            # Vector ROTATES with time (direction changes, magnitude constant)
            vec = get_rotating_force_vector(t, arrow.phase_offset, MAX_FORCE_LENGTH)
            arrow.put_start_and_end_on(gen_center, gen_center + vec)

        # ============================================================
        # TIP-TO-TAIL TRIANGLE (right side)
        # ============================================================
        triangle_center = np.array([3.5, 0, 0])

        # Create arrows for tip-to-tail demonstration
        triangle_arrow_a = Arrow(ORIGIN, ORIGIN, color=COLOR_A, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        triangle_arrow_b = Arrow(ORIGIN, ORIGIN, color=COLOR_B, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        triangle_arrow_c = Arrow(ORIGIN, ORIGIN, color=COLOR_C, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25)

        def update_triangle_arrows():
            """Update the tip-to-tail arrows to form a closed triangle (ROTATING)."""
            t = time_tracker.get_value()

            # Get ROTATING force vectors (equal magnitude, 120 degrees apart)
            vec_a = get_rotating_force_vector(t, PHASE_A, MAX_FORCE_LENGTH)
            vec_b = get_rotating_force_vector(t, PHASE_B, MAX_FORCE_LENGTH)
            vec_c = get_rotating_force_vector(t, PHASE_C, MAX_FORCE_LENGTH)

            # Tip-to-tail arrangement starting from triangle_center
            # These three vectors ALWAYS sum to zero, forming a closed triangle
            start_a = triangle_center
            end_a = start_a + vec_a

            start_b = end_a
            end_b = start_b + vec_b

            start_c = end_b
            end_c = start_c + vec_c  # This EXACTLY returns to start_a (net force = 0)

            # Update arrows
            triangle_arrow_a.put_start_and_end_on(start_a, end_a)
            triangle_arrow_b.put_start_and_end_on(start_b, end_b)
            triangle_arrow_c.put_start_and_end_on(start_c, end_c)

        def updater_triangle_a(mob):
            t = time_tracker.get_value()
            vec_a = get_rotating_force_vector(t, PHASE_A, MAX_FORCE_LENGTH)
            start_a = triangle_center
            end_a = start_a + vec_a
            mob.put_start_and_end_on(start_a, end_a)

        def updater_triangle_b(mob):
            t = time_tracker.get_value()
            vec_a = get_rotating_force_vector(t, PHASE_A, MAX_FORCE_LENGTH)
            vec_b = get_rotating_force_vector(t, PHASE_B, MAX_FORCE_LENGTH)
            start_b = triangle_center + vec_a
            end_b = start_b + vec_b
            mob.put_start_and_end_on(start_b, end_b)

        def updater_triangle_c(mob):
            t = time_tracker.get_value()
            vec_a = get_rotating_force_vector(t, PHASE_A, MAX_FORCE_LENGTH)
            vec_b = get_rotating_force_vector(t, PHASE_B, MAX_FORCE_LENGTH)
            vec_c = get_rotating_force_vector(t, PHASE_C, MAX_FORCE_LENGTH)
            start_c = triangle_center + vec_a + vec_b
            end_c = start_c + vec_c
            mob.put_start_and_end_on(start_c, end_c)

        # Net force indicator (should stay at origin of triangle)
        net_force_dot = Dot(triangle_center, color=YELLOW, radius=0.12)
        net_force_label = Text("Net Force = 0", font_size=24, color=YELLOW)
        net_force_label.next_to(net_force_dot, DOWN, buff=0.3)

        # Title for triangle section
        triangle_title = Text("Force Addition", font_size=28).move_to(triangle_center + UP * 2.5)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # 1. Show generator with coils
        self.play(Create(generator_circle), FadeIn(center_dot), run_time=1)
        self.play(
            Create(coil_a), Create(coil_b), Create(coil_c),
            FadeIn(label_a), FadeIn(label_b), FadeIn(label_c),
            run_time=1.5
        )
        self.wait(0.5)

        # 2. Draw force vectors from center
        self.play(
            GrowArrow(arrow_a),
            GrowArrow(arrow_b),
            GrowArrow(arrow_c),
            run_time=1
        )
        self.wait(0.5)

        # 3. Animate vectors pulsing (add updaters and run time)
        arrow_a.add_updater(update_arrow)
        arrow_b.add_updater(update_arrow)
        arrow_c.add_updater(update_arrow)

        # Show pulsing for 2 cycles
        self.play(
            time_tracker.animate.set_value(4 * PI / ROTATION_SPEED),
            run_time=4,
            rate_func=linear
        )
        self.wait(0.5)

        # 4. Show tip-to-tail addition on right side
        self.play(FadeIn(triangle_title), run_time=0.5)

        # Initialize triangle arrows at current time
        update_triangle_arrows()

        # Create copies of the force arrows to transform into triangle
        arrow_a_copy = arrow_a.copy()
        arrow_b_copy = arrow_b.copy()
        arrow_c_copy = arrow_c.copy()

        self.add(arrow_a_copy, arrow_b_copy, arrow_c_copy)

        # Transform to tip-to-tail position
        t_current = time_tracker.get_value()
        vec_a = get_rotating_force_vector(t_current, PHASE_A, MAX_FORCE_LENGTH)
        vec_b = get_rotating_force_vector(t_current, PHASE_B, MAX_FORCE_LENGTH)
        vec_c = get_rotating_force_vector(t_current, PHASE_C, MAX_FORCE_LENGTH)

        target_a = Arrow(triangle_center, triangle_center + vec_a, color=COLOR_A, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        target_b = Arrow(triangle_center + vec_a, triangle_center + vec_a + vec_b, color=COLOR_B, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        target_c = Arrow(triangle_center + vec_a + vec_b, triangle_center + vec_a + vec_b + vec_c, color=COLOR_C, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25)

        self.play(
            Transform(arrow_a_copy, target_a),
            Transform(arrow_b_copy, target_b),
            Transform(arrow_c_copy, target_c),
            run_time=1.5
        )

        # Remove copies and add the updater-based triangle arrows
        self.remove(arrow_a_copy, arrow_b_copy, arrow_c_copy)
        self.add(triangle_arrow_a, triangle_arrow_b, triangle_arrow_c)

        # Initialize positions
        update_triangle_arrows()

        # Add updaters to triangle arrows
        triangle_arrow_a.add_updater(updater_triangle_a)
        triangle_arrow_b.add_updater(updater_triangle_b)
        triangle_arrow_c.add_updater(updater_triangle_c)

        # 5. Show that triangle closes perfectly - net force = 0
        self.play(
            FadeIn(net_force_dot),
            FadeIn(net_force_label),
            run_time=0.5
        )

        # Let it run showing the closed triangle rotating
        self.play(
            time_tracker.animate.set_value(time_tracker.get_value() + 6 * PI / ROTATION_SPEED),
            run_time=6,
            rate_func=linear
        )

        self.wait(1)

        # ============================================================
        # OPTIONAL: 2-PHASE CONTRAST
        # ============================================================
        # Show that 2-phase does NOT close

        # Remove 3-phase elements
        triangle_arrow_a.remove_updater(updater_triangle_a)
        triangle_arrow_b.remove_updater(updater_triangle_b)
        triangle_arrow_c.remove_updater(updater_triangle_c)
        arrow_a.remove_updater(update_arrow)
        arrow_b.remove_updater(update_arrow)
        arrow_c.remove_updater(update_arrow)

        three_phase_group = VGroup(
            triangle_arrow_a, triangle_arrow_b, triangle_arrow_c,
            net_force_dot, net_force_label, triangle_title
        )

        # Fade out 3-phase and show 2-phase
        two_phase_title = Text("2-Phase: Forces DON'T Cancel", font_size=24, color=RED)
        two_phase_title.move_to(triangle_center + UP * 2.5)

        self.play(
            FadeOut(three_phase_group),
            FadeOut(coil_c), FadeOut(label_c), FadeOut(arrow_c),
            FadeIn(two_phase_title),
            run_time=1
        )

        # 2-phase: Two rotating vectors 90 degrees apart
        # Sum of two unit vectors at 90 degrees = sqrt(2) at 45 degrees between them
        # This creates a NET FORCE that rotates (not zero!)
        PHASE_B_2PHASE = PI / 2  # 90 degree offset

        # Move coil B to 3 o'clock position (visual indicator)
        new_b_pos = gen_center + np.array([GENERATOR_RADIUS, 0, 0])
        self.play(
            coil_b.animate.move_to(new_b_pos),
            label_b.animate.next_to(new_b_pos + np.array([COIL_RADIUS, 0, 0]), RIGHT, buff=0.1),
            run_time=1
        )

        # Update arrow_b phase for 2-phase (90 degrees offset instead of 120)
        arrow_b.phase_offset = PHASE_B_2PHASE

        # Create 2-phase triangle arrows
        two_phase_arrow_a = Arrow(ORIGIN, ORIGIN, color=COLOR_A, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25)
        two_phase_arrow_b = Arrow(ORIGIN, ORIGIN, color=COLOR_B, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.25)

        # Net force arrow (NON-ZERO for 2-phase - rotates with constant magnitude sqrt(2))
        net_force_arrow = Arrow(ORIGIN, ORIGIN, color=RED, buff=0, stroke_width=8, max_tip_length_to_length_ratio=0.3)

        def updater_2phase_a(mob):
            t = time_tracker.get_value()
            # Rotating vector A (phase 0)
            vec_a = get_rotating_force_vector(t, PHASE_A, MAX_FORCE_LENGTH)
            start_a = triangle_center
            end_a = start_a + vec_a
            mob.put_start_and_end_on(start_a, end_a)

        def updater_2phase_b(mob):
            t = time_tracker.get_value()
            # Rotating vectors for tip-to-tail
            vec_a = get_rotating_force_vector(t, PHASE_A, MAX_FORCE_LENGTH)
            vec_b = get_rotating_force_vector(t, PHASE_B_2PHASE, MAX_FORCE_LENGTH)
            start_b = triangle_center + vec_a
            end_b = start_b + vec_b
            mob.put_start_and_end_on(start_b, end_b)

        def updater_net_force(mob):
            t = time_tracker.get_value()
            # Sum of two rotating vectors 90 degrees apart = non-zero rotating vector
            vec_a = get_rotating_force_vector(t, PHASE_A, MAX_FORCE_LENGTH)
            vec_b = get_rotating_force_vector(t, PHASE_B_2PHASE, MAX_FORCE_LENGTH)
            net = vec_a + vec_b
            # Net force is NOT zero - it rotates with magnitude sqrt(2) * MAX_FORCE_LENGTH
            mob.put_start_and_end_on(triangle_center, triangle_center + net)

        def updater_arrow_a_2phase(mob):
            t = time_tracker.get_value()
            vec = get_rotating_force_vector(t, PHASE_A, MAX_FORCE_LENGTH)
            mob.put_start_and_end_on(gen_center, gen_center + vec)

        def updater_arrow_b_2phase(mob):
            t = time_tracker.get_value()
            vec = get_rotating_force_vector(t, PHASE_B_2PHASE, MAX_FORCE_LENGTH)
            mob.put_start_and_end_on(gen_center, gen_center + vec)

        # Add updaters
        two_phase_arrow_a.add_updater(updater_2phase_a)
        two_phase_arrow_b.add_updater(updater_2phase_b)
        net_force_arrow.add_updater(updater_net_force)
        arrow_a.add_updater(updater_arrow_a_2phase)
        arrow_b.add_updater(updater_arrow_b_2phase)

        # Initialize positions
        t_current = time_tracker.get_value()
        vec_a = get_rotating_force_vector(t_current, PHASE_A, MAX_FORCE_LENGTH)
        vec_b = get_rotating_force_vector(t_current, PHASE_B_2PHASE, MAX_FORCE_LENGTH)
        two_phase_arrow_a.put_start_and_end_on(triangle_center, triangle_center + vec_a)
        two_phase_arrow_b.put_start_and_end_on(triangle_center + vec_a, triangle_center + vec_a + vec_b)
        net_force_arrow.put_start_and_end_on(triangle_center, triangle_center + vec_a + vec_b)

        net_wobble_label = Text("Net Force ROTATES (not zero!)", font_size=20, color=RED)
        net_wobble_label.next_to(triangle_center, DOWN, buff=1.5)

        self.add(two_phase_arrow_a, two_phase_arrow_b, net_force_arrow)
        self.play(FadeIn(net_wobble_label), run_time=0.5)

        # Run 2-phase animation showing wobble
        self.play(
            time_tracker.animate.set_value(time_tracker.get_value() + 4 * PI / ROTATION_SPEED),
            run_time=4,
            rate_func=linear
        )

        self.wait(1)

        # Final message
        final_text = Text("3-Phase = Smooth Power, No Vibration", font_size=32, color=GREEN)
        final_text.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(final_text), run_time=1)
        self.wait(2)
