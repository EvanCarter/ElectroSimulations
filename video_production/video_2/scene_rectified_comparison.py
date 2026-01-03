from manim import *
import numpy as np



class RectifiedSideBySideScene(Scene):
    """
    Shows 1-phase, 2-phase, and 3-phase rectified waveforms side by side.
    Demonstrates the progression: valleys get shallower as phases increase.
    """

    def construct(self):
        # ============================================================
        # PARAMETERS
        # ============================================================
        CYCLES = 1.5
        POINTS = 300
        PEAK_VOLTAGE = 1.0
        # Threshold tuned to show progression:
        # 1-phase min = 0, 2-phase min ≈ 0.707, 3-phase min ≈ 0.866
        BATTERY_THRESHOLD = 0.85  # 2-phase dips below, 3-phase stays above

        # ============================================================
        # GENERATE DATA
        # ============================================================
        theta = np.linspace(0, CYCLES * 2 * np.pi, POINTS)
        t = theta / (2 * np.pi)

        # Single-phase full-wave rectified: |sin(θ)|
        single_phase = np.abs(np.sin(theta)) * PEAK_VOLTAGE

        # Two-phase rectified: max of |sin(θ)| and |sin(θ + 90°)|
        # This gives valleys at ~0.707 (cos(45°))
        two_phase = np.maximum(
            np.abs(np.sin(theta)),
            np.abs(np.sin(theta + np.pi/2))
        ) * PEAK_VOLTAGE

        # Three-phase rectified: max of three phases 120° apart
        phase_a = np.abs(np.sin(theta))
        phase_b = np.abs(np.sin(theta - 2*np.pi/3))
        phase_c = np.abs(np.sin(theta - 4*np.pi/3))
        three_phase = np.maximum(np.maximum(phase_a, phase_b), phase_c) * PEAK_VOLTAGE

        # ============================================================
        # LAYOUT - Three graphs stacked horizontally
        # ============================================================
        title = Text("The Valley of Death: 1 vs 2 vs 3 Phase", font_size=32, weight=BOLD)
        title.to_edge(UP, buff=0.3)

        graph_width = 3.8
        graph_height = 2.5

        # Create three axes
        ax_1 = Axes(
            x_range=[0, CYCLES, 0.5],
            y_range=[0, PEAK_VOLTAGE * 1.15, 0.5],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )
        ax_2 = Axes(
            x_range=[0, CYCLES, 0.5],
            y_range=[0, PEAK_VOLTAGE * 1.15, 0.5],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )
        ax_3 = Axes(
            x_range=[0, CYCLES, 0.5],
            y_range=[0, PEAK_VOLTAGE * 1.15, 0.5],
            x_length=graph_width,
            y_length=graph_height,
            axis_config={"include_tip": False, "color": GREY},
        )

        # Titles
        title_1 = Text("1-Phase", font_size=22, weight=BOLD, color=BLUE)
        title_2 = Text("2-Phase", font_size=22, weight=BOLD, color=ORANGE)
        title_3 = Text("3-Phase", font_size=22, weight=BOLD, color=GREEN)

        title_1.next_to(ax_1, UP, buff=0.1)
        title_2.next_to(ax_2, UP, buff=0.1)
        title_3.next_to(ax_3, UP, buff=0.1)

        # Group and arrange
        group_1 = VGroup(ax_1, title_1)
        group_2 = VGroup(ax_2, title_2)
        group_3 = VGroup(ax_3, title_3)

        all_graphs = VGroup(group_1, group_2, group_3).arrange(RIGHT, buff=0.5)
        all_graphs.next_to(title, DOWN, buff=0.4)

        # ============================================================
        # THRESHOLD LINES
        # ============================================================
        thresh_1 = DashedLine(
            ax_1.c2p(0, BATTERY_THRESHOLD),
            ax_1.c2p(CYCLES, BATTERY_THRESHOLD),
            color=YELLOW, stroke_width=2
        )
        thresh_2 = DashedLine(
            ax_2.c2p(0, BATTERY_THRESHOLD),
            ax_2.c2p(CYCLES, BATTERY_THRESHOLD),
            color=YELLOW, stroke_width=2
        )
        thresh_3 = DashedLine(
            ax_3.c2p(0, BATTERY_THRESHOLD),
            ax_3.c2p(CYCLES, BATTERY_THRESHOLD),
            color=YELLOW, stroke_width=2
        )

        thresh_label = Text("Battery Voltage", font_size=14, color=YELLOW)
        thresh_label.next_to(thresh_2, UP, buff=0.05)

        # ============================================================
        # WAVEFORM CURVES
        # ============================================================
        points_1 = [ax_1.c2p(t[i], single_phase[i]) for i in range(len(t))]
        curve_1 = VMobject().set_color(BLUE).set_stroke(width=3)
        curve_1.set_points_as_corners(points_1)

        points_2 = [ax_2.c2p(t[i], two_phase[i]) for i in range(len(t))]
        curve_2 = VMobject().set_color(ORANGE).set_stroke(width=3)
        curve_2.set_points_as_corners(points_2)

        points_3 = [ax_3.c2p(t[i], three_phase[i]) for i in range(len(t))]
        curve_3 = VMobject().set_color(GREEN).set_stroke(width=3)
        curve_3.set_points_as_corners(points_3)

        # ============================================================
        # DEAD ZONE SHADING
        # ============================================================
        def create_dead_zones(ax, waveform, threshold, color):
            zones = VGroup()
            below = waveform < threshold
            in_region = False
            start_idx = 0

            for i, is_below in enumerate(below):
                if is_below and not in_region:
                    start_idx = i
                    in_region = True
                elif not is_below and in_region:
                    pts = []
                    for j in range(start_idx, i + 1):
                        pts.append(ax.c2p(t[j], waveform[j]))
                    for j in range(i, start_idx - 1, -1):
                        pts.append(ax.c2p(t[j], threshold))
                    if len(pts) > 2:
                        zones.add(Polygon(*pts, color=color, fill_opacity=0.5, stroke_width=0))
                    in_region = False

            # Handle case where we end while still in region
            if in_region:
                pts = []
                for j in range(start_idx, len(below)):
                    pts.append(ax.c2p(t[j], waveform[j]))
                for j in range(len(below) - 1, start_idx - 1, -1):
                    pts.append(ax.c2p(t[j], threshold))
                if len(pts) > 2:
                    zones.add(Polygon(*pts, color=color, fill_opacity=0.5, stroke_width=0))

            return zones

        dead_1 = create_dead_zones(ax_1, single_phase, BATTERY_THRESHOLD, RED)
        dead_2 = create_dead_zones(ax_2, two_phase, BATTERY_THRESHOLD, RED)
        dead_3 = create_dead_zones(ax_3, three_phase, BATTERY_THRESHOLD, RED)

        # ============================================================
        # PERCENTAGE LABELS
        # ============================================================
        pct_1 = np.sum(single_phase < BATTERY_THRESHOLD) / len(single_phase) * 100
        pct_2 = np.sum(two_phase < BATTERY_THRESHOLD) / len(two_phase) * 100
        pct_3 = np.sum(three_phase < BATTERY_THRESHOLD) / len(three_phase) * 100

        label_1 = Text(f"Dead: {pct_1:.0f}%", font_size=20, color=RED, weight=BOLD)
        label_2 = Text(f"Dead: {pct_2:.0f}%", font_size=20, color=RED if pct_2 > 0 else GREEN, weight=BOLD)
        label_3 = Text(f"Dead: {pct_3:.0f}%", font_size=20, color=RED if pct_3 > 0 else GREEN, weight=BOLD)

        label_1.next_to(ax_1, DOWN, buff=0.15)
        label_2.next_to(ax_2, DOWN, buff=0.15)
        label_3.next_to(ax_3, DOWN, buff=0.15)

        # ============================================================
        # BOTTOM MESSAGE
        # ============================================================
        message = Text("More phases = shallower valleys = more time charging", font_size=22)
        message.to_edge(DOWN, buff=0.3)

        # ============================================================
        # ANIMATION
        # ============================================================

        self.play(Write(title), run_time=0.8)

        # Show all three axes
        self.play(
            FadeIn(ax_1), FadeIn(ax_2), FadeIn(ax_3),
            FadeIn(title_1), FadeIn(title_2), FadeIn(title_3),
            run_time=0.8
        )

        # Threshold lines
        self.play(
            Create(thresh_1), Create(thresh_2), Create(thresh_3),
            FadeIn(thresh_label),
            run_time=0.6
        )

        # Draw curves one by one
        self.play(Create(curve_1), run_time=1)
        self.play(FadeIn(dead_1), FadeIn(label_1), run_time=0.6)

        self.wait(0.3)

        self.play(Create(curve_2), run_time=1)
        self.play(FadeIn(dead_2), FadeIn(label_2), run_time=0.6)

        self.wait(0.3)

        self.play(Create(curve_3), run_time=1)
        if len(dead_3) > 0:
            self.play(FadeIn(dead_3), run_time=0.3)
        self.play(FadeIn(label_3), run_time=0.5)

        self.wait(0.5)

        # Highlight winner
        winner_box = SurroundingRectangle(group_3, color=GREEN, buff=0.15, stroke_width=3)
        self.play(Create(winner_box), FadeIn(message), run_time=0.8)

        self.wait(2)


class RectificationBreakdownScene(Scene):
    """
    Demonstrates TOTAL CHARGING CURRENT as the SUM of rectified (absolute value) phases.

    PHYSICS: For battery charging with diode rectifiers, each phase contributes current
    through its rectifier diode. The total charging current is the SUM of currents from
    all phases (each rectified to absolute value).

    Sum of rectified phases model:
    - 1-phase: |sin(theta)| * peak
      Min = 0, Max = peak, ripple = 100%
      LOTS of dead time where current = 0

    - 2-phase: |sin(theta)| + |cos(theta)| * peak
      Min = 1.0 * peak (at 0, 90, 180, 270 deg)
      Max = sqrt(2) * peak (~1.414) at 45, 135, etc.
      Ripple ~29%, NO dead time!

    - 3-phase: |sin(theta)| + |sin(theta+120)| + |sin(theta+240)| * peak
      Min = sqrt(3) * peak (~1.732)
      Max = 2.0 * peak
      Ripple ~13%, NO dead time, highest minimum!

    Visual elements:
    - Build-up animations showing raw AC, rectified phases, then sum
    - Battery threshold line (7V) to show dead zones
    - Side-by-side comparison with dead zone highlighting

    Animation sequence:
    1. 3-phase build-up: raw AC -> rectified each phase -> sum them
    2. 2-phase build-up: same process
    3. Side-by-side comparison with battery threshold
    4. Final message about continuous charging

    Expected output:
    - Clear demonstration that 1-phase has dead time (drops to 0)
    - 2-phase and 3-phase never drop below threshold
    - More phases = more continuous charging current
    """

    def construct(self):
        # ============================================================
        # PARAMETERS
        # ============================================================
        CYCLES = 2
        POINTS = 500
        PEAK_VOLTAGE = 10.0  # Real-world voltage scale (phase amplitude)
        BATTERY_THRESHOLD = 7.0  # Threshold below which no charging occurs

        # ============================================================
        # GENERATE DATA - SUM OF RECTIFIED PHASES
        # ============================================================
        theta = np.linspace(0, CYCLES * 2 * np.pi, POINTS)
        t_normalized = theta / (2 * np.pi)  # x-axis in cycles

        # --- 1-PHASE: just |sin| ---
        single_phase_rect = np.abs(np.sin(theta)) * PEAK_VOLTAGE
        # Min = 0, Max = 10V, ripple = 100%

        # --- 2-PHASE: |sin| + |cos| ---
        two_raw_a = np.sin(theta) * PEAK_VOLTAGE
        two_raw_b = np.sin(theta + np.pi / 2) * PEAK_VOLTAGE  # = cos
        two_rect_a = np.abs(np.sin(theta)) * PEAK_VOLTAGE
        two_rect_b = np.abs(np.sin(theta + np.pi / 2)) * PEAK_VOLTAGE
        two_phase_sum = two_rect_a + two_rect_b
        # Min = 10V (at 0, 90, etc), Max = 14.14V (at 45, etc), ripple ~29%

        # --- 3-PHASE: |sin(theta)| + |sin(theta+120)| + |sin(theta+240)| ---
        phase_a = np.sin(theta) * PEAK_VOLTAGE
        phase_b = np.sin(theta + 2 * np.pi / 3) * PEAK_VOLTAGE
        phase_c = np.sin(theta + 4 * np.pi / 3) * PEAK_VOLTAGE
        rect_a = np.abs(np.sin(theta)) * PEAK_VOLTAGE
        rect_b = np.abs(np.sin(theta + 2 * np.pi / 3)) * PEAK_VOLTAGE
        rect_c = np.abs(np.sin(theta + 4 * np.pi / 3)) * PEAK_VOLTAGE
        three_phase_sum = rect_a + rect_b + rect_c
        # Min = 17.32V (sqrt(3) * 10), Max = 20V (2 * 10), ripple ~13%

        # ============================================================
        # HELPER FUNCTION - Create curve from data
        # ============================================================
        def create_curve_on_ax(ax_obj, x_data, y_data, color, stroke_width=3, opacity=0.8):
            points = [ax_obj.c2p(x_data[i], y_data[i]) for i in range(len(x_data))]
            curve = VMobject()
            curve.set_stroke(color=color, width=stroke_width, opacity=opacity)
            curve.set_points_as_corners(points)
            return curve

        # ============================================================
        # AXES SETUP - Single large centered graph (for 3-phase build-up)
        # Y-axis needs to accommodate sum: peak = 2 * PEAK_VOLTAGE for 3-phase
        # ============================================================
        Y_MAX_3PHASE = 2.2 * PEAK_VOLTAGE  # 22V to fit 3-phase sum peak

        ax = Axes(
            x_range=[0, CYCLES, 0.5],
            y_range=[-PEAK_VOLTAGE * 1.2, Y_MAX_3PHASE, 5.0],
            x_length=10,
            y_length=5.5,
            axis_config={"include_tip": False, "color": GREY},
        ).shift(UP * 0.3)

        x_label = Text("Cycles", font_size=18, color=GREY)
        x_label.next_to(ax.x_axis, DOWN, buff=0.2)

        y_label = Text("Voltage", font_size=18, color=GREY)
        y_label.next_to(ax.y_axis, LEFT, buff=0.2).rotate(90 * DEGREES)

        # Zero line for reference
        zero_line = DashedLine(
            ax.c2p(0, 0), ax.c2p(CYCLES, 0),
            color=GREY, stroke_width=1, dash_length=0.1
        )

        # ============================================================
        # DYNAMIC LABEL
        # ============================================================
        label = Text("Raw 3-Phase AC", font_size=28, weight=BOLD)
        label.to_edge(DOWN, buff=0.5)

        # ============================================================
        # PHASE 1: RAW 3-PHASE AC
        # ============================================================
        curve_a_raw = create_curve_on_ax(ax, t_normalized, phase_a, BLUE, opacity=0.7)
        curve_b_raw = create_curve_on_ax(ax, t_normalized, phase_b, ORANGE, opacity=0.7)
        curve_c_raw = create_curve_on_ax(ax, t_normalized, phase_c, GREEN, opacity=0.7)

        # Legend for raw phase
        legend_a = VGroup(
            Line(ORIGIN, RIGHT * 0.4, color=BLUE, stroke_width=3),
            Text("Phase A", font_size=16, color=BLUE)
        ).arrange(RIGHT, buff=0.1)
        legend_b = VGroup(
            Line(ORIGIN, RIGHT * 0.4, color=ORANGE, stroke_width=3),
            Text("Phase B", font_size=16, color=ORANGE)
        ).arrange(RIGHT, buff=0.1)
        legend_c = VGroup(
            Line(ORIGIN, RIGHT * 0.4, color=GREEN, stroke_width=3),
            Text("Phase C", font_size=16, color=GREEN)
        ).arrange(RIGHT, buff=0.1)

        legend = VGroup(legend_a, legend_b, legend_c).arrange(RIGHT, buff=0.5)
        legend.next_to(ax, UP, buff=0.3)

        # ============================================================
        # PHASE 2: RECTIFIED PHASES (absolute value of each)
        # ============================================================
        curve_a_rect = create_curve_on_ax(ax, t_normalized, rect_a, BLUE, stroke_width=2, opacity=0.6)
        curve_b_rect = create_curve_on_ax(ax, t_normalized, rect_b, ORANGE, stroke_width=2, opacity=0.6)
        curve_c_rect = create_curve_on_ax(ax, t_normalized, rect_c, GREEN, stroke_width=2, opacity=0.6)

        label_rect = Text("Rectified: |Phase A| + |Phase B| + |Phase C|", font_size=28, weight=BOLD)
        label_rect.to_edge(DOWN, buff=0.5)

        # ============================================================
        # PHASE 3: SUM OF RECTIFIED PHASES (3-phase total current)
        # ============================================================
        curve_sum_3phase = create_curve_on_ax(ax, t_normalized, three_phase_sum, WHITE, stroke_width=5, opacity=1.0)

        label_sum = Text("Total Charging Current = Sum of Rectified Phases", font_size=28, weight=BOLD)
        label_sum.to_edge(DOWN, buff=0.5)

        # Minimum and peak voltage annotations
        min_sum_3phase = np.min(three_phase_sum)
        max_sum_3phase = np.max(three_phase_sum)
        ripple_pct = (max_sum_3phase - min_sum_3phase) / max_sum_3phase * 100

        min_line = DashedLine(
            ax.c2p(0, min_sum_3phase), ax.c2p(CYCLES, min_sum_3phase),
            color=YELLOW, stroke_width=2
        )
        min_label_text = Text(f"Min = {min_sum_3phase:.1f}V ({ripple_pct:.0f}% ripple)", font_size=16, color=YELLOW)
        min_label_text.next_to(min_line, RIGHT, buff=0.1)

        # ============================================================
        # ANIMATION SEQUENCE - PART 1: 3-PHASE BUILD-UP
        # ============================================================

        # Setup axes
        self.play(Create(ax), FadeIn(x_label), FadeIn(y_label), run_time=0.8)
        self.play(Create(zero_line), run_time=0.3)

        # Phase 1: Draw raw 3-phase AC
        self.play(FadeIn(label), FadeIn(legend), run_time=0.5)
        self.play(
            Create(curve_a_raw),
            Create(curve_b_raw),
            Create(curve_c_raw),
            run_time=2
        )
        self.wait(1)

        # Phase 2: Show rectified phases (absolute value)
        self.play(
            Transform(label, label_rect),
            run_time=0.5
        )
        self.play(
            FadeOut(curve_a_raw),
            FadeOut(curve_b_raw),
            FadeOut(curve_c_raw),
            FadeOut(zero_line),
            run_time=0.5
        )
        self.play(
            Create(curve_a_rect),
            Create(curve_b_rect),
            Create(curve_c_rect),
            run_time=1.5
        )
        self.wait(1)

        # Phase 3: Draw SUM (total charging current)
        self.play(
            Transform(label, label_sum),
            run_time=0.5
        )
        self.play(
            curve_a_rect.animate.set_stroke(opacity=0.3),
            curve_b_rect.animate.set_stroke(opacity=0.3),
            curve_c_rect.animate.set_stroke(opacity=0.3),
            run_time=0.5
        )
        self.play(Create(curve_sum_3phase), run_time=1.5)
        self.wait(0.5)

        # Show minimum voltage line
        self.play(Create(min_line), FadeIn(min_label_text), run_time=0.8)
        self.wait(1)

        # ============================================================
        # TRANSITION: Clear 3-phase, prepare for 2-phase
        # ============================================================
        three_phase_group = VGroup(
            ax, curve_sum_3phase, curve_a_rect, curve_b_rect, curve_c_rect,
            legend, x_label, y_label, min_line, min_label_text
        )

        self.play(
            FadeOut(three_phase_group),
            FadeOut(label),
            run_time=1
        )

        # ============================================================
        # PART 2: 2-PHASE BUILD-UP
        # ============================================================

        # 2-phase sum output: peak = sqrt(2) * PEAK_VOLTAGE (~14.14V)
        Y_MAX_2PHASE = 1.6 * PEAK_VOLTAGE  # ~16V to fit 2-phase sum

        # Create new axes for 2-phase
        ax2 = Axes(
            x_range=[0, CYCLES, 0.5],
            y_range=[-PEAK_VOLTAGE * 1.2, Y_MAX_2PHASE, 5.0],
            x_length=10,
            y_length=5.5,
            axis_config={"include_tip": False, "color": GREY},
        ).shift(UP * 0.3)

        x_label2 = Text("Cycles", font_size=18, color=GREY)
        x_label2.next_to(ax2.x_axis, DOWN, buff=0.2)

        y_label2 = Text("Voltage", font_size=18, color=GREY)
        y_label2.next_to(ax2.y_axis, LEFT, buff=0.2).rotate(90 * DEGREES)

        zero_line2 = DashedLine(
            ax2.c2p(0, 0), ax2.c2p(CYCLES, 0),
            color=GREY, stroke_width=1, dash_length=0.1
        )

        # 2-phase raw curves
        curve_2a_raw = create_curve_on_ax(ax2, t_normalized, two_raw_a, BLUE, opacity=0.7)
        curve_2b_raw = create_curve_on_ax(ax2, t_normalized, two_raw_b, ORANGE, opacity=0.7)

        # 2-phase legend
        legend_2a = VGroup(
            Line(ORIGIN, RIGHT * 0.4, color=BLUE, stroke_width=3),
            Text("Phase A", font_size=16, color=BLUE)
        ).arrange(RIGHT, buff=0.1)
        legend_2b = VGroup(
            Line(ORIGIN, RIGHT * 0.4, color=ORANGE, stroke_width=3),
            Text("Phase B (90 deg)", font_size=16, color=ORANGE)
        ).arrange(RIGHT, buff=0.1)

        legend2 = VGroup(legend_2a, legend_2b).arrange(RIGHT, buff=0.5)
        legend2.next_to(ax2, UP, buff=0.3)

        label_2phase_raw = Text("Raw 2-Phase AC (90 deg apart)", font_size=28, weight=BOLD)
        label_2phase_raw.to_edge(DOWN, buff=0.5)

        # Show 2-phase axes
        self.play(Create(ax2), FadeIn(x_label2), FadeIn(y_label2), run_time=0.8)
        self.play(Create(zero_line2), run_time=0.3)

        # Draw raw 2-phase AC
        self.play(FadeIn(label_2phase_raw), FadeIn(legend2), run_time=0.5)
        self.play(
            Create(curve_2a_raw),
            Create(curve_2b_raw),
            run_time=2
        )
        self.wait(1)

        # 2-phase rectified curves (absolute value)
        curve_2a_rect = create_curve_on_ax(ax2, t_normalized, two_rect_a, BLUE, stroke_width=2, opacity=0.6)
        curve_2b_rect = create_curve_on_ax(ax2, t_normalized, two_rect_b, ORANGE, stroke_width=2, opacity=0.6)

        label_2phase_rect = Text("Rectified: |Phase A| + |Phase B|", font_size=28, weight=BOLD)
        label_2phase_rect.to_edge(DOWN, buff=0.5)

        # Show rectified
        self.play(
            Transform(label_2phase_raw, label_2phase_rect),
            run_time=0.5
        )
        self.play(
            FadeOut(curve_2a_raw),
            FadeOut(curve_2b_raw),
            FadeOut(zero_line2),
            run_time=0.5
        )
        self.play(
            Create(curve_2a_rect),
            Create(curve_2b_rect),
            run_time=1.5
        )
        self.wait(1)

        # 2-phase SUM
        curve_sum_2phase = create_curve_on_ax(ax2, t_normalized, two_phase_sum, WHITE, stroke_width=5, opacity=1.0)

        label_2phase_sum = Text("Total Charging Current = |A| + |B|", font_size=28, weight=BOLD)
        label_2phase_sum.to_edge(DOWN, buff=0.5)

        self.play(
            Transform(label_2phase_raw, label_2phase_sum),
            run_time=0.5
        )
        self.play(
            curve_2a_rect.animate.set_stroke(opacity=0.3),
            curve_2b_rect.animate.set_stroke(opacity=0.3),
            run_time=0.5
        )
        self.play(Create(curve_sum_2phase), run_time=1.5)
        self.wait(0.5)

        # 2-phase minimum voltage annotation
        min_sum_2phase = np.min(two_phase_sum)
        max_sum_2phase = np.max(two_phase_sum)
        ripple_pct_2phase = (max_sum_2phase - min_sum_2phase) / max_sum_2phase * 100

        min_line2 = DashedLine(
            ax2.c2p(0, min_sum_2phase), ax2.c2p(CYCLES, min_sum_2phase),
            color=YELLOW, stroke_width=2
        )
        min_label2 = Text(f"Min = {min_sum_2phase:.1f}V ({ripple_pct_2phase:.0f}% ripple)", font_size=16, color=YELLOW)
        min_label2.next_to(min_line2, RIGHT, buff=0.1)

        self.play(Create(min_line2), FadeIn(min_label2), run_time=0.8)
        self.wait(1)

        # ============================================================
        # TRANSITION: Clear 2-phase, prepare for comparison
        # ============================================================
        two_phase_group = VGroup(
            ax2, curve_sum_2phase, curve_2a_rect, curve_2b_rect,
            legend2, x_label2, y_label2, min_line2, min_label2
        )

        self.play(
            FadeOut(two_phase_group),
            FadeOut(label_2phase_raw),
            run_time=1
        )

        # ============================================================
        # PART 3: NORMALIZED COMPARISON (1-phase, 2-phase, 3-phase)
        # ============================================================

        # Title for comparison section
        comparison_title = Text("Normalized Comparison (80% threshold)", font_size=32, weight=BOLD)
        comparison_title.to_edge(UP, buff=0.4)

        # Normalize each waveform to its own peak (all peaks = 1.0)
        single_phase_normalized = single_phase_rect / np.max(single_phase_rect)  # peak=1, min=0
        two_phase_normalized = two_phase_sum / np.max(two_phase_sum)  # peak=1, min~0.707
        three_phase_normalized = three_phase_sum / np.max(three_phase_sum)  # peak=1, min~0.866

        # Threshold at 80% of peak
        THRESHOLD_PERCENT = 0.80

        # Create 3 comparison axes - smaller and well-spaced
        COMP_GRAPH_WIDTH = 3.5
        COMP_GRAPH_HEIGHT = 2.8
        COMP_BUFF = 0.6

        # Y-axis from 0 to 1.0 (normalized scale)
        y_max_comp = 1.1  # Slightly above 1.0 for headroom
        y_step = 0.2

        ax_1phase = Axes(
            x_range=[0, CYCLES, 0.5],
            y_range=[0, y_max_comp, y_step],
            x_length=COMP_GRAPH_WIDTH,
            y_length=COMP_GRAPH_HEIGHT,
            axis_config={"include_tip": False, "color": GREY},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0], "font_size": 12},
        )
        ax_2phase = Axes(
            x_range=[0, CYCLES, 0.5],
            y_range=[0, y_max_comp, y_step],
            x_length=COMP_GRAPH_WIDTH,
            y_length=COMP_GRAPH_HEIGHT,
            axis_config={"include_tip": False, "color": GREY},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0], "font_size": 12},
        )
        ax_3phase = Axes(
            x_range=[0, CYCLES, 0.5],
            y_range=[0, y_max_comp, y_step],
            x_length=COMP_GRAPH_WIDTH,
            y_length=COMP_GRAPH_HEIGHT,
            axis_config={"include_tip": False, "color": GREY},
            y_axis_config={"numbers_to_include": [0, 0.2, 0.4, 0.6, 0.8, 1.0], "font_size": 12},
        )

        # Arrange horizontally with good spacing, centered vertically
        comparison_axes = VGroup(ax_1phase, ax_2phase, ax_3phase).arrange(RIGHT, buff=COMP_BUFF)
        comparison_axes.move_to(ORIGIN)  # Center in screen

        # Y-axis unit label on leftmost graph (percentage of peak)
        y_unit_label = Text("% of peak", font_size=14, color=GREY)
        y_unit_label.next_to(ax_1phase.y_axis, UP, buff=0.1)

        # 80% threshold lines on all graphs
        thresh_1 = DashedLine(
            ax_1phase.c2p(0, THRESHOLD_PERCENT),
            ax_1phase.c2p(CYCLES, THRESHOLD_PERCENT),
            color=YELLOW, stroke_width=2
        )
        thresh_2 = DashedLine(
            ax_2phase.c2p(0, THRESHOLD_PERCENT),
            ax_2phase.c2p(CYCLES, THRESHOLD_PERCENT),
            color=YELLOW, stroke_width=2
        )
        thresh_3 = DashedLine(
            ax_3phase.c2p(0, THRESHOLD_PERCENT),
            ax_3phase.c2p(CYCLES, THRESHOLD_PERCENT),
            color=YELLOW, stroke_width=2
        )

        thresh_label = Text("80% threshold", font_size=14, color=YELLOW)
        thresh_label.next_to(thresh_2, UP, buff=0.05)

        # Create curves for each comparison graph using NORMALIZED data
        points_1 = [ax_1phase.c2p(t_normalized[i], single_phase_normalized[i]) for i in range(len(t_normalized))]
        curve_1phase_comp = VMobject().set_stroke(color=BLUE, width=3).set_points_as_corners(points_1)

        points_2 = [ax_2phase.c2p(t_normalized[i], two_phase_normalized[i]) for i in range(len(t_normalized))]
        curve_2phase_comp = VMobject().set_stroke(color=ORANGE, width=3).set_points_as_corners(points_2)

        points_3 = [ax_3phase.c2p(t_normalized[i], three_phase_normalized[i]) for i in range(len(t_normalized))]
        curve_3phase_comp = VMobject().set_stroke(color=GREEN, width=3).set_points_as_corners(points_3)

        # ============================================================
        # DEAD ZONE SHADING (below 80% threshold) - using normalized data
        # ============================================================
        def create_dead_zones(ax_obj, waveform, threshold, color):
            zones = VGroup()
            below = waveform < threshold
            in_region = False
            start_idx = 0

            for i, is_below in enumerate(below):
                if is_below and not in_region:
                    start_idx = i
                    in_region = True
                elif not is_below and in_region:
                    pts = []
                    for j in range(start_idx, i + 1):
                        pts.append(ax_obj.c2p(t_normalized[j], waveform[j]))
                    for j in range(i, start_idx - 1, -1):
                        pts.append(ax_obj.c2p(t_normalized[j], threshold))
                    if len(pts) > 2:
                        zones.add(Polygon(*pts, color=color, fill_opacity=0.5, stroke_width=0))
                    in_region = False

            # Handle case where we end while still in region
            if in_region:
                pts = []
                for j in range(start_idx, len(below)):
                    pts.append(ax_obj.c2p(t_normalized[j], waveform[j]))
                for j in range(len(below) - 1, start_idx - 1, -1):
                    pts.append(ax_obj.c2p(t_normalized[j], threshold))
                if len(pts) > 2:
                    zones.add(Polygon(*pts, color=color, fill_opacity=0.5, stroke_width=0))

            return zones

        dead_1 = create_dead_zones(ax_1phase, single_phase_normalized, THRESHOLD_PERCENT, RED)
        dead_2 = create_dead_zones(ax_2phase, two_phase_normalized, THRESHOLD_PERCENT, RED)
        dead_3 = create_dead_zones(ax_3phase, three_phase_normalized, THRESHOLD_PERCENT, RED)

        # ============================================================
        # CALCULATE STATS FOR NORMALIZED WAVEFORMS
        # ============================================================
        # 1-phase: min=0, peak=1
        min_1_pct = np.min(single_phase_normalized) * 100  # 0%
        ripple_1_pct = (1.0 - np.min(single_phase_normalized)) * 100  # 100%
        dead_pct_1 = np.sum(single_phase_normalized < THRESHOLD_PERCENT) / len(single_phase_normalized) * 100

        # 2-phase: min~0.707 (1/sqrt(2)), peak=1
        min_2_pct = np.min(two_phase_normalized) * 100  # ~70.7%
        ripple_2_pct = (1.0 - np.min(two_phase_normalized)) * 100  # ~29.3%
        dead_pct_2 = np.sum(two_phase_normalized < THRESHOLD_PERCENT) / len(two_phase_normalized) * 100

        # 3-phase: min~0.866 (sqrt(3)/2), peak=1
        min_3_pct = np.min(three_phase_normalized) * 100  # ~86.6%
        ripple_3_pct = (1.0 - np.min(three_phase_normalized)) * 100  # ~13.4%
        dead_pct_3 = np.sum(three_phase_normalized < THRESHOLD_PERCENT) / len(three_phase_normalized) * 100

        # ============================================================
        # LABELS WITH MIN % OF PEAK
        # ============================================================
        label_1 = Text("1-Phase", font_size=18, color=BLUE, weight=BOLD)
        label_1.next_to(ax_1phase, UP, buff=0.15)
        sublabel_1 = Text(f"Min: {min_1_pct:.0f}% of peak", font_size=12, color=BLUE)
        sublabel_1.next_to(label_1, DOWN, buff=0.05)

        label_2 = Text("2-Phase", font_size=18, color=ORANGE, weight=BOLD)
        label_2.next_to(ax_2phase, UP, buff=0.15)
        sublabel_2 = Text(f"Min: {min_2_pct:.1f}% of peak", font_size=12, color=ORANGE)
        sublabel_2.next_to(label_2, DOWN, buff=0.05)

        label_3 = Text("3-Phase", font_size=18, color=GREEN, weight=BOLD)
        label_3.next_to(ax_3phase, UP, buff=0.15)
        sublabel_3 = Text(f"Min: {min_3_pct:.1f}% of peak", font_size=12, color=GREEN)
        sublabel_3.next_to(label_3, DOWN, buff=0.05)

        # ============================================================
        # DEAD PERCENTAGE AND RIPPLE LABELS
        # ============================================================
        dead_label_1 = Text(f"Dead: {dead_pct_1:.0f}%", font_size=16, color=RED, weight=BOLD)
        ripple_label_1 = Text(f"Ripple: {ripple_1_pct:.0f}%", font_size=14, color=GREY)
        bottom_labels_1 = VGroup(dead_label_1, ripple_label_1).arrange(DOWN, buff=0.05)
        bottom_labels_1.next_to(ax_1phase, DOWN, buff=0.15)

        dead_label_2 = Text(f"Dead: {dead_pct_2:.0f}%", font_size=16, color=GREEN if dead_pct_2 == 0 else RED, weight=BOLD)
        ripple_label_2 = Text(f"Ripple: {ripple_2_pct:.0f}%", font_size=14, color=GREY)
        bottom_labels_2 = VGroup(dead_label_2, ripple_label_2).arrange(DOWN, buff=0.05)
        bottom_labels_2.next_to(ax_2phase, DOWN, buff=0.15)

        dead_label_3 = Text(f"Dead: {dead_pct_3:.0f}%", font_size=16, color=GREEN if dead_pct_3 == 0 else RED, weight=BOLD)
        ripple_label_3 = Text(f"Ripple: {ripple_3_pct:.0f}%", font_size=14, color=GREY)
        bottom_labels_3 = VGroup(dead_label_3, ripple_label_3).arrange(DOWN, buff=0.05)
        bottom_labels_3.next_to(ax_3phase, DOWN, buff=0.15)

        label_final = Text("Only 3-phase stays above 80% at all times!", font_size=22, weight=BOLD)
        label_final.to_edge(DOWN, buff=0.3)

        # ============================================================
        # ANIMATION SEQUENCE - COMPARISON
        # ============================================================

        # Show comparison title
        self.play(FadeIn(comparison_title), run_time=0.5)

        # Show all 3 comparison axes with labels
        self.play(
            Create(ax_1phase), Create(ax_2phase), Create(ax_3phase),
            FadeIn(label_1), FadeIn(label_2), FadeIn(label_3),
            FadeIn(sublabel_1), FadeIn(sublabel_2), FadeIn(sublabel_3),
            FadeIn(y_unit_label),
            run_time=0.8
        )

        # Show threshold lines
        self.play(
            Create(thresh_1), Create(thresh_2), Create(thresh_3),
            FadeIn(thresh_label),
            run_time=0.6
        )

        # Draw curves one by one with dead zones
        self.play(Create(curve_1phase_comp), run_time=1)
        self.play(FadeIn(dead_1), FadeIn(bottom_labels_1), run_time=0.6)

        self.wait(0.3)

        self.play(Create(curve_2phase_comp), run_time=1)
        if len(dead_2) > 0:
            self.play(FadeIn(dead_2), run_time=0.3)
        self.play(FadeIn(bottom_labels_2), run_time=0.5)

        self.wait(0.3)

        self.play(Create(curve_3phase_comp), run_time=1)
        if len(dead_3) > 0:
            self.play(FadeIn(dead_3), run_time=0.3)
        self.play(FadeIn(bottom_labels_3), run_time=0.5)

        self.wait(0.5)

        # Highlight the winner (3-phase) - highest minimum, no dead time
        winner_box = SurroundingRectangle(
            VGroup(ax_3phase, label_3, bottom_labels_3),
            color=GREEN, buff=0.15, stroke_width=3
        )
        self.play(Create(winner_box), run_time=0.6)

        # Final message
        self.play(FadeIn(label_final), run_time=0.5)

        self.wait(2)
