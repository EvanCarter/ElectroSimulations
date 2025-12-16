import manim
from manim import *
import numpy as np

class FluxGridImproved(ThreeDScene):
    """
    Proper physics demonstration of magnetic flux:
    - Realistic dipole field lines (curved, not straight)
    - Measurement coil surface
    - Visual flux counting
    """

    class Config:
        # Camera
        CAMERA_PHI = 60 * DEGREES
        CAMERA_THETA = -90 * DEGREES

        # Magnet properties
        MAGNET_RADIUS = 0.5
        MAGNET_HEIGHT = 0.2
        MAGNET_X = 2.0

        # Field line properties
        FIELD_LINE_RESOLUTION = 30

        # Coil properties
        COIL_RADIUS = 0.8
        COIL_STROKE_WIDTH = 4

        # Layout
        ROW_Z_SPACING = 3.0
        TEXT_MARGIN_RIGHT = 1.0
        TEXT_VERTICAL_SPACING = 2.5

        # Data definitions: (Label, Flux Value, Magnet Scale, Field Line Count, Color)
        ROWS = [
            ("Weak Magnitude", "Flux: Low (1)", 0.6, 3, BLUE_C),
            ("Medium Magnitude", "Flux: Med (5)", 0.8, 6, BLUE_A),
            ("Strong Magnitude", "Flux: High (10)", 1.0, 9, BLUE_E)
        ]

    def create_dipole_field_line(self, r_max, theta_azimuth, phi_start=20*DEGREES, scale=1.0):
        """
        Create a proper dipole magnetic field line.

        Dipole field lines follow: r = r_max * sin²(φ)
        where φ is the polar angle from the north pole.

        Args:
            r_max: Maximum radial extent
            theta_azimuth: Azimuthal angle (rotation around z-axis)
            phi_start: Starting polar angle (avoid singularity at poles)
            scale: Scale factor for the magnet

        Returns:
            numpy array of 3D points forming the field line
        """
        num_points = self.Config.FIELD_LINE_RESOLUTION

        # Polar angle from north pole
        phi = np.linspace(phi_start, np.pi - phi_start, num_points)

        # Dipole field line equation: r ∝ sin²(φ)
        r = r_max * np.sin(phi)**2 * scale

        # Convert to Cartesian (spherical → Cartesian)
        x = r * np.sin(phi) * np.cos(theta_azimuth)
        y = r * np.sin(phi) * np.sin(theta_azimuth)
        z = r * np.cos(phi)

        return np.column_stack([x, y, z])

    def create_magnet(self, scale=1.0, with_glow=False):
        """Create a cylindrical magnet with optional glow effect."""
        magnet = Cylinder(
            radius=self.Config.MAGNET_RADIUS * scale,
            height=self.Config.MAGNET_HEIGHT,
            direction=OUT,  # Z axis (north pole up)
            fill_color=RED,
            fill_opacity=1.0,
            resolution=16
        )

        if with_glow:
            # Create a multi-layer glow by stacking transparent copies
            glow_layers = VGroup()
            for i in range(3):
                glow = Cylinder(
                    radius=self.Config.MAGNET_RADIUS * scale * (1.0 + 0.1 * (i + 1)),
                    height=self.Config.MAGNET_HEIGHT,
                    direction=OUT,
                    fill_color=YELLOW,
                    fill_opacity=0.15 / (i + 1),
                    stroke_width=0
                )
                glow.move_to(ORIGIN)  # Ensure each glow layer is centered
                glow_layers.add(glow)

            magnet.move_to(ORIGIN)  # Ensure magnet is centered
            return VGroup(glow_layers, magnet)

        return magnet

    def create_field_lines(self, scale, density, color=WHITE):
        """Create a group of dipole field lines around a magnet."""
        field_group = VGroup()

        # Distribute azimuthal angles evenly
        for i in range(density):
            theta_azimuth = (i / density) * 2 * np.pi

            # Create field line path
            points = self.create_dipole_field_line(
                r_max=1.5,
                theta_azimuth=theta_azimuth,
                scale=scale
            )

            # Create the curve
            line = VMobject(color=color, stroke_width=2)
            line.set_points_as_corners([*points])

            field_group.add(line)



        return field_group

    def create_measurement_coil(self, radius=None):
        """Create a coil/loop surface for flux measurement."""
        if radius is None:
            radius = self.Config.COIL_RADIUS

        coil = Circle(
            radius=radius,
            color=YELLOW,
            stroke_width=self.Config.COIL_STROKE_WIDTH,
            fill_opacity=0.1,
            fill_color=YELLOW
        )

        return coil

    def construct(self):
        # Set camera
        self.set_camera_orientation(
            phi=self.Config.CAMERA_PHI,
            theta=self.Config.CAMERA_THETA
        )

        # Build rows
        row_groups_3d = []
        text_groups_2d = []

        for i, (title, flux_text, scale, density, color) in enumerate(self.Config.ROWS):
            # 3D Position
            z_pos = self.Config.ROW_Z_SPACING * (0.8 - i)

            # --- 1. Text (2D Fixed) ---
            label_title = Text(title, font_size=24, color=GREY)
            label_val = Text(flux_text, font_size=36, color=color)

            label_group = VGroup(label_title, label_val).arrange(
                DOWN, buff=0.1, aligned_edge=LEFT
            )

            # Position text
            label_group.to_corner(UL).shift(
                DOWN * (1.5 + i * self.Config.TEXT_VERTICAL_SPACING) +
                RIGHT * self.Config.TEXT_MARGIN_RIGHT
            )

            text_groups_2d.append(label_group)

            # --- 2. Magnet (3D) ---
            magnet = self.create_magnet(scale=scale, with_glow=(i == 2))
            magnet.move_to(np.array([self.Config.MAGNET_X, 0, z_pos]))

            # --- 3. Field Lines (3D) ---
            field_lines = self.create_field_lines(scale, density, color=WHITE)
            field_lines.shift(np.array([self.Config.MAGNET_X, 0, z_pos]))

            # --- 4. Measurement Coil / Halo (3D) ---
            # Place it slightly above the magnet to show the "Flux Area"
            halo = self.create_measurement_coil(radius=self.Config.COIL_RADIUS)
            # Center on magnet, but shift slightly up in Z (magnet axis) relative to magnet center
            # Magnet height is 0.2, so top is at +0.1 relative to center. Let's put halo at +0.2
            halo_z_offset = 0.2
            halo.move_to(np.array([self.Config.MAGNET_X, 0, z_pos + halo_z_offset]))

            # Group all 3D elements
            row_3d = VGroup(magnet, field_lines, halo)
            row_groups_3d.append(row_3d)

        # --- Animation ---
        self.wait(1)

        for i in range(len(self.Config.ROWS)):
            # Add 2D Text
            self.add_fixed_in_frame_mobjects(text_groups_2d[i])
            self.play(Write(text_groups_2d[i]), run_time=0.8)

            # Fade In 3D Scene
            self.play(FadeIn(row_groups_3d[i]), run_time=0.8)
            self.wait(0.5)

        self.wait(2)
