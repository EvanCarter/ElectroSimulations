from manim import *
import numpy as np
import random

class Rain(VGroup):
    """
    Manages a collection of falling lines (rain).
    """
    def __init__(self, x_range=(-7, 7), y_start=4, y_end=-4, density=50, speed=3.0, color=BLUE_C, **kwargs):
        super().__init__(**kwargs)
        self.x_range = x_range
        self.y_start = y_start
        self.y_end = y_end
        self.density = density
        self.speed = speed
        self.rain_color = color
        
        # Create initial rain functionality
        self.drops = VGroup()
        for _ in range(density):
            self.add_drop(random_start=True)
        self.add(self.drops)
        
        # Updater for falling animation
        self.add_updater(self.update_rain)

    def add_drop(self, random_start=False):
        x = np.random.uniform(self.x_range[0], self.x_range[1])
        
        if random_start:
             y = np.random.uniform(self.y_end, self.y_start)
        else:
            y = self.y_start + np.random.uniform(0, 1) # Stagger slightly above

        length = np.random.uniform(0.3, 0.7)
        drop = Line(
            start=np.array([x, y + length/2, 0]),
            end=np.array([x, y - length/2, 0]),
            color=self.rain_color,
            stroke_width=2,
            stroke_opacity=0.6
        )
        self.drops.add(drop)

    def update_rain(self, mob, dt):
        # Move all drops down
        for drop in self.drops:
            drop.shift(DOWN * self.speed * dt)
            
            # Reset if below bottom
            if drop.get_center()[1] < self.y_end:
                x = np.random.uniform(self.x_range[0], self.x_range[1])
                y = self.y_start + np.random.uniform(0, 0.5)
                # Reset position
                length = drop.get_length()
                drop.put_start_and_end_on(
                     np.array([x, y + length/2, 0]),
                     np.array([x, y - length/2, 0])
                )
    
    def set_density(self, new_density):
        current_count = len(self.drops)
        if new_density > current_count:
            # Add drops
            for _ in range(new_density - current_count):
                self.add_drop(random_start=True)
        elif new_density < current_count:
            # Remove drops (randomly to avoid patterns)
            drops_to_remove = random.sample(list(self.drops), current_count - new_density)
            for d in drops_to_remove:
                self.drops.remove(d)

class FluxRainAnalogy(Scene):
    def construct(self):
        # --- SCENE SETUP ---
        self.camera.background_color = "#111111" # Dark grey background
        
        # 1. Analogy Text
        title = Text("Magnetic Flux = Total Rain Passing Through Loop", font_size=36).to_edge(UP)
        self.add(title)
        
        # 2. Add Hoop (Wire Loop)
        hoop_width_tracker = ValueTracker(2.0)
        
        def get_hoop_shape():
            w = hoop_width_tracker.get_value()
            # Ellipse to represent a 3D loop viewed from an angle
            # Height reflects the viewing angle (fixed for now, or proportional)
            # Let's keep height smaller than width to look like a loop
            h = min(w * 0.4, 1.5) 
            
            hoop = Ellipse(width=w, height=h, color=WHITE, stroke_width=6)
            
            # Make it look more like a "halo" or "area"
            # Fill with very light opacity to show it's an area
            bg = Ellipse(width=w, height=h, fill_color=BLUE_E, fill_opacity=0.2, stroke_opacity=0)
            
            return VGroup(bg, hoop)

        hoop_group = always_redraw(get_hoop_shape)
        hoop_label = Text("Wire Loop", font_size=24, color=WHITE).next_to(hoop_group, DOWN, buff=0.5)
        
        self.play(FadeIn(hoop_group), FadeIn(hoop_label))
        
        # 3. Add Rain (Magnetic Field)
        rain = Rain(x_range=(-6, 6), y_start=5, y_end=-5, density=10, speed=4.0)
        
        self.add(rain) # Add rain 
        self.bring_to_back(rain) # Rain behind hoop logic mostly, but hoop is transparent
        self.wait(2)
        
        # --- SCENARIO 1: Light Drizzle (Low Flux) ---
        scenario_text = Text("1. Weak Field (Low Flux)", font_size=32, color=YELLOW).to_corner(UL).shift(DOWN)
        self.play(FadeIn(scenario_text))
        
        # Add Flux Meter (Simple Bar)
        meter_box = Rectangle(width=1, height=4, color=WHITE).to_edge(RIGHT).shift(LEFT)
        meter_fill = Rectangle(width=0.8, height=0.1, fill_color=YELLOW, fill_opacity=1, stroke_opacity=0).move_to(meter_box.get_bottom() + UP*0.1)
        meter_label = Text("FLUX", font_size=24).next_to(meter_box, UP)
        
        self.play(Create(meter_box), FadeIn(meter_fill), FadeIn(meter_label))
        
        # Initial Meter Level updater
        def get_flux_value():
            # Flux ~ Density * Area
            # Here Area ~ Width (conceptually)
            d = len(rain.drops)
            w = hoop_width_tracker.get_value()
            return (d * w) / 500.0 # Normalization factor
            
        meter_tracker = ValueTracker(0)
        
        def update_meter(mob):
            # Smoothly catch up to target flux
            target = get_flux_value()
            current = meter_tracker.get_value()
            # Simple lerp for smoothness
            new_val = current + (target - current) * 0.1
            meter_tracker.set_value(new_val)
            
            # Update visual bar
            # Clamp height to box
            h = min(new_val * 3.8, 3.8) # 3.8 is max height inside 4.0 box
            mob.stretch_to_fit_height(max(h, 0.05), about_edge=DOWN)
            mob.move_to(meter_box.get_bottom() + UP * (h/2 + 0.1))
            
            # Color indicator
            if new_val < 0.3:
                mob.set_color(YELLOW)
            elif new_val < 0.7:
                mob.set_color(ORANGE)
            else:
                mob.set_color(RED)

        meter_fill.add_updater(update_meter)
        self.add(meter_tracker) # keep tracker alive
        
        self.wait(3)
        
        # --- SCENARIO 2: Hurricane (High Flux) ---
        self.play(FadeOut(scenario_text))
        scenario_text_2 = Text("2. Strong Field (High Flux)", font_size=32, color=RED).to_corner(UL).shift(DOWN)
        self.play(FadeIn(scenario_text_2))
        
        # Increase Rain Density
        for d in range(10, 150, 5):
            rain.set_density(d)
            self.wait(0.05)
            
        self.wait(3)
        
        # --- SCENARIO 3: Loop Size (Area) ---
        self.play(FadeOut(scenario_text_2))
        scenario_text_3 = Text("3. Bigger Area = More Flux", font_size=32, color=GREEN).to_corner(UL).shift(DOWN)
        self.play(FadeIn(scenario_text_3))
        
        # Reduce rain slightly so we have headroom for area increase
        for d in range(150, 80, -5):
            rain.set_density(d)
            self.wait(0.02)
            
        self.wait(1)
        
        # Animate Hoop Width
        self.play(hoop_width_tracker.animate.set_value(5.0), run_time=3)
        self.wait(2)
        
        # Shrink back
        self.play(FadeOut(scenario_text_3))
        scenario_text_4 = Text("4. Small Area = Less Flux", font_size=32, color=BLUE).to_corner(UL).shift(DOWN)
        self.play(FadeIn(scenario_text_4))
        
        self.play(hoop_width_tracker.animate.set_value(1.0), run_time=3)
        self.wait(2)
        self.play(FadeOut(scenario_text_4))
        
        # End
        end_text = Text("Flux = Field × Area", font_size=48, color=YELLOW).move_to(ORIGIN)
        self.play(FadeOut(hoop_group), FadeOut(rain), FadeOut(meter_box), FadeOut(meter_fill))

        self.play(Write(end_text))
        self.wait(2)

class RainVisualLoop(Scene):
    """
    A simple 30-second loop of rain falling through a hoop.
    No text, no meters. Purely visual background.
    """
    def construct(self):
        self.camera.background_color = "#111111"

        title = Text("Magnetic Flux = Total Rain Passing Through Loop", font_size=36).to_edge(UP)
        self.play(Write(title))
        
        # 1. Hoop
        # Fixed size for background loop
        w = 4.0
        h = 1.6 # Aspect ratio for "angled 3D loop"
        
        hoop = Ellipse(width=w, height=h, color=WHITE, stroke_width=6)
        bg = Ellipse(width=w, height=h, fill_color=BLUE_E, fill_opacity=0.2, stroke_opacity=0)
        hoop_group = VGroup(bg, hoop).move_to(ORIGIN)
        
        self.add(hoop_group)
        
        # 2. Rain
        # Medium-High density for good visuals
        rain = Rain(x_range=(-7, 7), y_start=5, y_end=-5, density=80, speed=4.0)
        self.add(rain)
        self.bring_to_back(rain)
        
        # 3. Wait
        self.wait(30)


