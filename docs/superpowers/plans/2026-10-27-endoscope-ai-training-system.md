# Endoscope AI Training System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-machine runnable Python implementation of the endoscope AI-assisted training system with desktop UI, REST API, SQLite persistence, deterministic mock analysis, and tests.

**Architecture:** Keep core algorithms independent from UI and API. Use SQLite as the shared persistence layer. Make model and hardware adapters replaceable while defaulting to deterministic local behavior.

**Tech Stack:** Python 3.10+, FastAPI, SQLite, Pydantic, PyYAML, NumPy, OpenCV optional, PySide6 optional, pytest.

---

### Task 1: Project Skeleton And Tests

**Files:**
- Create: `pyproject.toml`
- Create: `README.md`
- Create: `configs/default.yaml`
- Create: `src/endoscope_ai_training/__init__.py`
- Create: `tests/test_scoring.py`
- Create: `tests/test_collision.py`
- Create: `tests/test_pathing.py`
- Create: `tests/test_store.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write failing tests**

Create tests for score formulas, collision levels, standard path comparison, SQLite persistence/export, and API route behavior.

- [ ] **Step 2: Run tests to verify failure**

Run: `/opt/homebrew/bin/python3.11 -m pytest -q`

Expected: tests fail because package modules are not implemented.

### Task 2: Core Domain And Algorithms

**Files:**
- Create: `src/endoscope_ai_training/core/domain.py`
- Create: `src/endoscope_ai_training/core/scoring.py`
- Create: `src/endoscope_ai_training/core/collision.py`
- Create: `src/endoscope_ai_training/core/pathing.py`
- Create: `src/endoscope_ai_training/core/config.py`

- [ ] **Step 1: Implement domain dataclasses and config models**

Define explicit models for trachea tree, standard path, track state, collision event, session metadata, session record, and score report.

- [ ] **Step 2: Implement scoring, collision, and pathing**

Implement formulas and thresholds from the Feishu document with configurable defaults.

- [ ] **Step 3: Run focused tests**

Run: `/opt/homebrew/bin/python3.11 -m pytest tests/test_scoring.py tests/test_collision.py tests/test_pathing.py -q`

Expected: PASS.

### Task 3: SQLite Store And API

**Files:**
- Create: `src/endoscope_ai_training/storage/schema.py`
- Create: `src/endoscope_ai_training/storage/session_store.py`
- Create: `src/endoscope_ai_training/api/server.py`

- [ ] **Step 1: Implement SQLite schema and store**

Create tables from the detailed design and expose session, trajectory, collision, score, detail query, and export methods.

- [ ] **Step 2: Implement FastAPI app factory**

Expose `/api/v1/sessions`, `/api/v1/sessions/{id}`, `/api/v1/sessions/{id}/export`, `/api/v1/paths`, `/api/v1/models`, and `/api/v1/models/calibrate`.

- [ ] **Step 3: Run storage and API tests**

Run: `/opt/homebrew/bin/python3.11 -m pytest tests/test_store.py tests/test_api.py -q`

Expected: PASS.

### Task 4: Desktop UI And Entrypoints

**Files:**
- Create: `src/endoscope_ai_training/ui/main_window.py`
- Create: `src/endoscope_ai_training/app/cli.py`

- [ ] **Step 1: Implement PySide6 UI shell**

Create Train, Exam, and Replay tabs with live metrics, structure tree, event timeline, and clear launch-time missing dependency behavior.

- [ ] **Step 2: Implement CLI**

Expose `endoscope-training-api`, `endoscope-training-ui`, and `endoscope-training-demo-data`.

- [ ] **Step 3: Run full tests**

Run: `/opt/homebrew/bin/python3.11 -m pytest -q`

Expected: PASS.

