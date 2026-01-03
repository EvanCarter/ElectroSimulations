from manim import *
from generator import build_rotor, calculate_sine_voltage_trace
import math
import numpy as np


def build_rotor_custom(num_magnets, magnet_path_radius, magnet_radius, disk_radius, polarities=None, label_font_size=36):
    """
    Build a rotor with custom polarity configuration.

    Args:
        num_magnets: Number of magnets
        magnet_path_radius: Radius of magnet orbit
        magnet_radius: Radius of each magnet
        disk_radius: Radius of rotor disk
        polarities: Optional list of booleans (True=North, False=South).
                   If None, alternates N/S starting with N.
        label_font_size: Font size for N/S labels (default 36, scale with magnet size)
    """
    rotor_group = VGroup()

    # The Disk Body
    disk = Circle(radius=disk_radius, color=WHITE, stroke_opacity=0.5, stroke_width=2)
    disk.set_fill(color=GREY, opacity=0.1)
    rotor_group.add(disk)

    # The Magnets
    magnets = VGroup()
    for i in range(num_magnets):
        mag_angle = (PI / 2.0) - (i * (2 * PI / num_magnets))

        x = magnet_path_radius * math.cos(mag_angle)
        y = magnet_path_radius * math.sin(mag_angle)

        if polarities is not None:
            is_north = polarities[i]
        else:
            is_north = i % 2 == 0
        color = RED if is_north else BLUE

        magnet = Circle(radius=magnet_radius, color=color, fill_opacity=0.8)
        magnet.set_fill(color)
        magnet.move_to(np.array([x, y, 0]))

        # Add label N/S
        label_text = "N" if is_north else "S"
        label = Text(label_text, font_size=label_font_size, color=WHITE).move_to(magnet.get_center())

        mag_group = VGroup(magnet, label)
        magnets.add(mag_group)

    rotor_group.add(magnets)
    return rotor_group


def calculate_voltage_trace_custom(num_magnets, polarities, rotation_speed, total_time, coil_angle, amplitude, steps):
    """
    Calculate voltage trace for custom magnet configurations.

    This handles non-alternating polarity patterns (e.g., single N, or N-S at 90 degrees).
    """
    dt = total_time / steps

    # Setup magnets - evenly spaced starting from PI/2 (12 o'clock)
    magnet_angles_start = []
    for i in range(num_magnets):
        theta = (math.pi / 2.0) - (i * (2 * math.pi / num_magnets))
        magnet_angles_start.append(theta)

    voltage_trace = []
    prev_flux = None
    influence_width = math.pi / 6  # Narrower influence for smaller magnets (30 degrees)

    for step in range(steps):
        t = step * dt

        # Rotate magnets clockwise
        angle_delta = -rotation_speed * t
        current_magnet_angles = [
            (start_angle + angle_delta) % (2 * math.pi)
            for start_angle in magnet_angles_start
        ]

        # Calculate flux using localized sinusoidal model
        total_flux = 0.0
        for mag_angle, is_north in zip(current_magnet_angles, polarities):
            # Calculate angular difference, normalized to [-pi, pi]
            angle_diff = mag_angle - coil_angle
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            while angle_diff < -math.pi:
                angle_diff += 2 * math.pi

            # Only contribute if magnet is within influence zone
            if abs(angle_diff) >= influence_width:
                continue

            # Raised cosine: smooth falloff
            flux_contribution = amplitude * 0.5 * (1 + math.cos(math.pi * angle_diff / influence_width))

            if is_north:
                total_flux += flux_contribution
            else:
                total_flux -= flux_contribution

        # Calculate voltage (V = -dFlux/dt)
        if prev_flux is not None:
            voltage = -(total_flux - prev_flux) / dt
        else:
            voltage = 0.0

        voltage_trace.append((t, voltage))
        prev_flux = total_flux

    return voltage_trace


class SingleCoil4MagScene(Scene):
    """
    Demonstrates how 4 magnets produce 4 voltage peaks per rotation.

    Visual Elements:
    - Left side: Generator with 4 alternating magnets (N-S-N-S) on rotor
    - Single coil at 12 o'clock position (square coil style)
    - Right side: Voltage graph showing 4 complete sine cycles per rotation

    Animation Sequence:
    1. Scene starts with all elements visible
    2. Rotor spins one full rotation (4 seconds at 0.5*PI rad/s)
    3. Voltage trace accumulates in sync with rotor rotation
    4. Subtitle emphasizes "4 magnets = 4 peaks per rotation"

    Expected Output:
    - 4 complete sine wave cycles on the voltage graph
    - Each peak corresponds to a magnet passing the coil
    - Clear demonstration of frequency relationship to magnet count
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 3.0
        MAGNET_RADIUS = 0.6  # Smaller to fit 4 magnets
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        NUM_MAGNETS = 4
        ROTATION_SPEED = 0.5 * PI  # rad/s, clockwise

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        SIMULATION_TIME = 4.0  # One full rotation at 0.5*PI rad/s
        PHYSICS_STEPS = 2500
        dt = SIMULATION_TIME / PHYSICS_STEPS

        # ============================================================
        # PHYSICS CALCULATION
        # ============================================================
        # Single coil at 12 o'clock (PI/2 in standard math coordinates)
        coil_angle_static = PI / 2.0

        print(f"SingleCoil4Mag: Calculating physics for 1 coil, {NUM_MAGNETS} magnets...")

        voltage_trace = calculate_sine_voltage_trace(
            num_magnets=NUM_MAGNETS,
            rotation_speed=ROTATION_SPEED,
            total_time=SIMULATION_TIME,
            coil_angle_static=coil_angle_static,
            amplitude=10.0,
            steps=PHYSICS_STEPS,
        )

        print(f"  Generated {len(voltage_trace)} voltage data points")

        # Find max voltage for graph scaling
        max_voltage = 0.0
        for _, v in voltage_trace:
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

        # Single coil at 12 o'clock (square coil style)
        coil_pos = np.array([
            MAGNET_PATH_RADIUS * math.cos(coil_angle_static),
            MAGNET_PATH_RADIUS * math.sin(coil_angle_static),
            0
        ])

        coil = Rectangle(
            width=MAGNET_RADIUS * 2.0,  # Match magnet diameter
            height=MAGNET_RADIUS * 2.0,  # Match magnet diameter
            color=BLUE,
            stroke_width=6
        )
        # Rotate so long side is tangent to circle path
        coil.rotate(coil_angle_static - PI / 2)
        coil.move_to(coil_pos)

        # Coil label
        generator_group = VGroup(stator, rotor_group, coil)
        generator_group.scale(0.55)
        generator_group.to_corner(UL, buff=0.5)
        disk_center = rotor_group.get_center()

        # --- VOLTAGE GRAPH (Right side) ---
        voltage_ax = Axes(
            x_range=[0, SIMULATION_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage / 2],
            x_length=9,
            y_length=4.5,
            axis_config={"include_tip": False, "color": GREY},
        )

        voltage_title = Text("Induced Voltage", font_size=28)
        voltage_title.next_to(voltage_ax, UP, buff=0.15)

        # Subtitle emphasizing the educational point
        subtitle = Text("4 magnets = 4 peaks per rotation", font_size=20, color=YELLOW)
        subtitle.next_to(voltage_ax, DOWN, buff=0.25)

        graph_group = VGroup(voltage_ax, voltage_title, subtitle)
        graph_group.to_edge(RIGHT, buff=0.4)

        # --- VOLTAGE CURVE ---
        voltage_curve = VMobject().set_color(ORANGE).set_stroke(width=3)

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

        # Voltage curve updater (accumulating from t=0)
        def update_voltage_curve(mob):
            t_now = time_tracker.get_value()

            # Calculate index from time
            idx_end = int(t_now / dt)
            idx_end = min(len(voltage_trace) - 1, max(0, idx_end))

            # Extract visible points from start
            visible = voltage_trace[0:idx_end + 1]

            # Subsample to reduce point density
            SUBSAMPLE_RATE = 3
            visible_subsampled = visible[::SUBSAMPLE_RATE]

            # Always include the last point for accuracy
            if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                visible_subsampled.append(visible[-1])

            # Convert to screen coordinates
            points = []
            for t_val, v_val in visible_subsampled:
                points.append(voltage_ax.c2p(t_val, v_val))

            # Update curve
            if len(points) > 1:
                mob.set_points_as_corners(points)
            elif len(points) == 1:
                mob.set_points_as_corners([points[0], points[0]])
            else:
                mob.set_points_as_corners([])

        voltage_curve.add_updater(update_voltage_curve)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        self.add(generator_group, graph_group, voltage_curve)

        self.wait(1)

        # Run the full simulation (one rotation)
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=SIMULATION_TIME,
            rate_func=linear
        )

        self.wait(2)


class ProgressiveMagnetScene(Scene):
    """
    Progressive build-up of magnets while keeping a single coil at 12 o'clock.

    Visual Elements:
    - Left side: Generator with rotor that changes from 1 to 2 to 4 magnets
    - Single coil at 12 o'clock position (square coil style)
    - Right side: Voltage graph showing increasing peaks per rotation
    - Text labels indicating current magnet count

    Animation Sequence:
    1. Phase 1 (0-4s): 1 magnet (North only) rotating - shows 1 voltage peak per rotation
    2. Phase 2 (4-8s): 2 magnets (N at 12 o'clock, S at 6 o'clock = 180 degrees apart) - shows 2 peaks per rotation
    3. Phase 3 (8-12s): 4 magnets (N-S-N-S at 90 degree intervals) - shows 4 peaks per rotation

    Key Educational Point:
    More magnets = more voltage cycles per rotation = higher frequency output
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 3.0
        MAGNET_RADIUS = 0.6
        LABEL_FONT_SIZE = 36
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        ROTATION_SPEED = 0.5 * PI  # rad/s, clockwise

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        # Phase 1 & 2: 2 rotations each (more time to see peaks clearly)
        # Phase 3: 1 rotation (already dense with 4 magnets)
        PHASE_1_DURATION = 8.0  # 2 rotations at 0.5*PI rad/s
        PHASE_2_DURATION = 8.0  # 2 rotations
        PHASE_3_DURATION = 8.0  # 2 rotations (same as others)
        MAX_DURATION = max(PHASE_1_DURATION, PHASE_2_DURATION, PHASE_3_DURATION)
        PHYSICS_STEPS = 2500

        # Single coil at 12 o'clock
        coil_angle_static = PI / 2.0

        # ============================================================
        # PHASE CONFIGURATIONS
        # ============================================================
        # Phase 1: 1 magnet (North only) - 2 rotations to see peaks clearly
        config_1_mag = {
            "num_magnets": 1,
            "polarities": [True],  # North
            "label": "1 magnet",
            "duration": PHASE_1_DURATION
        }

        # Phase 2: 2 magnets (N at top, S at bottom - 180 degrees apart) - 2 rotations
        config_2_mag = {
            "num_magnets": 2,
            "polarities": [True, False],  # N, S (alternating)
            "label": "2 magnets",
            "duration": PHASE_2_DURATION
        }

        # Phase 3: 4 magnets (N-S-N-S at 90 degree intervals) - 1 rotation (already dense)
        config_4_mag = {
            "num_magnets": 4,
            "polarities": [True, False, True, False],  # N, S, N, S (alternating)
            "label": "4 magnets",
            "duration": PHASE_3_DURATION
        }

        configs = [config_1_mag, config_2_mag, config_4_mag]

        # ============================================================
        # PRE-CALCULATE VOLTAGE TRACES FOR ALL CONFIGURATIONS
        # ============================================================
        print("Calculating voltage traces for all configurations...")

        voltage_traces = {}
        for cfg in configs:
            # Scale physics steps with duration to maintain resolution
            phase_steps = int(PHYSICS_STEPS * cfg["duration"] / 4.0)
            trace = calculate_voltage_trace_custom(
                num_magnets=cfg["num_magnets"],
                polarities=cfg["polarities"],
                rotation_speed=ROTATION_SPEED,
                total_time=cfg["duration"],
                coil_angle=coil_angle_static,
                amplitude=10.0,
                steps=phase_steps,
            )
            voltage_traces[cfg["num_magnets"]] = trace
            print(f"  {cfg['label']}: {len(trace)} data points, duration={cfg['duration']}s")

        # Find max voltage across all configs for consistent graph scaling
        max_voltage = 0.0
        for trace in voltage_traces.values():
            for _, v in trace:
                max_voltage = max(max_voltage, abs(v))
        max_voltage *= 1.1  # Add padding

        # ============================================================
        # STATIC VISUAL ELEMENTS
        # ============================================================

        # Stator (static outer ring) - stays constant
        stator = Circle(
            radius=DISK_RADIUS + 0.3,
            color=GRAY,
            stroke_width=8,
            stroke_opacity=0.5
        )

        # Single coil at 12 o'clock (square coil style)
        coil_pos = np.array([
            MAGNET_PATH_RADIUS * math.cos(coil_angle_static),
            MAGNET_PATH_RADIUS * math.sin(coil_angle_static),
            0
        ])

        coil = Rectangle(
            width=MAGNET_RADIUS * 2.0,  # Match magnet diameter
            height=MAGNET_RADIUS * 2.0,  # Match magnet diameter
            color=ORANGE,
            stroke_width=6
        )
        coil.rotate(coil_angle_static - PI / 2)
        coil.move_to(coil_pos)

        # Voltage graph (Right side) - x_range uses max duration across phases
        voltage_ax = Axes(
            x_range=[0, MAX_DURATION, 1],
            y_range=[-max_voltage, max_voltage, max_voltage / 2],
            x_length=8,
            y_length=4.5,
            axis_config={"include_tip": False, "color": GREY},
        )

        voltage_title = Text("Induced Voltage", font_size=28)
        voltage_title.next_to(voltage_ax, UP, buff=0.15)

        graph_group = VGroup(voltage_ax, voltage_title)
        graph_group.to_edge(RIGHT, buff=0.4)

        # Static elements group (stator + coil) - position before rotor
        static_gen_elements = VGroup(stator, coil)
        static_gen_elements.scale(0.55)
        static_gen_elements.to_corner(UL, buff=0.5)

        # ============================================================
        # ANIMATION SEQUENCE - THREE PHASES
        # ============================================================

        # Add static elements
        self.add(static_gen_elements, graph_group)

        for phase_idx, cfg in enumerate(configs):
            print(f"\n--- Phase {phase_idx + 1}: {cfg['label']} ---")

            phase_duration = cfg["duration"]

            # Build rotor for this phase
            rotor_group = build_rotor_custom(
                num_magnets=cfg["num_magnets"],
                magnet_path_radius=MAGNET_PATH_RADIUS,
                magnet_radius=MAGNET_RADIUS,
                disk_radius=DISK_RADIUS,
                polarities=cfg["polarities"],
                label_font_size=LABEL_FONT_SIZE
            )
            rotor_group.scale(0.55)
            rotor_group.move_to(static_gen_elements.get_center())
            disk_center = rotor_group.get_center()

            # Create voltage curve for this phase
            voltage_curve = VMobject().set_color(ORANGE).set_stroke(width=3)
            current_trace = voltage_traces[cfg["num_magnets"]]

            # Calculate dt for this phase (matches physics calculation)
            phase_steps = len(current_trace)
            phase_dt = phase_duration / phase_steps

            # Create magnet count label
            magnet_label = Text(cfg["label"], font_size=24, color=YELLOW)
            magnet_label.next_to(voltage_ax, DOWN, buff=0.25)

            # Time tracker for this phase
            time_tracker = ValueTracker(0)
            last_t = [0.0]

            # Rotor rotation updater
            def make_rotor_updater(rotor, center, tracker, last_time_ref):
                def update_rotor(mob, dt):
                    t_now = tracker.get_value()
                    dt_sim = t_now - last_time_ref[0]
                    if dt_sim != 0:
                        mob.rotate(-ROTATION_SPEED * dt_sim, about_point=center)
                        last_time_ref[0] = t_now
                return update_rotor

            rotor_updater = make_rotor_updater(rotor_group, disk_center, time_tracker, last_t)
            rotor_group.add_updater(rotor_updater)

            # Voltage curve updater
            def make_curve_updater(curve, trace, tracker, axes, time_step):
                def update_curve(mob):
                    t_now = tracker.get_value()
                    idx_end = int(t_now / time_step)
                    idx_end = min(len(trace) - 1, max(0, idx_end))

                    visible = trace[0:idx_end + 1]

                    SUBSAMPLE_RATE = 3
                    visible_subsampled = visible[::SUBSAMPLE_RATE]
                    if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                        visible_subsampled.append(visible[-1])

                    points = []
                    for t_val, v_val in visible_subsampled:
                        points.append(axes.c2p(t_val, v_val))

                    if len(points) > 1:
                        mob.set_points_as_corners(points)
                    elif len(points) == 1:
                        mob.set_points_as_corners([points[0], points[0]])
                    else:
                        mob.set_points_as_corners([])
                return update_curve

            curve_updater = make_curve_updater(voltage_curve, current_trace, time_tracker, voltage_ax, phase_dt)
            voltage_curve.add_updater(curve_updater)

            # Transition into this phase
            if phase_idx == 0:
                # First phase: fade in rotor and label
                self.play(
                    FadeIn(rotor_group),
                    FadeIn(magnet_label),
                    run_time=0.5
                )
            else:
                # Subsequent phases: fade out old, fade in new
                self.play(
                    FadeIn(rotor_group),
                    FadeIn(magnet_label),
                    run_time=0.5
                )

            # Add voltage curve (starts empty)
            self.add(voltage_curve)

            # Run the rotation animation
            self.play(
                time_tracker.animate.set_value(phase_duration),
                run_time=phase_duration,
                rate_func=linear
            )

            # Brief pause at end of phase
            self.wait(0.5)

            # Clean up for next phase (except last)
            rotor_group.remove_updater(rotor_updater)
            voltage_curve.remove_updater(curve_updater)

            if phase_idx < len(configs) - 1:
                # Fade out current phase elements
                self.play(
                    FadeOut(rotor_group),
                    FadeOut(voltage_curve),
                    FadeOut(magnet_label),
                    run_time=0.5
                )

        # Final hold
        self.wait(2)
