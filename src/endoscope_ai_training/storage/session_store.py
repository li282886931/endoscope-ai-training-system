from __future__ import annotations

import csv
import io
import json
import sqlite3
from threading import RLock
from dataclasses import asdict
from pathlib import Path
from typing import Any

from endoscope_ai_training.core.domain import CollisionEvent, ScoreReport, SessionMeta, StandardPath, TrajectoryPoint

from .schema import SCHEMA_SQL


class SessionStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock:
            self.conn.executescript(SCHEMA_SQL)
            self.conn.commit()

    def create_session(self, session: SessionMeta) -> str:
        with self._lock:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO session
                (session_id, user_name, model_id, target_path_id, mode, start_ts, end_ts, duration_ms, total_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.user_name,
                    session.model_id,
                    session.target_path_id,
                    session.mode,
                    session.start_ts,
                    session.end_ts,
                    session.duration_ms,
                    session.total_score,
                ),
            )
            self.conn.commit()
        return session.session_id

    def list_sessions(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self.conn.execute("SELECT * FROM session ORDER BY start_ts DESC").fetchall()
        return [dict(row) for row in rows]

    def append_trajectory(self, session_id: str, points: list[TrajectoryPoint]) -> None:
        with self._lock:
            self.conn.executemany(
                """
                INSERT OR REPLACE INTO trajectory
                (session_id, ts, node_id, pos_x, pos_y, pos_z, deviation_mm, frame_seq)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        session_id,
                        point.ts,
                        point.node_id,
                        point.pos_mm[0],
                        point.pos_mm[1],
                        point.pos_mm[2],
                        point.deviation_mm,
                        point.frame_seq,
                    )
                    for point in points
                ],
            )
            self.conn.commit()

    def append_collision(self, session_id: str, event: CollisionEvent) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT INTO collision_event (session_id, ts, level, strength, node_id, frame_seq)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session_id, event.ts, event.level, event.strength, event.node_id, event.frame_seq),
            )
            self.conn.commit()

    def save_score(self, session_id: str, report: ScoreReport) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO score (session_id, total, s_path, s_collision, s_time, s_flow, template_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    report.total,
                    report.s_path,
                    report.s_collision,
                    report.s_time,
                    report.s_flow,
                    report.template_id,
                ),
            )
            self.conn.execute("UPDATE session SET total_score = ? WHERE session_id = ?", (report.total, session_id))
            self.conn.commit()

    def query_session(self, session_id: str) -> dict[str, Any]:
        with self._lock:
            session = self.conn.execute("SELECT * FROM session WHERE session_id = ?", (session_id,)).fetchone()
            if session is None:
                raise KeyError(session_id)
            trajectory = self.conn.execute(
                "SELECT ts, node_id, pos_x, pos_y, pos_z, deviation_mm, frame_seq FROM trajectory WHERE session_id = ? ORDER BY ts",
                (session_id,),
            ).fetchall()
            collisions = self.conn.execute(
                "SELECT ts, level, strength, node_id, frame_seq FROM collision_event WHERE session_id = ? ORDER BY ts",
                (session_id,),
            ).fetchall()
            score = self.conn.execute("SELECT * FROM score WHERE session_id = ?", (session_id,)).fetchone()
        return {
            "session": dict(session),
            "trajectory": [dict(row) for row in trajectory],
            "collisions": [dict(row) for row in collisions],
            "score": dict(score) if score else None,
        }

    def export_csv(self, session_id: str) -> str:
        detail = self.query_session(session_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["section", "field", "value"])
        for key, value in detail["session"].items():
            writer.writerow(["session", key, value])
        writer.writerow([])
        writer.writerow(["trajectory", "ts", "node_id", "pos_x", "pos_y", "pos_z", "deviation_mm", "frame_seq"])
        for row in detail["trajectory"]:
            writer.writerow(["trajectory", row["ts"], row["node_id"], row["pos_x"], row["pos_y"], row["pos_z"], row["deviation_mm"], row["frame_seq"]])
        writer.writerow([])
        writer.writerow(["collision_event", "ts", "level", "strength", "node_id", "frame_seq"])
        for row in detail["collisions"]:
            writer.writerow(["collision_event", row["ts"], row["level"], row["strength"], row["node_id"], row["frame_seq"]])
        return output.getvalue()

    def upsert_path(self, path: StandardPath) -> None:
        with self._lock:
            self.conn.execute(
                """
                INSERT OR REPLACE INTO standard_path
                (path_id, name, model_id, node_sequence_json, standard_time_ms, critical_nodes_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    path.path_id,
                    path.name,
                    path.model_id,
                    json.dumps(path.node_sequence, ensure_ascii=False),
                    path.standard_time_ms,
                    json.dumps(path.critical_nodes, ensure_ascii=False),
                ),
            )
            self.conn.commit()

    def list_paths(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self.conn.execute("SELECT * FROM standard_path ORDER BY path_id").fetchall()
        return [
            StandardPath(
                path_id=row["path_id"],
                name=row["name"],
                model_id=row["model_id"],
                node_sequence=json.loads(row["node_sequence_json"]),
                standard_time_ms=row["standard_time_ms"],
                critical_nodes=json.loads(row["critical_nodes_json"]),
            ).to_dict()
            for row in rows
        ]

    def close(self) -> None:
        with self._lock:
            self.conn.close()


def row_to_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return dict(value)
