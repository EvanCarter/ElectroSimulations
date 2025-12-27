from manim import *
from generator import (
    build_rotor,
    get_theta_distance,
    get_area_between_circle
)
import math
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
        # MAGNET SETUP
        # ============================================================
        magnet_angles_start = []
        magnet_polarities = []
        for i in range(NUM_MAGNETS):
            theta = (math.pi / 2.0) - (i * (2 * math.pi / NUM_MAGNETS))
            magnet_angles_start.append(theta)
            magnet_polarities.append(i % 2 == 0)

        # ============================================================
        # PHYSICS CALCULATION
        # ============================================================
        def calculate_flux_at_instant(t: float, coil_angle: float) -> float:
            angle_delta = -ROTATION_SPEED * t

            total_flux = 0.0
            for i, start_angle in enumerate(magnet_angles_start):
                current_mag_angle = (start_angle + angle_delta) % (2 * PI)
                dist = get_theta_distance(coil_angle, current_mag_angle)
                area = get_area_between_circle(dist, MAGNET_PATH_RADIUS, MAGNET_RADIUS)

                if magnet_polarities[i]:
                    total_flux += area
                else:
                    total_flux -= area

            return total_flux

        print(f"Static Phase: Calculating physics for {len(coils_config)} coil(s)...")

        from scipy.ndimage import gaussian_filter1d
        import numpy as np

        lookup_steps = 50000
        flux_lookup = []

        for i in range(lookup_steps):
            t_lookup = (i / lookup_steps) * (2 * PI / ROTATION_SPEED)
            flux = calculate_flux_at_instant(t_lookup, PI / 2.0)
            flux_lookup.append(flux)

        flux_lookup_smoothed = gaussian_filter1d(flux_lookup, sigma=100, mode='wrap')

        def get_smoothed_flux_at_angle(t, coil_angle):
            effective_time = t - (PI/2 - coil_angle) / ROTATION_SPEED
            phase = (effective_time * ROTATION_SPEED) % (2 * PI)

            fractional_idx = (phase / (2 * PI)) * lookup_steps
            idx_low = int(fractional_idx) % lookup_steps
            idx_high = (idx_low + 1) % lookup_steps
            alpha = fractional_idx - int(fractional_idx)

            flux_low = flux_lookup_smoothed[idx_low]
            flux_high = flux_lookup_smoothed[idx_high]
            return flux_low + alpha * (flux_high - flux_low)

        coil_data = {}

        for coil_cfg in coils_config:
            voltage_trace = []
            # Fixed coil angle
            coil_angle = (PI / 2.0) - coil_cfg.position_angle

            for step in range(PHYSICS_STEPS):
                t = step * dt

                if step > 0:
                    flux_now = get_smoothed_flux_at_angle(t, coil_angle)
                    flux_prev = get_smoothed_flux_at_angle(t - dt, coil_angle)
                    voltage = (flux_now - flux_prev) / dt
                else:
                    voltage = 0.0

                voltage_trace.append((t, voltage))

            coil_data[coil_cfg.name] = voltage_trace
            print(f"  Coil {coil_cfg.name} at {coil_cfg.position_angle/DEGREES:.0f} deg: {len(voltage_trace)} points")

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


class PhaseShiftRevealScene(Scene):
    """
    All three waveforms start overlapped, then B and C slide horizontally
    to reveal the phase shift as a time delay.
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
        SIMULATION_TIME = 5.0  # Show ~1.25 rotations
        PHYSICS_STEPS = 3000
        dt = SIMULATION_TIME / PHYSICS_STEPS

        # Period of one cycle
        PERIOD = (2 * PI) / ROTATION_SPEED  # Time for one full rotation

        # Phase shifts in time units
        PHASE_SHIFT_B = (120 * DEGREES) / ROTATION_SPEED  # 120° worth of time
        PHASE_SHIFT_C = (240 * DEGREES) / ROTATION_SPEED  # 240° worth of time

        # ============================================================
        # COIL CONFIG (all at same position for base waveform)
        # ============================================================
        coils_config = [
            {"name": "A", "color": BLUE, "shift": 0},
            {"name": "B", "color": ORANGE, "shift": PHASE_SHIFT_B},
            {"name": "C", "color": GREEN, "shift": PHASE_SHIFT_C},
        ]

        # ============================================================
        # MAGNET SETUP
        # ============================================================
        magnet_angles_start = []
        magnet_polarities = []
        for i in range(NUM_MAGNETS):
            theta = (math.pi / 2.0) - (i * (2 * math.pi / NUM_MAGNETS))
            magnet_angles_start.append(theta)
            magnet_polarities.append(i % 2 == 0)

        # ============================================================
        # PHYSICS - Generate base waveform (coil at 12 o'clock)
        # ============================================================
        def calculate_flux_at_instant(t: float, coil_angle: float) -> float:
            angle_delta = -ROTATION_SPEED * t
            total_flux = 0.0
            for i, start_angle in enumerate(magnet_angles_start):
                current_mag_angle = (start_angle + angle_delta) % (2 * PI)
                dist = get_theta_distance(coil_angle, current_mag_angle)
                area = get_area_between_circle(dist, MAGNET_PATH_RADIUS, MAGNET_RADIUS)
                if magnet_polarities[i]:
                    total_flux += area
                else:
                    total_flux -= area
            return total_flux

        print("PhaseShiftReveal: Calculating base waveform...")

        from scipy.ndimage import gaussian_filter1d
        import numpy as np

        lookup_steps = 50000
        flux_lookup = []
        for i in range(lookup_steps):
            t_lookup = (i / lookup_steps) * (2 * PI / ROTATION_SPEED)
            flux = calculate_flux_at_instant(t_lookup, PI / 2.0)
            flux_lookup.append(flux)

        flux_lookup_smoothed = gaussian_filter1d(flux_lookup, sigma=100, mode='wrap')

        def get_smoothed_flux_at_angle(t, coil_angle):
            effective_time = t - (PI/2 - coil_angle) / ROTATION_SPEED
            phase = (effective_time * ROTATION_SPEED) % (2 * PI)
            fractional_idx = (phase / (2 * PI)) * lookup_steps
            idx_low = int(fractional_idx) % lookup_steps
            idx_high = (idx_low + 1) % lookup_steps
            alpha = fractional_idx - int(fractional_idx)
            return flux_lookup_smoothed[idx_low] + alpha * (flux_lookup_smoothed[idx_high] - flux_lookup_smoothed[idx_low])

        # Generate voltage trace for coil at 12 o'clock
        base_voltage_trace = []
        coil_angle = PI / 2.0

        for step in range(PHYSICS_STEPS):
            t = step * dt
            if step > 0:
                flux_now = get_smoothed_flux_at_angle(t, coil_angle)
                flux_prev = get_smoothed_flux_at_angle(t - dt, coil_angle)
                voltage = (flux_now - flux_prev) / dt
            else:
                voltage = 0.0
            base_voltage_trace.append((t, voltage))

        max_voltage = max(abs(v) for _, v in base_voltage_trace) * 1.1

        print(f"  Generated {len(base_voltage_trace)} points, max_voltage={max_voltage:.2f}")

        # ============================================================
        # VISUAL ELEMENTS
        # ============================================================

        # --- GRAPH ---
        ax = Axes(
            x_range=[0, SIMULATION_TIME, 1],
            y_range=[-max_voltage, max_voltage, max_voltage / 2],
            x_length=11,
            y_length=5,
            axis_config={"include_tip": False, "color": GREY},
        )

        title = Text("Phase Shift = Horizontal Time Delay", font_size=32)
        title.next_to(ax, UP, buff=0.3)

        graph_group = VGroup(ax, title)
        graph_group.center()

        # --- PRE-BUILT FULL CURVES ---
        # Build complete curves for each coil (all same shape, will shift B and C)
        def build_curve_points(time_offset=0):
            points = []
            for t_val, v_val in base_voltage_trace:
                x = t_val + time_offset
                if 0 <= x <= SIMULATION_TIME:
                    points.append(ax.c2p(x, v_val))
            return points

        # Create curves - all start at same position (no offset)
        curve_a = VMobject().set_color(BLUE).set_stroke(width=3)
        curve_b = VMobject().set_color(ORANGE).set_stroke(width=3)
        curve_c = VMobject().set_color(GREEN).set_stroke(width=3)

        # Initial points (all same)
        points_a = build_curve_points(0)
        curve_a.set_points_as_corners(points_a)
        curve_b.set_points_as_corners(points_a.copy())
        curve_c.set_points_as_corners(points_a.copy())

        curves = VGroup(curve_a, curve_b, curve_c)

        # --- LEGEND ---
        legend = VGroup(
            VGroup(Line(LEFT * 0.3, RIGHT * 0.3, color=BLUE, stroke_width=3), Text("A (0°)", font_size=20, color=BLUE)).arrange(RIGHT, buff=0.1),
            VGroup(Line(LEFT * 0.3, RIGHT * 0.3, color=ORANGE, stroke_width=3), Text("B (120°)", font_size=20, color=ORANGE)).arrange(RIGHT, buff=0.1),
            VGroup(Line(LEFT * 0.3, RIGHT * 0.3, color=GREEN, stroke_width=3), Text("C (240°)", font_size=20, color=GREEN)).arrange(RIGHT, buff=0.1),
        ).arrange(RIGHT, buff=0.8)
        legend.next_to(ax, DOWN, buff=0.3)

        # ============================================================
        # ANIMATION
        # ============================================================

        self.add(graph_group, legend)

        # Draw curves appearing (all overlapped)
        self.play(Create(curve_a), run_time=1.5)
        self.play(Create(curve_b), Create(curve_c), run_time=0.5)

        self.wait(0.5)

        # Show "all same" label
        same_label = Text("All three coils: same waveform", font_size=24)
        same_label.next_to(ax, DOWN, buff=1.2)
        self.play(FadeIn(same_label))
        self.wait(1)

        # Now shift B and C horizontally
        shift_label = Text("Shifting by phase angle...", font_size=24)
        shift_label.move_to(same_label)
        self.play(FadeOut(same_label), FadeIn(shift_label))

        # Calculate pixel shift for B and C
        # shift in x-axis units = time shift
        x_shift_b = ax.c2p(PHASE_SHIFT_B, 0)[0] - ax.c2p(0, 0)[0]
        x_shift_c = ax.c2p(PHASE_SHIFT_C, 0)[0] - ax.c2p(0, 0)[0]

        self.play(
            curve_b.animate.shift(RIGHT * x_shift_b),
            curve_c.animate.shift(RIGHT * x_shift_c),
            run_time=2,
            rate_func=smooth
        )

        self.play(FadeOut(shift_label))
        self.wait(2)


class TwoPhaseVsSplitPhaseScene(Scene):
    """
    Side-by-side comparison of two-phase (90° offset) vs split-phase (180° offset).
    Generator on left with coils visible, two pre-drawn graphs stacked on right.
    Only the rotor animates.
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
        # MAGNET SETUP
        # ============================================================
        magnet_angles_start = []
        magnet_polarities = []
        for i in range(NUM_MAGNETS):
            theta = (math.pi / 2.0) - (i * (2 * math.pi / NUM_MAGNETS))
            magnet_angles_start.append(theta)
            magnet_polarities.append(i % 2 == 0)

        # ============================================================
        # PHYSICS CALCULATION
        # ============================================================
        def calculate_flux_at_instant(t: float, coil_angle: float) -> float:
            angle_delta = -ROTATION_SPEED * t
            total_flux = 0.0
            for i, start_angle in enumerate(magnet_angles_start):
                current_mag_angle = (start_angle + angle_delta) % (2 * PI)
                dist = get_theta_distance(coil_angle, current_mag_angle)
                area = get_area_between_circle(dist, MAGNET_PATH_RADIUS, MAGNET_RADIUS)
                if magnet_polarities[i]:
                    total_flux += area
                else:
                    total_flux -= area
            return total_flux

        print("TwoPhaseVsSplitPhase: Calculating physics...")

        from scipy.ndimage import gaussian_filter1d
        import numpy as np

        lookup_steps = 50000
        flux_lookup = []
        for i in range(lookup_steps):
            t_lookup = (i / lookup_steps) * (2 * PI / ROTATION_SPEED)
            flux = calculate_flux_at_instant(t_lookup, PI / 2.0)
            flux_lookup.append(flux)

        flux_lookup_smoothed = gaussian_filter1d(flux_lookup, sigma=100, mode='wrap')

        def get_smoothed_flux_at_angle(t, coil_angle):
            effective_time = t - (PI/2 - coil_angle) / ROTATION_SPEED
            phase = (effective_time * ROTATION_SPEED) % (2 * PI)
            fractional_idx = (phase / (2 * PI)) * lookup_steps
            idx_low = int(fractional_idx) % lookup_steps
            idx_high = (idx_low + 1) % lookup_steps
            alpha = fractional_idx - int(fractional_idx)
            return flux_lookup_smoothed[idx_low] + alpha * (flux_lookup_smoothed[idx_high] - flux_lookup_smoothed[idx_low])

        def calculate_voltage_trace(coil_angle):
            """Calculate voltage trace for a coil at fixed position."""
            voltage_trace = []
            for step in range(PHYSICS_STEPS):
                t = step * dt
                if step > 0:
                    flux_now = get_smoothed_flux_at_angle(t, coil_angle)
                    flux_prev = get_smoothed_flux_at_angle(t - dt, coil_angle)
                    voltage = (flux_now - flux_prev) / dt
                else:
                    voltage = 0.0
                voltage_trace.append((t, voltage))
            return voltage_trace

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

        # Calculate voltage traces for each configuration
        two_phase_data = {}
        for coil in two_phase_coils:
            coil_angle = (PI / 2.0) - coil["angle"]
            two_phase_data[coil["name"]] = calculate_voltage_trace(coil_angle)
            print(f"  Two-phase coil {coil['name']} at {coil['angle']/DEGREES:.0f}°: done")

        split_phase_data = {}
        for coil in split_phase_coils:
            coil_angle = (PI / 2.0) - coil["angle"]
            split_phase_data[coil["name"]] = calculate_voltage_trace(coil_angle)
            print(f"  Split-phase coil {coil['name']} at {coil['angle']/DEGREES:.0f}°: done")

        # Find max voltage for graph scaling
        max_voltage = 0.0
        for trace in list(two_phase_data.values()) + list(split_phase_data.values()):
            for _, v in trace:
                max_voltage = max(max_voltage, abs(v))
        max_voltage *= 1.1

        # ============================================================
        # VISUAL ELEMENTS
        # ============================================================

        # --- GENERATOR (Left side) ---
        rotor_group = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

        stator = Circle(
            radius=DISK_RADIUS + 0.3,
            color=GRAY,
            stroke_width=8,
            stroke_opacity=0.5
        )

        # --- COILS ON GENERATOR (12 and 3 o'clock for two-phase visualization) ---
        coil_mobjects = VGroup()
        coil_labels = VGroup()

        # We show the two-phase coil positions (12 and 3 o'clock)
        for coil_cfg in two_phase_coils:
            angle = (PI / 2.0) - coil_cfg["angle"]

            pos = np.array([
                MAGNET_PATH_RADIUS * math.cos(angle),
                MAGNET_PATH_RADIUS * math.sin(angle),
                0
            ])

            coil = DashedVMobject(
                Circle(radius=MAGNET_RADIUS, color=coil_cfg["color"], stroke_width=6),
                num_dashes=12
            ).move_to(pos)

            label = Text(coil_cfg["name"], font_size=28, color=coil_cfg["color"]).next_to(coil, UP, buff=0.15)

            coil_mobjects.add(coil)
            coil_labels.add(label)

        generator_group = VGroup(stator, rotor_group, coil_mobjects, coil_labels)
        generator_group.scale(0.5)
        generator_group.to_corner(UL, buff=0.5)
        disk_center = rotor_group.get_center()

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
        # UPDATER - ONLY FOR ROTOR
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

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        self.add(generator_group, graphs_group, curves)

        self.wait(1)

        # Only animate the rotor spinning
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=SIMULATION_TIME,
            rate_func=linear
        )

        self.wait(2)
