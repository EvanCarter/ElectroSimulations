from manim import *
from generator import build_rotor, calculate_sinusoidal_flux
import math
import numpy as np


class RPMVoltageDemoScene(Scene):
    """
    Demonstrates "Lever 1: Spin Faster" - how rotation speed affects voltage.

    Shows:
    - Rotor/stator combo (left)
    - RPM dial/display (center-top)
    - Rectified voltage meter/bar (center-bottom)

    The animation varies RPM from slow to fast, showing voltage scale accordingly.
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 2.2
        MAGNET_RADIUS = 0.55
        OFFSET_FROM_EDGE = 0.15
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        NUM_MAGNETS = 2

        # RPM range for the demo
        MIN_RPM = 30
        MAX_RPM = 150

        # Convert RPM to rad/s: RPM * (2*PI / 60)
        def rpm_to_rad_s(rpm):
            return rpm * (2 * PI / 60)

        # ============================================================
        # BUILD GENERATOR (Left Side)
        # ============================================================
        rotor_group = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

        # Stator ring
        stator = Circle(
            radius=DISK_RADIUS + 0.25,
            color=GRAY,
            stroke_width=6,
            stroke_opacity=0.6
        )

        # Single coil at top (12 o'clock) - square coil matching magnet diameter
        coil_angle = PI / 2
        coil_pos = np.array([
            MAGNET_PATH_RADIUS * math.cos(coil_angle),
            MAGNET_PATH_RADIUS * math.sin(coil_angle),
            0
        ])
        coil = Rectangle(
            width=MAGNET_RADIUS * 2.0,  # Match magnet diameter
            height=MAGNET_RADIUS * 2.0,  # Match magnet diameter
            color=ORANGE,
            stroke_width=6
        )
        # Rotate so long side is tangent to circle path
        coil.rotate(coil_angle - PI / 2)
        coil.move_to(coil_pos)

        generator_group = VGroup(stator, rotor_group, coil)
        generator_group.to_edge(LEFT, buff=0.8)
        disk_center = rotor_group.get_center()

        # ============================================================
        # RPM DISPLAY (Top Right)
        # ============================================================
        rpm_tracker = ValueTracker(MIN_RPM)

        rpm_label = Text("RPM", font_size=36, color=WHITE)
        rpm_value = always_redraw(
            lambda: DecimalNumber(
                rpm_tracker.get_value(),
                num_decimal_places=0,
                font_size=72,
                color=YELLOW
            )
        )

        rpm_display = VGroup(rpm_label, rpm_value).arrange(DOWN, buff=0.3)
        rpm_display.to_edge(UP, buff=0.8).shift(RIGHT * 2.5)

        # RPM dial/arc gauge
        dial_center = rpm_display.get_center() + DOWN * 2.2
        dial_radius = 1.3

        # Dial background arc (gray)
        dial_bg = Arc(
            radius=dial_radius,
            start_angle=PI,
            angle=-PI,
            color=GRAY,
            stroke_width=12,
            stroke_opacity=0.3
        ).move_arc_center_to(dial_center)

        # Dial filled arc (gradient from green to red)
        def get_dial_arc():
            current_rpm = rpm_tracker.get_value()
            fill_ratio = (current_rpm - MIN_RPM) / (MAX_RPM - MIN_RPM)
            fill_ratio = max(0.01, min(1.0, fill_ratio))  # Clamp

            # Color interpolation: green -> yellow -> red
            if fill_ratio < 0.5:
                color = interpolate_color(GREEN, YELLOW, fill_ratio * 2)
            else:
                color = interpolate_color(YELLOW, RED, (fill_ratio - 0.5) * 2)

            arc = Arc(
                radius=dial_radius,
                start_angle=PI,
                angle=-PI * fill_ratio,
                color=color,
                stroke_width=12
            ).move_arc_center_to(dial_center)
            return arc

        dial_arc = always_redraw(get_dial_arc)

        # Dial tick marks
        dial_ticks = VGroup()
        for i in range(5):
            tick_angle = PI - (i / 4) * PI
            tick_start = dial_center + dial_radius * 0.85 * np.array([math.cos(tick_angle), math.sin(tick_angle), 0])
            tick_end = dial_center + dial_radius * 1.05 * np.array([math.cos(tick_angle), math.sin(tick_angle), 0])
            tick = Line(tick_start, tick_end, color=WHITE, stroke_width=2)
            dial_ticks.add(tick)

        # Min/Max labels
        min_label = Text(str(MIN_RPM), font_size=20, color=GRAY).next_to(dial_bg.get_start(), DOWN, buff=0.1)
        max_label = Text(str(MAX_RPM), font_size=20, color=GRAY).next_to(dial_bg.get_end(), DOWN, buff=0.1)

        dial_group = VGroup(dial_bg, dial_arc, dial_ticks, min_label, max_label)

        # ============================================================
        # VOLTAGE METER (Bottom Right)
        # ============================================================
        # Vertical bar meter showing rectified voltage

        meter_label = Text("Rectified Voltage", font_size=28, color=WHITE)

        bar_width = 0.8
        bar_height = 3.5

        # Bar background
        bar_bg = Rectangle(
            width=bar_width,
            height=bar_height,
            color=GRAY,
            stroke_width=2,
            fill_opacity=0.2
        )

        # Reference voltage at base RPM for scaling
        BASE_VOLTAGE = 50  # Arbitrary units at MIN_RPM

        def get_voltage_bar():
            current_rpm = rpm_tracker.get_value()
            # Voltage scales linearly with RPM (angular velocity)
            voltage_ratio = current_rpm / MIN_RPM
            normalized_height = min(1.0, voltage_ratio / (MAX_RPM / MIN_RPM))

            # Color based on level
            if normalized_height < 0.5:
                color = interpolate_color(GREEN, YELLOW, normalized_height * 2)
            else:
                color = interpolate_color(YELLOW, RED, (normalized_height - 0.5) * 2)

            bar = Rectangle(
                width=bar_width - 0.1,
                height=max(0.05, bar_height * normalized_height),
                color=color,
                fill_opacity=0.8,
                stroke_width=0
            )
            bar.align_to(bar_bg, DOWN)
            bar.move_to(bar_bg.get_center(), coor_mask=np.array([1, 0, 0]))
            return bar

        voltage_bar = always_redraw(get_voltage_bar)

        # Voltage value display
        def get_voltage_value():
            current_rpm = rpm_tracker.get_value()
            voltage = BASE_VOLTAGE * (current_rpm / MIN_RPM)
            return DecimalNumber(
                voltage,
                num_decimal_places=0,
                font_size=36,
                color=WHITE,
                unit="V"
            )

        voltage_value = always_redraw(get_voltage_value)

        # Arrange meter
        meter_group = VGroup(bar_bg, voltage_bar)
        meter_label.next_to(meter_group, UP, buff=0.3)
        voltage_value_container = always_redraw(
            lambda: get_voltage_value().next_to(meter_group, DOWN, buff=0.3)
        )

        full_meter = VGroup(meter_label, meter_group, voltage_value_container)
        full_meter.move_to(dial_center + DOWN * 1.8)

        # ============================================================
        # ROTOR ROTATION UPDATER
        # ============================================================
        # Rotor speed matches RPM tracker

        def update_rotor(mob, dt):
            current_rpm = rpm_tracker.get_value()
            angular_speed = rpm_to_rad_s(current_rpm)
            mob.rotate(-angular_speed * dt, about_point=disk_center)

        rotor_group.add_updater(update_rotor)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # Initial setup
        self.add(generator_group)
        self.add(rpm_display, dial_bg, dial_arc, dial_ticks, min_label, max_label)
        self.add(meter_label, bar_bg, voltage_bar, voltage_value_container)

        self.wait(1)

        # Ramp up RPM slowly
        self.play(
            rpm_tracker.animate.set_value(MAX_RPM * 0.5),
            run_time=3,
            rate_func=smooth
        )
        self.wait(0.5)

        # Continue to max
        self.play(
            rpm_tracker.animate.set_value(MAX_RPM),
            run_time=2,
            rate_func=smooth
        )
        self.wait(1)

        # Ramp back down
        self.play(
            rpm_tracker.animate.set_value(MIN_RPM * 1.5),
            run_time=2,
            rate_func=smooth
        )
        self.wait(0.5)

        # Quick pulse up and down
        self.play(
            rpm_tracker.animate.set_value(MAX_RPM * 0.7),
            run_time=1,
            rate_func=smooth
        )
        self.play(
            rpm_tracker.animate.set_value(MIN_RPM),
            run_time=1.5,
            rate_func=smooth
        )

        self.wait(1)


class CoilWrapsDemoScene(Scene):
    """
    Demonstrates "Lever 2: More Wraps Per Coil" - how adding more wire turns increases voltage.

    Shows:
    - Rotor/stator combo (left) - spinning at constant 60 RPM
    - Turns counter display (top right)
    - Coil visualization as nested concentric rings (center right)
    - Voltage meter bar (bottom right)
    - Formula V proportional to N

    The animation steps through different turn counts showing voltage scale proportionally.
    """

    def construct(self):
        # ============================================================
        # PHYSICAL CONSTANTS
        # ============================================================
        DISK_RADIUS = 2.2
        MAGNET_RADIUS = 0.55
        OFFSET_FROM_EDGE = 0.15
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        NUM_MAGNETS = 2

        # Turns range for the demo
        MIN_TURNS = 1
        MAX_TURNS = 10
        CONSTANT_RPM = 60
        BASE_VOLTAGE = 10  # Voltage per turn

        # Convert RPM to rad/s: RPM * (2*PI / 60)
        def rpm_to_rad_s(rpm):
            return rpm * (2 * PI / 60)

        # ============================================================
        # BUILD GENERATOR (Left Side)
        # ============================================================
        rotor_group = build_rotor(NUM_MAGNETS, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS)

        # Stator ring
        stator = Circle(
            radius=DISK_RADIUS + 0.25,
            color=GRAY,
            stroke_width=6,
            stroke_opacity=0.6
        )

        # Single coil at top (12 o'clock) - square coil matching magnet diameter
        coil_angle = PI / 2
        coil_pos = np.array([
            MAGNET_PATH_RADIUS * math.cos(coil_angle),
            MAGNET_PATH_RADIUS * math.sin(coil_angle),
            0
        ])
        coil = Rectangle(
            width=MAGNET_RADIUS * 2.0,  # Match magnet diameter
            height=MAGNET_RADIUS * 2.0,  # Match magnet diameter
            color=ORANGE,
            stroke_width=6
        )
        # Rotate so long side is tangent to circle path
        coil.rotate(coil_angle - PI / 2)
        coil.move_to(coil_pos)

        generator_group = VGroup(stator, rotor_group, coil)
        generator_group.to_edge(LEFT, buff=0.8)
        disk_center = rotor_group.get_center()

        # ============================================================
        # TURNS DISPLAY (Top Right)
        # ============================================================
        turns_tracker = ValueTracker(MIN_TURNS)

        turns_label = Text("Turns", font_size=36, color=WHITE)
        turns_value = always_redraw(
            lambda: DecimalNumber(
                turns_tracker.get_value(),
                num_decimal_places=0,
                font_size=72,
                color=ORANGE
            )
        )

        turns_display = VGroup(turns_label, turns_value).arrange(DOWN, buff=0.3)
        turns_display.to_edge(UP, buff=0.8).shift(RIGHT * 2.5)

        # ============================================================
        # COIL VISUALIZATION (Center of screen) - Nested concentric rings
        # ============================================================
        coil_viz_center = ORIGIN + UP * 0.5
        BASE_COIL_RADIUS = 0.3
        RING_SPACING = 0.08

        def get_coil_viz():
            current_turns = int(turns_tracker.get_value())
            rings = VGroup()
            for i in range(current_turns):
                radius = BASE_COIL_RADIUS + i * RING_SPACING
                # Increase opacity for outer rings
                opacity = 0.4 + 0.6 * (i / max(1, MAX_TURNS - 1))
                ring = Circle(
                    radius=radius,
                    color=ORANGE,
                    stroke_width=4,
                    stroke_opacity=opacity
                )
                rings.add(ring)
            rings.move_to(coil_viz_center)
            return rings

        coil_viz = always_redraw(get_coil_viz)

        # ============================================================
        # VOLTAGE METER (Bottom Right)
        # ============================================================
        meter_label = Text("Voltage", font_size=28, color=WHITE)

        bar_width = 0.8
        bar_height = 3.0

        # Bar background
        bar_bg = Rectangle(
            width=bar_width,
            height=bar_height,
            color=GRAY,
            stroke_width=2,
            fill_opacity=0.2
        )

        def get_voltage_bar():
            current_turns = turns_tracker.get_value()
            # Voltage scales linearly with turns
            voltage_ratio = current_turns / MAX_TURNS
            normalized_height = min(1.0, voltage_ratio)

            # Color based on level: green -> yellow -> red
            if normalized_height < 0.5:
                color = interpolate_color(GREEN, YELLOW, normalized_height * 2)
            else:
                color = interpolate_color(YELLOW, RED, (normalized_height - 0.5) * 2)

            bar = Rectangle(
                width=bar_width - 0.1,
                height=max(0.05, bar_height * normalized_height),
                color=color,
                fill_opacity=0.8,
                stroke_width=0
            )
            bar.align_to(bar_bg, DOWN)
            bar.move_to(bar_bg.get_center(), coor_mask=np.array([1, 0, 0]))
            return bar

        voltage_bar = always_redraw(get_voltage_bar)

        # Voltage value display
        def get_voltage_value():
            current_turns = turns_tracker.get_value()
            voltage = BASE_VOLTAGE * current_turns
            return DecimalNumber(
                voltage,
                num_decimal_places=0,
                font_size=36,
                color=WHITE,
                unit="V"
            )

        voltage_value = always_redraw(get_voltage_value)

        # Arrange meter (independent position - right side, lower)
        meter_group = VGroup(bar_bg, voltage_bar)
        meter_group.move_to(RIGHT * 4.5 + DOWN * 1.0)
        meter_label.next_to(meter_group, UP, buff=0.3)
        voltage_value_container = always_redraw(
            lambda: get_voltage_value().next_to(meter_group, DOWN, buff=0.3)
        )

        # ============================================================
        # ROTOR ROTATION UPDATER (Constant speed)
        # ============================================================
        angular_speed = rpm_to_rad_s(CONSTANT_RPM)

        def update_rotor(mob, dt):
            mob.rotate(-angular_speed * dt, about_point=disk_center)

        rotor_group.add_updater(update_rotor)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # Initial setup
        self.add(generator_group)
        self.add(turns_display)
        self.add(coil_viz)
        self.add(meter_label, bar_bg, voltage_bar, voltage_value_container)

        self.wait(1)

        # Step through turns: 1 -> 2 -> 3 -> 5 -> 10
        turn_sequence = [2, 3, 5, 10]
        for target_turns in turn_sequence:
            self.play(
                turns_tracker.animate.set_value(target_turns),
                run_time=1.0,
                rate_func=smooth
            )
            self.wait(0.5)

        self.wait(0.5)

        # Back down to 1
        self.play(
            turns_tracker.animate.set_value(MIN_TURNS),
            run_time=1.5,
            rate_func=smooth
        )
        self.wait(0.5)

        # Quick ramp to max (10)
        self.play(
            turns_tracker.animate.set_value(MAX_TURNS),
            run_time=2.0,
            rate_func=smooth
        )

        self.wait(1)


class VoltageLeversSummaryScene(Scene):
    """
    Summary scene showing all three voltage levers side by side.

    Three columns:
    1. Speed (RPM dial)
    2. Wraps (coil with increasing turns)
    3. Size (growing stator)

    Each with a slider and visual representation.
    """

    def construct(self):
        title = Text("Three Voltage Levers", font_size=48, color=WHITE)
        title.to_edge(UP, buff=0.5)

        # Three columns
        col_positions = [-4, 0, 4]

        # Column 1: Speed
        speed_label = Text("Speed", font_size=32, color=YELLOW)
        speed_icon = VGroup(
            Circle(radius=0.8, color=GRAY, stroke_width=4),
            Arrow(ORIGIN, UP * 0.6, color=YELLOW, buff=0)
        )
        speed_slider = VGroup(
            Rectangle(width=0.3, height=2, color=GRAY, fill_opacity=0.3),
            Rectangle(width=0.25, height=1, color=YELLOW, fill_opacity=0.8).shift(DOWN * 0.5)
        )
        speed_col = VGroup(speed_label, speed_icon, speed_slider).arrange(DOWN, buff=0.5)
        speed_col.move_to(RIGHT * col_positions[0])

        # Column 2: Wraps
        wraps_label = Text("Wraps", font_size=32, color=ORANGE)
        # Coil with multiple turns visualized as nested circles
        wraps_icon = VGroup(*[
            Circle(radius=0.4 + i*0.15, color=ORANGE, stroke_width=3)
            for i in range(4)
        ])
        wraps_slider = VGroup(
            Rectangle(width=0.3, height=2, color=GRAY, fill_opacity=0.3),
            Rectangle(width=0.25, height=1.2, color=ORANGE, fill_opacity=0.8).shift(DOWN * 0.4)
        )
        wraps_col = VGroup(wraps_label, wraps_icon, wraps_slider).arrange(DOWN, buff=0.5)
        wraps_col.move_to(RIGHT * col_positions[1])

        # Column 3: Size
        size_label = Text("Size", font_size=32, color=GREEN)
        size_icon = VGroup(
            Circle(radius=0.5, color=GREEN, stroke_width=2, stroke_opacity=0.4),
            Circle(radius=0.7, color=GREEN, stroke_width=2, stroke_opacity=0.6),
            Circle(radius=0.9, color=GREEN, stroke_width=3)
        )
        size_slider = VGroup(
            Rectangle(width=0.3, height=2, color=GRAY, fill_opacity=0.3),
            Rectangle(width=0.25, height=1.5, color=GREEN, fill_opacity=0.8).shift(DOWN * 0.25)
        )
        size_col = VGroup(size_label, size_icon, size_slider).arrange(DOWN, buff=0.5)
        size_col.move_to(RIGHT * col_positions[2])

        # Formula at bottom
        formula = MathTex(
            r"V = N \cdot B \cdot A \cdot \omega",
            font_size=42,
            color=WHITE
        )
        formula.to_edge(DOWN, buff=0.8)

        # Annotations
        n_label = Text("turns", font_size=20, color=ORANGE).next_to(formula[0][2], DOWN, buff=0.1)
        omega_label = Text("speed", font_size=20, color=YELLOW).next_to(formula[0][-1], DOWN, buff=0.1)
        a_label = Text("area", font_size=20, color=GREEN).next_to(formula[0][6], DOWN, buff=0.1)

        annotations = VGroup(n_label, omega_label, a_label)

        # Animation
        self.play(Write(title))
        self.wait(0.5)

        self.play(
            FadeIn(speed_col, shift=UP),
            FadeIn(wraps_col, shift=UP),
            FadeIn(size_col, shift=UP),
            lag_ratio=0.2
        )
        self.wait(1)

        self.play(Write(formula))
        self.play(FadeIn(annotations))

        self.wait(2)
