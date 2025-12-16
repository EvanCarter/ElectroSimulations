# AI Coding Agent Guide: High-Quality Manim Animations

This guide outlines best practices for generating 3B1B-style educational animations, specifically focusing on physics simulations with 3D elements, synchronized data visualization, and performance optimization.

## 1. Scene Composition & Architecture

### Strategy: Integrated vs. Composited
- **The "One Scene" Approach (Integrated)**: 
  - Best for: Synchronized demos where 3D motion *directly drives* 2D data (e.g., a magnet moving and drawing a graph).
  - **Technique**: Use `self.add_fixed_in_frame_mobjects(...)` for 2D UI/Graphs. This allows you to rotate the 3D camera without breaking the 2D overlay.
- **The "Composited" Approach (Separated)**:
  - Best for: Complex 3D scenes where performance is low, or layout is tricky.
  - **Technique**: Render the 3D Scene and 2D Graphs as *separate videos* or separate scenes, then combine them in a video editor.
  - **Advice**: If the 2D graphs are just "data readouts", keeping them in the same scene is usually preferred for perfect synchronization.

### 3D Camera Angles: The "Head-On" Look
- **Avoid Defaults**: Standard overhead views are often boring and lack depth.
- **The "Immersive" View**:
  - **Recommended**: `phi=75*DEGREES` (closer to the ground), `theta=-90*DEGREES` (frontal/side).
  - **Why?**: This gives a sense of scale and depth, making the viewer feel like they are standing on the table watching the experiment. It maximizes information (circles look like ellipses, showing disk shape).

### Layout: Split Screen
- **The Rule**: **Never Overlap**. Do not let moving 3D objects pass behind or in front of 2D data plots.
- **Implementation**:
  - **Top Window (2D)**: Graphs, Flux meters, Labels. Pin to corners (e.g., `axes.to_corner(UL)`).
  - **Bottom Window (3D)**: The physical apparatus (Magnet, Coil). Shift the entire 3D group down (e.g., `scene_group.shift(DOWN * 2.5)`).
- **Visual Fidelity**:
  - **Backgrounds**: Always put `BackgroundRectangle(opacity=0.8)` behind graphs if there is any chance of overlap.
  - **Thick Lines**: Standard 1px lines are invisible on mobile. Use `stroke_width=4` minimum for graphs.
  - **Glowing Objects**: For coils/wires, set `opacity=0.1` + `stroke_width=8` to look like glowing copper/neon.

## 2. Dynamic Graphing (The "Real Time" Look)

### The Golden Rule: "Pointwise Partial Updaters"
**Do NOT use `TracedPath` or `always_redraw` for high-precision graphs.**
- `TracedPath`: Creates jagged, low-res lines prone to "ghosting".
- `always_redraw`: Performance heavy, causes flickering.

### The Correct Pattern
1. **Pre-calculate** the *entire* curve (all points) at initialization using `axes.c2p`.
2. Create a **Static VMobject** for the curve.
3. Use a **Custom Updater** to set the points of that VMobject to a *slice* of the pre-calculated points based on time/parameter.

```python
# 1. Pre-calculate
full_points = [axes.c2p(t, func(t)) for t in t_values]
curve = VMobject(color=YELLOW, stroke_width=4)

# 2. Define Updater
def update_curve(mob):
    # Map current parameter (e.g. magnet x) to index
    # Use searchsorted for O(log n) speed
    idx = np.searchsorted(t_values, tracker.get_value())
    # 3. Slice and Set
    mob.set_points_as_corners(full_points[:idx])

curve.add_updater(update_curve)
self.add_fixed_in_frame_mobjects(curve)
```

## 3. Physics & Math Precision ("No Faking It")

### Mathematical Integrity
- **The "Flat Top" Standard**: 
  - When a magnet moves through a coil, the Flux is constant (flat) while fully inside.
  - **Common Bug**: Using a simple bell curve (Gaussian) is WRONG.
  - **Technical Fix**: Calculate the exact **Circle-Square Intersection Area**.
- **Integration Bounds**: ensure integration bounds are shifted relative to the shape's center `(x - cx)` if the formula assumes `(0,0)`.

### Scale Matching
- **Size Matters**: If Magnet Radius is 0.8, Coil Side Length should be at least 1.6 (2x Radius) to physically fit. Do not use default `Radius=0.5, Side=1.0` blindly.

### Field Lines
- **Direction**: Magnet "North" face down $\rightarrow$ Field lines point **DOWN** (-Z).
- **Motion**: Ensure arrows move *with* the object (add to group).

### Animation State
- **Critical**: Always explicitly add `self.add(value_tracker)` to the scene. Updaters on "dangling" trackers may fail/garbage-collect.

## 4. Performance: "Keep Rendering Fast"

### The Speed Killers
- **Arrow3D is SLOW**: Complex mesh geometry. 10+ arrows can tank render times.
- **Too Many Sub-objects**: Loops creating dozens of 3D objects kill performance only if caching is ON.

### The Speed Fixes
1. **Use `Line3D` instead of `Arrow3D`**:
   - `Line3D` is ~10x Faster. Cleaner for field visualizations.
2. **Reduce Density**:
   - Use minimum density needed (e.g. 2, 4, 8 lines instead of 20).
3. **Disable Caching**:
   - Always run with `--disable_caching`. 
   - Caching often slows down scenes with many sub-objects.
   - Command: `manim -ql --disable_caching scene.py SceneName`
4. **Simplify Geometry**:
   - Lower resolution for cylinders (`resolution=8`).
   - Use flat shapes where depth isn't critical.

### Performance Benchmark
- **Bad**: 20 `Arrow3D` objects $\rightarrow$ ~8 minutes render time.
- **Good**: 14 `Line3D` objects + `--disable_caching` $\rightarrow$ ~20 seconds render time.
- **Result**: 24x speedup with minimal visual compromise.

## 5. Visual Polish (The "Wow" Factor)
- **Fonts**: Use `Text` (Arial-like) for labels. Use `MathTex` only for equations.
- **Stroke Width**: Bold lines (4px+) for visibility.

## 6. Agent Workflow & Verification

### Feedback Loop
- **Auto-Play**: After rendering, **ALWAYS** run the `open` command on the output video file immediately.
  - Command: `open /absolute/path/to/video.mp4`
- **Iterate**:
  1. **Low Qual (`-ql`)**: Check timing and motion.
  2. **Physics Check**: Does graph match motion? (Derivative zero when flux constant?)
  3. **High Qual**: Render final.
