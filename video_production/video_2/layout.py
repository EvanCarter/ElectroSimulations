"""
Constrained Layout System for Manim
====================================
Solves the "move it left and it goes off screen" problem.

USAGE IN SCENES:
    from layout import Layout, REGIONS

    # Position by named region
    graph.move_to(REGIONS["right_panel"])
    generator.move_to(REGIONS["left_panel"])

    # Safe shift (clamped to screen)
    Layout.safe_shift(graph, DOWN * 2)

    # Check if on screen
    Layout.validate(graph)  # Raises if off-screen

    # Get safe position from natural language
    pos = Layout.parse_position("bottom right")
    graph.move_to(pos)
"""

from manim import *
import numpy as np

# ============================================================
# SCREEN BOUNDS (Manim default 16:9 frame)
# ============================================================
FRAME_WIDTH = 14.2   # Usable width (with margin)
FRAME_HEIGHT = 8.0   # Usable height (with margin)

SCREEN_LEFT = -FRAME_WIDTH / 2
SCREEN_RIGHT = FRAME_WIDTH / 2
SCREEN_TOP = FRAME_HEIGHT / 2
SCREEN_BOTTOM = -FRAME_HEIGHT / 2

MARGIN = 0.5  # Buffer from edge

# ============================================================
# NAMED REGIONS (use these instead of raw coordinates)
# ============================================================
REGIONS = {
    # Main layout zones
    "left_panel":    np.array([-4.0, 0.0, 0.0]),
    "right_panel":   np.array([3.5, 0.0, 0.0]),
    "center":        np.array([0.0, 0.0, 0.0]),

    # Quadrants
    "top_left":      np.array([-4.0, 2.0, 0.0]),
    "top_right":     np.array([4.0, 2.0, 0.0]),
    "bottom_left":   np.array([-4.0, -2.0, 0.0]),
    "bottom_right":  np.array([4.0, -2.0, 0.0]),

    # Edge positions (for labels, titles)
    "top_center":    np.array([0.0, 3.2, 0.0]),
    "bottom_center": np.array([0.0, -3.2, 0.0]),

    # Generator + Graph split layout (your common pattern)
    "generator":     np.array([-4.0, 0.0, 0.0]),
    "graph":         np.array([3.0, 0.0, 0.0]),
    "graph_upper":   np.array([3.0, 1.5, 0.0]),
    "graph_lower":   np.array([3.0, -1.5, 0.0]),

    # For 3-panel layouts
    "panel_1":       np.array([-4.5, 0.0, 0.0]),
    "panel_2":       np.array([0.0, 0.0, 0.0]),
    "panel_3":       np.array([4.5, 0.0, 0.0]),
}

# Natural language mappings
POSITION_ALIASES = {
    # Horizontal
    "left": "left_panel",
    "right": "right_panel",
    "middle": "center",
    "center": "center",

    # Corners
    "top left": "top_left",
    "upper left": "top_left",
    "top right": "top_right",
    "upper right": "top_right",
    "bottom left": "bottom_left",
    "lower left": "bottom_left",
    "bottom right": "bottom_right",
    "lower right": "bottom_right",

    # Edges
    "top": "top_center",
    "bottom": "bottom_center",
    "up": "top_center",
    "down": "bottom_center",

    # Your specific use cases
    "generator side": "generator",
    "graph side": "graph",
    "graph area": "graph",
    "upper graph": "graph_upper",
    "lower graph": "graph_lower",
}


class Layout:
    """Safe positioning utilities for Manim."""

    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Clamp value to range."""
        return max(min_val, min(max_val, value))

    @staticmethod
    def clamp_position(pos: np.ndarray, obj_width: float = 0, obj_height: float = 0) -> np.ndarray:
        """Clamp a position to keep object on screen."""
        half_w = obj_width / 2
        half_h = obj_height / 2

        return np.array([
            Layout.clamp(pos[0], SCREEN_LEFT + MARGIN + half_w, SCREEN_RIGHT - MARGIN - half_w),
            Layout.clamp(pos[1], SCREEN_BOTTOM + MARGIN + half_h, SCREEN_TOP - MARGIN - half_h),
            pos[2] if len(pos) > 2 else 0.0
        ])

    @staticmethod
    def safe_move_to(mobject: Mobject, target: np.ndarray) -> Mobject:
        """Move object to target, clamped to screen bounds."""
        # Get object dimensions
        width = mobject.width if hasattr(mobject, 'width') else 0
        height = mobject.height if hasattr(mobject, 'height') else 0

        safe_pos = Layout.clamp_position(target, width, height)
        mobject.move_to(safe_pos)
        return mobject

    @staticmethod
    def safe_shift(mobject: Mobject, direction: np.ndarray) -> Mobject:
        """Shift object by direction, but clamp to screen bounds."""
        current = mobject.get_center()
        target = current + direction
        return Layout.safe_move_to(mobject, target)

    @staticmethod
    def is_on_screen(mobject: Mobject) -> bool:
        """Check if object is fully visible on screen."""
        center = mobject.get_center()
        width = mobject.width if hasattr(mobject, 'width') else 0
        height = mobject.height if hasattr(mobject, 'height') else 0

        left = center[0] - width/2
        right = center[0] + width/2
        top = center[1] + height/2
        bottom = center[1] - height/2

        return (left >= SCREEN_LEFT and right <= SCREEN_RIGHT and
                bottom >= SCREEN_BOTTOM and top <= SCREEN_TOP)

    @staticmethod
    def validate(mobject: Mobject, name: str = "object") -> None:
        """Raise an error if object is off screen (for debugging)."""
        if not Layout.is_on_screen(mobject):
            center = mobject.get_center()
            raise ValueError(
                f"'{name}' is off screen! Center: ({center[0]:.1f}, {center[1]:.1f}), "
                f"Size: {mobject.width:.1f}x{mobject.height:.1f}. "
                f"Screen bounds: x=[{SCREEN_LEFT:.1f}, {SCREEN_RIGHT:.1f}], "
                f"y=[{SCREEN_BOTTOM:.1f}, {SCREEN_TOP:.1f}]"
            )

    @staticmethod
    def parse_position(description: str) -> np.ndarray:
        """
        Convert natural language to position.

        Examples:
            parse_position("bottom right") -> REGIONS["bottom_right"]
            parse_position("graph area") -> REGIONS["graph"]
        """
        desc_lower = description.lower().strip()

        # Direct alias match
        if desc_lower in POSITION_ALIASES:
            return REGIONS[POSITION_ALIASES[desc_lower]].copy()

        # Direct region match
        if desc_lower.replace(" ", "_") in REGIONS:
            return REGIONS[desc_lower.replace(" ", "_")].copy()

        # Try to parse compound descriptions
        x, y = 0.0, 0.0

        if "left" in desc_lower:
            x = -4.0
        elif "right" in desc_lower:
            x = 4.0

        if "top" in desc_lower or "upper" in desc_lower or "up" in desc_lower:
            y = 2.5
        elif "bottom" in desc_lower or "lower" in desc_lower or "down" in desc_lower:
            y = -2.5

        return np.array([x, y, 0.0])

    @staticmethod
    def get_region(name: str) -> np.ndarray:
        """Get a named region position."""
        if name in REGIONS:
            return REGIONS[name].copy()
        if name in POSITION_ALIASES:
            return REGIONS[POSITION_ALIASES[name]].copy()
        raise ValueError(f"Unknown region: '{name}'. Available: {list(REGIONS.keys())}")

    @staticmethod
    def create_axes_at(region: str, width: float = 5.0, height: float = 2.5,
                       x_range: list = None, y_range: list = None) -> Axes:
        """
        Create axes positioned at a named region.

        Usage:
            axes = Layout.create_axes_at("graph", width=5, height=2.5)
        """
        x_range = x_range or [0, 8, 1]
        y_range = y_range or [-12, 12, 4]

        pos = Layout.get_region(region)

        axes = Axes(
            x_range=x_range,
            y_range=y_range,
            x_length=width,
            y_length=height,
            axis_config={"include_numbers": False},
        )
        axes.move_to(pos)
        return axes

    @staticmethod
    def debug_regions(scene) -> VGroup:
        """Add visual markers for all regions (for debugging layout)."""
        markers = VGroup()
        for name, pos in REGIONS.items():
            dot = Dot(pos, color=YELLOW, radius=0.1)
            label = Text(name, font_size=14, color=YELLOW).next_to(dot, UP, buff=0.1)
            markers.add(dot, label)
        scene.add(markers)
        return markers


# ============================================================
# GRAPH POSITIONING HELPERS
# ============================================================

def position_graph_right(axes: Axes, y_offset: float = 0) -> Axes:
    """Position a graph in the standard right-side location."""
    target = REGIONS["graph"].copy()
    target[1] += y_offset
    Layout.safe_move_to(axes, target)
    return axes


def position_stacked_graphs(axes_list: list, region: str = "right_panel",
                            spacing: float = 0.3) -> list:
    """
    Stack multiple graphs vertically in a region.

    Usage:
        axes_a, axes_b, axes_c = create_three_axes()
        position_stacked_graphs([axes_a, axes_b, axes_c], "right_panel")
    """
    n = len(axes_list)
    base_pos = Layout.get_region(region)

    # Calculate total height needed
    total_height = sum(ax.height for ax in axes_list) + spacing * (n - 1)

    # Start from top
    current_y = base_pos[1] + total_height / 2

    for ax in axes_list:
        current_y -= ax.height / 2
        ax.move_to(np.array([base_pos[0], current_y, 0]))
        current_y -= ax.height / 2 + spacing

    return axes_list
