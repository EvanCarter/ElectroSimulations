from manim import *
from generator import build_rotor
import math
import numpy as np


def build_coils_square(num_coils, path_radius, magnet_radius, start_angle=PI/2):
    """Build square coils evenly spaced around the path."""
    coils = VGroup()
    for i in range(num_coils):
        coil_angle = start_angle - (i * (2 * PI / num_coils))
        x = path_radius * math.cos(coil_angle)
        y = path_radius * math.sin(coil_angle)

        coil = Rectangle(
            width=magnet_radius * 2,
            height=magnet_radius * 2,
            color=ORANGE,
            stroke_width=4,
            fill_opacity=0.3,
            fill_color=ORANGE
        )
        coil.rotate(coil_angle - PI / 2)
        coil.move_to(np.array([x, y, 0]))
        coils.add(coil)
    return coils


class CoggingComparisonScene(Scene):
    """
    Side-by-side comparison showing why fractional magnet:coil ratios reduce cogging.

    Visual Elements:
    - LEFT: 4/4 generator (4 magnets, 4 coils)
    - RIGHT: 4/3 generator (4 magnets, 3 coils)
    - Labels above each generator (4/4 in RED, 4/3 in WHITE)
    - Yellow alignment highlights flash when magnets align with coils
    - Scrolling cogging torque graphs below each generator
    - Winner box around 4/3 at the end

    Physics Demonstrated:
    - 4/4 (1:1 ratio): All 4 magnets align with all 4 coils simultaneously
      -> Big cogging torque spikes -> JERKY rotation
    - 4/3 (fractional ratio): Magnets and coils never all align at once
      -> Forces partially cancel -> SMOOTH, smaller ripple
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 1.6  # Smaller to make room for graphs
        MAGNET_RADIUS = 0.4
        OFFSET_FROM_EDGE = 0.1
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        ROTATION_SPEED = 0.3 * PI  # Slow rotation for clarity

        # Generator configurations
        NUM_MAGNETS = 4  # Both have 4 magnets at 90 degree intervals
        NUM_COILS_LEFT = 4   # 4/4 ratio - 1:1
        NUM_COILS_RIGHT = 3  # 4/3 ratio - fractional

        # Alignment threshold for highlight flashing
        ALIGNMENT_THRESHOLD = PI / 8  # 22.5 degrees

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        SIMULATION_TIME = 10.0

        # ============================================================
        # HELPER FUNCTIONS
        # ============================================================

        def normalize_angle(angle):
            """Normalize angle to [-PI, PI]."""
            while angle > PI:
                angle -= 2 * PI
            while angle < -PI:
                angle += 2 * PI
            return angle

        def get_magnet_angles(rotation_angle):
            """Get current magnet angles given rotation from initial position."""
            base_angles = [(PI / 2.0) - (i * (2 * PI / NUM_MAGNETS)) for i in range(NUM_MAGNETS)]
            return [(angle - rotation_angle) for angle in base_angles]

        def get_coil_angles(num_coils):
            """Get angular positions of evenly spaced coils starting at 12 o'clock."""
            return [(PI / 2.0) - (i * (2 * PI / num_coils)) for i in range(num_coils)]

        def calculate_cogging_potential(rotation, num_coils, sigma=0.1):
            """
            Calculate cogging potential using pairwise Gaussian summation.

            Each magnet-coil pair contributes based on alignment.
            Narrow sigma (~0.1 rad = 5.7°) makes peaks sharp like "detent clicks"
            while keeping the animation smooth.

            4/4: All 4 magnets align at once → peak height ~4
            4/3: Only 1 magnet aligns at a time → peak height ~1
            """
            magnet_spacing = (2 * PI) / NUM_MAGNETS
            coil_spacing = (2 * PI) / num_coils

            total = 0.0

            for m in range(NUM_MAGNETS):
                # Current angle of this magnet
                m_angle = (rotation + m * magnet_spacing) % (2 * PI)

                for c in range(num_coils):
                    # Fixed angle of this coil
                    c_angle = (c * coil_spacing) % (2 * PI)

                    # Shortest distance on circle
                    diff = min(abs(m_angle - c_angle), 2 * PI - abs(m_angle - c_angle))

                    # Gaussian: peak at 1 when aligned, decays quickly
                    interaction = np.exp(-(diff**2) / (2 * sigma**2))
                    total += interaction

            return total

        # Get coil angles for each configuration
        COIL_ANGLES_LEFT = get_coil_angles(NUM_COILS_LEFT)
        COIL_ANGLES_RIGHT = get_coil_angles(NUM_COILS_RIGHT)

        # ============================================================
        # BUILD TWO GENERATORS (moved up to make room for graphs)
        # ============================================================

        # Generator positions
        GEN_SPACING = 5.0
        GEN_Y_OFFSET = 1.3  # Move up to make room for graphs
        LEFT_POS = np.array([-GEN_SPACING / 2, GEN_Y_OFFSET, 0])
        RIGHT_POS = np.array([GEN_SPACING / 2, GEN_Y_OFFSET, 0])

        # --- LEFT GENERATOR: 4/4 (1:1 ratio) ---
        rotor_left = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)
        coils_left = build_coils_square(NUM_COILS_LEFT, MAGNET_PATH_RADIUS, MAGNET_RADIUS)
        stator_left = Circle(radius=DISK_RADIUS + 0.1, color=GRAY, stroke_width=3, stroke_opacity=0.5)

        gen_left = VGroup(stator_left, coils_left, rotor_left)
        gen_left.move_to(LEFT_POS)
        disk_center_left = rotor_left.get_center()

        # --- RIGHT GENERATOR: 4/3 (fractional ratio) ---
        rotor_right = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)
        coils_right = build_coils_square(NUM_COILS_RIGHT, MAGNET_PATH_RADIUS, MAGNET_RADIUS)
        stator_right = Circle(radius=DISK_RADIUS + 0.1, color=GRAY, stroke_width=3, stroke_opacity=0.5)

        gen_right = VGroup(stator_right, coils_right, rotor_right)
        gen_right.move_to(RIGHT_POS)
        disk_center_right = rotor_right.get_center()

        generators = VGroup(gen_left, gen_right)

        # ============================================================
        # LABELS (titles above generators)
        # ============================================================
        label_left = VGroup(
            Text("4/4", font_size=32, color=RED),
            Text("(1:1 ratio)", font_size=18, color=RED)
        ).arrange(DOWN, buff=0.05)
        label_left.next_to(gen_left, UP, buff=0.25)

        label_right = VGroup(
            Text("4/3", font_size=32, color=WHITE),
            Text("(fractional)", font_size=18, color=LIGHT_GREY)
        ).arrange(DOWN, buff=0.05)
        label_right.next_to(gen_right, UP, buff=0.25)

        labels = VGroup(label_left, label_right)

        # ============================================================
        # COGGING TORQUE GRAPHS
        # ============================================================
        GRAPH_WIDTH = 4.0
        GRAPH_HEIGHT = 1.5
        GRAPH_Y_POS = -2.0

        # Left graph (4/4 - will show big spikes)
        # Y-range: 0 to 5 (positive only, cogging is always >= 0)
        axes_left = Axes(
            x_range=[0, SIMULATION_TIME, 2],
            y_range=[0, 5, 1],
            x_length=GRAPH_WIDTH,
            y_length=GRAPH_HEIGHT,
            axis_config={"color": GREY, "stroke_width": 2},
            tips=False,
        )
        axes_left.move_to(np.array([LEFT_POS[0], GRAPH_Y_POS, 0]))

        # Add y-axis label
        y_label_left = Text("Cogging", font_size=14, color=GREY)
        y_label_left.rotate(PI / 2)
        y_label_left.next_to(axes_left, LEFT, buff=0.1)

        # Right graph (4/3 - will show smaller ripple)
        axes_right = Axes(
            x_range=[0, SIMULATION_TIME, 2],
            y_range=[0, 5, 1],
            x_length=GRAPH_WIDTH,
            y_length=GRAPH_HEIGHT,
            axis_config={"color": GREY, "stroke_width": 2},
            tips=False,
        )
        axes_right.move_to(np.array([RIGHT_POS[0], GRAPH_Y_POS, 0]))

        y_label_right = Text("Cogging", font_size=14, color=GREY)
        y_label_right.rotate(PI / 2)
        y_label_right.next_to(axes_right, LEFT, buff=0.1)

        graphs = VGroup(axes_left, y_label_left, axes_right, y_label_right)

        # ============================================================
        # TIME TRACKER AND ROTOR UPDATERS
        # ============================================================
        time_tracker = ValueTracker(0)

        last_t = [0.0]

        def update_rotor_left(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t[0]
            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center_left)

        def update_rotor_right(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t[0]
            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center_right)
                last_t[0] = t_now  # Only update once per frame

        rotor_left.add_updater(update_rotor_left)
        rotor_right.add_updater(update_rotor_right)

        # ============================================================
        # ALIGNMENT HIGHLIGHT ELEMENTS
        # ============================================================

        def create_alignment_highlights(num_coils, path_radius, center, color):
            """Create highlight circles at each coil position."""
            highlights = VGroup()
            for i in range(num_coils):
                coil_angle = (PI / 2) - (i * (2 * PI / num_coils))
                x = center[0] + path_radius * math.cos(coil_angle)
                y = center[1] + path_radius * math.sin(coil_angle)
                highlight = Circle(
                    radius=MAGNET_RADIUS * 1.3,
                    color=color,
                    stroke_width=4,
                    fill_opacity=0.0
                )
                highlight.move_to(np.array([x, y, 0]))
                highlight.set_stroke(opacity=0)  # Start invisible
                highlights.add(highlight)
            return highlights

        highlights_left = create_alignment_highlights(
            NUM_COILS_LEFT, MAGNET_PATH_RADIUS, disk_center_left, YELLOW
        )
        highlights_right = create_alignment_highlights(
            NUM_COILS_RIGHT, MAGNET_PATH_RADIUS, disk_center_right, YELLOW
        )

        # Highlight updaters
        def update_highlights_left(mob):
            t_now = time_tracker.get_value()
            rotation = ROTATION_SPEED * t_now
            mag_angles = get_magnet_angles(rotation)

            for i, highlight in enumerate(mob):
                coil_angle = COIL_ANGLES_LEFT[i]
                is_aligned = False
                for mag_angle in mag_angles:
                    angle_diff = normalize_angle(mag_angle - coil_angle)
                    if abs(angle_diff) < ALIGNMENT_THRESHOLD:
                        is_aligned = True
                        break

                if is_aligned:
                    highlight.set_stroke(opacity=0.5)
                else:
                    highlight.set_stroke(opacity=0)

        def update_highlights_right(mob):
            t_now = time_tracker.get_value()
            rotation = ROTATION_SPEED * t_now
            mag_angles = get_magnet_angles(rotation)

            for i, highlight in enumerate(mob):
                coil_angle = COIL_ANGLES_RIGHT[i]
                is_aligned = False
                for mag_angle in mag_angles:
                    angle_diff = normalize_angle(mag_angle - coil_angle)
                    if abs(angle_diff) < ALIGNMENT_THRESHOLD:
                        is_aligned = True
                        break

                if is_aligned:
                    highlight.set_stroke(opacity=0.5)
                else:
                    highlight.set_stroke(opacity=0)

        highlights_left.add_updater(update_highlights_left)
        highlights_right.add_updater(update_highlights_right)

        # ============================================================
        # TORQUE GRAPH TRACES
        # ============================================================

        # Create traced paths for torque graphs
        trace_left = VMobject(color=RED, stroke_width=3)
        trace_left.set_points_as_corners([axes_left.c2p(0, 0), axes_left.c2p(0, 0)])

        trace_right = VMobject(color=GREEN, stroke_width=3)
        trace_right.set_points_as_corners([axes_right.c2p(0, 0), axes_right.c2p(0, 0)])

        # Pre-compute cogging data for smooth curves
        NUM_SAMPLES = 500
        times = np.linspace(0, SIMULATION_TIME, NUM_SAMPLES)
        cogging_left_data = []
        cogging_right_data = []

        # Use narrow sigma for sharp "detent click" peaks
        SIGMA = 0.12  # ~7 degrees - sharp but smooth

        for t in times:
            rotation = ROTATION_SPEED * t
            cogging_left_data.append(calculate_cogging_potential(rotation, NUM_COILS_LEFT, SIGMA))
            cogging_right_data.append(calculate_cogging_potential(rotation, NUM_COILS_RIGHT, SIGMA))

        cogging_left_data = np.array(cogging_left_data)
        cogging_right_data = np.array(cogging_right_data)

        # DON'T normalize separately - keep same scale so 4/4 shows bigger peaks
        # The math naturally gives: 4/4 peaks ~4, 4/3 peaks ~1
        # Scale to fit y-range of [0, 4.5]
        global_max = max(np.max(cogging_left_data), np.max(cogging_right_data))
        cogging_left_data = cogging_left_data / global_max * 4.5
        cogging_right_data = cogging_right_data / global_max * 4.5

        def update_trace_left(mob):
            t_now = time_tracker.get_value()
            if t_now <= 0:
                return

            # Find index up to current time
            idx = int(t_now / SIMULATION_TIME * (NUM_SAMPLES - 1))
            idx = min(idx, NUM_SAMPLES - 1)

            if idx < 1:
                return

            # Build path from samples
            points = [axes_left.c2p(times[i], cogging_left_data[i]) for i in range(idx + 1)]
            mob.set_points_as_corners(points)

        def update_trace_right(mob):
            t_now = time_tracker.get_value()
            if t_now <= 0:
                return

            idx = int(t_now / SIMULATION_TIME * (NUM_SAMPLES - 1))
            idx = min(idx, NUM_SAMPLES - 1)

            if idx < 1:
                return

            points = [axes_right.c2p(times[i], cogging_right_data[i]) for i in range(idx + 1)]
            mob.set_points_as_corners(points)

        trace_left.add_updater(update_trace_left)
        trace_right.add_updater(update_trace_right)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # 1. Show both generators
        self.add(generators)
        self.wait(0.5)

        # 2. Add labels
        self.play(FadeIn(labels), run_time=0.5)
        self.wait(0.3)

        # 3. Add graph axes
        self.play(FadeIn(graphs), run_time=0.5)
        self.wait(0.3)

        # 4. Add highlights and traces, start rotation
        self.add(highlights_left, highlights_right)
        self.add(trace_left, trace_right)

        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=SIMULATION_TIME,
            rate_func=linear
        )

        self.wait(2)
