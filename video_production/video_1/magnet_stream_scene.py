"""
Magnet Stream Animation (Refined)
-----------------------
A complex scene demonstrating an infinite stream of magnets passing through a coil.
Features:
- Dynamic Controls: Vertical Sliders for Coil Width, Spacing, Strength; Switch for Polarity.
- Real-time Physics: Flux and Voltage calculations.
- Display: 
    - Scrolling Flux Graph (Top Right).
    - RMS Digital Readout (Below Flux Graph).
- "Conveyor Belt" Spawning: Visualizing the stream source.
"""

from manim import *
import numpy as np

# --- 1. Physics Logic ---

def circle_segment_area(r, x):
    """ Area of circular segment to the LEFT of vertical line at x. """
    if x <= -r: return 0
    if x >= r: return np.pi * r**2
    d = abs(x)
    cap_area = r**2 * np.arccos(d/r) - d * np.sqrt(r**2 - d**2)
    if x > 0: return np.pi * r**2 - cap_area
    else: return cap_area

def calculate_single_magnet_flux(magnet_center_x, coil_width, magnet_radius, b_field_strength):
    x_left_coil = -coil_width / 2
    x_right_coil = coil_width / 2
    rel_x_left = x_left_coil - magnet_center_x
    rel_x_right = x_right_coil - magnet_center_x
    area = circle_segment_area(magnet_radius, rel_x_right) - circle_segment_area(magnet_radius, rel_x_left)
    return b_field_strength * area

# --- 2. Classes ---

class VerticalSlider(VGroup):
    def __init__(self, label_text, min_val, max_val, start_val, color=WHITE, height=2.0, **kwargs):
        super().__init__(**kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.current_val = ValueTracker(start_val)
        self.height_visual = height
        
        self.track = RoundedRectangle(width=0.15, height=height, corner_radius=0.075, color=GREY)
        self.fill_track = RoundedRectangle(width=0.15, height=0.1, corner_radius=0.075, color=color, fill_opacity=0.5)
        self.knob = RoundedRectangle(width=0.4, height=0.2, corner_radius=0.05, color=color, fill_opacity=1)
        
        self.label = Text(label_text, font_size=16, color=color).next_to(self.track, UP, buff=0.2)
         # Initial text
        self.val_text = Text(f"{start_val:.2f}", font_size=16, color=color).next_to(self.track, DOWN, buff=0.2)
        
        self.add(self.track, self.fill_track, self.knob, self.label, self.val_text)
        self.add_updater(self.update_visuals)
        
    def update_visuals(self, mob, dt):
        val = self.current_val.get_value()
        # Recreate text object to update value (Pango)
        new_text = Text(f"{val:.2f}", font_size=16, color=self.val_text.color).move_to(self.val_text.get_center())
        self.val_text.become(new_text)
        
        pct = (val - self.min_val) / (self.max_val - self.min_val)
        pct = max(0, min(1, pct))
        
        track_bottom = self.track.get_bottom()[1]
        track_height = self.track.get_height()
        target_y = track_bottom + pct * track_height
        
        self.knob.set_y(target_y)
        
        fill_h = max(0.01, pct * track_height)
        self.fill_track.stretch_to_fit_height(fill_h)
        self.fill_track.move_to([self.track.get_center()[0], track_bottom + fill_h/2, 0])
        
    def animate_to(self, target, duration):
        return self.current_val.animate(run_time=duration).set_value(target)




class StreamManager:
    def __init__(self, scene, y_level, start_x, end_x, speed):
        self.scene = scene
        self.y_level = y_level
        self.start_x = start_x 
        self.end_x = end_x   
        self.speed = speed
        self.magnets = VGroup()
        self.scene.add(self.magnets)
        
        self.magnet_counter = 0     
        self.magnet_objects = []   
        
    def update(self, dt, spacing_gap, magnet_radius, is_alternating, magnet_strength_val):
        move_dist = self.speed * dt
        
        # 1. Move & Remove
        to_remove = []
        for obj in self.magnet_objects:
            mob = obj['mobject']
            mob.shift(RIGHT * move_dist)
            x = mob.get_x()
            
            # Opacity
            if x > self.end_x - 1.0: 
                alpha = (self.end_x - x) 
                mob.set_opacity(max(0, min(1, alpha)))
            elif x < self.start_x + 1.0: 
                alpha = (x - self.start_x)
                mob.set_opacity(max(0, min(1, alpha)))
            else:
                mob.set_opacity(1)
                
            if x > self.end_x:
                to_remove.append(obj)
                
        for obj in to_remove:
            self.move_to_trash(obj)
            
        # 2. Spawn Logic
        magnet_diameter = 2 * magnet_radius
        required_stride = magnet_diameter + spacing_gap
        
        # Robust Spawning: 
        # Check if we need to fill the gap.
        # If no magnets, spawn at start.
        if not self.magnet_objects:
             self.spawn_magnet(self.start_x, magnet_radius, is_alternating)
        else:
            # Check last magnet position
            # We assume magnets are ordered by X (since they all move same speed)
            # The last added is the left-most one.
            last_magnet = self.magnet_objects[-1]['mobject']
            last_x = last_magnet.get_x()
            
            # Distance from start point
            dist_moved = last_x - self.start_x
            
            # While we have room to fit magnets between last_x and start_x
            # (Use 'while' to catch up if lag/gap)
            # Spawn point: last_x - stride.
            # We want to force a spawn if last_x > start_x + stride
            
            # Wait, standard "conveyor" logic:
            # If last magnet is at (start_x + stride), we spawn a new one at start_x.
            # If it's at (start_x + stride + delta), we spawn at (start_x + delta).
            
            while dist_moved >= required_stride:
                new_x = last_x - required_stride
                self.spawn_magnet(new_x, magnet_radius, is_alternating)
                
                # Update for next iteration
                last_x = new_x
                dist_moved = last_x - self.start_x
                
                # Safety break to prevent infinite spawning off-screen left
                if new_x < self.start_x - required_stride:
                    break

    def move_to_trash(self, obj):
        if obj in self.magnet_objects:
            self.magnet_objects.remove(obj)
        self.scene.remove(obj['mobject'])
        self.magnets.remove(obj['mobject'])

    def spawn_magnet(self, x_pos, r, is_alternating):
        self.magnet_counter += 1
        if is_alternating:
            is_north = (self.magnet_counter % 2 != 0)
        else:
            is_north = True
            
        color = RED if is_north else BLUE
        label = "N" if is_north else "S"
        sign = 1.0 if is_north else -1.0
        
        circ = Circle(radius=r, color=color, fill_opacity=0.5, stroke_width=2).move_to([x_pos, self.y_level, 0])
        txt = Text(label, font_size=24, color=WHITE).move_to(circ)
        mob = VGroup(circ, txt)
        
        obj = {
            'mobject': mob,
            'polarity_sign': sign,
            'strength_mult': 1.0 
        }
        
        self.magnets.add(mob)
        self.magnet_objects.append(obj)
        
    def update_strength_visuals(self, strength_val):
        for obj in self.magnet_objects:
            obj['strength_mult'] = strength_val
            op = 0.4 + 0.4 * ((strength_val - 0.5) / 4.5) 
            obj['mobject'][0].set_fill(opacity=min(0.9, op))


class MagnetStreamScene(Scene):
    def construct(self):
        # --- Config ---
        magnet_radius = 0.5
        phys_speed = 0.8
        
        # --- Layout ---
        ctrl_y_center = 2.0
        ctrl_x_start = -5.0
        phy_y = -1.5
        phy_center_x = 0
        
        # --- 1. Controls ---
        spacing_start = 0.0
        width_start = 1.0
        strength_start = 1.0
        
        slider_width = VerticalSlider("Coil Width", 0.2, 3.0, width_start, color=YELLOW).move_to([ctrl_x_start, ctrl_y_center, 0])
        slider_space = VerticalSlider("Spacing", 0.0, 3.0, spacing_start, color=BLUE).move_to([ctrl_x_start + 1.5, ctrl_y_center, 0])
        slider_strength = VerticalSlider("Strength", 0.5, 5.0, strength_start, color=PURPLE).move_to([ctrl_x_start + 3.0, ctrl_y_center, 0])
        
        self.add(slider_width, slider_space, slider_strength)
        
        # --- 2. Graphs + Readout ---
        
        # Flux Graph
        flux_ax = Axes(
            x_range=[0, 3.0, 1], 
            y_range=[-6, 6, 3],
            x_length=4.0,
            y_length=2.5,
            axis_config={"include_tip": False, "font_size": 16}
        ).to_edge(RIGHT, buff=0.5).to_edge(UP, buff=0.5)
        flux_lbl = Text("Flux", font_size=24).next_to(flux_ax, UP, buff=0.1)
        
        # RMS Readout (Large Text)
        rms_box = RoundedRectangle(width=3.0, height=1.0, color=RED, fill_opacity=0.1).next_to(flux_ax, DOWN, buff=0.8)
        rms_lbl = Text("RMS Voltage (Last 1s)", font_size=16, color=RED).next_to(rms_box, UP, buff=0.1)
        self.rms_value_text = Text("0.00 V", font_size=36, color=RED).move_to(rms_box)
        
        flux_curve = VMobject(color=YELLOW, stroke_width=2)
        
        self.add(flux_ax, flux_lbl, flux_curve)
        self.add(rms_box, rms_lbl, self.rms_value_text)

         # --- 3. Physics Setup ---
        self.coil_width = ValueTracker(1.0)
        coil_rect = Rectangle(width=1.0, height=1.5, color=WHITE).move_to([phy_center_x, phy_y, 0])
        coil_lbl = Text("Coil", font_size=20).next_to(coil_rect, DOWN)
        
        def coil_updater(mob):
            w = self.coil_width.get_value()
            mob.stretch_to_fit_width(w)
        coil_rect.add_updater(coil_updater)
        
        self.add(coil_rect, coil_lbl)
        stream = StreamManager(self, phy_y, -6.0, 8.0, phys_speed)
        
        # --- 4. Loop ---
        self._global_time = 0
        self.data_time = []
        self.data_flux = []
        self.data_volt = []
        
        def scene_update(mob, dt):
            self._global_time += dt
            t_now = self._global_time
            
            # Values
            c_width = self.coil_width.get_value()
            c_space = slider_space.current_val.get_value()
            c_strength = slider_strength.current_val.get_value()
            is_alt = True
            self.coil_width.set_value(slider_width.current_val.get_value())
            
            # Stream
            stream.update(dt, c_space, magnet_radius, is_alt, c_strength)
            stream.update_strength_visuals(c_strength)
            
            # Physics
            total_flux = 0
            check_range = c_width/2 + magnet_radius + 1.0
            
            for m in stream.magnet_objects:
                mx = m['mobject'].get_x() - phy_center_x
                if abs(mx) < check_range:
                    f = calculate_single_magnet_flux(mx, c_width, magnet_radius, m['strength_mult'] * m['polarity_sign'])
                    total_flux += f
            
            # Volt
            current_volt = 0
            if len(self.data_flux) > 0:
                prev_f = self.data_flux[-1]
                if dt > 0.0001:
                    current_volt = -(total_flux - prev_f) / dt
                    
            self.data_time.append(t_now)
            self.data_flux.append(total_flux)
            self.data_volt.append(current_volt)
            
            # RMS (1s)
            cutoff = t_now - 1.0
            recent_vs = []
            for i in range(len(self.data_time)-1, -1, -1):
                if self.data_time[i] < cutoff: break
                recent_vs.append(self.data_volt[i])
            
            rms = np.sqrt(np.mean(np.square(recent_vs))) if recent_vs else 0
            
            # Update Readout
            new_rms_text = Text(f"{rms:.2f} V", font_size=36, color=RED).move_to(rms_box)
            self.rms_value_text.become(new_rms_text)
            
            # Pruning
            if len(self.data_time) > 400:
                bg = len(self.data_time) - 400
                self.data_time = self.data_time[bg:]
                self.data_flux = self.data_flux[bg:]
                self.data_volt = self.data_volt[bg:]
                
            # Flux Graph Update
            t_win_start = t_now - 3.0
            f_pts = []
            for i in range(len(self.data_time)):
                t_val = self.data_time[i]
                if t_val >= t_win_start:
                    x_graph = t_val - t_win_start 
                    pt_f = flux_ax.c2p(x_graph, self.data_flux[i])
                    f_pts.append(pt_f)
            
            if len(f_pts) > 1:
                flux_curve.set_points_as_corners(f_pts)

        updater_mob = Mobject()
        updater_mob.add_updater(scene_update)
        self.add(updater_mob)

        # --- 5. Animation Script ---
        
        self.wait(3)
        self.play(slider_space.animate_to(1.5, 4.0)) 
        self.wait(2)
        self.play(slider_width.animate_to(2.5, 4.0))
        self.wait(1)
        self.play(slider_strength.animate_to(3.0, 3.0))
        self.wait(2)
        self.play(slider_width.animate_to(0.4, 3.0))
        self.wait(1)
        # switch_polarity removed
        self.wait(3)
        self.play(slider_space.animate_to(0.0, 3.0))
        self.wait(4)
        
