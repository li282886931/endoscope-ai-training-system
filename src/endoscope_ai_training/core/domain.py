from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class TracheaNode:
    level: int
    name: str
    parent: str | None
    children: list[str]
    ref_diameter_mm: float


@dataclass(frozen=True)
class TracheaTree:
    model_id: str
    version: str
    scale_mm_per_px: float
    nodes: dict[str, TracheaNode]

    def get_node(self, node_id: str) -> TracheaNode | None:
        return self.nodes.get(node_id)


@dataclass(frozen=True)
class StandardPath:
    path_id: str
    name: str
    model_id: str
    node_sequence: list[str]
    standard_time_ms: int
    critical_nodes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StandardPath":
        return cls(
            path_id=str(data["path_id"]),
            name=str(data["name"]),
            model_id=str(data["model_id"]),
            node_sequence=[str(item) for item in data["node_sequence"]],
            standard_time_ms=int(data["standard_time_ms"]),
            critical_nodes=[str(item) for item in data.get("critical_nodes", [])],
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PathCompareResult:
    node_id: str | None
    deviation_mm: float
    on_standard_path: bool
    wrong_branch: bool
    off_path: bool
    path_progress: float


@dataclass(frozen=True)
class TrajectoryPoint:
    ts: int
    node_id: str | None
    pos_mm: tuple[float, float, float]
    deviation_mm: float
    frame_seq: int


@dataclass(frozen=True)
class CollisionEvent:
    ts: int
    level: str
    strength: float
    node_id: str | None
    frame_seq: int


@dataclass(frozen=True)
class ScoreTemplate:
    w_path: float = 0.40
    w_collision: float = 0.35
    w_time: float = 0.15
    w_flow: float = 0.10
    template_id: str = "default_exam"


@dataclass(frozen=True)
class ScoreReport:
    total: float
    s_path: float
    s_collision: float
    s_time: float
    s_flow: float
    issues: list[dict[str, Any]]
    template_id: str = "default_exam"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SessionMeta:
    session_id: str
    user_name: str
    model_id: str
    target_path_id: str
    mode: str
    start_ts: int
    end_ts: int | None = None
    duration_ms: int | None = None
    total_score: float | None = None


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    user_name: str
    model_id: str
    target_path_id: str
    mode: str
    start_ts: int
    end_ts: int | None
    duration_ms: int
    standard_ms: int
    deviation_ms: int
    wrong_branch: int
    branch_total: int
    n_light: int
    n_heavy: int
    strength_sum: float
    key_site_heavy: int
    n_pause: int
    n_reverse: int

