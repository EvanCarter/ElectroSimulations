# Video 2 - Phase Shift Animations

## Agent Usage (MANDATORY)

**Always delegate to these agents - do not do the work directly:**

| Task | Agent | When to use |
|------|-------|-------------|
| **Manim scene creation/editing** | `manim-coder` | Any new scene, scene modifications, or Manim code changes |
| **Render & verify output** | `animation-qa` | **ALWAYS** after manim-coder finishes - NO EXCEPTIONS |
| **Codebase exploration** | `Explore` | "Where is X?", "How does Y work?", understanding existing patterns |
| **Implementation planning** | `Plan` | Before starting multi-step features or refactors |

### CRITICAL: animation-qa is MANDATORY after any scene work

Every time `manim-coder` writes or edits a scene, you MUST immediately spawn `animation-qa` to:
1. Render the scene
2. Extract and view frames
3. Verify the output matches the code intent
4. **Validate physics-visual correlation** (see below)
5. Report any issues

**Never skip this step.** Do not ask the user if they want QA. Do not wait. Just do it.

### CRITICAL: Physics Validation in QA

The `animation-qa` agent MUST verify that **voltage graphs match the visual magnet-coil proximity**:

**The Rule:** Voltage ≠ 0 ONLY when a magnet is within ±45° (`influence_width`) of a coil. When NO magnet is near a coil, voltage MUST be ~0 (flat line).

**How to validate:**
1. Find frames where a specific coil has NO magnet visually nearby (>45° away from all magnets)
2. Check if that coil's voltage trace shows ~0 at that moment
3. Find frames where a magnet is CROSSING a coil (within ±45°)
4. Check if that coil's voltage trace shows a peak/trough at that moment
5. Report any physics-visual mismatches as **FAIL**

**Common failure modes:**
- Voltage showing continuous sine wave when magnets periodically leave coil's influence zone
- Flat voltage when a magnet is clearly passing the coil visually
- Phase of voltage peak not matching when magnet crosses coil

**Geometry reference for validation:**
- 2 magnets (180° apart): Each coil has ~50% "dead time" with no magnet nearby → expect flat periods
- 4 magnets (90° apart): Coils at 120° spacing still have brief gaps (~15° rotation) when no magnet is within 45° → expect brief flat periods
- The `influence_width = PI/4` (45°) means a magnet only affects coils within ±45° of its position

Example workflow for a new scene:
1. `Plan` agent → design the scene structure
2. `manim-coder` agent → write the code
3. `animation-qa` agent → render and verify (AUTOMATIC, NOT OPTIONAL)

**Rendering flags:**
- During QA iteration: use `-ql` (no `-p`) to avoid popup spam
- Only when FULLY DONE: use `open <video_path>` to play the final result
- For 4K final renders: use `-qk` (no `-p`), then `open` the result

## Key Files

- **`script.md`** - Full video script with production progress tables at the bottom
- **`manim.cfg`** - Local config, sets `media_dir = ./video_2_media`

## Configuration

**CRITICAL: Run from the video_2 directory** so output goes to the correct folder:
```bash
cd video_production/video_2
uv run manim -ql scene_file.py SceneName     # Quick preview (480p)
uv run manim -qk scene_file.py SceneName     # 4K final render
```

The `manim.cfg` sets `media_dir = ./video_2_media`, so running from this directory outputs to `video_production/video_2/video_2_media/`.

**Important:** Always use `uv run` for all Python/manim commands. The project uses uv for dependency management.

**Do NOT run from the repo root** - that outputs to a different `media/` folder.

## Animation Principles

### Scene Organization
- Create **new scene classes** rather than modifying existing ones - makes it easy to compare iterations
- Name scenes with version suffixes (V2, V3) or descriptive names (PhaseStaticScene, PhaseShiftRevealScene)

### Graph Clarity
- **Fewer cycles = clearer visualization** - reduce simulation time to show 1-2 rotations instead of many
- When comparing multiple signals, consider **separate graphs** (one per signal) vs overlay - depends on what you're trying to show
- Remove redundant visual elements - if something is already clear from another element, don't duplicate it

### Creative Visualization
- Show relationships through animation, not just static display
- Example: phase shift can be shown as horizontal sliding of overlapped waveforms - demonstrates that phase = time delay
- Let the animation tell the story progressively (draw base curve, then reveal shifted versions)

### Updaters
- When using `add_updater` with dt parameter, it must be named `dt` exactly
- Use ValueTracker for time-based animations that need to sync multiple elements

### Generator Physics (REFERENCE: scene_phase_shift_final.py)

**✨ PINNACLE IMPLEMENTATION**: `scene_phase_shift_final.py` → `PhaseShiftSceneFinal`

This is the BEST way to animate generator physics. Use this as the reference for all future scenes.

**Key Features:**
- **Localized sinusoidal flux model** (`generator.py::calculate_sinusoidal_flux`)
  - `influence_width` = angular size where magnet affects coil
  - **CRITICAL:** Must calculate from geometry: `influence_width = 2 * MAGNET_RADIUS / MAGNET_PATH_RADIUS`
  - Default PI/4 (45°) only works for MAGNET_RADIUS=0.8, MAGNET_PATH_RADIUS=2.0
  - For smaller magnets (e.g., 4-magnet config with MAGNET_RADIUS=0.6), calculate explicitly!
  - Produces smooth sine waves that match the visual
  - Voltage = 0 when no magnet is near coil (physically accurate)
- **Sign convention**: North magnet entering coil → voltage goes **negative** (0 → negative → 0). South magnet entering → voltage goes **positive**. This is `V = -dΦ/dt` (Lenz's law).
- Uses `calculate_sine_voltage_trace()` for voltage calculations
- No gaussian smoothing needed - the sinusoidal model produces clean curves
- Coil positions defined as angular offset from 12 o'clock (clockwise positive)
- Standard positions: 12 o'clock (0°), 4 o'clock (120°), 8 o'clock (240°) for 3-phase
- **Square coils** that match magnet size: Use `Rectangle(width=MAGNET_RADIUS*2.0, height=MAGNET_RADIUS*2.0)` - coil should match magnet diameter to capture full flux. See `scene_single_coil_4mag.py` for reference

**When creating new scenes:**
1. Import: `from generator import build_rotor, calculate_sine_voltage_trace`
2. Use `calculate_sine_voltage_trace()` for voltage data
3. The default `influence_width=PI/4` in `calculate_sinusoidal_flux` is already tuned

**Migration Complete (Dec 27, 2025):**
All scenes updated to use FINAL sinusoidal model:
- ✅ `scene_phase_shift_final.py` - PhaseShiftSceneFinal (reference implementation)
- ✅ `scene_phase_static.py` - PhaseStaticScene (fixed coils at 12/4/8 o'clock)
- ✅ `scene_phase_static.py` - TwoPhaseVsSplitPhaseScene (90° vs 180° comparison)

Old physics (circle-overlap + gaussian smoothing) removed from all scenes.
Removed scenes: PhaseShiftRevealScene (not needed), PhaseShiftSceneV3 (showed Doppler effects from moving coils, not standard 3-phase).

## Scene Tracking

The `script.md` file contains two tables at the bottom:

1. **PRODUCTION PROGRESS** - Tracks main script sections and their completion status
2. **ANIMATION ASSETS** - Supplementary scenes that can be used as B-roll, linked to relevant script sections

When creating new scenes, add them to the appropriate table with file path, scene class name, and related script section.
