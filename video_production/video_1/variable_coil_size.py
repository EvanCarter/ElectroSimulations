import manim
from manim import *
import numpy as np

class VariableCoilSize(ThreeDScene):
    def construct(self):
        # --- Config ---
        self.set_camera_orientation(phi=60 * DEGREES, theta=-90 * DEGREES)
        
        MAGNET_RADIUS = 0.6
        MAGNET_SPEED = 3.0
        X_START = -5.0
        X_END = 5.0
        
        # Define Coils to test
        # (Side Length, Label, Color)
        COIL_CONFIGS = [
            (1.5, "Small Coil", TEAL),
            (2.5, "Medium Coil", PURPLE),
            (3.5, "Large Coil", GOLD)
        ]

        # --- Shared Assets ---
        # 1. Magnet (Reused)
        magnet = Cylinder(
            radius=MAGNET_RADIUS, 
            height=0.2, 
            direction=OUT,
            fill_color=RED, 
            fill_opacity=1.0,
            resolution=24
        )
        magnet_label = Text("N", font_size=32, color=WHITE).rotate(PI/2, axis=RIGHT).rotate(PI/2, axis=OUT).move_to(magnet)
        magnet_group = VGroup(magnet, magnet_label)
        magnet_group.move_to(RIGHT * X_START + OUT * 1.0)
        
        # 2. Graph Axes (Fixed)
        axes_flux = Axes(
            x_range=[X_START, X_END, 2],
            y_range=[-0.2, 3.5, 1], # Adjusted for larger potential flux (PI*0.6^2 ~ 1.13, larger square captures all)
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False, "font_size": 16},
            tips=False,
        ).to_corner(UL).shift(DOWN*0.5)
        
        axes_flux.background_rect = BackgroundRectangle(axes_flux, fill_opacity=0.8, color=BLACK)
        flux_label = Text("Flux", font_size=20, color=WHITE).next_to(axes_flux, UP, buff=0.1)

        # We'll just focus on FLUX for this comparison to avoid clutter
        graph_group = VGroup(axes_flux.background_rect, axes_flux, flux_label)
        self.add_fixed_in_frame_mobjects(graph_group)
        
        # --- Physics Math ---
        def get_flux_area(cx, r, square_half_width):
            # Circle centered at cx with radius r.
            # Square centered at 0 with width 2*square_half_width.
            # We want the area of the circle that overlaps with [-w, w].
            # Circle equation: (x-cx)^2 + y^2 = r^2  => y = +/- sqrt(r^2 - (x-cx)^2)
            # Area is integral of 2*y dx.
            # Let u = x - cx. Then area is integral of 2*sqrt(r^2 - u^2) du.
            # Limits in x: max(-w, cx-r) to min(w, cx+r).
            # Limits in u: x - cx.
            
            w = square_half_width
            x_start = max(-w, cx - r)
            x_end = min(w, cx + r)
            
            if x_start >= x_end: return 0.0
            
            def indefinite_circle_area(u):
                # Integral 2*sqrt(r^2 - u^2) du = u*sqrt(r^2-u^2) + r^2*arcsin(u/r)
                # Clamp u to [-r, r] to avoid math domain errors
                u = np.clip(u, -r, r)
                return u * np.sqrt(r**2 - u**2) + (r**2) * np.arcsin(u/r)
            
            return indefinite_circle_area(x_end - cx) - indefinite_circle_area(x_start - cx)

        # Precompute x range
        t_values = np.linspace(X_START, X_END, 300)

        # --- Layout Separator ---
        # Visual line removed per user request
        # separator = Line(LEFT*7, RIGHT*7, color=GREY).shift(UP*0.5)
        # self.add_fixed_in_frame_mobjects(separator)

        # --- Animation Loop ---
        previous_curves = VGroup()
        self.add_fixed_in_frame_mobjects(previous_curves)
        
        # Shift for 3D objects to be in the "bottom window"
        SCENE_SHIFT = DOWN * 2.5
        
        # Initial Magnet Setup
        magnet_group.move_to(RIGHT * X_START + OUT * 1.0 + SCENE_SHIFT)
        
        for i, (side_len, label_text, color) in enumerate(COIL_CONFIGS):
            # 1. Setup Coil
            coil = Square(side_length=side_len, color=color, stroke_width=8)
            coil.set_fill(color, opacity=0.1)
            # Shift coil to bottom window
            coil.move_to(SCENE_SHIFT)
            
            # Label also in bottom window
            label = Text(label_text, font_size=36, color=color)
            label.to_corner(DL).shift(UP*0.5) # Bottom Left of screen
            self.add_fixed_in_frame_mobjects(label)
            
            self.play(FadeIn(coil), Write(label))
            
            # 2. Calculate Curve
            flux_values = [get_flux_area(x, MAGNET_RADIUS, side_len/2) for x in t_values]
            
            # Create Curve Object
            full_points = [axes_flux.c2p(t, f) for t, f in zip(t_values, flux_values)]
            curve = VMobject(color=color, stroke_width=4)
            
            magnet_x = ValueTracker(X_START)
            self.add(magnet_x)
            
            # Updater for curve
            def update_curve(mob):
                curr_x = magnet_x.get_value()
                idx = np.searchsorted(t_values, curr_x, side='right')
                if idx > 0:
                    mob.set_points_as_corners(full_points[:idx])
            
            curve.add_updater(update_curve)
            self.add_fixed_in_frame_mobjects(curve)
            
            # Magnet Updater (with Shift)
            magnet_group.add_updater(lambda m: m.move_to(RIGHT * magnet_x.get_value() + OUT * 1.0 + SCENE_SHIFT))
            self.add(magnet_group)
            
            # 3. Play Animation
            self.play(magnet_x.animate.set_value(X_END), run_time=2.5, rate_func=linear)
            
            # 4. Cleanup for next run
            magnet_group.clear_updaters()
            curve.clear_updaters()
            
            # Reset magnet
            magnet_group.move_to(RIGHT * X_START + OUT * 1.0 + SCENE_SHIFT)
            
            # Ghost comparisons
            # Fade coil out
            self.play(FadeOut(coil), FadeOut(label))
            
            # Make curve ghost
            # current curve remains, but we might want to fade it slightly
            curve.set_stroke(opacity=0.4)
            previous_curves.add(curve) # comparison history
            
        self.wait(2)
