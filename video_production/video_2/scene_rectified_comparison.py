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
