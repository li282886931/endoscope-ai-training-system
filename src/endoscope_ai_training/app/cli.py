from __future__ import annotations

from pathlib import Path

import uvicorn

from endoscope_ai_training.api.server import create_app
from endoscope_ai_training.storage.session_store import SessionStore
from endoscope_ai_training.ui.main_window import create_demo_dataset, launch


DEFAULT_DB = Path("data/training.db")


def run_api() -> None:
    app = create_app(SessionStore(DEFAULT_DB))
    uvicorn.run(app, host="127.0.0.1", port=8000)


def run_ui() -> None:
    raise SystemExit(launch(DEFAULT_DB))


def create_demo_data() -> None:
    session_id = create_demo_dataset(SessionStore(DEFAULT_DB))
    print(f"created demo session: {session_id}")

