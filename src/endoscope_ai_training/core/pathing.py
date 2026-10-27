from __future__ import annotations

from .domain import PathCompareResult, StandardPath


def compare_path(
    node_id: str | None,
    deviation_mm: float,
    path: StandardPath,
    off_path_threshold_mm: float = 10.0,
) -> PathCompareResult:
    if node_id is None:
        return PathCompareResult(None, deviation_mm, False, False, True, 0.0)

    if node_id not in path.node_sequence:
        return PathCompareResult(node_id, deviation_mm, False, True, False, 0.0)

    off_path = deviation_mm > off_path_threshold_mm
    index = path.node_sequence.index(node_id)
    progress = round((index + 1) / max(len(path.node_sequence), 1), 2)
    return PathCompareResult(node_id, deviation_mm, not off_path, False, off_path, progress)


def calibrate_scale(ref_diameter_mm: float, est_diameter_px: float, focal_px: float) -> float:
    if ref_diameter_mm <= 0 or est_diameter_px <= 0 or focal_px <= 0:
        raise ValueError("ref_diameter_mm, est_diameter_px and focal_px must be positive")
    depth_mm = ref_diameter_mm * focal_px / est_diameter_px
    return depth_mm / focal_px

