"""
Intro Animation 1: Lorentz Force - Magnet passing over U-shaped wire (3D)

PHYSICS (Lorentz Force perspective):
- F = qv × B on electrons in the wire
- U-shaped wire at z=0
- Magnet at z=1, N pole facing DOWN (B field in -z direction)
- Magnet moves in +x direction
- When magnet passes left leg: v_eff = -x, B = -z
- v × B = (-x) × (-z) = -y for positive charges
- For electrons (negative): pushed in +y direction (UP the left leg)
- Current flows: UP left leg → across top → DOWN right leg → through voltmeter

This is the "wire" view (Lorentz) not the "area" view (Faraday).
"""
from manim import *
import numpy as np


class LorentzForceWire(ThreeDScene):
    """
    3D visualization: N pole magnet moves over U-shaped wire.
    Camera positioned like viewing a museum exhibit from the front.
    """

    def construct(self):
        # Camera: front view, looking at the exhibit
        # Position: x=0, y=6, z=3 looking toward origin
        self.set_camera_orientation(phi=70 * DEGREES, theta=-90 * DEGREES, zoom=0.8)
        self.camera.set_focal_distance(20)

        # Create all elements
        wire = self.create_u_wire()
        voltmeter = self.create_voltmeter()
        magnet, field_arrows = self.create_magnet_with_field()
        electrons = self.create_circuit_electrons()

        # Title
        title = Text("Lorentz Force: Field Cuts Wire", font_size=32)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)

        # Build scene
        self.play(Create(wire), run_time=1)
        self.play(FadeIn(voltmeter), run_time=0.5)
        self.play(FadeIn(electrons), run_time=0.5)
        self.play(FadeIn(magnet), FadeIn(field_arrows), run_time=0.5)
        self.wait(0.5)

        # Animate
        self.animate_pass(magnet, field_arrows, electrons)

        # Result
        result = Text("Electrons pushed UP left leg by v × B force!", font_size=24, color=YELLOW)
        result.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(result)
        self.play(Write(result), run_time=0.5)

        self.wait(2)

    def create_u_wire(self):
        """Create U-shaped wire at z=0."""
        wire = VGroup()

        # Left leg: x=-2, y from -1.5 to 1.5
        left_leg = Line3D(
            start=np.array([-2, -1.5, 0]),
            end=np.array([-2, 1.5, 0]),
            color=ORANGE,
            thickness=0.06
        )

        # Top bar: y=1.5, x from -2 to 2
        top_bar = Line3D(
            start=np.array([-2, 1.5, 0]),
            end=np.array([2, 1.5, 0]),
            color=ORANGE,
            thickness=0.06
        )

        # Right leg: x=2, y from 1.5 to -1.5
        right_leg = Line3D(
            start=np.array([2, 1.5, 0]),
            end=np.array([2, -1.5, 0]),
            color=ORANGE,
            thickness=0.06
        )

        wire.add(left_leg, top_bar, right_leg)
        return wire

    def create_voltmeter(self):
        """Create voltmeter at bottom of circuit."""
        voltmeter = VGroup()

        # Circle for voltmeter body
        circle = Circle(radius=0.4, color=WHITE, fill_opacity=0.2)
        circle.move_to([0, -1.5, 0])
        circle.rotate(PI/2, axis=RIGHT)  # Lay flat in xz plane

        # V label
        v_label = Text("V", font_size=28, color=WHITE)
        v_label.move_to([0, -1.5, 0.1])
        self.add_fixed_orientation_mobjects(v_label)

        # Connection lines
        left_conn = Line3D(
            start=np.array([-2, -1.5, 0]),
            end=np.array([-0.4, -1.5, 0]),
            color=GRAY,
            thickness=0.04
        )
        right_conn = Line3D(
            start=np.array([0.4, -1.5, 0]),
            end=np.array([2, -1.5, 0]),
            color=GRAY,
            thickness=0.04
        )

        voltmeter.add(circle, left_conn, right_conn)
        return voltmeter

    def create_magnet_with_field(self):
        """Create magnet with pre-attached field arrows."""
        # Magnet body
        magnet = Cylinder(
            radius=0.5,
            height=0.3,
            direction=OUT,
            fill_color=RED,
            fill_opacity=0.9,
            checkerboard_colors=False
        )
        magnet.set_color(RED)

        # N label
        n_label = Text("N", font_size=24, color=WHITE, weight=BOLD)
        n_label.move_to([0, 0, -0.2])
        self.add_fixed_orientation_mobjects(n_label)
        self.n_label = n_label  # Store reference for updating

        # Pre-create field arrows (static, will move with magnet)
        field_arrows = VGroup()
        arrow_positions = [(-0.25, -0.15), (-0.25, 0.15), (0.25, -0.15), (0.25, 0.15), (0, 0)]

        for dx, dy in arrow_positions:
            arrow = Line3D(
                start=np.array([dx, dy, 0.6]),
                end=np.array([dx, dy, -0.4]),
                color=BLUE_C,
                thickness=0.02
            )
            field_arrows.add(arrow)

        # Position everything at start
        start_x = -4
        magnet.move_to([start_x, 0, 1])
        field_arrows.move_to([start_x, 0, 1])
        n_label.move_to([start_x, 0, 0.7])

        return magnet, field_arrows

    def create_circuit_electrons(self):
        """Create electrons distributed around the circuit."""
        electrons = VGroup()

        # Circuit path: left leg (bottom to top) → top bar → right leg (top to bottom) → bottom (right to left)
        # We'll place electrons along this path with a parameter t from 0 to 1

        # Path segments and their lengths (approximate)
        # Left leg: 3 units, top bar: 4 units, right leg: 3 units, bottom: 4 units
        # Total: 14 units

        num_electrons = 12
        for i in range(num_electrons):
            t = i / num_electrons
            pos = self.get_circuit_position(t)
            e = Sphere(radius=0.1, color=YELLOW).move_to(pos)
            electrons.add(e)

        return electrons

    def get_circuit_position(self, t):
        """Get position on circuit for parameter t in [0, 1].

        Path: left leg up → top bar right → right leg down → bottom left
        """
        # Segment lengths (normalized)
        left_leg = 3.0    # y: -1.5 to 1.5
        top_bar = 4.0     # x: -2 to 2
        right_leg = 3.0   # y: 1.5 to -1.5
        bottom = 4.0      # x: 2 to -2
        total = left_leg + top_bar + right_leg + bottom

        pos_in_path = t * total

        if pos_in_path < left_leg:
            # Left leg: going UP
            frac = pos_in_path / left_leg
            y = -1.5 + frac * 3.0
            return np.array([-2, y, 0])

        elif pos_in_path < left_leg + top_bar:
            # Top bar: going RIGHT
            frac = (pos_in_path - left_leg) / top_bar
            x = -2 + frac * 4.0
            return np.array([x, 1.5, 0])

        elif pos_in_path < left_leg + top_bar + right_leg:
            # Right leg: going DOWN
            frac = (pos_in_path - left_leg - top_bar) / right_leg
            y = 1.5 - frac * 3.0
            return np.array([2, y, 0])

        else:
            # Bottom: going LEFT (through voltmeter area)
            frac = (pos_in_path - left_leg - top_bar - right_leg) / bottom
            x = 2 - frac * 4.0
            return np.array([x, -1.5, 0])

    def animate_pass(self, magnet, field_arrows, electrons):
        """Animate magnet passing over, electrons flowing in circuit."""

        magnet_x = ValueTracker(-4)
        prev_magnet_x = ValueTracker(-4)  # Track previous position to detect motion

        # Track cumulative electron flow
        electron_offset = ValueTracker(0)

        # Update magnet position
        def update_magnet(mob):
            mx = magnet_x.get_value()
            mob.move_to([mx, 0, 1])

        magnet.add_updater(update_magnet)

        # Update field arrows position (move with magnet)
        def update_field(mob):
            mx = magnet_x.get_value()
            mob.move_to([mx, 0, 1])

        field_arrows.add_updater(update_field)

        # Update N label
        def update_label(mob):
            mx = magnet_x.get_value()
            mob.move_to([mx, 0, 0.7])

        self.n_label.add_updater(update_label)

        # Update electrons - flow ONLY when magnet is moving AND over the left leg
        def update_electrons(mob):
            mx = magnet_x.get_value()
            prev_mx = prev_magnet_x.get_value()

            # Detect if magnet is actually moving
            magnet_velocity = mx - prev_mx
            prev_magnet_x.set_value(mx)

            # Only apply force when:
            # 1. Magnet is directly over left leg (tight range)
            # 2. Magnet is actually moving (velocity != 0)
            distance_to_left_leg = abs(mx - (-2))
            is_over_leg = distance_to_left_leg < 0.8  # Tight range - only when really over it
            is_moving = abs(magnet_velocity) > 0.001

            if is_over_leg and is_moving:
                # Flow speed proportional to how centered and how fast
                proximity = (0.8 - distance_to_left_leg) / 0.8
                flow_speed = 0.012 * proximity * (magnet_velocity / 0.1)  # Normalized by typical velocity

                current_offset = electron_offset.get_value()
                electron_offset.set_value(current_offset + flow_speed)

            # Reposition all electrons based on cumulative offset
            total_offset = electron_offset.get_value()
            num_electrons = len(mob)

            for i, e in enumerate(mob):
                base_t = i / num_electrons
                t = (base_t + total_offset) % 1.0
                new_pos = self.get_circuit_position(t)
                e.move_to(new_pos)

        electrons.add_updater(update_electrons)

        # Phase 1: Move to left leg
        self.play(
            magnet_x.animate.set_value(-2),
            run_time=2,
            rate_func=smooth
        )

        # Phase 2: Pause over left leg (no motion = no current!)
        # Add a label explaining this
        pause_text = Text("Magnet stopped → No flux change → No current!", font_size=20, color=RED)
        pause_text.to_edge(DOWN).shift(UP * 0.5)
        self.add_fixed_in_frame_mobjects(pause_text)
        self.play(FadeIn(pause_text), run_time=0.3)
        self.wait(1.5)
        self.play(FadeOut(pause_text), run_time=0.3)

        # Phase 3: Continue moving right
        self.play(
            magnet_x.animate.set_value(4),
            run_time=3,
            rate_func=smooth
        )

        # Cleanup
        magnet.remove_updater(update_magnet)
        field_arrows.remove_updater(update_field)
        self.n_label.remove_updater(update_label)
        electrons.remove_updater(update_electrons)


class LorentzForceWireSimple(ThreeDScene):
    """
    Simpler version focusing on just the left leg.
    """

    def construct(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # Just show one vertical wire segment
        wire = Line3D(
            start=np.array([0, -2, 0]),
            end=np.array([0, 2, 0]),
            color=ORANGE,
            thickness=0.1
        )

        wire_label = Text("Wire", font_size=24, color=ORANGE)
        wire_label.move_to([0.5, 0, 0])
        self.add_fixed_orientation_mobjects(wire_label)

        # Magnet at z=1
        magnet = Cylinder(
            radius=0.4,
            height=0.3,
            direction=OUT,
            fill_color=RED,
            fill_opacity=0.9
        )
        magnet.set_color(RED)
        magnet.move_to([-3, 0, 1])

        n_label = Text("N", font_size=28, color=WHITE, weight=BOLD)
        self.add_fixed_orientation_mobjects(n_label)

        # Electrons on wire
        electrons = VGroup()
        for i in range(6):
            y = -1.5 + i * 0.6
            e = Sphere(radius=0.12, color=YELLOW).move_to([0, y, 0])
            electrons.add(e)

        # Field lines
        field_lines = VGroup()

        # Title
        title = Text("Lorentz Force: F = qv × B", font_size=28)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)

        # Build
        self.play(Create(wire), run_time=0.5)
        self.play(FadeIn(electrons), run_time=0.3)
        self.play(FadeIn(magnet), run_time=0.5)

        def update_n_label(mob):
            n_label.move_to(magnet.get_center() + np.array([0, 0, -0.3]))

        magnet.add_updater(update_n_label)
        # Field lines - Create them ONCE
        for dx in [-0.2, 0.2]:
            line = Line3D(
                start=np.array([dx, 0, 0.8]),
                end=np.array([dx, 0, -0.2]),
                color=BLUE_C,
                thickness=0.02
            )
            field_lines.add(line)
        
        # Initially move to magnet start pos
        field_lines.move_to([-3, 0, 0.3]) # magnet is at [-3, 0, 1], mid Z is ~0.3 based on start/end
        
        self.add(field_lines)
        self.wait(0.5)

        # Explanation
        explain = Text("B field points down, magnet moves right", font_size=20, color=GRAY)
        explain.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(explain)
        self.play(Write(explain), run_time=0.5)

        # Animate
        magnet_x = ValueTracker(-3)

        def update_magnet(mob):
            mob.move_to([magnet_x.get_value(), 0, 1])

        magnet.add_updater(update_magnet)

        def update_field(mob):
            mx = magnet_x.get_value()
            # Just move the existing lines
            # Lines were created relative to origin, we just shift them to x=mx
            # But since they are in a VGroup 'field_lines', we can just move the group?
            # Actually, let's just re-define positions relative to magnet_x
            
            # Better: We added them to field_lines. Let's just update their positions individually or as group.
            # Simpler: The group effectively moves with the magnet.
            
            # Use relative positioning if they were attached to magnet, but here they are separate.
            # We can just construct the positions manually like before but using set_start_and_end_attrs
            # BUT Line3D is a Cylinder mesh, set_start_and_end might be tricky if not supported directly cleanly.
            # Actually Line3D inherits from Cylinder. 
            
            # EASIEST PATTERN: Use simple translation
            # 'field_lines' has 2 children.
            # We calculated starts at dx,0,0.8.
            # We want them at mx+dx, ...
            
            # Since we initialized them at x=0 (relative to group center?) 
            # effectively just move the whole group to mx.
            
            # Calculating center of group:
            # If we set them up at 0, moving to mx is easy.
            
            # Let's fix the initialization (Chunk 2) to be at origin, then move.
            # Wait, Chunk 2 initialization:
            # start=[dx, 0, 0.8] -> dx is -0.2 or 0.2. Center X is 0.
            # so field_lines.move_to([mx, 0, ...]) works if we align correctly.
            
            # Actually, let's just update the individual lines.
            children = mob.submobjects
            for i, dx in enumerate([-0.2, 0.2]):
                if i < len(children):
                    line = children[i]
                    # Direct mobject update is fast
                    # Line3D is a Cylinder. It doesn't have put_start_and_end_on like Line.
                    # It works by scaling and rotating a cylinder.
                    # Re-instantiating Line3D IS safer for geometry if start/end change drastically, 
                    # but here only translation changes.
                    
                    # So: Move the WHOLE GROUP.
                    pass
            
            mob.move_to([mx, 0, 0.3]) # 0.3 is approx center of z=0.8 and z=-0.2
            
            # Toggle visibility based on range
            if abs(mx) < 2:
                mob.set_opacity(1)
            else:
                mob.set_opacity(0)

        field_lines.add_updater(update_field)

        def update_electrons(mob):
            mx = magnet_x.get_value()
            if abs(mx) < 1.5:
                effect = (1.5 - abs(mx)) / 1.5
                speed = 0.04 * effect
                for e in mob:
                    pos = e.get_center()
                    new_y = pos[1] - speed
                    if new_y < -2:
                        new_y = 2
                    e.move_to([0, new_y, 0])

        electrons.add_updater(update_electrons)

        self.play(
            magnet_x.animate.set_value(3),
            run_time=4,
            rate_func=linear
        )

        magnet.remove_updater(update_magnet)
        magnet.remove_updater(update_n_label)
        field_lines.remove_updater(update_field)
        electrons.remove_updater(update_electrons)

        # Result
        self.play(FadeOut(explain), run_time=0.2)
        result = Text("v × B pushes electrons along wire!", font_size=22, color=YELLOW)
        result.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(result)
        self.play(Write(result), run_time=0.5)

        self.wait(2)


# To render:
# manim -pql intro_wire.py LorentzForceWire
# manim -pql intro_wire.py LorentzForceWireSimple
