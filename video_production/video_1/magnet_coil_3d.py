import manim
from manim import *
import numpy as np

class MagnetCoil3D(ThreeDScene):
    def construct(self):
        # --- Config ---
        # 3D Camera
        # User requested: more head on.
        # phi 75 degrees (closer to ground), theta -90 (side profile)
        self.set_camera_orientation(phi=75 * DEGREES, theta=-90 * DEGREES)
        
        # Physics Parameters
        MAGNET_RADIUS = 0.8  # Increased from 0.5
        COIL_SIDE = MAGNET_RADIUS * 2.0  # Exact fit (1.6)
        MAGNET_SPEED = 2.0
        X_START = -5.0       # Widened range
        X_END = 5.0
        TOTAL_TIME = (X_END - X_START) / MAGNET_SPEED
        
        # --- Assets ---
        
        # 1. The Coil (Square)
        # Positioned at z=0, centered at origin
        coil = Square(side_length=COIL_SIDE, color=ORANGE, stroke_width=8)
        # Make it look 3D by rotating or using a thick line? 
        # Square is 2D, let's keep it flat on xy plane. 
        # But for 3D goodness, let's make it a thin tube or just thick lines.
        # Simple Square is fine for now, maybe add a glow.
        coil.set_fill(ORANGE, opacity=0.1)
        
        coil_label = Text("Coil", font_size=24, color=ORANGE)
        coil_label.to_corner(DL).shift(UP*2 + RIGHT*1)
        # We'll fix label orientation later or just keep it 2D overlay
        
        # 2. The Magnet (Coin)
        # Cylinder: radius 0.5, height 0.2
        # Position z=1
        magnet = Cylinder(
            radius=MAGNET_RADIUS, 
            height=0.2, 
            direction=OUT, # Z-axis
            fill_color=RED, 
            fill_opacity=1.0,
            resolution=24
        )
        # Rotate to verify it looks like a coin (already z-aligned)
        # magnet.set_shading(0.5) # Deprecated
        
        # N/S Labels on Magnet
        # N on bottom (facing coil), S on top? Or N on top?
        # User said "magnet at z=1... produce real flux". 
        # Usually N pointing DOWN produces flux into the coil.
        # Let's put "N" on the top for visibility in 3d view.
        magnet_label = Text("N", font_size=40, color=WHITE).rotate(PI/2, axis=RIGHT).rotate(PI/2, axis=OUT)
        # Actually, let's just group them.
        magnet_group = VGroup(magnet)
        
        # 3. Graphs (2D Overlay)
        # We need a fixed 2D layer. changing camera breaks 2D usually unless fixed_in_frame is used.
        
        # Flux Graph
        axes_flux = Axes(
            x_range=[X_START, X_END, 1],
            y_range=[-0.2, 2.5, 0.5], # Increased max y for larger area (PI*0.8^2 approx 2.0)
            x_length=4,
            y_length=2,
            axis_config={"include_tip": False, "font_size": 16},
            tips=False,
        )
        # axes_flux.add_coordinates() # CAUSES LATEX ERROR
        axes_flux.to_corner(UL)
        axes_flux.background_rect = BackgroundRectangle(axes_flux, fill_opacity=0.8, color=BLACK)
        
        flux_label = Text("Flux", font_size=20, color=YELLOW).next_to(axes_flux, UP, buff=0.1)
        
        # Voltage Graph (EMF)
        # V = - dPhi/dt
        axes_volt = Axes(
            x_range=[X_START, X_END, 1],
            y_range=[-8, 8, 2], # Increased range for spikes
            x_length=4,
            y_length=2,
            axis_config={"include_tip": False, "font_size": 16},
            tips=False,
        )
        # axes_volt.add_coordinates() # CAUSES LATEX ERROR
        axes_volt.next_to(axes_flux, DOWN, buff=0.8)
        axes_volt.background_rect = BackgroundRectangle(axes_volt, fill_opacity=0.8, color=BLACK)
        
        volt_label = Text("Voltage", font_size=20, color=BLUE).next_to(axes_volt, UP, buff=0.1)
        
        # Group for fixed frame
        graph_group = VGroup(
            axes_flux.background_rect, axes_flux, flux_label, 
            axes_volt.background_rect, axes_volt, volt_label
        )
        self.add_fixed_in_frame_mobjects(graph_group)


        # --- Physics Math ---
        def get_circle_square_intersection_area(cx, r, square_half_width):
            """
            Calculate area of circle at (cx, 0) with radius r intersecting 
            square centered at (0,0) with x-bounds [-w, w].
            Since y-bounds same as diameter, we just clip x.
            Effective area is Integral of chord length from max(-w, cx-r) to min(w, cx+r).
            
            Code simplified: Circle is x^2 + y^2 = r^2.
            Area(x) = x*sqrt(r^2 - x^2) + r^2*arcsin(x/r) (Indefinite integral of 2*sqrt(r^2-x^2))
            """
            w = square_half_width
            
            # Intersection bounds
            x_left = max(-w, cx - r)
            x_right = min(w, cx + r)
            
            if x_left >= x_right:
                return 0.0
            
            def indefinite_area_integral(u):
                # Integral of 2 * sqrt(r^2 - u^2) du
                # Clamp u to [-r, r]
                u = np.clip(u, -r, r)
                return u * np.sqrt(r**2 - u**2) + (r**2) * np.arcsin(u/r)

            # Shift bounds by cx to match circle-centered integration
            return indefinite_area_integral(x_right - cx) - indefinite_area_integral(x_left - cx)

        # Precompute Curves
        # We'll plot x from X_START to X_END
        t_values = np.linspace(X_START, X_END, 200) # Using x as parameter
        flux_values = [get_circle_square_intersection_area(x, MAGNET_RADIUS, COIL_SIDE/2) for x in t_values]
        
        # Numerical Derivative for Voltage
        dt = (X_END - X_START) / 200.0
        # V = - dPhi / dt. Since x = v*t, dPhi/dt = dPhi/dx * v. Let's assume v=1 for graph shape, scale later.
        # Actually user said "make sure values are real". 
        # If speed = 2.0.
        voltage_values = -np.gradient(flux_values, dt) * MAGNET_SPEED # Chain rule if x were time. 
        # But here X-axis is POSITION.
        # If we plot vs Position, the shape is dPhi/dx.
        # If we plot vs Time, it's dPhi/dt.
        # Let's label x-axis as "Magnet Position" 
        
        # Create plotted lines
        flux_graph_line = axes_flux.plot_line_graph(t_values, flux_values, add_vertex_dots=False, line_color=YELLOW)
        volt_graph_line = axes_volt.plot_line_graph(t_values, voltage_values, add_vertex_dots=False, line_color=BLUE)
        
        # Masking? We can just create the full line and reveal it, or use a dot.
        # Let's use a dot and a tracing line.
        
        # --- Animation Setup ---
        
        magnet_x = ValueTracker(X_START)
        self.add(magnet_x)
        
        # Magnet Updater
        magnet_group.add_updater(lambda m: m.move_to(RIGHT * magnet_x.get_value() + OUT * 1.0))
        
        # Dots on graphs
        dot_flux = Dot(color=YELLOW)
        dot_flux.add_updater(lambda m: m.move_to(
             axes_flux.c2p(magnet_x.get_value(), get_circle_square_intersection_area(magnet_x.get_value(), MAGNET_RADIUS, COIL_SIDE/2))
        ))
        
        dot_volt = Dot(color=BLUE)
        def get_volt_at_x(x):
            # Recalculate derivative roughly or interpolate
            idx = np.searchsorted(t_values, x)
            idx = np.clip(idx, 0, len(voltage_values)-1)
            return voltage_values[idx]

        dot_volt.add_updater(lambda m: m.move_to(
             axes_volt.c2p(magnet_x.get_value(), get_volt_at_x(magnet_x.get_value()))
        ))
        
        
        self.add_fixed_in_frame_mobjects(dot_flux, dot_volt) 
        
        # --- optimized graphing ---
        # 1. Generate FULL points for the curves in the axes' coordinate system
        # coordinates are list of [x, y, 0]
        full_flux_points = [
            axes_flux.c2p(t, f) for t, f in zip(t_values, flux_values)
        ]
        full_volt_points = [
            axes_volt.c2p(t, v) for t, v in zip(t_values, voltage_values)
        ]
        
        # 2. Create the display objects
        display_flux_curve = VMobject(color=YELLOW, stroke_width=4)
        display_volt_curve = VMobject(color=BLUE, stroke_width=4)
        
        # 3. Add updaters to slice the points based on progress
        def update_flux_curve(mob):
            curr_x = magnet_x.get_value()
            # Filter points where the data-x (recovered from point?) 
            # Easier: Find index in t_values
            # slice full_flux_points
            idx = np.searchsorted(t_values, curr_x, side='right')
            if idx > 0:
                # Add current tip point for smoothness?
                # For now just discrete slice is fine with 200 points
                active_points = full_flux_points[:idx]
                mob.set_points_as_corners(active_points)
                
        def update_volt_curve(mob):
            curr_x = magnet_x.get_value()
            idx = np.searchsorted(t_values, curr_x, side='right')
            if idx > 0:
                active_points = full_volt_points[:idx]
                mob.set_points_as_corners(active_points)

        display_flux_curve.add_updater(update_flux_curve)
        display_volt_curve.add_updater(update_volt_curve)
        
        self.add_fixed_in_frame_mobjects(display_flux_curve, display_volt_curve)

        # --- Scene Construction ---
        self.add(coil)
        self.add(magnet_group)
        
        # Field Lines
        # Pointing DOWN (-Z direction) from the magnet
        field_lines = VGroup()
        for dx in [-0.2, 0, 0.2]:
            for dy in [-0.2, 0, 0.2]:
               # Start relative to magnet center. Magnet height is 0.2 (z from 0.9 to 1.1)
               # Let's interact visually.
               # Arrow pointing IN (0, 0, -1)
               arrow = Arrow3D(
                   start=OUT*0.2, end=IN*0.6, color=GREY, thickness=0.01
               ).shift(RIGHT*dx + UP*dy)
               field_lines.add(arrow)
        
        # Attach field lines to magnet
        field_lines.add_updater(lambda m: m.move_to(magnet_group.get_center() + DOWN*0.2)) # Offset slightly if needed
        # Wait, move_to sets the CENTER.
        # We constructed arrow relative to approx (0,0,0).
        # We need to maintain relative positions.
        # Easier: add field_lines to magnet_group? NO, VGroup nesting with updaters can be tricky.
        # Let's just update position.
        
        magnet_group.add(field_lines) # Add to group so it moves with it automatically?
        # If magnet_group has updater, and field_lines is in it, it should move.
        # But we already set updater on magnet_group.

        self.wait(1)
        self.play(magnet_x.animate.set_value(X_END), run_time=TOTAL_TIME, rate_func=linear)
        self.wait(1)

