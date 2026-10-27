from endoscope_ai_training.core.domain import StandardPath, TracheaNode, TracheaTree
from endoscope_ai_training.core.pathing import compare_path


def test_compare_path_reports_progress_for_standard_node():
    path = StandardPath(
        path_id="P_RUL",
        name="right upper lobe",
        model_id="M1",
        node_sequence=["L0", "L1", "L2", "L3"],
        standard_time_ms=120_000,
        critical_nodes=["L1"],
    )

    result = compare_path("L2", deviation_mm=4.0, path=path, off_path_threshold_mm=10.0)

    assert result.on_standard_path is True
    assert result.wrong_branch is False
    assert result.off_path is False
    assert result.path_progress == 0.75


def test_compare_path_detects_wrong_branch_and_off_path():
    path = StandardPath(
        path_id="P_RUL",
        name="right upper lobe",
        model_id="M1",
        node_sequence=["L0", "L1", "L2", "L3"],
        standard_time_ms=120_000,
        critical_nodes=[],
    )

    wrong = compare_path("L9", deviation_mm=1.0, path=path, off_path_threshold_mm=10.0)
    off = compare_path("L2", deviation_mm=11.0, path=path, off_path_threshold_mm=10.0)

    assert wrong.wrong_branch is True
    assert wrong.on_standard_path is False
    assert off.off_path is True
    assert off.on_standard_path is False


def test_tree_node_lookup_uses_defined_nodes():
    tree = TracheaTree(
        model_id="M1",
        version="1.0",
        scale_mm_per_px=0.018,
        nodes={"L0": TracheaNode(level=0, name="声门", parent=None, children=["L1"], ref_diameter_mm=16.0)},
    )

    assert tree.get_node("L0").name == "声门"
    assert tree.get_node("missing") is None

