SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS session (
    session_id      TEXT PRIMARY KEY,
    user_name       TEXT NOT NULL,
    model_id        TEXT NOT NULL,
    target_path_id  TEXT NOT NULL,
    mode            TEXT NOT NULL CHECK (mode IN ('train','exam')),
    start_ts        INTEGER NOT NULL,
    end_ts          INTEGER,
    duration_ms     INTEGER,
    total_score     REAL
);

CREATE TABLE IF NOT EXISTS trajectory (
    session_id    TEXT NOT NULL,
    ts            INTEGER NOT NULL,
    node_id       TEXT,
    pos_x         REAL,
    pos_y         REAL,
    pos_z         REAL,
    deviation_mm  REAL,
    frame_seq     INTEGER,
    PRIMARY KEY (session_id, ts)
);

CREATE TABLE IF NOT EXISTS collision_event (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    ts          INTEGER NOT NULL,
    level       TEXT NOT NULL CHECK (level IN ('warn','light','heavy')),
    strength    REAL,
    node_id     TEXT,
    frame_seq   INTEGER
);

CREATE TABLE IF NOT EXISTS path_deviation (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    ts          INTEGER NOT NULL,
    dev_type    TEXT NOT NULL CHECK (dev_type IN ('wrong_branch','off_path')),
    duration_ms INTEGER,
    node_id     TEXT
);

CREATE TABLE IF NOT EXISTS score (
    session_id    TEXT PRIMARY KEY,
    total         REAL,
    s_path        REAL,
    s_collision   REAL,
    s_time        REAL,
    s_flow        REAL,
    template_id   TEXT
);

CREATE TABLE IF NOT EXISTS standard_path (
    path_id            TEXT PRIMARY KEY,
    name               TEXT NOT NULL,
    model_id           TEXT NOT NULL,
    node_sequence_json TEXT NOT NULL,
    standard_time_ms   INTEGER NOT NULL,
    critical_nodes_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_traj_session ON trajectory(session_id);
CREATE INDEX IF NOT EXISTS idx_collision_session ON collision_event(session_id);
"""

