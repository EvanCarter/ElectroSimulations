"""
Orbiting Hoop Simulation
Physics: Dipole Magnetic Field + Numerical Flux Integration
Visuals: Orbiting Coil around Central Magnet
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

class OrbitingHoopScene(ThreeDScene):
    def construct(self):
        # 1. Camera
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        
        # 2. Physics & Params
        physics = MagneticPhysics(moment=5.0)
        magnet_pos = ORIGIN
        coil_radius = 0.6
        orbit_radius = 3.0
        
        # 3. Magnet Visuals (Silo)
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
        scene_center.shift(DOWN * 1.5) # Shift entire apparatus down
        
        self.add(scene_center)
        
        # 4. Coil Visuals
        coil = Circle(radius=coil_radius, color=YELLOW, stroke_width=6)
        coil.set_stroke(opacity=1.0)
        coil_fill = Circle(radius=coil_radius, color=YELLOW, fill_opacity=0.1, stroke_width=0)
        
        # Group coil for easy movement
        coil_group = VGroup(coil, coil_fill)
        
        # Add a normal vector visual (optional, helpful for debugging)
        normal_arrow = Arrow3D(start=ORIGIN, end=OUT*1.0, color=GREEN)
        # We won't add normal_arrow to scene for final render to keep it clean, unless requested.
        
        self.add(coil_group)
        
        # 5. Graphs (Top Right)
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-2, 2, 1],
            x_length=5,
            y_length=3,
            axis_config={"include_tip": False}
        ).to_corner(UR)
        
        x_label = Text("Time", font_size=20).next_to(axes.x_axis, DOWN)
        y_label = Text("Flux", font_size=20).rotate(90*DEGREES).next_to(axes.y_axis, LEFT)
        
        bg_rect = BackgroundRectangle(axes, color=BLACK, fill_opacity=0.8, buff=0.2)
        
        flux_graph = VMobject(color=YELLOW, stroke_width=4)
        
        # Group graph elements
        graph_group = VGroup(bg_rect, axes, x_label, y_label, flux_graph)
        self.add_fixed_in_frame_mobjects(graph_group)
        
        # 6. Animation Logic
        
        # Original coil state for stateless updates
        coil_template = coil_group.copy()
        
        # Tracker for Time
        time_tracker = ValueTracker(0)
        self.add(time_tracker) # Ensure tracker is in scene
        
        # -- Helpers --
        def safe_rotate_to_face(mob, target_point, current_center):
            """Rotate mob (assumed facing +Z) to face target_point."""
            direction = target_point - current_center
            dist = np.linalg.norm(direction)
            if dist < 1e-3: return # Too close
            
            v_target = direction / dist
            v_start = np.array([0, 0, 1])
            
            # Rotation axis = start x target
            axis = np.cross(v_start, v_target)
            axis_norm = np.linalg.norm(axis)
            
            if axis_norm < 1e-6:
                # Parallel or anti-parallel
                if np.dot(v_start, v_target) < 0:
                    mob.rotate(PI, axis=RIGHT)
            else:
                axis = axis / axis_norm
                angle = np.arccos(np.clip(np.dot(v_start, v_target), -1, 1))
                mob.rotate(angle, axis=axis)

        # -- SCENARIO 1: Horizontal Orbit --
        duration_1 = 6.0
        
        # Physics calc function
        def get_flux_val_horizontal(angle):
            x = orbit_radius * np.cos(angle)
            y = orbit_radius * np.sin(angle)
            z = 0
            pos = np.array([x, y, z])
            normal = -pos / np.linalg.norm(pos)
            return physics.calculate_flux(pos, normal, coil_radius)

        # Pre-calc graph 1
        points_1 = []
        # Map time [0, duration] -> angle [0, 4pi]
        for t_val in np.linspace(0, duration_1, 200):
            a_val = (t_val / duration_1) * 4 * np.pi
            f_val = get_flux_val_horizontal(a_val)
            points_1.append(axes.c2p(t_val, f_val))
            
        flux_graph.set_points_as_corners([points_1[0], points_1[0]])

        # Updaters
        def scene_update_horizontal(mob):
            t = time_tracker.get_value()
            angle = (t / duration_1) * 4 * np.pi
            
            x = orbit_radius * np.cos(angle)
            y = orbit_radius * np.sin(angle)
            z = 0
            
            center_relative = np.array([x, y, z])
            center_global = center_relative + scene_center.get_center()
            
            # Stateless update: Reset -> Move -> Rotate
            mob.become(coil_template.copy())
            mob.move_to(center_global)
            safe_rotate_to_face(mob, scene_center.get_center(), center_global)

        def update_graph_1(mob):
            curr_time = time_tracker.get_value()
            idx = int( (curr_time / duration_1) * 199 )
            if idx > 199: idx = 199
            if idx < 1: 
                mob.set_points_as_corners([points_1[0], points_1[0]])
            else:
                mob.set_points_as_corners(points_1[:idx])
        
        coil_group.add_updater(scene_update_horizontal)
        flux_graph.add_updater(update_graph_1)
        
        # Play 1
        self.play(
            time_tracker.animate.set_value(duration_1),
            run_time=duration_1,
            rate_func=linear
        )
        
        # Reset for Scenario 2
        coil_group.remove_updater(scene_update_horizontal)
        flux_graph.remove_updater(update_graph_1)
        time_tracker.set_value(0)
        flux_graph.set_points_as_corners([axes.c2p(0,0), axes.c2p(0,0)])
        
        self.wait(1)
        
        # -- SCENARIO 2: Vertical Orbit --
        duration_2 = 6.0
        
        def get_flux_val_vertical(angle):
            y = -orbit_radius * np.cos(angle)
            z = orbit_radius * np.sin(angle)
            x = 0
            pos = np.array([x, y, z])
            normal = -pos / np.linalg.norm(pos)
            return physics.calculate_flux(pos, normal, coil_radius)
            
        points_2 = []
        for t_val in np.linspace(0, duration_2, 200):
            a_val = (t_val / duration_2) * 2 * np.pi
            f_val = get_flux_val_vertical(a_val)
            points_2.append(axes.c2p(t_val, f_val))
            
        def scene_update_vertical(mob):
            t = time_tracker.get_value()
            angle = (t / duration_2) * 2 * np.pi
            
            y = -orbit_radius * np.cos(angle)
            z = orbit_radius * np.sin(angle)
            x = 0
            
            center_relative = np.array([x, y, z])
            center_global = center_relative + scene_center.get_center()
            
            mob.become(coil_template.copy())
            mob.move_to(center_global)
            safe_rotate_to_face(mob, scene_center.get_center(), center_global)

        def update_graph_2(mob):
            curr_time = time_tracker.get_value()
            idx = int( (curr_time / duration_2) * 199 )
            if idx > 199: idx = 199
            if idx < 1: 
                mob.set_points_as_corners([points_2[0], points_2[0]])
            else:
                mob.set_points_as_corners(points_2[:idx])
                
        coil_group.add_updater(scene_update_vertical)
        flux_graph.add_updater(update_graph_2)
        
        self.play(
            time_tracker.animate.set_value(duration_2),
            run_time=duration_2,
            rate_func=linear
        )
        
        self.wait()

class VerticalOrbit(ThreeDScene):
    def construct(self):
        # 1. Camera
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        
        # 2. Physics & Params
        physics = MagneticPhysics(moment=5.0)
        magnet_pos = ORIGIN
        coil_radius = 0.6
        orbit_radius = 3.0
        
        # 3. Magnet Visuals (Silo)
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
        scene_center.shift(DOWN * 1.5) # Shift entire apparatus down
        
        self.add(scene_center)
        
        # 4. Coil Visuals
        coil = Circle(radius=coil_radius, color=YELLOW, stroke_width=6)
        coil.set_stroke(opacity=1.0)
        coil_fill = Circle(radius=coil_radius, color=YELLOW, fill_opacity=0.1, stroke_width=0)
        
        # Group coil for easy movement
        coil_group = VGroup(coil, coil_fill)
        
        self.add(coil_group)
        
        # 5. Graphs (Top Right)
        axes = Axes(
            x_range=[0, 20, 2],
            y_range=[-2, 2, 1],
            x_length=5,
            y_length=3,
            axis_config={"include_tip": False}
        ).to_corner(UR)
        
        x_label = Text("Time", font_size=20).next_to(axes.x_axis, DOWN)
        y_label = Text("Flux", font_size=20).rotate(90*DEGREES).next_to(axes.y_axis, LEFT)
        
        bg_rect = BackgroundRectangle(axes, color=BLACK, fill_opacity=0.8, buff=0.2)
        
        flux_graph = VMobject(color=YELLOW, stroke_width=4)
        
        # Group graph elements
        graph_group = VGroup(bg_rect, axes, x_label, y_label, flux_graph)
        self.add_fixed_in_frame_mobjects(graph_group)
        
        # 6. Animation Logic
        
        # Original coil state for stateless updates
        coil_template = coil_group.copy()
        
        # Tracker for Time
        time_tracker = ValueTracker(0)
        self.add(time_tracker) 
        
        # -- Helpers --
        def safe_rotate_to_face(mob, target_point, current_center):
            """Rotate mob (assumed facing +Z) to face target_point."""
            direction = target_point - current_center
            dist = np.linalg.norm(direction)
            if dist < 1e-3: return # Too close
            
            v_target = direction / dist
            v_start = np.array([0, 0, 1])
            
            # Rotation axis = start x target
            axis = np.cross(v_start, v_target)
            axis_norm = np.linalg.norm(axis)
            
            if axis_norm < 1e-6:
                # Parallel or anti-parallel
                if np.dot(v_start, v_target) < 0:
                    mob.rotate(PI, axis=RIGHT)
            else:
                axis = axis / axis_norm
                angle = np.arccos(np.clip(np.dot(v_start, v_target), -1, 1))
                mob.rotate(angle, axis=axis)

        # -- SCENARIO: Vertical Orbit --
        duration = 20.0 # Slower speed as requested
        num_revolutions = 2
        total_angle = num_revolutions * 2 * np.pi
        
        def get_flux_val_vertical(angle):
            y = -orbit_radius * np.cos(angle)
            z = orbit_radius * np.sin(angle)
            x = 0
            pos = np.array([x, y, z])
            # CHANGED: Normal points AWAY from origin (pos) to align with B field at North pole
            # At North pole (z>0), B points approx OUT (+Z). 
            # If normal points OUT (+Z), dot product is Positive.
            normal = pos / np.linalg.norm(pos) 
            return physics.calculate_flux(pos, normal, coil_radius)
            
        points = []
        # Pre-calculate graph points
        for t_val in np.linspace(0, duration, 400):
            a_val = (t_val / duration) * total_angle
            f_val = get_flux_val_vertical(a_val)
            points.append(axes.c2p(t_val, f_val))
            
        def scene_update_vertical(mob):
            t = time_tracker.get_value()
            angle = (t / duration) * total_angle
            
            y = -orbit_radius * np.cos(angle)
            z = orbit_radius * np.sin(angle)
            x = 0
            
            center_relative = np.array([x, y, z])
            center_global = center_relative + scene_center.get_center()
            
            mob.become(coil_template.copy())
            mob.move_to(center_global)
            
            # Face AWAY from center to ensure normal points outward (matching the flux calc change)
            outward_point = center_global + center_relative
            safe_rotate_to_face(mob, outward_point, center_global)

        def update_graph(mob):
            curr_time = time_tracker.get_value()
            # Find index
            idx = int( (curr_time / duration) * (len(points)-1) )
            if idx > len(points)-1: idx = len(points)-1
            if idx < 1: 
                mob.set_points_as_corners([points[0], points[0]])
            else:
                mob.set_points_as_corners(points[:idx])
                
        coil_group.add_updater(scene_update_vertical)
        flux_graph.add_updater(update_graph)
        
        flux_graph.set_points_as_corners([points[0], points[0]])

        self.play(
            time_tracker.animate.set_value(duration),
            run_time=duration,
            rate_func=linear
        )
        
        self.wait()
