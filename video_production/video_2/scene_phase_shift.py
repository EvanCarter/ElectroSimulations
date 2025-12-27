from manim import *
from generator import (
    build_rotor,
    get_theta_distance,
    get_area_between_circle
)
import math
from dataclasses import dataclass
from typing import Callable, List, Tuple


@dataclass
class CoilConfig:
    """Configuration for a single coil"""
    name: str
    color: str
    motion_profile: Callable[[float], float]  # time -> angular_offset_from_12_oclock (radians)


class PhaseShiftScene(Scene):
    """
    Clean physics simulation showing voltage phase shifts as coils move.

    KEY FEATURE: Each coil's voltage trace is calculated from actual physics
    at each moment in time, NOT by shifting graphs. This means historical data
    stays accurate as coils move.
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
        SIMULATION_TIME = 15.0  # Total physics simulation time
        PHYSICS_STEPS = 5000  # Fixed number of steps for smooth curves
        dt = SIMULATION_TIME / PHYSICS_STEPS  # Calculate dt from steps

        # ============================================================
        # COIL MOTION PROFILES
        # ============================================================
        # Define how each coil moves over time
        # All coils start at 12 o'clock (top, PI/2)

        def stationary_profile(t):
            """Coil stays at 12 o'clock"""
            return 0.0

        def moving_1x_profile(t):
            """Coil moves to target position over 8 seconds"""
            MOVE_START = 2.0
            MOVE_DURATION = 8.0
            TARGET_OFFSET = 90 * DEGREES  # clockwise from top (3 o'clock position)

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
        # Start with ONE coil, then uncomment others to add more
        coils_config = [
            CoilConfig(name="A", color=BLUE, motion_profile=stationary_profile),
            CoilConfig(name="B", color=ORANGE, motion_profile=moving_1x_profile),
            CoilConfig(name="C", color=GREEN, motion_profile=moving_2x_profile),
        ]

        # ============================================================
        # MAGNET SETUP
        # ============================================================
        # Calculate initial magnet positions (matching build_rotor logic)
        magnet_angles_start = []
        magnet_polarities = []
        for i in range(NUM_MAGNETS):
            theta = (math.pi / 2.0) - (i * (2 * math.pi / NUM_MAGNETS))
            magnet_angles_start.append(theta)
            magnet_polarities.append(i % 2 == 0)  # Alternating N/S

        # ============================================================
        # PHYSICS CALCULATION
        # ============================================================
        def calculate_flux_at_instant(t: float, coil_angle: float) -> float:
            """
            Calculate the magnetic flux through a coil at a specific time.

            Args:
                t: Current time (determines magnet positions)
                coil_angle: Angular position of coil (radians, 0=right, PI/2=top)

            Returns:
                Total flux through the coil
            """
            # Magnets rotate clockwise (negative direction)
            angle_delta = -ROTATION_SPEED * t

            total_flux = 0.0
            for i, start_angle in enumerate(magnet_angles_start):
                # Current magnet position
                current_mag_angle = (start_angle + angle_delta) % (2 * PI)

                # Angular distance between coil and magnet
                dist = get_theta_distance(coil_angle, current_mag_angle)

                # Overlap area (proxy for flux)
                area = get_area_between_circle(dist, MAGNET_PATH_RADIUS, MAGNET_RADIUS)

                # Add or subtract based on polarity
                if magnet_polarities[i]:
                    total_flux += area
                else:
                    total_flux -= area

            return total_flux

        # Pre-calculate physics data for ALL coils
        print(f"Calculating physics for {len(coils_config)} coil(s)...")

        # STEP 1: Build a flux lookup table as a function of relative angle
        # This represents the flux a stationary coil would see at any angle
        # We'll use one full rotation to capture the pattern
        from scipy.ndimage import gaussian_filter1d
        import numpy as np

        lookup_steps = 5000  # High resolution lookup table
        flux_lookup = []

        for i in range(lookup_steps):
            # Coil at top (PI/2), magnets at various angles
            t_lookup = (i / lookup_steps) * (2 * PI / ROTATION_SPEED)
            flux = calculate_flux_at_instant(t_lookup, PI / 2.0)
            flux_lookup.append(flux)

        # Smooth the lookup table
        flux_lookup_smoothed = gaussian_filter1d(flux_lookup, sigma=50)

        def get_smoothed_flux_at_angle(t, coil_angle):
            """Get smoothed flux for a coil at given angle at time t"""
            # Calculate relative angle between coil and magnet(s)
            angle_delta = -ROTATION_SPEED * t
            # We need the magnet angle relative to coil
            # Our lookup is for coil at PI/2, so adjust
            effective_time = t + (PI/2 - coil_angle) / ROTATION_SPEED
            # Map to lookup table index
            phase = (effective_time * ROTATION_SPEED) % (2 * PI)

            # Use LINEAR INTERPOLATION instead of integer indexing to avoid discrete jumps
            fractional_idx = (phase / (2 * PI)) * lookup_steps
            idx_low = int(fractional_idx) % lookup_steps
            idx_high = (idx_low + 1) % lookup_steps
            alpha = fractional_idx - int(fractional_idx)

            # Interpolate between adjacent lookup table values
            flux_low = flux_lookup_smoothed[idx_low]
            flux_high = flux_lookup_smoothed[idx_high]
            return flux_low + alpha * (flux_high - flux_low)

        # STEP 2: Calculate voltage for each coil
        coil_data = {}  # coil_name -> List[(time, voltage)]

        for coil_cfg in coils_config:
            voltage_trace = []

            for step in range(PHYSICS_STEPS):
                t = step * dt

                # Get coil position at this time
                offset = coil_cfg.motion_profile(t)
                coil_angle = (PI / 2.0) - offset

                if step > 0:
                    # Calculate voltage as if coil is stationary at current position
                    # Flux now (with magnet at current position)
                    flux_now = get_smoothed_flux_at_angle(t, coil_angle)

                    # Flux dt ago (with magnet dt ago, coil at SAME position)
                    flux_prev = get_smoothed_flux_at_angle(t - dt, coil_angle)

                    voltage = (flux_now - flux_prev) / dt
                else:
                    voltage = 0.0

                voltage_trace.append((t, voltage))

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

            # Create coil visual
            coil = DashedVMobject(
                Circle(radius=MAGNET_RADIUS, color=coil_cfg.color, stroke_width=6),
                num_dashes=12
            ).move_to(pos)

            # Create label
            label = Text(coil_cfg.name, font_size=28, color=coil_cfg.color).next_to(coil, UP, buff=0.15)

            # Store for later reference
            coil.coil_name = coil_cfg.name
            coil.motion_profile = coil_cfg.motion_profile
            label.coil_name = coil_cfg.name

            coil_mobjects.add(coil)
            coil_labels.add(label)

        generator_group = VGroup(stator, rotor_group, coil_mobjects, coil_labels)
        generator_group.to_edge(LEFT, buff=1.0)
        disk_center = rotor_group.get_center()

        # --- VOLTAGE GRAPH (Right side) ---
        GRAPH_WINDOW = 6.0  # Show last 6 seconds of data

        voltage_ax = Axes(
            x_range=[0, GRAPH_WINDOW, 1],
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
            curve = VMobject().set_color(coil_cfg.color).set_stroke(width=2)
            curve.coil_name = coil_cfg.name
            curves.add(curve)

        # ============================================================
        # UPDATERS
        # ============================================================
        time_tracker = ValueTracker(0)

        # Rotor rotation updater
        def update_rotor(mob, dt):
            """Rotate rotor based on animation time delta"""
            mob.rotate(-ROTATION_SPEED * dt, about_point=disk_center)

        rotor_group.add_updater(update_rotor)

        # Coil position updaters
        for coil in coil_mobjects:
            def update_coil_position(mob):
                t = time_tracker.get_value()
                offset = mob.motion_profile(t)
                angle = (PI / 2.0) - offset

                new_pos = disk_center + np.array([
                    MAGNET_PATH_RADIUS * math.cos(angle),
                    MAGNET_PATH_RADIUS * math.sin(angle),
                    0
                ])
                mob.move_to(new_pos)

            coil.add_updater(update_coil_position)

        # Label position updaters (follow coils)
        for label in coil_labels:
            def update_label_position(mob):
                # Find corresponding coil
                for coil in coil_mobjects:
                    if coil.coil_name == mob.coil_name:
                        mob.next_to(coil, UP, buff=0.15)
                        break

            label.add_updater(update_label_position)

        # Voltage curve updaters (scrolling window)
        for curve in curves:
            def update_curve(mob):
                t_now = time_tracker.get_value()

                # Get trace data for this coil
                trace = coil_data[mob.coil_name]

                # Calculate visible window [t_now - GRAPH_WINDOW, t_now]
                # Map to graph x coordinates [0, GRAPH_WINDOW]
                idx_end = int(t_now / dt)
                idx_start = int((t_now - GRAPH_WINDOW) / dt)

                # Clamp indices
                idx_end = min(len(trace) - 1, max(0, idx_end))
                idx_start = max(0, idx_start)

                # Extract visible points
                visible = trace[idx_start:idx_end + 1]

                # Subsample to reduce point density (every 3rd point for smoother rendering)
                SUBSAMPLE_RATE = 3
                visible_subsampled = visible[::SUBSAMPLE_RATE]

                # Always include the last point for accuracy at the edge
                if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                    visible_subsampled.append(visible[-1])

                # Convert to screen coordinates
                points = []
                for t_val, v_val in visible_subsampled:
                    # Map time to graph x: newest data at right edge
                    x_graph = t_val - t_now + GRAPH_WINDOW
                    if 0 <= x_graph <= GRAPH_WINDOW:  # Only show points in range
                        points.append(voltage_ax.c2p(x_graph, v_val))

                # Update curve
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

        # Wait a moment
        self.wait(1)

        # Run the full simulation
        # Time moves from 0 to SIMULATION_TIME
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=SIMULATION_TIME,
            rate_func=linear
        )

        # Final wait
        self.wait(2)
