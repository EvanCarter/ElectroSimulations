from manim import *
import numpy as np

class RMSComparison(Scene):
    def construct(self):
        # --- Constants & Configuration ---
        AMPLITUDE = 3
        GAPPED_AMPLITUDE = 2
        FREQUENCY = 1.0
        GAP_DURATION = 0.5 # Seconds of zero voltage between pulses
        PULSE_DURATION = 1.0 # Seconds of sine wave
        TOTAL_PERIOD = PULSE_DURATION + GAP_DURATION
        
        # --- Mathematical Functions ---
        def pure_sine(t):
            return AMPLITUDE * np.sin(2 * np.pi * FREQUENCY * t)
        
        def gapped_sine(t):
            # Calculate where we are in the repeated cycle
            cycle_t = t % TOTAL_PERIOD
            if cycle_t < PULSE_DURATION:
                # Map the pulse duration to a full sine wave (0 to pi or 2pi?) 
                # Request said: "sit at zero for a little bit in between each osolation"
                # Standard AC sine is 2pi. Let's say one "oscillation" is a full period.
                # If we want a gap between full waves:
                return GAPPED_AMPLITUDE * np.sin(2 * np.pi * (1/PULSE_DURATION) * cycle_t)
            else:
                return 0

        # Refined gapped sine: The user said "sit at zero... in between each oscillation".
        # A standard full wave is 0 -> 2pi.
        # Let's make the "Pulse" exactly one full sine wave, then a gap.
        def gapped_sine_corrected(t):
            cycle_t = t % TOTAL_PERIOD
            if cycle_t < PULSE_DURATION:
                # We want one full wave (0 to 2pi) in 'PULSE_DURATION' time
                return GAPPED_AMPLITUDE * np.sin(2 * np.pi * (1/PULSE_DURATION) * cycle_t)
            else:
                return 0

        # --- Visual Setup ---
        # Top Axes: Pure Sine
        top_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-10, 10, 2],
            x_length=10, 
            y_length=2.5, 
            axis_config={"include_numbers": False, "tip_shape": StealthTip},
        ).to_edge(UP, buff=1.6) # Moved down a smidge more (1.2 -> 1.6)
        
        top_label = Text("Pure Sine Wave", font_size=24).next_to(top_axes, UP)

        # Bottom Axes: Gapped Sine
        bottom_axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-10, 10, 2],
            x_length=10,
            y_length=2.5,
            axis_config={"include_numbers": False, "tip_shape": StealthTip},
        ).to_edge(DOWN, buff=0.5) # Closer to bottom edge -> More space in middle

        bottom_label = Text("Gapped Sine Wave", font_size=24).next_to(bottom_axes, UP)

        # Plot Graphs
        top_graph = top_axes.plot(pure_sine, color=BLUE, stroke_width=4)
        bottom_graph = bottom_axes.plot(gapped_sine_corrected, color=TEAL, stroke_width=4)

        # --- Animation Sequence ---
        self.play(
            DrawBorderThenFill(top_axes),
            DrawBorderThenFill(bottom_axes),
            Write(top_label),
            Write(bottom_label),
            run_time=1.5
        )
        self.play(
            Create(top_graph),
            Create(bottom_graph),
            run_time=3,
            rate_func=linear
        )
        self.wait()

        # --- Step 1: SQUARE ---
        # "Everything turn those into lines" -> implies we want to see the negative parts flip up 
        # But actually, squaring changes the shape too (sin -> sin^2 is steeper per peak).
        
        # Define Squared Functions
        def pure_sine_squared(t):
            return (pure_sine(t))**2 # Amplitude^2 * sin^2(...) -> 4 * sin^2(...)

        def gapped_sine_squared(t):
            return (gapped_sine_corrected(t))**2

        # Create Squared Graphs
        # Note: y-axis is [-3, 3]. Squared max is 4. We might need to rescale axes or just let it go off?
        # Let's check ranges. 2^2 = 4. Graph goes to 3. 
        # We need to update the axes or clip/scale. 
        # User prompt: "Show two differnet voltage graphs... square up... nice visual transition"
        # Let's Rescale Y-Axis for the Squared View dynamically or just set initial range to fits.
        # It's better to rescale the axes to show the full squared wave.

        # Text Transition
        square_text = Text("Square the Voltage (V²)", font_size=36, color=YELLOW).next_to(bottom_label, UP, buff=0.5)
        
        self.play(Write(square_text))
        
        # Transform Graphs to Squared Versions
        top_graph_sq = top_axes.plot(pure_sine_squared, color=YELLOW, stroke_width=4)
        bottom_graph_sq = bottom_axes.plot(gapped_sine_squared, color=YELLOW, stroke_width=4)

        # To fit y=4, we might need to change the coordinate system scale or just zoom out.
        # Let's simply animate the axes scaling if possible, or just accept it goes high?
        # Actually, let's just use the plot. Manim axes clamp? No, they don't by default.
        # But we defined Y range to 3. 4 is outside.
        # Let's Assume the axes were set up to handle it or we re-setup axes. 
        # Simplest fix: Re-configure axes or just draw it. Let's draw it; it might clip if frame is tight.
        # Let's modify the previous setup to have y_range=[-4, 5] initially to be safe? 
        # Too late for that in this block. Let's just animate the transformation.
        
        self.play(
            ReplacementTransform(top_graph, top_graph_sq),
            ReplacementTransform(bottom_graph, bottom_graph_sq),
            run_time=2
        )
        self.wait(0.5)

        # Show Area (Integration preparation)
        top_area = top_axes.get_area(top_graph_sq, opacity=0.3, color=YELLOW)
        bottom_area = bottom_axes.get_area(bottom_graph_sq, opacity=0.3, color=YELLOW)
        
        self.play(FadeIn(top_area), FadeIn(bottom_area))
        self.wait(0.5)

        # --- Step 2: MEAN ---
        # Calculate Mean Values
        # Pure Sine: Mean of A^2 * sin^2(t) is A^2 / 2.
        MEAN_TOP = (AMPLITUDE**2) / 2
        
        # Gapped Sine: Mean over total period T = 1.5. Pulse = 1.0.
        # Integral over pulse (0 to 1) of A_gapped^2 * sin^2(2pi*t) dt.
        # Integral of sin^2 over full period is 0.5 * Period.
        # Area = (GAPPED_AMPLITUDE**2) * 0.5 * PULSE_DURATION
        # Mean = Total Area / TOTAL_PERIOD
        bottom_area_val = (GAPPED_AMPLITUDE**2) * 0.5 * PULSE_DURATION
        MEAN_BOTTOM = bottom_area_val / TOTAL_PERIOD

        mean_text = Text("Calculate Mean (Average)", font_size=36, color=ORANGE).move_to(square_text)
        self.play(ReplacementTransform(square_text, mean_text))

        # Morph the variable area into a rectangle of constant height (The Mean)
        # We'll represent this by a horizontal line at the Mean Level and a Rect.
        top_mean_line = top_axes.get_horizontal_line(top_axes.c2p(10, MEAN_TOP), color=ORANGE, stroke_width=5)
        bottom_mean_line = bottom_axes.get_horizontal_line(bottom_axes.c2p(10, MEAN_BOTTOM), color=ORANGE, stroke_width=5)
        
        # Numeric Mean Labels
        top_mean_label = Text(f"Mean = {MEAN_TOP:.2f}", color=ORANGE, font_size=24).next_to(top_mean_line, UP)
        bottom_mean_label = Text(f"Mean = {MEAN_BOTTOM:.2f}", color=ORANGE, font_size=24).next_to(bottom_mean_line, UP)

        # Create Rectangles acting as the "flattened" area
        top_mean_rect = top_axes.get_riemann_rectangles(
            top_axes.plot(lambda t: MEAN_TOP), x_range=[0, 10], dx=0.1, color=ORANGE, fill_opacity=0.5, stroke_width=0
        )
        bottom_mean_rect = bottom_axes.get_riemann_rectangles(
            bottom_axes.plot(lambda t: MEAN_BOTTOM), x_range=[0, 10], dx=0.1, color=ORANGE, fill_opacity=0.5, stroke_width=0
        )

        self.play(
            ReplacementTransform(top_area, top_mean_rect),
            ReplacementTransform(bottom_area, bottom_mean_rect),
            Create(top_mean_line),
            Create(bottom_mean_line),
            Write(top_mean_label),
            Write(bottom_mean_label),
            # Fade out the squared curves to emphasize the mean level? 
            # Or keep them phantom. Let's Fade axes lines slightly or just the curves.
            top_graph_sq.animate.set_opacity(0.3),
            bottom_graph_sq.animate.set_opacity(0.3),
            run_time=2
        )
        self.wait(0.5)

        # --- Step 3: ROOT ---
        # Calculate Root of the Mean
        ROOT_TOP = np.sqrt(MEAN_TOP) # sqrt(2) = 1.414
        ROOT_BOTTOM = np.sqrt(MEAN_BOTTOM) # sqrt(1.333) = 1.1547

        root_text = Text("Take the Root (RMS)", font_size=36, color=RED).move_to(mean_text)
        self.play(ReplacementTransform(mean_text, root_text))

        # Show the Root Level
        # This is a line LOWER than the Mean level (since x > 1, sqrt(x) < x for x > 1... wait. 2->1.414. Correct.)
        top_rms_line = top_axes.get_horizontal_line(top_axes.c2p(10, ROOT_TOP), color=RED, stroke_width=6)
        bottom_rms_line = bottom_axes.get_horizontal_line(bottom_axes.c2p(10, ROOT_BOTTOM), color=RED, stroke_width=6)
        
        # RMS Labels in "Middle of screen" (horizontally centered)
        # We can just center them relative to the screen width, but at the right vertical height.
        top_rms_label = Text(f"RMS = {ROOT_TOP:.2f}", color=RED, font_size=24).move_to(top_axes.c2p(5, ROOT_TOP + 1.5))
        bottom_rms_label = Text(f"RMS = {ROOT_BOTTOM:.2f}", color=RED, font_size=24).move_to(bottom_axes.c2p(5, ROOT_BOTTOM + 1.5))

        self.play(
            ReplacementTransform(top_mean_line, top_rms_line),
            ReplacementTransform(bottom_mean_line, bottom_rms_line),
            ReplacementTransform(top_mean_label, top_rms_label),
            ReplacementTransform(bottom_mean_label, bottom_rms_label),
            # Fade out mean rects to just show the level? Or keep them?
            # User wants "pop up on screen". A line popping up is good.
            FadeOut(top_mean_rect),
            FadeOut(bottom_mean_rect),
            run_time=2
        )
        
        self.wait(2)
