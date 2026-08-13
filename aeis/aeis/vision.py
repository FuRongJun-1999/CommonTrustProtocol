#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.vision · 视觉感知模块（第 1 项：外接 YOLO）
=================================================
- VisionProvider 接口（duck-typed · 核心零依赖 D-005）
- YOLOVisionProvider：ultralytics YOLOv8 实现（可选扩展，缺失时优雅降级）
- 视觉感知 → 记忆（modality="image" 节点写入知识层 · 与 add_perception 复用）
- 身体能力声明（available() → 纳入 body_capabilities，第 4 项铺垫）

安装（可选扩展）：pip install ultralytics -i https://mirrors.aliyun.com/pypi/simple/
权重：yolov8n.pt（首次自动下载，~6MB）
"""

import os
import time
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# 检测结果结构
# ---------------------------------------------------------------------------


class Detection:
    """单目标检测结果"""

    def __init__(self, label: str, confidence: float, bbox: List[float]):
        self.label = label
        self.confidence = confidence
        self.bbox = bbox  # [x1, y1, x2, y2]

    def to_dict(self) -> Dict:
        return {"label": self.label, "confidence": round(self.confidence, 3),
                "bbox": [round(b, 1) for b in self.bbox]}

    def __repr__(self):
        return f"Detection({self.label}, {self.confidence:.2f})"


# ---------------------------------------------------------------------------
# 提供者接口
# ---------------------------------------------------------------------------


class VisionProvider:
    """视觉提供者接口：detect(image_path) -> List[Detection]"""

    name = "base"

    def available(self) -> bool:
        """身体能力声明（第 4 项 body_capabilities 输入）"""
        return False

    def detect(self, image_path: str, conf_threshold: float = 0.35) -> List[Detection]:
        raise NotImplementedError


class NullVisionProvider(VisionProvider):
    """降级提供者：无视觉依赖时的空实现（核心保持零依赖）"""

    name = "null"

    def available(self) -> bool:
        return False

    def detect(self, image_path: str, conf_threshold: float = 0.35) -> List[Detection]:
        return []


class YOLOVisionProvider(VisionProvider):
    """YOLOv8 提供者（ultralytics 可选扩展）"""

    name = "yolov8"

    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model_path = model_path
        self._model = None
        self._load_error: Optional[str] = None
        self._load()

    def _load(self):
        try:
            from ultralytics import YOLO  # 可选依赖（D-005：核心不依赖）
            self._model = YOLO(self.model_path)
        except Exception as e:
            self._load_error = f"{type(e).__name__}: {e}"
            self._model = None

    def available(self) -> bool:
        return self._model is not None

    def detect(self, image_path: str, conf_threshold: float = 0.35) -> List[Detection]:
        """目标检测：image_path → List[Detection]"""
        if self._model is None:
            return []
        if not os.path.exists(image_path):
            return []
        results = self._model(image_path, conf=conf_threshold, verbose=False)
        detections = []
        for r in results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                label = r.names[int(box.cls)]
                conf = float(box.conf)
                bbox = [float(v) for v in box.xyxy[0]]
                detections.append(Detection(label, conf, bbox))
        return detections


# ---------------------------------------------------------------------------
# 工厂
# ---------------------------------------------------------------------------


def create_vision_provider(model_path: str = "yolov8n.pt") -> VisionProvider:
    """创建视觉提供者：ultralytics 可用 → YOLO；否则 → Null（降级）"""
    provider = YOLOVisionProvider(model_path)
    if provider.available():
        return provider
    return NullVisionProvider()


# ---------------------------------------------------------------------------
# 视觉感知 → 记忆（与引擎集成辅助）
# ---------------------------------------------------------------------------


def perceive_image(engine, image_path: str, provider: Optional[VisionProvider] = None,
                   conf_threshold: float = 0.35, importance: float = 0.6) -> Dict:
    """视觉感知闭环：检测 → 摘要文本 → 写入知识层（modality="image"）。
    返回 {status, detections, node} —— 视觉输入成为可检索记忆。"""
    prov = provider or getattr(engine, "_vision_provider", None)
    if prov is None or not prov.available():
        return {"status": "vision_unavailable",
                "note": "视觉提供者未装配（pip install ultralytics）"}
    detections = prov.detect(image_path, conf_threshold)
    if not detections:
        return {"status": "no_detection", "detections": []}
    summary = "；".join(f"{d.label}({d.confidence:.2f})" for d in detections[:10])
    content = f"[视觉感知] {os.path.basename(image_path)} 检测到: {summary}"
    node = engine.add_perception(content, modality="image", importance=importance,
                                 tags=["vision", "perception"],
                                 entities=[d.label for d in detections[:8]] or None)
    return {"status": "ok", "detections": [d.to_dict() for d in detections],
            "node_id": node.id, "summary": content}
