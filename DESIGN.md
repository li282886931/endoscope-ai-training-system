# Design

## Surface

Desktop operating interface for endoscope AI-assisted training.

## Visual Direction

Use a restrained clinical operations style: dark inspection canvas, light control panels, high-contrast status chips, tabular numeric metrics, and concise Chinese labels. The interface should feel like a professional training console, not a marketing page.

## Layout

- Top title bar with system name and local runtime status.
- Main tabs: Training, Exam, Replay.
- Training and exam screens use a wide left analysis canvas and a compact right operations column.
- Right column contains current node, path progress, collision state, score summary, structure tree, and event timeline.
- Replay emphasizes session metadata, event list, and score detail.

## Interaction Rules

- Primary commands are direct buttons: start, stop, generate demo data, refresh.
- Exam mode hides training guidance and emphasizes objective state and scoring.
- Warnings use direct language: distance warning, light contact, heavy contact.
- Missing optional dependencies must explain the package to install.

## Components

- Video canvas placeholder that can later be replaced by OpenGL/QPainter frame rendering.
- Metric strips for score, progress, deviation, and collision strength.
- Structure tree using stable anatomical node labels.
- Event timeline with timestamp, event level, node, and frame sequence.

## Palette

- Canvas: near-black `#101820`.
- Panels: `#f6f8fb`.
- Text: `#17202a`.
- Accent: clinical teal `#007f7a`.
- Warning: amber `#b7791f`.
- Heavy collision: red `#c53030`.

