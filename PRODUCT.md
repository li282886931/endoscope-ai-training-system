# Product

<!-- impeccable:product-schema 1 -->

## Platform

adaptive

## Stack

Python 3.10+, PySide6 desktop UI, FastAPI local REST API, SQLite, Pydantic, PyYAML, NumPy, optional OpenCV/ONNX/YOLO adapters.

## Users

Primary users are endoscope training students, instructors, examiners, and local system administrators in a clinical training classroom using a single-lens endoscope and a high-fidelity trachea model.

## Product Purpose

The product supports real-time endoscope operation training and examination. It visualizes operation state, standard path progress, branch location, collision warning, event history, and quantitative scoring.

## Positioning

This system is a pure-vision training tool. It does not depend on extra sensors, and it keeps algorithm engines replaceable so real segmentation, depth, YOLO, and future diagnostic adapters can be introduced without rewriting business workflows.

## Operating Context

The first runnable version is a single-machine application. It must work without real endoscope hardware or trained model weights by using deterministic mock analysis, while preserving the data structures and API contracts from the detailed design.

## Capabilities and Constraints

- Train, exam, and replay workflows are first-class.
- SQLite stores sessions, trajectories, collision events, path deviations, standard paths, and scores.
- REST APIs expose session query/export, path management, model listing, and geometry calibration.
- Real-time performance targets and clinical accuracy require later validation with hardware, labeled data, and model weights.
- Generated hard data must not be fabricated; absent model or hardware evidence must remain explicit.

## Evidence on Hand

- Feishu detailed design: `https://bytedance.larkoffice.com/wiki/HFrsweYbqiC7nGkOlSHcUTDMnNf`
- No real endoscope stream, trained model weights, clinical benchmark data, or visual brand assets are available in this project.

## Product Principles

- Keep the operator workflow dense and direct.
- Separate algorithm adapters from business, storage, API, and UI.
- Preserve human verification around AI-generated or model-derived evidence.
- Make local demos deterministic before hardware integration.

