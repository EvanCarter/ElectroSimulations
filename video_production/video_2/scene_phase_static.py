from manim import *
from generator import build_rotor, calculate_sine_voltage_trace
import math
import numpy as np
from dataclasses import dataclass
from typing import Callable


@dataclass
class CoilConfig:
    """Configuration for a single coil"""
    name: str
    color: str
    position_angle: float  # Fixed angular position (radians from 12 o'clock, clockwise)


class PhaseStaticScene(Scene):
    """
    Shows coils at fixed positions (12, 4, 8 o'clock) to observe phase relationships.
    Includes both individual graphs and a combined overlay graph.
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 3.0
        MAGNET_RADIUS = 0.8
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        NUM_MAGNETS = 2
        ROTATION_SPEED = 0.5 * PI  # rad/s, clockwise

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        SIMULATION_TIME = 4.0  # Shorter time = fewer cycles = clearer phase view
        PHYSICS_STEPS = 2500
        dt = SIMULATION_TIME / PHYSICS_STEPS

        # ============================================================
        # COIL CONFIGURATIONS - FIXED POSITIONS
        # ============================================================
        coils_config = [
            CoilConfig(name="A", color=BLUE, position_angle=0 * DEGREES),      # 12 o'clock
            CoilConfig(name="B", color=ORANGE, position_angle=120 * DEGREES),  # 4 o'clock
            CoilConfig(name="C", color=GREEN, position_angle=240 * DEGREES),   # 8 o'clock
        ]

        # ============================================================
        # PHYSICS CALCULATION (FINAL Sinusoidal Model)
        # ============================================================
        print(f"Static Phase: Calculating physics for {len(coils_config)} coil(s)...")

        coil_data = {}

        for coil_cfg in coils_config:
            # Fixed coil angle
            coil_angle_static = (PI / 2.0) - coil_cfg.position_angle

            voltage_trace = calculate_sine_voltage_trace(
                num_magnets=NUM_MAGNETS,
                rotation_speed=ROTATION_SPEED,
                total_time=SIMULATION_TIME,
                coil_angle_static=coil_angle_static,
                amplitude=10.0,
                steps=PHYSICS_STEPS,
            )

            coil_data[coil_cfg.name] = voltage_trace
            print(f"  Coil {coil_cfg.name} at {coil_cfg.position_angle/DEGREES:.0f}°: {len(voltage_trace)} points")

        max_voltage = 0.0
        for trace in coil_data.values():
            for _, v in trace:
                max_voltage = max(max_voltage, abs(v))
        max_voltage *= 1.1

        # ============================================================
        # VISUAL ELEMENTS
        # ============================================================

        # --- GENERATOR (Left side, smaller) ---
        rotor_group = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

        stator = Circle(
            radius=DISK_RADIUS + 0.3,
            color=GRAY,
            stroke_width=8,
            stroke_opacity=0.5
        )

        coil_mobjects = VGroup()
        coil_labels = VGroup()

        for coil_cfg in coils_config:
            angle = (PI / 2.0) - coil_cfg.position_angle

            pos = np.array([
                MAGNET_PATH_RADIUS * math.cos(angle),
                MAGNET_PATH_RADIUS * math.sin(angle),
                0
            ])

            coil = DashedVMobject(
                Circle(radius=MAGNET_RADIUS, color=coil_cfg.color, stroke_width=6),
                num_dashes=12
            ).move_to(pos)

            label = Text(coil_cfg.name, font_size=28, color=coil_cfg.color).next_to(coil, UP, buff=0.15)

            coil_mobjects.add(coil)
            coil_labels.add(label)

        generator_group = VGroup(stator, rotor_group, coil_mobjects, coil_labels)
        generator_group.scale(0.55)
        generator_group.to_corner(UL, buff=0.5)
        disk_center = rotor_group.get_center()

        # --- COMBINED PHASE GRAPH (Main feature - larger, centered right) ---
        # Shows all three waveforms overlaid
        combined_ax = Axes(
            x_range=[0, SIMULATION_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage / 2],
            x_length=9,
            y_length=4.5,
            axis_config={"include_tip": False, "color": GREY},
        )

        combined_title = Text("Phase Comparison", font_size=28)
        combined_title.next_to(combined_ax, UP, buff=0.15)

        # Phase labels showing the angular separation
        phase_info = VGroup(
            Text("A: 12 o'clock (0°)", font_size=18, color=BLUE),
            Text("B: 4 o'clock (120°)", font_size=18, color=ORANGE),
            Text("C: 8 o'clock (240°)", font_size=18, color=GREEN),
        ).arrange(RIGHT, buff=0.6)
        phase_info.next_to(combined_ax, DOWN, buff=0.25)

        combined_group = VGroup(combined_ax, combined_title, phase_info)
        combined_group.to_edge(RIGHT, buff=0.4)

        # --- VOLTAGE CURVES ---
        curves = VGroup()
        for coil_cfg in coils_config:
            curve = VMobject().set_color(coil_cfg.color).set_stroke(width=3)
            curve.coil_name = coil_cfg.name
            curves.add(curve)

        # ============================================================
        # UPDATERS
        # ============================================================
        time_tracker = ValueTracker(0)

        last_t = [0.0]

        def update_rotor(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t[0]

            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center)
                last_t[0] = t_now

        rotor_group.add_updater(update_rotor)

        # Voltage curve updaters
        for curve in curves:
            def update_curve(mob):
                t_now = time_tracker.get_value()
                trace = coil_data[mob.coil_name]

                idx_end = int(t_now / dt)
                idx_end = min(len(trace) - 1, max(0, idx_end))

                visible = trace[0:idx_end + 1]

                SUBSAMPLE_RATE = 3
                visible_subsampled = visible[::SUBSAMPLE_RATE]

                if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                    visible_subsampled.append(visible[-1])

                points = []
                for t_val, v_val in visible_subsampled:
                    points.append(combined_ax.c2p(t_val, v_val))

                if len(points) > 1:
                    mob.set_points_as_corners(points)
                elif len(points) == 1:
                    mob.set_points_as_corners([points[0], points[0]])
                else:
                    mob.set_points_as_corners([])

            curve.add_updater(update_curve)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        self.add(generator_group, combined_group, curves)

        self.wait(1)

        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=SIMULATION_TIME,
            rate_func=linear
        )

        self.wait(2)


class TwoPhaseVsSplitPhaseScene(Scene):
    """
    Side-by-side comparison of two-phase (90° offset) vs split-phase (180° offset).
    Two generators stacked on the left:
      - Top: Two-phase (coils at 12 o'clock and 3 o'clock)
      - Bottom: Split-phase (coils at 12 o'clock and 6 o'clock)
    Two pre-drawn graphs stacked on the right showing waveform differences.
    Both rotors animate in sync.
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 3.0
        MAGNET_RADIUS = 0.8
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        NUM_MAGNETS = 2
        ROTATION_SPEED = 0.5 * PI

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        SIMULATION_TIME = 4.0  # Show ~1 rotation
        PHYSICS_STEPS = 2500
        dt = SIMULATION_TIME / PHYSICS_STEPS

        # ============================================================
        # COIL CONFIGURATIONS
        # ============================================================
        # Two-phase: coils at 0° and 90° (12 o'clock and 3 o'clock)
        # Split-phase: coils at 0° and 180° (12 o'clock and 6 o'clock)

        two_phase_coils = [
            {"name": "A", "color": BLUE, "angle": 0 * DEGREES},      # 12 o'clock
            {"name": "B", "color": ORANGE, "angle": 90 * DEGREES},   # 3 o'clock
        ]

        split_phase_coils = [
            {"name": "A", "color": BLUE, "angle": 0 * DEGREES},      # 12 o'clock
            {"name": "B", "color": RED, "angle": 180 * DEGREES},     # 6 o'clock
        ]

        # ============================================================
        # PHYSICS CALCULATION (FINAL Sinusoidal Model)
        # ============================================================
        print("TwoPhaseVsSplitPhase: Calculating physics...")

        # Calculate voltage traces for each configuration
        two_phase_data = {}
        for coil in two_phase_coils:
            coil_angle = (PI / 2.0) - coil["angle"]
            two_phase_data[coil["name"]] = calculate_sine_voltage_trace(
                num_magnets=NUM_MAGNETS,
                rotation_speed=ROTATION_SPEED,
                total_time=SIMULATION_TIME,
                coil_angle_static=coil_angle,
                amplitude=10.0,
                steps=PHYSICS_STEPS,
            )
            print(f"  Two-phase coil {coil['name']} at {coil['angle']/DEGREES:.0f}°: done")

        split_phase_data = {}
        for coil in split_phase_coils:
            coil_angle = (PI / 2.0) - coil["angle"]
            split_phase_data[coil["name"]] = calculate_sine_voltage_trace(
                num_magnets=NUM_MAGNETS,
                rotation_speed=ROTATION_SPEED,
                total_time=SIMULATION_TIME,
                coil_angle_static=coil_angle,
                amplitude=10.0,
                steps=PHYSICS_STEPS,
            )
            print(f"  Split-phase coil {coil['name']} at {coil['angle']/DEGREES:.0f}°: done")

        # Find max voltage for graph scaling
        max_voltage = 0.0
        for trace in list(two_phase_data.values()) + list(split_phase_data.values()):
            for _, v in trace:
                max_voltage = max(max_voltage, abs(v))
        max_voltage *= 1.1

        # ============================================================
        # HELPER FUNCTION: Build square coil
        # ============================================================
        def build_square_coil(coil_angle, coil_color, path_radius, magnet_radius):
            """Build a square coil at the given angle position."""
            pos = np.array([
                path_radius * math.cos(coil_angle),
                path_radius * math.sin(coil_angle),
                0
            ])
            coil = Rectangle(
                width=magnet_radius * 1.5,
                height=magnet_radius * 2.0,
                color=coil_color,
                stroke_width=6
            )
            # Rotate so long side is tangent to the circle path
            coil.rotate(coil_angle - PI/2)
            coil.move_to(pos)
            return coil

        # ============================================================
        # VISUAL ELEMENTS
        # ============================================================

        # --- TWO-PHASE GENERATOR (Top left) ---
        rotor_group_two = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

        stator_two = Circle(
            radius=DISK_RADIUS + 0.3,
            color=GRAY,
            stroke_width=8,
            stroke_opacity=0.5
        )

        coil_mobjects_two = VGroup()
        coil_labels_two = VGroup()

        for coil_cfg in two_phase_coils:
            angle = (PI / 2.0) - coil_cfg["angle"]
            coil = build_square_coil(angle, coil_cfg["color"], MAGNET_PATH_RADIUS, MAGNET_RADIUS)
            label = Text(coil_cfg["name"], font_size=28, color=coil_cfg["color"]).next_to(coil, UP, buff=0.15)
            coil_mobjects_two.add(coil)
            coil_labels_two.add(label)

        generator_two_phase = VGroup(stator_two, rotor_group_two, coil_mobjects_two, coil_labels_two)

        # --- SPLIT-PHASE GENERATOR (Bottom left) ---
        rotor_group_split = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

        stator_split = Circle(
            radius=DISK_RADIUS + 0.3,
            color=GRAY,
            stroke_width=8,
            stroke_opacity=0.5
        )

        coil_mobjects_split = VGroup()
        coil_labels_split = VGroup()

        for coil_cfg in split_phase_coils:
            angle = (PI / 2.0) - coil_cfg["angle"]
            coil = build_square_coil(angle, coil_cfg["color"], MAGNET_PATH_RADIUS, MAGNET_RADIUS)
            label = Text(coil_cfg["name"], font_size=28, color=coil_cfg["color"]).next_to(coil, UP, buff=0.15)
            coil_mobjects_split.add(coil)
            coil_labels_split.add(label)

        generator_split_phase = VGroup(stator_split, rotor_group_split, coil_mobjects_split, coil_labels_split)

        # Stack generators vertically on the left
        generators_group = VGroup(generator_two_phase, generator_split_phase)
        generators_group.arrange(DOWN, buff=0.8)
        generators_group.scale(0.4)
        generators_group.to_edge(LEFT, buff=0.4)

        # Get disk centers for rotor updaters (after scaling and positioning)
        disk_center_two = rotor_group_two.get_center()
        disk_center_split = rotor_group_split.get_center()

        # --- TWO GRAPHS (Right side, stacked) ---
        graph_width = 7.0
        graph_height = 2.2

        # Top graph: Two-phase (90°)
        ax_two_phase = Axes(
            x_range=[0, SIMULATION_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )
        two_phase_title = Text("Two-Phase (90° offset)", font_size=24, color=WHITE)
        two_phase_title.next_to(ax_two_phase, UP, buff=0.15)

        two_phase_legend = VGroup(
            VGroup(Line(LEFT * 0.2, RIGHT * 0.2, color=BLUE, stroke_width=3), Text("A (0°)", font_size=16, color=BLUE)).arrange(RIGHT, buff=0.08),
            VGroup(Line(LEFT * 0.2, RIGHT * 0.2, color=ORANGE, stroke_width=3), Text("B (90°)", font_size=16, color=ORANGE)).arrange(RIGHT, buff=0.08),
        ).arrange(RIGHT, buff=0.5)
        two_phase_legend.next_to(ax_two_phase, DOWN, buff=0.15)

        two_phase_group = VGroup(ax_two_phase, two_phase_title, two_phase_legend)

        # Bottom graph: Split-phase (180°)
        ax_split_phase = Axes(
            x_range=[0, SIMULATION_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )
        split_phase_title = Text("Split-Phase (180° offset)", font_size=24, color=WHITE)
        split_phase_title.next_to(ax_split_phase, UP, buff=0.15)

        split_phase_legend = VGroup(
            VGroup(Line(LEFT * 0.2, RIGHT * 0.2, color=BLUE, stroke_width=3), Text("A (0°)", font_size=16, color=BLUE)).arrange(RIGHT, buff=0.08),
            VGroup(Line(LEFT * 0.2, RIGHT * 0.2, color=RED, stroke_width=3), Text("B (180°)", font_size=16, color=RED)).arrange(RIGHT, buff=0.08),
        ).arrange(RIGHT, buff=0.5)
        split_phase_legend.next_to(ax_split_phase, DOWN, buff=0.15)

        split_phase_group = VGroup(ax_split_phase, split_phase_title, split_phase_legend)

        # Stack graphs
        graphs_group = VGroup(two_phase_group, split_phase_group)
        graphs_group.arrange(DOWN, buff=0.6)
        graphs_group.to_edge(RIGHT, buff=0.3)

        # --- PRE-DRAW VOLTAGE CURVES (no animation) ---
        def build_full_curve(trace, ax, color):
            """Build a complete curve from trace data."""
            SUBSAMPLE_RATE = 3
            visible_subsampled = trace[::SUBSAMPLE_RATE]
            if len(trace) > 0 and (len(trace) - 1) % SUBSAMPLE_RATE != 0:
                visible_subsampled.append(trace[-1])

            points = [ax.c2p(t_val, v_val) for t_val, v_val in visible_subsampled]

            curve = VMobject().set_color(color).set_stroke(width=2.5)
            if len(points) > 1:
                curve.set_points_as_corners(points)
            return curve

        # Two-phase curves (pre-drawn)
        curve_two_a = build_full_curve(two_phase_data["A"], ax_two_phase, BLUE)
        curve_two_b = build_full_curve(two_phase_data["B"], ax_two_phase, ORANGE)

        # Split-phase curves (pre-drawn)
        curve_split_a = build_full_curve(split_phase_data["A"], ax_split_phase, BLUE)
        curve_split_b = build_full_curve(split_phase_data["B"], ax_split_phase, RED)

        curves = VGroup(curve_two_a, curve_two_b, curve_split_a, curve_split_b)

        # ============================================================
        # UPDATERS - FOR BOTH ROTORS
        # ============================================================
        time_tracker = ValueTracker(0)
        last_t_two = [0.0]
        last_t_split = [0.0]

        def update_rotor_two(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t_two[0]
            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center_two)
                last_t_two[0] = t_now

        def update_rotor_split(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t_split[0]
            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center_split)
                last_t_split[0] = t_now

        rotor_group_two.add_updater(update_rotor_two)
        rotor_group_split.add_updater(update_rotor_split)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        self.add(generators_group, graphs_group, curves)

        self.wait(1)

        # Only animate the rotor spinning
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=SIMULATION_TIME,
            rate_func=linear
        )

        self.wait(2)

