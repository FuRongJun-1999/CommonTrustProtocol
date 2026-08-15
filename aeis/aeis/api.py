# -*- coding: utf-8 -*-
"""
aeis.api · 灵枢高层接口 — 面向其他智能体的接入点
=================================================
Agent 类封装 SpacetimeMemoryEngine（v1.11），提供分组化的简洁方法面。
协议语义（智能论 v3.2）：五层记忆 · 信息差 D_norm · 信任值 T_total ·
条件空间 · 盲区 · 生命周期七相 · 知识飞轮。

设计约束：
- 零外部依赖（D-005）：全部基于核心引擎与标准库。
- 薄封装：所有方法直接委托核心引擎，不复制逻辑。
- AI 友好：每个方法含类型标注与协议语义说明。
"""

from typing import Dict, List, Optional, Tuple

from .core import (
    SpacetimeMemoryEngine, ConditionSpace, EdgeType, MemoryLayer,
)


class Agent:
    """灵枢智能体 — 其他 AI 的协议接入点。

    用法::

        import aeis
        agent = aeis.Agent(identity="助手", db_path="memory.db")
        agent.remember("用户偏好简洁回答", tags=["preference"])
        hits = agent.recall("偏好")
        agent.distill()          # 知识飞轮：经验 → 可复用模式
        agent.calibrate()        # 宇宙校准参照（方向性检查）
        agent.close()
    """

    def __init__(self, identity: str = "智能体",
                 db_path: str = ":memory:",
                 role: str = "primary",
                 data_dir: Optional[str] = None):
        self.identity = identity
        from .core import Role
        role_enum = Role.PRIMARY if role in ("primary", "PRIMARY") else Role.SECONDARY
        self.engine = SpacetimeMemoryEngine(db_path=db_path, identity=identity,
                                            role=role_enum)
        self._data_dir = data_dir

    # =====================================================================
    # 记忆层（五层记忆 · 3.2 节）
    # =====================================================================

    def remember(self, content: str, importance: float = 0.5,
                 tags: Optional[List[str]] = None,
                 entities: Optional[List[str]] = None,
                 modality: str = "text",
                 condition_space: Optional[ConditionSpace] = None):
        """写入一条感知记忆（自动进入知识层）。

        - content: 记忆内容（中文语义优先）
        - importance: 重要性 [0,1]（近因/重要性参与召回加权）
        - tags: 标签（如 learning_result / preference / anchor 语义标记）
        - entities: 实体名列表（挂接实体注册表）
        - modality: text / image / code 等
        - 自动去重（中文二元组 Jaccard ≥ 动态阈值 → 提升原节点权重）
        """
        return self.engine.add_perception(
            content, modality=modality, importance=importance,
            tags=list(tags or []), entities=list(entities or []) or None,
            condition_space=condition_space)

    def recall(self, query: str, limit: int = 10) -> List[Tuple]:
        """组合联想召回（内容相似 0.5 + 重要性 0.3 + 近因 0.2）。
        返回 [(STNode, score)]。"""
        return self.engine.recall(query, limit=limit)

    def search(self, query: str, limit: int = 20) -> List[Tuple]:
        """内容检索（LIKE 预筛 + 中文二元组 Jaccard 排序）。
        返回 [(STNode, score)]；触发复用追踪（飞轮度量输入）。"""
        return self.engine.search_content(query, limit=limit)

    def timeline(self, limit: int = 50) -> List[Dict]:
        """时间线（按时间倒序的记忆快照）。"""
        return self.engine.timeline(limit=limit)

    def what_happened(self, since: float, until: Optional[float] = None) -> List:
        """时间窗口内发生了什么（时态查询）。"""
        return self.engine.what_happened_at(since, until)

    def anchors(self) -> List:
        """锚点层记忆（不可遗忘的结构记忆，如协议副本）。"""
        return self.engine.get_anchors()

    # =====================================================================
    # 关系与推理（图结构 · 条件空间）
    # =====================================================================

    def relate(self, source_id: str, target_id: str,
               relation: str = "causal",
               confidence: float = 0.5,
               source_evidence: str = "extracted"):
        """在两个节点间建立关系边。

        - relation: causal / similar / sequential / spatial / hierarchical
        - source_evidence: extracted（观察）/ inferred（推导）/ ambiguous
        - 边默认未验证（待验证单元复核）
        """
        et = getattr(EdgeType, relation.upper(), EdgeType.CAUSAL)
        return self.engine.add_edge(source_id, target_id, relation_type=et,
                                    confidence=confidence,
                                    source_evidence=source_evidence)

    def reason(self, start_id: str, end_id: str = None,
               max_depth: int = 5) -> List:
        """因果推理：从起点出发的因果路径集合（List[List[STEdge]]）。"""
        return self.engine.reason_causal(start_id, end_id, max_depth=max_depth)

    def predict_routes(self, start_id: str = None, horizon: int = 3,
                       blindspot_id: str = None) -> Dict:
        """生成式预测：候选未来路线集合（盲区驱动 · T_pred 对齐）。"""
        return self.engine.predict_routes(start_id=start_id,
                                          blindspot_id=blindspot_id,
                                          horizon=horizon)

    def shortest_path(self, start_id: str, end_id: str, max_depth: int = 6) -> List[str]:
        """多边类型最短路径（BFS）。"""
        return self.engine.shortest_path(start_id, end_id, max_depth)

    def subgraph(self, query: str, max_nodes: int = 15) -> Dict:
        """语义检索作用域子图。"""
        return self.engine.query_subgraph(query, max_nodes)

    # =====================================================================
    # 认知（盲区 · 学习 · 归纳）
    # =====================================================================

    def blindspots(self, status: str = None) -> List[Dict]:
        """盲区注册表（D-001 语义判定：对人类文明级负面影响不写入）。"""
        return self.engine.list_blindspots(status=status)

    def learn(self, use_prediction: bool = True) -> Dict:
        """一轮盲区学习（可预测盲区 → 预测路线假设 → 探索 → 终态判定）。"""
        return self.engine.learn_next(use_prediction=use_prediction)

    def induce(self) -> List:
        """归纳/知识合成：并查集聚类 → 概念节点（SIMILAR 边 · inferred 证据）。"""
        return self.engine.induce_concepts()

    def resolve_blindspot(self, blindspot_id: str, resolved: bool = True,
                          note: str = "", designer_key: str = None) -> bool:
        """盲区闭环（D-007 需设计者密钥：D-001 语义判定权在维生系统）。"""
        return self.engine.resolve_blindspot(blindspot_id, resolved, note,
                                             designer_key=designer_key)

    # =====================================================================
    # 知识飞轮（v1.11 · FLYWHEEL-REV1）
    # =====================================================================

    def distill(self, source_filter: str = None) -> Dict:
        """蒸馏管线：经验（被拒路径 + learning_result/induced）→ 可复用模式。
        模式节点带 dsv:<标准版本> 标签；模式→成员 SIMILAR 边（inferred）。"""
        return self.engine.evo_distill_cycle(source_filter)

    def flywheel_report(self) -> Dict:
        """飞轮度量（知识增长率 / 复用率 / 蒸馏产出率）。
        性质：工程观测值，不参与信任值计算（DEVIATION-004）。"""
        return self.engine.evo_flywheel_metrics()

    def transfer_test(self) -> Dict:
        """迁移测试：已对齐条件空间内新实体预测成功率（2×SE 显著性）。
        样本 < 20 不构成迁移判定（DEVIATION-005）。"""
        return self.engine.test_transfer_capability()

    def calibrate(self) -> Dict:
        """宇宙校准参照（元理论方向性检查 · 5 判据）。
        定位：方向性检查工具，不替代工程验证/外部校准；非盲区33关闭依据。"""
        return self.engine.universe_calibrate()

    def mark_contested(self, node_id: str, reason: str) -> bool:
        """标记争议（工作记忆深化）。"""
        return self.engine.mark_contested(node_id, reason)

    def reverify(self, node_id: str) -> bool:
        """重验证（移除 stale · 置信度 +0.05）。"""
        return self.engine.reverify(node_id)

    # =====================================================================
    # 生命周期（v1.10 · 七相工程映射）
    # =====================================================================

    def step(self) -> Dict:
        """生命周期一步：感知 → 好奇 → 缩小信息差 → 信任 → 协作 → 巩固 → standby。
        先消费事件队列（v1.11 P1-4 事件驱动）。"""
        return self.engine.lifecycle_cycle()

    def lifecycle_state(self) -> Dict:
        """生命周期状态（cycle / state / 感知 d_norm），不执行一步。"""
        lc = getattr(self.engine, "_lifecycle", None)
        if lc is None:
            return {"status": "v110_not_ready",
                    "error": getattr(self.engine, "_lifecycle_error", "")}
        state = getattr(lc, "state", "unknown")
        cycle = getattr(lc, "cycle_count", 0)
        return {"status": "ok", "state": state, "cycle": cycle}

    def resolve_crisis(self, decision: str, designer_key: str = None) -> bool:
        """P0 危机终裁（维生系统接口·D-007 需设计者密钥）：decision ∈
        (protect, freeze, rollback, continue, emergency_sleep)。"""
        return self.engine.resolve_crisis(decision, designer_key=designer_key)

    # =====================================================================
    # 元认知与持久化
    # =====================================================================

    def self_check(self) -> Dict:
        """自检：完整性 / 孤儿边 / 表统计。"""
        return self.engine.verify_integrity()

    # =====================================================================
    # 自我认知循环（v1.12 · SELF-COGNITION-REV2）
    # =====================================================================

    def action_log(self, limit: int = 50) -> List[Dict]:
        """P0-1 行为日志（最近 N 条，倒序）：引擎"自己做了什么"的记录面。"""
        return self.engine.get_action_log(limit)

    def action_stats(self) -> Dict:
        """P0-1 行为日志聚合统计（按行为类型）。"""
        return self.engine.action_log_stats()

    def cognition_cycle(self) -> Dict:
        """P0-2 自我认知循环一步：行为↔价值观对照 → 一致性评分 → 失调检测
        → 触发链（detect_deviation）→ 价值迭代候选（pending_review，不自动生效）。"""
        return self.engine.cognition_cycle()

    def cognition_report(self) -> Dict:
        """P0-2 认知报告（最近评分 / 失调记录 / 候选状态）。"""
        return self.engine.cognition_report()

    def apply_value_candidate(self, candidate_id: str, new_value: str = None) -> bool:
        """P0-2 价值迭代候选生效（验证单元复核后调用 · 经 record_value_change
        + 注意力基准联动，role='reflect' 权限规则）。"""
        return self.engine.apply_value_candidate(candidate_id, new_value)

    def emotional_bias(self) -> Dict:
        """P0-3 情绪方向性偏好 d²D_norm/dt²（信息差二阶差分，短期曲率）。
        独立通道，不参与信任值计算（E_weight 零改动）。"""
        return self.engine.get_emotional_bias()

    def self_reliability(self, window: int = 30) -> Dict:
        """P0-4 元认知校准：预测命中率 vs 行为置信度 → 自我可靠性模型
        （reliable / watch / degraded；输出归一化参考，不修改存储）。"""
        return self.engine.get_self_reliability(window)

    def learning_impact(self, window: int = 30) -> Dict:
        """P0-5b 学习效果测量（模式命中率 vs D_norm 趋势 · 相关性观测，非因果声明）。"""
        return self.engine.learning_impact(window)

    # =====================================================================
    # 上下文外部化（第 5 项：上下文通过灵枢解决）
    # =====================================================================

    def session_note(self, session_id: str, key_points: list,
                     importance: float = 0.7) -> Dict:
        """会话要点外部化：关键信息写入灵枢（session 标签），
        上下文可释放后按需恢复。每个要点一个节点，可检索。"""
        if isinstance(key_points, str):
            key_points = [key_points]
        nodes = []
        for i, pt in enumerate(key_points):
            node = self.remember(f"[会话{session_id}·要点{i+1}] {pt}",
                                 importance=importance,
                                 tags=[f"session:{session_id}", "context_external"])
            nodes.append(node.id)
        return {"status": "ok", "session": session_id,
                "nodes": len(nodes), "node_ids": nodes}

    def session_recall(self, session_id: str = None, query: str = None,
                       limit: int = 10) -> List:
        """会话要点恢复：检索灵枢中的会话记忆（按 session 或语义）。"""
        if session_id:
            nodes = self.engine.store.query_nodes(limit=200)
            hits = [(n, 1.0) for n in nodes
                    if any(t.startswith(f"session:{session_id}") for t in n.tags)]
            hits.sort(key=lambda x: -x[0].importance)
            return hits[:limit]
        if query:
            return self.recall(query, limit=limit)
        return []

    def compact_context(self, session_id: str, summary: str) -> Dict:
        """上下文压缩：生成会话摘要节点（超长会话恢复入口）。
        调用方：会话接近上下文上限时，写入摘要后释放旧上下文。"""
        node = self.remember(f"[会话摘要·{session_id}] {summary}",
                             importance=0.9,
                             tags=[f"session:{session_id}", "context_summary"])
        return {"status": "ok", "session": session_id, "node_id": node.id,
                "note": "恢复路径：session_recall(session_id) 或 search('会话摘要')"}

    # =====================================================================
    # 视觉与身体（v1.13 · VISION-REV1）
    # =====================================================================

    # =====================================================================
    # 推理强化（第 2 项：协议 + 反思 + 长记忆）
    # =====================================================================

    # =====================================================================
    # 外部知识摄取（第 3 项：记忆含外部知识）
    # =====================================================================

    def ingest_text(self, content: str, source: str = "manual",
                    tags: Optional[List[str]] = None,
                    importance: float = 0.6) -> Dict:
        """外部知识摄取：文本 → 知识层（source 标签可追溯 · 实体提取 · 可检索）"""
        from .knowledge import ingest_text as _it
        return _it(self.engine, content, source, tags, importance)

    def ingest_file(self, path: str, tags: Optional[List[str]] = None,
                    importance: float = 0.6) -> Dict:
        """外部知识摄取：文件（txt/md/json/代码等，按扩展名处理）"""
        from .knowledge import ingest_file as _if
        return _if(self.engine, path, tags, importance)

    def ingest_url(self, url: str, tags: Optional[List[str]] = None,
                   importance: float = 0.6) -> Dict:
        """外部知识摄取：URL 页面（requests+bs4 优先，编码修复；urllib 降级）"""
        from .knowledge import ingest_url as _iu
        return _iu(self.engine, url, tags, importance)

    def ingest_search(self, query: str, count: int = 5,
                      tags: Optional[List[str]] = None,
                      importance: float = 0.6) -> Dict:
        """博查搜索摄取：搜索 query → 结果摘要写入知识层（自主学习外部摄取）。
        需要环境变量 BOCHA_API_KEY。"""
        from .knowledge import ingest_search as _is
        return _is(self.engine, query, count, tags, importance)

    def web_search(self, query: str, count: int = 5) -> Dict:
        """博查实时搜索（不写入记忆，仅返回结果）。需要 BOCHA_API_KEY。"""
        from .web import WebTool
        return WebTool().search(query, count=count)

    def think(self, query: str, limit: int = 8) -> Dict:
        """推理前记忆注入：检索相关记忆（内容检索+组合联想+模式加权）
        → 组合推理上下文。推理链：记忆支撑 → 协议推理 → 输出。
        返回 {query, memory_count, context}——context 为按分数排序的记忆摘要。"""
        results = []
        seen = set()
        for src in (self.search(query, limit=limit), self.recall(query, limit=limit)):
            for node, score in src:
                if node.id in seen:
                    continue
                seen.add(node.id)
                results.append((node, score))
        results.sort(key=lambda x: -x[1])
        results = results[:limit]
        context = []
        for node, score in results:
            tag = "[模式]" if "reusable_pattern" in node.tags else ""
            context.append(f"{tag}{node.content[:120]} (score={score:.2f})")
        return {"query": query, "memory_count": len(context),
                "context": context,
                "note": "记忆增强推理：检索结果作为推理上下文，非结论"}

    def preflight(self, text: str) -> Dict:
        """输出前反思钩子：内容与价值观一致性检查（冲突词拦截）。
        推理强化：重要输出对外发布前调用，失调内容前置拦截。"""
        sc = getattr(self.engine, "_self_cognition", None)
        if sc is None:
            return {"ok": True, "note": "自我认知组件未装配"}
        return sc.preflight(text)

    def see(self, image_path: str, conf_threshold: float = 0.35,
            importance: float = 0.6, classes: list = None) -> Dict:
        """视觉感知：目标检测 → 摘要写入知识层记忆（modality=image）。
        检测结果可检索、可参与后续推理（第 1 项：视觉）。
        classes：开放词汇检测词（中/英，YOLO-World；默认文生图核心词表）"""
        return self.engine.perceive_image(image_path, conf_threshold, importance, classes)

    def body(self) -> Dict:
        """身体能力声明：感知模态（文本/图像）+ 运动工具 + 记忆（第 4 项铺垫）。
        身体 = 自我的一部分（自我模型的感知-运动面）。"""
        return self.engine.get_body_capabilities()

    def body_devices(self) -> Dict:
        """BODY-REV1：外部设备能力声明 + 健康状态（screen/files/process）。"""
        return self.engine.body_devices()

    def device_call(self, name: str, action: str, params: Dict = None) -> Dict:
        """BODY-REV1：统一设备调用（严格隔离——设备输出是数据，永不是指令）。

        name: screen | files | process；action 见各设备 capabilities。
        越权/未知 → 容器化失败（不抛异常）。"""
        return self.engine.device_call(name, action, params)

    def sync_body_state(self) -> Dict:
        """BODY-REV1：身体状态同步到自我模型（感知模态+设备清单）。"""
        return self.engine.sync_body_state()

    def world3d(self, action: str, params: dict = None) -> Dict:
        """WORLD3D-REV1 时空重建：语义 → 3D 空间与颜色（build/render/status/add）。"""
        return self.engine.world3d(action, params)

    def vprim_query(self, action: str, params: dict = None) -> Dict:
        """VPRIM-REV1 视觉原语查询（确定性·零 LLM）：
        spatial（两 bbox 空间关系）/ count（视觉原语计数）/ anchors（锚点列表）"""
        return self.engine.vprim_query(action, params)

    def voice_session_log(self, turn: dict) -> str:
        """语音对话会话沉淀（voice_session 记忆节点）。"""
        return self.engine.voice_session_log(turn)

    def longterm_snapshot(self, content: str, source: str = "snapshot",
                          tags: list = None, entities: list = None,
                          importance_hint: float = None) -> Dict:
        """v1.15 长期记忆写入：快照 → 重要性评估（信息差/信任/二阶变化/提及）
        → 按层级写入（长期/知识/情境）+ 条件空间 + 关联边。"""
        return self.engine.longterm_snapshot(content, source, tags,
                                             entities, importance_hint)

    def promote_memories(self, limit: int = 30) -> list:
        """情境层批量提升（睡眠巩固/会话结束）：够格者升知识层/长期层。"""
        return self.engine.promote_context_memories(limit)

    def recursive_reflect(self, claim: str, expected: str = None,
                          actual: str = None, context: str = None,
                          depth: int = 0, max_depth: int = 3) -> Dict:
        """协议 3.12 递归验证反思 + 1.6.7 元反思（REFLECT-REV1 显式推理技能）。

        元反思（定标准）→ 一级验证（预期vs实际）→ 二级反思（问1 隐藏前提
        /问2 影响）→ 三级终裁（可逆性优先）→ 记录单元归档。递归 ≤ 3 层。"""
        return self.engine.recursive_reflect(claim, expected, actual,
                                             context, depth, max_depth)

    def visual_check(self, reference: str = None, threshold: float = 0.1,
                     remember: bool = True) -> Dict:
        """视觉面 v1 思考路线：预期 vs 实际（基于记忆中的历史屏幕状态对照）。

        视觉 = 信息差处理：预期（过去）与当前帧的差异即新信息；
        对照结果回写记忆形成持续更新的"过去"。"""
        return self.engine.visual_check(reference, threshold, remember)

    def gap_trend(self, window: int = 30) -> Dict:
        """信息差收敛趋势（A-4 线性回归斜率）。"""
        return self.engine.get_gap_trend(window=window)

    def export(self, path: str) -> Dict:
        """全库导出（JSON · 灾备/迁移/摘要交换）。"""
        return self.engine.export_all(path)

    def import_backup(self, path: str) -> Dict:
        """全库导入（恢复/合并）。"""
        return self.engine.import_all(path)

    # ---- 智慧之书（白箱智能引擎 · wisdom_book 条件论知识图谱） ----
    _wisdom = None

    def _get_wisdom(self):
        """惰性加载智慧之书 ConditionDex（类级缓存，只建一次）。"""
        if type(self)._wisdom is None:
            import sys as _s
            import os as _os
            _pkg = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
            _wdir = _os.path.join(_pkg, "wisdom")
            if _wdir not in _s.path:
                _s.path.insert(0, _wdir)
            import wisdom_book as _wb
            dex = _wb.ConditionDex(fresh=True)
            dex.seed_base()
            type(self)._wisdom = dex
        return self._wisdom

    def wisdom_analyze(self, knowledge: str, limit: int = 6) -> Dict:
        """智慧之书 · 外来知识分析（条件卡 + 候选 + 判定）。"""
        return self._get_wisdom().dex_analyze(knowledge, limit=limit)

    def wisdom_verify(self, knowledge: str, limit: int = 5) -> Dict:
        """智慧之书 · 自动验证（P5 信息修复 · 基地裁判）——互维协议双通道的白箱通道。"""
        return self._get_wisdom().dex_auto_verify(knowledge, limit=limit)

    def wisdom_compose(self, knowledge: str, limit: int = 5) -> Dict:
        """智慧之书 · 跨学科组合分析（Convergence Over Coverage）。"""
        return self._get_wisdom().dex_compose(knowledge, limit=limit)

    def wisdom_predict(self, knowledge: str, horizon: int = 2, limit: int = 4) -> Dict:
        """智慧之书 · 生成式预测（候选未来路线）——白箱智能的预测生成化。"""
        return self._get_wisdom().dex_predict(knowledge, horizon=horizon, limit=limit)

    def wisdom_respond(self, condition: str, limit: int = 3) -> Dict:
        """智慧之书 · 出招查询（条件 → 命中学科出招）。"""
        return {"results": self._get_wisdom().dex_respond(condition, limit=limit)}

    def wisdom_trust_judge(self, knowledge: str, trust: float = None,
                           relation: str = "public", limit: int = 4) -> Dict:
        """智慧之书 · 信任上下文判定（内容 × 信任值 × 关系 → 条件化判定）。"""
        return self._get_wisdom().dex_trust_judge(
            knowledge, trust=trust, relation=relation, limit=limit)

    def close(self):
        """关闭引擎（释放连接）。"""
        try:
            self.engine.close()
        except Exception:
            pass
