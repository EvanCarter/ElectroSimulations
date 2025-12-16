from manim import *
import math

class SpinningGenerator(Scene):
    def construct(self):
        # --- CONSTANTS (Scaled for Manim) ---
        DISK_RADIUS = 3.2
        MAGNET_RADIUS = 0.5
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS
        
        NUM_MAGNETS = 4
        NUM_COILS = 3
        
        ROTATION_SPEED = 0.375 * PI # 75% of original 0.5 * PI
        TOTAL_TIME = 8.0
        
        # --- STYLING ---
        # 2D "Flat" Style: Top-down view
        # No camera orientation needed for standard Scene
        
        # --- BUILD STATOR (Bottom Layer) ---
        coils = VGroup()
        for i in range(NUM_COILS):
            # Calculate angle
            coil_angle = (PI / 2.0) - (i * (2 * PI / NUM_COILS))
            
            x = MAGNET_PATH_RADIUS * math.cos(coil_angle)
            y = MAGNET_PATH_RADIUS * math.sin(coil_angle)
            
            # Using DashedVMobject for the coil look as per reference style
            base_circle = Circle(radius=MAGNET_RADIUS, color=ORANGE, stroke_width=6)
            coil = DashedVMobject(base_circle, num_dashes=12)
            
            coil.move_to(np.array([x, y, 0]))
            coils.add(coil)
            
        # --- BUILD ROTOR (Top Layer) ---
        rotor_group = VGroup()
        
        # The Disk Body
        disk = Circle(radius=DISK_RADIUS, color=WHITE, stroke_opacity=0.5, stroke_width=2)
        disk.set_fill(color=GREY, opacity=0.1) 
        rotor_group.add(disk)
        
        # The Magnets
        magnets = VGroup()
        for i in range(NUM_MAGNETS):
            mag_angle = (PI / 2.0) - (i * (2 * PI / NUM_MAGNETS))
            
            x = MAGNET_PATH_RADIUS * math.cos(mag_angle)
            y = MAGNET_PATH_RADIUS * math.sin(mag_angle)
            
            is_north = (i % 2 == 0)
            color = RED if is_north else BLUE
            
            magnet = Circle(radius=MAGNET_RADIUS, color=color, fill_opacity=0.8)
            magnet.set_fill(color)
            magnet.move_to(np.array([x, y, 0]))
            
            # Add label N/S
            label_text = "N" if is_north else "S"
            label = Text(label_text, font_size=36, color=WHITE).move_to(magnet.get_center())
            
            mag_group = VGroup(magnet, label)
            magnets.add(mag_group)
            
        rotor_group.add(magnets)
        
        # Ensure Rotor is visually on top of Coils in 2D
        # By adding them in order: Coils first, then Rotor
        
        # --- ADD TO SCENE ---
        self.add(coils)
        self.add(rotor_group)
        
        # --- ANIMATION ---
        self.play(
            Rotate(
                rotor_group,
                angle=-ROTATION_SPEED * TOTAL_TIME, # Negative for clockwise
                about_point=ORIGIN,
                rate_func=linear
            ),
            run_time=TOTAL_TIME
        )
