from manim import *
from generator import build_rotor
import math
import numpy as np


class ScalingRevealScene(Scene):
    """
    Visually demonstrates why scaling up magnets/coils preserves 3-phase.

    LAYOUT:
    - Generator on LEFT (about 40% of screen width)
    - Single voltage graph on RIGHT showing all 3 phases overlaid (blue, green, orange)

    ANIMATION SEQUENCE:
    1. Start with 4-magnet / 3-coil generator spinning with 3 sine waves
       - 2 electrical cycles per rotation (2 pole pairs)
       - Let it spin ~2 rotations
    2. "Double it" text appears
       - New magnets fade in at midpoints (4 -> 8)
       - New coils fade in between existing (3 -> 6)
       - Graph redraws with doubled cycles (4 per rotation)
    3. Reveal: "Same ratio. Same 3-phase." with "8/6 = 4/3"
       - Spin for another rotation or two

    TECHNICAL:
    - 4/3 config: 2 pole pairs = 2 electrical cycles per rotation
    - 8/6 config: 4 pole pairs = 4 electrical cycles per rotation
    - Phase colors: BLUE (A), GREEN (B), ORANGE (C)
    - Uses simple np.sin() with phase offsets (0, 2*PI/3, 4*PI/3)
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 2.2
        MAGNET_RADIUS_4 = 0.5   # For 4-magnet config
        MAGNET_RADIUS_8 = 0.35  # Smaller for 8-magnet config
        OFFSET_FROM_EDGE = 0.15
        MAGNET_PATH_RADIUS_4 = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS_4
        MAGNET_PATH_RADIUS_8 = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS_8

        # Phase colors
        PHASE_A_COLOR = BLUE
        PHASE_B_COLOR = GREEN
        PHASE_C_COLOR = ORANGE

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        ROTATION_SPEED = 0.4 * PI  # rad/s, clockwise (slower for clarity)
        # 2 rotations at 0.4*PI rad/s = 2 * 2*PI / (0.4*PI) = 10 seconds
        PHASE_1_TIME = 10.0  # ~2 rotations for 4-mag config
        PHASE_2_TIME = 10.0  # ~2 rotations for 8-mag config

        # ============================================================
        # HELPER: BUILD GENERATOR
        # ============================================================
        def build_generator(num_magnets, num_coils, magnet_radius, coil_colors):
            """Build generator with numbered coils following gold standard."""
            magnet_path_radius = DISK_RADIUS - OFFSET_FROM_EDGE - magnet_radius

            # Use build_rotor from generator.py
            rotor = build_rotor(num_magnets, magnet_path_radius, magnet_radius, DISK_RADIUS)

            # Stator ring outside magnets
            stator = Circle(
                radius=DISK_RADIUS + 0.25,
                color=GRAY,
                stroke_width=6,
                stroke_opacity=0.5
            )

            # Square coils at magnet path radius
            coils = VGroup()
            for i in range(num_coils):
                coil_angle = (PI / 2.0) - (i * (2 * PI / num_coils))
                coil_pos = np.array([
                    magnet_path_radius * math.cos(coil_angle),
                    magnet_path_radius * math.sin(coil_angle),
                    0
                ])

                coil = Rectangle(
                    width=magnet_radius * 2.0,
                    height=magnet_radius * 2.0,
                    color=coil_colors[i % len(coil_colors)],
                    stroke_width=5
                )
                coil.rotate(coil_angle - PI / 2)
                coil.move_to(coil_pos)
                coils.add(coil)

            return VGroup(stator, rotor, coils), rotor

        # ============================================================
        # BUILD INITIAL 4-MAGNET / 3-COIL GENERATOR
        # ============================================================
        # Phase pattern for 3 coils: A, C, B (electrical order)
        coil_colors_3 = [PHASE_A_COLOR, PHASE_C_COLOR, PHASE_B_COLOR]
        generator_4, rotor_4 = build_generator(4, 3, MAGNET_RADIUS_4, coil_colors_3)
        generator_4.scale(0.9).to_edge(LEFT, buff=0.8)
        rotor_4_center = rotor_4.get_center()

        # ============================================================
        # VOLTAGE GRAPH (RIGHT SIDE)
        # ============================================================
        # For 4-mag: 2 cycles per rotation, 2 rotations = 4 cycles shown
        # For 8-mag: 4 cycles per rotation, 2 rotations = 8 cycles shown
        # Use normalized time (0 to 1 = one rotation) for x-axis

        NUM_ROTATIONS = 2
        GRAPH_POINTS = 300

        voltage_ax = Axes(
            x_range=[0, NUM_ROTATIONS, 0.5],
            y_range=[-1.2, 1.2, 0.5],
            x_length=5.5,
            y_length=3.5,
            axis_config={"include_tip": False, "color": GREY},
        ).to_edge(RIGHT, buff=0.6)

        x_label = Text("Rotations", font_size=18, color=GREY)
        x_label.next_to(voltage_ax, DOWN, buff=0.1)

        graph_group = VGroup(voltage_ax, x_label)

        # ============================================================
        # CREATE VOLTAGE CURVES FOR 4-MAG CONFIG
        # ============================================================
        # 2 pole pairs = 2 electrical cycles per rotation
        # Phase offsets: A=0, B=2*PI/3, C=4*PI/3

        def create_phase_curves(pole_pairs, ax, colors):
            """Create 3 phase sine curves for given pole pair count."""
            curves = VGroup()
            phase_offsets = [0, 2 * PI / 3, 4 * PI / 3]  # A, B, C

            for i, (offset, color) in enumerate(zip(phase_offsets, colors)):
                points = []
                for j in range(GRAPH_POINTS + 1):
                    x = j / GRAPH_POINTS * NUM_ROTATIONS
                    # electrical angle = mechanical angle * pole_pairs
                    elec_angle = x * 2 * PI * pole_pairs
                    y = np.sin(elec_angle + offset)
                    points.append(ax.c2p(x, y))

                curve = VMobject().set_color(color).set_stroke(width=2.5)
                curve.set_points_as_corners(points)
                curves.add(curve)

            return curves

        curves_4 = create_phase_curves(2, voltage_ax, [PHASE_A_COLOR, PHASE_B_COLOR, PHASE_C_COLOR])

        # ============================================================
        # VALUE TRACKER FOR ROTATION
        # ============================================================
        rotation_tracker = ValueTracker(0)

        # Store last rotation value for delta calculation
        last_rotation = [0.0]

        def update_rotor_4(mob):
            current = rotation_tracker.get_value()
            delta = current - last_rotation[0]
            if delta != 0:
                mob.rotate(-delta * 2 * PI, about_point=rotor_4_center)
                last_rotation[0] = current

        rotor_4.add_updater(update_rotor_4)

        # ============================================================
        # ANIMATION PHASE 1: Show 4-mag / 3-coil spinning
        # ============================================================
        self.add(generator_4, graph_group, curves_4)
        self.wait(0.5)

        # Spin for ~2 rotations
        self.play(
            rotation_tracker.animate.set_value(NUM_ROTATIONS),
            run_time=PHASE_1_TIME,
            rate_func=linear
        )

        rotor_4.clear_updaters()
        self.wait(0.5)

        # ============================================================
        # TRANSFORMATION: 4 -> 8 magnets, 3 -> 6 coils
        # ============================================================

        # "Double it" text
        double_text = Text("Double it", font_size=36, weight=BOLD, color=YELLOW)
        double_text.to_edge(UP, buff=0.4)
        self.play(FadeIn(double_text), run_time=0.6)
        self.wait(0.5)

        # Build 8-magnet / 6-coil generator
        # Phase pattern for 6 coils: A, C, B, A, C, B
        coil_colors_6 = [PHASE_A_COLOR, PHASE_C_COLOR, PHASE_B_COLOR,
                         PHASE_A_COLOR, PHASE_C_COLOR, PHASE_B_COLOR]
        generator_8, rotor_8 = build_generator(8, 6, MAGNET_RADIUS_8, coil_colors_6)
        generator_8.scale(0.9).to_edge(LEFT, buff=0.8)
        rotor_8_center = rotor_8.get_center()

        # Create new curves for 8-mag config (4 pole pairs)
        curves_8 = create_phase_curves(4, voltage_ax, [PHASE_A_COLOR, PHASE_B_COLOR, PHASE_C_COLOR])

        # Transform generator and curves
        self.play(
            ReplacementTransform(generator_4, generator_8),
            ReplacementTransform(curves_4, curves_8),
            run_time=1.5
        )

        self.play(FadeOut(double_text), run_time=0.3)

        # ============================================================
        # ANIMATION PHASE 2: Spin 8-mag / 6-coil
        # ============================================================
        rotation_tracker.set_value(0)
        last_rotation[0] = 0.0

        def update_rotor_8(mob):
            current = rotation_tracker.get_value()
            delta = current - last_rotation[0]
            if delta != 0:
                mob.rotate(-delta * 2 * PI, about_point=rotor_8_center)
                last_rotation[0] = current

        rotor_8.add_updater(update_rotor_8)

        # Spin for ~2 rotations
        self.play(
            rotation_tracker.animate.set_value(NUM_ROTATIONS),
            run_time=PHASE_2_TIME,
            rate_func=linear
        )

        rotor_8.clear_updaters()

        # ============================================================
        # THE REVEAL
        # ============================================================
        self.wait(0.5)

        # Ratio equation
        ratio_eq = MathTex(r"\frac{8}{6} = \frac{4}{3}", font_size=42)
        ratio_eq.to_edge(UP, buff=0.4)

        reveal_text = Text("Same ratio. Same 3-phase.", font_size=24, color=YELLOW)
        reveal_text.next_to(ratio_eq, DOWN, buff=0.2)

        self.play(Write(ratio_eq), run_time=0.8)
        self.play(FadeIn(reveal_text), run_time=0.5)

        # One more spin to drive it home
        rotation_tracker.set_value(0)
        last_rotation[0] = 0.0
        rotor_8.add_updater(update_rotor_8)

        self.play(
            rotation_tracker.animate.set_value(1.0),
            run_time=5.0,
            rate_func=linear
        )

        rotor_8.clear_updaters()
        self.wait(1.5)


class ScalingMathScene(Scene):
    """
    Visualizes why 24/18 configuration maintains 3-phase separation.

    Key insight: 24/18 = 4/3 ratio means it's equivalent to 4 magnets / 3 coils,
    but with 6x more electrical cycles per mechanical rotation.

    Shows:
    1. The 24-magnet, 18-coil configuration
    2. The math: mechanical → electrical angle conversion
    3. Phase groupings (every 3rd coil = same phase)
    4. Comparison to simpler 4/3 configuration
    """

    def construct(self):
        # ============================================================
        # CONSTANTS
        # ============================================================
        DISK_RADIUS = 2.8
        MAGNET_RADIUS = 0.25  # Smaller magnets to fit 24
        OFFSET_FROM_EDGE = 0.15
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS

        NUM_MAGNETS = 24
        NUM_COILS = 18
        POLE_PAIRS = NUM_MAGNETS // 2  # 12

        COIL_RADIUS = 0.22  # Smaller coils to fit 18

        # Phase colors
        PHASE_A_COLOR = BLUE
        PHASE_B_COLOR = GREEN
        PHASE_C_COLOR = ORANGE

        # ============================================================
        # BUILD GENERATOR VISUAL
        # ============================================================

        # Disk
        disk = Circle(radius=DISK_RADIUS, color=WHITE, stroke_opacity=0.5, stroke_width=2)
        disk.set_fill(color=GREY, opacity=0.1)

        # Magnets (24 alternating N/S)
        magnets = VGroup()
        for i in range(NUM_MAGNETS):
            mag_angle = (PI / 2.0) - (i * (2 * PI / NUM_MAGNETS))
            x = MAGNET_PATH_RADIUS * math.cos(mag_angle)
            y = MAGNET_PATH_RADIUS * math.sin(mag_angle)

            is_north = i % 2 == 0
            color = RED if is_north else BLUE_E

            magnet = Circle(radius=MAGNET_RADIUS, color=color, fill_opacity=0.8)
            magnet.set_fill(color)
            magnet.move_to(np.array([x, y, 0]))

            # Smaller labels for dense config
            label_text = "N" if is_north else "S"
            label = Text(label_text, font_size=14, color=WHITE).move_to(magnet.get_center())

            magnets.add(VGroup(magnet, label))

        rotor = VGroup(disk, magnets)

        # Stator ring
        stator = Circle(
            radius=DISK_RADIUS + 0.25,
            color=GRAY,
            stroke_width=6,
            stroke_opacity=0.5
        )

        # Coils (18 total, colored by phase)
        # Phase assignment: coil i has electrical offset = i * 20° * 12 = i * 240°
        # Coil 0: 0° (Phase A)
        # Coil 1: 240° (Phase C)
        # Coil 2: 480° = 120° (Phase B)
        # Coil 3: 720° = 0° (Phase A)
        # Pattern: A, C, B, A, C, B, ...

        def get_phase_for_coil(coil_index):
            """Returns phase (0=A, 1=B, 2=C) for a given coil index."""
            mechanical_offset = coil_index * (360 / NUM_COILS)  # degrees
            electrical_offset = mechanical_offset * POLE_PAIRS
            electrical_offset = electrical_offset % 360

            # Map to phase: 0° = A, 120° = B, 240° = C
            if electrical_offset < 60 or electrical_offset >= 300:
                return 0  # Phase A (around 0°)
            elif 60 <= electrical_offset < 180:
                return 2  # Phase C (around 120° but we labeled it C for visual)
            else:
                return 1  # Phase B (around 240° but we labeled it B)

        # Actually let's be more precise based on the math:
        # Coil 0: 0° electrical → Phase A
        # Coil 1: 240° electrical → Phase C
        # Coil 2: 480° = 120° electrical → Phase B
        # So pattern is A, C, B repeating

        phase_colors = [PHASE_A_COLOR, PHASE_B_COLOR, PHASE_C_COLOR]
        phase_names = ["A", "B", "C"]
        phase_pattern = [0, 2, 1]  # A, C, B pattern

        coils = VGroup()
        coil_labels = VGroup()

        for i in range(NUM_COILS):
            coil_angle = (PI / 2.0) - (i * (2 * PI / NUM_COILS))

            # Position slightly outside magnet path
            coil_path_radius = MAGNET_PATH_RADIUS + MAGNET_RADIUS + COIL_RADIUS + 0.08
            x = coil_path_radius * math.cos(coil_angle)
            y = coil_path_radius * math.sin(coil_angle)

            phase_idx = phase_pattern[i % 3]
            color = phase_colors[phase_idx]

            coil = DashedVMobject(
                Circle(radius=COIL_RADIUS, color=color, stroke_width=4),
                num_dashes=8
            ).move_to(np.array([x, y, 0]))

            coils.add(coil)

        generator = VGroup(stator, rotor, coils)
        generator.scale(0.85)
        generator.to_edge(LEFT, buff=0.6)

        # ============================================================
        # MATH EXPLANATION (Right side)
        # ============================================================

        title = Text("24 Magnets / 18 Coils", font_size=36, weight=BOLD)
        title.to_edge(UP, buff=0.4).shift(RIGHT * 2)

        # Step-by-step math
        math_group = VGroup()

        step1 = VGroup(
            Text("Pole pairs:", font_size=24),
            MathTex(r"24 \div 2 = 12", font_size=32)
        ).arrange(RIGHT, buff=0.3)

        step2 = VGroup(
            Text("Coil spacing:", font_size=24),
            MathTex(r"360° \div 18 = 20°", font_size=32),
            Text("mechanical", font_size=20, color=GRAY)
        ).arrange(RIGHT, buff=0.3)

        step3_title = Text("Mechanical → Electrical:", font_size=24)

        step3a = MathTex(
            r"\text{Coil 1 → Coil 2: } 20° \times 12 = 240°",
            font_size=28
        )

        step3b = MathTex(
            r"\text{Coil 1 → Coil 3: } 40° \times 12 = 480° \rightarrow 120°",
            font_size=28
        )

        step4 = VGroup(
            Text("Electrical phases:", font_size=24),
            MathTex(r"0°, 240°, 120° \rightarrow 0°, 120°, 240°", font_size=28, color=YELLOW)
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)

        math_group = VGroup(step1, step2, step3_title, step3a, step3b, step4)
        math_group.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        math_group.next_to(title, DOWN, buff=0.5)
        math_group.shift(RIGHT * 1.5)

        # ============================================================
        # KEY INSIGHT BOX
        # ============================================================

        insight_box = RoundedRectangle(
            width=6.5, height=2.2,
            corner_radius=0.2,
            color=YELLOW,
            stroke_width=2
        )

        insight_text = VGroup(
            Text("Key Insight", font_size=24, weight=BOLD, color=YELLOW),
            Text("12 pole pairs = 12 electrical cycles", font_size=22),
            Text("per mechanical rotation", font_size=22),
            Text("", font_size=10),  # spacer
            Text("It's like 12 copies of a simple", font_size=20, color=GRAY),
            Text("4-magnet / 3-coil generator!", font_size=20, color=GRAY),
        ).arrange(DOWN, buff=0.12)

        insight_group = VGroup(insight_box, insight_text)
        insight_text.move_to(insight_box.get_center())
        insight_group.to_edge(DOWN, buff=0.4).shift(RIGHT * 2)

        # ============================================================
        # PHASE LEGEND
        # ============================================================

        legend = VGroup(
            VGroup(
                Circle(radius=0.12, color=PHASE_A_COLOR, fill_opacity=0.8).set_fill(PHASE_A_COLOR),
                Text("Phase A (6 coils)", font_size=18, color=PHASE_A_COLOR)
            ).arrange(RIGHT, buff=0.15),
            VGroup(
                Circle(radius=0.12, color=PHASE_B_COLOR, fill_opacity=0.8).set_fill(PHASE_B_COLOR),
                Text("Phase B (6 coils)", font_size=18, color=PHASE_B_COLOR)
            ).arrange(RIGHT, buff=0.15),
            VGroup(
                Circle(radius=0.12, color=PHASE_C_COLOR, fill_opacity=0.8).set_fill(PHASE_C_COLOR),
                Text("Phase C (6 coils)", font_size=18, color=PHASE_C_COLOR)
            ).arrange(RIGHT, buff=0.15),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        legend.next_to(generator, DOWN, buff=0.3)

        # ============================================================
        # RATIO COMPARISON
        # ============================================================

        ratio_text = MathTex(
            r"\frac{24}{18} = \frac{12}{9} = \frac{4}{3}",
            font_size=36
        )
        ratio_label = Text("Same ratio, same 3-phase magic", font_size=20, color=GRAY)
        ratio_group = VGroup(ratio_text, ratio_label).arrange(DOWN, buff=0.1)
        ratio_group.next_to(insight_group, UP, buff=0.4)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # 1. Fade in generator
        self.play(FadeIn(generator), FadeIn(legend), run_time=1.5)
        self.wait(0.5)

        # 2. Title
        self.play(Write(title), run_time=0.8)
        self.wait(0.5)

        # 3. Math steps one by one
        self.play(FadeIn(step1), run_time=0.6)
        self.wait(0.8)

        self.play(FadeIn(step2), run_time=0.6)
        self.wait(0.8)

        self.play(FadeIn(step3_title), run_time=0.4)
        self.play(FadeIn(step3a), run_time=0.6)
        self.wait(0.5)
        self.play(FadeIn(step3b), run_time=0.6)
        self.wait(0.8)

        # 4. Result with highlight
        self.play(FadeIn(step4), run_time=0.8)
        self.wait(1)

        # 5. Highlight phase groups on generator
        # Flash each phase group
        phase_a_coils = VGroup(*[coils[i] for i in range(NUM_COILS) if phase_pattern[i % 3] == 0])
        phase_b_coils = VGroup(*[coils[i] for i in range(NUM_COILS) if phase_pattern[i % 3] == 1])
        phase_c_coils = VGroup(*[coils[i] for i in range(NUM_COILS) if phase_pattern[i % 3] == 2])

        self.play(
            phase_a_coils.animate.set_stroke(width=8),
            run_time=0.5
        )
        self.play(
            phase_a_coils.animate.set_stroke(width=4),
            run_time=0.3
        )

        self.play(
            phase_b_coils.animate.set_stroke(width=8),
            run_time=0.5
        )
        self.play(
            phase_b_coils.animate.set_stroke(width=4),
            run_time=0.3
        )

        self.play(
            phase_c_coils.animate.set_stroke(width=8),
            run_time=0.5
        )
        self.play(
            phase_c_coils.animate.set_stroke(width=4),
            run_time=0.3
        )

        self.wait(0.5)

        # 6. Show ratio comparison
        self.play(FadeIn(ratio_group), run_time=0.8)
        self.wait(1)

        # 7. Key insight box
        self.play(
            FadeIn(insight_box),
            FadeIn(insight_text),
            run_time=1
        )
        self.wait(2)

        # 8. Slow rotation to show it works
        self.play(
            Rotate(rotor, angle=-PI/6, about_point=rotor.get_center()),
            run_time=2,
            rate_func=smooth
        )

        self.wait(2)


class PolesVsSpeedScene(Scene):
    """
    CONCEPT: Show that adding more magnets is electrically equivalent to spinning faster.
    One rotation with many poles produces the same electrical output as multiple rotations
    with few poles.

    VISUAL LAYOUT:
    - LEFT: Simple 4-magnet generator (2 pole pairs) with voltage graph below it
    - RIGHT: Dense 24-magnet generator (12 pole pairs) with voltage graph below it
    - Both generators same physical size

    ANIMATION SEQUENCE:
    1. Setup: Show both generators side by side with their voltage graphs (empty axes)
    2. The Comparison: Spin DENSE generator 1 rotation (~3 seconds), draws 12 cycles
       - Counter shows "1 rotation"
    3. The Equivalence: Spin SPARSE generator until it produces same 12 cycles
       - Requires 6 full rotations (2 pole pairs x 6 = 12 cycles)
       - Counter counts up: "1... 2... 3... 4... 5... 6 rotations"
    4. The Reveal: Show equation "1 rotation x 12 poles = 6 rotations x 2 poles"
       - Key insight: "More poles = electrical 'gearing' without mechanical speed"

    COLORS:
    - Magnets: RED (N) / BLUE_E (S)
    - Voltage trace: YELLOW for both
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 1.6  # Smaller to fit both generators
        SPARSE_MAGNET_RADIUS = 0.35
        DENSE_MAGNET_RADIUS = 0.12

        NUM_SPARSE_MAGNETS = 4  # 2 pole pairs
        NUM_DENSE_MAGNETS = 24  # 12 pole pairs

        SPARSE_POLE_PAIRS = NUM_SPARSE_MAGNETS // 2  # 2
        DENSE_POLE_PAIRS = NUM_DENSE_MAGNETS // 2    # 12

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        # Dense generator: 1 rotation in ~3 seconds
        DENSE_ROTATION_TIME = 3.0
        DENSE_ROTATION_SPEED = 2 * PI / DENSE_ROTATION_TIME  # rad/s

        # Sparse generator: 6 rotations to match 12 cycles
        SPARSE_ROTATIONS_NEEDED = DENSE_POLE_PAIRS // SPARSE_POLE_PAIRS  # 6
        SPARSE_ROTATION_TIME = DENSE_ROTATION_TIME * SPARSE_ROTATIONS_NEEDED  # 18 seconds total

        # For voltage calculation, we want 12 cycles on each graph
        # Dense: 12 cycles from 1 rotation
        # Sparse: 12 cycles from 6 rotations (2 cycles per rotation)

        # ============================================================
        # BUILD SPARSE GENERATOR (LEFT)
        # ============================================================
        sparse_path_radius = DISK_RADIUS - 0.15 - SPARSE_MAGNET_RADIUS

        sparse_disk = Circle(radius=DISK_RADIUS, color=WHITE, stroke_opacity=0.5, stroke_width=2)
        sparse_disk.set_fill(color=GREY, opacity=0.1)

        sparse_magnets = VGroup()
        for i in range(NUM_SPARSE_MAGNETS):
            mag_angle = (PI / 2.0) - (i * (2 * PI / NUM_SPARSE_MAGNETS))
            x = sparse_path_radius * math.cos(mag_angle)
            y = sparse_path_radius * math.sin(mag_angle)

            is_north = i % 2 == 0
            color = RED if is_north else BLUE_E

            magnet = Circle(radius=SPARSE_MAGNET_RADIUS, color=color, fill_opacity=0.8)
            magnet.set_fill(color)
            magnet.move_to(np.array([x, y, 0]))

            label = Text("N" if is_north else "S", font_size=20, color=WHITE).move_to(magnet.get_center())
            sparse_magnets.add(VGroup(magnet, label))

        sparse_rotor = VGroup(sparse_disk, sparse_magnets)

        sparse_stator = Circle(radius=DISK_RADIUS + 0.15, color=GRAY, stroke_width=4, stroke_opacity=0.5)

        sparse_generator = VGroup(sparse_stator, sparse_rotor)
        sparse_generator_center = sparse_generator.get_center()

        # ============================================================
        # BUILD DENSE GENERATOR (RIGHT)
        # ============================================================
        dense_path_radius = DISK_RADIUS - 0.08 - DENSE_MAGNET_RADIUS

        dense_disk = Circle(radius=DISK_RADIUS, color=WHITE, stroke_opacity=0.5, stroke_width=2)
        dense_disk.set_fill(color=GREY, opacity=0.1)

        dense_magnets = VGroup()
        for i in range(NUM_DENSE_MAGNETS):
            mag_angle = (PI / 2.0) - (i * (2 * PI / NUM_DENSE_MAGNETS))
            x = dense_path_radius * math.cos(mag_angle)
            y = dense_path_radius * math.sin(mag_angle)

            is_north = i % 2 == 0
            color = RED if is_north else BLUE_E

            magnet = Circle(radius=DENSE_MAGNET_RADIUS, color=color, fill_opacity=0.8)
            magnet.set_fill(color)
            magnet.move_to(np.array([x, y, 0]))
            dense_magnets.add(magnet)

        dense_rotor = VGroup(dense_disk, dense_magnets)

        dense_stator = Circle(radius=DISK_RADIUS + 0.15, color=GRAY, stroke_width=4, stroke_opacity=0.5)

        dense_generator = VGroup(dense_stator, dense_rotor)
        dense_generator_center = dense_generator.get_center()

        # ============================================================
        # POSITION GENERATORS
        # ============================================================
        sparse_generator.shift(LEFT * 4.5 + UP * 1.5)
        dense_generator.shift(RIGHT * 4.5 + UP * 1.5)

        sparse_rotor_center = sparse_rotor.get_center()
        dense_rotor_center = dense_rotor.get_center()

        # ============================================================
        # LABELS FOR GENERATORS
        # ============================================================
        sparse_label = VGroup(
            Text("4 magnets", font_size=20, weight=BOLD),
            Text("2 pole pairs", font_size=16, color=GRAY),
        ).arrange(DOWN, buff=0.05)
        sparse_label.next_to(sparse_generator, UP, buff=0.2)

        dense_label = VGroup(
            Text("24 magnets", font_size=20, weight=BOLD),
            Text("12 pole pairs", font_size=16, color=GRAY),
        ).arrange(DOWN, buff=0.05)
        dense_label.next_to(dense_generator, UP, buff=0.2)

        # ============================================================
        # VOLTAGE GRAPHS
        # ============================================================
        # Both graphs show 12 complete cycles when done
        # X-axis is normalized to show "cycles" (0 to 12)
        NUM_CYCLES = 12

        graph_width = 2.8
        graph_height = 1.8

        # Sparse graph (below left generator)
        sparse_ax = Axes(
            x_range=[0, NUM_CYCLES, 2],
            y_range=[-1.2, 1.2, 0.5],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )
        sparse_ax.next_to(sparse_generator, DOWN, buff=0.5)

        sparse_graph_label = Text("Voltage", font_size=16, color=GRAY)
        sparse_graph_label.next_to(sparse_ax, LEFT, buff=0.15).rotate(90 * DEGREES)

        # Dense graph (below right generator)
        dense_ax = Axes(
            x_range=[0, NUM_CYCLES, 2],
            y_range=[-1.2, 1.2, 0.5],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )
        dense_ax.next_to(dense_generator, DOWN, buff=0.5)

        dense_graph_label = Text("Voltage", font_size=16, color=GRAY)
        dense_graph_label.next_to(dense_ax, LEFT, buff=0.15).rotate(90 * DEGREES)

        # ============================================================
        # ROTATION COUNTERS
        # ============================================================
        sparse_counter = VGroup(
            Text("Rotations:", font_size=18),
            Text("0", font_size=24, color=YELLOW)
        ).arrange(RIGHT, buff=0.15)
        sparse_counter.next_to(sparse_ax, DOWN, buff=0.25)

        dense_counter = VGroup(
            Text("Rotations:", font_size=18),
            Text("0", font_size=24, color=YELLOW)
        ).arrange(RIGHT, buff=0.15)
        dense_counter.next_to(dense_ax, DOWN, buff=0.25)

        # ============================================================
        # VALUE TRACKERS
        # ============================================================
        dense_rotation_tracker = ValueTracker(0)  # tracks rotations (0 to 1)
        sparse_rotation_tracker = ValueTracker(0)  # tracks rotations (0 to 6)

        # ============================================================
        # VOLTAGE CURVES
        # ============================================================
        sparse_curve = VMobject().set_color(YELLOW).set_stroke(width=2)
        dense_curve = VMobject().set_color(YELLOW).set_stroke(width=2)

        def update_sparse_curve(mob):
            rotations = sparse_rotation_tracker.get_value()
            cycles = rotations * SPARSE_POLE_PAIRS  # 2 cycles per rotation

            if cycles <= 0:
                return

            # Generate sine wave points
            num_points = max(2, int(cycles * 50))
            points = []
            for i in range(num_points + 1):
                x = (i / num_points) * cycles
                y = math.sin(2 * PI * x / 1.0)  # 1 cycle = 1 unit on x-axis
                points.append(sparse_ax.c2p(x, y))

            if len(points) > 1:
                mob.set_points_as_corners(points)

        def update_dense_curve(mob):
            rotations = dense_rotation_tracker.get_value()
            cycles = rotations * DENSE_POLE_PAIRS  # 12 cycles per rotation

            if cycles <= 0:
                return

            # Generate sine wave points
            num_points = max(2, int(cycles * 50))
            points = []
            for i in range(num_points + 1):
                x = (i / num_points) * cycles
                y = math.sin(2 * PI * x / 1.0)  # 1 cycle = 1 unit on x-axis
                points.append(dense_ax.c2p(x, y))

            if len(points) > 1:
                mob.set_points_as_corners(points)

        sparse_curve.add_updater(update_sparse_curve)
        dense_curve.add_updater(update_dense_curve)

        # ============================================================
        # ROTOR UPDATERS
        # ============================================================
        sparse_last_rotation = [0.0]
        dense_last_rotation = [0.0]

        def update_sparse_rotor(mob):
            current = sparse_rotation_tracker.get_value()
            delta = current - sparse_last_rotation[0]
            if delta != 0:
                mob.rotate(-delta * 2 * PI, about_point=sparse_rotor_center)
                sparse_last_rotation[0] = current

        def update_dense_rotor(mob):
            current = dense_rotation_tracker.get_value()
            delta = current - dense_last_rotation[0]
            if delta != 0:
                mob.rotate(-delta * 2 * PI, about_point=dense_rotor_center)
                dense_last_rotation[0] = current

        sparse_rotor.add_updater(update_sparse_rotor)
        dense_rotor.add_updater(update_dense_rotor)

        # ============================================================
        # COUNTER UPDATERS
        # ============================================================
        def update_sparse_counter(mob):
            rotations = sparse_rotation_tracker.get_value()
            new_text = Text(f"{int(rotations)}", font_size=24, color=YELLOW)
            new_text.move_to(mob[1].get_center())
            mob[1].become(new_text)

        def update_dense_counter(mob):
            rotations = dense_rotation_tracker.get_value()
            new_text = Text(f"{int(rotations)}", font_size=24, color=YELLOW)
            new_text.move_to(mob[1].get_center())
            mob[1].become(new_text)

        sparse_counter.add_updater(update_sparse_counter)
        dense_counter.add_updater(update_dense_counter)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # 1. Setup - show both generators with empty graphs
        self.add(
            sparse_generator, sparse_label, sparse_ax, sparse_graph_label, sparse_counter,
            dense_generator, dense_label, dense_ax, dense_graph_label, dense_counter,
            sparse_curve, dense_curve
        )
        self.wait(1)

        # 2. The Comparison - spin DENSE generator 1 rotation
        comparison_title = Text("1 Rotation Comparison", font_size=28, weight=BOLD)
        comparison_title.to_edge(UP, buff=0.3)
        self.play(FadeIn(comparison_title), run_time=0.5)

        # Animate dense generator: 1 rotation, produces 12 cycles
        self.play(
            dense_rotation_tracker.animate.set_value(1),
            run_time=DENSE_ROTATION_TIME,
            rate_func=linear
        )

        # Update counter to show "1"
        dense_counter[1].become(Text("1", font_size=24, color=YELLOW).move_to(dense_counter[1].get_center()))
        self.wait(0.5)

        # 3. The Equivalence - spin SPARSE generator until 12 cycles
        equivalence_text = Text("How many rotations for the same output?", font_size=22, color=GRAY)
        equivalence_text.next_to(comparison_title, DOWN, buff=0.2)
        self.play(FadeIn(equivalence_text), run_time=0.5)

        # Animate sparse generator: 6 rotations to produce 12 cycles
        # Speed it up a bit so it doesn't take forever (3x faster = 6 seconds)
        self.play(
            sparse_rotation_tracker.animate.set_value(6),
            run_time=6.0,  # Faster animation
            rate_func=linear
        )

        # Final counter update
        sparse_counter[1].become(Text("6", font_size=24, color=YELLOW).move_to(sparse_counter[1].get_center()))
        self.wait(0.5)

        # Remove updaters to freeze
        sparse_rotor.clear_updaters()
        dense_rotor.clear_updaters()
        sparse_curve.clear_updaters()
        dense_curve.clear_updaters()
        sparse_counter.clear_updaters()
        dense_counter.clear_updaters()

        # 4. The Reveal - show equation
        self.play(FadeOut(equivalence_text), run_time=0.3)

        equation = MathTex(
            r"1 \text{ rotation} \times 12 \text{ poles} = 6 \text{ rotations} \times 2 \text{ poles}",
            font_size=32
        )
        equation.next_to(comparison_title, DOWN, buff=0.25)

        insight = Text(
            "More poles = electrical 'gearing' without mechanical speed",
            font_size=22,
            color=YELLOW
        )
        insight.to_edge(DOWN, buff=0.3)

        self.play(Write(equation), run_time=1.5)
        self.wait(0.5)

        self.play(FadeIn(insight), run_time=0.8)
        self.wait(2)


class ScalingComparisonScene(Scene):
    """
    Side-by-side comparison of 4/3 vs 24/18 configurations.
    Shows that 24/18 produces 6x more electrical cycles per rotation.
    """

    def construct(self):
        # ============================================================
        # TITLE
        # ============================================================
        title = Text("Same Ratio, Different Density", font_size=36, weight=BOLD)
        title.to_edge(UP, buff=0.4)

        # ============================================================
        # LEFT: Simple 4/3 configuration
        # ============================================================
        DISK_RADIUS_SMALL = 1.8
        MAGNET_RADIUS_SMALL = 0.4
        MAGNET_PATH_RADIUS_SMALL = DISK_RADIUS_SMALL - 0.15 - MAGNET_RADIUS_SMALL

        # Build simple 4-magnet rotor
        disk_simple = Circle(radius=DISK_RADIUS_SMALL, color=WHITE, stroke_opacity=0.5, stroke_width=2)
        disk_simple.set_fill(color=GREY, opacity=0.1)

        magnets_simple = VGroup()
        for i in range(4):
            mag_angle = (PI / 2.0) - (i * (2 * PI / 4))
            x = MAGNET_PATH_RADIUS_SMALL * math.cos(mag_angle)
            y = MAGNET_PATH_RADIUS_SMALL * math.sin(mag_angle)

            is_north = i % 2 == 0
            color = RED if is_north else BLUE_E

            magnet = Circle(radius=MAGNET_RADIUS_SMALL, color=color, fill_opacity=0.8)
            magnet.set_fill(color)
            magnet.move_to(np.array([x, y, 0]))

            label = Text("N" if is_north else "S", font_size=24, color=WHITE).move_to(magnet.get_center())
            magnets_simple.add(VGroup(magnet, label))

        rotor_simple = VGroup(disk_simple, magnets_simple)

        # 3 coils for simple config
        phase_colors = [BLUE, GREEN, ORANGE]
        coils_simple = VGroup()
        for i in range(3):
            coil_angle = (PI / 2.0) - (i * (2 * PI / 3))
            coil_path_radius = MAGNET_PATH_RADIUS_SMALL + MAGNET_RADIUS_SMALL + 0.35
            x = coil_path_radius * math.cos(coil_angle)
            y = coil_path_radius * math.sin(coil_angle)

            coil = DashedVMobject(
                Circle(radius=0.3, color=phase_colors[i], stroke_width=5),
                num_dashes=10
            ).move_to(np.array([x, y, 0]))
            coils_simple.add(coil)

        stator_simple = Circle(radius=DISK_RADIUS_SMALL + 0.2, color=GRAY, stroke_width=4, stroke_opacity=0.5)

        generator_simple = VGroup(stator_simple, rotor_simple, coils_simple)

        label_simple = VGroup(
            Text("4 magnets / 3 coils", font_size=22, weight=BOLD),
            Text("2 pole pairs", font_size=18, color=GRAY),
            Text("1 electrical cycle / rotation", font_size=18, color=YELLOW),
        ).arrange(DOWN, buff=0.1)

        simple_group = VGroup(generator_simple, label_simple).arrange(DOWN, buff=0.4)
        simple_group.to_edge(LEFT, buff=1.0).shift(DOWN * 0.3)

        # ============================================================
        # RIGHT: Dense 24/18 configuration
        # ============================================================
        DISK_RADIUS_DENSE = 1.8
        MAGNET_RADIUS_DENSE = 0.12
        MAGNET_PATH_RADIUS_DENSE = DISK_RADIUS_DENSE - 0.1 - MAGNET_RADIUS_DENSE

        disk_dense = Circle(radius=DISK_RADIUS_DENSE, color=WHITE, stroke_opacity=0.5, stroke_width=2)
        disk_dense.set_fill(color=GREY, opacity=0.1)

        magnets_dense = VGroup()
        for i in range(24):
            mag_angle = (PI / 2.0) - (i * (2 * PI / 24))
            x = MAGNET_PATH_RADIUS_DENSE * math.cos(mag_angle)
            y = MAGNET_PATH_RADIUS_DENSE * math.sin(mag_angle)

            is_north = i % 2 == 0
            color = RED if is_north else BLUE_E

            magnet = Circle(radius=MAGNET_RADIUS_DENSE, color=color, fill_opacity=0.8)
            magnet.set_fill(color)
            magnet.move_to(np.array([x, y, 0]))
            magnets_dense.add(magnet)

        rotor_dense = VGroup(disk_dense, magnets_dense)

        # 18 coils
        phase_pattern = [0, 2, 1]  # A, C, B
        coils_dense = VGroup()
        for i in range(18):
            coil_angle = (PI / 2.0) - (i * (2 * PI / 18))
            coil_path_radius = MAGNET_PATH_RADIUS_DENSE + MAGNET_RADIUS_DENSE + 0.18
            x = coil_path_radius * math.cos(coil_angle)
            y = coil_path_radius * math.sin(coil_angle)

            phase_idx = phase_pattern[i % 3]
            color = phase_colors[phase_idx]

            coil = DashedVMobject(
                Circle(radius=0.1, color=color, stroke_width=3),
                num_dashes=6
            ).move_to(np.array([x, y, 0]))
            coils_dense.add(coil)

        stator_dense = Circle(radius=DISK_RADIUS_DENSE + 0.15, color=GRAY, stroke_width=4, stroke_opacity=0.5)

        generator_dense = VGroup(stator_dense, rotor_dense, coils_dense)

        label_dense = VGroup(
            Text("24 magnets / 18 coils", font_size=22, weight=BOLD),
            Text("12 pole pairs", font_size=18, color=GRAY),
            Text("12 electrical cycles / rotation", font_size=18, color=YELLOW),
        ).arrange(DOWN, buff=0.1)

        dense_group = VGroup(generator_dense, label_dense).arrange(DOWN, buff=0.4)
        dense_group.to_edge(RIGHT, buff=1.0).shift(DOWN * 0.3)

        # ============================================================
        # CENTER: Equals sign and ratio
        # ============================================================
        equals = MathTex(r"=", font_size=72)
        equals.move_to(ORIGIN).shift(DOWN * 0.3)

        ratio_eq = MathTex(r"\frac{4}{3} = \frac{24}{18}", font_size=32)
        ratio_eq.next_to(equals, UP, buff=0.3)

        # ============================================================
        # BOTTOM: Key message
        # ============================================================
        message = Text(
            "Same 3-phase geometry, 6× more power density",
            font_size=24,
            color=YELLOW
        )
        message.to_edge(DOWN, buff=0.5)

        # ============================================================
        # ANIMATION
        # ============================================================

        self.play(Write(title), run_time=0.8)
        self.wait(0.3)

        # Show simple config
        self.play(FadeIn(simple_group), run_time=1)
        self.wait(0.5)

        # Show dense config
        self.play(FadeIn(dense_group), run_time=1)
        self.wait(0.5)

        # Show equals
        self.play(
            Write(equals),
            Write(ratio_eq),
            run_time=0.8
        )
        self.wait(0.5)

        # Rotate both at same mechanical speed
        self.play(
            Rotate(rotor_simple, angle=-2*PI, about_point=rotor_simple.get_center()),
            Rotate(rotor_dense, angle=-2*PI, about_point=rotor_dense.get_center()),
            run_time=4,
            rate_func=linear
        )

        # Show message
        self.play(FadeIn(message), run_time=0.8)

        self.wait(2)


class SeriesConnectionScene(Scene):
    """
    CONCEPT: Show how scaling from 4mag/3coil to 8mag/6coil creates phase-twin coils
    that can be wired in series to double voltage.

    VISUAL LAYOUT:
    - LEFT: Generator (scaled 0.8, with numbered coils 1-6) using classic layout
    - RIGHT: Voltage graphs in 2x3 grid:
        Row 1: Coil 1 | Coil 2 | Coil 3
        Row 2: Coil 4 | Coil 5 | Coil 6
      Phase twins are grouped vertically (1 above 4, 2 above 5, 3 above 6)
    - Final merged 3-phase graphs also on right side

    Generator takes ~40% left, graphs take ~60% right (classic generator viz layout).

    ANIMATION SEQUENCE:
    1. Start Simple: 4-magnet/3-coil generator with 3 voltage graphs (A, B, C)
    2. Scale Up: Transform to 8-magnet/6-coil generator
    3. Show 6 Individual Graphs in 2x3 grid
    4. Highlight Phase Twins
    5. ANIMATED MERGE: Graphs slide together (1+4, 2+5, 3+6) before combining
    6. Final Reveal: 3 merged Phase graphs with "Same 3-phase, 2x voltage!"

    TECHNICAL DETAILS:
    - 8 magnets = 4 pole pairs
    - 6 coils at 60 deg mechanical spacing
    - Phase twins: 1&4 (A/BLUE), 2&5 (C/ORANGE), 3&6 (B/GREEN)

    COLORS:
    - Phase A (coils 1,4): BLUE
    - Phase B (coils 3,6): GREEN
    - Phase C (coils 2,5): ORANGE
    """

    def construct(self):
        from generator import calculate_sine_voltage_trace

        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 2.0  # Slightly smaller for better layout
        OFFSET_FROM_EDGE = 0.12

        # Phase colors
        PHASE_A_COLOR = BLUE      # Coils 1, 4
        PHASE_B_COLOR = GREEN     # Coils 3, 6
        PHASE_C_COLOR = ORANGE    # Coils 2, 5

        # ============================================================
        # TIME PARAMETERS (REDUCED for less clutter)
        # ============================================================
        ROTATION_SPEED = 0.5 * PI  # rad/s, clockwise
        QUICK_SPIN_TIME = 3.0  # Reduced from 4.0
        FULL_SPIN_TIME = 3.0   # Reduced from 6.0 - fewer cycles = cleaner graphs
        PHYSICS_STEPS = 2000   # Reduced for faster calculation

        # ============================================================
        # HELPER: BUILD GENERATOR WITH NUMBERED COILS (GOLD STANDARD)
        # ============================================================
        def build_generator_with_numbers(num_magnets, num_coils, coil_colors, coil_labels=None):
            """
            Build a generator following the gold standard pattern from
            scene_single_coil_4mag.py and scene_phase_shift_final.py.

            Key pattern:
            - Use build_rotor() from generator.py for magnets
            - Square coils using Rectangle, sized to match magnet diameter
            - Coils positioned at MAGNET_PATH_RADIUS (same radius as magnets)
            - Coils rotated to be tangent to circle
            - Stator ring OUTSIDE the magnets

            Args:
                num_magnets: Number of magnets (alternating N/S)
                num_coils: Number of coils
                coil_colors: List of colors for each coil
                coil_labels: Optional list of label strings for each coil (defaults to "1", "2", ...)

            Returns:
                (generator_group, rotor_group) tuple
            """
            if coil_labels is None:
                coil_labels = [str(i + 1) for i in range(num_coils)]
            # Scale magnet size based on count
            if num_magnets <= 4:
                magnet_radius = 0.5
                label_font_size = 24
            else:
                magnet_radius = 0.35  # Smaller to fit more magnets
                label_font_size = 18

            magnet_path_radius = DISK_RADIUS - OFFSET_FROM_EDGE - magnet_radius

            # Use build_rotor() from generator.py (gold standard)
            rotor = build_rotor(num_magnets, magnet_path_radius, magnet_radius, DISK_RADIUS)

            # Stator ring OUTSIDE the magnets (gold standard)
            stator = Circle(
                radius=DISK_RADIUS + 0.3,
                color=GRAY,
                stroke_width=8,
                stroke_opacity=0.5
            )

            # Square coils at MAGNET_PATH_RADIUS (same radius as magnets)
            # Sized to match magnet diameter (gold standard)
            coils = VGroup()
            coil_number_labels = VGroup()

            for i in range(num_coils):
                coil_angle = (PI / 2.0) - (i * (2 * PI / num_coils))

                # Position at MAGNET_PATH_RADIUS (same as magnets)
                coil_pos = np.array([
                    magnet_path_radius * math.cos(coil_angle),
                    magnet_path_radius * math.sin(coil_angle),
                    0
                ])

                # Square coil matching magnet diameter (gold standard)
                coil = Rectangle(
                    width=magnet_radius * 2.0,  # Match magnet diameter
                    height=magnet_radius * 2.0,  # Match magnet diameter
                    color=coil_colors[i],
                    stroke_width=6
                )
                # Rotate to be tangent to circle (gold standard)
                coil.rotate(coil_angle - PI / 2)
                coil.move_to(coil_pos)
                coils.add(coil)

                # Add label centered on each coil
                num_label = Text(coil_labels[i], font_size=18, color=WHITE, weight=BOLD)
                num_label.move_to(coil.get_center())
                coil_number_labels.add(num_label)

            return VGroup(stator, rotor, coils, coil_number_labels), rotor

        # ============================================================
        # PHASE 1: BUILD 4-MAGNET / 3-COIL GENERATOR
        # ============================================================
        coil_colors_3 = [PHASE_A_COLOR, PHASE_C_COLOR, PHASE_B_COLOR]
        coil_labels_3 = ["1", "2", "3"]  # Numbers for initial 4-mag/3-coil config
        generator_4, rotor_4 = build_generator_with_numbers(4, 3, coil_colors_3, coil_labels_3)
        generator_4.scale(0.8).to_edge(LEFT, buff=0.8)

        label_4 = Text("4 magnets / 3 coils", font_size=22, weight=BOLD)
        label_4.next_to(generator_4, DOWN, buff=0.2)

        # ============================================================
        # 3 VOLTAGE GRAPHS FOR 4-MAG CONFIG
        # ============================================================
        NUM_MAGNETS_4 = 4

        def get_coil_angle_static(mechanical_offset):
            angle = (PI / 2.0) - mechanical_offset
            def coil_func(t):
                return angle
            return coil_func

        coil_offsets_3 = [0, 120 * DEGREES, 240 * DEGREES]

        voltage_traces_3 = []
        for offset in coil_offsets_3:
            trace = calculate_sine_voltage_trace(
                num_magnets=NUM_MAGNETS_4,
                rotation_speed=ROTATION_SPEED,
                total_time=QUICK_SPIN_TIME,
                coil_angle_func=get_coil_angle_static(offset),
                amplitude=10.0,
                steps=PHYSICS_STEPS,
            )
            voltage_traces_3.append(trace)

        max_v_3 = max(abs(v) for trace in voltage_traces_3 for _, v in trace) * 1.1

        graph_width_3 = 2.2
        graph_height_3 = 1.4

        axes_3 = []
        graph_labels_3 = ["Phase A", "Phase B", "Phase C"]
        graph_colors_3 = [PHASE_A_COLOR, PHASE_B_COLOR, PHASE_C_COLOR]
        trace_order_3 = [0, 2, 1]

        graphs_3_group = VGroup()
        for i in range(3):
            ax = Axes(
                x_range=[0, QUICK_SPIN_TIME, 1],
                y_range=[-max_v_3, max_v_3, max_v_3],
                x_length=graph_width_3,
                y_length=graph_height_3,
                axis_config={"include_tip": False, "color": GREY},
            )
            label = Text(graph_labels_3[i], font_size=16, color=graph_colors_3[i])
            label.next_to(ax, DOWN, buff=0.08)  # Labels BELOW graphs
            axes_3.append(ax)
            graphs_3_group.add(VGroup(ax, label))

        graphs_3_group.arrange(DOWN, buff=0.35)
        # Position graphs on right side, vertically centered
        graphs_3_group.to_edge(RIGHT, buff=0.5).move_to(
            graphs_3_group.get_center() * RIGHT + ORIGIN  # Keep x, reset y to center
        )

        curves_3 = VGroup()
        for i in range(3):
            curve = VMobject().set_color(graph_colors_3[i]).set_stroke(width=2.5)
            curves_3.add(curve)

        # ============================================================
        # PHASE 2: BUILD 8-MAGNET / 6-COIL GENERATOR
        # ============================================================
        coil_colors_6 = [
            PHASE_A_COLOR,  # A (Phase A)
            PHASE_C_COLOR,  # B (Phase C)
            PHASE_B_COLOR,  # C (Phase B)
            PHASE_A_COLOR,  # A' (Phase A)
            PHASE_C_COLOR,  # B' (Phase C)
            PHASE_B_COLOR,  # C' (Phase B)
        ]
        generator_coil_labels = ["A", "B", "C", "A'", "B'", "C'"]

        generator_8, rotor_8 = build_generator_with_numbers(8, 6, coil_colors_6, generator_coil_labels)
        generator_8.scale(0.8).to_edge(LEFT, buff=0.8)

        label_8 = Text("8 magnets / 6 coils", font_size=22, weight=BOLD)
        label_8.next_to(generator_8, DOWN, buff=0.2)

        # ============================================================
        # 6 VOLTAGE GRAPHS IN 2x3 GRID (CLEAN MINIMAL STYLE)
        # ============================================================
        # Phase relationships for 8 magnets (4 pole pairs), 6 coils at 60 deg spacing:
        # Electrical angle = mechanical angle x 4
        # Coil 1: 0 deg elec (Phase A)
        # Coil 2: 240 deg elec (Phase C, same as -120 deg)
        # Coil 3: 120 deg elec (Phase B)
        # Coil 4: 0 deg elec (Phase A - same as Coil 1)
        # Coil 5: 240 deg elec (Phase C - same as Coil 2)
        # Coil 6: 120 deg elec (Phase B - same as Coil 3)

        # Use simple np.sin() for clean waveforms
        NUM_CYCLES = 3  # Show 3 complete cycles
        WAVEFORM_POINTS = 200

        # Phase offsets in radians for each coil
        # Phase A (Coils 1,4): sin(x) -> offset = 0
        # Phase B (Coils 3,6): sin(x + 2*PI/3) -> offset = 2*PI/3 (120 deg ahead)
        # Phase C (Coils 2,5): sin(x + 4*PI/3) -> offset = 4*PI/3 (240 deg ahead)
        phase_offsets = [
            0,              # Coil 1: Phase A
            4 * PI / 3,     # Coil 2: Phase C (240 deg)
            2 * PI / 3,     # Coil 3: Phase B (120 deg)
            0,              # Coil 4: Phase A (same as 1)
            4 * PI / 3,     # Coil 5: Phase C (same as 2)
            2 * PI / 3,     # Coil 6: Phase B (same as 3)
        ]

        # Generate waveform data for each coil
        x_data = np.linspace(0, NUM_CYCLES * 2 * PI, WAVEFORM_POINTS)
        coil_waveforms = []
        for offset in phase_offsets:
            y_data = np.sin(x_data + offset)
            coil_waveforms.append((x_data, y_data))

        # Graph dimensions for 2x3 grid - minimal clean style
        graph_width_6 = 1.6
        graph_height_6 = 0.9

        axes_6 = []
        coil_labels_6 = ["A", "B", "C", "A'", "B'", "C'"]

        # Create 6 graph groups with MINIMAL axes (no ticks, just baseline)
        # Add "+1" / "-1" markers to show amplitude scale for comparison with merged graphs
        graph_items_6 = []
        for i in range(6):
            # Create minimal axis - just a horizontal baseline
            baseline = Line(
                start=LEFT * graph_width_6 / 2,
                end=RIGHT * graph_width_6 / 2,
                color=GREY,
                stroke_width=1,
                stroke_opacity=0.5
            )

            # Create axes for coordinate conversion (invisible)
            ax = Axes(
                x_range=[0, NUM_CYCLES * 2 * PI, 1],
                y_range=[-1.2, 1.2, 1],
                x_length=graph_width_6,
                y_length=graph_height_6,
                axis_config={"include_tip": False, "stroke_opacity": 0},  # Invisible axes
            )

            label = Text(coil_labels_6[i], font_size=14, color=coil_colors_6[i])
            label.next_to(ax, DOWN, buff=0.08)

            # Add "+1" and "-1" markers for amplitude reference
            plus_1_marker = Text("+1", font_size=10, color=GREY)
            minus_1_marker = Text("-1", font_size=10, color=GREY)
            plus_1_pos = ax.c2p(0, 1)
            minus_1_pos = ax.c2p(0, -1)
            plus_1_marker.move_to(plus_1_pos).shift(LEFT * 0.3)
            minus_1_marker.move_to(minus_1_pos).shift(LEFT * 0.3)

            axes_6.append(ax)
            graph_items_6.append(VGroup(ax, baseline, label, plus_1_marker, minus_1_marker))

        # Arrange in 2 rows of 3
        # Row 1: Coil 1, Coil 2, Coil 3 (blue, orange, green)
        row1 = VGroup(graph_items_6[0], graph_items_6[1], graph_items_6[2])
        row1.arrange(RIGHT, buff=0.4)

        # Row 2: Coil 4, Coil 5, Coil 6 (blue, orange, green)
        row2 = VGroup(graph_items_6[3], graph_items_6[4], graph_items_6[5])
        row2.arrange(RIGHT, buff=0.4)

        graphs_6_group = VGroup(row1, row2)
        graphs_6_group.arrange(DOWN, buff=0.5)
        # Position on right side, vertically centered
        graphs_6_group.to_edge(RIGHT, buff=0.5).move_to(
            graphs_6_group.get_center() * RIGHT + ORIGIN
        )

        # Pre-draw all 6 curves (static waveforms, not animated)
        curves_6 = VGroup()
        for i in range(6):
            x_vals, y_vals = coil_waveforms[i]
            points = [axes_6[i].c2p(x, y) for x, y in zip(x_vals, y_vals)]
            curve = VMobject().set_color(coil_colors_6[i]).set_stroke(width=2.5)
            curve.set_points_as_corners(points)
            curves_6.add(curve)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # --- STEP 1: Show 4-magnet / 3-coil generator ---
        self.add(generator_4, label_4, graphs_3_group, curves_3)
        self.wait(0.5)

        # Quick rotation to show it working
        rotor_4_center = rotor_4.get_center()
        self.play(
            Rotate(rotor_4, angle=-2*PI, about_point=rotor_4_center),
            run_time=2.0,
            rate_func=linear
        )

        self.wait(0.8)

        # --- STEP 2: Transform to 8-magnet / 6-coil ---
        transform_text = Text("Double the magnets and coils...", font_size=24, color=YELLOW)
        transform_text.to_edge(UP, buff=0.15)

        self.play(FadeIn(transform_text), run_time=0.5)
        self.wait(0.3)

        self.play(
            ReplacementTransform(generator_4, generator_8),
            ReplacementTransform(label_4, label_8),
            FadeOut(graphs_3_group),
            FadeOut(curves_3),
            run_time=1.2
        )

        self.play(FadeOut(transform_text), run_time=0.3)

        # Spin the rotor for a few seconds to show the generator in action
        self.play(
            Rotate(rotor_8, angle=-2*PI, about_point=rotor_8.get_center()),
            run_time=3,
            rate_func=linear
        )

        # --- STEP 3: Show 6 individual graphs in 2x3 grid (PHASE 1) ---
        # All 6 graphs appear at once with their pre-drawn waveforms
        self.play(
            FadeIn(graphs_6_group),
            FadeIn(curves_6),
            run_time=1.0
        )

        self.wait(1.5)  # Let viewer see the 6 graphs

        # --- STEP 4: Highlight Phase Twins ---
        coils_8 = generator_8[2]  # stator, rotor, coils, numbers

        # Phase A: Coils A & A' (indices 0, 3) - identical waveforms
        highlight_A = Text("A & A': Phase twins (identical)", font_size=20, color=PHASE_A_COLOR, weight=BOLD)
        highlight_A.to_edge(UP, buff=0.3)

        self.play(
            Indicate(coils_8[0], color=PHASE_A_COLOR, scale_factor=1.3),
            Indicate(coils_8[3], color=PHASE_A_COLOR, scale_factor=1.3),
            Indicate(graph_items_6[0], color=PHASE_A_COLOR),
            Indicate(graph_items_6[3], color=PHASE_A_COLOR),
            FadeIn(highlight_A),
            run_time=0.8
        )
        self.wait(0.6)
        self.play(FadeOut(highlight_A), run_time=0.2)

        # Phase C: Coils B & B' (indices 1, 4) - identical waveforms
        highlight_C = Text("B & B': Phase twins (identical)", font_size=20, color=PHASE_C_COLOR, weight=BOLD)
        highlight_C.to_edge(UP, buff=0.3)

        self.play(
            Indicate(coils_8[1], color=PHASE_C_COLOR, scale_factor=1.3),
            Indicate(coils_8[4], color=PHASE_C_COLOR, scale_factor=1.3),
            Indicate(graph_items_6[1], color=PHASE_C_COLOR),
            Indicate(graph_items_6[4], color=PHASE_C_COLOR),
            FadeIn(highlight_C),
            run_time=0.8
        )
        self.wait(0.6)
        self.play(FadeOut(highlight_C), run_time=0.2)

        # Phase B: Coils C & C' (indices 2, 5) - identical waveforms
        highlight_B = Text("C & C': Phase twins (identical)", font_size=20, color=PHASE_B_COLOR, weight=BOLD)
        highlight_B.to_edge(UP, buff=0.3)

        self.play(
            Indicate(coils_8[2], color=PHASE_B_COLOR, scale_factor=1.3),
            Indicate(coils_8[5], color=PHASE_B_COLOR, scale_factor=1.3),
            Indicate(graph_items_6[2], color=PHASE_B_COLOR),
            Indicate(graph_items_6[5], color=PHASE_B_COLOR),
            FadeIn(highlight_B),
            run_time=0.8
        )
        self.wait(0.6)
        self.play(FadeOut(highlight_B), run_time=0.2)

        # --- STEP 5: ANIMATED MERGE - Scale approach ---
        # Simple approach: bottom curves slide up and fade, top curves scale Y by 2x
        # The scale happens around the baseline center so waves grow symmetrically

        series_text = Text("Wire phase twins in series...", font_size=22, weight=BOLD)
        series_text.to_edge(UP, buff=0.3)
        self.play(FadeIn(series_text), run_time=0.4)

        self.wait(0.5)

        # Get the center of each top row baseline (the horizontal line at index [1])
        baseline_center_0 = graph_items_6[0][1].get_center()
        baseline_center_1 = graph_items_6[1][1].get_center()
        baseline_center_2 = graph_items_6[2][1].get_center()

        # Store top row positions for the slide-up animation
        top_row_centers = [curves_6[i].get_center() for i in range(3)]

        # Create new Phase labels for top row (replacing "Coil N" labels)
        # Shift labels DOWN more so they don't crowd the scaled waveform
        phase_a_label = Text("Phase A", font_size=14, color=PHASE_A_COLOR, weight=BOLD)
        phase_a_label.move_to(graph_items_6[0][2].get_center()).shift(DOWN * 0.35)

        phase_c_label = Text("Phase C", font_size=14, color=PHASE_C_COLOR, weight=BOLD)
        phase_c_label.move_to(graph_items_6[1][2].get_center()).shift(DOWN * 0.35)

        phase_b_label = Text("Phase B", font_size=14, color=PHASE_B_COLOR, weight=BOLD)
        phase_b_label.move_to(graph_items_6[2][2].get_center()).shift(DOWN * 0.35)

        # Create +2/-2 markers (replacing +1/-1)
        plus_2_markers = []
        minus_2_markers = []
        marker_colors = [PHASE_A_COLOR, PHASE_C_COLOR, PHASE_B_COLOR]
        for i in range(3):
            plus_2 = Text("+2", font_size=10, color=marker_colors[i], weight=BOLD)
            plus_2.move_to(graph_items_6[i][3].get_center())
            plus_2_markers.append(plus_2)

            minus_2 = Text("-2", font_size=10, color=marker_colors[i], weight=BOLD)
            minus_2.move_to(graph_items_6[i][4].get_center())
            minus_2_markers.append(minus_2)

        self.play(
            # Bottom curves slide up and fade
            curves_6[3].animate.move_to(top_row_centers[0]).set_opacity(0),
            curves_6[4].animate.move_to(top_row_centers[1]).set_opacity(0),
            curves_6[5].animate.move_to(top_row_centers[2]).set_opacity(0),

            # Top curves SCALE vertically by 2x around baseline center
            # scale([1, 2, 1]) means: X unchanged, Y doubled, Z unchanged
            curves_6[0].animate.scale([1, 2, 1], about_point=baseline_center_0),
            curves_6[1].animate.scale([1, 2, 1], about_point=baseline_center_1),
            curves_6[2].animate.scale([1, 2, 1], about_point=baseline_center_2),

            # Bottom row elements fade out
            FadeOut(graph_items_6[3][1]),  # baseline
            FadeOut(graph_items_6[3][2]),  # label
            FadeOut(graph_items_6[3][3]),  # +1 marker
            FadeOut(graph_items_6[3][4]),  # -1 marker
            FadeOut(graph_items_6[4][1]),
            FadeOut(graph_items_6[4][2]),
            FadeOut(graph_items_6[4][3]),
            FadeOut(graph_items_6[4][4]),
            FadeOut(graph_items_6[5][1]),
            FadeOut(graph_items_6[5][2]),
            FadeOut(graph_items_6[5][3]),
            FadeOut(graph_items_6[5][4]),

            # Top row labels transform to Phase names
            Transform(graph_items_6[0][2], phase_a_label),
            Transform(graph_items_6[1][2], phase_c_label),
            Transform(graph_items_6[2][2], phase_b_label),

            # Top row +1/-1 markers transform to +2/-2
            Transform(graph_items_6[0][3], plus_2_markers[0]),
            Transform(graph_items_6[0][4], minus_2_markers[0]),
            Transform(graph_items_6[1][3], plus_2_markers[1]),
            Transform(graph_items_6[1][4], minus_2_markers[1]),
            Transform(graph_items_6[2][3], plus_2_markers[2]),
            Transform(graph_items_6[2][4], minus_2_markers[2]),

            run_time=1.5
        )

        self.wait(1.0)

        # --- STEP 6: Final Reveal ---
        self.play(FadeOut(series_text), run_time=0.3)

        final_text = Text("Same 3-phase, 2x voltage!", font_size=26, weight=BOLD, color=YELLOW)
        final_text.to_edge(UP, buff=0.3)

        amplitude_text = VGroup(
            Text("Original: 1 coil per phase", font_size=14, color=GRAY),
            Text("Scaled: 2 coils in series = 2x voltage", font_size=14, color=YELLOW)
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        amplitude_text.next_to(final_text, RIGHT, buff=0.4)

        self.play(FadeIn(final_text), FadeIn(amplitude_text), run_time=0.8)

        # Quick highlight of phase groupings on generator
        self.play(
            coils_8[0].animate.set_stroke(width=10),
            coils_8[3].animate.set_stroke(width=10),
            run_time=0.3
        )
        self.play(
            coils_8[0].animate.set_stroke(width=6),
            coils_8[3].animate.set_stroke(width=6),
            coils_8[1].animate.set_stroke(width=10),
            coils_8[4].animate.set_stroke(width=10),
            run_time=0.3
        )
        self.play(
            coils_8[1].animate.set_stroke(width=6),
            coils_8[4].animate.set_stroke(width=6),
            coils_8[2].animate.set_stroke(width=10),
            coils_8[5].animate.set_stroke(width=10),
            run_time=0.3
        )
        self.play(
            coils_8[2].animate.set_stroke(width=6),
            coils_8[5].animate.set_stroke(width=6),
            run_time=0.3
        )

        self.wait(2)
