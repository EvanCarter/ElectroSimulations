"""
Magnet Polarity Simulation
Shows the effect of North vs South pole on Flux and Voltage.

Sequences:
1. North Pole (+ Flux) -> Show Flux and Voltage
2. South Pole (- Flux) -> Show Flux ONLY
3. South Pole (- Flux) -> Show Flux and Voltage
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
    """
    # Coil x bounds in world space
    x_left_coil = -coil_width / 2
    x_right_coil = coil_width / 2
    
    # Transform to Magnet-Relative coordinates
    rel_x_left = x_left_coil - magnet_x
    rel_x_right = x_right_coil - magnet_x
    
    # Area = (Area left of Right Edge) - (Area left of Left Edge)
    area = circle_segment_area(magnet_radius, rel_x_right) - circle_segment_area(magnet_radius, rel_x_left)
    
    return b_field_strength * area

def get_voltage(flux_func, t, dt=0.001):
    """ A simple finite difference derivative: V = -dPhi/dt """
    return -(flux_func(t + dt) - flux_func(t - dt)) / (2 * dt)


class MagnetPolaritySimulation(Scene):
    def construct(self):
        # --- Configuration ---
        magnet_radius = 0.5
        magnet_diameter = 2 * magnet_radius # 1.0
        coil_width = 1.0 # Matched width for clean look
        
        # Motion: Start far left, go to right
        # Coil is at 0. Width 1.0 (Edges +/- 0.5).
        # Magnet clears at 0.5 + 0.5 = 1.0. 
        start_x = -5.0
        end_x = 4.0 
        
        duration = 4.0
        
        # --- Visual Setup ---
        # 1. Physical Scene (Left)
        phy_center = LEFT * 3.5
        
        coil = Square(side_length=2.0, color=WHITE, stroke_width=4).move_to(phy_center)
        # Visual adjustment: make it look like a coil of width 'coil_width' (1.0)
        # The 'Square' above is just the frame, let's make the actual interaction area explicit?
        # The reference used a Square side_length=2.0 but then changed width in the variable coil demo.
        # Let's use a Rectangle of width 1.0 to match the physics 'coil_width'.
        coil_visual = Rectangle(width=coil_width, height=2.0, color=WHITE, stroke_width=4).move_to(phy_center)
        
        coil_label = Text("Coil", font_size=20).next_to(coil_visual, DOWN)
        
        # Magnet Placeholder (will be set in loop)
        magnet = Circle(radius=magnet_radius, fill_opacity=0.5).move_to(phy_center + RIGHT * start_x)
        magnet_label = Text("", font_size=24, color=WHITE).move_to(magnet)
        magnet_group = VGroup(magnet, magnet_label)
        
        self.add(coil_visual, coil_label, magnet_group)
        
        # 2. Graphs (Right)
        # Flux (Top)
        # Max Area = pi * 0.5^2 = 0.785.
        # Max Flux (+/-) = +/- 0.785 * B. 
        # Range should cover +/- 1.0.
        flux_axes = Axes(
            x_range=[0, duration, 1],
            y_range=[-1.0, 1.0, 0.5], 
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).to_edge(RIGHT, buff=0.5).to_edge(UP, buff=1.0)
        
        flux_label = Text("Flux", font_size=24).next_to(flux_axes, UP)
        
        # Voltage (Bottom)
        # Voltage is derivative. 
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
        
        # Legend Group (Top Left)
        legend_group = VGroup().to_corner(UL).shift(RIGHT * 0.5)
        self.add(legend_group)

        # Helper to run simulation
        def run_scenario(display_text, magnet_color, pole_label, b_strength, show_voltage_curve=True):
            nonlocal magnet_group, magnet
            # 1. Update Legend (Current Run Only)
            # Clear previous items in legend group physically from scene if needed, 
            # but better to just clear the group and rebuild it.
            # Since we added legend_group to scene, modifying it updates scene.
            # But we need to remove old children from scene if they were added via group?
            # VGroup children are not auto-added to scene unless group is added. 
            # If we remove from group, they disappear from scene if group is in scene? Yes.
            
            # Fade out old text if it exists? Or just swap.
            # User wants "single legend showing current run".
            
            # Remove all current sub-mobjects
            legend_group.submobjects = [] 
            
            legend_dot = Square(side_length=0.2, color=magnet_color, fill_opacity=1, fill_color=magnet_color)
            legend_text = Text(display_text, font_size=20, color=magnet_color) # Slightly larger font
            entry = VGroup(legend_dot, legend_text).arrange(RIGHT, buff=0.2)
            
            legend_group.add(entry)
            legend_group.to_corner(UL).shift(RIGHT * 0.5)
            
            # 2. Reset Magnet
            # Recreate magnet to ensure label is correct and on top
            # Text.set_text() might not work as expected for in-place update in all versions
            
            # Remove old magnet group if present
            self.remove(magnet_group)
            
            magnet.set_color(magnet_color)
            magnet.set_fill(color=magnet_color, opacity=0.5)
            
            # Create NEW label
            new_label = Text(pole_label, font_size=24, color=WHITE).move_to(magnet.get_center())
            new_label.set_z_index(10) # Force on top
            magnet.set_z_index(5)
            
            magnet_group = VGroup(magnet, new_label)
            magnet_group.move_to(phy_center + RIGHT * start_x)
            
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
                f = calculate_exact_flux(curr_x, coil_width, magnet_radius, b_strength)
                
                # Voltage (Derivative)
                def flux_of_time(time_val):
                    p = time_val / duration
                    if p < 0: p = 0
                    if p > 1: p = 1 
                    x_val = start_x + (end_x - start_x) * p
                    return calculate_exact_flux(x_val, coil_width, magnet_radius, b_strength)
                
                v = get_voltage(flux_of_time, t)
                
                # Clean edges
                if t <= 0.05 or t >= duration - 0.05: v = 0
                
                flux_points.append(flux_axes.c2p(t, f))
                volt_points.append(volt_axes.c2p(t, v))
                
            # Create curve VMobjects
            flux_curve = VMobject(color=magnet_color, stroke_width=3)
            flux_curve.set_points_as_corners([flux_points[0], flux_points[0]])
            
            volt_curve = VMobject(color=magnet_color, stroke_width=3)
            volt_curve.set_points_as_corners([volt_points[0], volt_points[0]])
            
            self.add(flux_curve)
            if show_voltage_curve:
                self.add(volt_curve)
            
            # Dots
            flux_dot = Dot(color=magnet_color).scale(0.5).move_to(flux_points[0])
            volt_dot = Dot(color=magnet_color).scale(0.5).move_to(volt_points[0])
            self.add(flux_dot)
            if show_voltage_curve:
                self.add(volt_dot)

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
                    
                flux_dot.move_to(flux_points[idx])
                
                if show_voltage_curve:
                    current_volt_path = volt_points[:idx+1]
                    if len(current_volt_path) > 1:
                        volt_curve.set_points_as_corners(current_volt_path)
                    volt_dot.move_to(volt_points[idx])
                
            magnet_group.add_updater(update_scene)
            
            self.play(t_tracker.animate.set_value(duration), run_time=duration, rate_func=linear)
            
            magnet_group.remove_updater(update_scene)
            self.wait(0.5)
            
            # Use remove instead of FadeOut to persist
            self.remove(flux_dot, volt_dot)
            self.play(FadeOut(magnet_group))

        # --- Scenarios ---
        
        # 1. North Pole (Red) - Flux & Voltage
        run_scenario("North", RED, "N", 1.0, show_voltage_curve=True)
        self.wait(0.5)
        
        # 2. South Pole (Blue) - Flux ONLY
        run_scenario("South", BLUE, "S", -1.0, show_voltage_curve=False)
        self.wait(0.5)

        # 3. South Pole (Blue) - Flux & Voltage
        run_scenario("South", BLUE, "S", -1.0, show_voltage_curve=True)
        self.wait(0.5)
        
        self.wait(2)
