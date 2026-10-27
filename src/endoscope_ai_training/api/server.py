from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

from endoscope_ai_training.core.domain import StandardPath
from endoscope_ai_training.core.pathing import calibrate_scale
from endoscope_ai_training.storage.session_store import SessionStore


class CalibrationRequest(BaseModel):
    ref_diameter_mm: float
    est_diameter_px: float
    focal_px: float


def create_app(store: SessionStore | None = None) -> FastAPI:
    app = FastAPI(title="Endoscope AI Training System", version="0.1.0")
    app.state.store = store or SessionStore(Path("data/training.db"))

    @app.get("/api/v1/sessions")
    def list_sessions() -> dict[str, Any]:
        return {"items": app.state.store.list_sessions()}

    @app.get("/api/v1/sessions/{session_id}")
    def get_session(session_id: str) -> dict[str, Any]:
        try:
            return app.state.store.query_session(session_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"session not found: {session_id}") from exc

    @app.get("/api/v1/sessions/{session_id}/export")
    def export_session(session_id: str, fmt: str = "csv") -> Response:
        try:
            if fmt == "json":
                return Response(content=_json_dumps(app.state.store.query_session(session_id)), media_type="application/json")
            if fmt == "csv":
                return Response(content=app.state.store.export_csv(session_id), media_type="text/csv")
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"session not found: {session_id}") from exc
        raise HTTPException(status_code=400, detail="fmt must be csv or json")

    @app.get("/api/v1/paths")
    def list_paths() -> dict[str, Any]:
        return {"items": app.state.store.list_paths()}

    @app.post("/api/v1/paths")
    def upsert_path(path: StandardPath) -> dict[str, Any]:
        app.state.store.upsert_path(path)
        return {"ok": True, "path": path.to_dict()}

    @app.get("/api/v1/models")
    def list_models() -> dict[str, Any]:
        return {
            "items": [
                {
                    "model_id": "trachea_model_001",
                    "version": "1.0",
                    "status": "mock-ready",
                    "description": "Default single-machine demo trachea model.",
                }
            ]
        }

    @app.post("/api/v1/models/calibrate")
    def calibrate_model(req: CalibrationRequest) -> dict[str, float]:
        return {"scale_mm_per_px": calibrate_scale(req.ref_diameter_mm, req.est_diameter_px, req.focal_px)}

    return app


def _json_dumps(data: Any) -> str:
    import json

    return json.dumps(data, ensure_ascii=False)

