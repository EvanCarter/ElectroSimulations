"""
Single Loop Generator Animation
Physics: Analytical Flux (Circle-Square Intersection)
Visuals: Flat XY Plane (Z=0), Cyclic Motion, Highlighted Front Leg
"""
from manim import *
import numpy as np

# --- Analytical Physics Logic ---

def circle_segment_area(r, x):
    """
    Area of circular segment to the LEFT of vertical line at relative position x.
    Circle center at (0,0).
    """
    # Clamp x
    if x <= -r: return 0
    if x >= r: return np.pi * r**2
    
    # Formula for area of cap cut by chord at distance d from center
    d = abs(x)
    # Area of cap = r^2 * acos(d/r) - d * sqrt(r^2 - d^2)
    cap_area = r**2 * np.arccos(d/r) - d * np.sqrt(r**2 - d**2)
    
    if x > 0:
        # Line is on right, area is Total - Right Cap
        return np.pi * r**2 - cap_area
    else:
        # Line is on left, area is Left Cap
        return cap_area

def calculate_exact_flux(magnet_x, coil_width, magnet_radius):
    """
    Calculate area of magnet circle intersecting with square coil.
    Assumes square is centered at origin, height >> magnet diameter.
    So only the vertical sides clip the circle.
    """
    # Coil x bounds
    x_left = -coil_width / 2
    x_right = coil_width / 2
    
    # Relative positions of the coil edges to the magnet center
    # x_line_relative = x_line_global - magnet_x
    rel_x_left = x_left - magnet_x
    rel_x_right = x_right - magnet_x
    
    # Area is (Area left of Right Edge) - (Area left of Left Edge)
    area = circle_segment_area(magnet_radius, rel_x_right) - circle_segment_area(magnet_radius, rel_x_left)
    return area

class SingleLoopScene(ThreeDScene):
    def construct(self):
        # 1. Setup Camera
        self.set_camera_orientation(phi=55 * DEGREES, theta=-90 * DEGREES)
        
        # 2. Parameters
        coil_side = 2.0
        magnet_radius = 0.5
        
        # Motion Parameters
        start_x = -2.5       # Closer start
        center_x = 0.0
        cycle_time = 8.0     # Time for one full In-Out (Half speed)
        num_cycles = 2
        total_duration = cycle_time * num_cycles
        
        fps = 60 
        total_frames = int(total_duration * fps)
        
        # 3. Pre-calculate Motion and Physics Data
        t_values = np.linspace(0, total_duration, total_frames)
        x_values = []
        
        # Build piecewise position array
        # One cycle: Start -> Center -> Start
        # Half cycle time for In, Half for Out
        half_cycle = cycle_time / 2.0
        
        for t in t_values:
            # Determine which cycle we are in
            cycle_idx = int(t / cycle_time)
            time_in_cycle = t % cycle_time
            
            if time_in_cycle < half_cycle:
                # Moving IN: Start -> Center
                prog = time_in_cycle / half_cycle
                # Smooth ease in/out
                # Using sine for smooth velocity reversal
                # Map 0..1 to -PI/2 .. PI/2 range? 
                # Or just simple cosine: x = Start + (Center-Start) * (1 - cos(prog*PI/2))?
                # Simple linear for now to match linear_simulation constant velocity assumption, 
                # BUT instant turnaround is unphysical. Let's use smooth interpolation.
                
                # Using (1 - cos(t * PI)) / 2 for full swing 0->1
                # Here we want 0->1 logic
                # Ease: (1 - np.cos(prog * np.pi)) / 2  <-- S-curve
                # But constant velocity gives "Flat Top". If we ease, V changes.
                # User asked for linear_simulation logic (constant V). 
                # But instant turnaround means infinite acceleration.
                # Let's stick to CONSTANT SPEED for the bulk, maybe tiny smooth at ends?
                # linear_simulation had constant velocity. Let's do linear.
                x = start_x + (center_x - start_x) * prog
            else:
                # Moving OUT: Center -> Start
                prog = (time_in_cycle - half_cycle) / half_cycle
                x = center_x + (start_x - center_x) * prog
            
            x_values.append(x)
            
        x_values = np.array(x_values)
        
        # Calculate Flux
        flux_data = []
        for x in x_values:
            f = calculate_exact_flux(x, coil_side, magnet_radius)
            flux_data.append(f)
            
        # Calculate Voltage: V = -dPhi/dt
        dt = total_duration / (total_frames - 1)
        voltage_data = np.gradient(flux_data, dt)
        
        # Normalize Voltage
        peak_v = np.max(np.abs(voltage_data)) if np.max(np.abs(voltage_data)) > 0 else 1
        scaling = 1.0 / peak_v 
        scaled_voltage = voltage_data * scaling
        
        # 4. Visual Elements
        scene_shift = DOWN * 2.5
        
        # Coil Group
        # Main square
        coil = Square(side_length=coil_side, color=ORANGE, stroke_width=6)
        
        # Front Leg Highlight (Lower Y side)
        # Square vertices: UL, DL, DR, UR (Manim standard?)
        # Let's just create a separate Line for the front.
        # Front means closest to camera. If theta=-90 (from front), we are looking along +Y axis? 
        # Standard Manim: Camera at [0, -lat, +z] looking at origin?
        # theta=-90 usually means camera is at [0, -Y, Z]. So "Front" is min-Y edge.
        # Square corners are (+-1, +-1). Min Y is -1.
        
        front_leg = Line3D(
            start=np.array([-coil_side/2, -coil_side/2, 0]),
            end=np.array([coil_side/2, -coil_side/2, 0]),
            color=YELLOW, # Highlight color
            thickness=0.08
        )
        # Note: Line3D is cylinder. Coil is 2D.
        # Let's stick to 2D line if Coil is 2D, or upgrade all to 3D?
        # Manim's 2D Square is flat. Better to use Line for 2D.
        front_leg_2d = Line(
            start=np.array([-coil_side/2, -coil_side/2, 0]),
            end=np.array([coil_side/2, -coil_side/2, 0]),
            color=YELLOW,
            stroke_width=10
        )
        
        coil_group = VGroup(coil, front_leg_2d).move_to(ORIGIN)
        
        # Voltmeter
        voltmeter = VGroup()
        vm_body = Circle(radius=0.3, color=WHITE, fill_opacity=0.2)
        vm_text = Text("V", font_size=20).move_to(vm_body)
        voltmeter.add(vm_body, vm_text)
        voltmeter.next_to(front_leg_2d, DOWN, buff=0.1)
        
        # Magnet
        magnet = Cylinder(radius=magnet_radius, height=0.5, direction=OUT, resolution=24)
        magnet.set_color(RED)
        magnet.set_opacity(0.9)
        n_label = Text("N", font_size=32).move_to([0,0,0.26])
        magnet_group = VGroup(magnet, n_label)
        magnet_group.move_to([start_x, 0, 0])
        
        scene_3d = VGroup(coil_group, voltmeter, magnet_group)
        scene_3d.shift(scene_shift)
        self.add(scene_3d)
        
        # 5. Graphing (Top Half)
        # Bipolar Y-axis for +/- Voltage
        axes = Axes(
            x_range=[0, total_duration, 1],
            y_range=[-1.5, 1.5, 0.5], 
            x_length=6,
            y_length=3.5,
            axis_config={"include_tip": False},
        ).to_corner(UL)
        
        # Manual Labels
        x_label = Text("Time", font_size=20).next_to(axes.x_axis, DOWN)
        y_label = Text("Voltage", font_size=20).rotate(90*DEGREES).next_to(axes.y_axis, LEFT)
        
        bg = BackgroundRectangle(axes, color=BLACK, fill_opacity=0.9, buff=0.3)
        
        # Graph curve
        curve = VMobject(color=YELLOW, stroke_width=4)
        full_points = [axes.c2p(t, v) for t, v in zip(t_values, scaled_voltage)]
        curve.set_points_as_corners([full_points[0], full_points[0]])
        
        self.add_fixed_in_frame_mobjects(bg, axes, x_label, y_label, curve)
        
        # 6. Animation Updaters
        timer = ValueTracker(0)
        self.add(timer)
        
        # Magnet Position Updater
        # Use helper to get X from time
        def get_magnet_x(t):
            cycle_idx = int(t / cycle_time)
            time_in_cycle = t % cycle_time
            if time_in_cycle < half_cycle:
                prog = time_in_cycle / half_cycle
                return start_x + (center_x - start_x) * prog
            else:
                prog = (time_in_cycle - half_cycle) / half_cycle
                return center_x + (start_x - center_x) * prog

        magnet_group.add_updater(lambda m: m.move_to([
            get_magnet_x(timer.get_value()),
            0, 0
        ] + scene_shift))
        
        # Curve Updater
        curve.add_updater(lambda m: m.set_points_as_corners(
            full_points[:int((timer.get_value()/total_duration) * len(full_points))]
            if int((timer.get_value()/total_duration) * len(full_points)) > 1 else [full_points[0], full_points[0]]
        ))
        
        self.play(
            timer.animate.set_value(total_duration),
            run_time=total_duration,
            rate_func=linear
        )
        self.wait()
