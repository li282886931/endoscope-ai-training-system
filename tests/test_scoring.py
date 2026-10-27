from endoscope_ai_training.core.domain import ScoreTemplate, SessionRecord
from endoscope_ai_training.core.scoring import (
    Scorer,
    score_collision,
    score_flow,
    score_path,
    score_time,
    total_score,
)


def test_scoring_formulas_match_design_document():
    assert score_path(deviation_ms=10_000, total_ms=100_000, wrong_branch=1, branch_total=5) == 80.0
    assert score_collision(n_light=1, n_heavy=1, strength_sum=100, key_site_heavy=1) == 55.0
    assert score_time(t_actual_ms=120_000, t_standard_ms=120_000) == 50.0
    assert score_flow(n_pause=1, n_reverse=2) == 80.0
    assert total_score(80, 55, 50, 80) == 66.8


def test_scorer_builds_report_with_ordered_issues():
    session = SessionRecord(
        session_id="S1",
        user_name="student",
        model_id="trachea_model_001",
        target_path_id="P_RUL",
        mode="exam",
        start_ts=1_000,
        end_ts=121_000,
        duration_ms=120_000,
        standard_ms=120_000,
        deviation_ms=10_000,
        wrong_branch=1,
        branch_total=5,
        n_light=1,
        n_heavy=1,
        strength_sum=100,
        key_site_heavy=1,
        n_pause=1,
        n_reverse=2,
    )

    report = Scorer(ScoreTemplate()).score(session)

    assert report.total == 67.4
    assert report.s_path == 81.7
    assert report.s_collision == 55.0
    assert report.issues[0]["type"] == "wrong_branch"
    assert report.issues[1]["type"] == "collision"
