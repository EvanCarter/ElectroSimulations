# AI Coding Agent Guide: High-Quality Manim Animations

This guide outlines best practices for generating 3B1B-style educational animations, specifically focusing on physics simulations with 3D elements and synchronized data visualization.

## 1. Scene Composition & Architecture
### Strategy: Integrated vs. Composited
- **The "One Scene" Approach (Integrated)**: 
  - Best for: Synchronized demos where 3D motion *directly drives* 2D data (e.g., a magnet moving and drawing a graph).
  - **Technique**: Use `self.add_fixed_in_frame_mobjects(...)` for 2D UI/Graphs. This allows you to rotate the 3D camera without breaking the 2D overlay.
- **The "Composited" Approach (Separated)**:
  - Best for: Complex 3D scenes where performance is low, or layout is tricky.
  - **Technique**: Render the 3D Scene and 2D Graphs as *separate videos* or separate scenes, then combine them in a video editor (or a Manim `Group` scene, though that's complex).
  - **Advice**: If the 2D graphs are just "data readouts", keeping them in the same scene is usually preferred for perfect synchronization. If they are complex mathematical derivations, separate them.

### 3D Camera Angles
- **Avoid Defaults**: The default camera is often too meaningless.
- **Head-On / Side Views**: For physics demos (like flux), a view that shows "depth" but preserves the "side profile" is best.
  - **Recommended**: `phi=55*DEGREES` (tilted down), `theta=-90*DEGREES` (frontal/side).
  - **Why?**: It maximizes information. Circles look like ellipses (showing disk shape), and displacement in depth is visible.

## 2. Dynamic Graphing (The "Real Time" Look)
### The Golden Rule: "Pointwise Partial Updaters"
**Do NOT use `TracedPath` or `always_redraw` for high-precision graphs.**
- `TracedPath`: Creates jagged, low-res lines prone to "ghosting" artifacts.
- `always_redraw`: Re-instantiates objects every frame, causing flickering and performance hits.

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
**Result**: Vector-perfect, smooth lines that grow exactly with the simulation, with zero artifacts.

## 3. Physics & Math Precision
### Exact Geometry (Integration Bounds)
- **Math Precision**: When integrating intersection areas (e.g., Circle-Square), ensure integration bounds are shifted relative to the shape's center if the formula assumes `(0,0)`.
  - Failure to do this results in incorrect "Bell Curve" shapes instead of "Flat Tops" for flux.
  
### Field Lines
- **Direction & Orientation**: 
  - Magnet "North" face down $\rightarrow$ Field lines point **DOWN** (-Z).
  - Ensure arrows move *with* the object. Use `mob.add(arrows)` if the group moves together, or updaters if simpler.

### Animation State (ValueTracker Lifecycle)
- **CRITICAL**: Always explicitly add `self.add(value_tracker)` to the scene.
- Without this, complex scenes (especially those with loops or multiple animations) may fail to update the tracker, resulting in static/frozen animations.

### Layout (Split Screen)
- **Separation**: To prevent 3D objects from clipping through 2D graphs, use a "Split Screen" approach.
- Shift all 3D content (`DOWN*2`) and keep UI/Graphs fixed in the opposite corner (`UP*3` or `UL`).
- This avoids the need for complex z-indexing or separate render passes.

## 4. Visual Polish (The "Wow" Factor)
- **Backgrounds for UI**: Always put `BackgroundRectangle(opacity=0.8)` behind graphs when overlaying on 3D scenes to prevent line conflicts.
- **Stroke Width**: Bold lines (4px+) read better on video than defaults.
- **San-serif Fonts**: Use `Text` (Arial-like) for labels. Use `MathTex` only for equations.

## 5. Agent Workflow & Verification
- **Auto-Play Videos**: 
  - After rendering any animation, **ALWAYS** run the `open` command on the output video file immediately.
  - Do not wait for the user to ask "can you see it" or "play it".
  - Command: `open /absolute/path/to/video.mp4`
