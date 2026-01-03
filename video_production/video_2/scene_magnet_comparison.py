from manim import *
from generator import build_rotor, calculate_sine_voltage_trace
import math
from dataclasses import dataclass
import numpy as np


class MagnetComparisonScene(Scene):
    """
    Demonstrates the difference between 1 magnet and 2 magnets with two coils at 90 degrees apart.

    Visual elements:
    - Left side: Generator with two square coils at 12 o'clock (BLUE) and 3 o'clock (ORANGE)
    - Right side: Two vertically stacked graphs (one per coil)

    Animation sequence:
    1. Phase 1 (5.5s): 1 magnet rotating, both graphs draw voltage traces showing 45 degree phase offset
    2. Transition (1s): Fade out 1-magnet rotor, fade in 2-magnet rotor, clear graphs
    3. Phase 2 (5.5s): 2 magnets rotating, showing 90 degree phase offset and doubled frequency
    4. Final wait (1s)

    Key physics:
    - 1 magnet: coils at 90 degrees apart see 45 degree phase offset (half the physical separation)
    - 2 magnets: coils at 90 degrees apart see 90 degree phase offset (true quadrature)
    - 2 magnets also doubles the frequency (2 cycles per rotation vs 1)
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 3.0
        MAGNET_RADIUS = 0.8
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        ROTATION_SPEED = 0.5 * PI  # rad/s, clockwise

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        SIMULATION_TIME = 5.5  # Each phase duration
        PHYSICS_STEPS = 3300
        dt = SIMULATION_TIME / PHYSICS_STEPS

        # ============================================================
        # COIL CONFIGURATIONS
        # ============================================================
        # Coil A at 12 o'clock (0 degrees offset)
        # Coil B at 3 o'clock (90 degrees offset, clockwise from top)
        coils_config = [
            {"name": "A", "color": BLUE, "position_offset": 0 * DEGREES},      # 12 o'clock
            {"name": "B", "color": ORANGE, "position_offset": 90 * DEGREES},   # 3 o'clock
        ]

        # ============================================================
        # PHYSICS CALCULATION
        # ============================================================
        print("MagnetComparison: Calculating physics...")

        # Data for 1 magnet configuration
        one_magnet_data = {}
        for coil_cfg in coils_config:
            coil_angle_static = (PI / 2.0) - coil_cfg["position_offset"]
            voltage_trace = calculate_sine_voltage_trace(
                num_magnets=1,
                rotation_speed=ROTATION_SPEED,
                total_time=SIMULATION_TIME,
                coil_angle_static=coil_angle_static,
                amplitude=10.0,
                steps=PHYSICS_STEPS,
            )
            one_magnet_data[coil_cfg["name"]] = voltage_trace
            print(f"  1 magnet - Coil {coil_cfg['name']}: {len(voltage_trace)} points")

        # Data for 2 magnet configuration
        two_magnet_data = {}
        for coil_cfg in coils_config:
            coil_angle_static = (PI / 2.0) - coil_cfg["position_offset"]
            voltage_trace = calculate_sine_voltage_trace(
                num_magnets=2,
                rotation_speed=ROTATION_SPEED,
                total_time=SIMULATION_TIME,
                coil_angle_static=coil_angle_static,
                amplitude=10.0,
                steps=PHYSICS_STEPS,
            )
            two_magnet_data[coil_cfg["name"]] = voltage_trace
            print(f"  2 magnets - Coil {coil_cfg['name']}: {len(voltage_trace)} points")

        # Find max voltage for graph scaling (use both configurations)
        max_voltage = 0.0
        for trace in list(one_magnet_data.values()) + list(two_magnet_data.values()):
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
            # Coil size matches magnet diameter to capture full flux
            coil = Rectangle(
                width=magnet_radius * 2.0,
                height=magnet_radius * 2.0,
                color=coil_color,
                stroke_width=6
            )
            coil.rotate(coil_angle - PI/2)
            coil.move_to(pos)
            return coil

        # ============================================================
        # VISUAL ELEMENTS - GENERATOR (Left side)
        # ============================================================

        # Build 1-magnet rotor (Phase 1)
        rotor_1_magnet = build_rotor(1, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)
        # Make disk completely invisible
        rotor_1_magnet[0].set_opacity(0)

        # Build 2-magnet rotor (Phase 2)
        rotor_2_magnets = build_rotor(2, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)
        # Make disk completely invisible
        rotor_2_magnets[0].set_opacity(0)

        # Stator (static outer ring) - explicitly no fill
        stator = Circle(
            radius=DISK_RADIUS + 0.3,
            color=GRAY,
            stroke_width=8,
            stroke_opacity=0.5,
            fill_opacity=0
        )

        # Build coil visual objects
        coil_mobjects = VGroup()
        coil_labels = VGroup()

        for coil_cfg in coils_config:
            angle = (PI / 2.0) - coil_cfg["position_offset"]
            coil = build_square_coil(angle, coil_cfg["color"], MAGNET_PATH_RADIUS, MAGNET_RADIUS)
            label = Text(coil_cfg["name"], font_size=28, color=coil_cfg["color"]).next_to(coil, UP, buff=0.15)
            coil_mobjects.add(coil)
            coil_labels.add(label)

        # Scale and position all generator elements together
        # We keep rotors separate from static elements for proper z-ordering

        # Create a temporary group for positioning to find target center
        positioning_group = VGroup(stator.copy(), rotor_1_magnet.copy())
        positioning_group.scale(0.55)
        positioning_group.to_edge(LEFT, buff=0.8)
        target_center = positioning_group.get_center()

        # Group ALL generator elements together for unified scaling and positioning
        # This ensures coils scale around the same center as the rotor
        all_generator_elements = VGroup(
            stator, rotor_1_magnet, rotor_2_magnets, coil_mobjects, coil_labels
        )
        all_generator_elements.scale(0.55)
        all_generator_elements.move_to(target_center)

        # Rebuild labels to be properly positioned relative to their coils after scaling
        for i, coil_cfg in enumerate(coils_config):
            coil_labels[i].next_to(coil_mobjects[i], UP, buff=0.1)

        # Hide the 2-magnet rotor initially (will be shown in Phase 2)
        rotor_2_magnets.set_opacity(0)

        disk_center = rotor_1_magnet.get_center()

        # Generator group for reference (positioning magnet label)
        generator_group = VGroup(stator, rotor_1_magnet, coil_mobjects, coil_labels)

        # Magnet count label
        magnet_label = Text("1 Magnet", font_size=28, color=WHITE)
        magnet_label.next_to(generator_group, DOWN, buff=0.3)

        # ============================================================
        # VISUAL ELEMENTS - GRAPHS (Right side, stacked)
        # ============================================================
        graph_width = 6.5
        graph_height = 2.0

        # Top graph: Coil A (12 o'clock)
        ax_coil_a = Axes(
            x_range=[0, SIMULATION_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )
        coil_a_title = Text("Coil A (12 o'clock)", font_size=22, color=BLUE)
        coil_a_title.next_to(ax_coil_a, UP, buff=0.1)
        graph_a_group = VGroup(ax_coil_a, coil_a_title)

        # Bottom graph: Coil B (3 o'clock)
        ax_coil_b = Axes(
            x_range=[0, SIMULATION_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )
        coil_b_title = Text("Coil B (3 o'clock)", font_size=22, color=ORANGE)
        coil_b_title.next_to(ax_coil_b, UP, buff=0.1)
        graph_b_group = VGroup(ax_coil_b, coil_b_title)

        # Stack graphs vertically
        graphs_group = VGroup(graph_a_group, graph_b_group)
        graphs_group.arrange(DOWN, buff=0.5)
        graphs_group.to_edge(RIGHT, buff=0.4)

        # ============================================================
        # VOLTAGE CURVES
        # ============================================================
        curve_a = VMobject().set_color(BLUE).set_stroke(width=2.5)
        curve_b = VMobject().set_color(ORANGE).set_stroke(width=2.5)
        curves = VGroup(curve_a, curve_b)

        # Store current data source (will be swapped during transition)
        current_data = {"A": one_magnet_data["A"], "B": one_magnet_data["B"]}

        # ============================================================
        # UPDATERS
        # ============================================================
        time_tracker = ValueTracker(0)

        # Rotor rotation updater for 1-magnet rotor
        last_t_1 = [0.0]

        def update_rotor_1(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t_1[0]
            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center)
                last_t_1[0] = t_now

        rotor_1_magnet.add_updater(update_rotor_1)

        # Rotor rotation updater for 2-magnet rotor
        last_t_2 = [0.0]

        def update_rotor_2(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t_2[0]
            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center)
                last_t_2[0] = t_now

        # Curve updater for Coil A
        def update_curve_a(mob):
            t_now = time_tracker.get_value()
            trace = current_data["A"]

            idx_end = int(t_now / dt)
            idx_end = min(len(trace) - 1, max(0, idx_end))

            visible = trace[0:idx_end + 1]

            SUBSAMPLE_RATE = 3
            visible_subsampled = visible[::SUBSAMPLE_RATE]

            if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                visible_subsampled.append(visible[-1])

            points = [ax_coil_a.c2p(t_val, v_val) for t_val, v_val in visible_subsampled]

            if len(points) > 1:
                mob.set_points_as_corners(points)
            elif len(points) == 1:
                mob.set_points_as_corners([points[0], points[0]])

        curve_a.add_updater(update_curve_a)

        # Curve updater for Coil B
        def update_curve_b(mob):
            t_now = time_tracker.get_value()
            trace = current_data["B"]

            idx_end = int(t_now / dt)
            idx_end = min(len(trace) - 1, max(0, idx_end))

            visible = trace[0:idx_end + 1]

            SUBSAMPLE_RATE = 3
            visible_subsampled = visible[::SUBSAMPLE_RATE]

            if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                visible_subsampled.append(visible[-1])

            points = [ax_coil_b.c2p(t_val, v_val) for t_val, v_val in visible_subsampled]

            if len(points) > 1:
                mob.set_points_as_corners(points)
            elif len(points) == 1:
                mob.set_points_as_corners([points[0], points[0]])

        curve_b.add_updater(update_curve_b)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # Add all objects with proper z-order:
        # 1. Stator (background)
        # 2. Rotors (behind coils)
        # 3. Coils and labels (on top of rotors)
        # 4. Other elements
        self.add(stator)
        self.add(rotor_1_magnet)
        self.add(rotor_2_magnets)
        self.add(coil_mobjects)
        self.add(coil_labels)
        self.add(graphs_group, curves, magnet_label)

        # Phase 1: 1 magnet (5.5 seconds)
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=SIMULATION_TIME,
            rate_func=linear
        )

        # Transition: Fade out 1-magnet, fade in 2-magnets, clear graphs
        rotor_1_magnet.remove_updater(update_rotor_1)
        curve_a.remove_updater(update_curve_a)
        curve_b.remove_updater(update_curve_b)

        # Reset time tracker
        time_tracker.set_value(0)
        last_t_2[0] = 0.0

        # Clear curves
        curve_a.set_points_as_corners([ax_coil_a.c2p(0, 0), ax_coil_a.c2p(0, 0)])
        curve_b.set_points_as_corners([ax_coil_b.c2p(0, 0), ax_coil_b.c2p(0, 0)])

        # Update data source to 2-magnet data
        current_data["A"] = two_magnet_data["A"]
        current_data["B"] = two_magnet_data["B"]

        # Update label
        new_magnet_label = Text("2 Magnets", font_size=28, color=WHITE)
        new_magnet_label.next_to(generator_group, DOWN, buff=0.3)

        # Transition animation: swap rotors
        # First set 2-magnet rotor visible (but keep disk invisible)
        rotor_2_magnets.set_opacity(1)
        rotor_2_magnets[0].set_opacity(0)  # Keep disk invisible

        self.play(
            FadeOut(rotor_1_magnet),
            FadeIn(rotor_2_magnets),
            Transform(magnet_label, new_magnet_label),
            run_time=1.0
        )

        # Completely remove the 1-magnet rotor from the scene to prevent any artifacts
        self.remove(rotor_1_magnet)

        # Ensure coils and labels stay on top after rotor transition
        self.bring_to_front(coil_mobjects)
        self.bring_to_front(coil_labels)

        # Re-add updaters for phase 2
        rotor_2_magnets.add_updater(update_rotor_2)
        curve_a.add_updater(update_curve_a)
        curve_b.add_updater(update_curve_b)

        # Phase 2: 2 magnets (5.5 seconds)
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=SIMULATION_TIME,
            rate_func=linear
        )

        # Final wait
        self.wait(1)
