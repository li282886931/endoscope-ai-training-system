from __future__ import annotations

from .domain import ScoreReport, ScoreTemplate, SessionRecord


def score_path(deviation_ms: int, total_ms: int, wrong_branch: int, branch_total: int) -> float:
    ratio = deviation_ms / max(total_ms, 1)
    penalty = ratio + 0.5 * wrong_branch / max(branch_total, 1)
    return round(100.0 * max(0.0, 1.0 - penalty), 1)


def score_collision(n_light: int, n_heavy: int, strength_sum: float, key_site_heavy: int, base: float = 10.0) -> float:
    weighted = (n_light + 2.0 * n_heavy + key_site_heavy) * base + strength_sum * 0.05
    return round(100.0 * max(0.0, 1.0 - weighted / 100.0), 1)


def score_time(t_actual_ms: int, t_standard_ms: int) -> float:
    ratio = t_actual_ms / max(t_standard_ms, 1)
    return round(100.0 * min(1.0, max(0.0, 1.5 - ratio)), 1)


def score_flow(n_pause: int, n_reverse: int) -> float:
    return round(100.0 * max(0.0, 1.0 - 0.10 * n_pause - 0.05 * n_reverse), 1)


def total_score(
    s_path: float,
    s_coll: float,
    s_time: float,
    s_flow: float,
    weights: tuple[float, float, float, float] = (0.40, 0.35, 0.15, 0.10),
) -> float:
    return round(weights[0] * s_path + weights[1] * s_coll + weights[2] * s_time + weights[3] * s_flow, 1)


def build_issue_list(session: SessionRecord) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    if session.wrong_branch:
        issues.append(
            {
                "type": "wrong_branch",
                "count": session.wrong_branch,
                "message": "Detected standard path branch mismatch.",
            }
        )
    collision_count = session.n_light + session.n_heavy
    if collision_count:
        issues.append(
            {
                "type": "collision",
                "light": session.n_light,
                "heavy": session.n_heavy,
                "strength_sum": session.strength_sum,
                "message": "Detected wall contact events.",
            }
        )
    if session.n_pause or session.n_reverse:
        issues.append(
            {
                "type": "flow",
                "pause": session.n_pause,
                "reverse": session.n_reverse,
                "message": "Detected operation fluency issues.",
            }
        )
    return issues


class Scorer:
    def __init__(self, template: ScoreTemplate):
        self.template = template
        self.weights = (template.w_path, template.w_collision, template.w_time, template.w_flow)

    def score(self, session: SessionRecord) -> ScoreReport:
        s_path = score_path(session.deviation_ms, session.duration_ms, session.wrong_branch, session.branch_total)
        s_collision = score_collision(session.n_light, session.n_heavy, session.strength_sum, session.key_site_heavy)
        s_time = score_time(session.duration_ms, session.standard_ms)
        s_flow = score_flow(session.n_pause, session.n_reverse)
        total = total_score(s_path, s_collision, s_time, s_flow, self.weights)
        return ScoreReport(
            total=total,
            s_path=s_path,
            s_collision=s_collision,
            s_time=s_time,
            s_flow=s_flow,
            issues=build_issue_list(session),
            template_id=self.template.template_id,
        )

