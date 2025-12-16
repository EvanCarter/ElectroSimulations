"""
Magnet Alternating Polarity Simulation
Shows the effect of alternating North/South magnets on Flux and Voltage.

Sequences:
1. North Magnets (Space 1.0x)
2. South Magnets (Space 1.0x)
3. Alternating N/S (Space 1.0x) - NO GRAPHS
4. Alternating N/S (Space 1.0x) - WITH GRAPHS
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

def calculate_total_flux(magnet_data, coil_width, magnet_radius):
    """
    magnet_data: list of tuples (center_x, b_strength)
    """
    total_flux = 0
    cutoff = coil_width/2 + magnet_radius + 0.1
    for center_x, b_str in magnet_data:
        # Optimization: only calculate if close to coil
        if abs(center_x) < cutoff:
            total_flux += calculate_single_magnet_flux(center_x, coil_width, magnet_radius, b_str)
    return total_flux

def get_voltage(flux_func, t, dt=0.001):
    return -(flux_func(t + dt) - flux_func(t - dt)) / (2 * dt)


class MagnetAlternatingSimulation(Scene):
    def construct(self):
        # --- Configuration ---
        magnet_radius = 0.5
        magnet_diameter = 2 * magnet_radius 
        coil_width = magnet_diameter 
        
        speed = 1.5 # units/sec
        duration = 8.0 
        
        # --- Visual Setup ---
        phy_center = LEFT * 3.5
        
        # Coil
        coil_visual = Rectangle(width=coil_width, height=2.0, color=WHITE, stroke_width=4).move_to(phy_center)
        coil_label = Text("Coil", font_size=20).next_to(coil_visual, DOWN)
        self.add(coil_visual, coil_label)
        
        # Graphs (Right side)
        flux_axes = Axes(
            x_range=[0, duration, 1],
            y_range=[-1.5, 1.5, 0.5], # Increased range for N and S
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).to_edge(RIGHT, buff=0.5).to_edge(UP, buff=1.0)
        flux_label = Text("Flux", font_size=24).next_to(flux_axes, UP)
        
        volt_axes = Axes(
            x_range=[0, duration, 1], 
            y_range=[-4, 4, 1],
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).next_to(flux_axes, DOWN, buff=0.8)
        volt_label = Text("Voltage", font_size=24).next_to(volt_axes, UP)
        
        self.add(flux_axes, flux_label, volt_axes, volt_label)
        
        # Legend Group
        legend_group = VGroup().next_to(coil_visual, UP, buff=0.8)
        self.add(legend_group)
        
        
        def run_scenario(name, pattern_type, gap_ratio=1.0, initial_offset=0.0, show_graphs=True):
            """
            pattern_type: "NORTH", "SOUTH", "ALTERNATING"
            show_graphs: boolean
            initial_offset: extra shift for the start position (negative = further back/left)
            """
            
            # 1. Magnet Stream Setup
            gap_size = gap_ratio * magnet_diameter
            stride = magnet_diameter + gap_size
            
            # Start logic match spacing sim
            start_x_leader_world = phy_center[0] - coil_width/2 - magnet_radius + initial_offset
            
            num_magnets = int((speed * duration + 5.0) / stride) + 2
            
            magnets = VGroup()
            magnet_props = [] # List of dicts: {offset, b_strength, color, label}
            
            # Generate Pattern
            for i in range(num_magnets):
                off = -i * stride
                
                # Determine Polarity based on pattern
                if pattern_type == "NORTH":
                    b_val = 1.0
                    col = RED
                    lbl_txt = "N"
                elif pattern_type == "SOUTH":
                    b_val = -1.0
                    col = BLUE
                    lbl_txt = "S"
                elif pattern_type == "ALTERNATING":
                    # Alternating N, S, N, S...
                    # Leader (i=0) is N
                    is_north = (i % 2 == 0)
                    b_val = 1.0 if is_north else -1.0
                    col = RED if is_north else BLUE
                    lbl_txt = "N" if is_north else "S"
                
                magnet_props.append({
                    "offset": off,
                    "b": b_val,
                    "color": col,
                    "label": lbl_txt
                })
                
                # Visual
                m_pos = RIGHT * (start_x_leader_world + off) + UP * phy_center[1]
                m = Circle(radius=magnet_radius, color=col, fill_opacity=0.5).move_to(m_pos)
                lbl = Text(lbl_txt, font_size=16).move_to(m)
                magnets.add(VGroup(m, lbl))
            
            self.add(magnets)
            
            # Legend Update
            # For this run, we show just the name
            # Clear old legend
            legend_group.submobjects = []
            
            # For alternating, show both colors in legend? Or just Purple/White?
            # Let's just use White for neutral text, or based on pattern
            leg_color = WHITE
            if pattern_type == "NORTH": leg_color = RED
            elif pattern_type == "SOUTH": leg_color = BLUE
            
            l_dot = Square(side_length=0.2, color=leg_color, fill_opacity=1)
            l_txt = Text(name, font_size=20, color=leg_color)
            l_entry = VGroup(l_dot, l_txt).arrange(RIGHT, buff=0.2)
            legend_group.add(l_entry)
            legend_group.next_to(coil_visual, UP, buff=0.8) # Keep pos
            
            # 2. Pre-calculate Data
            num_points = 600
            t_values = np.linspace(0, duration, num_points)
            flux_path = []
            volt_path = []
            
            math_start_x = start_x_leader_world - phy_center[0]
            
            for t in t_values:
                curr_leader_math_x = math_start_x + speed * t
                
                # Prepare data for flux calc
                curr_magnet_data = []
                for prop in magnet_props:
                    cx = curr_leader_math_x + prop["offset"]
                    curr_magnet_data.append((cx, prop["b"]))
                
                f = calculate_total_flux(curr_magnet_data, coil_width, magnet_radius)
                
                def time_flux(tm):
                    cx_leader = math_start_x + speed * tm
                    md = []
                    for prop in magnet_props:
                        md.append((cx_leader + prop["offset"], prop["b"]))
                    return calculate_total_flux(md, coil_width, magnet_radius)
                
                v = get_voltage(time_flux, t)
                if t < 0.05: v = 0
                
                flux_path.append(flux_axes.c2p(t, f))
                volt_path.append(volt_axes.c2p(t, v))
                
            
            # 3. Animation Elements
            # Curves
            # For alternating, curves might be multi-colored? Or just one color (e.g. Yellow/White) to distinguish?
            # Let's use YELLOW for the alternating graph line to stand out
            curve_color = leg_color
            if pattern_type == "ALTERNATING": curve_color = YELLOW
            
            f_curve = VMobject(color=curve_color, stroke_width=3)
            v_curve = VMobject(color=curve_color, stroke_width=3)
            
            f_dot = Dot(color=curve_color).scale(0.5)
            v_dot = Dot(color=curve_color).scale(0.5)

            if show_graphs:
                self.add(f_curve, v_curve, f_dot, v_dot)
            
            # 4. Animation Loop
            t_tracker = ValueTracker(0)
            
            def update_anim(mob):
                t = t_tracker.get_value()
                
                # Move Magnets
                delta = speed * t
                for i, grp in enumerate(magnets):
                    orig_x = start_x_leader_world + magnet_props[i]["offset"]
                    new_x = orig_x + delta
                    
                    grp.move_to(RIGHT * new_x + UP * phy_center[1])
                    
                    # Opacity logic
                    disappear_thresh = phy_center[0] + coil_width/2 + 2.0
                    if new_x > disappear_thresh:
                        grp.set_opacity(0)
                    else:
                        grp.set_opacity(1)
                
                if show_graphs:
                    idx = int((t / duration) * (num_points - 1))
                    if idx < 0: idx = 0
                    if idx >= num_points: idx = num_points - 1
                    
                    current_f_path = flux_path[:idx+1]
                    current_v_path = volt_path[:idx+1]
                    
                    if len(current_f_path) > 1:
                        f_curve.set_points_as_corners(current_f_path)
                    if len(current_v_path) > 1:
                        v_curve.set_points_as_corners(current_v_path)
                        
                    f_dot.move_to(flux_path[idx])
                    v_dot.move_to(volt_path[idx])

            magnets.add_updater(update_anim)
            self.play(t_tracker.animate.set_value(duration), run_time=duration, rate_func=linear)
            magnets.remove_updater(update_anim)
            
            self.wait(1)
            
            # Cleanup
            # Keep curves persisted, only remove the active dots and magnets
            cleanup_items = [magnets]
            if show_graphs:
                # Remove dots so they don't clutter the end of the chart
                cleanup_items.extend([f_dot, v_dot])
                # Do NOT remove f_curve and v_curve (Persist them)
                
            self.play(*[FadeOut(m) for m in cleanup_items], run_time=0.5)

        
        # --- Run Sequences ---
        # 1. North Only (Gap 1.0)
        run_scenario("North Sequence", "NORTH", gap_ratio=1.0, show_graphs=True)
        self.wait(1)
        
        # 2. South Only (Gap 1.0)
        # Offset by -magnet_diameter so it aligns with the 'South' slots of the alternating sequence
        run_scenario("South Sequence", "SOUTH", gap_ratio=1.0, initial_offset=-magnet_diameter, show_graphs=True)
        self.wait(1)
        
        # 3. Alternating (Hidden Graphs, Gap 0.0)
        run_scenario("Alternating", "ALTERNATING", gap_ratio=0.0, show_graphs=False)
        self.wait(1)
        
        # 4. Alternating (Shown, Gap 0.0)
        run_scenario("Alternating", "ALTERNATING", gap_ratio=0.0, show_graphs=True)
        self.wait(2)
