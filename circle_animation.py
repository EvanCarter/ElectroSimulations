"""
Disk and Magnet Visualization using Manim (3Blue1Brown style)
Clean architecture for visualizing a rotating generator with magnets.
"""
from manim import *
import math


class DiskConfig:
    """Configuration for disk and magnet setup."""
    def __init__(
        self, 
        disk_radius=2.5,
        magnet_diameter=0.3,
        offset_from_edge=0.3,
        num_magnets=4
    ):
        self.disk_radius = disk_radius
        self.magnet_diameter = magnet_diameter
        self.offset_from_edge = offset_from_edge
        self.num_magnets = num_magnets
    
    @property
    def magnet_radius(self):
        return self.magnet_diameter / 2.0
    
    @property
    def magnet_path_radius(self):
        return self.disk_radius - self.offset_from_edge - self.magnet_radius


class MagnetPositionCalculator:
    """Calculates magnet positions around the disk."""
    
    @staticmethod
    def calculate_positions(config, rotation_angle=0):
        """Returns list of (x, y) positions for magnet centers."""
        positions = []
        angle_step = 2 * PI / config.num_magnets
        
        for i in range(config.num_magnets):
            angle = i * angle_step + rotation_angle
            x = config.magnet_path_radius * np.cos(angle)
            y = config.magnet_path_radius * np.sin(angle)
            positions.append((x, y))
        
        return positions


class DiskGenerator(VGroup):
    """A VGroup representing the disk with magnets."""
    
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.rotation_angle = 0
        
        # Create disk
        self.disk = Circle(
            radius=config.disk_radius,
            color=BLUE,
            fill_opacity=0.3,
            stroke_width=4
        )
        
        # Create magnet path (reference circle)
        self.magnet_path = DashedVMobject(
            Circle(radius=config.magnet_path_radius),
            num_dashes=50,
            color=GRAY
        ).set_stroke(width=2, opacity=0.5)
        
        # Create magnets
        self.magnets = VGroup()
        self._create_magnets()
        
        # Add everything to the group
        self.add(self.disk, self.magnet_path, self.magnets)
    
    def _create_magnets(self):
        """Create magnet objects at their positions."""
        positions = MagnetPositionCalculator.calculate_positions(
            self.config, 
            self.rotation_angle
        )
        
        for i, (x, y) in enumerate(positions):
            magnet = self._create_single_magnet(x, y, i)
            self.magnets.add(magnet)
    
    def _create_single_magnet(self, x, y, index):
        """Create a single magnet with N/S poles."""
        magnet_group = VGroup()
        
        # Magnet body (circle)
        body = Circle(
            radius=self.config.magnet_radius,
            color=RED,
            fill_opacity=0.8,
            stroke_width=3
        ).move_to([x, y, 0])
        
        # Calculate angle for pole orientation (radial)
        angle = np.arctan2(y, x)
        pole_offset = self.config.magnet_radius * 0.5
        
        # North pole (red dot)
        n_x = x + pole_offset * np.cos(angle)
        n_y = y + pole_offset * np.sin(angle)
        north_pole = Dot(
            point=[n_x, n_y, 0],
            color=RED_E,
            radius=0.08
        )
        
        # South pole (blue dot)
        s_x = x - pole_offset * np.cos(angle)
        s_y = y - pole_offset * np.sin(angle)
        south_pole = Dot(
            point=[s_x, s_y, 0],
            color=BLUE_E,
            radius=0.08
        )
        
        # Label
        label = Text(
            str(index + 1),
            font_size=20,
            color=WHITE
        ).move_to([x, y, 0])
        
        magnet_group.add(body, north_pole, south_pole, label)
        return magnet_group
    
    def update_rotation(self, angle):
        """Update magnet positions based on rotation angle."""
        self.rotation_angle = angle
        
        # Recalculate positions
        positions = MagnetPositionCalculator.calculate_positions(
            self.config,
            self.rotation_angle
        )
        
        # Update each magnet
        for i, (magnet, (x, y)) in enumerate(zip(self.magnets, positions)):
            # Update body position
            magnet[0].move_to([x, y, 0])
            
            # Update poles
            angle = np.arctan2(y, x)
            pole_offset = self.config.magnet_radius * 0.5
            
            n_x = x + pole_offset * np.cos(angle)
            n_y = y + pole_offset * np.sin(angle)
            magnet[1].move_to([n_x, n_y, 0])
            
            s_x = x - pole_offset * np.cos(angle)
            s_y = y - pole_offset * np.sin(angle)
            magnet[2].move_to([s_x, s_y, 0])
            
            # Update label
            magnet[3].move_to([x, y, 0])


class DiskMagnetScene(Scene):
    """Basic scene showing the disk with magnets (no animation)."""
    
    def construct(self):
        # Configuration - using default values with offset
        config = DiskConfig(
            disk_radius=2.5,
            magnet_diameter=0.3,
            offset_from_edge=0.3,
            num_magnets=4
        )
        
        # Create disk generator
        generator = DiskGenerator(config)
        
        # Add title
        title = Text("Disk Generator", font_size=36).to_edge(UP)
        
        # Add info
        info = VGroup(
            Text(f"Disk radius: {config.disk_radius}", font_size=20),
            Text(f"Magnets: {config.num_magnets}", font_size=20),
            Text(f"Magnet diameter: {config.magnet_diameter:.3f}", font_size=20),
            Text(f"Offset from edge: {config.offset_from_edge:.3f}", font_size=20),
            Text(f"Magnet path radius: {config.magnet_path_radius:.3f}", font_size=20)
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UL).shift(DOWN * 0.5)
        
        # Display
        self.add(title, generator, info)
        self.wait(2)


class RotatingDiskScene(Scene):
    """Scene with rotating disk animation."""
    
    def construct(self):
        # Configuration - using default values with offset
        config = DiskConfig(
            disk_radius=2.5,
            magnet_diameter=0.3,
            offset_from_edge=0.3,
            num_magnets=4
        )
        
        # Create disk generator
        generator = DiskGenerator(config)
        
        # Add title
        title = Text("Rotating Generator", font_size=36).to_edge(UP)
        
        self.add(title, generator)
        self.wait(1)
        
        # Rotate the entire generator
        # Simple approach: rotate the whole VGroup
        self.play(
            Rotate(generator, angle=2*PI, about_point=ORIGIN),
            rate_func=linear,
            run_time=4
        )
        self.wait(1)


class RotatingDiskSceneAdvanced(Scene):
    """Scene with updater-based rotation for continuous control."""
    
    def construct(self):
        # Configuration - using default values with offset
        config = DiskConfig(
            disk_radius=2.5,
            magnet_diameter=0.3,
            offset_from_edge=0.3,
            num_magnets=4
        )
        
        # Create disk generator
        generator = DiskGenerator(config)
        
        # Rotation tracker
        rotation_tracker = ValueTracker(0)
        
        # Add updater to continuously update rotation
        def update_generator(mob):
            angle = rotation_tracker.get_value()
            mob.rotation_angle = angle
            mob.magnets.clear()
            mob._create_magnets()
        
        generator.add_updater(update_generator)
        
        # Title with rotation angle
        title = Text("Rotating Generator", font_size=36).to_edge(UP)
        
        angle_text = always_redraw(
            lambda: Text(
                f"Angle: {rotation_tracker.get_value():.2f} rad",
                font_size=24
            ).to_corner(UR)
        )
        
        self.add(title, generator, angle_text)
        self.wait(1)
        
        # Animate rotation
        self.play(
            rotation_tracker.animate.set_value(2*PI),
            rate_func=linear,
            run_time=4
        )
        
        self.wait(1)


# To render:
# manim -pql circle_animation.py DiskMagnetScene
# manim -pql circle_animation.py RotatingDiskScene
# manim -pqh circle_animation.py RotatingDiskSceneAdvanced