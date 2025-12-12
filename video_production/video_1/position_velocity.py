"""
Position/Velocity Analogy - THE KEY TEACHING MOMENT
"Flux is position. Voltage is velocity."
"""
from manim import *
import numpy as np


class PositionVelocityAnalogy(Scene):
    """Ball rolling on track - position and velocity graphs"""

    def construct(self):
        title = Text("The Key Insight", font_size=40, color=YELLOW)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # The punchline
        insight = VGroup(
            Text("Position is to Velocity", font_size=32),
            Text("as", font_size=24, color=GRAY),
            Text("Flux is to Voltage", font_size=32, color=YELLOW)
        ).arrange(DOWN, buff=0.3)

        self.play(Write(insight))
        self.wait(1.5)
        self.play(FadeOut(insight))

        # Track
        track = Line(LEFT * 5, RIGHT * 5, color=GRAY, stroke_width=4)
        track.shift(UP * 2)

        track_label = Text("Ball on Track", font_size=20, color=GRAY)
        track_label.next_to(track, UP)

        # Ball
        ball = Dot(radius=0.2, color=BLUE)
        ball.move_to(track.get_start())

        # Position graph
        pos_axes = Axes(
            x_range=[0, 10, 2], y_range=[-1.2, 1.2, 0.5],
            x_length=5, y_length=1.5, tips=False,
            axis_config={"include_tip": False}
        ).shift(DOWN * 0.2)
        pos_label = Text("Position", font_size=18, color=BLUE)
        pos_label.next_to(pos_axes, LEFT)

        # Velocity graph
        vel_axes = Axes(
            x_range=[0, 10, 2], y_range=[-1.2, 1.2, 0.5],
            x_length=5, y_length=1.5, tips=False,
            axis_config={"include_tip": False}
        ).shift(DOWN * 2.2)
        vel_label = Text("Velocity (derivative)", font_size=18, color=RED)
        vel_label.next_to(vel_axes, LEFT)

        # Build
        self.play(Create(track), Write(track_label))
        self.play(FadeIn(ball))
        self.play(Create(pos_axes), Write(pos_label))
        self.play(Create(vel_axes), Write(vel_label))
        self.wait(0.5)

        # Animation
        time_tracker = ValueTracker(0)
        pos_graph = VMobject().set_stroke(color=BLUE, width=3)
        vel_graph = VMobject().set_stroke(color=RED, width=3)

        def position(t):
            # Smooth curve: starts slow, speeds up, slows down
            return np.sin(t * 0.8)

        def velocity(t):
            # Derivative of position
            return 0.8 * np.cos(t * 0.8)

        def update_ball(mob):
            t = time_tracker.get_value()
            pos = position(t)
            x = track.get_start()[0] + (pos + 1) / 2 * 10  # Map [-1,1] to track
            mob.move_to([x, track.get_y(), 0])

        def update_pos_graph(mob):
            t = time_tracker.get_value()
            if t > 0.1:
                points = [pos_axes.c2p(ti, position(ti)) for ti in np.linspace(0, t, int(t * 20) + 1)]
                if len(points) > 1:
                    mob.set_points_smoothly(points)

        def update_vel_graph(mob):
            t = time_tracker.get_value()
            if t > 0.1:
                points = [vel_axes.c2p(ti, velocity(ti)) for ti in np.linspace(0, t, int(t * 20) + 1)]
                if len(points) > 1:
                    mob.set_points_smoothly(points)

        ball.add_updater(update_ball)
        pos_graph.add_updater(update_pos_graph)
        vel_graph.add_updater(update_vel_graph)

        self.add(pos_graph, vel_graph)

        self.play(time_tracker.animate.set_value(10), run_time=8, rate_func=linear)

        ball.remove_updater(update_ball)
        pos_graph.remove_updater(update_pos_graph)
        vel_graph.remove_updater(update_vel_graph)

        # Annotations
        arrow1 = Arrow(pos_axes.c2p(5, 0.8), pos_axes.c2p(5, 0.2), color=GREEN, buff=0.1)
        note1 = Text("Peak position", font_size=14, color=GREEN)
        note1.next_to(arrow1, RIGHT)

        arrow2 = Arrow(vel_axes.c2p(5, 0), vel_axes.c2p(5, 0), color=ORANGE, buff=0)
        note2 = Text("Zero velocity!", font_size=14, color=ORANGE)
        note2.next_to(arrow2, RIGHT)

        self.play(GrowArrow(arrow1), Write(note1))
        self.play(GrowArrow(arrow2), Write(note2))
        self.wait(1)

        # The punchline returns
        final = Text("Same relationship: Flux → Voltage", font_size=24, color=YELLOW)
        final.to_edge(DOWN)
        self.play(Write(final))
        self.wait(2)


class FluxVoltageParallel(Scene):
    """Show flux and voltage side by side with same derivative relationship"""

    def construct(self):
        title = Text("Flux is Position, Voltage is Velocity", font_size=36)
        title.to_edge(UP)
        self.play(Write(title))

        # Flux graph (like position)
        flux_axes = Axes(
            x_range=[0, 10, 2], y_range=[-1.2, 1.2, 0.5],
            x_length=5, y_length=1.8, tips=False
        ).shift(LEFT * 0 + UP * 1)
        flux_label = Text("Flux Φ (like position)", font_size=18, color=BLUE)
        flux_label.next_to(flux_axes, UP)

        # Voltage graph (like velocity)
        voltage_axes = Axes(
            x_range=[0, 10, 2], y_range=[-1.2, 1.2, 0.5],
            x_length=5, y_length=1.8, tips=False
        ).shift(LEFT * 0 + DOWN * 1.5)
        voltage_label = Text("Voltage V = dΦ/dt (like velocity)", font_size=18, color=RED)
        voltage_label.next_to(voltage_axes, UP)

        self.play(Create(flux_axes), Write(flux_label))
        self.play(Create(voltage_axes), Write(voltage_label))
        self.wait(0.5)

        # Animation
        t_tracker = ValueTracker(0)
        flux_graph = VMobject().set_stroke(color=BLUE, width=4)
        voltage_graph = VMobject().set_stroke(color=RED, width=4)

        def flux(t):
            return np.sin(t * 0.6)

        def voltage(t):
            return 0.6 * np.cos(t * 0.6)

        def update_flux_graph(mob):
            t = t_tracker.get_value()
            if t > 0.1:
                points = [flux_axes.c2p(ti, flux(ti)) for ti in np.linspace(0, t, int(t * 20) + 1)]
                if len(points) > 1:
                    mob.set_points_smoothly(points)

        def update_voltage_graph(mob):
            t = t_tracker.get_value()
            if t > 0.1:
                points = [voltage_axes.c2p(ti, voltage(ti)) for ti in np.linspace(0, t, int(t * 20) + 1)]
                if len(points) > 1:
                    mob.set_points_smoothly(points)

        flux_graph.add_updater(update_flux_graph)
        voltage_graph.add_updater(update_voltage_graph)

        self.add(flux_graph, voltage_graph)

        self.play(t_tracker.animate.set_value(10), run_time=8, rate_func=linear)

        flux_graph.remove_updater(update_flux_graph)
        voltage_graph.remove_updater(update_voltage_graph)

        # Key insight
        insight = VGroup(
            Text("High flux? Irrelevant.", font_size=20, color=BLUE),
            Text("High rate of change? VOLTAGE!", font_size=20, color=RED, weight=BOLD)
        ).arrange(DOWN, buff=0.2)
        insight.to_edge(DOWN)

        self.play(Write(insight[0]))
        self.wait(0.5)
        self.play(Write(insight[1]))
        self.wait(2)
