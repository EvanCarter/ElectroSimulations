from manim import *
from generator import (
    calculate_physics_data,
    build_coils,
    build_rotor,
)
import math


class SinglePhaseScene(Scene):
    def construct(self):
        # --- CONSTANTS ---
        DISK_RADIUS = 3.0
        MAGNET_RADIUS = 0.8  # Bigger as requested
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS

        NUM_MAGNETS = 2
        NUM_COILS = 1

        ROTATION_SPEED = 0.5 * PI  # 1 full rotation in 4 seconds
        TOTAL_TIME = 8.0  # 2 full rotations

        # --- PHYSICS CALCULATION ---
        # We use the helper from generator.py
        # It returns smoothed flux and voltage data
        flux_data, voltage_data = calculate_physics_data(
            num_magnets=NUM_MAGNETS,
            rotation_speed=ROTATION_SPEED,
            total_time=TOTAL_TIME,
            magnet_path_radius=MAGNET_PATH_RADIUS,
            magnet_radius=MAGNET_RADIUS,
        )

        # Determine Max Voltage for Graph Scaling
        max_voltage = (
            max([abs(v[1]) for v in voltage_data]) * 1.1 if voltage_data else 1.0
        )

        # --- VISUAL SETUP ---

        # 1. GENERATOR (LEFT SIDE)
        # Create standard objects using helpers
        coils = build_coils(NUM_COILS, MAGNET_PATH_RADIUS, MAGNET_RADIUS)
        rotor_group = build_rotor(
            NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS
        )

        # Group them
        generator_group = VGroup(coils, rotor_group)

        # Position: Move to LEFT side
        generator_group.to_edge(LEFT, buff=1.0)

        # 2. GRAPH (RIGHT SIDE)
        # Axes for Voltage vs Time
        # x_range: [0, TOTAL_TIME]
        # y_range: [-max, max]
        voltage_ax = Axes(
            x_range=[0, TOTAL_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage / 2],
            x_length=6,
            y_length=4,
            axis_config={"include_tip": False, "color": GREY},
        ).to_edge(RIGHT, buff=0.5)

        # Add a center line (zero voltage) for clarity
        zero_line = voltage_ax.get_horizontal_line(
            voltage_ax.c2p(TOTAL_TIME, 0),
            color=GREY,
            stroke_width=1,
        ).set_stroke(opacity=0.5)

        voltage_label = voltage_ax.get_y_axis_label(
            Text("Voltage", font_size=24).rotate(90 * DEGREES)
        ).next_to(voltage_ax, LEFT, buff=0.1)

        voltage_title = Text("Single Phase Output", font_size=32).next_to(
            voltage_ax, UP
        )

        graph_group = VGroup(voltage_ax, voltage_label, voltage_title, zero_line)

        # --- ANIMATION SETUP ---

        self.add(generator_group, graph_group)

        # Time Tracker to drive both rotation and graph
        time_tracker = ValueTracker(0)

        # A. Rotor Rotation Updater
        # Use absolute tracking to avoid lag/drift
        self.last_angle = 0

        def update_rotor(mob):
            t = time_tracker.get_value()
            target_angle = -ROTATION_SPEED * t
            angle_delta = target_angle - self.last_angle

            mob.rotate(angle_delta, about_point=generator_group.get_center())
            self.last_angle = target_angle

        rotor_group.add_updater(update_rotor)

        # B. Graph Updater
        # Create a path that follows the calculated data points up to time t

        # Pre-calc points
        graph_points = [voltage_ax.c2p(t, v) for t, v in voltage_data]

        voltage_curve = (
            VMobject()
            .set_points_as_corners([graph_points[0]])
            .set_color(YELLOW)
            .set_stroke(width=3)
        )
        voltage_dot = Dot(color=YELLOW).scale(0.8)

        def update_graph(mob):
            t = time_tracker.get_value()
            idx = int((t / TOTAL_TIME) * len(graph_points))
            idx = max(0, min(idx, len(graph_points) - 1))

            # Draw up to current index
            mob.set_points_as_corners(graph_points[: idx + 1])

            # Move dot
            if idx < len(graph_points):
                voltage_dot.move_to(graph_points[idx])

        voltage_curve.add_updater(update_graph)
        voltage_dot.add_updater(
            lambda m: update_graph(voltage_curve)
        )  # Sync dot with curve update?
        # Actually update_graph handles both if we structure it right, or separate them.
        # Let's separate cleanly.

        def update_dot(mob):
            t = time_tracker.get_value()
            idx = int((t / TOTAL_TIME) * len(graph_points))
            idx = max(0, min(idx, len(graph_points) - 1))
            mob.move_to(graph_points[idx])

        voltage_dot.add_updater(update_dot)

        self.add(voltage_curve, voltage_dot)

        # --- ACTION ---
        self.wait(0.5)

        self.play(
            time_tracker.animate.set_value(TOTAL_TIME),
            run_time=TOTAL_TIME,
            rate_func=linear,
        )

        self.wait(1)
