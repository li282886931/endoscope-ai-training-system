from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from .collision import CollisionConfig
from .domain import ScoreTemplate


class CaptureConfig(BaseModel):
    device: int | str = 0
    width: int = 1920
    height: int = 1080
    fps: int = 30
    backend: str = "opencv"
    calib_file: str = "calib/endoscope_001.json"


class PreprocessConfig(BaseModel):
    target_size: int = 512
    clahe_clip: float = 2.0
    clahe_tile: int = 8
    highlight_threshold: int = 245
    queue_capacity: int = 8


class YoloConfig(BaseModel):
    seg: str = "weights/yolov8s-seg.pt"
    pose: str = "weights/yolov8s-pose.pt"
    det: str = "weights/yolov8s.pt"
    conf: float = 0.45
    imgsz: int = 512


class ModelConfig(BaseModel):
    segmentation: str = "weights/deeplabv3p_resnet50.onnx"
    depth: str = "weights/dpt_hybrid_midas.onnx"
    input_size: int = 512
    yolo: YoloConfig = Field(default_factory=YoloConfig)


class TrackerConfig(BaseModel):
    orb_features: int = 1500
    kf_process_noise: float = 0.01
    kf_measure_noise: float = 0.5
    off_path_threshold_mm: float = 10.0


class DbConfig(BaseModel):
    path: str = "data/training.db"
    archive_dir: str = "data/sessions"


class AppConfig(BaseModel):
    capture: CaptureConfig = Field(default_factory=CaptureConfig)
    preprocess: PreprocessConfig = Field(default_factory=PreprocessConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    tracker: TrackerConfig = Field(default_factory=TrackerConfig)
    collision: CollisionConfig = Field(default_factory=CollisionConfig)
    scoring: ScoreTemplate = Field(default_factory=ScoreTemplate)
    db: DbConfig = Field(default_factory=DbConfig)


def load_config(path: str | Path) -> AppConfig:
    with Path(path).open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp) or {}
    return AppConfig.model_validate(data)

