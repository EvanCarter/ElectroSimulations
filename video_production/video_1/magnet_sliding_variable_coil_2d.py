"""
Magnet Sliding Variable Coil 2D Animation
Compare 4 scenarios: 
1. Baseline (Width 2.0, Magnet Dia 1.2)
2. Matched (Width 1.2)
3. Small (Width 0.6)
4. Large (Width 4.0)

Shows Flux and Voltage graphs to demonstrate that smaller coils produce steeper slopes/higher voltage spikes.
"""
from manim import *
import numpy as np

# --- Physics Logic ---

def circle_segment_area(r, x):
    """
    Area of circular segment to the LEFT of vertical line at relative position x.
    Circle center at (0,0).
    """
    if x <= -r: return 0
    if x >= r: return np.pi * r**2
    
    d = abs(x)
    # Area of circular segment = r^2 arccos(d/r) - d * sqrt(r^2 - d^2)
    # This is the area of the "cap" cut off by the chord at distance d from center.
    cap_area = r**2 * np.arccos(d/r) - d * np.sqrt(r**2 - d**2)
    
    if x > 0:
        return np.pi * r**2 - cap_area
    else:
        return cap_area

def calculate_exact_flux(magnet_x, coil_width, magnet_radius, b_field_strength):
    """
    Calculate Flux = B * Intersection Area of Magnet (Circle) and Coil (Rect strip in 2D proj).
    Assume Coil is a rectangle from -width/2 to width/2.
    Magnet is circle at magnet_x.
    Intersect is Area of Circle between (x_left, x_right) of coil relative to magnet.
    """
    # Coil x bounds in world space
    x_left_coil = -coil_width / 2
    x_right_coil = coil_width / 2
    
    # Transform to Magnet-Relative coordinates
    # We want boundaries relative to magnet center (0 means at magnet center)
    # If Boundary is at X_b, and Magnet is at X_m, relative pos is X_b - X_m
    rel_x_left = x_left_coil - magnet_x
    rel_x_right = x_right_coil - magnet_x
    
    # Area = (Area left of Right Edge) - (Area left of Left Edge)
    area = circle_segment_area(magnet_radius, rel_x_right) - circle_segment_area(magnet_radius, rel_x_left)
    
    return b_field_strength * area

def get_voltage(flux_func, t, dt=0.001):
    """ A simple finite difference derivative """
    return -(flux_func(t + dt) - flux_func(t - dt)) / (2 * dt)


class MagnetSlidingVariableCoil(Scene):
    def construct(self):
        # --- Configuration ---
        # Normalize: Magnet Diameter = 1.0 -> Radius = 0.5
        magnet_radius = 0.5
        magnet_diameter = 2 * magnet_radius # 1.0
        b_strength = 1.0
        
        # Motion: Start far left, go to right
        # Coil is at 0. Max width 4.0 (Right edge +2.0).
        # Magnet clears at 2.0 + 0.5 = 2.5.
        # Start X: -5.0 (plenty of room).
        # End X: Previous was 5.0. User wants shorter.
        # "75% of a magnet width earlier". Magnet width = 1.0. 
        # So reduce by ~0.75-1.0. Let's try 4.0.
        start_x = -5.0
        end_x = 4.0 
        
        # Speed: 
        # Distance = 9.0. Speed ~ 2.0 -> 4.5s.
        duration = 4.5
        
        # --- Visual Setup ---
        # 1. Physical Scene (Left)
        phy_center = LEFT * 3.5
        
        # Initial Coil (will update)
        coil = Square(side_length=2.0, color=WHITE, stroke_width=4).move_to(phy_center)
        coil_label = Text("Coil", font_size=20).next_to(coil, DOWN)
        
        # Magnet
        magnet = Circle(radius=magnet_radius, color=RED, fill_opacity=0.5).move_to(phy_center + RIGHT * start_x)
        # N label - Adjust size for smaller magnet
        n_label = Text("N", font_size=24, color=WHITE).move_to(magnet)
        magnet_group = VGroup(magnet, n_label)
        
        self.add(coil, coil_label, magnet_group)
        
        # 2. Graphs (Right)
        # Flux (Top)
        # Max Flux: Area * B = pi * 0.5^2 * 1.0 = 0.785.
        # Range 0 to 1.0 is good.
        flux_axes = Axes(
            x_range=[0, duration, 1],
            y_range=[0, 1.0, 0.25], 
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).to_edge(RIGHT, buff=0.5).to_edge(UP, buff=1.0)
        
        flux_label = Text("Flux", font_size=24).next_to(flux_axes, UP)
        
        # Voltage (Bottom)
        # Voltage spikes will be sharper for tiny coil.
        volt_axes = Axes(
            x_range=[0, duration, 1],
            y_range=[-2.5, 2.5, 1],
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).next_to(flux_axes, DOWN, buff=0.8)
        
        volt_label = Text("Voltage", font_size=24).next_to(volt_axes, UP)
        volt_x_label = Text("Time (s)", font_size=16).next_to(volt_axes, DOWN).shift(RIGHT * 2)
        
        self.add(flux_axes, flux_label, volt_axes, volt_label, volt_x_label)
        
        # Legend Group
        legend_group = VGroup().to_corner(UL).shift(RIGHT * 0.5)

        # Helper to run simulation
        def run_scenario(scenario_name, color, coil_w):
            # 1. Update Legend
            legend_dot = Square(side_length=0.2, color=color, fill_opacity=1, fill_color=color)
            legend_text = Text(f"{scenario_name} (w={coil_w})", font_size=16, color=color)
            entry = VGroup(legend_dot, legend_text).arrange(RIGHT, buff=0.2)
            legend_group.add(entry)
            legend_group.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            # Re-position
            legend_group.to_corner(UL).shift(RIGHT * 0.5)
            self.add(entry)
            
            # 2. Update Coil Visual
            new_coil = Rectangle(width=coil_w, height=2.0, color=WHITE, stroke_width=4).move_to(phy_center)
            
            # Transition to new coil shape
            self.play(Transform(coil, new_coil), run_time=1.0)
            
            # Reset Magnet Position
            magnet_group.move_to(phy_center + RIGHT * start_x)
            magnet.set_color(color)
            magnet.set_fill(opacity=0.5)
            self.play(FadeIn(magnet_group, run_time=0.5))

            # 3. Pre-calculate Data
            num_points = 1000 
            t_values = np.linspace(0, duration, num_points)
            
            flux_points = []
            volt_points = []
            
            for t in t_values:
                # Magnet Position
                progress = t / duration
                curr_x = start_x + (end_x - start_x) * progress
                
                # Flux
                f = calculate_exact_flux(curr_x, coil_w, magnet_radius, b_strength)
                
                # Voltage (Derivative)
                def flux_of_time(time_val):
                    p = time_val / duration
                    if p < 0: p = 0
                    if p > 1: p = 1 
                    x_val = start_x + (end_x - start_x) * p
                    return calculate_exact_flux(x_val, coil_w, magnet_radius, b_strength)
                
                v = get_voltage(flux_of_time, t)
                
                if t <= 0.05 or t >= duration - 0.05: v = 0
                
                flux_points.append(flux_axes.c2p(t, f))
                volt_points.append(volt_axes.c2p(t, v))
                
            # Create curve VMobjects
            flux_curve = VMobject(color=color, stroke_width=3)
            flux_curve.set_points_as_corners([flux_points[0], flux_points[0]])
            
            volt_curve = VMobject(color=color, stroke_width=3)
            volt_curve.set_points_as_corners([volt_points[0], volt_points[0]])
            
            self.add(flux_curve, volt_curve)
            
            # Dots
            flux_dot = Dot(color=color).scale(0.5).move_to(flux_points[0])
            volt_dot = Dot(color=color).scale(0.5).move_to(volt_points[0])
            self.add(flux_dot, volt_dot)

            # 4. Animation
            t_tracker = ValueTracker(0)
            
            def update_scene(mob):
                t = t_tracker.get_value()
                
                # Magnet Position
                progress = t / duration
                curr_x = start_x + (end_x - start_x) * progress
                magnet_group.move_to(phy_center + RIGHT * curr_x)
                
                # Curves & Dots
                idx = int((t / duration) * (num_points - 1))
                if idx < 0: idx = 0
                if idx >= num_points: idx = num_points - 1
                
                current_flux_path = flux_points[:idx+1]
                if len(current_flux_path) > 1:
                    flux_curve.set_points_as_corners(current_flux_path)
                    
                current_volt_path = volt_points[:idx+1]
                if len(current_volt_path) > 1:
                    volt_curve.set_points_as_corners(current_volt_path)
                    
                flux_dot.move_to(flux_points[idx])
                volt_dot.move_to(volt_points[idx])
                
            magnet_group.add_updater(update_scene)
            
            self.play(t_tracker.animate.set_value(duration), run_time=duration, rate_func=linear)
            
            magnet_group.remove_updater(update_scene)
            self.wait(0.5)
            
            # Remove Dots, Keep Curves
            self.remove(flux_dot, volt_dot)
            self.play(FadeOut(magnet_group, run_time=0.5))

        # --- Scenarios ---
        # 1. Baseline: Width 2.0
        run_scenario("Baseline", BLUE, 2.0)
        self.wait(0.5)
        
        # 2. Matched: Width 1.0 (Exact Magnet Width)
        run_scenario("Matched", GREEN, 1.0)
        self.wait(0.5)

        # 3. Small: Width 0.33 (approx 1/3 Magnet Width)
        run_scenario("Small", RED, 0.33)
        self.wait(0.5)
        
        # 4. Large: Width 4.0
        run_scenario("Large", YELLOW, 4.0)
        self.wait(0.5)
        
        self.wait(2)
