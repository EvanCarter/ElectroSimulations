"""
Rotating Hoop Simulation
Physics: Dipole Magnetic Field + Numerical Flux Integration
Visuals: Fixed Coil Rotating above Central Magnet
"""
from manim import *
import numpy as np

# --- Physics Engine ---

class MagneticPhysics:
    """
    Handles B-field calculations and Flux integration.
    Assumes Magnet is a dipole at Origin aligned with Z-axis.
    """
    def __init__(self, moment=1.0):
        self.moment = np.array([0, 0, moment]) # m vector
        
    def get_b_field(self, point):
        """
        Calculate B-field at a point (x,y,z) due to dipole at origin.
        B = (3(m . r_hat)r_hat - m) / r^3
        """
        r_vec = point
        r = np.linalg.norm(r_vec)
        if r < 0.1: return np.zeros(3) # Singularity avoidance
        
        r_hat = r_vec / r
        
        # Dot product m . r_hat
        m_dot_r = np.dot(self.moment, r_hat)
        
        # B formula (ignoring mu_0 / 4pi scale factors, using proportional units)
        B = (3 * m_dot_r * r_hat - self.moment) / (r**3)
        return B

    def calculate_flux(self, coil_center, coil_normal, radius, grid_res=10):
        """
        Calculate Flux through a circular coil by numerical integration.
        coil_center: [x,y,z]
        coil_normal: unit vector [nx, ny, nz]
        radius: coil radius
        """
        # Create a grid of points on the disk
        # Basis vectors for the disk plane
        # tangent1: cross(normal, Z). If normal is Z, use X.
        if np.allclose(np.abs(coil_normal), [0,0,1], atol=1e-2):
            t1 = np.array([1, 0, 0])
        else:
            t1 = np.cross(coil_normal, [0,0,1])
            if np.linalg.norm(t1) < 1e-6:
                t1 = np.cross(coil_normal, [0,1,0])
            t1 = t1 / np.linalg.norm(t1)
            
        t2 = np.cross(coil_normal, t1)
        
        # Monte Carlo or Grid integration
        # Let's use polar grid for better circular coverage
        flux = 0.0
        
        # Grid settings
        r_steps = 5
        theta_steps = 8
        
        samples = []
        
        # Center point
        samples.append(coil_center)
        
        # Rings
        for r_frac in np.linspace(0.2, 0.9, r_steps):
            curr_r = radius * r_frac
            for theta_idx in range(theta_steps):
                theta = (theta_idx / theta_steps) * 2 * np.pi
                # Point on disk
                pt = coil_center + (curr_r * np.cos(theta) * t1) + (curr_r * np.sin(theta) * t2)
                samples.append(pt)
                
        # Calculate B for all samples
        total_b_dot_n = 0
        for pt in samples:
            B = self.get_b_field(pt)
            b_dot_n = np.dot(B, coil_normal)
            total_b_dot_n += b_dot_n
            
        avg_b_dot_n = total_b_dot_n / len(samples)
        area = np.pi * radius**2
        return avg_b_dot_n * area

# --- Visuals ---

class RotatingHoopScene(ThreeDScene):
    def construct(self):
        # 1. Camera
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        
        # 2. Physics & Params
        physics = MagneticPhysics(moment=5.0)
        magnet_pos = ORIGIN
        coil_radius = 0.8 # Slightly larger for visuals
        coil_height = 2.0
        
        # 3. Magnet Visuals (Silo-d for 3D vibes)
        magnet = Cylinder(radius=0.5, height=1.0, direction=OUT, color=RED, fill_opacity=0.8)
        magnet.set_shade_in_3d(True)
        # N label
        n_label = Text("N", font_size=40, color=WHITE).rotate(90*DEGREES, axis=RIGHT).move_to([0, 0, 0.6])
        # S label
        s_label = Text("S", font_size=40, color=WHITE).rotate(90*DEGREES, axis=RIGHT).move_to([0, 0, -0.6])
        
        # Field Lines (Dipole style)
        field_lines = VGroup()
        for theta in np.linspace(0, 2*np.pi, 12, endpoint=False):
            # 2D dipole curve rotated
            # r = sin^2(phi)
            points = []
            for phi in np.linspace(0.1, np.pi-0.1, 40):
                r = 15.0 * (np.sin(phi)**2) # Scale 15.0 for straighter lines
                x = r * np.sin(phi)
                z = r * np.cos(phi)
                
                # Rotate to 3D
                pt = np.array([x * np.cos(theta), x * np.sin(theta), z])
                points.append(pt)
            
            line = VMobject(color=BLUE_E, stroke_width=2, stroke_opacity=0.5)
            line.set_points_smoothly(points)
            field_lines.add(line)
            
        scene_center = VGroup(magnet, n_label, s_label, field_lines)
        # Shift everything down so coil can be comfortably above, and LEFT to make room for graph
        scene_center.shift(DOWN * 1.0 + LEFT * 2.0)
        
        self.add(scene_center)
        
        # 4. Coil Visuals
        # Initial state: Flat horizontal, above magnet. Normal = -Z (Facing Down towards Magnet N)
        initial_coil_pos = scene_center.get_center() + np.array([0, 0, coil_height])
        
        coil = Circle(radius=coil_radius, color=YELLOW, stroke_width=6)
        coil.set_stroke(opacity=1.0)
        coil_fill = Circle(radius=coil_radius, color=YELLOW, fill_opacity=0.2, stroke_width=0)
        
        # Group coil
        coil_group = VGroup(coil, coil_fill)
        coil_group.move_to(initial_coil_pos)
        
        # Add Normal Vector Arrow using Arrow3D or simple Arrow
        # We want it attached to the coil group conceptually, but Arrow3D sometimes behaves weirdly in VGroups with rotation.
        # Let's clean manage it with an updater.
        # Initial Normal is (0,0,-1) but Arrow defaults to pointing RIGHT.
        # Let's use a standard Arrow (2D in 3D space) or Arrow3D? Arrow3D matches 3D vibe better but can be glitchy.
        # Let's try Line + Cone for more control or just Arrow3D.
        # User asked for "subtle".
        normal_arrow = Arrow3D(
            start=ORIGIN, 
            end=OUT * 1.5, # Length 1.5
            color=GREEN,
            resolution=8,
            thickness=0.02
        )
        normal_arrow.set_opacity(0) # Hide initially to avoid glitch before first update
        # Initially, coil normal is (0,0,-1) effectively for max positive flux, 
        # but visually the "Top" is facing UP.
        # Let's say Arrow points OUT (UP) meaning "Positive Normal".
        # If Field is UP, Flux is Positive.
        # Wait, Magnet N is Top. Field lines go UP out of N.
        # So Flux is Positive if Normal is UP.
        
        self.add(coil_group, normal_arrow)
        
        # 5. Graphs (Top Right)
        axes = Axes(
            x_range=[0, 16, 4],
            y_range=[-1.5, 1.5, 1],
            x_length=4,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).to_corner(UR, buff=1.0) # Added buffer to move away from edge
        
        x_label = Text("Time", font_size=20).next_to(axes.x_axis, DOWN, buff=0.1)
        y_label = Text("Flux", font_size=20).rotate(90*DEGREES).next_to(axes.y_axis, LEFT, buff=0.1)
        
        bg_rect = BackgroundRectangle(axes, color=BLACK, fill_opacity=0.7, buff=0.2)
        
        flux_graph = VMobject(color=YELLOW, stroke_width=4)
        
        graph_group = VGroup(bg_rect, axes, x_label, y_label, flux_graph)
        graph_group.shift(DOWN * 0.5) # Extra nudge down
        self.add_fixed_in_frame_mobjects(graph_group)
        
        graph_group.shift(DOWN * 0.5) # Extra nudge down
        self.add_fixed_in_frame_mobjects(graph_group)
        
        # 6. Animation Logic
        
        # We want to rotate the coil around the X-axis (or Y)
        # 0 deg: Normal points -Z (Max Flux)
        # 90 deg: Normal points -Y (Zero Flux)
        # 180 deg: Normal points +Z (Min Flux / Max Negative from perspective of surface normal?)
        # Let's verify normal direction with physics
        
        duration = 16.0
        rotations = 2 # Number of full spins
        total_angle = rotations * 2 * np.pi
        
        # Pre-calc coil normal over time for flux
        # Coil starts flat in XY plane. Normal is (0,0,1) or (0,0,-1).
        # Manim Circle creates points in XY plane.
        # Let's say we rotate around RIGHT axis.
        
        coil_template = coil_group.copy()
        arrow_template = normal_arrow.copy()
        
        def get_flux_val(angle_rad):
            # Rotate vector (0,0,-1) by angle around X-axis
            # But wait, initially coil is facing down?
            # Let's just track the normal vector explicitly.
            # Initial Normal = (0,0,-1) IF we consider "down" to be "into the magnet"
            # Actually Manim Circle normal is +Z.
            # Whatever, let's just calculate Flux based on the geometry.
            
            # Rotation Matrix for X-axis
            # [1  0     0   ]
            # [0 cos -sin]
            # [0 sin  cos]
            
            c = np.cos(angle_rad)
            s = np.sin(angle_rad)
            
            # Initial Normal assumed (0,0,1) for this calculation logic
            nx = 0
            ny = -s
            nz = c
            
            normal = np.array([nx, ny, nz])
            
            # Pos is fixed
            pos = initial_coil_pos - scene_center.get_center() # Relative to magnet
            
            # Since magnet field at (0,0,z) is mostly (0,0,B), 
            # and Normal is (0,-s,c)
            # Dot product ~ c.
            # So at angle 0 (c=1), Flux is Max. Correct.
            
            return physics.calculate_flux(pos, normal, coil_radius)

        # Generate Graph Points
        points = []
        for t_val in np.linspace(0, duration, 300):
            a_val = (t_val / duration) * total_angle
            f_val = get_flux_val(a_val)
            points.append(axes.c2p(t_val, f_val))
            
        flux_graph.set_points_as_corners([points[0], points[0]])
        
        # Updaters
        
        time_tracker = ValueTracker(0)
        
        # Calculate max flux for thresholding (at angle 0)
        max_flux = abs(get_flux_val(0))
        scale_factor = 0.8
        scaled_max_flux = max_flux * scale_factor
        
        def scene_updater(mob):
            # Update Coil
            t = time_tracker.get_value()
            angle = (t / duration) * total_angle
            
            coil_group.become(coil_template.copy())
            coil_group.move_to(initial_coil_pos)
            # Rotate around coil center
            coil_group.rotate(angle, axis=RIGHT)
            
            # Update Arrow
            # Calculate current flux for color and scale
            current_flux = get_flux_val(angle)
            
            # Use a scaling factor for visual length
            # Max flux is roughly when coil is flat. 
            # B at z=2.0, m=5.0 -> B ~ 2*5 / 2^3 = 10/8 = 1.25 roughly (ignoring constants)
            # Area ~ pi * 0.8^2 ~ 2.0
            # Flux ~ 2.5 ish?
            # Let's scale so max length is around 1.5 or 2.0
            
            # Determine direction-based color
            directional_color = GREEN if current_flux >= 0 else RED
            
            # DEBUG: High threshold to force hiding
            threshold_flux = 0.20 * max_flux 
            
            # Determine state
            if abs(current_flux) < threshold_flux:
                length = 0.001
                visual_opacity = 0.0
                color = BLACK 
            else:
                length = abs(current_flux) * scale_factor
                visual_opacity = 1.0
                color = directional_color
            
            # Determine direction
            c = np.cos(angle)
            s = np.sin(angle)
            normal_dir = np.array([0, -s, c]) 
            
            direction = normal_dir * np.sign(current_flux + 1e-9)
            direction = direction / (np.linalg.norm(direction) + 1e-9)
            
            start_point = initial_coil_pos
            end_point = start_point + direction * length
            
            # Recreate arrow 
            new_arrow = Arrow3D(
                start=start_point, 
                end=end_point, 
                color=color,
                resolution=8,
                thickness=0.04
            )
            
            normal_arrow.become(new_arrow)
            
            # Force opacity on all sub-mobjects of the arrow
            normal_arrow.set_opacity(visual_opacity)
            normal_arrow.set_fill(opacity=visual_opacity)
            normal_arrow.set_stroke(opacity=visual_opacity)

            
        def graph_updater(mob):
            t = time_tracker.get_value()
            idx = int( (t / duration) * 299 )
            if idx > 299: idx = 299
            if idx < 1:
                mob.set_points_as_corners([points[0], points[0]])
            else:
                mob.set_points_as_corners(points[:idx])
                
        # Attach updater to something that is always in scene.
        
        coil_group.add_updater(lambda m, dt: scene_updater(m)) 
        
        flux_graph.add_updater(graph_updater)
        
        self.play(
            time_tracker.animate.set_value(duration),
            run_time=duration,
            rate_func=linear
        )
        self.wait(3)

