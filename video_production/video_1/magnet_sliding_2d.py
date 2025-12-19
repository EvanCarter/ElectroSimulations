"""
Magnet Sliding 2D Animation
Compare 3 scenarios: Baseline, Stronger Magnet, Faster Magnet.
Shows Flux and Voltage graphs with persistence.
"""
from manim import *
import numpy as np

# --- 1. Physics Logic (Adapted from single_loop.py) ---

def circle_segment_area(r, x):
    """
    Area of circular segment to the LEFT of vertical line at relative position x.
    Circle center at (0,0).
    """
    if x <= -r: return 0
    if x >= r: return np.pi * r**2
    
    d = abs(x)
    cap_area = r**2 * np.arccos(d/r) - d * np.sqrt(r**2 - d**2)
    
    if x > 0:
        return np.pi * r**2 - cap_area
    else:
        return cap_area

def calculate_exact_flux(magnet_x, coil_width, magnet_radius, b_field_strength):
    """
    Calculate Flux = B * Area
    """
    # Coil x bounds (Square centered at origin)
    x_left = -coil_width / 2
    x_right = coil_width / 2
    
    # Relative positions
    rel_x_left = x_left - magnet_x
    rel_x_right = x_right - magnet_x
    
    # Area = (Area left of Right Edge) - (Area left of Left Edge)
    area = circle_segment_area(magnet_radius, rel_x_right) - circle_segment_area(magnet_radius, rel_x_left)
    
    return b_field_strength * area

def get_voltage(flux_func, t, dt=0.001):
    """ A simple finite difference derivative """
    return -(flux_func(t + dt) - flux_func(t - dt)) / (2 * dt)


class MagnetSliding2D(Scene):
    def construct(self):
        # --- Configuration ---
        coil_side = 2.0
        magnet_radius = 0.6
        
        # Motion
        start_x = -4.0
        center_x = 0.0
        
        # --- Visual Setup ---
        # 1. Physical Scene (Left)
        # Shift slightly left to make room for graphs
        phy_center = LEFT * 3.5
        
        coil = Square(side_length=coil_side, color=WHITE, stroke_width=4).move_to(phy_center)
        coil_label = Text("Coil", font_size=20).next_to(coil, DOWN)
        
        magnet = Circle(radius=magnet_radius, color=RED, fill_opacity=0.5).move_to(phy_center + RIGHT * start_x)
        # N label
        n_label = Text("N", font_size=32, color=WHITE).move_to(magnet)
        magnet_group = VGroup(magnet, n_label)
        
        self.add(coil, coil_label, magnet_group)
        
        # 2. Graphs (Right)
        # Flux (Top)
        flux_axes = Axes(
            x_range=[0, 9, 1], # Extended for slower animation (was 5)
            y_range=[0, 4, 1], 
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).to_edge(RIGHT, buff=0.5).to_edge(UP, buff=1.0)
        
        flux_label = Text("Flux", font_size=24).next_to(flux_axes, UP)
        
        # Voltage (Bottom)
        volt_axes = Axes(
            x_range=[0, 9, 1], # Extended (was 5)
            y_range=[-4, 4, 1],
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
        def run_scenario(scenario_name, color, duration, b_strength):
            # 1. Add Legend
            legend_dot = Square(side_length=0.2, color=color, fill_opacity=1, fill_color=color)
            legend_text = Text(scenario_name, font_size=20, color=color)
            entry = VGroup(legend_dot, legend_text).arrange(RIGHT, buff=0.2)
            legend_group.add(entry)
            legend_group.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            # Re-position if it moved
            legend_group.to_corner(UL).shift(RIGHT * 0.5)
            self.add(entry)
            
            # 2. Setup Magnet Visuals
            magnet.set_color(color)
            if b_strength > 1.0:
                magnet.set_fill(opacity=0.8)
            else:
                magnet.set_fill(opacity=0.5)
                
            magnet_group.move_to(phy_center + RIGHT * start_x)
            self.play(FadeIn(magnet_group, run_time=0.5))

            # 3. Pre-calculate Data for Smooth Curves
            # We want to show the "Linger" plateau on the graph.
            # So we plot for (duration + linger_time).
            linger_time = 1.0
            total_plot_time = duration + linger_time
            
            num_points = 2000 # Increased for smoothness
            t_values = np.linspace(0, total_plot_time, num_points)
            
            flux_points = []
            volt_points = []
            
            # Pre-calc arrays
            for t in t_values:
                # Magnet Position logic
                # Clamps at 'duration'
                sim_time = min(t, duration)
                progress = sim_time / duration
                curr_x = start_x + (center_x - start_x) * progress
                
                # Flux
                f = calculate_exact_flux(curr_x, coil_side, magnet_radius, b_strength)
                
                # Voltage (Derivative)
                def flux_of_time(time_val):
                    # Clamp time for physics
                    phys_t = min(time_val, duration)
                    if phys_t < 0: phys_t = 0
                    p = phys_t / duration
                    x_val = start_x + (center_x - start_x) * p
                    return calculate_exact_flux(x_val, coil_side, magnet_radius, b_strength)
                
                v = get_voltage(flux_of_time, t)
                # Cleanup edge cases
                if t == 0: v = 0
                if t >= duration: v = 0 # Explicitly zero during linger
                
                flux_points.append(flux_axes.c2p(t, f))
                volt_points.append(volt_axes.c2p(t, v))
                
            # Create curve VMobjects
            flux_curve = VMobject(color=color, stroke_width=3)
            flux_curve.set_points_as_corners([flux_points[0], flux_points[0]])
            
            volt_curve = VMobject(color=color, stroke_width=3)
            volt_curve.set_points_as_corners([volt_points[0], volt_points[0]])
            
            self.add(flux_curve, volt_curve)
            
            # Dots for current value
            flux_dot = Dot(color=color).scale(0.5).move_to(flux_points[0])
            volt_dot = Dot(color=color).scale(0.5).move_to(volt_points[0])
            self.add(flux_dot, volt_dot)

            # 4. Animation
            t_tracker = ValueTracker(0)
            
            def update_scene(mob):
                t = t_tracker.get_value()
                
                # Magnet Position
                sim_time = min(t, duration)
                progress = sim_time / duration
                curr_x = start_x + (center_x - start_x) * progress
                magnet_group.move_to(phy_center + RIGHT * curr_x)
                
                # Curves & Dots
                idx = int((t / total_plot_time) * (num_points - 1))
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
            
            # Animate for FULL total_plot_time
            self.play(t_tracker.animate.set_value(total_plot_time), run_time=total_plot_time, rate_func=linear)
            # Linger is now part of the animation loop (the last 1.0s)
            
            magnet_group.remove_updater(update_scene)
            
            # Increase Final Wait for the "last one" request?
            # Or just wait a bit before clearing
            self.wait(0.5) 
            
            # Remove Dots, Keep Curves
            self.remove(flux_dot, volt_dot)
            self.play(FadeOut(magnet_group, run_time=0.5))


        # --- Scenario 1: Baseline ---
        # Blue, T=6s (Was 3s), B=1.0
        run_scenario("Baseline", BLUE, 6.0, 1.0)
        self.wait(0.5)

        # --- Scenario 2: Stronger Magnet ---
        # Purple, T=6s (Was 3s), B=2.0
        run_scenario("Stronger Magnet", PURPLE, 6.0, 2.0)
        self.wait(0.5)

        # --- Scenario 3: Faster Magnet ---
        # Yellow, T=3s (Was 1.5s), B=1.0
        run_scenario("Faster Movement", YELLOW, 3.0, 1.0)
        
        self.wait(2)


class BaselineSlow(Scene):
    def construct(self):
        # --- Configuration ---
        coil_side = 2.0
        magnet_radius = 0.6
        
        # Motion
        start_x = -4.0
        center_x = 0.0
        
        # --- Visual Setup ---
        # 1. Physical Scene (Left) - IDENTICAL POSITIONS
        phy_center = LEFT * 3.5
        
        coil = Square(side_length=coil_side, color=WHITE, stroke_width=4).move_to(phy_center)
        coil_label = Text("Coil", font_size=20).next_to(coil, DOWN)
        
        magnet = Circle(radius=magnet_radius, color=RED, fill_opacity=0.5).move_to(phy_center + RIGHT * start_x)
        n_label = Text("N", font_size=32, color=WHITE).move_to(magnet)
        magnet_group = VGroup(magnet, n_label)
        
        self.add(coil, coil_label, magnet_group)
        
        # 2. Graphs (Right)
        # Flux (Top)
        # Increased buff to 1.3 to add more space at top
        flux_axes = Axes(
            x_range=[0, 5, 1], # Original Range
            y_range=[0, 4, 1], # Original Range
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).to_edge(RIGHT, buff=0.5).to_edge(UP, buff=1.3)
        
        flux_label = Text("Flux", font_size=24).next_to(flux_axes, UP)
        
        # Voltage (Bottom)
        volt_axes = Axes(
            x_range=[0, 5, 1], # Original Range
            y_range=[-4, 4, 1], # Original Range
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).next_to(flux_axes, DOWN, buff=0.8)
        
        volt_label = Text("Voltage", font_size=24).next_to(volt_axes, UP)
        volt_x_label = Text("Time (s)", font_size=16).next_to(volt_axes, DOWN).shift(RIGHT * 2)
        
        self.add(flux_axes, flux_label, volt_axes, volt_label, volt_x_label)
        
        # Legend Group - IDENTICAL POSITION
        legend_group = VGroup().to_corner(UL).shift(RIGHT * 0.5)

        # Baseline Parameters (Standard Physics)
        scenario_name = "Baseline"
        color = BLUE
        duration = 3.0 # Standard 3s Physics
        b_strength = 1.0
        
        # Legend Entry
        legend_dot = Square(side_length=0.2, color=color, fill_opacity=1, fill_color=color)
        legend_text = Text(scenario_name, font_size=20, color=color)
        entry = VGroup(legend_dot, legend_text).arrange(RIGHT, buff=0.2)
        legend_group.add(entry)
        legend_group.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        legend_group.to_corner(UL).shift(RIGHT * 0.5)
        self.add(entry)

        # Magnet Init
        magnet.set_color(color)
        magnet.set_fill(opacity=0.5)
        magnet_group.move_to(phy_center + RIGHT * start_x)
        self.play(FadeIn(magnet_group, run_time=0.5))

        # Calculation
        linger_time = 1.0
        total_plot_time = duration + linger_time # 4.0s of physics data
        # Increased resolution for slow motion smoothness
        num_points = 3000 
        t_values = np.linspace(0, total_plot_time, num_points)
        
        flux_points = []
        volt_points = []
        
        # Pre-calc arrays
        for t in t_values:
            sim_time = min(t, duration)
            progress = sim_time / duration
            curr_x = start_x + (center_x - start_x) * progress
            
            f = calculate_exact_flux(curr_x, coil_side, magnet_radius, b_strength)
            
            def flux_of_time(time_val):
                phys_t = min(time_val, duration)
                if phys_t < 0: phys_t = 0
                p = phys_t / duration
                x_val = start_x + (center_x - start_x) * p
                return calculate_exact_flux(x_val, coil_side, magnet_radius, b_strength)
            
            v = get_voltage(flux_of_time, t)
            if t == 0: v = 0
            if t >= duration: v = 0
            
            flux_points.append(flux_axes.c2p(t, f))
            volt_points.append(volt_axes.c2p(t, v))
            
        flux_curve = VMobject(color=color, stroke_width=3)
        flux_curve.set_points_as_corners([flux_points[0], flux_points[0]])
        
        volt_curve = VMobject(color=color, stroke_width=3)
        volt_curve.set_points_as_corners([volt_points[0], volt_points[0]])
        
        self.add(flux_curve, volt_curve)
        
        flux_dot = Dot(color=color).scale(0.5).move_to(flux_points[0])
        volt_dot = Dot(color=color).scale(0.5).move_to(volt_points[0])
        self.add(flux_dot, volt_dot)

        # Animation
        t_tracker = ValueTracker(0)
        
        def update_scene(mob):
            t = t_tracker.get_value()
            
            sim_time = min(t, duration)
            progress = sim_time / duration
            curr_x = start_x + (center_x - start_x) * progress
            magnet_group.move_to(phy_center + RIGHT * curr_x)
            
            idx = int((t / total_plot_time) * (num_points - 1))
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
        
        # PLAY SLOWLY: Simulate 4s of physics over 12s of real time
        playback_duration = 12.0
        self.play(t_tracker.animate.set_value(total_plot_time), run_time=playback_duration, rate_func=linear)
        
        magnet_group.remove_updater(update_scene)
        self.wait(1)
        self.remove(flux_dot, volt_dot)
        self.play(FadeOut(magnet_group, run_time=0.5))
