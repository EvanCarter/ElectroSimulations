from manim import *
import math


# --- PHYSICS HELPERS ---
def get_theta_distance(theta1, theta2):
    abs_diff = abs(theta1 - theta2)
    return min(abs_diff, 2 * math.pi - abs_diff)


def get_area_between_circle(theta_dist, orbit_radius, r) -> float:
    d = 2 * orbit_radius * math.sin(theta_dist / 2.0)
    if d >= 2 * r:
        return 0
    if d == 0:
        return math.pi * (r**2)
    term1 = 2 * (r**2) * math.acos(d / (2 * r))
    term2 = 0.5 * d * math.sqrt(4 * (r**2) - d**2)
    return term1 - term2


def check_valid_constants(
    disk_radius, magnet_radius, offset_from_edge, magnet_path_radius, num_magnets
):
    magnet_diameter = magnet_radius * 2
    # MAGNET DIAMETER MUST BE SMALLER THAN OR EQUAL TO DISK RADIUS
    if magnet_diameter > disk_radius:
        print("ERROR: MAGNET RADIUS TOO LARGE FOR DISK RADIUS")
        exit(1)

    if magnet_diameter + offset_from_edge > disk_radius:
        print("ERROR: OFFSET IS TOO LARGE MAGNET OVERLAPS WITH CENTER OF DISK")
        exit(1)

    # theta_per_magent logic
    theta_per_magnet = 2 * math.asin(magnet_diameter / (2 * magnet_path_radius))
    max_possible_magnet = int((2 * math.pi) / theta_per_magnet)

    print("Max magnets: ", max_possible_magnet)
    print("theta occupied per magnet: ", theta_per_magnet)

    if num_magnets > max_possible_magnet:
        print("ERROR: THIS MANY MAGNETS CAN NOT FIT")
        print(
            f"With these constraints can only accommodate {max_possible_magnet} magnets"
        )
        exit(1)


def calculate_physics_data(
    num_magnets=4,
    rotation_speed=0.375 * PI,
    total_time=8.0,
    magnet_path_radius=2.5,
    magnet_radius=0.5,
    coil_theta=math.pi / 2.0,
):
    # Physics Constants
    magnet_diameter_physics = magnet_radius * 2

    # Physics Step Calculation
    dt = total_time / 5000  # Resolution for graph
    steps = 5000

    flux_data = []
    voltage_data = []

    # Setup Initial Magnet Angles (Aligned with Visuals)
    # Visuals: Start at PI/2, rotating CLOCKWISE (rotate is negative angle)
    magnet_angles = []
    magnet_polarities = []  # True for North, False for South
    for i in range(num_magnets):
        theta = (math.pi / 2.0) - (i * (2 * math.pi / num_magnets))
        # Normalize to 0-2PI
        theta = theta % (2 * math.pi)
        magnet_angles.append(theta)
        magnet_polarities.append(i % 2 == 0)

    # Target Coil: Default is Top Coil at PI/2
    # coil_theta is now passed in

    # Simulation Loop
    for step in range(steps):
        t = step * dt
        # Calculate current rotation angle delta
        # Visuals rotate by -ROTATION_SPEED * t
        angle_delta = -rotation_speed * t

        total_flux_this_step = 0

        # Check interaction with each magnet
        for idx, mag_start_angle in enumerate(magnet_angles):
            # Current angle of this magnet
            current_mag_angle = (mag_start_angle + angle_delta) % (2 * math.pi)
            theta_dist = get_theta_distance(coil_theta, current_mag_angle)
            area = get_area_between_circle(
                theta_dist, magnet_path_radius, magnet_radius
            )

            if magnet_polarities[idx]:
                total_flux_this_step += area
            else:
                total_flux_this_step -= area

        flux_data.append((t, total_flux_this_step))

    # --- PHYSICS REFINEMENT: FIELD SMOOTHING ---
    # Solution: Apply a Gaussian Smooth to the calculated flux data.
    from scipy.ndimage import gaussian_filter1d

    # Extract flux values, smooth them, and rebuild data
    flux_values = [d[1] for d in flux_data]
    # Sigma controls the "softness" of the field.
    # sigma=50 steps (at 5000 steps/rot) is about 1% of rotation width.
    flux_values_smoothed = gaussian_filter1d(flux_values, sigma=50)

    # Reconstruct the list of tuples (time, smoothed_flux)
    flux_data = [
        (original_tuple[0], smoothed_val)
        for original_tuple, smoothed_val in zip(flux_data, flux_values_smoothed)
    ]

    # Calculate Voltage (dFlux/dt) from SMOOTHED data
    for step in range(steps):
        t = step * dt
        if step > 0:
            current_flux = flux_data[step][1]
            prev_flux = flux_data[step - 1][1]
            voltage = (current_flux - prev_flux) / dt
            voltage_data.append((t, voltage))
        else:
            voltage_data.append((t, 0))  # Initial voltage 0

    return flux_data, voltage_data


# --- HELPER FUNCTIONS FOR OBJECT CREATION ---
def build_coils(num_coils, magnet_path_radius, magnet_radius):
    coils = VGroup()
    for i in range(num_coils):
        # Calculate angle
        coil_angle = (PI / 2.0) - (i * (2 * PI / num_coils))

        x = magnet_path_radius * math.cos(coil_angle)
        y = magnet_path_radius * math.sin(coil_angle)

        # Using DashedVMobject for the coil look as per reference style
        base_circle = Circle(radius=magnet_radius, color=ORANGE, stroke_width=6)
        coil = DashedVMobject(base_circle, num_dashes=12)

        coil.move_to(np.array([x, y, 0]))
        coils.add(coil)
    return coils


def build_rotor(num_magnets, magnet_path_radius, magnet_radius, disk_radius):
    rotor_group = VGroup()

    # The Disk Body
    disk = Circle(radius=disk_radius, color=WHITE, stroke_opacity=0.5, stroke_width=2)
    disk.set_fill(color=GREY, opacity=0.1)
    rotor_group.add(disk)

    # The Magnets
    magnets = VGroup()
    for i in range(num_magnets):
        mag_angle = (PI / 2.0) - (i * (2 * PI / num_magnets))

        x = magnet_path_radius * math.cos(mag_angle)
        y = magnet_path_radius * math.sin(mag_angle)

        is_north = i % 2 == 0
        color = RED if is_north else BLUE

        magnet = Circle(radius=magnet_radius, color=color, fill_opacity=0.8)
        magnet.set_fill(color)
        magnet.move_to(np.array([x, y, 0]))

        # Add label N/S
        label_text = "N" if is_north else "S"
        label = Text(label_text, font_size=36, color=WHITE).move_to(magnet.get_center())

        mag_group = VGroup(magnet, label)
        magnets.add(mag_group)

    rotor_group.add(magnets)
    return rotor_group


class SpinningGenerator(Scene):
    def construct(self):
        # --- CONSTANTS (Scaled for Manim) ---
        DISK_RADIUS = 3.2
        MAGNET_RADIUS = 0.5
        OFFSET_FROM_EDGE = 0.2
        MAGNET_PATH_RADIUS = DISK_RADIUS - OFFSET_FROM_EDGE - MAGNET_RADIUS

        # SCENARIO 1: 4 Magnets, 3 Coils
        NUM_MAGNETS_START = 4
        NUM_COILS_START = 3

        # SCENARIO 2: 12 Magnets, 9 Coils
        NUM_MAGNETS_END = 12
        NUM_COILS_END = 9

        # Physics Constants
        MAGNET_DIAMETER_PHYSICS = MAGNET_RADIUS * 2

        # Verify both configs
        check_valid_constants(
            DISK_RADIUS,
            MAGNET_RADIUS,
            OFFSET_FROM_EDGE,
            MAGNET_PATH_RADIUS,
            NUM_MAGNETS_START,
        )
        check_valid_constants(
            DISK_RADIUS,
            MAGNET_RADIUS,
            OFFSET_FROM_EDGE,
            MAGNET_PATH_RADIUS,
            NUM_MAGNETS_END,
        )

        # Physics Step Calculation
        STEPS_PER_ROTATION = 5000
        # We want approx 2 full rotations for the graph, or match TOTAL_TIME
        # The rotation speed is 0.375 * PI rad/sec.
        # One full rotation (2PI) takes 2PI / (0.375 * PI) = 2 / 0.375 = 5.333 sec.
        # TOTAL_TIME is 8.0s, so roughly 1.5 rotations.

        ROTATION_SPEED = 0.375 * PI  # 75% of original 0.5 * PI
        TOTAL_TIME = 8.0

        # --- PRE-CALCULATE PHYSICS FOR BOTH SCENARIOS ---
        flux_data_start, voltage_data_start = calculate_physics_data(
            num_magnets=NUM_MAGNETS_START,
            rotation_speed=ROTATION_SPEED,
            total_time=TOTAL_TIME,
            magnet_path_radius=MAGNET_PATH_RADIUS,
            magnet_radius=MAGNET_RADIUS,
        )

        flux_data_end, voltage_data_end = calculate_physics_data(
            num_magnets=NUM_MAGNETS_END,
            rotation_speed=ROTATION_SPEED,
            total_time=TOTAL_TIME,
            magnet_path_radius=MAGNET_PATH_RADIUS,
            magnet_radius=MAGNET_RADIUS,
        )

        # --- GRAPH SCALING ---
        # User requested keeping the scale constant/valid for the higher range?
        # Or just using one scale. Let's use the END config max as it's likely higher/denser.
        # Actually user said "voltage nor flux is not going to be any different".
        # Let's start with scale from START to ensure initial look is good,
        # or max of both to be safe.
        max_flux = max(
            [abs(f[1]) for f in flux_data_start] + [abs(f[1]) for f in flux_data_end]
        )
        max_voltage = max(
            [abs(v[1]) for v in voltage_data_start]
            + [abs(v[1]) for v in voltage_data_end]
        )

        # Add slight padding
        max_flux *= 1.1
        max_voltage *= 1.1

        # --- STYLING ---
        # 2D "Flat" Style: Top-down view
        # No camera orientation needed for standard Scene

        # --- BUILD OBJECTS SCENARIO 1 ---
        coils = build_coils(NUM_COILS_START, MAGNET_PATH_RADIUS, MAGNET_RADIUS)
        rotor_group = build_rotor(
            NUM_MAGNETS_START, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS
        )

        generator_system = VGroup(coils, rotor_group)

        # Ensure Rotor is visually on top of Coils in 2D
        # By adding them in order: Coils first, then Rotor

        # --- STATE TRACKING ---
        time_tracker = ValueTracker(0)

        # Coil rotation updater driven by time_tracker
        # We need to rotate "visually" by -ROTATION_SPEED * t
        # Use initial state as reference to avoid cumulative float errors?
        # Manim's rotation is cumulative if we use dt.
        # Better: reset to neutral and rotate to absolute angle?
        # Manim objects don't store "absolute angle" easily.
        # Let's stick to dt updater but drive it via tracker differencing?
        # Or simpler: The rotate logic used `dt`.
        # Let's switch to `always_redraw` or similar absolute positioning IF needed.
        # But 'rotate' is efficient. Let's keep a standard updater for the generator
        # BUT we must ensure the graph matches the visual rotation.
        # Actually, "ROTATION_SPEED * dt" in updater is exactly what we simulated with "t".
        # So if we simply animate time_tracker linearly, and have an updater that uses dt,
        # they will stay in sync assuming frame deltas are correct.

        def rotate_logic(m, dt):
            m.rotate(
                -ROTATION_SPEED * dt,
                about_point=m.get_center(),
            )

        rotor_group.add_updater(rotate_logic)

        # --- GRAPHS ---
        # Right screen space: approx x=0 to x=7

        # Flux Graph (Top Right)
        # Position: x=1 to 6.5, y=0.5 to 3.5
        flux_ax = (
            Axes(
                x_range=[0, TOTAL_TIME, 1],
                y_range=[-max_flux, max_flux, max_flux / 2],
                x_length=5.5,
                y_length=3,
                axis_config={"include_tip": False, "color": GREY},
            )
            .to_edge(UP)
            .to_edge(RIGHT, buff=0.5)
        )

        flux_label = flux_ax.get_y_axis_label(
            Text("Flux", font_size=24).rotate(90 * DEGREES)
        )
        flux_title = Text("Magnetic Flux", font_size=24).next_to(flux_ax, UP)

        # Voltage Graph (Bottom Right)
        # Position: x=1 to 6.5, y=-3.5 to -0.5
        voltage_ax = (
            Axes(
                x_range=[0, TOTAL_TIME, 1],
                y_range=[-max_voltage, max_voltage, max_voltage / 2],
                x_length=5.5,
                y_length=3,
                axis_config={"include_tip": False, "color": GREY},
            )
            .to_edge(DOWN)
            .to_edge(RIGHT, buff=0.5)
        )

        voltage_label = voltage_ax.get_y_axis_label(
            Text("Voltage", font_size=24).rotate(90 * DEGREES)
        )
        voltage_title = Text("Induced Voltage", font_size=24).next_to(voltage_ax, UP)

        graph_group = VGroup(
            flux_ax, flux_label, flux_title, voltage_ax, voltage_label, voltage_title
        )

        # Dynamic Curves
        # We'll use always_redraw to plot the subset of data up to current time

        # EFFICIENT IMPLEMENTATION:
        # Pre-calc all points in axes coords for BOTH scenarios
        flux_points_start = [flux_ax.c2p(t, f) for t, f in flux_data_start]
        voltage_points_start = [voltage_ax.c2p(t, v) for t, v in voltage_data_start]

        flux_points_end = [flux_ax.c2p(t, f) for t, f in flux_data_end]
        voltage_points_end = [voltage_ax.c2p(t, v) for t, v in voltage_data_end]

        # Initial Curves (Start Scenario)
        flux_curve = (
            VMobject().set_points_as_corners([flux_points_start[0]]).set_color(YELLOW)
        )
        voltage_curve = (
            VMobject().set_points_as_corners([voltage_points_start[0]]).set_color(GREEN)
        )

        # Create a "Tip" dot for each
        flux_dot = Dot(color=YELLOW).scale(0.8)
        voltage_dot = Dot(color=GREEN).scale(0.8)

        # State to switch data source
        self.current_flux_points = flux_points_start
        self.current_voltage_points = voltage_points_start

        def update_flux_curve(mob):
            t = time_tracker.get_value()
            points = self.current_flux_points

            # Map time to index. Note: t might reset or continue.
            # If we continue t, we need to map t to the correct range in the points list?
            # Or we just generate points for the full [0, TOTAL_TIME] range and t moves through it.
            # Assuming t goes 0 -> TOTAL_TIME in Phase 1, then maybe resets or continues?
            # Let's say we run Phase 1 for HALF time, then Phase 2.

            # Simplified: t is absolute time in the simulation data context.
            # If we reset t for phase 2, we just look up from 0 again.

            idx = int((t / TOTAL_TIME) * len(points))
            idx = max(0, min(idx, len(points) - 1))

            # Set points up to index
            mob.set_points_as_corners(points[: idx + 1])

            # Update dot position
            if idx < len(points):
                flux_dot.move_to(points[idx])

        def update_voltage_curve(mob):
            t = time_tracker.get_value()
            points = self.current_voltage_points

            idx = int((t / TOTAL_TIME) * len(points))
            idx = max(0, min(idx, len(points) - 1))

            mob.set_points_as_corners(points[: idx + 1])

            if idx < len(points):
                voltage_dot.move_to(points[idx])

        flux_curve.add_updater(update_flux_curve)
        voltage_curve.add_updater(update_voltage_curve)

        # Group for animation
        graphs_dynamic = VGroup(flux_curve, voltage_curve, flux_dot, voltage_dot)

        self.add(visual_group_start)

        self.wait(1)

        # Layout animation: Move generator left, fade in graphs
        p1 = self.play(
            visual_group_start.animate.scale(0.7).to_edge(LEFT, buff=1.0),
            FadeIn(graph_group),
            run_time=2,
        )

        # --- PHASE 1: 4 Magnets ---
        self.next_section(name="Phase 1 - 4 Magnets", skip_animations=False)

        # Start Rotation and Plotting
        self.add(graphs_dynamic)

        PHASE_1_DURATION = 8
        self.play(
            time_tracker.animate.set_value(PHASE_1_DURATION),
            run_time=PHASE_1_DURATION,
            rate_func=linear,
        )

        # --- TRANSITION ---
        self.next_section(name="Transition", skip_animations=False)

        # Build new objects
        coils_new = build_coils(NUM_COILS_END, MAGNET_PATH_RADIUS, MAGNET_RADIUS)
        rotor_new = build_rotor(
            NUM_MAGNETS_END, MAGNET_PATH_RADIUS, MAGNET_RADIUS, DISK_RADIUS
        )

        # Position them to match current generator state
        # Fix: changing positioning to match CENTER instead of re-calculating edge
        new_system = VGroup(coils_new, rotor_new).scale(0.7)
        new_system.move_to(visual_group_start.get_center())

        # Important: Match rotation of the OLD rotor visual?
        # The old rotor has been rotating via updater.
        # We should stop the updater, get its angle, apply to new rotor?
        # Or simpler: just replace transform and let the updater pick up?
        # The updater relies on `dt`. If we attach updater to new rotor, it starts fresh?
        # Actually, simpler visual hack: align the new rotor to 0 angle (or visually match if possible)
        # and just transform.

        rotor_group.remove_updater(rotate_logic)

        # Perform Transform
        self.play(
            ReplacementTransform(visual_group_start, new_system),
            # ReplacementTransform(rotor_group, rotor_new), # Included in VGroup transform
            run_time=1.5,
        )

        # Update references
        self.remove(
            visual_group_start
        )  # It's been transformed out visually but variable remains
        coils = coils_new
        rotor_group = rotor_new
        generator_system = new_system  # conceptually
        self.add(generator_system)

        # Switch Data Source
        self.current_flux_points = flux_points_end
        self.current_voltage_points = voltage_points_end

        # Reset Time Tracker for Phase 2 (since data starts from t=0)
        # But we want the graph to look continuous?
        # If we reset t=0, the graph line disappears and starts from left.
        # If we want it to "scroll" or continue, we'd need to shift the drawing.
        # For this request, simply restarting the graph trace for the new config is likely acceptable
        # and clearer to show the change in density/frequency.
        time_tracker.set_value(0)

        # Re-attach updater to new rotor
        rotor_group.add_updater(rotate_logic)

        self.wait(0.5)

        # --- PHASE 2: 12 Magnets ---
        self.next_section(name="Phase 2 - 12 Magnets", skip_animations=False)

        PHASE_2_DURATION = 4.0
        self.play(
            time_tracker.animate.set_value(PHASE_2_DURATION),
            run_time=PHASE_2_DURATION,
            rate_func=linear,
        )

        self.wait(2)
