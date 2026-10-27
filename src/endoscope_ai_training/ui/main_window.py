from __future__ import annotations

from pathlib import Path

from endoscope_ai_training.core.domain import CollisionEvent, ScoreReport, SessionMeta, StandardPath, TrajectoryPoint
from endoscope_ai_training.storage.session_store import SessionStore


def launch(db_path: str | Path = "data/training.db") -> int:
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QApplication,
            QFrame,
            QGridLayout,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QPushButton,
            QTabWidget,
            QTreeWidget,
            QTreeWidgetItem,
            QVBoxLayout,
            QWidget,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError("PySide6 is not installed. Run: pip install -e '.[desktop]'") from exc

    class MainWindow(QMainWindow):
        def __init__(self, store: SessionStore):
            super().__init__()
            self.store = store
            self.setWindowTitle("内窥镜AI辅助训练系统")
            self.resize(1280, 820)
            self.setStyleSheet(STYLE)

            root = QWidget()
            layout = QVBoxLayout(root)
            header = QLabel("内窥镜AI辅助训练系统  |  单机训练控制台")
            header.setObjectName("Header")
            layout.addWidget(header)

            tabs = QTabWidget()
            tabs.addTab(self._operate_tab(exam=False), "训练")
            tabs.addTab(self._operate_tab(exam=True), "考核")
            tabs.addTab(self._replay_tab(), "复盘")
            layout.addWidget(tabs)
            self.setCentralWidget(root)

        def _operate_tab(self, exam: bool) -> QWidget:
            page = QWidget()
            layout = QHBoxLayout(page)

            canvas = QFrame()
            canvas.setObjectName("Canvas")
            canvas_layout = QVBoxLayout(canvas)
            title = QLabel("实时内镜画面 / AI叠加层")
            title.setObjectName("CanvasTitle")
            subtitle = QLabel("等待视频流接入。当前版本使用确定性模拟分析，真实 OpenCV/ONNX/YOLO 适配器可替换。")
            subtitle.setWordWrap(True)
            subtitle.setObjectName("CanvasSub")
            canvas_layout.addStretch(1)
            canvas_layout.addWidget(title, alignment=Qt.AlignCenter)
            canvas_layout.addWidget(subtitle, alignment=Qt.AlignCenter)
            canvas_layout.addStretch(1)
            layout.addWidget(canvas, 3)

            side = QWidget()
            side_layout = QVBoxLayout(side)
            actions = QHBoxLayout()
            start = QPushButton("开始考核" if exam else "开始训练")
            stop = QPushButton("结束")
            demo = QPushButton("生成样例")
            demo.clicked.connect(self._create_demo)
            actions.addWidget(start)
            actions.addWidget(stop)
            actions.addWidget(demo)
            side_layout.addLayout(actions)

            metrics = QGridLayout()
            metric_values = [
                ("当前节点", "L1_trachea"),
                ("路径进度", "42%"),
                ("偏离距离", "5.2 mm"),
                ("碰壁状态", "正常" if not exam else "记录中"),
                ("当前评分", "--" if not exam else "待生成"),
                ("模式", "考核" if exam else "训练"),
            ]
            for idx, (name, value) in enumerate(metric_values):
                label = QLabel(name)
                label.setObjectName("MetricLabel")
                val = QLabel(value)
                val.setObjectName("MetricValue")
                metrics.addWidget(label, idx, 0)
                metrics.addWidget(val, idx, 1)
            side_layout.addLayout(metrics)

            tree = QTreeWidget()
            tree.setHeaderLabels(["气管结构"])
            root = QTreeWidgetItem(["L0 声门"])
            trachea = QTreeWidgetItem(["L1 气管"])
            right = QTreeWidgetItem(["L2 右主支气管"])
            right.addChildren([QTreeWidgetItem(["L3 右上叶"]), QTreeWidgetItem(["L3 右中叶"]), QTreeWidgetItem(["L3 右下叶"])])
            trachea.addChildren([QTreeWidgetItem(["L2 左主支气管"]), right])
            root.addChild(trachea)
            tree.addTopLevelItem(root)
            tree.expandAll()
            side_layout.addWidget(tree)

            timeline = QLabel("事件时间轴\n00:00 正常追踪\n00:12 分叉识别\n00:28 距离预警")
            timeline.setObjectName("Timeline")
            timeline.setWordWrap(True)
            side_layout.addWidget(timeline)
            layout.addWidget(side, 1)
            return page

        def _replay_tab(self) -> QWidget:
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.addWidget(QLabel("复盘回放"))
            latest = self.store.list_sessions()[:5]
            if not latest:
                layout.addWidget(QLabel("暂无会话。点击训练/考核页的“生成样例”创建本地数据。"))
                return page
            for item in latest:
                layout.addWidget(QLabel(f"{item['session_id']} | {item['user_name']} | {item['mode']} | score={item['total_score']}"))
            return page

        def _create_demo(self) -> None:
            create_demo_dataset(self.store)

    app = QApplication([])
    window = MainWindow(SessionStore(db_path))
    window.show()
    return app.exec()


def create_demo_dataset(store: SessionStore) -> str:
    path = StandardPath(
        path_id="P_RUL",
        name="右肺上叶路径",
        model_id="trachea_model_001",
        node_sequence=["L0_glottis", "L1_trachea", "L2_right_main", "L3_upper_right"],
        standard_time_ms=120_000,
        critical_nodes=["L1_trachea", "L2_right_main"],
    )
    store.upsert_path(path)
    session_id = "S_DEMO_001"
    store.create_session(
        SessionMeta(
            session_id=session_id,
            user_name="demo_student",
            model_id="trachea_model_001",
            target_path_id="P_RUL",
            mode="exam",
            start_ts=1_710_000_000_000,
            end_ts=1_710_000_120_000,
            duration_ms=120_000,
        )
    )
    store.append_trajectory(
        session_id,
        [
            TrajectoryPoint(ts=1_710_000_001_000, node_id="L1_trachea", pos_mm=(0.0, 0.0, 12.0), deviation_mm=2.0, frame_seq=1),
            TrajectoryPoint(ts=1_710_000_050_000, node_id="L2_right_main", pos_mm=(4.0, 8.0, 38.0), deviation_mm=5.2, frame_seq=900),
        ],
    )
    store.append_collision(session_id, CollisionEvent(ts=1_710_000_072_000, level="light", strength=32, node_id="L2_right_main", frame_seq=1234))
    store.save_score(session_id, ScoreReport(total=86.5, s_path=90.0, s_collision=82.0, s_time=88.0, s_flow=85.0, issues=[]))
    return session_id


STYLE = """
QWidget {
    background: #f6f8fb;
    color: #17202a;
    font-size: 14px;
}
#Header {
    background: #101820;
    color: #ffffff;
    font-size: 20px;
    font-weight: 700;
    padding: 14px 18px;
}
#Canvas {
    background: #101820;
    border-radius: 4px;
}
#CanvasTitle {
    background: transparent;
    color: #ffffff;
    font-size: 28px;
    font-weight: 700;
}
#CanvasSub {
    background: transparent;
    color: #b8c7d9;
    max-width: 620px;
}
#MetricLabel {
    color: #5d6b7a;
    padding: 6px 0;
}
#MetricValue {
    color: #007f7a;
    font-weight: 700;
    padding: 6px 0;
}
#Timeline {
    background: #ffffff;
    border: 1px solid #d8e0e8;
    border-radius: 4px;
    padding: 12px;
}
QPushButton {
    background: #007f7a;
    color: #ffffff;
    border: none;
    border-radius: 4px;
    padding: 8px 12px;
    font-weight: 700;
}
QPushButton:hover {
    background: #006763;
}
QTreeWidget {
    background: #ffffff;
    border: 1px solid #d8e0e8;
    border-radius: 4px;
}
"""

