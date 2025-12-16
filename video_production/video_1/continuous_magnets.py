import manim
from manim import *
import numpy as np

class ContinuousMagnets(ThreeDScene):
    def construct(self):
        # --- Config ---
        self.set_camera_orientation(phi=75 * DEGREES, theta=-90 * DEGREES)

        # --- Constants ---
        MAGNET_RADIUS = 0.6
        MAGNET_HEIGHT = 0.3
        MAGNET_SPACING = 2.5  # Distance between magnet centers
        COIL_SIDE = 1.6  # 2x magnet radius for good fit

        X_START = -6.0
        X_END = 6.0
        ANIMATION_DURATION = 8.0

        # Magnet configuration: N-S-N-S alternating
        # Each magnet: (x_offset, polarity: 1=North up, -1=South up)
        MAGNETS = [
            (0.0, 1),   # North
            (MAGNET_SPACING, -1),  # South
            (MAGNET_SPACING * 2, 1),   # North
            (MAGNET_SPACING * 3, -1),  # South
        ]

        # --- Layout: Split Screen ---
        SCENE_SHIFT = DOWN * 2.5  # Shift 3D objects down

        # --- 2D Graphs (Fixed in Frame) ---
        # Flux Graph
        axes_flux = Axes(
            x_range=[X_START, X_END, 2],
            y_range=[-1.5, 1.5, 0.5],
            x_length=5,
            y_length=1.8,
            axis_config={"include_tip": False, "font_size": 14},
            tips=False,
        ).to_corner(UL).shift(DOWN * 0.3 + RIGHT * 0.5)

        flux_bg = BackgroundRectangle(axes_flux, fill_opacity=0.85, color=BLACK)
        flux_label = Text("Magnetic Flux (Φ)", font_size=20, color=YELLOW).next_to(axes_flux, UP, buff=0.15)

        # Voltage Graph
        axes_voltage = Axes(
            x_range=[X_START, X_END, 2],
            y_range=[-3.0, 3.0, 1.0],
            x_length=5,
            y_length=1.8,
            axis_config={"include_tip": False, "font_size": 14},
            tips=False,
        ).next_to(axes_flux, DOWN, buff=0.8).align_to(axes_flux, LEFT)

        voltage_bg = BackgroundRectangle(axes_voltage, fill_opacity=0.85, color=BLACK)
        voltage_label = Text("Induced Voltage (dΦ/dt)", font_size=20, color=RED).next_to(axes_voltage, UP, buff=0.15)

        graph_group = VGroup(
            flux_bg, axes_flux, flux_label,
            voltage_bg, axes_voltage, voltage_label
        )
        self.add_fixed_in_frame_mobjects(graph_group)
        self.play(FadeIn(graph_group), run_time=0.5)

        # --- 3D Scene ---
        # Coil
        coil = Square(side_length=COIL_SIDE, color=TEAL, stroke_width=8)
        coil.set_fill(TEAL, opacity=0.1)
        coil.move_to(SCENE_SHIFT)

        coil_label = Text("Coil", font_size=28, color=TEAL)
        coil_label.to_corner(DR).shift(UP * 0.5 + LEFT * 0.5)
        self.add_fixed_in_frame_mobjects(coil_label)

        self.play(FadeIn(coil), Write(coil_label), run_time=0.8)

        # --- Physics Calculation ---
        def get_flux_area(cx, r, square_half_width):
            """Calculate area of circle overlapping with square centered at origin."""
            w = square_half_width
            x_start = max(-w, cx - r)
            x_end = min(w, cx + r)

            if x_start >= x_end:
                return 0.0

            def indefinite_circle_area(u):
                u = np.clip(u, -r, r)
                return u * np.sqrt(r**2 - u**2) + (r**2) * np.arcsin(u/r)

            return indefinite_circle_area(x_end - cx) - indefinite_circle_area(x_start - cx)

        # --- Pre-calculate Curves ---
        t_values = np.linspace(X_START, X_END, 500)

        # Calculate flux for all magnets combined
        flux_values = np.zeros_like(t_values)
        for mag_offset, polarity in MAGNETS:
            for i, x in enumerate(t_values):
                # Magnet position relative to coil
                magnet_x = x + mag_offset
                area = get_flux_area(magnet_x, MAGNET_RADIUS, COIL_SIDE / 2)
                flux_values[i] += polarity * area

        # Calculate voltage as derivative of flux
        # voltage = -dΦ/dt = -dΦ/dx * dx/dt
        # Since we're moving at constant speed, dx/dt is constant, so voltage ∝ dΦ/dx
        dt = t_values[1] - t_values[0]
        voltage_values = -np.gradient(flux_values, dt) * 0.8  # Scale factor for visibility

        # Create curve objects
        flux_curve = VMobject(color=YELLOW, stroke_width=4)
        voltage_curve = VMobject(color=RED, stroke_width=4)

        flux_full_points = [axes_flux.c2p(t, f) for t, f in zip(t_values, flux_values)]
        voltage_full_points = [axes_voltage.c2p(t, v) for t, v in zip(t_values, voltage_values)]

        # --- Create Magnets ---
        magnet_groups = VGroup()

        for mag_offset, polarity in MAGNETS:
            # Cylinder for magnet body
            magnet = Cylinder(
                radius=MAGNET_RADIUS,
                height=MAGNET_HEIGHT,
                direction=OUT,
                fill_color=RED if polarity > 0 else BLUE,
                fill_opacity=1.0,
                resolution=16
            )

            # Label (N or S)
            label_text = "N" if polarity > 0 else "S"
            label = Text(label_text, font_size=32, color=WHITE)
            label.rotate(PI/2, axis=RIGHT).rotate(PI/2, axis=OUT)

            # Field lines (minimal for performance)
            field_group = VGroup()
            num_lines = 6
            for _ in range(num_lines):
                rand_x = np.random.uniform(-0.35 * MAGNET_RADIUS, 0.35 * MAGNET_RADIUS)
                rand_y = np.random.uniform(-0.35 * MAGNET_RADIUS, 0.35 * MAGNET_RADIUS)

                # Direction based on polarity
                line_length = 1.2
                start_z = -line_length if polarity > 0 else line_length
                end_z = line_length if polarity > 0 else -line_length

                start = np.array([rand_x, rand_y, start_z])
                end = np.array([rand_x, rand_y, end_z])

                line = Line3D(
                    start=start,
                    end=end,
                    color=WHITE,
                    thickness=0.008
                )
                field_group.add(line)

            mag_group = VGroup(magnet, label, field_group)
            mag_group.move_to(RIGHT * (X_START - mag_offset) + OUT * 1.0 + SCENE_SHIFT)
            magnet_groups.add(mag_group)

        self.add(*magnet_groups)
        self.play(*[FadeIn(mg) for mg in magnet_groups], run_time=0.8)

        # --- Animation with ValueTracker ---
        position_tracker = ValueTracker(X_START)
        self.add(position_tracker)

        # Updater for flux curve
        def update_flux_curve(mob):
            curr_x = position_tracker.get_value()
            idx = np.searchsorted(t_values, curr_x, side='right')
            if idx > 0:
                mob.set_points_as_corners(flux_full_points[:idx])

        # Updater for voltage curve
        def update_voltage_curve(mob):
            curr_x = position_tracker.get_value()
            idx = np.searchsorted(t_values, curr_x, side='right')
            if idx > 0:
                mob.set_points_as_corners(voltage_full_points[:idx])

        flux_curve.add_updater(update_flux_curve)
        voltage_curve.add_updater(update_voltage_curve)

        self.add_fixed_in_frame_mobjects(flux_curve, voltage_curve)

        # Updater for magnets
        for i, mag_group in enumerate(magnet_groups):
            mag_offset = MAGNETS[i][0]
            mag_group.add_updater(
                lambda m, offset=mag_offset: m.move_to(
                    RIGHT * (position_tracker.get_value() - offset) + OUT * 1.0 + SCENE_SHIFT
                )
            )

        # --- Animate ---
        self.wait(0.5)
        self.play(
            position_tracker.animate.set_value(X_END),
            run_time=ANIMATION_DURATION,
            rate_func=linear
        )
        self.wait(1)

        # Cleanup
        for mag_group in magnet_groups:
            mag_group.clear_updaters()
        flux_curve.clear_updaters()
        voltage_curve.clear_updaters()

        self.wait(1)
