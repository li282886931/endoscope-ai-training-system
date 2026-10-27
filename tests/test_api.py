from pathlib import Path

from fastapi.testclient import TestClient

from endoscope_ai_training.api.server import create_app
from endoscope_ai_training.core.domain import SessionMeta
from endoscope_ai_training.storage.session_store import SessionStore


def test_api_lists_sessions_and_returns_detail(tmp_path: Path):
    store = SessionStore(tmp_path / "training.db")
    store.create_session(
        SessionMeta(
            session_id="S1",
            user_name="student",
            model_id="trachea_model_001",
            target_path_id="P_RUL",
            mode="train",
            start_ts=1_000,
        )
    )
    client = TestClient(create_app(store))

    listed = client.get("/api/v1/sessions").json()
    detail = client.get("/api/v1/sessions/S1").json()

    assert listed["items"][0]["session_id"] == "S1"
    assert detail["session"]["mode"] == "train"


def test_api_upserts_paths_and_calibrates_model(tmp_path: Path):
    client = TestClient(create_app(SessionStore(tmp_path / "training.db")))

    response = client.post(
        "/api/v1/paths",
        json={
            "path_id": "P_RUL",
            "name": "右肺上叶路径",
            "model_id": "trachea_model_001",
            "node_sequence": ["L0", "L1"],
            "standard_time_ms": 120000,
            "critical_nodes": ["L1"],
        },
    )
    assert response.status_code == 200
    assert client.get("/api/v1/paths").json()["items"][0]["path_id"] == "P_RUL"

    calibration = client.post(
        "/api/v1/models/calibrate",
        json={"ref_diameter_mm": 18.0, "est_diameter_px": 200.0, "focal_px": 500.0},
    ).json()
    assert calibration["scale_mm_per_px"] > 0

