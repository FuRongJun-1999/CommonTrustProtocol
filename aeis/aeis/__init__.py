# -*- coding: utf-8 -*-
"""
aeis · 灵枢 — Agent Engineering Implementation Specification
==============================================================
智能体工程实现规范库：基于智能论 v3.2 协议框架的持久记忆与认知引擎。

其他智能体通过本包接入协议框架：
  import aeis
  agent = aeis.Agent()                     # 高层接口（api.py）
  agent.remember("...")                    # 写入记忆
  agent.recall("...")                      # 检索记忆
  agent.distill()                          # 知识飞轮蒸馏
  agent.calibrate()                        # 宇宙校准参照

核心（core.py）：时空记忆引擎 v1.12（五层记忆 · 信息差 · 信任值 · 生命周期 · 自我认知循环）
  - SpacetimeMemoryEngine  协议实例核心引擎
  - LayeredStore           五层记忆存储（锚点/结构/知识/情境/自我）
  - ConditionSpace         条件空间（观测位置/工具/时间窗口/存在约束）
  - EdgeType / MemoryLayer / Role / NodeType

组件（包内命名空间）：
  - flywheel.py   知识飞轮（蒸馏/度量/迁移测试/宇宙校准参照/图遍历）
  - self_cognition.py 自我认知循环（行为日志/反思闭环触发/情绪方向性偏好/元认知校准/学习回写）
  - semantic.py   语义空间（语义坐标 · 中文象形语义投影）
  - attention.py  注意力策略（决策偏好）
  - prediction.py 预测引擎（因果路线 · 盲区驱动）
  - lifecycle.py  生命周期自动机（七相工程映射）
  - blindspot.py  盲区学习闭环
  - cognition.py  认知编排
  - entities.py   实体注册表

设计约束（D-005）：纯标准库 · 零外部依赖。
版本：v0.2.0（引擎基线 v1.12.0 · SELF-COGNITION-REV2）
协议：智能论 v3.2 —— 保留所有权利。
"""

import sys as _sys

# ---------------------------------------------------------------------------
# 命名空间注册：引擎内部惰性导入（from <old_name> import ...）通过
# sys.modules 别名命中包内模块 —— 保持与生产引擎逐字节一致，零代码改动。
# ---------------------------------------------------------------------------
from . import core as _core
_sys.modules["spacetime_memory_core"] = _core

from . import flywheel as _flywheel
_sys.modules["flywheel_engine"] = _flywheel

from . import semantic as _semantic
_sys.modules["semantic_space"] = _semantic

from . import attention as _attention
_sys.modules["attention_policy"] = _attention

from . import prediction as _prediction
_sys.modules["prediction_engine"] = _prediction

from . import lifecycle as _lifecycle
_sys.modules["lifecycle_engine"] = _lifecycle

from . import blindspot as _blindspot
_sys.modules["blindspot_learning_loop"] = _blindspot

from . import cognition as _cognition
_sys.modules["cognitive_orchestrator"] = _cognition

from . import entities as _entities
_sys.modules["entity_registry"] = _entities

from . import self_cognition as _self_cognition
_sys.modules["self_cognition_engine"] = _self_cognition

from . import vision as _vision
_sys.modules["vision"] = _vision

from . import knowledge as _knowledge
_sys.modules["knowledge"] = _knowledge

from . import body as _body
_sys.modules["body"] = _body

from . import api as _api
from .api import Agent

# ---------------------------------------------------------------------------
# 公共 API 导出
# ---------------------------------------------------------------------------
from .core import (
    SpacetimeMemoryEngine, LayeredStore, ConditionSpace,
    STNode, STEdge, SelfModel,
    EdgeType, MemoryLayer, Role, NodeType,
)
from .flywheel import FlywheelEngine
from .semantic import SemanticSpaceProvider
from .attention import AttentionPolicy
from .prediction import PredictionEngine
from .lifecycle import LifecycleEngine
from .blindspot import BlindSpotLearningLoop
from .cognition import CognitiveOrchestrator
from .entities import EntityRegistry
from .self_cognition import SelfCognitionEngine
from .vision import VisionProvider, YOLOVisionProvider, NullVisionProvider, create_vision_provider
from .knowledge import ingest_text, ingest_file, ingest_url

__version__ = "0.3.1"
ENGINE_VERSION = "v1.13.0"
PROTOCOL = "智能论 v3.2"
DISTILL_STANDARD_VERSION = _flywheel.FlywheelEngine.DISTILL_STANDARD_VERSION

__all__ = [
    "Agent",
    "SpacetimeMemoryEngine", "LayeredStore", "ConditionSpace",
    "STNode", "STEdge", "SelfModel",
    "EdgeType", "MemoryLayer", "Role", "NodeType",
    "FlywheelEngine", "SemanticSpaceProvider", "AttentionPolicy",
    "PredictionEngine", "LifecycleEngine", "BlindSpotLearningLoop",
    "CognitiveOrchestrator", "EntityRegistry", "SelfCognitionEngine",
    "VisionProvider", "YOLOVisionProvider", "NullVisionProvider", "create_vision_provider",
    "ingest_text", "ingest_file", "ingest_url",
    "__version__", "ENGINE_VERSION", "PROTOCOL", "DISTILL_STANDARD_VERSION",
]
