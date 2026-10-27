from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .domain import CollisionEvent


class CollisionLevel(Enum):
    NONE = "none"
    WARN = "warn"
    LIGHT = "light"
    HEAVY = "heavy"


@dataclass(frozen=True)
class CollisionConfig:
    dist_warn_mm: float = 8.0
    lumen_ratio_contact: float = 0.55
    white_area_max: float = 0.08
    strong_threshold: float = 60.0
    confirm_frames: int = 3


def judge_collision(
    d_min_mm: float,
    lumen_ratio: float,
    white_area: float,
    streak: int,
    cfg: CollisionConfig | None = None,
) -> tuple[CollisionLevel, int]:
    config = cfg or CollisionConfig()
    contacting = (lumen_ratio <= config.lumen_ratio_contact) or (white_area > config.white_area_max)
    if not contacting:
        if d_min_mm <= config.dist_warn_mm:
            return CollisionLevel.WARN, int(100 * (1.0 - d_min_mm / config.dist_warn_mm))
        return CollisionLevel.NONE, 0

    strength = int(100 * (1.0 - d_min_mm / max(config.dist_warn_mm * 2, 1e-3)))
    strength = min(100, max(10, strength + int(white_area * 200)))
    level = CollisionLevel.HEAVY if strength >= config.strong_threshold else CollisionLevel.LIGHT
    return level, strength


class CollisionDetector:
    def __init__(self, config: CollisionConfig | None = None):
        self.config = config or CollisionConfig()
        self.streak = 0

    def update(
        self,
        d_min_mm: float,
        lumen_ratio: float,
        white_area: float,
        node_id: str | None,
        ts: int,
        frame_seq: int,
    ) -> CollisionEvent | None:
        state, strength = judge_collision(d_min_mm, lumen_ratio, white_area, self.streak, self.config)
        if state in (CollisionLevel.NONE, CollisionLevel.WARN):
            self.streak = 0
            return None

        self.streak += 1
        if self.streak < self.config.confirm_frames:
            return None
        return CollisionEvent(ts=ts, level=state.value, strength=strength, node_id=node_id, frame_seq=frame_seq)

