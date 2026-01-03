from manim import *
from generator import build_rotor, calculate_sine_voltage_trace
import math
from dataclasses import dataclass
from typing import Callable, List, Tuple
import numpy as np


@dataclass
class CoilConfig:
    """Configuration for a single coil"""
    name: str
    color: str
    motion_profile: Callable[[float], float]  # time -> angular_offset_from_12_oclock (radians)


class OneToTwoPhaseScene(Scene):
    """
    Shows the transition from single-phase to two-phase power.

    Visual elements:
    - Generator with rotating magnets (left side)
    - Phase A coil at 12 o'clock (stationary, BLUE)
    - Phase B coil that fades in at t=3, then moves to 3 o'clock (90 degrees)
    - Voltage graph showing both phase curves (right side)

    Animation sequence:
    1. t=0-3s: Single coil (Phase A) at 12 o'clock, single sine wave
    2. t=3s: Phase B fades in at 12 o'clock
    3. t=3-6s: Phase B smoothly moves from 12 o'clock to 3 o'clock (90 degrees clockwise)
    4. t=6-10s: Both coils fixed, showing 90-degree phase offset

    Total simulation time: 10 seconds
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
        SIMULATION_TIME = 10.0
        PHYSICS_STEPS = 6000  # Fixed number of steps for smooth curves
        dt = SIMULATION_TIME / PHYSICS_STEPS

        # Phase B timing
        FADE_IN_TIME = 3.0
        MOVE_START = 3.0
        MOVE_END = 6.0
        MOVE_DURATION = MOVE_END - MOVE_START
        TARGET_OFFSET = 90 * DEGREES  # 3 o'clock position (90 degrees clockwise from top)

        # ============================================================
        # COIL MOTION PROFILES
        # ============================================================

        def stationary_profile(t):
            """Coil A stays at 12 o'clock"""
            return 0.0

        def phase_b_profile(t):
            """Phase B: starts at 12 o'clock, moves to 3 o'clock (90 degrees) between t=3 and t=6"""
            if t < MOVE_START:
                return 0.0
            elif t < MOVE_END:
                # Smooth interpolation using smooth_step (ease in/out)
                alpha = (t - MOVE_START) / MOVE_DURATION
                # Use smoothstep for nice easing: 3x^2 - 2x^3
                smooth_alpha = alpha * alpha * (3 - 2 * alpha)
                return smooth_alpha * TARGET_OFFSET
            else:
                return TARGET_OFFSET

        # ============================================================
        # COIL CONFIGURATIONS
        # ============================================================
        coils_config = [
            CoilConfig(name="A", color=BLUE, motion_profile=stationary_profile),
            CoilConfig(name="B", color=ORANGE, motion_profile=phase_b_profile),
        ]

        # ============================================================
        # PHYSICS CALCULATION (Sinusoidal Model)
        # ============================================================
        print(f"Calculating physics for {len(coils_config)} coil(s)...")

        coil_data = {}  # coil_name -> List[(time, voltage)]

        for coil_cfg in coils_config:
            def make_coil_angle_func(motion_profile):
                def coil_angle_func(t):
                    offset = motion_profile(t)
                    return (PI / 2.0) - offset
                return coil_angle_func

            voltage_trace = calculate_sine_voltage_trace(
                num_magnets=NUM_MAGNETS,
                rotation_speed=ROTATION_SPEED,
                total_time=SIMULATION_TIME,
                coil_angle_func=make_coil_angle_func(coil_cfg.motion_profile),
                amplitude=10.0,
                steps=PHYSICS_STEPS,
            )

            coil_data[coil_cfg.name] = voltage_trace
            print(f"  Coil {coil_cfg.name}: {len(voltage_trace)} data points")

        # Find max voltage for graph scaling
        max_voltage = 0.0
        for trace in coil_data.values():
            for _, v in trace:
                max_voltage = max(max_voltage, abs(v))

        max_voltage *= 1.1  # Add padding

        # ============================================================
        # VISUAL ELEMENTS
        # ============================================================

        # --- GENERATOR (Left side) ---
        rotor_group = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

        # Stator (static outer ring)
        stator = Circle(
            radius=DISK_RADIUS + 0.3,
            color=GRAY,
            stroke_width=8,
            stroke_opacity=0.5
        )

        # Build coil visual objects
        coil_mobjects = VGroup()
        coil_labels = VGroup()

        for coil_cfg in coils_config:
            # Initial position (all start at 12 o'clock)
            initial_offset = coil_cfg.motion_profile(0)
            initial_angle = (PI / 2.0) - initial_offset

            pos = np.array([
                MAGNET_PATH_RADIUS * math.cos(initial_angle),
                MAGNET_PATH_RADIUS * math.sin(initial_angle),
                0
            ])

            # Create coil visual (rectangle per scene_linear_to_circular.py pattern)
            coil = Rectangle(
                width=MAGNET_RADIUS * 1.5,
                height=MAGNET_RADIUS * 2.0,
                color=coil_cfg.color,
                stroke_width=6,
                fill_opacity=0
            )
            coil.rotate(initial_angle - PI/2)  # Rotate so long side is tangent to circle
            coil.move_to(pos)

            # Create label
            label = Text(coil_cfg.name, font_size=28, color=coil_cfg.color).next_to(coil, UP, buff=0.15)

            # Store for later reference
            coil.coil_name = coil_cfg.name
            coil.motion_profile = coil_cfg.motion_profile
            coil.current_angle = initial_angle  # Track angle for updater rotation
            label.coil_name = coil_cfg.name

            coil_mobjects.add(coil)
            coil_labels.add(label)

        # Phase B starts hidden (use set_stroke to avoid enabling fill)
        coil_b = coil_mobjects[1]
        label_b = coil_labels[1]
        coil_b.set_stroke(opacity=0)
        label_b.set_opacity(0)

        generator_group = VGroup(stator, coil_mobjects, rotor_group, coil_labels)
        generator_group.to_edge(LEFT, buff=1.0)
        disk_center = rotor_group.get_center()

        # --- VOLTAGE GRAPH (Right side) ---
        voltage_ax = Axes(
            x_range=[0, SIMULATION_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage / 2],
            x_length=6,
            y_length=4.5,
            axis_config={"include_tip": False, "color": GREY},
        ).to_edge(RIGHT, buff=0.5)

        voltage_label = voltage_ax.get_y_axis_label(
            Text("Voltage", font_size=24).rotate(90 * DEGREES)
        )
        voltage_title = Text("Induced Voltage", font_size=32).next_to(voltage_ax, UP)

        graph_group = VGroup(voltage_ax, voltage_label, voltage_title)

        # --- VOLTAGE CURVES ---
        curves = VGroup()
        for coil_cfg in coils_config:
            curve = VMobject().set_color(coil_cfg.color).set_stroke(width=2).set_fill(opacity=0)
            curve.coil_name = coil_cfg.name
            curves.add(curve)

        # Phase B curve starts hidden (use set_stroke to avoid enabling fill)
        curve_b = curves[1]
        curve_b.set_stroke(opacity=0)

        # ============================================================
        # UPDATERS
        # ============================================================
        time_tracker = ValueTracker(0)

        # Rotor rotation updater
        last_t = [0.0]

        def update_rotor(mob, dt):
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t[0]

            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center)
                last_t[0] = t_now

        rotor_group.add_updater(update_rotor)

        # Coil position updaters
        for coil in coil_mobjects:
            def update_coil_position(mob, profile=coil.motion_profile, start_angle=coil.current_angle):
                t = time_tracker.get_value()
                offset = profile(t)
                new_angle = (PI / 2.0) - offset

                delta_angle = new_angle - mob.current_angle
                if delta_angle != 0:
                    mob.rotate(delta_angle, about_point=disk_center)
                    mob.current_angle = new_angle

            coil.add_updater(update_coil_position)

        # Label position updaters (follow coils)
        for label in coil_labels:
            def update_label_position(mob, target_name=label.coil_name):
                for coil in coil_mobjects:
                    if coil.coil_name == target_name:
                        mob.next_to(coil, UP, buff=0.15)
                        break

            label.add_updater(update_label_position)

        # Voltage curve updaters (ACCUMULATING from t=0)
        for curve in curves:
            def update_curve(mob, coil_name=curve.coil_name):
                t_now = time_tracker.get_value()

                trace = coil_data[coil_name]

                idx_end = int(t_now / dt)
                idx_end = min(len(trace) - 1, max(0, idx_end))

                visible = trace[0:idx_end + 1]

                SUBSAMPLE_RATE = 3
                visible_subsampled = visible[::SUBSAMPLE_RATE]

                if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                    visible_subsampled.append(visible[-1])

                points = []
                for t_val, v_val in visible_subsampled:
                    x_graph = t_val
                    points.append(voltage_ax.c2p(x_graph, v_val))

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

        # Add all objects
        self.add(generator_group, graph_group, curves)

        # Phase 1: Single coil (Phase A only) - run for 3 seconds
        self.play(
            time_tracker.animate.set_value(FADE_IN_TIME),
            run_time=FADE_IN_TIME,
            rate_func=linear
        )

        # Phase B fades in at t=3
        coil_b.set_stroke(opacity=1)  # Use set_stroke to keep fill disabled
        label_b.set_opacity(1)
        curve_b.set_stroke(opacity=1)  # Use set_stroke to avoid enabling fill
        self.play(
            FadeIn(coil_b),
            FadeIn(label_b),
            run_time=0.5
        )

        # Phase 2: Phase B moves to 3 o'clock (t=3 to t=6)
        # Continue simulation - Phase B will move via its motion profile
        self.play(
            time_tracker.animate.set_value(MOVE_END),
            run_time=(MOVE_END - FADE_IN_TIME),
            rate_func=linear
        )

        # Phase 3: Both coils fixed, showing 90-degree phase offset (t=6 to t=10)
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=(SIMULATION_TIME - MOVE_END),
            rate_func=linear
        )

        # Final wait
        self.wait(1)
