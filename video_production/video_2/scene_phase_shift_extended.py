from manim import *
from generator import build_rotor, calculate_sine_voltage_trace, calculate_sinusoidal_flux
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


class PhaseShiftExtendedScene(Scene):
    """
    Extended phase shift animation with 3 phases:

    PHASE 1 (~8 seconds):
    - 3 coils (A, B, C) start at 12 o'clock
    - B moves to 4 o'clock (120 deg), C moves to 8 o'clock (240 deg)
    - Single graph on the right shows all 3 overlaid voltage traces
    - Uses localized sinusoidal flux model (PI/4 influence width)

    PHASE 2 (brief transition):
    - Single graph transforms into 3 separate vertically-stacked graphs
    - Each graph is 1/3 height and shows one coil's voltage
    - Labels with coil name and color

    PHASE 3 (8 seconds steady-state):
    - Rotor continues spinning at same speed
    - Coils fixed at final positions (A at 12 o'clock, B at 4 o'clock, C at 8 o'clock)
    - Each graph shows a scrolling window (~2-3 seconds history)
    - Phase relationships: A=0 deg, B=120 deg lagging, C=240 deg lagging
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
        PHASE_1_TIME = 8.0  # Phase 1 duration (coil separation)
        PHASE_3_TIME = 8.0  # Phase 3 duration (steady-state scrolling)
        SCROLL_WINDOW = 2.5  # Scrolling window width in seconds
        PHYSICS_STEPS = 5000  # Fixed number of steps for smooth curves
        dt_phase1 = PHASE_1_TIME / PHYSICS_STEPS

        # ============================================================
        # COIL MOTION PROFILES (PHASE 1)
        # ============================================================
        def stationary_profile(t):
            """Coil stays at 12 o'clock"""
            return 0.0

        def moving_1x_profile(t):
            """Coil moves to target position over 8 seconds"""
            MOVE_START = 2.0
            MOVE_DURATION = 5.0
            TARGET_OFFSET = 120 * DEGREES  # clockwise from top (4 o'clock position)

            if t < MOVE_START:
                return 0.0
            elif t < MOVE_START + MOVE_DURATION:
                alpha = (t - MOVE_START) / MOVE_DURATION
                return alpha * TARGET_OFFSET
            else:
                return TARGET_OFFSET

        def moving_2x_profile(t):
            """Coil moves twice as fast/far as 1x coil"""
            return 2.0 * moving_1x_profile(t)

        # ============================================================
        # COIL CONFIGURATIONS
        # ============================================================
        coils_config = [
            CoilConfig(name="A", color=BLUE, motion_profile=stationary_profile),
            CoilConfig(name="B", color=ORANGE, motion_profile=moving_1x_profile),
            CoilConfig(name="C", color=GREEN, motion_profile=moving_2x_profile),
        ]

        # ============================================================
        # PHYSICS CALCULATION (Phase 1 - Moving Coils)
        # ============================================================
        print(f"Calculating physics for Phase 1 ({len(coils_config)} coils)...")

        coil_data_phase1 = {}  # coil_name -> List[(time, voltage)]

        for coil_cfg in coils_config:
            def make_coil_angle_func(motion_profile):
                def coil_angle_func(t):
                    offset = motion_profile(t)
                    return (PI / 2.0) - offset
                return coil_angle_func

            voltage_trace = calculate_sine_voltage_trace(
                num_magnets=NUM_MAGNETS,
                rotation_speed=ROTATION_SPEED,
                total_time=PHASE_1_TIME,
                coil_angle_func=make_coil_angle_func(coil_cfg.motion_profile),
                amplitude=10.0,
                steps=PHYSICS_STEPS,
            )

            coil_data_phase1[coil_cfg.name] = voltage_trace
            print(f"  Coil {coil_cfg.name}: {len(voltage_trace)} data points")

        # Find max voltage for graph scaling
        max_voltage = 0.0
        for trace in coil_data_phase1.values():
            for _, v in trace:
                max_voltage = max(max_voltage, abs(v))
        max_voltage *= 1.1  # Add padding

        # ============================================================
        # PHASE 3 SETUP - Real-time voltage calculation
        # ============================================================
        # Final coil positions (angular offset from 12 o'clock, clockwise)
        FINAL_COIL_OFFSETS = {
            "A": 0.0,           # 12 o'clock
            "B": 120 * DEGREES, # 4 o'clock
            "C": 240 * DEGREES, # 8 o'clock
        }

        # Convert to coil angles (radians, 0=right, PI/2=top)
        FINAL_COIL_ANGLES = {
            name: (PI / 2.0) - offset
            for name, offset in FINAL_COIL_OFFSETS.items()
        }

        # Magnet setup for real-time calculation
        # Magnets start evenly spaced, first one at top (PI/2)
        MAGNET_ANGLES_START = []
        MAGNET_POLARITIES = []
        for i in range(NUM_MAGNETS):
            theta = (PI / 2.0) - (i * (2 * PI / NUM_MAGNETS))
            MAGNET_ANGLES_START.append(theta)
            MAGNET_POLARITIES.append(i % 2 == 0)  # Alternating N/S

        # Amplitude for voltage calculation (matches Phase 1)
        VOLTAGE_AMPLITUDE = 10.0

        print(f"Phase 3 will use real-time voltage calculation based on rotor angle")

        # ============================================================
        # VISUAL ELEMENTS - GENERATOR (Left side)
        # ============================================================
        rotor_group = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

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
            initial_offset = coil_cfg.motion_profile(0)
            initial_angle = (PI / 2.0) - initial_offset

            pos = np.array([
                MAGNET_PATH_RADIUS * math.cos(initial_angle),
                MAGNET_PATH_RADIUS * math.sin(initial_angle),
                0
            ])

            coil = Rectangle(
                width=MAGNET_RADIUS * 2.0,
                height=MAGNET_RADIUS * 2.0,
                color=coil_cfg.color,
                stroke_width=6
            )
            coil.rotate(initial_angle - PI/2)
            coil.move_to(pos)

            label = Text(coil_cfg.name, font_size=28, color=coil_cfg.color).next_to(coil, UP, buff=0.15)

            coil.coil_name = coil_cfg.name
            coil.motion_profile = coil_cfg.motion_profile
            coil.current_angle = initial_angle
            label.coil_name = coil_cfg.name

            coil_mobjects.add(coil)
            coil_labels.add(label)

        generator_group = VGroup(stator, coil_mobjects, rotor_group, coil_labels)
        generator_group.to_edge(LEFT, buff=1.0)
        disk_center = rotor_group.get_center()

        # ============================================================
        # VISUAL ELEMENTS - SINGLE GRAPH (Phase 1)
        # ============================================================
        voltage_ax = Axes(
            x_range=[0, PHASE_1_TIME, 1],
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

        # Voltage curves for Phase 1
        curves_phase1 = VGroup()
        for coil_cfg in coils_config:
            curve = VMobject().set_color(coil_cfg.color).set_stroke(width=2)
            curve.coil_name = coil_cfg.name
            curves_phase1.add(curve)

        # ============================================================
        # VISUAL ELEMENTS - THREE STACKED GRAPHS (Phase 2/3)
        # ============================================================
        # Create 3 smaller axes stacked vertically
        stacked_axes = VGroup()
        stacked_labels = VGroup()
        GRAPH_HEIGHT = 1.4
        GRAPH_WIDTH = 6
        GRAPH_SPACING = 0.3

        for i, coil_cfg in enumerate(coils_config):
            ax = Axes(
                x_range=[0, SCROLL_WINDOW, 0.5],
                y_range=[-max_voltage, max_voltage, max_voltage],
                x_length=GRAPH_WIDTH,
                y_length=GRAPH_HEIGHT,
                axis_config={"include_tip": False, "color": GREY},
            )
            ax.coil_name = coil_cfg.name
            ax.coil_color = coil_cfg.color

            # Label for each graph
            label = Text(f"Coil {coil_cfg.name}", font_size=20, color=coil_cfg.color)
            label.coil_name = coil_cfg.name

            stacked_axes.add(ax)
            stacked_labels.add(label)

        # Position stacked graphs vertically
        stacked_axes.arrange(DOWN, buff=GRAPH_SPACING)
        stacked_axes.to_edge(RIGHT, buff=0.5)

        # Position labels to the left of each axis
        for ax, label in zip(stacked_axes, stacked_labels):
            label.next_to(ax, LEFT, buff=0.2)

        stacked_graphs_group = VGroup(stacked_axes, stacked_labels)

        # Scrolling curves for Phase 3
        curves_phase3 = VGroup()
        for coil_cfg in coils_config:
            curve = VMobject().set_color(coil_cfg.color).set_stroke(width=2.5)
            curve.coil_name = coil_cfg.name
            curves_phase3.add(curve)

        # ============================================================
        # UPDATERS - PHASE 1
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

        # Coil position updaters
        for coil in coil_mobjects:
            def update_coil_position(mob):
                t = time_tracker.get_value()
                offset = mob.motion_profile(t)
                new_angle = (PI / 2.0) - offset

                delta_angle = new_angle - mob.current_angle
                if delta_angle != 0:
                    mob.rotate(delta_angle, about_point=disk_center)
                    mob.current_angle = new_angle

            coil.add_updater(update_coil_position)

        # Label position updaters
        for label in coil_labels:
            def update_label_position(mob):
                for coil in coil_mobjects:
                    if coil.coil_name == mob.coil_name:
                        mob.next_to(coil, UP, buff=0.15)
                        break

            label.add_updater(update_label_position)

        # Voltage curve updaters (Phase 1 - accumulating)
        for curve in curves_phase1:
            def update_curve(mob):
                t_now = time_tracker.get_value()
                trace = coil_data_phase1[mob.coil_name]

                idx_end = int(t_now / dt_phase1)
                idx_end = min(len(trace) - 1, max(0, idx_end))

                visible = trace[0:idx_end + 1]

                SUBSAMPLE_RATE = 3
                visible_subsampled = visible[::SUBSAMPLE_RATE]

                if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                    visible_subsampled.append(visible[-1])

                points = []
                for t_val, v_val in visible_subsampled:
                    points.append(voltage_ax.c2p(t_val, v_val))

                if len(points) > 1:
                    mob.set_points_as_corners(points)
                elif len(points) == 1:
                    mob.set_points_as_corners([points[0], points[0]])
                else:
                    mob.set_points_as_corners([])

            curve.add_updater(update_curve)

        # ============================================================
        # ANIMATION SEQUENCE - PHASE 1
        # ============================================================
        self.add(generator_group, graph_group, curves_phase1)
        self.wait(1)

        # Run Phase 1 simulation
        self.play(
            time_tracker.animate.set_value(PHASE_1_TIME),
            run_time=PHASE_1_TIME,
            rate_func=linear
        )

        self.wait(0.5)

        # ============================================================
        # PHASE 2 - TRANSFORM TO STACKED GRAPHS
        # ============================================================
        # Remove updaters from Phase 1 curves
        for curve in curves_phase1:
            curve.clear_updaters()

        # Remove coil motion updaters (coils are now fixed)
        for coil in coil_mobjects:
            coil.clear_updaters()
        for label in coil_labels:
            label.clear_updaters()

        # Create final static curves from Phase 1 data for transformation
        final_curves_phase1 = VGroup()
        for coil_cfg in coils_config:
            trace = coil_data_phase1[coil_cfg.name]
            points = [voltage_ax.c2p(t, v) for t, v in trace[::3]]
            curve = VMobject().set_color(coil_cfg.color).set_stroke(width=2)
            if len(points) > 1:
                curve.set_points_as_corners(points)
            curve.coil_name = coil_cfg.name
            final_curves_phase1.add(curve)

        # Replace dynamic curves with static versions
        self.remove(curves_phase1)
        self.add(final_curves_phase1)

        # Create target curves for each stacked graph
        # Calculate voltage history based on ACTUAL rotor position at transition time
        # The rotor has been spinning for PHASE_1_TIME, so its cumulative angle is:
        cumulative_angle_at_transition = ROTATION_SPEED * PHASE_1_TIME

        def calculate_voltage_at_rotor_angle(rotor_angle, coil_name):
            """Calculate instantaneous voltage for a coil given rotor angle."""
            coil_angle = FINAL_COIL_ANGLES[coil_name]
            # Current magnet angles based on rotor rotation
            current_magnet_angles = [
                (start_angle - rotor_angle) % (2 * PI)
                for start_angle in MAGNET_ANGLES_START
            ]
            flux = calculate_sinusoidal_flux(
                current_magnet_angles,
                MAGNET_POLARITIES,
                coil_angle,
                amplitude=VOLTAGE_AMPLITUDE
            )
            return flux

        # Build initial curves showing history up to current rotor position
        # We need voltage (derivative of flux), so we compute flux at small intervals
        target_curves = VGroup()
        POINTS_PER_WINDOW = 200
        dt_window = SCROLL_WINDOW / POINTS_PER_WINDOW

        for i, coil_cfg in enumerate(coils_config):
            ax = stacked_axes[i]

            # Generate voltage trace for the SCROLL_WINDOW history leading up to transition
            points = []
            prev_flux = None

            for j in range(POINTS_PER_WINDOW + 1):
                # Time offset from transition (negative = past)
                time_offset = -SCROLL_WINDOW + j * dt_window
                # Rotor angle at this time
                rotor_angle = cumulative_angle_at_transition + ROTATION_SPEED * time_offset

                flux = calculate_voltage_at_rotor_angle(rotor_angle, coil_cfg.name)

                if prev_flux is not None:
                    voltage = -(flux - prev_flux) / dt_window
                else:
                    voltage = 0.0

                # x_graph: 0 = left edge (oldest), SCROLL_WINDOW = right edge (now)
                x_graph = j * dt_window
                points.append(ax.c2p(x_graph, voltage))
                prev_flux = flux

            curve = VMobject().set_color(coil_cfg.color).set_stroke(width=2.5)
            if len(points) > 1:
                curve.set_points_as_corners(points)
            curve.coil_name = coil_cfg.name
            target_curves.add(curve)

        # Animate transformation
        self.play(
            FadeOut(voltage_label),
            FadeOut(voltage_title),
            run_time=0.5
        )

        self.play(
            ReplacementTransform(voltage_ax, stacked_axes),
            *[ReplacementTransform(final_curves_phase1[i], target_curves[i])
              for i in range(len(coils_config))],
            FadeIn(stacked_labels),
            run_time=1.5
        )

        self.remove(graph_group, final_curves_phase1)
        self.add(stacked_graphs_group, target_curves)

        self.wait(0.5)

        # ============================================================
        # PHASE 3 - SCROLLING GRAPHS
        # ============================================================
        # Set up Phase 3 time tracker (separate from Phase 1)
        phase3_time_tracker = ValueTracker(SCROLL_WINDOW)  # Start after initial window

        # Rotor updater for Phase 3 (continues from Phase 1 state)
        phase3_start_angle = [last_t[0]]  # Store the angle offset from Phase 1

        def update_rotor_phase3(mob, dt):
            t_now = phase3_time_tracker.get_value()
            # Continue rotation from where we left off
            expected_t = phase3_start_angle[0] + (t_now - SCROLL_WINDOW)
            dt_sim = expected_t - last_t[0]

            if abs(dt_sim) > 0.0001:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center)
                last_t[0] = expected_t

        rotor_group.clear_updaters()
        rotor_group.add_updater(update_rotor_phase3)

        # Remove target curves and add scrolling curves
        self.remove(target_curves)

        # Create "NOW" indicator lines at the right edge of each graph
        now_indicators = VGroup()
        for ax in stacked_axes:
            # Vertical line at the right edge (x = SCROLL_WINDOW)
            now_line = Line(
                start=ax.c2p(SCROLL_WINDOW, -max_voltage),
                end=ax.c2p(SCROLL_WINDOW, max_voltage),
                color=WHITE,
                stroke_width=1.5,
                stroke_opacity=0.6
            )
            now_indicators.add(now_line)

        # Scrolling curve updaters - REAL-TIME voltage calculation
        # Track cumulative time for rotor angle calculation
        # Phase 3 time tracker starts at SCROLL_WINDOW, representing time since Phase 3 start
        # But the rotor has already been spinning for PHASE_1_TIME

        for curve in curves_phase3:
            def make_scroll_updater(coil_name, ax):
                # Store previous flux values for derivative calculation
                prev_flux_cache = [None] * (POINTS_PER_WINDOW + 1)

                def update_scroll_curve(mob):
                    t_phase3 = phase3_time_tracker.get_value()  # Time since Phase 3 start

                    # Total simulation time (Phase 1 time + Phase 3 time elapsed)
                    # phase3_time_tracker starts at SCROLL_WINDOW, so actual elapsed Phase 3 time is:
                    t_elapsed_phase3 = t_phase3 - SCROLL_WINDOW
                    total_sim_time = PHASE_1_TIME + t_elapsed_phase3

                    # Current rotor angle (cumulative rotation since t=0)
                    current_rotor_angle = ROTATION_SPEED * total_sim_time

                    # Generate voltage trace for the SCROLL_WINDOW history
                    points = []
                    coil_angle = FINAL_COIL_ANGLES[coil_name]

                    for j in range(POINTS_PER_WINDOW + 1):
                        # Time offset from now (negative = past, 0 = now)
                        time_offset = -SCROLL_WINDOW + j * dt_window
                        # Rotor angle at this historical time
                        rotor_angle = current_rotor_angle + ROTATION_SPEED * time_offset

                        # Current magnet angles based on rotor rotation
                        current_magnet_angles = [
                            (start_angle - rotor_angle) % (2 * PI)
                            for start_angle in MAGNET_ANGLES_START
                        ]

                        flux = calculate_sinusoidal_flux(
                            current_magnet_angles,
                            MAGNET_POLARITIES,
                            coil_angle,
                            amplitude=VOLTAGE_AMPLITUDE
                        )

                        if j > 0 and prev_flux_cache[j-1] is not None:
                            # Use cached previous flux for smoother derivative
                            prev_flux = prev_flux_cache[j-1]
                        elif j > 0:
                            # Fallback: calculate previous flux
                            prev_time_offset = -SCROLL_WINDOW + (j-1) * dt_window
                            prev_rotor_angle = current_rotor_angle + ROTATION_SPEED * prev_time_offset
                            prev_magnet_angles = [
                                (start_angle - prev_rotor_angle) % (2 * PI)
                                for start_angle in MAGNET_ANGLES_START
                            ]
                            prev_flux = calculate_sinusoidal_flux(
                                prev_magnet_angles,
                                MAGNET_POLARITIES,
                                coil_angle,
                                amplitude=VOLTAGE_AMPLITUDE
                            )
                        else:
                            prev_flux = flux

                        voltage = -(flux - prev_flux) / dt_window if j > 0 else 0.0
                        prev_flux_cache[j] = flux

                        # x_graph: 0 = left edge (oldest), SCROLL_WINDOW = right edge (now)
                        x_graph = j * dt_window
                        points.append(ax.c2p(x_graph, voltage))

                    if len(points) > 1:
                        mob.set_points_as_corners(points)
                    elif len(points) == 1:
                        mob.set_points_as_corners([points[0], points[0]])

                return update_scroll_curve

            # Find the corresponding axis for this curve
            for ax in stacked_axes:
                if ax.coil_name == curve.coil_name:
                    curve.add_updater(make_scroll_updater(curve.coil_name, ax))
                    break

        self.add(curves_phase3, now_indicators)

        # Run Phase 3 simulation (scrolling)
        self.play(
            phase3_time_tracker.animate.set_value(SCROLL_WINDOW + PHASE_3_TIME),
            run_time=PHASE_3_TIME,
            rate_func=linear
        )

        self.wait(1)
