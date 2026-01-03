from manim import *
import numpy as np


class ZeroSumStackScene(Scene):
    """
    Demonstrates that three-phase voltages always sum to zero with a stack-and-cancel bar visualization.

    Visual elements:
    - LEFT: Axes showing sinusoidal waveforms for phases A, B, C with sweep line
    - RIGHT: Vertical stack bar visualization showing positive values stacking up,
             negative values stacking down, always returning to zero line

    The stack visualization updates in real-time as the sweep line moves, providing
    continuous visual proof that the three phases sum to zero at every instant.

    Animation sequence:
    1. Draw axes and three phase curves
    2. Show equation "A + B + C = ?"
    3. Animate sweep line across graph with real-time stack bar updating
    4. Transform "?" to "0" and show trig identity
    """

    def construct(self):
        # ============================================================
        # PARAMETERS
        # ============================================================
        AMPLITUDE = 2.0
        CYCLES = 1
        OMEGA = 2 * PI  # Angular frequency (1 cycle per unit time)
        SIMULATION_TIME = CYCLES  # 1 cycle = 1 time unit

        # Phase offsets (in radians)
        PHASE_A = 0
        PHASE_B = 2 * PI / 3  # 120 degrees
        PHASE_C = 4 * PI / 3  # 240 degrees

        # Colors
        COLOR_A = BLUE
        COLOR_B = ORANGE
        COLOR_C = GREEN
        COLOR_SUM = YELLOW

        # Stack bar dimensions
        BAR_WIDTH = 0.6
        STACK_CENTER_X = 5.5  # X position for stack visualization
        ZERO_LINE_Y = 0  # Y position for zero reference line
        VALUE_SCALE = 1.0  # Scale factor for bar heights (1 unit = 1 unit on screen)

        # ============================================================
        # WAVE FUNCTIONS
        # ============================================================
        def wave_a(t):
            return AMPLITUDE * np.sin(OMEGA * t + PHASE_A)

        def wave_b(t):
            return AMPLITUDE * np.sin(OMEGA * t + PHASE_B)

        def wave_c(t):
            return AMPLITUDE * np.sin(OMEGA * t + PHASE_C)

        # ============================================================
        # AXES SETUP (shifted left to make room for stack viz)
        # ============================================================
        axes = Axes(
            x_range=[0, SIMULATION_TIME, 0.5],
            y_range=[-AMPLITUDE * 1.3, AMPLITUDE * 1.3, AMPLITUDE],
            x_length=8,
            y_length=5,
            axis_config={"include_tip": False, "color": GREY},
        )
        axes.to_edge(LEFT, buff=0.6)

        x_label = axes.get_x_axis_label(Text("Time", font_size=20), edge=RIGHT, direction=DOWN)
        y_label = axes.get_y_axis_label(Text("Voltage", font_size=20).rotate(90 * DEGREES), edge=UP, direction=LEFT)

        # ============================================================
        # CREATE STATIC CURVES
        # ============================================================
        curve_a = axes.plot(wave_a, x_range=[0, SIMULATION_TIME], color=COLOR_A, stroke_width=3)
        curve_b = axes.plot(wave_b, x_range=[0, SIMULATION_TIME], color=COLOR_B, stroke_width=3)
        curve_c = axes.plot(wave_c, x_range=[0, SIMULATION_TIME], color=COLOR_C, stroke_width=3)

        # ============================================================
        # LABELS FOR WAVES
        # ============================================================
        label_a = Text("A", font_size=24, color=COLOR_A)
        label_b = Text("B", font_size=24, color=COLOR_B)
        label_c = Text("C", font_size=24, color=COLOR_C)

        t_label = 0.25
        label_a.next_to(axes.c2p(t_label, wave_a(t_label)), UP, buff=0.1)
        label_b.next_to(axes.c2p(t_label + 0.33, wave_b(t_label + 0.33)), DOWN, buff=0.1)
        label_c.next_to(axes.c2p(t_label + 0.67, wave_c(t_label + 0.67)), DOWN, buff=0.1)

        # ============================================================
        # EQUATION DISPLAY
        # ============================================================
        equation_question = MathTex("A + B + C = ", "?", font_size=36)
        equation_question.to_corner(UR, buff=0.5).shift(LEFT * 0.5)

        equation_zero = MathTex("A + B + C = ", "0", font_size=36)
        equation_zero.move_to(equation_question)

        trig_identity = MathTex(
            r"\sin(\theta) + \sin(\theta + 120°) + \sin(\theta + 240°) = 0",
            font_size=24
        )
        trig_identity.to_edge(DOWN, buff=0.5)

        # ============================================================
        # STACK VISUALIZATION SETUP
        # ============================================================
        # Zero reference line (dashed white line)
        zero_line = DashedLine(
            start=np.array([STACK_CENTER_X - 1.0, ZERO_LINE_Y, 0]),
            end=np.array([STACK_CENTER_X + 1.0, ZERO_LINE_Y, 0]),
            color=WHITE,
            stroke_width=2,
            dash_length=0.1
        )

        # "Stack" label
        stack_label = Text("Sum", font_size=24, color=WHITE)
        stack_label.next_to(zero_line, UP, buff=2.8)

        # Zero label on the line
        zero_label = Text("0", font_size=18, color=WHITE)
        zero_label.next_to(zero_line, LEFT, buff=0.2)

        # ============================================================
        # TIME TRACKER
        # ============================================================
        time_tracker = ValueTracker(0)

        # ============================================================
        # VERTICAL SWEEP LINE
        # ============================================================
        sweep_line = always_redraw(
            lambda: DashedLine(
                start=axes.c2p(time_tracker.get_value(), -AMPLITUDE * 1.2),
                end=axes.c2p(time_tracker.get_value(), AMPLITUDE * 1.2),
                color=WHITE,
                stroke_width=2,
                dash_length=0.1
            )
        )

        # Dots on each curve at the sweep line position
        dot_a = always_redraw(
            lambda: Dot(
                axes.c2p(time_tracker.get_value(), wave_a(time_tracker.get_value())),
                color=COLOR_A,
                radius=0.08
            )
        )
        dot_b = always_redraw(
            lambda: Dot(
                axes.c2p(time_tracker.get_value(), wave_b(time_tracker.get_value())),
                color=COLOR_B,
                radius=0.08
            )
        )
        dot_c = always_redraw(
            lambda: Dot(
                axes.c2p(time_tracker.get_value(), wave_c(time_tracker.get_value())),
                color=COLOR_C,
                radius=0.08
            )
        )

        # ============================================================
        # STACK BAR VISUALIZATION (always_redraw)
        # ============================================================
        def create_stack_bars():
            """Create the stacking bar visualization for current time."""
            t = time_tracker.get_value()

            val_a = wave_a(t)
            val_b = wave_b(t)
            val_c = wave_c(t)

            # Sort values into positive and negative groups
            values = [
                (val_a, COLOR_A, "A"),
                (val_b, COLOR_B, "B"),
                (val_c, COLOR_C, "C")
            ]

            # Separate positive and negative values
            positives = [(v, c, n) for v, c, n in values if v >= 0]
            negatives = [(v, c, n) for v, c, n in values if v < 0]

            # Sort by absolute value (largest first) for stable stacking
            positives.sort(key=lambda x: -abs(x[0]))
            negatives.sort(key=lambda x: -abs(x[0]))

            bars = VGroup()

            # Stack positive values upward from zero line
            current_y = ZERO_LINE_Y
            for val, color, name in positives:
                if abs(val) < 0.01:  # Skip near-zero values
                    continue
                bar_height = val * VALUE_SCALE
                bar = Rectangle(
                    width=BAR_WIDTH,
                    height=abs(bar_height),
                    color=color,
                    fill_opacity=0.7,
                    stroke_width=2
                )
                # Position bar so bottom is at current_y
                bar.move_to(np.array([STACK_CENTER_X, current_y + bar_height / 2, 0]))
                bars.add(bar)

                # Add value label
                val_label = Text(f"{val:.1f}", font_size=14, color=color)
                val_label.move_to(bar.get_center())
                bars.add(val_label)

                current_y += bar_height

            # Stack negative values downward from zero line
            current_y = ZERO_LINE_Y
            for val, color, name in negatives:
                if abs(val) < 0.01:  # Skip near-zero values
                    continue
                bar_height = abs(val) * VALUE_SCALE
                bar = Rectangle(
                    width=BAR_WIDTH,
                    height=bar_height,
                    color=color,
                    fill_opacity=0.7,
                    stroke_width=2
                )
                # Position bar so top is at current_y
                bar.move_to(np.array([STACK_CENTER_X, current_y - bar_height / 2, 0]))
                bars.add(bar)

                # Add value label
                val_label = Text(f"{val:.1f}", font_size=14, color=color)
                val_label.move_to(bar.get_center())
                bars.add(val_label)

                current_y -= bar_height

            return bars

        stack_bars = always_redraw(create_stack_bars)

        # ============================================================
        # SUM INDICATOR (small marker showing final stack position)
        # ============================================================
        def create_sum_indicator():
            """Create a small triangle marker showing where the stack ends (should be at zero)."""
            t = time_tracker.get_value()
            total = wave_a(t) + wave_b(t) + wave_c(t)

            # Small triangle pointing to the sum position
            indicator = Triangle(color=YELLOW, fill_opacity=1.0)
            indicator.scale(0.15)
            indicator.rotate(-90 * DEGREES)  # Point left
            indicator.move_to(np.array([STACK_CENTER_X + BAR_WIDTH / 2 + 0.2, ZERO_LINE_Y + total * VALUE_SCALE, 0]))

            return indicator

        sum_indicator = always_redraw(create_sum_indicator)

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # 1. Draw axes
        self.play(Create(axes), Write(x_label), Write(y_label))
        self.wait(0.3)

        # 2. Draw three phase curves simultaneously
        self.play(
            Create(curve_a),
            Create(curve_b),
            Create(curve_c),
            run_time=3
        )
        self.wait(0.3)

        # 3. Add labels for the phase curves
        self.play(
            FadeIn(label_a),
            FadeIn(label_b),
            FadeIn(label_c),
        )
        self.wait(0.3)

        # 4. Show the equation with question mark
        self.play(Write(equation_question))
        self.wait(0.3)

        # 5. Add stack visualization elements
        self.play(
            Create(zero_line),
            FadeIn(zero_label),
            FadeIn(stack_label),
            run_time=1
        )
        self.wait(0.3)

        # 6. Add sweep line, dots, and stack bars
        self.add(sweep_line, dot_a, dot_b, dot_c, stack_bars, sum_indicator)

        # 7. Animate sweep across the full simulation time (slow sweep)
        self.play(
            time_tracker.animate.set_value(SIMULATION_TIME),
            run_time=10,  # Slow, meditative pace
            rate_func=linear
        )

        # 8. Remove sweep elements but keep final stack visualization
        self.remove(sweep_line, dot_a, dot_b, dot_c, sum_indicator)
        self.wait(0.5)

        # 9. Transform "?" to "0"
        self.play(
            Transform(equation_question[1], equation_zero[1])
        )
        self.wait(0.5)

        # 10. Show the trig identity
        self.play(Write(trig_identity))
        self.wait(2)
