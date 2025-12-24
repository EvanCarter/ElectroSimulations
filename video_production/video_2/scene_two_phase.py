from manim import *
from generator import (
    calculate_physics_data,
    build_coils,
    build_rotor,
)
import math


class TwoPhaseScene(Scene):
    def construct(self):
        # --- CONSTANTS ---
        DISK_RADIUS = 3.0
        MAGNET_RADIUS = 0.8
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS

        NUM_MAGNETS = 2
        # We manually build coils to control placement
        # Coil A: Top (PI/2)
        # Coil B: Right (0)

        ROTATION_SPEED = 0.5 * PI
        TOTAL_TIME = 8.0

        # --- PHYSICS CALCULATION ---
        # Phase A (Top Coil)
        _, voltage_data_a = calculate_physics_data(
            num_magnets=NUM_MAGNETS,
            rotation_speed=ROTATION_SPEED,
            total_time=TOTAL_TIME,
            magnet_path_radius=MAGNET_PATH_RADIUS,
            magnet_radius=MAGNET_RADIUS,
            coil_theta=PI / 2.0,
        )

        # Phase B (Right Coil - 3 o'clock - Angle 0)
        _, voltage_data_b = calculate_physics_data(
            num_magnets=NUM_MAGNETS,
            rotation_speed=ROTATION_SPEED,
            total_time=TOTAL_TIME,
            magnet_path_radius=MAGNET_PATH_RADIUS,
            magnet_radius=MAGNET_RADIUS,
            coil_theta=0,
        )

        # Determine Max Voltage for Graph Scaling
        # Scale to peak ~10V
        raw_max = max(
            [abs(v[1]) for v in voltage_data_a] + [abs(v[1]) for v in voltage_data_b]
        )
        scale_factor = 10.0 / raw_max if raw_max != 0 else 1.0

        voltage_data_a = [(t, v * scale_factor) for t, v in voltage_data_a]
        voltage_data_b = [(t, v * scale_factor) for t, v in voltage_data_b]

        # Calculate Combined Voltage Squared (Power)
        power_data = []
        for i in range(len(voltage_data_a)):
            t = voltage_data_a[i][0]
            v_a = voltage_data_a[i][1]
            v_b = voltage_data_b[i][1]
            p = (v_a**2) + (v_b**2)
            power_data.append((t, p))

        max_voltage = 12.0
        max_power = max([p[1] for p in power_data]) * 1.1

        # --- VISUAL SETUP ---

        # 1. GENERATOR (LEFT SIDE)
        # Build Rotor
        rotor_group = build_rotor(
            NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS
        )

        # Build Coils Manually
        # Coil A
        coil_a_pos = np.array(
            [
                MAGNET_PATH_RADIUS * math.cos(PI / 2),
                MAGNET_PATH_RADIUS * math.sin(PI / 2),
                0,
            ]
        )
        base_circle_a = Circle(radius=MAGNET_RADIUS, color=YELLOW, stroke_width=6)
        coil_a = DashedVMobject(base_circle_a, num_dashes=12).move_to(coil_a_pos)
        label_a = Text("A", font_size=24).move_to(coil_a.get_center())

        # Coil B
        coil_b_pos = np.array(
            [MAGNET_PATH_RADIUS * math.cos(0), MAGNET_PATH_RADIUS * math.sin(0), 0]
        )
        base_circle_b = Circle(radius=MAGNET_RADIUS, color=BLUE, stroke_width=6)
        coil_b = DashedVMobject(base_circle_b, num_dashes=12).move_to(coil_b_pos)
        label_b = Text("B", font_size=24).move_to(coil_b.get_center())

        coils_group = VGroup(coil_a, label_a, coil_b, label_b)

        # Group All
        generator_group = VGroup(coils_group, rotor_group)

        # Position: Move to LEFT side, slightly up
        generator_group.to_edge(LEFT, buff=1.0).shift(UP * 0.5)

        # 2. GRAPH (RIGHT SIDE)
        voltage_ax = (
            Axes(
                x_range=[0, TOTAL_TIME, 1],
                y_range=[-max_voltage, max_voltage, 5],
                x_length=6,
                y_length=3.5,
                axis_config={"include_tip": False, "color": GREY},
            )
            .to_edge(RIGHT, buff=0.5)
            .to_edge(UP, buff=1.0)
        )

        zero_line = voltage_ax.get_horizontal_line(
            voltage_ax.c2p(TOTAL_TIME, 0),
            color=GREY,
            stroke_width=1,
        ).set_stroke(opacity=0.5)

        voltage_label = voltage_ax.get_y_axis_label(
            Text("Voltage", font_size=24).rotate(90 * DEGREES)
        ).next_to(voltage_ax, LEFT, buff=0.1)

        voltage_title = Text("Two Phase Output", font_size=32).next_to(voltage_ax, UP)

        # Legend
        legend_a = (
            Text("Phase A", font_size=20, color=YELLOW)
            .next_to(voltage_title, DOWN)
            .shift(LEFT * 1.5)
        )
        legend_b = (
            Text("Phase B", font_size=20, color=BLUE)
            .next_to(voltage_title, DOWN)
            .shift(RIGHT * 1.5)
        )

        # Power Graph (Bottom Right - Tiny)
        power_ax = (
            Axes(
                x_range=[0, TOTAL_TIME, 1],
                y_range=[0, max_power, max_power / 2],
                x_length=6,
                y_length=2.0,
                axis_config={"include_tip": False, "color": GREY},
            )
            .to_edge(RIGHT, buff=0.5)
            .to_edge(DOWN, buff=0.5)
        )

        power_label = power_ax.get_y_axis_label(
            Text("Power (V²)", font_size=20).rotate(90 * DEGREES)
        ).next_to(power_ax, LEFT, buff=0.1)

        graph_group = VGroup(
            voltage_ax,
            voltage_label,
            voltage_title,
            zero_line,
            legend_a,
            legend_b,
            power_ax,
            power_label,
        )

        # --- ANIMATION SETUP ---

        self.add(generator_group, graph_group)

        # Time Tracker
        time_tracker = ValueTracker(0)

        # A. Rotor Rotation
        self.last_angle = 0

        def update_rotor(mob):
            t = time_tracker.get_value()
            target_angle = -ROTATION_SPEED * t
            angle_delta = target_angle - self.last_angle
            mob.rotate(angle_delta, about_point=generator_group.get_center())
            self.last_angle = target_angle

        rotor_group.add_updater(update_rotor)

        # B. Graph Updaters

        # Phase A
        points_a = [voltage_ax.c2p(t, v) for t, v in voltage_data_a]
        curve_a = (
            VMobject()
            .set_points_as_corners([points_a[0]])
            .set_color(YELLOW)
            .set_stroke(width=3)
        )
        dot_a = Dot(color=YELLOW).scale(0.8)

        # Phase B
        points_b = [voltage_ax.c2p(t, v) for t, v in voltage_data_b]
        curve_b = (
            VMobject()
            .set_points_as_corners([points_b[0]])
            .set_color(BLUE)
            .set_stroke(width=3)
        )
        dot_b = Dot(color=BLUE).scale(0.8)

        # Power Curve
        points_p = [power_ax.c2p(t, p) for t, p in power_data]
        curve_p = (
            VMobject()
            .set_points_as_corners([points_p[0]])
            .set_color(RED)
            .set_stroke(width=3)
        )
        dot_p = Dot(color=RED).scale(0.6)

        def update_graph_a(mob):
            t = time_tracker.get_value()
            idx = int((t / TOTAL_TIME) * len(points_a))
            idx = max(0, min(idx, len(points_a) - 1))
            mob.set_points_as_corners(points_a[: idx + 1])
            if idx < len(points_a):
                dot_a.move_to(points_a[idx])

        def update_graph_b(mob):
            t = time_tracker.get_value()
            idx = int((t / TOTAL_TIME) * len(points_b))
            idx = max(0, min(idx, len(points_b) - 1))
            mob.set_points_as_corners(points_b[: idx + 1])
            if idx < len(points_b):
                dot_b.move_to(points_b[idx])

        def update_graph_p(mob):
            t = time_tracker.get_value()
            idx = int((t / TOTAL_TIME) * len(points_p))
            idx = max(0, min(idx, len(points_p) - 1))
            mob.set_points_as_corners(points_p[: idx + 1])
            if idx < len(points_p):
                dot_p.move_to(points_p[idx])

        curve_a.add_updater(update_graph_a)
        curve_b.add_updater(update_graph_b)
        curve_p.add_updater(update_graph_p)

        self.add(curve_a, dot_a, curve_b, dot_b, curve_p, dot_p)

        # --- ACTION ---
        self.wait(0.5)

        self.play(
            time_tracker.animate.set_value(TOTAL_TIME),
            run_time=TOTAL_TIME,
            rate_func=linear,
        )

        self.wait(1)
