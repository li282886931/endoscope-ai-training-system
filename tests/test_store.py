from pathlib import Path

from endoscope_ai_training.core.domain import CollisionEvent, ScoreReport, SessionMeta, TrajectoryPoint
from endoscope_ai_training.storage.session_store import SessionStore


def test_session_store_persists_session_detail_and_export(tmp_path: Path):
    store = SessionStore(tmp_path / "training.db")
    session_id = store.create_session(
        SessionMeta(
            session_id="S1",
            user_name="student",
            model_id="trachea_model_001",
            target_path_id="P_RUL",
            mode="exam",
            start_ts=1_000,
        )
    )
    store.append_trajectory(session_id, [TrajectoryPoint(ts=1_010, node_id="L1", pos_mm=(1, 2, 3), deviation_mm=4.0, frame_seq=1)])
    store.append_collision(session_id, CollisionEvent(ts=1_020, level="light", strength=32, node_id="L1", frame_seq=2))
    store.save_score(session_id, ScoreReport(total=90.0, s_path=95.0, s_collision=85.0, s_time=90.0, s_flow=92.0, issues=[]))

    detail = store.query_session(session_id)
    assert detail["session"]["session_id"] == "S1"
    assert detail["trajectory"][0]["node_id"] == "L1"
    assert detail["collisions"][0]["strength"] == 32
    assert detail["score"]["total"] == 90.0

    csv_text = store.export_csv(session_id)
    assert "trajectory" in csv_text
    assert "collision_event" in csv_text

