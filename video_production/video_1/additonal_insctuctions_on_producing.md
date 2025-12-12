# Production Guide: The "Real Physics" Style

This document captures the specific aesthetic and technical requirements for creating animations that meet the "Real Physics" standard.

## 1. The Aesthetic: "Immersive but Clean"

### Camera Angles
- **The "Head-On" Look**: 
  - Standard overhead views are boring.
  - Use `phi=75°` (closer to the ground) to give a sense of scale and depth.
  - Keep `theta=-90°` for side-scrolling motion clarity.
  - *Goal*: The viewer should feel like they are standing on the table watching the experiment.

### Layout: Split Screen
- **Never Overlap**: 
  - Do not let moving 3D objects pass behind or in front of 2D data plots. It looks messy.
  - **Solution**: Use a hard visual separation.
    - **Top Window (2D)**: Graphs, Flux meters, Labels.
    - **Bottom Window (3D)**: The physical apparatus (Magnet, Coil).
  - **Implementation**:
    - Shift 3D Group: `scene_group.shift(DOWN * 2.5)`
    - Pin 2D graphs: `axes.to_corner(UL)`

### Visual Fidelity
- **Thick Lines**: Standard 1px lines are invisible on mobile. Use `stroke_width=4` minimum for graphs.
- **Glowing Objects**: Set `opacity=0.1` + `stroke_width=8` for Coils to make them look like glowing copper/neon rather than flat wireframes.

## 2. The Physics: "No Faking It"

### Mathematical Integrity
- **The "Flat Top" Standard**: 
  - When a magnet moves through a coil, the Flux is constant (flat) while fully inside.
  - **Common Bug**: Using a simple bell curve (Gaussian) is WRONG.
  - **Technical Fix**: You must calculate the exact `Circle-Square Intersection Area`.
  - **Critical Math Detail**: When integrating, ensure bounds are shifted relative to the circle center `(x - cx)`.

### Scale Matching
- **Size Matters**: 
  - If the Magnet Radius is 0.8, the Coil Side Length should be at least 1.6 (2x Radius) to physically fit.
  - Don't use default `Radius=0.5, Side=1.0` blindly.

## 3. The Workflow: "Automated & Verified"

### Animation Tech
- **The ValueTracker Rule**: 
  - Always `self.add(value_tracker)` to the scene. 
  - If you rely on Updaters reading a "dangling" tracker, Manim might garbage-collect or ignore it, leading to static videos.

### Instant Feedback
- **Auto-Play**:
  - Never wait for the user to ask "show me".
  - Always run: `open /path/to/video.mp4` immediately after generation.

### Iterate
1. **Low Qual (`-ql`)**: Check timing and motion.
2. **Physics Check**: Does the graph match the motion? (e.g., Derivative zero when flux constant?)
3. **High Qual**: Render final.
