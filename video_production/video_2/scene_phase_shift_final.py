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


class PhaseShiftSceneFinal(Scene):
    """
    FINAL: Clean physics simulation showing voltage phase shifts as coils move.

    Uses localized sinusoidal flux model (PI/4 influence width) for smooth
    sine waves that match the visual - voltage is zero when no magnet is near coil.

    - 3 coils (A, B, C) start at 12 o'clock
    - B moves to 4 o'clock (120°), C moves to 8 o'clock (240°)
    - Shows phase shift appearing as coils separate
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
        SIMULATION_TIME = 8.0  # Reduced to 8.0s (approx 2 rotations at 0.5*PI rad/s)
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
            MOVE_DURATION = 5.0 # Slightly faster move to fit in 8s
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
        # Start with ONE coil, then uncomment others to add more
        coils_config = [
            CoilConfig(name="A", color=BLUE, motion_profile=stationary_profile),
            CoilConfig(name="B", color=ORANGE, motion_profile=moving_1x_profile),
            CoilConfig(name="C", color=GREEN, motion_profile=moving_2x_profile),
        ]

        # ============================================================
        # PHYSICS CALCULATION (Sinusoidal Model)
        # ============================================================
        print(f"Calculating physics for {len(coils_config)} coil(s)...")

        coil_data = {}  # coil_name -> List[(time, voltage)]

        for coil_cfg in coils_config:
            # Create a function that returns coil angle at time t
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

            # Create coil visual (square coil matching magnet diameter)
            # Create at origin, rotate to follow circle tangent, then move to position
            coil = Rectangle(
                width=MAGNET_RADIUS * 2.0,
                height=MAGNET_RADIUS * 2.0,
                color=coil_cfg.color,
                stroke_width=6
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

        generator_group = VGroup(stator, coil_mobjects, rotor_group, coil_labels)
        generator_group.to_edge(LEFT, buff=1.0)
        disk_center = rotor_group.get_center()

        # --- VOLTAGE GRAPH (Right side) ---
        # No window, show full simulation range
        
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
            curve = VMobject().set_color(coil_cfg.color).set_stroke(width=2)
            curve.coil_name = coil_cfg.name
            curves.add(curve)

        # ============================================================
        # UPDATERS
        # ============================================================
        time_tracker = ValueTracker(0)

        # Rotor rotation updater
        # Use a list to store last time to calculate delta t from tracker
        last_t = [0.0]
        
        def update_rotor(mob, dt):
            # We ignore the frame 'dt' and calculate dt based on simulation time
            t_now = time_tracker.get_value()
            dt_sim = t_now - last_t[0]
            
            if dt_sim != 0:
                mob.rotate(-ROTATION_SPEED * dt_sim, about_point=disk_center)
                last_t[0] = t_now

        rotor_group.add_updater(update_rotor)

        # Coil position updaters
        # Rotate around disk center to both move and orient the coil correctly
        for coil in coil_mobjects:
            def update_coil_position(mob):
                t = time_tracker.get_value()
                offset = mob.motion_profile(t)
                new_angle = (PI / 2.0) - offset

                # Rotate by delta from current angle around disk center
                # This moves the coil along the circle AND rotates it to stay tangent
                delta_angle = new_angle - mob.current_angle
                if delta_angle != 0:
                    mob.rotate(delta_angle, about_point=disk_center)
                    mob.current_angle = new_angle

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

        # Voltage curve updaters (ACCUMULATING from t=0)
        for curve in curves:
            def update_curve(mob):
                t_now = time_tracker.get_value()

                # Get trace data for this coil
                trace = coil_data[mob.coil_name]

                # Calculate visible range [0, t_now]
                idx_end = int(t_now / dt)
                
                # Clamp index
                idx_end = min(len(trace) - 1, max(0, idx_end))
                
                # Extract visible points from start
                visible = trace[0:idx_end + 1]

                # Subsample to reduce point density (every 3rd point for smoother rendering)
                SUBSAMPLE_RATE = 3
                visible_subsampled = visible[::SUBSAMPLE_RATE]

                # Always include the last point for accuracy at the edge
                if len(visible) > 0 and (len(visible) - 1) % SUBSAMPLE_RATE != 0:
                    visible_subsampled.append(visible[-1])

                # Convert to screen coordinates
                points = []
                for t_val, v_val in visible_subsampled:
                    # Map time to graph x: direct 1:1 mapping (since x_range starts at 0)
                    x_graph = t_val
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
        self.wait(1)


class PhaseShiftScene4Mag(Scene):
    """
    3-phase generator with 4 magnets and 3 STACKED SCROLLING GRAPHS.

    Shows steady-state 3-phase output at 2x frequency compared to 2-magnet version.
    Coils are STATIC (no movement) - this is the equilibrium 3-phase configuration.

    Visual Elements:
    - Left side: Generator with 4 alternating magnets (N-S-N-S at 90 degree intervals)
    - 3 static coils at standard 3-phase positions:
      - Coil A (BLUE) at 12 o'clock (0 degrees)
      - Coil B (ORANGE) at 4 o'clock (120 degrees)
      - Coil C (GREEN) at 8 o'clock (240 degrees)
    - Square coils sized to MAGNET_RADIUS * 2.0 (matching magnet diameter)
    - Right side: 3 vertically stacked graphs, one per coil
      - Each graph has a scrolling window showing ~2.5 seconds of history
      - Labels "Coil A", "Coil B", "Coil C" on the left of each graph

    Animation Sequence:
    1. Scene starts with all elements visible
    2. Rotor spins for ~8 seconds steady-state
    3. Each graph scrolls in real-time showing voltage history
    4. Clear 120 degree phase offset visible between A, B, C waveforms

    Expected Output:
    - Scrolling waveforms in each stacked graph
    - Higher frequency output (4 magnets = 2x frequency of 2 magnets)
    - Clear phase relationships between the three coils
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 3.0
        MAGNET_RADIUS = 0.75  # Bigger magnets = less dead space in voltage
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        NUM_MAGNETS = 4
        ROTATION_SPEED = 0.5 * PI  # rad/s, clockwise
        VOLTAGE_AMPLITUDE = 10.0

        # Calculate influence_width based on magnet geometry (must match visual!)
        # Magnets influence coils when they visually overlap
        # influence_width = angular size of magnet on the path
        INFLUENCE_WIDTH = 2 * MAGNET_RADIUS / MAGNET_PATH_RADIUS  # ~31° for these values

        # ============================================================
        # TIME PARAMETERS
        # ============================================================
        SIMULATION_TIME = 4.0  # ~1 rotation at 0.5*PI rad/s
        SCROLL_WINDOW = 2.5  # Scrolling window width in seconds
        POINTS_PER_WINDOW = 200  # Number of points to calculate for scrolling curve

        # ============================================================
        # COIL CONFIGURATIONS - FIXED POSITIONS (3-phase standard)
        # ============================================================
        coils_config = [
            {"name": "A", "color": BLUE, "position_angle": 0 * DEGREES},      # 12 o'clock
            {"name": "B", "color": ORANGE, "position_angle": 120 * DEGREES},  # 4 o'clock
            {"name": "C", "color": GREEN, "position_angle": 240 * DEGREES},   # 8 o'clock
        ]

        # Store final coil angles for physics calculations
        FINAL_COIL_ANGLES = {}
        for coil_cfg in coils_config:
            FINAL_COIL_ANGLES[coil_cfg["name"]] = (PI / 2.0) - coil_cfg["position_angle"]

        # Setup magnet initial angles and polarities
        MAGNET_ANGLES_START = []
        MAGNET_POLARITIES = []
        for i in range(NUM_MAGNETS):
            theta = (PI / 2.0) - (i * (2 * PI / NUM_MAGNETS))
            MAGNET_ANGLES_START.append(theta)
            MAGNET_POLARITIES.append(i % 2 == 0)  # Alternating N/S

        # Time step for scrolling window calculations
        dt_window = SCROLL_WINDOW / POINTS_PER_WINDOW

        # Find max voltage for graph scaling (run a quick simulation)
        print(f"PhaseShiftScene4Mag: Calculating physics for {len(coils_config)} coils, {NUM_MAGNETS} magnets...")
        print(f"  INFLUENCE_WIDTH = {INFLUENCE_WIDTH:.3f} rad ({INFLUENCE_WIDTH * 180 / PI:.1f} degrees)")
        test_trace = calculate_sine_voltage_trace(
            num_magnets=NUM_MAGNETS,
            rotation_speed=ROTATION_SPEED,
            total_time=SCROLL_WINDOW * 2,
            coil_angle_static=PI / 2.0,
            amplitude=VOLTAGE_AMPLITUDE,
            steps=1000,
            influence_width=INFLUENCE_WIDTH,
        )
        max_voltage = max(abs(v) for _, v in test_trace) * 1.1

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

        # Build coil visual objects (static positions)
        coil_mobjects = VGroup()
        coil_labels = VGroup()

        for coil_cfg in coils_config:
            # Calculate coil angle in standard math coordinates
            angle = (PI / 2.0) - coil_cfg["position_angle"]

            pos = np.array([
                MAGNET_PATH_RADIUS * math.cos(angle),
                MAGNET_PATH_RADIUS * math.sin(angle),
                0
            ])

            # Square coil matching magnet diameter
            coil = Rectangle(
                width=MAGNET_RADIUS * 2.0,
                height=MAGNET_RADIUS * 2.0,
                color=coil_cfg["color"],
                stroke_width=6
            )
            # Rotate so sides are tangent to circle path
            coil.rotate(angle - PI / 2)
            coil.move_to(pos)

            coil_mobjects.add(coil)

        generator_group = VGroup(stator, coil_mobjects, rotor_group)
        generator_group.to_edge(LEFT, buff=1.0)
        disk_center = rotor_group.get_center()

        # --- THREE STACKED GRAPHS (Right side) ---
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
            ax.coil_name = coil_cfg["name"]
            ax.coil_color = coil_cfg["color"]

            # Label for each graph
            label = Text(f"Coil {coil_cfg['name']}", font_size=20, color=coil_cfg["color"])
            label.coil_name = coil_cfg["name"]

            stacked_axes.add(ax)
            stacked_labels.add(label)

        # Position stacked graphs vertically
        stacked_axes.arrange(DOWN, buff=GRAPH_SPACING)
        stacked_axes.to_edge(RIGHT, buff=0.5)

        # Position labels to the left of each axis
        for ax, label in zip(stacked_axes, stacked_labels):
            label.next_to(ax, LEFT, buff=0.2)

        stacked_graphs_group = VGroup(stacked_axes, stacked_labels)

        # Title above stacked graphs
        graphs_title = Text("3-Phase Voltage (4 Magnets)", font_size=24)
        graphs_title.next_to(stacked_axes, UP, buff=0.3)

        # --- SCROLLING CURVES ---
        curves = VGroup()
        for coil_cfg in coils_config:
            curve = VMobject().set_color(coil_cfg["color"]).set_stroke(width=2.5)
            curve.coil_name = coil_cfg["name"]
            curves.add(curve)

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

        # Scrolling curve updaters - calculate voltage in real-time
        for curve in curves:
            def make_scroll_updater(coil_name, ax):
                def update_scroll_curve(mob):
                    t_now = time_tracker.get_value()

                    # Current rotor angle (cumulative rotation since t=0)
                    current_rotor_angle = ROTATION_SPEED * t_now

                    # Generate voltage trace for the SCROLL_WINDOW history
                    points = []
                    coil_angle = FINAL_COIL_ANGLES[coil_name]
                    prev_flux = None

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
                            amplitude=VOLTAGE_AMPLITUDE,
                            influence_width=INFLUENCE_WIDTH
                        )

                        # Calculate voltage (V = -dFlux/dt)
                        if prev_flux is not None:
                            voltage = -(flux - prev_flux) / dt_window
                        else:
                            voltage = 0.0

                        prev_flux = flux

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

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # Add all objects
        self.add(generator_group, stacked_graphs_group, graphs_title, curves)

        # Initial wait
        self.wait(1)

        # Run the full simulation
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=30.0,  # Slow-mo: 4s physics stretched to 30s real-time
            rate_func=linear
        )

        # Final wait
        self.wait(1)
