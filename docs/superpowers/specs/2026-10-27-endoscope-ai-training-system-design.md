# Endoscope AI Training System Design

## Goal

Build a single-machine runnable implementation of the endoscope AI-assisted training system described in the Feishu design document. The first version must run without real endoscope hardware or trained model weights, while preserving clean extension points for OpenCV capture, ONNX segmentation/depth models, YOLO detectors, PySide6 desktop UI, FastAPI REST APIs, and SQLite storage.

## Scope

The first delivery includes:

- A Python 3.10+ project under `/Users/bytedance/endoscope-ai-training-system`.
- Configuration loading from YAML with typed validation.
- Core domain models for sessions, trajectories, collision events, standard paths, trachea trees, and score reports.
- SQLite storage matching the detailed design DDL.
- Deterministic algorithm modules for preprocessing-independent scoring, path comparison, collision classification, and simulated frame analysis.
- FastAPI endpoints for session listing/detail/export, path listing/upsert, model listing, and geometry calibration.
- PySide6 desktop shell with Train, Exam, and Replay tabs. It should remain importable when PySide6 is not installed and show a clear dependency error at launch time.
- Tests for config, scoring, collision classification, path comparison, SQLite storage, and REST API behavior.

Out of scope for the first delivery:

- Training DeepLabV3+/MiDaS/YOLO models.
- Bundling real model weights.
- Real endoscope device validation.
- Meeting the production 30 FPS / 100 ms latency target on this workstation.

## Architecture

The project is a modular single-machine Python application:

- `core`: pure domain and algorithm logic with no UI dependency.
- `storage`: SQLite persistence and export.
- `api`: FastAPI app factory and REST routes.
- `ui`: PySide6 desktop app that uses the same core and storage modules.
- `app`: command-line entry points.

The default runtime uses deterministic mock analysis so a developer can run and test the workflow before hardware and model weights are available. Real ONNX/YOLO adapters can later replace mock components without changing business, storage, or UI code.

## Data Flow

1. A training or exam session is created with user, model, path, and mode.
2. A frame analyzer emits track state, warning/collision events, and path deviation information.
3. Session records are persisted to SQLite.
4. Scoring aggregates path, collision, time, and flow metrics into a score report.
5. The REST API and desktop UI read the same session store.

## UI Shape

The desktop UI is an operating interface, not a landing page. It uses dense, professional panels:

- Left: video/analysis canvas and current overlay state.
- Right: structure tree, selected path, live metrics, and event timeline.
- Tabs: Train, Exam, Replay.
- Exam mode hides guidance copy and emphasizes scoring state.

## Error Handling

- Missing optional model weights fall back to deterministic mock inference.
- Missing PySide6 raises a clear launch-time message rather than breaking package import.
- API returns 404 for unknown sessions and 400 for unsupported export formats.
- SQLite schema initializes automatically.

## Testing

Core behavior is test-first:

- Scoring formulas match the design document.
- Collision classification covers none, warning, light, and heavy contact.
- Standard path comparison detects wrong branch and progress.
- SQLite store creates, reads, scores, and exports a session.
- FastAPI routes expose the expected JSON and CSV behavior.

