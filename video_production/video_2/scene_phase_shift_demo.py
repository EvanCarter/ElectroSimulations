from manim import *
import numpy as np


class PhaseShiftDemoScene(Scene):
    """
    Demonstrates that phase shift is simply a horizontal time shift of a waveform.

    Visual elements:
    - Centered graph with sine waves
    - Phase A (BLUE): Original sine wave
    - Phase B (ORANGE): Copy that slides horizontally to show 90 degree phase shift

    Animation sequence:
    1. Draw single sine wave (Phase A, BLUE) - 2.5 cycles
    2. Brief pause
    3. Create overlapping copy (Phase B, ORANGE)
    4. Animate Phase B sliding right by 90 degrees (1/4 cycle)
    5. Add labels "Phase A" and "Phase B"
    6. Show explanatory text: "90 degree phase shift = 1/4 cycle delay"

    Duration: ~6-8 seconds
    """

    def construct(self):
        # ============================================================
        # PARAMETERS
        # ============================================================
        NUM_CYCLES = 2.5
        AMPLITUDE = 2.0
        PHASE_SHIFT_DEGREES = 90
        PHASE_SHIFT_RADIANS = PHASE_SHIFT_DEGREES * DEGREES

        # Graph dimensions - centered and prominent
        X_LENGTH = 10
        Y_LENGTH = 4.5

        # ============================================================
        # AXES SETUP
        # ============================================================
        # x_range covers 2.5 cycles (2.5 * 2*PI)
        x_max = NUM_CYCLES * 2 * PI

        axes = Axes(
            x_range=[0, x_max, PI / 2],
            y_range=[-AMPLITUDE * 1.2, AMPLITUDE * 1.2, AMPLITUDE],
            x_length=X_LENGTH,
            y_length=Y_LENGTH,
            axis_config={"include_tip": False, "color": GREY},
        ).shift(UP * 0.3)

        # X-axis labels (in terms of cycles)
        x_labels = VGroup()
        for i in range(int(NUM_CYCLES) + 1):
            label = MathTex(f"{i}T" if i > 0 else "0", font_size=28)
            label.next_to(axes.c2p(i * 2 * PI, 0), DOWN, buff=0.2)
            x_labels.add(label)

        # ============================================================
        # SINE WAVE FUNCTIONS
        # ============================================================
        def sine_a(x):
            return AMPLITUDE * np.sin(x)

        def sine_b(x):
            # Phase B starts identical to Phase A (will be shifted via animation)
            return AMPLITUDE * np.sin(x)

        # ============================================================
        # CREATE CURVES
        # ============================================================
        # Phase A - the original sine wave
        curve_a = axes.plot(
            sine_a,
            x_range=[0, x_max],
            color=BLUE,
            stroke_width=3,
        )

        # Phase B - initially identical, will slide right
        curve_b = axes.plot(
            sine_b,
            x_range=[0, x_max],
            color=ORANGE,
            stroke_width=3,
        )

        # ============================================================
        # LABELS
        # ============================================================
        label_a = Text("Phase A", font_size=28, color=BLUE)
        label_b = Text("Phase B", font_size=28, color=ORANGE)

        # Position labels at different locations to avoid overlap
        # Phase A label above second peak (x = 5*PI/2)
        label_a.next_to(axes.c2p(5 * PI / 2, AMPLITUDE), UP, buff=0.15)

        # Explanatory text
        explanation_text = Text(
            "90 degree phase shift = 1/4 cycle delay",
            font_size=32,
        ).to_edge(DOWN, buff=0.8)

        # ============================================================
        # CALCULATE SHIFT AMOUNT
        # ============================================================
        # 90 degrees = PI/2 radians = 1/4 of a full cycle (2*PI)
        # Convert to screen units
        shift_x_units = PI / 2  # In graph coordinates
        # Convert to screen coordinates
        point_0 = axes.c2p(0, 0)
        point_shifted = axes.c2p(shift_x_units, 0)
        shift_amount = point_shifted[0] - point_0[0]  # Screen x displacement

        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================

        # 1. Show axes
        self.play(Create(axes), FadeIn(x_labels), run_time=0.8)

        # 2. Draw Phase A sine wave
        self.play(Create(curve_a), run_time=1.5)

        # 3. Brief pause
        self.wait(0.5)

        # 4. Create Phase B as overlapping copy (fade in on top)
        self.play(FadeIn(curve_b), run_time=0.5)

        # 5. Slide Phase B to the right by 90 degrees (1/4 cycle)
        self.play(
            curve_b.animate.shift(RIGHT * shift_amount),
            run_time=1.5,
            rate_func=smooth,
        )

        # 6. Add labels
        # Phase B label below its first trough (shifted, so at x = 3*PI/2)
        label_b.next_to(axes.c2p(3 * PI / 2, -AMPLITUDE), DOWN, buff=0.15)

        self.play(
            FadeIn(label_a),
            FadeIn(label_b),
            run_time=0.5,
        )

        # 7. Show explanation
        self.play(FadeIn(explanation_text), run_time=0.5)

        # 8. Hold for viewing
        self.wait(2)
