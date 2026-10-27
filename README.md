# Endoscope AI Training System

单机可运行版内窥镜 AI 辅助训练系统，按飞书《内窥镜AI辅助训练系统详细设计》实现第一版工程骨架。

## 能力范围

- FastAPI REST API：会话查询、会话详情、导出、标准路径、模型与几何校准。
- SQLite 数据存储：训练会话、轨迹、碰壁事件、路径偏离、评分。
- 核心算法接口：碰壁分级、路径比对、量化评分。
- PySide6 桌面端：训练、考核、复盘三页签。
- 无真实模型权重时默认使用确定性规则/模拟数据，便于本地演示和测试。

## 快速开始

```bash
cd /Users/bytedance/endoscope-ai-training-system
/opt/homebrew/bin/python3.11 -m venv .venv
. .venv/bin/activate
pip install -e ".[test]"
pytest -q
endoscope-training-demo-data
endoscope-training-api
```

桌面端需要额外安装：

```bash
pip install -e ".[desktop]"
endoscope-training-ui
```

桌面依赖使用 `PySide6-Essentials`，避免拉取当前界面不需要的 WebEngine/Addons 大包。

## 说明

真实内窥镜采集、ONNX 分割/深度估计、YOLO 检测与 PySide6 实时画面叠加已保留工程边界。本版重点保证业务闭环、接口、数据结构和评分规则可运行、可测试、可替换。
