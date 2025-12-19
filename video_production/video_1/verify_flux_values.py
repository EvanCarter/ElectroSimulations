import numpy as np

# --- Physics Logic ---
def circle_segment_area(r, x):
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

def calculate_total_flux(magnet_centers, coil_width, magnet_radius, b_field_strength):
    total_flux = 0
    cutoff = coil_width/2 + magnet_radius + 0.1
    for center_x in magnet_centers:
        if abs(center_x) < cutoff:
            total_flux += calculate_single_magnet_flux(center_x, coil_width, magnet_radius, b_field_strength)
    return total_flux

def get_voltage(flux_func, t, dt=0.001):
    return -(flux_func(t + dt) - flux_func(t - dt)) / (2 * dt)

# Parameters
magnet_radius = 0.5
magnet_diameter = 2 * magnet_radius 
coil_width = magnet_diameter 
b_strength = 9.0
speed = 1.5
duration = 10.0

def analyze_scenario(name, gap_ratio):
    gap_size = gap_ratio * magnet_diameter
    stride = magnet_diameter + gap_size
    
    # Logic matching magnet_spacing_simulation.py
    phy_center_x = -3.5
    start_x_leader_world = phy_center_x - coil_width/2 - magnet_radius
    math_start_x = start_x_leader_world - phy_center_x # Relative to coil
    
    # Reverted: Dynamic count to fill duration
    num_magnets = int((speed * duration + 5.0) / stride) + 2
    magnet_offsets = [-i * stride for i in range(num_magnets)]
    
    t_values = np.linspace(0, duration, 1000)
    
    volt_values = []
    
    for t in t_values:
        def time_flux(tm):
            # Leader pos relative to coil at time tm
            leader_x = math_start_x + speed * tm
            cc = [leader_x + o for o in magnet_offsets]
            return calculate_total_flux(cc, coil_width, magnet_radius, b_strength)
            
        v = get_voltage(time_flux, t)
        if t < 0.05: v = 0 # Match simulation glitch fix
        volt_values.append(v)
        
    rms_v = np.sqrt(np.mean([v**2 for v in volt_values]))
    
    print(f"--- {name} ---")
    print(f"RMS Voltage (10s): {rms_v:.4f}")

analyze_scenario("Gap 1.0x", 1.0)
analyze_scenario("Gap 0.5x", 0.5)
analyze_scenario("Gap 0.0x", 0.0)
