"""
Magnet Spacing Simulation Animation (Final Polish)
Compare 3 scenarios of CONTINUOUS North-facing magnets.
Layout: Split Screen (Physics Left, Graphs Right).

Features:
- Continuous stream of magnets.
- Fixed duration (6s).
- Starts 'right before' coil.
- Real-time plotting (synced).
- Wipes previous plots.
"""
from manim import *
import numpy as np

# --- Physics Logic ---
def circle_segment_area(r, x):
    if x <= -r: return 0
    if x >= r: return np.pi * r**2
    d = abs(x)
    cap_area = r**2 * np.arccos(d/r) - d * np.sqrt(r**2 - d**2)
    if x > 0: return np.pi * r**2 - cap_area
    else: return cap_area

def calculate_single_magnet_flux(magnet_center_x, coil_width, magnet_radius, b_field_strength):
    x_left_coil = -coil_width / 2
    x_right_coil = coil_width / 2
    rel_x_left = x_left_coil - magnet_center_x
    rel_x_right = x_right_coil - magnet_center_x
    area = circle_segment_area(magnet_radius, rel_x_right) - circle_segment_area(magnet_radius, rel_x_left)
    return b_field_strength * area

def calculate_total_flux(magnet_centers, coil_width, magnet_radius, b_field_strength):
    total_flux = 0
    cutoff = coil_width/2 + magnet_radius + 0.1
    for center_x in magnet_centers:
        if abs(center_x) < cutoff:
            total_flux += calculate_single_magnet_flux(center_x, coil_width, magnet_radius, b_field_strength)
    return total_flux

def get_voltage(flux_func, t, dt=0.001):
    return -(flux_func(t + dt) - flux_func(t - dt)) / (2 * dt)


class MagnetSpacingSimulation(Scene):
    def construct(self):
        # --- Configuration ---
        magnet_radius = 0.5
        magnet_diameter = 2 * magnet_radius 
        coil_width = magnet_diameter 
        b_strength = 1.0 # North facing
        
        speed = 1.5 # units/sec
        duration = 10.0 
        
        # --- Visual Setup ---
        # Split Screen Layout (Restored)
        phy_center = LEFT * 3.5
        
        # Coil
        coil_visual = Rectangle(width=coil_width, height=2.0, color=WHITE, stroke_width=4).move_to(phy_center)
        coil_label = Text("Coil", font_size=20).next_to(coil_visual, DOWN)
        self.add(coil_visual, coil_label)
        
        # Graphs (Right side)
        flux_axes = Axes(
            x_range=[0, duration, 1],
            y_range=[0, 1.2, 0.5], 
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).to_edge(RIGHT, buff=0.5).to_edge(UP, buff=1.0)
        flux_label = Text("Flux", font_size=24).next_to(flux_axes, UP)
        
        volt_axes = Axes(
            x_range=[0, duration, 1], 
            y_range=[-3, 3, 1],
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).next_to(flux_axes, DOWN, buff=0.8)
        volt_label = Text("Voltage", font_size=24).next_to(volt_axes, UP)
        
        self.add(flux_axes, flux_label, volt_axes, volt_label)
        
         # Legend (initially empty, position will be set when items are added)
        legend_group = VGroup() # Position handled in loop
        
        def run_scenario(name, gap_ratio, color):
            # 1. Magnet Stream Setup
            gap_size = gap_ratio * magnet_diameter
            stride = magnet_diameter + gap_size
            
            # Start logic:
            # We want the 'Leading' Magnet (Magnet 0) to start just left of coil.
            # Coil center: phy_center[0]
            # Left edge coil: phy_center[0] - coil_width/2
            # Magnet right edge: magnet_center + magnet_radius
            # So: magnet_center + magnet_radius = phy_center[0] - coil_width/2 - epsilon
            # magnet_center = phy_center[0] - coil_width/2 - magnet_radius - 0.2
            
            start_x_leader_world = phy_center[0] - coil_width/2 - magnet_radius
            
            # We need enough magnets behind it to fill `duration * speed` length.
            # Distance needed = speed * duration = 18.0
            # Num magnets = Distance / stride
            num_magnets = int((speed * duration + 5.0) / stride) + 2
            
            magnets = VGroup()
            magnet_offsets = [] # Relative to Leader
            
            # Create stream behind leader
            for i in range(num_magnets):
                off = -i * stride
                magnet_offsets.append(off)
                
                # Create visual
                # World Pos = Start + Offset
                m_pos = RIGHT * (start_x_leader_world + off) + UP * phy_center[1] # Align Y
                m = Circle(radius=magnet_radius, color=color, fill_opacity=0.5).move_to(m_pos)
                lbl = Text("N", font_size=16).move_to(m)
                magnets.add(VGroup(m, lbl))
            
            self.add(magnets)
            
            # Create initial legend entry (Simulation START info)
            l_dot = Square(side_length=0.2, color=color, fill_opacity=1)
            # Just Name initially
            l_txt_initial = Text(name, font_size=20, color=color)
            l_entry = VGroup(l_dot, l_txt_initial).arrange(RIGHT, buff=0.2)
            legend_group.add(l_entry)
            legend_group.arrange(DOWN, aligned_edge=LEFT)
            
            # FIX: Robust Positioning
            # Ensure it is always above the coil, regardless of content size
            legend_group.next_to(coil_visual, UP, buff=0.8)
            print(f"DEBUG: Legend Center: {legend_group.get_center()}")
            
            self.add(l_entry)
            
            # 2. Pre-calculate Data
            num_points = 600
            t_values = np.linspace(0, duration, num_points)
            flux_path = []
            volt_path = []
            sum_sq_voltage = 0
            
            # Start x of leader relative to coil center (0) for math
            # World leader start: start_x_leader_world
            # Coil center world: phy_center[0]
            # Math leader start: start_x_leader_world - phy_center[0]
            math_start_x = start_x_leader_world - phy_center[0]
            
            for t in t_values:
                # Math calc
                curr_leader_math_x = math_start_x + speed * t
                curr_centers = [curr_leader_math_x + off for off in magnet_offsets]
                
                f = calculate_total_flux(curr_centers, coil_width, magnet_radius, b_strength)
                
                def time_flux(tm):
                    # For derivative
                    cx = math_start_x + speed * tm
                    cc = [cx + o for o in magnet_offsets]
                    return calculate_total_flux(cc, coil_width, magnet_radius, b_strength)
                
                v = get_voltage(time_flux, t)
                if t < 0.05: v = 0
                
                sum_sq_voltage += v**2
                flux_path.append(flux_axes.c2p(t, f))
                volt_path.append(volt_axes.c2p(t, v))
                
            rms_voltage = np.sqrt(sum_sq_voltage / len(t_values))
            
            # 3. Animation Elements
            f_curve = VMobject(color=color, stroke_width=3)
            v_curve = VMobject(color=color, stroke_width=3)
            # Add them to scene
            self.add(f_curve, v_curve)
            
            # Dots
            f_dot = Dot(color=color).scale(0.5)
            v_dot = Dot(color=color).scale(0.5)
            self.add(f_dot, v_dot)
            
            # RMS Text
            rms_str = f"{name}: {rms_voltage:.2f}V"
            # Add to legend
            l_dot = Square(side_length=0.2, color=color, fill_opacity=1)
            l_txt = Text(rms_str, font_size=20, color=color)
            # l_entry = VGroup(l_dot, l_txt).arrange(RIGHT, buff=0.2)
            # legend_group.add(l_entry)
            # legend_group.arrange(DOWN, aligned_edge=LEFT)
            # self.add(l_entry)
            
            # 4. Animation Execution
            t_tracker = ValueTracker(0)
            
            def update_anim(mob):
                t = t_tracker.get_value()
                
                # Update Magnets (World Space)
                # Shift from initial position
                delta = speed * t
                # Reset and move - safest
                # recalculate positions
                for i, grp in enumerate(magnets):
                    # Original World X + Delta
                    orig_x = start_x_leader_world + magnet_offsets[i]
                    new_x = orig_x + delta
                    
                    # Optimization: Don't render if far off screen?
                    # Manim handles this okay.
                    grp.move_to(RIGHT * new_x + UP * phy_center[1])

                    # Disappear Check
                    # "2d to the right" (approx 2 diameters or just enough to be clear)
                    # Let's say 2.5 units past the coil right edge
                    disappear_thresh = phy_center[0] + coil_width/2 + 2.0
                    if new_x > disappear_thresh:
                        grp.set_opacity(0)
                    else:
                        grp.set_opacity(1)
                    
                # Update Curves
                idx = int((t / duration) * (num_points - 1))
                if idx < 0: idx = 0
                if idx >= num_points: idx = num_points - 1
                
                # Careful with empty list
                if idx >= 0:
                    current_f_path = flux_path[:idx+1]
                    current_v_path = volt_path[:idx+1]
                    
                    if len(current_f_path) > 1:
                        f_curve.set_points_as_corners(current_f_path)
                    if len(current_v_path) > 1:
                        v_curve.set_points_as_corners(current_v_path)
                        
                    f_dot.move_to(flux_path[idx])
                    v_dot.move_to(volt_path[idx])

            # Attach updater to something in scene
            magnets.add_updater(update_anim)
            
            self.play(t_tracker.animate.set_value(duration), run_time=duration, rate_func=linear)
            
            magnets.remove_updater(update_anim)
            
            # 5. Cleanup
            self.wait(1)
            self.play(
                FadeOut(magnets),
                FadeOut(f_curve),
                FadeOut(v_curve),
                FadeOut(f_dot),
                FadeOut(v_dot),
                run_time=0.5
            )

            
            # UPDATE Legend with RMS
            # Create the final version
            l_txt_final = Text(rms_str, font_size=20, color=color)
            l_entry_final = VGroup(l_dot.copy(), l_txt_final).arrange(RIGHT, buff=0.2).move_to(l_entry.get_center(), aligned_edge=LEFT)
            
            # Swap them
            self.play(ReplacementTransform(l_entry, l_entry_final))
            
            # Since l_entry is in VGroup, we might need to be careful about updating the reference in the group
            # But visually replacing it is enough. To keep the group valid for layout next time:
            legend_group.remove(l_entry)
            legend_group.add(l_entry_final)
            legend_group.arrange(DOWN, aligned_edge=LEFT)
            # Re-apply position just in case size changed
            legend_group.next_to(coil_visual, UP, buff=0.8)
            
            
        # Run Scenarios
        run_scenario("Gap 1.0x", 1.0, BLUE)
        run_scenario("Gap 0.5x", 0.5, GREEN)
        run_scenario("Gap 0.0x", 0.0, RED)
        
        self.wait(2)
