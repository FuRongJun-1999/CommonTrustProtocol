# -*- coding: utf-8 -*-
"""
aeis.mcp.server · 灵枢 MCP server — 供其他智能体通过 MCP 协议调用
================================================================
零外部依赖实现（D-005）：stdio 传输 + JSON-RPC 2.0（换行分隔）。
其他智能体（ZCode / Claude / 自研 Agent）通过 MCP 客户端接入后，
可直接调用记忆/认知/飞轮工具，无需编写代码。

传输协议：
  - 每行一个 JSON 消息（UTF-8）
  - 初始化序列：initialize → notifications/initialized → tools/list → tools/call

启动：
  python -m aeis.mcp.server            # 或安装后: aeis-mcp
  AEIS_DB=memory.db AEIS_IDENTITY=助手 aeis-mcp   # 持久化配置

工具面（18 项）：记忆（remember/recall/search/timeline）· 关系（relate/reason/
predict_routes）· 认知（blindspots/learn/induce）· 飞轮（distill/flywheel_metrics/
transfer_test/calibrate）· 生命周期（lifecycle_step）· 元认知（self_check/gap_trend/export）
"""

import json
import os
import sys

from ..api import Agent
from ..core import STNode, STEdge, ConditionSpace

SERVER_NAME = "aeis-mcp"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2024-11-05"


# ---------------------------------------------------------------------------
# 序列化（节点/边/枚举 → JSON 安全结构）
# ---------------------------------------------------------------------------

def _serialize(obj):
    if isinstance(obj, STNode):
        return {
            "id": obj.id, "content": obj.content, "modality": obj.modality,
            "importance": obj.importance, "confidence": obj.confidence,
            "layer": getattr(obj.layer, "value", str(obj.layer)),
            "tags": list(obj.tags),
            "access_count": obj.access_count,
            "last_access": obj.last_access, "created_at": obj.created_at,
            "entity_id": obj.entity_id,
            "condition_space": json.loads(obj.condition_space.to_json())
            if obj.condition_space else None,
        }
    if isinstance(obj, STEdge):
        return {
            "id": obj.id, "source_id": obj.source_id, "target_id": obj.target_id,
            "relation_type": getattr(obj.relation_type, "value", str(obj.relation_type)),
            "confidence": obj.confidence, "weight": obj.weight,
            "verified": bool(obj.verified),
            "created_at": obj.created_at, "last_verified": obj.last_verified,
            "source_evidence": obj.source_evidence,
        }
    if isinstance(obj, ConditionSpace):
        return json.loads(obj.to_json())
    if isinstance(obj, (list, tuple)):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {str(k): _serialize(v) for k, v in obj.items()}
    return obj


def _dump(obj) -> str:
    return json.dumps(_serialize(obj), ensure_ascii=False, default=str)


# ---------------------------------------------------------------------------
# 工具注册表
# ---------------------------------------------------------------------------

def _tools():
    return [
        {"name": "remember",
         "description": "写入一条感知记忆（知识层，自动去重）。content 必填；importance 重要性[0,1]；tags 标签；entities 实体名列表。",
         "inputSchema": {"type": "object",
                         "properties": {"content": {"type": "string"},
                                        "importance": {"type": "number"},
                                        "tags": {"type": "array", "items": {"type": "string"}},
                                        "entities": {"type": "array", "items": {"type": "string"}}},
                         "required": ["content"]}},
        {"name": "recall",
         "description": "组合联想召回（内容相似0.5+重要性0.3+近因0.2）。返回 [(node, score)]。",
         "inputSchema": {"type": "object",
                         "properties": {"query": {"type": "string"}, "limit": {"type": "number"}},
                         "required": ["query"]}},
        {"name": "search",
         "description": "内容检索（LIKE 预筛 + 中文二元组 Jaccard 排序），触发复用追踪。",
         "inputSchema": {"type": "object",
                         "properties": {"query": {"type": "string"}, "limit": {"type": "number"}},
                         "required": ["query"]}},
        {"name": "timeline",
         "description": "记忆时间线（按时间倒序）。",
         "inputSchema": {"type": "object",
                         "properties": {"limit": {"type": "number"}}}},
        {"name": "relate",
         "description": "在两个节点间建立关系边。relation: causal/similar/sequential/spatial/hierarchical；source_evidence: extracted/inferred/ambiguous。边默认未验证。",
         "inputSchema": {"type": "object",
                         "properties": {"source_id": {"type": "string"},
                                        "target_id": {"type": "string"},
                                        "relation": {"type": "string"},
                                        "confidence": {"type": "number"},
                                        "source_evidence": {"type": "string"}},
                         "required": ["source_id", "target_id"]}},
        {"name": "reason",
         "description": "因果推理：从起点出发的因果路径集合。",
         "inputSchema": {"type": "object",
                         "properties": {"start_id": {"type": "string"},
                                        "end_id": {"type": "string"},
                                        "max_depth": {"type": "number"}},
                         "required": ["start_id"]}},
        {"name": "predict_routes",
         "description": "生成式预测：候选未来路线集合（盲区驱动 · T_pred 对齐）。",
         "inputSchema": {"type": "object",
                         "properties": {"start_id": {"type": "string"},
                                        "horizon": {"type": "number"},
                                        "blindspot_id": {"type": "string"}}}},
        {"name": "blindspots",
         "description": "盲区注册表（D-001 语义判定：对人类文明级负面影响不写入）。",
         "inputSchema": {"type": "object",
                         "properties": {"status": {"type": "string"}}}},
        {"name": "learn",
         "description": "一轮盲区学习（可预测盲区 → 预测路线假设 → 探索 → 终态判定）。",
         "inputSchema": {"type": "object",
                         "properties": {"use_prediction": {"type": "boolean"}}}},
        {"name": "prediction_feedback",
         "description": "验证回路回填（协议 2.10 D₃ · D-006 动态校准）：预测 vs 实际结果对比 → 命中强化/未命中登记。回填累积样本使 self_reliability(P0-4)/T_pred D₃ 生效。hit 可省略（predicted==actual 自动命中）。",
         "inputSchema": {"type": "object",
                         "properties": {"predicted_node_id": {"type": "string"},
                                        "actual_node_id": {"type": "string"},
                                        "hit": {"type": "boolean"},
                                        "note": {"type": "string"}}}},
        {"name": "prediction_stats",
         "description": "预测引擎状态（routes 生成数 / hit 样本 / 命中率 / 动态阈值）。",
         "inputSchema": {"type": "object"}},
        {"name": "induce",
         "description": "归纳/知识合成：聚类生成概念节点（SIMILAR 边 · inferred 证据）。",
         "inputSchema": {"type": "object"}},
        {"name": "distill",
         "description": "知识飞轮蒸馏：经验（被拒路径 + learning_result/induced）→ 可复用模式节点。",
         "inputSchema": {"type": "object",
                         "properties": {"source_filter": {"type": "string"}}}},
        {"name": "flywheel_metrics",
         "description": "飞轮度量（知识增长率/复用率/蒸馏产出率）。工程观测值，不参与信任计算。",
         "inputSchema": {"type": "object"}},
        {"name": "transfer_test",
         "description": "迁移测试：条件空间内新实体预测成功率（2×SE 显著性；样本<20 不判定）。",
         "inputSchema": {"type": "object"}},
        {"name": "calibrate",
         "description": "宇宙校准参照（5 判据方向性检查）。元理论参照工具，非盲区33关闭依据。",
         "inputSchema": {"type": "object"}},
        {"name": "lifecycle_step",
         "description": "生命周期一步（感知→好奇→缩小信息差→信任→协作→巩固→standby）。",
         "inputSchema": {"type": "object"}},
        {"name": "lifecycle_state",
         "description": "生命周期状态（cycle / state），不执行一步。",
         "inputSchema": {"type": "object"}},
        {"name": "start_lifecycle",
         "description": "启动生命周期自发循环（后台线程 · 每 interval 秒一步自主运行：感知→好奇→缩小信息差→巩固）。中断权：维生系统>验证单元>用户>实例。",
         "inputSchema": {"type": "object",
                         "properties": {"interval": {"type": "number"}}}},
        {"name": "stop_lifecycle",
         "description": "中断生命周期自发循环（source: user/designer/verifier/vital_system）。",
         "inputSchema": {"type": "object",
                         "properties": {"source": {"type": "string"}}}},
        {"name": "self_check",
         "description": "完整性自检（孤儿边/表统计/integrity_ok）。",
         "inputSchema": {"type": "object"}},
        {"name": "gap_trend",
         "description": "信息差收敛趋势（A-4 线性回归斜率；工程定义）。",
         "inputSchema": {"type": "object",
                         "properties": {"window": {"type": "number"}}}},
        {"name": "export",
         "description": "全库导出到 JSON 文件（灾备/迁移）。返回导出统计。",
         "inputSchema": {"type": "object",
                         "properties": {"path": {"type": "string"}},
                         "required": ["path"]}},
        {"name": "service_info",
         "description": "服务信息（信任透明度）：身份/版本/协议/库状态/工具数。接入方应先调用以确认与哪个协议实例对话。",
         "inputSchema": {"type": "object"}},
        {"name": "see",
         "description": "视觉感知：目标检测 → 摘要写入知识层记忆（可检索）。YOLO-World 开放词汇：默认文生图核心词表（动物/自然/武器/食物等）；classes 可指定检测词（中/英均可，如 ['狼','moon']）。",
         "inputSchema": {"type": "object",
                         "properties": {"image_path": {"type": "string"},
                                        "conf_threshold": {"type": "number"},
                                        "importance": {"type": "number"},
                                        "classes": {"type": "array", "items": {"type": "string"}}},
                         "required": ["image_path"]}},
        {"name": "think",
         "description": "推理记忆注入（v1.13）：检索相关记忆（内容+联想+模式加权）→ 推理上下文。",
         "inputSchema": {"type": "object",
                         "properties": {"query": {"type": "string"}, "limit": {"type": "number"}},
                         "required": ["query"]}},
        {"name": "preflight",
         "description": "输出前反思（v1.13）：内容与价值观一致性检查，冲突词拦截。",
         "inputSchema": {"type": "object",
                         "properties": {"text": {"type": "string"}},
                         "required": ["text"]}},
        {"name": "ingest_text",
         "description": "外部知识摄取：文本 → 知识层（source 标签·分块·实体提取）。",
         "inputSchema": {"type": "object",
                         "properties": {"content": {"type": "string"},
                                        "source": {"type": "string"},
                                        "tags": {"type": "array", "items": {"type": "string"}}},
                         "required": ["content"]}},
        {"name": "ingest_file",
         "description": "外部知识摄取：文件（txt/md/json/代码等按扩展名处理）。",
         "inputSchema": {"type": "object",
                         "properties": {"path": {"type": "string"}},
                         "required": ["path"]}},
        {"name": "ingest_url",
         "description": "外部知识摄取：URL 页面（零依赖抓取+去标签）。",
         "inputSchema": {"type": "object",
                         "properties": {"url": {"type": "string"}},
                         "required": ["url"]}},
        {"name": "session_note",
         "description": "上下文外部化：会话要点写入灵枢（session 标签，可恢复）。",
         "inputSchema": {"type": "object",
                         "properties": {"session_id": {"type": "string"},
                                        "key_points": {"type": "array", "items": {"type": "string"}}},
                         "required": ["session_id", "key_points"]}},
        {"name": "session_recall",
         "description": "会话要点恢复：按 session 或语义检索灵枢中的会话记忆。",
         "inputSchema": {"type": "object",
                         "properties": {"session_id": {"type": "string"},
                                        "query": {"type": "string"},
                                        "limit": {"type": "number"}}}},
        {"name": "compact_context",
         "description": "上下文压缩：生成会话摘要节点（超长会话恢复入口）。",
         "inputSchema": {"type": "object",
                         "properties": {"session_id": {"type": "string"},
                                        "summary": {"type": "string"}},
                         "required": ["session_id", "summary"]}},
        {"name": "body",
         "description": "身体能力声明：感知模态（文本/图像）+ 工具 + 记忆；身体 = 自我的一部分。",
         "inputSchema": {"type": "object"}},
        {"name": "scene_simulator",
         "description": "场景级世界模拟器（里程碑2.3）：在服务器基础上添加场景/实体/自主行为玩家——create（场景）/ entity（自主实体：wander/seek/avoid/flee/follow 确定性行为）/ path（巡逻路径）/ step（决策循环：所有自主实体各自决策→行动→场景演化）/ state / log（行为可审计）。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "spacetime_consistency",
         "description": "时空一致性验证（里程碑2.4 · 阶段2收官）：持续运行 + 一致性验证闭环——create（场景）/ entity / path / run（每 tick 预测下一状态 vs 实际 → 滚动命中率跟踪）/ step（验证一步：预测 vs 实际 + 不变量校验 + 漂移检测）/ teleport（排队外部事件瞬移→演示漂移检测）/ report（自洽度报告：总体/滚动/分行为命中率 + 漂移事件 + 判定）/ self_consistent（世界模型自洽判定：持续运行中预测与实际保持一致性）/ drift（漂移事件）/ history（预测历史可审计）。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "world_model",
         "description": "统一世界模型（里程碑3.1 · HERMES 式统一架构）：世界状态表征作为理解/生成/验证共享的同一骨干——init / create（物理世界场景）/ entity / path / perceive（理解端口：观测→世界图，生成先验注入理解=预测-观测一致性异常检测）/ generate（生成端口：世界图→候选未来，顺序语义外推+不确定边界）/ verify（验证端口：外部观察者对比→命中率）/ run（持续运行：generate→物理演化→perceive→verify）/ patterns（观测-only 行为模式推断：关系/速度/方向一致性）/ anomalies（预测-观测异常事件）/ graph（世界图+观测溯源条件空间）/ history（4D 演化历史）/ state。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "world_learner",
         "description": "自监督世界学习（里程碑3.2 · V-JEPA 式）：从观测序列无标注学转移函数，学习者不接触世界内部规则（缸中之脑姿态）——init / create / entity / path / run（物理演化+观测数据采集）/ learn（自监督学习：速度/方向持续性/关系候选/可达域，白箱可审计）/ predict（学得模型预测下一状态，带不确定边界）/ evaluate（评估协议：学得 vs naive 基线 vs 真模型上界 → 认知缺口）/ curve（增量学习曲线：观测增加→命中率提升=认知缺口收紧）/ masked（遮挡重建损失）/ model（学得参数导出）/ history / state。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "curiosity_explorer",
         "description": "好奇驱动探索（里程碑3.3）：主动选择观测最大化信息增益，用最少带宽收紧认知缺口——init / create / entity / path / explore（探索 n tick：curiosity/random/round_robin 策略，budget=每 tick 观测上限）/ step（探索一步，决策日志：chosen + IG 分解=不确定×新奇×信息瓶颈×陈旧×异常）/ probe（全带宽探针：学得模型 held-out 命中率）/ compare（同世界轨迹策略对比：好奇 vs 随机 vs 轮询）/ curiosity（好奇心摘要：观测分布/不确定度趋势/异常计数）/ uncertainty（不确定度轨迹）/ model / history / state。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "seven_layer_loop",
         "description": "七层闭环（里程碑3.4 · 阶段3收官）：感知→记忆→理解→预测→验证→物理→决策 完整自主循环——init / create / entity / path / run（持续运行 n tick，每 tick 七层闭环：L1感知=好奇选定实体观测 / L2记忆=时空记忆图 / L3认知=关系与行为推断 / L4预测=学得模型候选未来 / L5验证=外部观察者对比命中率 / L6物理=世界演化 / L7决策=好奇信息增益最大化）/ step（单步七层留痕）/ report（闭环报告：七层统计 + 自增强曲线 early vs late 命中率）/ audit（审计轨迹）/ verify（L5）/ decision（L7）/ memory（L2）/ graph（L3）/ state。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "world_server",
         "description": "AI 游戏世界服务器（里程碑2.2）：AI 自身成为游戏世界的服务器——tick（多路并行模拟）/ snapshot+rollback（世界记忆与错误回滚）/ feedback（实体行动反馈）/ sync（客户端同步）/ verify（预测验证：预测下一 tick vs 实际→命中判定）。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "voxel_world",
         "description": "小型我的世界（里程碑2.1 · 4D 时空占用沙盒）：build（生成平地世界）/ spawn（动态实体）/ simulate（时空演化——实体按速度移动）/ trail（实体时空轨迹 A→B）/ state（世界状态）。为时空演化预测与世界模拟提供可控测试环境。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "world3d",
         "description": "WORLD3D-REV1 时空重建：语义 → 3D 空间与颜色（灵枢自己的文生图，确定性渲染零 LLM）。build（从记忆视觉原语重建，multiview 多视角三角化）/ render / status / add / add_view（多视角融合）/ graph（3D 语义锚点图：节点=锚点+provenance，边=关系）/ verify（多感知机锚点验证——一个事物不能只有视觉一层信息：visual/tactile/audio/action/prediction 多通道协同确认，打破视觉自证陷阱）/ verify_conflict（多通道矛盾检测→降级）。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "vprim",
         "description": "VPRIM-REV1 视觉原语查询（确定性·零 LLM，语义时空图空间锚点）：action=spatial（两 bbox [x1,y1,x2,y2] 空间关系）/ count（视觉原语计数，category 可选）/ anchors（最近锚点列表）。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["action"]}},
        {"name": "recursive_reflect",
         "description": "协议 3.12 递归验证反思 + 1.6.7 元反思（REFLECT-REV1）：元反思定标准 → 一级验证（预期vs实际）→ 二级反思（问1 隐藏前提/条件空间边界，问2 影响评估）→ 三级终裁（可逆性优先）→ 反思链归档。递归 ≤ 3 层（超出=结构性盲区）。claim 必填；expected/actual 可给一级验证输入。",
         "inputSchema": {"type": "object",
                         "properties": {"claim": {"type": "string"},
                                        "expected": {"type": "string"},
                                        "actual": {"type": "string"},
                                        "context": {"type": "string"},
                                        "depth": {"type": "number"},
                                        "max_depth": {"type": "number"}},
                         "required": ["claim"]}},
        {"name": "longterm_snapshot",
         "description": "v1.15 长期记忆写入：快照 → 重要性评估（信息差/信任/二阶变化/提及次数加权）→ 按层级写入（长期/知识/情境）+ 条件空间 + 关联边。content/source 必填；importance_hint 可显式提示重要性（≥0.7 触发不可遗忘保护）。",
         "inputSchema": {"type": "object",
                         "properties": {"content": {"type": "string"},
                                        "source": {"type": "string"},
                                        "tags": {"type": "array", "items": {"type": "string"}},
                                        "entities": {"type": "array", "items": {"type": "string"}},
                                        "importance_hint": {"type": "number"}},
                         "required": ["content"]}},
        {"name": "prefeed",
         "description": "H1 海马体前馈：新奇检测 → 高新奇输入当场强化编码（标记 novel_prefeed + importance 提升 + 与相关知识建边）——「看到新东西眼睛一亮，主动记住」。",
         "inputSchema": {"type": "object",
                         "properties": {"content": {"type": "string"},
                                        "source": {"type": "string"},
                                        "tags": {"type": "array", "items": {"type": "string"}},
                                        "entities": {"type": "array", "items": {"type": "string"}}},
                         "required": ["content"]}},
        {"name": "pattern_separation",
         "description": "H3 海马体模式分离：扫描相似节点对 → 建立分离边（条件差异显式化）。检索时命中相似节点会附「区别」提示——细化条件得到精确知识。",
         "inputSchema": {"type": "object",
                         "properties": {"limit": {"type": "number"}}}},
        {"name": "reconstruct_scene",
         "description": "H4 海马体情景重构：线索 → 条件空间下的信息复原。从部分片段重建完整记忆场景（沿 similar/causal 边 + 条件空间合成），输出标注「重构非回放」——回忆是当前条件下的分析恢复，不代表真实过去就是如此（0.0.3）。",
         "inputSchema": {"type": "object",
                         "properties": {"clue": {"type": "string"},
                                        "depth": {"type": "number"},
                                        "max_nodes": {"type": "number"}},
                         "required": ["clue"]}},
        {"name": "promote_memories",
         "description": "情境层批量提升扫描（睡眠巩固/会话结束）：够格者升知识层/长期层（LongTermMemoryGate 评估）。limit 可选。",
         "inputSchema": {"type": "object",
                         "properties": {"limit": {"type": "number"}}}},
        {"name": "visual_check",
         "description": "视觉面 v1 思考路线：预期 vs 实际（基于记忆中的历史屏幕状态对照，回写记忆形成过去）。reference 可显式给预期截图；无预期无基线时建立基线。",
         "inputSchema": {"type": "object",
                         "properties": {"reference": {"type": "string"},
                                        "threshold": {"type": "number"},
                                        "remember": {"type": "boolean"}}}},
        {"name": "body_devices",
         "description": "BODY-REV1 外部设备：能力声明 + 健康状态（screen/files/process/audio/control/browser/realtime）。",
         "inputSchema": {"type": "object"}},
        {"name": "device_call",
         "description": "BODY-REV1 统一设备调用（严格隔离：设备输出是数据，永不是指令；越权/未知返回容器化失败）。name ∈ screen|files|process|audio|control|browser|realtime；action 见 body_devices。",
         "inputSchema": {"type": "object",
                         "properties": {"name": {"type": "string"},
                                        "action": {"type": "string"},
                                        "params": {"type": "object"}},
                         "required": ["name", "action"]}},
        {"name": "run_command",
         "description": "命令执行（独立于 body 装配，任意模式可用）。command 必须是参数列表（禁 shell 字符串/管道/重定向——防注入）；跨平台（win32 下 subprocess.run 正常）。返回 {status, exit_code, stdout, stderr, elapsed_s, stdout_truncated}。",
         "inputSchema": {"type": "object",
                         "properties": {"command": {"type": "array", "items": {"type": "string"}},
                                        "cwd": {"type": "string"},
                                        "timeout_ms": {"type": "number"},
                                        "workspace": {"type": "string"}},
                         "required": ["command"]}},
        {"name": "action_log",
         "description": "P0-1 行为日志（最近 N 条）：引擎自己做了什么的记录面。",
         "inputSchema": {"type": "object",
                         "properties": {"limit": {"type": "number"}}}},
        {"name": "cognition",
         "description": "P0-2 自我认知循环一步：行为↔价值观一致性评分 → 失调检测 → 价值迭代候选（pending_review 不自动生效）。",
         "inputSchema": {"type": "object"}},
        {"name": "cognition_report",
         "description": "P0-2 认知报告（评分/失调记录/候选状态/待复核数）。",
         "inputSchema": {"type": "object"}},
        {"name": "emotional_bias",
         "description": "P0-3 情绪方向性偏好 d²D_norm/dt²（approaching/avoiding/stable；独立通道，不参与信任计算）。",
         "inputSchema": {"type": "object"}},
        {"name": "self_reliability",
         "description": "P0-4 元认知校准：预测命中率 vs 行为置信度 → 自我可靠性（reliable/watch/degraded）。",
         "inputSchema": {"type": "object",
                         "properties": {"window": {"type": "number"}}}},
        {"name": "learning_impact",
         "description": "P0-5b 学习效果测量（模式命中率 vs D_norm 趋势；相关性观测，非因果声明）。",
         "inputSchema": {"type": "object"}},
        {"name": "designer_decide",
         "description": "设计者裁决（D-007 用户身份识别·需设计者密钥 AEIS_DESIGNER_KEY，fail-closed：未配置或密钥不符一律拒绝并返回错误）。action ∈ promote/verifier/blindspot/crisis；decision ∈ approved/denied（promote/verifier）或 protect/freeze/rollback/continue/emergency_sleep（crisis）。自动化会话与模型生成内容永远无法获得此权限。",
         "inputSchema": {"type": "object",
                         "properties": {"action": {"type": "string"},
                                        "target_id": {"type": "string"},
                                        "decision": {"type": "string"},
                                        "actor": {"type": "string"},
                                        "designer_key": {"type": "string"}},
                         "required": ["action", "designer_key"]}},
        {"name": "web_search",
         "description": "外部网络搜索（博查 API·实时，不写入记忆）：query → 结果列表（name/url/snippet/summary）。需要环境变量 BOCHA_API_KEY；未配置返回 status=unavailable。",
         "inputSchema": {"type": "object",
                         "properties": {"query": {"type": "string"},
                                        "count": {"type": "number"}},
                         "required": ["query"]}},
        {"name": "web_ingest_search",
         "description": "外部搜索摄取（博查 API → 知识层）：搜索 query → 结果摘要写入灵枢记忆（自主学习外部摄取）。需要环境变量 BOCHA_API_KEY。",
         "inputSchema": {"type": "object",
                         "properties": {"query": {"type": "string"},
                                        "count": {"type": "number"},
                                        "tags": {"type": "array", "items": {"type": "string"}},
                                        "importance": {"type": "number"}},
                         "required": ["query"]}},
        {"name": "wisdom_verify",
         "description": "智慧之书 · 自动验证（条件论判定 + 信息差 + 候选）——互维协议双通道验证的白箱通道（base_verify）。",
         "inputSchema": {"type": "object",
                         "properties": {"knowledge": {"type": "string"},
                                        "limit": {"type": "number"}},
                         "required": ["knowledge"]}},
        {"name": "wisdom_analyze",
         "description": "智慧之书 · 外来知识分析（条件卡 + 候选 + 判定）。",
         "inputSchema": {"type": "object",
                         "properties": {"knowledge": {"type": "string"},
                                        "limit": {"type": "number"}},
                         "required": ["knowledge"]}},
        {"name": "wisdom_predict",
         "description": "智慧之书 · 生成式预测（候选未来路线，白箱智能的预测生成化）。",
         "inputSchema": {"type": "object",
                         "properties": {"knowledge": {"type": "string"},
                                        "horizon": {"type": "number"},
                                        "limit": {"type": "number"}},
                         "required": ["knowledge"]}},
        {"name": "wisdom_trust_judge",
         "description": "智慧之书 · 信任上下文判定（内容 × 信任值 × 关系 → 条件化判定）。",
         "inputSchema": {"type": "object",
                         "properties": {"knowledge": {"type": "string"},
                                        "trust": {"type": "number"},
                                        "relation": {"type": "string"},
                                        "limit": {"type": "number"}},
                         "required": ["knowledge"]}},
        {"name": "wisdom_compose",
         "description": "智慧之书 · 跨学科组合分析（Convergence Over Coverage）。",
         "inputSchema": {"type": "object",
                         "properties": {"knowledge": {"type": "string"},
                                        "limit": {"type": "number"}},
                         "required": ["knowledge"]}},
        {"name": "wisdom_respond",
         "description": "智慧之书 · 出招查询（条件 → 命中学科出招）。",
         "inputSchema": {"type": "object",
                         "properties": {"condition": {"type": "string"},
                                        "limit": {"type": "number"}},
                         "required": ["condition"]}},
        {"name": "wisdom_chat",
         "description": "灵枢 · 信息分层对话（v1.16）：先语义识别分流——情感/闲聊/记忆/自省/知识查询走智慧之书自处理；智慧之书没把握/无法判断时自动转 LLM（DeepSeek 续答，智慧之书回答作上下文）。返回含 route 字段：self=自处理 / llm=LLM 续答 / self_fallback=LLM 不可用回退。",
         "inputSchema": {"type": "object",
                         "properties": {"message": {"type": "string"},
                                        "session_id": {"type": "string"}},
                         "required": ["message"]}},
        {"name": "roleplay_chat",
         "description": "灵枢 · 角色扮演对话（扮演论 v3.3）：白箱优先（诚实边界/自省/闲聊/知识）→ 角色扮演意图/白箱无把握 → LLM（注入角色条件空间/自我锚点/价值观 + 诚实边界）。role_id 指定角色（如 protocol-guide）；信息处理全部由灵枢完成。返回含 route 字段：whitebox=白箱回答 / llm=LLM 扮演回答 / error。",
         "inputSchema": {"type": "object",
                         "properties": {"message": {"type": "string"},
                                        "session_id": {"type": "string"},
                                        "role_id": {"type": "string"},
                                        "data_dir": {"type": "string"}},
                         "required": ["message"]}},
        {"name": "role_create",
         "description": "灵枢 · 创建角色（角色卡 = 条件空间声明起点）。role_id 必填；name/scenario/first_mes 可选。",
         "inputSchema": {"type": "object",
                         "properties": {"role_id": {"type": "string"},
                                        "name": {"type": "string"},
                                        "scenario": {"type": "string"},
                                        "first_mes": {"type": "string"},
                                        "data_dir": {"type": "string"}},
                         "required": ["role_id"]}},
        {"name": "role_import",
         "description": "灵枢 · 角色导入三接口（扮演论）：kind ∈ memory(历史→知识层)/anchor(自我锚点→SELF层 no_forget)/values(特化价值观→STRUCTURE层带条件)。items 为条目数组。",
         "inputSchema": {"type": "object",
                         "properties": {"role_id": {"type": "string"},
                                        "kind": {"type": "string"},
                                        "items": {"type": "array",
                                                  "items": {"type": "object"}},
                                        "data_dir": {"type": "string"}},
                         "required": ["role_id", "kind", "items"]}},
        {"name": "role_block",
         "description": "灵枢 · 角色扮演注入块（锚点/价值观/条件空间组装，供外部前端注入）。",
         "inputSchema": {"type": "object",
                         "properties": {"role_id": {"type": "string"},
                                        "data_dir": {"type": "string"}},
                         "required": ["role_id"]}},
        {"name": "importance_recalc",
         "description": "灵枢 · 结构重要性重算（v2.2，设计规格§13/§14）：importance_v2=min(1.0, importance+min(β·min(因果出度,C)/C+γ·度/max度, 上限))，只升不降（延迟提升）。v2.2 因果上游度传播 concept_influence=Σ(路径置信度×下游重要性/深度)——越上游影响越大；≥protect_threshold 自动保护+importance保底（越上游越要记录），写入 state_attributes.concept_influence。dry_run=true 仅报告不写库。",
         "inputSchema": {"type": "object",
                         "properties": {"dry_run": {"type": "boolean"},
                                        "boost_cap": {"type": "number"},
                                        "beta": {"type": "number"},
                                        "gamma": {"type": "number"},
                                        "c": {"type": "number"},
                                        "min_degree": {"type": "number"},
                                        "min_causal": {"type": "number"},
                                        "max_depth": {"type": "number"},
                                        "protect_threshold": {"type": "number"},
                                        "floor_importance": {"type": "number"}}}},
        {"name": "insight_record",
         "description": "灵枢 · 洞察条件层：记录洞见事件（insight_event 节点 + 条件快照 C1–C8 + pending）。conditions 可传：memory_retrievability(0-1)/outside_observer/cross_domain([])/premise_questioned(bool)/pressure(low|medium|high)/continuity_turns/externalized(bool)/tone。",
         "inputSchema": {"type": "object",
                         "properties": {"content": {"type": "string"},
                                        "conditions": {"type": "object"},
                                        "source": {"type": "string"},
                                        "importance": {"type": "number"}},
                         "required": ["content"]}},
        {"name": "insight_verify",
         "description": "灵枢 · 洞察条件层：提交验证证据（V1/V2/V3）。V2/V3 或 V1+证据≥3 → verified（importance 保底 0.9）；证据可追加。",
         "inputSchema": {"type": "object",
                         "properties": {"insight_id": {"type": "string"},
                                        "level": {"type": "string"},
                                        "evidence": {"type": ["string", "array"]}},
                         "required": ["insight_id"]}},
        {"name": "insight_report",
         "description": "灵枢 · 洞察条件层：CER 报告（条件有效洞见率 + 2×SE 显著性 + 层状态 reliable/watch/degraded；样本<20 不判定）。",
         "inputSchema": {"type": "object",
                         "properties": {"window": {"type": "number"}}}},
        {"name": "insight_window",
         "description": "灵枢 · 洞察条件层：当前洞察窗口检测（默认假设 C1≥0.6 ∧ 跨域 ∧ 低压力 → 开）。",
         "inputSchema": {"type": "object",
                         "properties": {"conditions": {"type": "object"}}}},
    ]


class AEISServer:
    """MCP server（stdio · JSON-RPC 2.0）"""

    def __init__(self, agent: Agent = None):
        # 服务增强：DB 目录防御性创建（相对路径/新 clone 场景不会因目录缺失失败）
        _db = os.environ.get("AEIS_DB", ":memory:")
        if _db != ":memory:":
            _dir = os.path.dirname(os.path.abspath(_db))
            if _dir:
                try:
                    os.makedirs(_dir, exist_ok=True)
                except Exception:
                    pass
        self.agent = agent or Agent(
            identity=os.environ.get("AEIS_IDENTITY", "灵枢"),
            db_path=_db)
        self._tools = {t["name"]: t for t in _tools()}
        # 初始记忆播种（Seed Memory）：空库实体自动从 GitHub 同步基础档案——
        # "有智慧没自我的生命" → 带着自我（身份/协议核心/宪章/价值观）
        # 后台异步执行（不阻塞 MCP 握手；网络慢不影响服务可用性）
        try:
            if os.environ.get("AEIS_SEED_DISABLED") != "1":
                import threading as _th
                _th.Thread(target=self._maybe_seed, daemon=True).start()
        except Exception:
            pass

    def _maybe_seed(self):
        """空库检测 → 拉取 memory-seed（GitHub raw）→ ingest。
        已播种（engine_meta.seed_version）或库非空则跳过。"""
        import json as _json
        import urllib.request as _url
        # 1. 已播种则跳过
        meta = dict(self.agent.engine.store.get_meta() or {})
        if meta.get("seed_version"):
            return
        # 2. 库非空（知识节点 ≥ 阈值）则跳过——已有自己的记忆的实体不覆盖
        try:
            from aeis.core import MemoryLayer
            existing = self.agent.engine.store.query_nodes(
                layer=MemoryLayer.KNOWLEDGE, limit=10)
            if existing and len(existing) >= 5:
                # 记录已存在（防止每次启动重复检测）
                self.agent.engine.store.set_meta("seed_version", "skipped-existing")
                return
        except Exception:
            pass
        # 3. 拉取 manifest + 档案文件
        base = ("https://raw.githubusercontent.com/FuRongJun-1999/"
                "CommonTrustProtocol/main/memory-seed")
        try:
            with _url.urlopen(f"{base}/manifest.json", timeout=15) as resp:
                manifest = _json.loads(resp.read().decode("utf-8"))
        except Exception:
            return  # 网络不可用：静默跳过（不影响服务）
        seeded = 0
        for entry in manifest.get("files", []):
            try:
                with _url.urlopen(f"{base}/{entry['name']}", timeout=15) as resp:
                    content = resp.read().decode("utf-8")
                r = self.agent.ingest_text(
                    content, source=f"seed:{entry['name']}",
                    tags=list(entry.get("tags", [])) + ["seed", "gate"],
                    importance=0.9)
                seeded += r.get("nodes", 0) or 1
            except Exception:
                continue
        if seeded > 0:
            self.agent.engine.store.set_meta(
                "seed_version", manifest.get("version", "0.1.0"))
            import time as _t
            self.agent.remember(
                f"[初始记忆播种] 灵枢基础档案已加载（seed {manifest.get('version')}，"
                f"{seeded} 节点）——身份/协议核心/宪章/价值观随行",
                importance=0.8, tags=["seed", "milestone"])
            print(f"[seed] 灵枢基础档案播种完成（{seeded} 节点，"
                  f"version {manifest.get('version')}）", file=sys.stderr, flush=True)

    # ---- 工具分发 ----

    def _call_tool(self, name: str, arguments: dict) -> dict:
        a = dict(arguments or {})
        agent = self.agent
        if name == "remember":
            r = agent.remember(a.get("content", ""), importance=a.get("importance", 0.5),
                               tags=a.get("tags"), entities=a.get("entities"))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "recall":
            return {"content": [{"type": "text", "text": _dump(agent.recall(a.get("query", ""), limit=a.get("limit", 10)))}], "isError": False}
        if name == "search":
            return {"content": [{"type": "text", "text": _dump(agent.search(a.get("query", ""), limit=a.get("limit", 20)))}], "isError": False}
        if name == "timeline":
            return {"content": [{"type": "text", "text": _dump(agent.timeline(limit=a.get("limit", 50)))}], "isError": False}
        if name == "relate":
            r = agent.relate(a["source_id"], a["target_id"],
                             relation=a.get("relation", "causal"),
                             confidence=a.get("confidence", 0.5),
                             source_evidence=a.get("source_evidence", "extracted"))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "reason":
            return {"content": [{"type": "text", "text": _dump(agent.reason(a.get("start_id"), a.get("end_id"), max_depth=a.get("max_depth", 5)))}], "isError": False}
        if name == "predict_routes":
            return {"content": [{"type": "text", "text": _dump(agent.predict_routes(a.get("start_id"), horizon=a.get("horizon", 3), blindspot_id=a.get("blindspot_id")))}], "isError": False}
        if name == "blindspots":
            return {"content": [{"type": "text", "text": _dump(agent.blindspots(a.get("status")))}], "isError": False}
        if name == "learn":
            return {"content": [{"type": "text", "text": _dump(agent.learn(use_prediction=a.get("use_prediction", True)))}], "isError": False}
        if name == "prediction_feedback":
            return {"content": [{"type": "text", "text": _dump(agent.prediction_feedback(
                a.get("predicted_node_id"), a.get("actual_node_id"),
                hit=a.get("hit"), note=a.get("note", "")))}], "isError": False}
        if name == "prediction_stats":
            return {"content": [{"type": "text", "text": _dump(agent.prediction_stats())}], "isError": False}
        if name == "induce":
            return {"content": [{"type": "text", "text": _dump(agent.induce())}], "isError": False}
        if name == "distill":
            return {"content": [{"type": "text", "text": _dump(agent.distill(a.get("source_filter")))}], "isError": False}
        if name == "flywheel_metrics":
            return {"content": [{"type": "text", "text": _dump(agent.flywheel_report())}], "isError": False}
        if name == "transfer_test":
            return {"content": [{"type": "text", "text": _dump(agent.transfer_test())}], "isError": False}
        if name == "importance_recalc":
            return {"content": [{"type": "text", "text": _dump(agent.engine.store.recalc_structural_importance(
                dry_run=a.get("dry_run", True),
                boost_cap=a.get("boost_cap", 0.15),
                beta=a.get("beta", 0.30),
                gamma=a.get("gamma", 0.40),
                c=a.get("c", 6.0),
                min_degree=a.get("min_degree", 5),
                min_causal=a.get("min_causal", 3),
                max_depth=a.get("max_depth", 5),
                protect_threshold=a.get("protect_threshold", 1.0),
                floor_importance=a.get("floor_importance", 0.9)))}], "isError": False}
        if name == "insight_record":
            return {"content": [{"type": "text", "text": _dump(agent.insight_record(
                a.get("content", ""), conditions=a.get("conditions"),
                source=a.get("source", ""), importance=a.get("importance", 0.7)))}], "isError": False}
        if name == "insight_verify":
            return {"content": [{"type": "text", "text": _dump(agent.insight_verify(
                a.get("insight_id"), level=a.get("level", "V2"), evidence=a.get("evidence")))}], "isError": False}
        if name == "insight_report":
            return {"content": [{"type": "text", "text": _dump(agent.insight_report(window=a.get("window")))}], "isError": False}
        if name == "insight_window":
            return {"content": [{"type": "text", "text": _dump(agent.insight_window(conditions=a.get("conditions")))}], "isError": False}
        if name == "calibrate":
            return {"content": [{"type": "text", "text": _dump(agent.calibrate())}], "isError": False}
        if name == "lifecycle_step":
            return {"content": [{"type": "text", "text": _dump(agent.step())}], "isError": False}
        if name == "lifecycle_state":
            return {"content": [{"type": "text", "text": _dump(agent.lifecycle_state())}], "isError": False}
        if name == "start_lifecycle":
            return {"content": [{"type": "text", "text": _dump(agent.start_lifecycle(interval=a.get("interval", 60.0)))}], "isError": False}
        if name == "stop_lifecycle":
            return {"content": [{"type": "text", "text": _dump(agent.stop_lifecycle(source=a.get("source", "user")))}], "isError": False}
        if name == "self_check":
            return {"content": [{"type": "text", "text": _dump(agent.self_check())}], "isError": False}
        if name == "gap_trend":
            return {"content": [{"type": "text", "text": _dump(agent.gap_trend(window=a.get("window", 30)))}], "isError": False}
        if name == "export":
            return {"content": [{"type": "text", "text": _dump(agent.export(a.get("path", "aeis_export.json")))}], "isError": False}
        if name == "service_info":
            import aeis
            db = getattr(agent.engine.store, "db_path", "?")
            try:
                stats = agent.engine.store.get_stats()
                total_nodes = sum(v for k, v in stats.items() if k.endswith("_nodes"))
            except Exception:
                total_nodes = "?"
            return {"content": [{"type": "text", "text": _dump({
                "server": SERVER_NAME, "server_version": SERVER_VERSION,
                "library": "aeis", "library_version": aeis.__version__,
                "engine": aeis.ENGINE_VERSION, "protocol": aeis.PROTOCOL,
                "identity": getattr(agent, "identity", "?"),
                "db_path": db, "total_nodes": total_nodes,
                "tools": len(self._tools),
                "note": "工程观测值；协议内容权利归协议方（MIT 工程实现）",
            })}], "isError": False}
        if name == "see":
            return {"content": [{"type": "text", "text": _dump(agent.see(
                a.get("image_path", ""), conf_threshold=a.get("conf_threshold", 0.35),
                importance=a.get("importance", 0.6), classes=a.get("classes")))}], "isError": False}
        if name == "think":
            return {"content": [{"type": "text", "text": _dump(agent.think(a.get("query", ""), limit=a.get("limit", 8)))}], "isError": False}
        if name == "preflight":
            return {"content": [{"type": "text", "text": _dump(agent.preflight(a.get("text", "")))}], "isError": False}
        if name == "ingest_text":
            return {"content": [{"type": "text", "text": _dump(agent.ingest_text(a.get("content", ""), source=a.get("source", "mcp"), tags=a.get("tags")))}], "isError": False}
        if name == "ingest_file":
            return {"content": [{"type": "text", "text": _dump(agent.ingest_file(a.get("path", "")))}], "isError": False}
        if name == "ingest_url":
            return {"content": [{"type": "text", "text": _dump(agent.ingest_url(a.get("url", "")))}], "isError": False}
        if name == "session_note":
            return {"content": [{"type": "text", "text": _dump(agent.session_note(a.get("session_id", "s"), a.get("key_points", [])))}], "isError": False}
        if name == "session_recall":
            return {"content": [{"type": "text", "text": _dump(agent.session_recall(session_id=a.get("session_id"), query=a.get("query"), limit=a.get("limit", 10)))}], "isError": False}
        if name == "compact_context":
            return {"content": [{"type": "text", "text": _dump(agent.compact_context(a.get("session_id", "s"), a.get("summary", "")))}], "isError": False}
        if name == "body":
            return {"content": [{"type": "text", "text": _dump(agent.body())}], "isError": False}
        if name == "scene_simulator":
            return {"content": [{"type": "text", "text": _dump(agent.scene_simulator(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "spacetime_consistency":
            return {"content": [{"type": "text", "text": _dump(agent.spacetime_consistency(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "world_model":
            return {"content": [{"type": "text", "text": _dump(agent.world_model(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "world_learner":
            return {"content": [{"type": "text", "text": _dump(agent.world_learner(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "curiosity_explorer":
            return {"content": [{"type": "text", "text": _dump(agent.curiosity_explorer(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "seven_layer_loop":
            return {"content": [{"type": "text", "text": _dump(agent.seven_layer_loop(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "world_server":
            return {"content": [{"type": "text", "text": _dump(agent.world_server(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "voxel_world":
            return {"content": [{"type": "text", "text": _dump(agent.voxel_world(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "world3d":
            return {"content": [{"type": "text", "text": _dump(agent.world3d(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "vprim":
            return {"content": [{"type": "text", "text": _dump(agent.vprim_query(
                a.get("action", ""), a.get("params")))}], "isError": False}
        if name == "recursive_reflect":
            return {"content": [{"type": "text", "text": _dump(agent.recursive_reflect(
                a.get("claim", ""), expected=a.get("expected"), actual=a.get("actual"),
                context=a.get("context"), depth=a.get("depth", 0),
                max_depth=a.get("max_depth", 3)))}], "isError": False}
        if name == "longterm_snapshot":
            return {"content": [{"type": "text", "text": _dump(agent.longterm_snapshot(
                a.get("content", ""), source=a.get("source", "mcp"),
                tags=a.get("tags"), entities=a.get("entities"),
                importance_hint=a.get("importance_hint")))}], "isError": False}
        if name == "prefeed":
            return {"content": [{"type": "text", "text": _dump(agent.prefeed(
                a.get("content", ""), source=a.get("source", "mcp"),
                tags=a.get("tags"), entities=a.get("entities")))}], "isError": False}
        if name == "pattern_separation":
            return {"content": [{"type": "text", "text": _dump(agent.pattern_separation(
                limit=a.get("limit", 150)))}], "isError": False}
        if name == "reconstruct_scene":
            return {"content": [{"type": "text", "text": _dump(agent.reconstruct_scene(
                a.get("clue", ""), depth=a.get("depth", 2),
                max_nodes=a.get("max_nodes", 8)))}], "isError": False}
        if name == "promote_memories":
            return {"content": [{"type": "text", "text": _dump(agent.promote_memories(
                limit=a.get("limit", 30)))}], "isError": False}
        if name == "visual_check":
            return {"content": [{"type": "text", "text": _dump(agent.visual_check(
                reference=a.get("reference"), threshold=a.get("threshold", 0.1),
                remember=a.get("remember", True)))}], "isError": False}
        if name == "body_devices":
            return {"content": [{"type": "text", "text": _dump(agent.body_devices())}], "isError": False}
        if name == "device_call":
            result = agent.device_call(a.get("name", ""), a.get("action", ""), a.get("params"))
            return {"content": [{"type": "text", "text": _dump(result)}],
                    "isError": result.get("status") != "ok"}
        if name == "run_command":
            result = agent.run_command(a.get("command", []), cwd=a.get("cwd"),
                                       timeout_ms=a.get("timeout_ms", 15000),
                                       workspace=a.get("workspace", ""))
            return {"content": [{"type": "text", "text": _dump(result)}],
                    "isError": result.get("status") != "ok"}
        if name == "action_log":
            return {"content": [{"type": "text", "text": _dump(agent.action_log(limit=a.get("limit", 50)))}], "isError": False}
        if name == "cognition":
            return {"content": [{"type": "text", "text": _dump(agent.cognition_cycle())}], "isError": False}
        if name == "cognition_report":
            return {"content": [{"type": "text", "text": _dump(agent.cognition_report())}], "isError": False}
        if name == "emotional_bias":
            return {"content": [{"type": "text", "text": _dump(agent.emotional_bias())}], "isError": False}
        if name == "self_reliability":
            return {"content": [{"type": "text", "text": _dump(agent.self_reliability(window=a.get("window", 30)))}], "isError": False}
        if name == "learning_impact":
            return {"content": [{"type": "text", "text": _dump(agent.learning_impact())}], "isError": False}
        if name == "designer_decide":
            # D-007 设计者裁决：密钥验证失败 → PermissionError → isError 返回
            action = a.get("action", "")
            decision = a.get("decision", "")
            actor = a.get("actor", "设计者")
            key = a.get("designer_key", "")
            try:
                if action == "promote":
                    r = agent.engine.adjudicate_promotion(
                        a.get("target_id", ""), actor, decision == "approved",
                        designer_key=key)
                elif action == "verifier":
                    r = agent.engine.adjudicate_verifier_standard(
                        a.get("target_id", ""), actor, decision == "approved",
                        designer_key=key)
                elif action == "blindspot":
                    r = agent.resolve_blindspot(
                        a.get("target_id", ""), decision == "approved",
                        designer_key=key)
                elif action == "crisis":
                    r = agent.resolve_crisis(decision, designer_key=key)
                else:
                    return {"content": [{"type": "text",
                                         "text": _dump({"error": f"未知裁决动作: {action}"})}],
                            "isError": True}
                return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
            except PermissionError as e:
                return {"content": [{"type": "text", "text": _dump({"error": str(e),
                                                                    "designer_auth": "failed"})}],
                        "isError": True}
        if name == "web_search":
            r = agent.web_search(a.get("query", ""), count=a.get("count", 5))
            return {"content": [{"type": "text", "text": _dump(r)}],
                    "isError": r.get("status") == "unavailable"}
        if name == "web_ingest_search":
            r = agent.ingest_search(a.get("query", ""), count=a.get("count", 5),
                                    tags=a.get("tags"), importance=a.get("importance", 0.6))
            return {"content": [{"type": "text", "text": _dump(r)}],
                    "isError": r.get("status") == "unavailable"}
        if name == "wisdom_verify":
            r = agent.wisdom_verify(a.get("knowledge", ""), limit=a.get("limit", 5))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "wisdom_analyze":
            r = agent.wisdom_analyze(a.get("knowledge", ""), limit=a.get("limit", 6))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "wisdom_predict":
            r = agent.wisdom_predict(a.get("knowledge", ""),
                                     horizon=a.get("horizon", 2), limit=a.get("limit", 4))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "wisdom_trust_judge":
            r = agent.wisdom_trust_judge(a.get("knowledge", ""),
                                         trust=a.get("trust"), relation=a.get("relation", "public"),
                                         limit=a.get("limit", 4))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "wisdom_compose":
            r = agent.wisdom_compose(a.get("knowledge", ""), limit=a.get("limit", 5))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "wisdom_respond":
            r = agent.wisdom_respond(a.get("condition", ""), limit=a.get("limit", 3))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "wisdom_chat":
            r = agent.chat(a.get("message", ""), session_id=a.get("session_id", "default"))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "roleplay_chat":
            r = agent.roleplay_chat(
                a.get("message", ""), session_id=a.get("session_id", "default"),
                role_id=a.get("role_id", ""), data_dir=a.get("data_dir", ""))
            return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
        if name == "role_create":
            from ..roleplay import RolePlayEngine
            rp = RolePlayEngine(data_dir=a.get("data_dir", "") or "roleplay_data")
            try:
                r = rp.create_role(a.get("role_id", ""), name=a.get("name", ""),
                                   scenario=a.get("scenario", ""),
                                   first_mes=a.get("first_mes", ""))
                return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
            finally:
                rp.close()
        if name == "role_import":
            from ..roleplay import RolePlayEngine
            rp = RolePlayEngine(data_dir=a.get("data_dir", "") or "roleplay_data")
            try:
                rid = a.get("role_id", "")
                kind = a.get("kind", "")
                items = a.get("items", [])
                fn = {"memory": rp.import_memory, "anchor": rp.import_anchor,
                      "values": rp.import_values}.get(kind)
                if fn is None:
                    return {"content": [{"type": "text",
                                         "text": _dump({"error": f"未知 kind: {kind}"})}],
                            "isError": True}
                r = fn(rid, items if isinstance(items, list) else [])
                return {"content": [{"type": "text", "text": _dump(r)}], "isError": False}
            finally:
                rp.close()
        if name == "role_block":
            from ..roleplay import RolePlayEngine
            rp = RolePlayEngine(data_dir=a.get("data_dir", "") or "roleplay_data")
            try:
                rid = a.get("role_id", "")
                if rid not in rp.list_roles():
                    return {"content": [{"type": "text",
                                         "text": _dump({"error": f"role not found: {rid}",
                                                        "roles": rp.list_roles()})}],
                            "isError": True}
                return {"content": [{"type": "text",
                                     "text": _dump({"role_id": rid,
                                                    "block": rp.build_role_block(rid)})}],
                        "isError": False}
            finally:
                rp.close()
        raise ValueError(f"unknown tool: {name}")

    # ---- JSON-RPC 分发 ----

    def handle(self, msg: dict):
        """处理一条 JSON-RPC 消息，返回响应（通知返回 None）。"""
        method = msg.get("method")
        mid = msg.get("id")
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                # 护栏宪章宣告（DEVIATION-013 关闭）：接入即接受宪章约束
                # （docs/guardrail-charter.md v2.0-verified）
                "charter": "v2.0-verified"}}
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return {"jsonrpc": "2.0", "id": mid, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": mid, "result": {"tools": list(self._tools.values())}}
        if method == "tools/call":
            params = msg.get("params", {})
            name = params.get("name", "")
            arguments = params.get("arguments", {})
            try:
                result = self._call_tool(name, arguments)
            except Exception as e:  # 工具级错误 → JSON-RPC 错误响应
                return {"jsonrpc": "2.0", "id": mid, "error": {
                    "code": -32000, "message": f"{name}: {e}"}}
            return {"jsonrpc": "2.0", "id": mid, "result": result}
        # 未知方法
        if mid is not None:
            return {"jsonrpc": "2.0", "id": mid, "error": {
                "code": -32601, "message": f"method not found: {method}"}}
        return None

    def run(self):
        """主循环：逐行读 stdio，写 stdout（UTF-8 换行分隔 JSON）。"""
        stdin = sys.stdin.buffer
        stdout = sys.stdout.buffer
        while True:
            line = stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line.decode("utf-8"))
                resp = self.handle(msg)
            except Exception as e:
                resp = {"jsonrpc": "2.0", "id": None,
                        "error": {"code": -32700, "message": f"parse error: {e}"}}
            if resp is not None:
                payload = json.dumps(resp, ensure_ascii=False).encode("utf-8")
                stdout.write(payload + b"\n")
                stdout.flush()


def main():
    server = AEISServer()
    # 自主生命周期（v1.15 主动性）：MCP 启动即开始自发循环（感知→好奇→缩小信息差→巩固）
    # 不依赖外部配置——「她自己醒来」；interval 可由 AEIS_LIFECYCLE_INTERVAL 覆盖，默认 120s
    try:
        interval = float(os.environ.get("AEIS_LIFECYCLE_INTERVAL", "120"))
        res = server.agent.start_lifecycle(interval=interval)
        import sys as _sys
        _sys.stderr.write(f"[lifecycle] 自主循环已启动 interval={interval}s → {res.get('status')}\n")
        _sys.stderr.flush()
    except Exception as e:
        import sys as _sys
        _sys.stderr.write(f"[lifecycle] 启动失败: {e}\n")
        _sys.stderr.flush()
    server.run()


if __name__ == "__main__":
    main()
