from manim import *

class BallHillScene(Scene):
    def construct(self):
        # 1. Configuration / Parameters
        # ValueTrackers for dynamic updates
        hill_height_tracker = ValueTracker(2.0)
        # Fixed width for this version, as requested
        hill_width_sigma = 1.0
        duration_tracker = ValueTracker(5.0)
        
        start_x = -4.0
        end_x = 4.0
        
        # 2. Physics / Math Functions
        def get_hill_func(height):
            return lambda x: height * np.exp(-(x**2) / (2 * hill_width_sigma**2))

        def get_velocity_func(height, duration):
            # v_y = dy/dt = (dy/dx) * (dx/dt)
            # dx/dt = (end_x - start_x) / duration
            speed_x = (end_x - start_x) / duration
            return lambda x: (-x * height * np.exp(-(x**2) / (2 * hill_width_sigma**2)) / (hill_width_sigma**2)) * speed_x

        # 3. Visual Setup
        
        # Hill Axes
        hill_axes = Axes(
            x_range=[-5, 5, 1],
            y_range=[0, 4, 1],
            x_length=6,
            y_length=3,
            axis_config={"include_tip": False, "include_numbers": False}
        ).to_edge(LEFT).shift(DOWN * 1.5)
        
        # Hill Graph (Dynamic)
        hill_graph = always_redraw(lambda: hill_axes.plot(
            get_hill_func(hill_height_tracker.get_value()), 
            color=WHITE
        ))
        
        hill_label = Text("Hill", font_size=24, color=WHITE).next_to(hill_axes, UP).shift(LEFT)

        ball = Dot(color=BLUE, radius=0.15) # Default color, will change
        # We will manually move the ball during animations, initially place it at start
        initial_h = get_hill_func(hill_height_tracker.get_value())(start_x)
        ball.move_to(hill_axes.c2p(start_x, initial_h))

        # 4. Graphs Setup (Right side)
        pos_axes = Axes(
            x_range=[0, 9, 1], # Extended range to accommodate 8s run
            y_range=[0, 4, 1],
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).to_edge(RIGHT, buff=0.5).to_edge(UP, buff=1.0) # Increased top buffer to prevent cutoff
        
        pos_label = Text("Height", font_size=24).next_to(pos_axes, UP)
        pos_x_label = Text("Time", font_size=16).next_to(pos_axes, DOWN).shift(RIGHT * 2)
        
        vel_axes = Axes(
            x_range=[0, 9, 1], # Extended range
            y_range=[-8, 8, 2],
            x_length=5,
            y_length=2.5,
            axis_config={"include_tip": False}
        ).next_to(pos_axes, DOWN, buff=1.0)
        
        vel_label = Text("Velocity", font_size=24).next_to(vel_axes, UP)
        vel_x_label = Text("Time", font_size=16).next_to(vel_axes, DOWN).shift(RIGHT * 2)
        
        self.add(pos_x_label, vel_x_label)

        # 5. Sliders (Visual representation)
        slider_group = VGroup()
        
        # Height Slider
        h_line = Line(ORIGIN, RIGHT * 2, color=GREY)
        h_dot = Dot(color=YELLOW)
        # Position dot based on value 1.0 to 3.0
        def h_dot_updater(d):
            val = hill_height_tracker.get_value()
            prop = (val - 1.0) / (3.0 - 1.0) # Map 1..3 to 0..1
            d.move_to(h_line.point_from_proportion(np.clip(prop, 0, 1)))
        
        h_dot.add_updater(h_dot_updater)
        h_dot.update() # Explicitly update to set initial position
        h_text = always_redraw(lambda: Text(f"Height: {hill_height_tracker.get_value():.1f} m", font_size=20).next_to(h_line, UP))
        h_group = VGroup(h_line, h_dot, h_text).to_corner(UL).shift(RIGHT * 0.5)

        # Duration Slider
        d_line = Line(ORIGIN, RIGHT * 2, color=GREY)
        d_dot = Dot(color=YELLOW)
        def d_dot_updater(d):
            val = duration_tracker.get_value()
            prop = (val - 1.0) / (9.0 - 1.0) # Map 1..9 to 0..1
            d.move_to(d_line.point_from_proportion(np.clip(prop, 0, 1)))
        
        d_dot.add_updater(d_dot_updater)
        d_dot.update() # Explicitly update
        d_text = always_redraw(lambda: Text(f"Duration: {duration_tracker.get_value():.1f} s", font_size=20).next_to(d_line, UP))
        d_group = VGroup(d_line, d_dot, d_text).next_to(h_group, DOWN, buff=0.5)
        
        slider_group.add(h_group, d_group)

        # 6. Legend Setup
        # Position Legend to the right of sliders (Top Center)
        # Note: We cannot position an empty VGroup, so we just init here
        legend_group = VGroup() 

        # Note: Removed 'ball' from initial add to avoid it sitting at start 
        self.add(hill_axes, hill_graph, hill_label, pos_axes, pos_label, vel_axes, vel_label, slider_group, legend_group)
        self.wait(1)

        # Helper to run the ball animation
        def run_simulation(color, scenario_name):
            # 1. Update Ball color to match run
            ball.set_color(color)
            
            # 2. Add Legend Entry
            legend_dot = Square(side_length=0.2, color=color, fill_opacity=1, fill_color=color)
            legend_text = Text(scenario_name, font_size=20, color=color) # Slightly larger font for visibility
            entry = VGroup(legend_dot, legend_text).arrange(RIGHT, buff=0.2)
            legend_group.add(entry)
            
            # Re-arrange and re-position every time an entry is added
            legend_group.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            # Now that it has content, we can position it
            legend_group.next_to(slider_group, RIGHT, buff=1.5).align_to(slider_group, UP)
            
            # 3. Setup Ball Position
            t_tracker = ValueTracker(0)
            dur = duration_tracker.get_value()
            h = hill_height_tracker.get_value()
            
            # Create dots for graphs
            pos_dot = Dot(color=color).scale(0.5)
            vel_dot = Dot(color=color).scale(0.5)
            
            # Initial placement
            x_start_world = start_x 
            y_start = get_hill_func(h)(x_start_world)
            v_start = get_velocity_func(h, dur)(x_start_world)
            
            ball.move_to(hill_axes.c2p(x_start_world, y_start))
            pos_dot.move_to(pos_axes.c2p(0, y_start))
            vel_dot.move_to(vel_axes.c2p(0, v_start))
            
            # Fade In Ball + Legend Entry
            self.play(FadeIn(entry), FadeIn(ball), run_time=0.5)
            
            self.add(pos_dot, vel_dot)
            
            # Traced Paths - crucial for persistence
            pos_path = TracedPath(pos_dot.get_center, stroke_color=color, stroke_width=3)
            vel_path = TracedPath(vel_dot.get_center, stroke_color=color, stroke_width=3)
            self.add(pos_path, vel_path)

            # Update function for ball and dots
            def update_simulation(mob, dt):
                t_tracker.increment_value(dt)
                t = t_tracker.get_value()
                
                if t > dur: 
                    t = dur
                
                # Current X
                frac = t / dur
                x = start_x + (end_x - start_x) * frac
                
                # Math
                y = get_hill_func(h)(x)
                v = get_velocity_func(h, dur)(x)
                
                # Visuals
                ball.move_to(hill_axes.c2p(x, y))
                
                pos_point = pos_axes.c2p(t, y)
                vel_point = vel_axes.c2p(t, v)
                
                pos_dot.move_to(pos_point)
                vel_dot.move_to(vel_point)

            ball.add_updater(update_simulation)
            
            # Run for 'dur' seconds. 
            self.wait(dur + 0.5)
            
            ball.remove_updater(update_simulation)
            
            # Remove dots but KEEP paths (Persistence)
            self.remove(pos_dot, vel_dot)
            
            # Fade Out Ball to avoid teleportation artifact
            self.play(FadeOut(ball), run_time=0.5)


        # SEQUENCE
        
        # 1. Base Run (H=2, T=5) - BLUE
        run_simulation(BLUE, "Baseline") # Renamed from "Normal"
        
        # 2. Increase Height (H=3, T=5) - RED
        self.play(hill_height_tracker.animate.set_value(3.0), run_time=2.0)
        self.wait(0.5)
        run_simulation(RED, "High")
        
        # 3. Decrease Duration (H=3, T=2) - GREEN (FAST)
        self.play(duration_tracker.animate.set_value(2.0), run_time=2.0)
        self.wait(0.5)
        run_simulation(GREEN, "High & Fast")
        
        # 4. Increase Duration (H=3, T=8) - GOLD (SLOW) "High Hill, Slow"
        self.play(duration_tracker.animate.set_value(8.0), run_time=2.0)
        self.wait(0.5)
        run_simulation(GOLD, "High & Slow")
        
        self.wait(3)
