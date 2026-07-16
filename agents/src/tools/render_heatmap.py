"""
Standalone heatmap renderer for CIVITAS traffic simulation results.

Generates SVG and PNG congestion heatmaps for route scenario comparisons.
Can be invoked from the CLI or imported as a module by the SimulationAgent.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap

    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False


# Custom colormap: green (low) -> yellow (medium) -> red (high congestion)
CIVITAS_CMAP_COLORS = [(0.2, 0.7, 0.3), (1.0, 0.85, 0.2), (0.9, 0.15, 0.15)]


def _get_output_dir() -> str:
    """Return the heatmaps output directory, creating it if needed."""
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    heatmap_dir = os.path.join(base_dir, "data", "heatmaps")
    os.makedirs(heatmap_dir, exist_ok=True)
    return heatmap_dir


def _build_congestion_grid(route_name: str, grid_size: int = 10) -> "np.ndarray":
    """Build a synthetic congestion grid for a given route scenario."""
    if not HAS_PLOT:
        return None

    data = np.random.RandomState(42).rand(grid_size, grid_size) * 0.15

    name = route_name.lower()
    if "surface" in name or "street" in name:
        # Surface streets: diagonal corridor with high spread
        for i in range(grid_size):
            data[i, i] = 0.85 + np.random.RandomState(i).rand() * 0.15
            if i > 0:
                data[i - 1, i] = 0.55
            if i < grid_size - 1:
                data[i + 1, i] = 0.45
            # Side-street bleed
            if i > 1:
                data[i - 2, i] = 0.25
    else:
        # Highway: isolated L-shaped corridor
        for i in range(grid_size):
            data[0, i] = 0.75 + np.random.RandomState(i + 100).rand() * 0.15
            data[i, grid_size - 1] = 0.70
        # Onramp congestion hotspot
        data[0, 0] = 0.95
        data[1, 0] = 0.60

    return data


def render_heatmap_png(route_name: str, score: Optional[float] = None) -> str:
    """
    Render a PNG congestion heatmap for the given route scenario.

    Args:
        route_name: Name of the route corridor (e.g. 'Surface Streets', 'Highway 1')
        score: Optional congestion score to display on the image

    Returns:
        Absolute file path to the generated PNG image, or a mock URL fallback.
    """
    if not HAS_PLOT:
        logger.warning("matplotlib not available; returning mock heatmap path")
        return f"mock_url_for_{route_name.lower().replace(' ', '_')}_heatmap.png"

    data = _build_congestion_grid(route_name)
    cmap = LinearSegmentedColormap.from_list("civitas_heat", CIVITAS_CMAP_COLORS, N=256)

    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(data, cmap=cmap, interpolation="bilinear", vmin=0, vmax=1)

    title = f"{route_name} Congestion"
    if score is not None:
        title += f" (Score: {score:.0f})"
    ax.set_title(title, fontsize=10, fontweight="bold", pad=8)
    ax.axis("off")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Congestion Level", fontsize=8)

    output_dir = _get_output_dir()
    filename = f"{route_name.lower().replace(' ', '_')}_heatmap.png"
    filepath = os.path.join(output_dir, filename)

    fig.savefig(filepath, bbox_inches="tight", dpi=150, facecolor="white")
    plt.close(fig)

    logger.info(f"Rendered PNG heatmap: {filepath}")
    return filepath


def render_heatmap_svg(route_name: str, score: Optional[float] = None) -> str:
    """
    Render an SVG congestion heatmap for the given route scenario.

    Args:
        route_name: Name of the route corridor
        score: Optional congestion score to display

    Returns:
        Absolute file path to the generated SVG image.
    """
    if not HAS_PLOT:
        logger.warning("matplotlib not available; returning mock heatmap path")
        return f"mock_url_for_{route_name.lower().replace(' ', '_')}_heatmap.svg"

    data = _build_congestion_grid(route_name)
    cmap = LinearSegmentedColormap.from_list("civitas_heat", CIVITAS_CMAP_COLORS, N=256)

    fig, ax = plt.subplots(figsize=(4, 4))
    im = ax.imshow(data, cmap=cmap, interpolation="bilinear", vmin=0, vmax=1)

    title = f"{route_name} Congestion"
    if score is not None:
        title += f" (Score: {score:.0f})"
    ax.set_title(title, fontsize=10, fontweight="bold", pad=8)
    ax.axis("off")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Congestion Level", fontsize=8)

    output_dir = _get_output_dir()
    filename = f"{route_name.lower().replace(' ', '_')}_heatmap.svg"
    filepath = os.path.join(output_dir, filename)

    fig.savefig(filepath, format="svg", bbox_inches="tight", facecolor="white")
    plt.close(fig)

    logger.info(f"Rendered SVG heatmap: {filepath}")
    return filepath


def render_comparison(
    route_a_name: str,
    score_a: float,
    route_b_name: str,
    score_b: float,
    winner: str = None,
) -> str:
    """
    Render a side-by-side comparison heatmap of both route scenarios.

    Args:
        route_a_name: Name of route A
        score_a: Congestion score for route A
        route_b_name: Name of route B
        score_b: Congestion score for route B
        winner: Optional winner ID for highlighting

    Returns:
        Absolute file path to the generated comparison PNG.
    """
    if not HAS_PLOT:
        return "mock_url_for_comparison_heatmap.png"

    data_a = _build_congestion_grid(route_a_name)
    data_b = _build_congestion_grid(route_b_name)
    cmap = LinearSegmentedColormap.from_list("civitas_heat", CIVITAS_CMAP_COLORS, N=256)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

    # Route A
    border_a = "blue" if winner and "route_a" in winner else "gray"
    ax1.imshow(data_a, cmap=cmap, interpolation="bilinear", vmin=0, vmax=1)
    ax1.set_title(
        f"{route_a_name}\nScore: {score_a:.0f}", fontsize=9, fontweight="bold"
    )
    ax1.axis("off")
    for spine in ax1.spines.values():
        spine.set_edgecolor(border_a)
        spine.set_linewidth(3)
        spine.set_visible(True)

    # Route B
    border_b = "blue" if winner and "route_b" in winner else "gray"
    ax2.imshow(data_b, cmap=cmap, interpolation="bilinear", vmin=0, vmax=1)
    ax2.set_title(
        f"{route_b_name}\nScore: {score_b:.0f}", fontsize=9, fontweight="bold"
    )
    ax2.axis("off")
    for spine in ax2.spines.values():
        spine.set_edgecolor(border_b)
        spine.set_linewidth(3)
        spine.set_visible(True)

    fig.suptitle(
        "CIVITAS Congestion Simulation Comparison",
        fontsize=11,
        fontweight="bold",
        y=1.02,
    )
    fig.tight_layout()

    output_dir = _get_output_dir()
    filepath = os.path.join(output_dir, "comparison_heatmap.png")
    fig.savefig(filepath, bbox_inches="tight", dpi=150, facecolor="white")
    plt.close(fig)

    logger.info(f"Rendered comparison heatmap: {filepath}")
    return filepath


if __name__ == "__main__":
    """CLI entry point for testing heatmap generation."""
    logging.basicConfig(level=logging.INFO)

    print("Generating heatmaps...")
    png_a = render_heatmap_png("Surface Streets", score=92)
    png_b = render_heatmap_png("Highway 1", score=74)
    svg_a = render_heatmap_svg("Surface Streets", score=92)
    svg_b = render_heatmap_svg("Highway 1", score=74)
    comp = render_comparison(
        "Surface Streets", 92, "Highway 1", 74, winner="route_a_speed_first"
    )

    print(f"PNG A: {png_a}")
    print(f"PNG B: {png_b}")
    print(f"SVG A: {svg_a}")
    print(f"SVG B: {svg_b}")
    print(f"Comparison: {comp}")
    print("Done.")
