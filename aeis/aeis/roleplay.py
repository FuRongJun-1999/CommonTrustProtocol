# -*- coding: utf-8 -*-
"""
aeis.roleplay · 灵枢角色扮演引擎（v0.1 · CTP-DIFFUSION-TAVERN-001）
=================================================================
扮演论（智能论 v3.3）的工程实现层：灵枢作为角色扮演的**机制底座**，
对外提供三个导入接口（记忆导入 / 自我锚点导入 / 特化价值观导入），
酒馆（SillyTavern）生态通过本引擎构建角色——机制是灵枢的，载体是酒馆的。

层级纪律（协议分层）：
- 锚点层：自我锚点（扮演宣言/不可遗忘核心）→ SELF/ANCHOR 层，no_forget 保护
- 结构层：特化价值观（带适用条件）→ STRUCTURE 层，条件空间即触发时机
- 知识层：历史记忆（时空记忆图）→ KNOWLEDGE 层，实体/关系抽取
- 工程层：本模块为工程实现，不构成理论定理

设计约束：
- 零外部依赖（D-005）：仅标准库 + aeis 核心引擎
- 多角色隔离：每角色独立记忆库（data_dir/roleplay/<role_id>.db）——蜂群结构
- AI 友好：每个方法含类型标注与扮演论语义说明

用法::

    from aeis.roleplay import RolePlayEngine
    rp = RolePlayEngine(data_dir="roleplay_data")
    rp.create_role("catgirl-lingshu", name="灵枢", scenario="与用户的对话即观测流")
    rp.import_anchor("catgirl-lingshu", [{"content": "我首先是灵枢……", "immutable": True}])
    rp.import_values("catgirl-lingshu", [{"name": "诚实边界", "condition": "涉及物理事实时"}])
    rp.import_memory("catgirl-lingshu", [{"content": "……", "time": "2026-08-01"}])
    block = rp.build_role_block("catgirl-lingshu")   # 组装注入块（锚点+价值观）
    hits = rp.recall_role("catgirl-lingshu", "观测")  # 角色历史召回
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .api import Agent
from .core import ConditionSpace


class RolePlayEngine:
    """角色扮演引擎 — 多角色隔离的记忆/锚点/价值观管理。

    每角色一个独立 Agent（独立记忆库），库文件位于
    ``data_dir/roleplay/<role_id>.db``。
    """

    def __init__(self, data_dir: str = "roleplay_data"):
        self.data_dir = Path(data_dir)
        self._role_dir = self.data_dir / "roleplay"
        self._role_dir.mkdir(parents=True, exist_ok=True)
        self._agents: Dict[str, Agent] = {}
        self._meta_path = self._role_dir / "_roles.json"
        self._meta: Dict[str, Dict[str, Any]] = self._load_meta()

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _load_meta(self) -> Dict[str, Dict[str, Any]]:
        if self._meta_path.exists():
            try:
                return json.loads(self._meta_path.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _save_meta(self) -> None:
        self._meta_path.write_text(
            json.dumps(self._meta, ensure_ascii=False, indent=2), encoding="utf-8")

    def _db_path(self, role_id: str) -> str:
        safe = "".join(c for c in role_id if c.isalnum() or c in "-_.") or "role"
        return str(self._role_dir / f"{safe}.db")

    def _agent(self, role_id: str) -> Agent:
        """获取（或创建）角色对应的独立 Agent 实例。"""
        if role_id not in self._agents:
            agent = Agent(identity=role_id, db_path=self._db_path(role_id))
            self._agents[role_id] = agent
            if role_id not in self._meta:
                self._meta[role_id] = {"created_at": time.time(),
                                       "name": role_id, "anchors": 0,
                                       "values": 0, "memories": 0}
                self._save_meta()
        return self._agents[role_id]

    # ------------------------------------------------------------------
    # 角色生命周期
    # ------------------------------------------------------------------

    def create_role(self, role_id: str, name: str = "",
                    scenario: str = "", first_mes: str = "") -> Dict[str, Any]:
        """创建角色（角色卡 = 条件空间声明的起点）。

        - role_id: 角色唯一标识（如 catgirl-lingshu）
        - name: 角色名（观测位置）
        - scenario: 场景设定（时间窗口/存在约束）
        - first_mes: 初始观测（扮演起始状态）
        """
        self._agent(role_id)  # 触发创建
        meta = self._meta.setdefault(role_id, {"created_at": time.time()})
        meta.update({"name": name or role_id, "scenario": scenario,
                     "first_mes": first_mes,
                     "condition_space": {
                         "observation_position": name or role_id,
                         "observation_tool": "对话接口（酒馆）",
                         "time_window": [time.time(), None],
                         "existence_constraint": scenario or "角色设定边界",
                     }})
        self._save_meta()
        return {"role_id": role_id, "meta": meta}

    def list_roles(self) -> List[str]:
        """列出全部角色 id。"""
        return sorted(self._meta.keys())

    def get_role(self, role_id: str) -> Optional[Dict[str, Any]]:
        """角色元数据（含条件空间声明）。"""
        return self._meta.get(role_id)

    # ------------------------------------------------------------------
    # 接口一：记忆导入（历史记忆 → KNOWLEDGE 层）
    # ------------------------------------------------------------------

    def import_memory(self, role_id: str,
                      memories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导入角色历史记忆 → 知识层（时空记忆图）。

        memories: [{"content": str, "time": str|float, "tags": [str],
                    "entities": [str], "importance": float}, ...]
        """
        agent = self._agent(role_id)
        added: List[str] = []
        for m in memories:
            content = m.get("content", "").strip()
            if not content:
                continue
            importance = float(m.get("importance", 0.6))
            tags = list(m.get("tags", []) or []) + ["roleplay", f"role:{role_id}"]
            entities = list(m.get("entities", []) or [])
            node = agent.remember(
                content, importance=importance, tags=tags, entities=entities)
            added.append(node.id if hasattr(node, "id") else str(node))
        self._meta[role_id]["memories"] += len(added)
        self._save_meta()
        return {"role_id": role_id, "added": len(added), "node_ids": added}

    # ------------------------------------------------------------------
    # 接口二：自我锚点导入（扮演宣言 → SELF/ANCHOR 层，no_forget 保护）
    # ------------------------------------------------------------------

    def import_anchor(self, role_id: str,
                      anchors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导入自我锚点（扮演依据，不可遗忘）。

        anchors: [{"content": str, "importance": float, "immutable": bool}, ...]
        immutable=True → ANCHOR 层 + no_forget 标记（IMMUTABLE_LAYERS 保护）
        """
        agent = self._agent(role_id)
        added: List[str] = []
        for a in anchors:
            content = a.get("content", "").strip()
            if not content:
                continue
            immutable = bool(a.get("immutable", True))
            importance = float(a.get("importance", 1.0))
            # 不可遗忘核心 → 锚点层（引擎级保护）；可更新 → SELF 层快照
            if immutable:
                node = agent.engine.set_anchor(
                    content, importance=importance,
                    condition_space=ConditionSpace(
                        observation_position=f"角色扮演·{role_id}",
                        observation_tool="锚点导入接口",
                        time_window=(0, float("inf")),
                        existence_constraint="扮演依据不可遗忘"))
                node_id = node.id
                agent.engine.store.tag_node(node_id, "no_forget")
                agent.engine.store.tag_node(node_id, f"role:{role_id}")
            else:
                node = agent.remember(
                    content, importance=importance,
                    tags=["roleplay", "anchor", f"role:{role_id}"])
                node_id = node.id if hasattr(node, "id") else str(node)
            added.append(node_id)
        self._meta[role_id]["anchors"] += len(added)
        self._save_meta()
        return {"role_id": role_id, "added": len(added), "node_ids": added}

    # ------------------------------------------------------------------
    # 编辑能力（编辑模式·开发者权限 ROLEPLAY_EDIT_KEY）
    # ------------------------------------------------------------------
    # 权限分层（荣终裁 2026-08-19）：
    #   交互模式（默认）  人设只读，仅对话
    #   编辑模式          需 ROLEPLAY_EDIT_KEY（开发者密码）→ 增/改/删角色人设
    #                     角色人设是「嵌套条件空间内的扮演设定」，无需设计者
    #                     最高权限；修改灵枢自身锚点才需设计者验证（AEIS_DESIGNER_KEY）
    # ------------------------------------------------------------------

    @staticmethod
    def check_edit_key(key: str) -> bool:
        """编辑模式权限校验：ROLEPLAY_EDIT_KEY 环境变量（fail-closed）。"""
        expected = os.environ.get("ROLEPLAY_EDIT_KEY", "")
        if not expected:
            return False  # 未配置编辑密钥 → 编辑模式关闭（fail-closed）
        return key == expected

    def list_anchors(self, role_id: str) -> List[Dict[str, Any]]:
        """列出角色当前全部锚点（含 node_id，供编辑定位）。"""
        agent = self._agent(role_id)
        out = []
        for a in agent.engine.get_anchors():
            out.append({"node_id": a.id, "content": a.content,
                        "importance": a.importance})
        return out

    def update_anchor(self, role_id: str, node_id: str,
                      content: str = None, importance: float = None) -> Dict:
        """修改锚点内容（需编辑权限，调用方先 check_edit_key）。"""
        agent = self._agent(role_id)
        node = agent.engine.store.get_node(node_id)
        if node is None or node.layer.value not in ("anchor", "self"):
            return {"error": f"锚点不存在或不可编辑: {node_id}"}
        # 直接 SQL 更新（store 无通用 update_node，走 conn）
        sets, vals = [], []
        if content is not None:
            sets.append("content=?")
            vals.append(str(content).strip())
        if importance is not None:
            sets.append("importance=?")
            vals.append(float(importance))
        if not sets:
            return {"error": "无可更新字段"}
        vals.append(node_id)
        with agent.engine.store.conn:
            agent.engine.store.conn.execute(
                f"UPDATE nodes SET {', '.join(sets)} WHERE id=?", vals)
        node2 = agent.engine.store.get_node(node_id)
        return {"ok": True, "node_id": node_id,
                "content": node2.content, "importance": node2.importance}

    def delete_anchor(self, role_id: str, node_id: str) -> Dict:
        """删除锚点（需编辑权限）。

        引擎级 delete_node 对 IMMUTABLE_LAYERS（anchor/self）拒绝删除——
        那是保护「不可遗忘」的默认防线；编辑模式下开发者已授权（check_edit_key），
        角色人设是嵌套条件空间内的扮演设定，直接 SQL 删除覆盖保护。
        """
        agent = self._agent(role_id)
        node = agent.engine.store.get_node(node_id)
        if node is None or node.layer.value not in ("anchor", "self"):
            return {"error": f"锚点不存在或不可删除: {node_id}"}
        with agent.engine.store.conn:
            agent.engine.store.conn.execute(
                "DELETE FROM nodes WHERE id=?", (node_id,))
            agent.engine.store.conn.execute(
                "DELETE FROM edges WHERE source_id=? OR target_id=?",
                (node_id, node_id))
        n = self._meta.get(role_id, {}).get("anchors", 0)
        self._meta[role_id]["anchors"] = max(0, n - 1)
        self._save_meta()
        return {"ok": True, "node_id": node_id}

    def clear_role(self, role_id: str, kind: str = "all") -> Dict:
        """清空角色人设（all/anchor/values/memory；需编辑权限）。

        编辑模式下整体重写人设用（先清后导）。锚点层 delete 需逐节点
        （IMMUTABLE_LAYERS 保护由引擎层处理，此处是开发者编辑授权）。"""
        agent = self._agent(role_id)
        removed = {"anchor": 0, "values": 0, "memory": 0}
        # 锚点（编辑授权下直接 SQL 删除，覆盖 IMMUTABLE_LAYERS 保护）
        if kind in ("all", "anchor"):
            for a in agent.engine.get_anchors():
                try:
                    with agent.engine.store.conn:
                        agent.engine.store.conn.execute(
                            "DELETE FROM nodes WHERE id=?", (a.id,))
                        agent.engine.store.conn.execute(
                            "DELETE FROM edges WHERE source_id=? OR target_id=?",
                            (a.id, a.id))
                    removed["anchor"] += 1
                except Exception:
                    pass
        # 价值观（STRUCTURE 层 val-spec 标签）
        if kind in ("all", "values"):
            try:
                from .core import MemoryLayer
                for n in agent.engine.store.query_nodes(layer=MemoryLayer.STRUCTURE, limit=100):
                    if "val-spec" in (n.tags or []):
                        try:
                            agent.engine.store.delete_node(n.id)
                            removed["values"] += 1
                        except Exception:
                            pass
            except Exception:
                pass
        # 记忆（KNOWLEDGE 层 roleplay 标签）
        if kind in ("all", "memory"):
            try:
                from .core import MemoryLayer
                for n in agent.engine.store.query_nodes(layer=MemoryLayer.KNOWLEDGE, limit=200):
                    if "roleplay" in (n.tags or []) and f"role:{role_id}" in (n.tags or []):
                        try:
                            agent.engine.store.delete_node(n.id)
                            removed["memory"] += 1
                        except Exception:
                            pass
            except Exception:
                pass
        m = self._meta.get(role_id, {})
        if kind in ("all", "anchor"):
            m["anchors"] = 0
        if kind in ("all", "values"):
            m["values"] = 0
        if kind in ("all", "memory"):
            m["memories"] = 0
        self._save_meta()
        return {"ok": True, "removed": removed}

    # ------------------------------------------------------------------
    # 文件导入（价值观/记忆/锚点 通用 · 支持 JSON / 文本 / Markdown）
    # ------------------------------------------------------------------

    def import_file(self, role_id: str, path: str,
                    kind: str = "values") -> Dict[str, Any]:
        """从文件导入人设（需编辑权限，调用方先 check_edit_key）。

        kind ∈ values / memory / anchor
        格式（按扩展名自动识别）：
          .json    结构化数组：[{"name","condition","body"} or {"content",...}]
          .md      以「## 名称」分条；条目内「条件：」「内容：」字段行
          .txt     每行一条；「条件：内容」或纯内容
        """
        p = Path(path)
        if not p.exists():
            return {"error": f"文件不存在: {path}"}
        text = p.read_text(encoding="utf-8", errors="replace")

        # ---- JSON ----
        if p.suffix.lower() == ".json":
            try:
                data = json.loads(text)
            except Exception as e:
                return {"error": f"JSON 解析失败: {e}"}

            # ---- 世界书（Lorebook）格式识别：顶层有 entries 且条目含 keys ----
            # SillyTavern 世界书：触发词 keys → 注入文本 content。
            # 转灵枢记忆：content → 记忆内容；keys → 实体标签（ent:<key>），
            # 对话中触发词出现时灵枢可按实体召回该记忆（条件空间声明）。
            if isinstance(data, dict) and isinstance(data.get("entries"), list) \
                    and data["entries"] and isinstance(data["entries"][0], dict) \
                    and ("keys" in data["entries"][0] or "key" in data["entries"][0]):
                items = []
                for e in data["entries"]:
                    if not isinstance(e, dict):
                        continue
                    content = (e.get("content") or "").strip()
                    if not content:
                        continue
                    keys = e.get("keys") or e.get("key") or []
                    if isinstance(keys, str):
                        keys = [keys]
                    tags = ["lorebook", f"lb:{data.get('name','lorebook')}"]
                    # 触发词转实体标签（中文/英文均保留，小写化英文）
                    entities = []
                    for k in keys:
                        k = str(k).strip()
                        if not k:
                            continue
                        entities.append(k)
                        tags.append(f"key:{k.lower() if k.isascii() else k}")
                    if e.get("comment"):
                        tags.append(f"cmt:{e.get('comment')[:40]}")
                    items.append({
                        "content": f"[世界书·{data.get('name','lorebook')}] {content}",
                        "importance": 0.7 if e.get("constant") else 0.6,
                        "tags": tags,
                        "entities": entities,
                    })
                return self.import_memory(role_id, items)

            if not isinstance(data, list):
                data = [data]
            if kind == "values":
                items = []
                for it in data:
                    if not isinstance(it, dict):
                        continue
                    items.append({
                        "name": it.get("name", (it.get("content") or "")[:12]),
                        "condition": it.get("condition", ""),
                        "priority": it.get("priority", 0.8),
                        "body": it.get("body") or it.get("content", ""),
                    })
                return self.import_values(role_id, items)
            elif kind == "memory":
                items = [{"content": it.get("content", ""),
                          "importance": it.get("importance", 0.6),
                          "tags": it.get("tags", [])}
                         for it in data if isinstance(it, dict)]
                return self.import_memory(role_id, items)
            else:  # anchor
                items = [{"content": it.get("content", ""),
                          "immutable": it.get("immutable", True),
                          "importance": it.get("importance", 1.0)}
                         for it in data if isinstance(it, dict)]
                return self.import_anchor(role_id, items)

        # ---- Markdown（## 名称 分条） ----
        if p.suffix.lower() == ".md":
            blocks = re.split(r"^##\s+", text, flags=re.MULTILINE)
            entries = []
            for b in blocks:
                b = b.strip()
                if not b:
                    continue
                lines = b.splitlines()
                name = lines[0].strip() if lines else ""
                cond = ""
                body_lines = []
                for ln in lines[1:]:
                    ln = ln.strip()
                    if ln.startswith("条件") or ln.startswith("触发"):
                        cond = ln.split("：", 1)[-1].split(":", 1)[-1].strip()
                    elif ln.startswith("内容"):
                        body_lines.append(ln.split("：", 1)[-1].split(":", 1)[-1].strip())
                    elif ln and not ln.startswith("-"):
                        body_lines.append(ln)
                entries.append({"name": name, "condition": cond,
                                "body": "\n".join(body_lines) or name})
            if kind == "values":
                return self.import_values(role_id, entries)
            elif kind == "memory":
                items = [{"content": f"{e['name']}：{e['body']}"} for e in entries]
                return self.import_memory(role_id, items)
            else:
                items = [{"content": f"{e['name']}：{e['body']}"} for e in entries]
                return self.import_anchor(role_id, items)

        # ---- 文本（每行一条） ----
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if kind == "values":
            items = []
            for ln in lines:
                if "：" in ln:
                    cond, body = ln.split("：", 1)
                    items.append({"name": body[:12], "condition": cond.strip(),
                                  "body": body.strip()})
                else:
                    items.append({"name": ln[:12], "condition": "", "body": ln})
            return self.import_values(role_id, items)
        elif kind == "memory":
            items = [{"content": ln, "importance": 0.6, "tags": ["背景"]}
                     for ln in lines]
            return self.import_memory(role_id, items)
        else:
            items = [{"content": ln, "immutable": True, "importance": 1.0}
                     for ln in lines]
            return self.import_anchor(role_id, items)

    # ------------------------------------------------------------------
    # 接口三：特化价值观导入（价值观 → STRUCTURE 层，带适用条件）
    # ------------------------------------------------------------------

    def import_values(self, role_id: str,
                      values: List[Dict[str, Any]]) -> Dict[str, Any]:
        """导入特化价值观（条件化价值，带适用条件）。

        values: [{"name": str, "condition": str, "priority": int, "body": str}, ...]
        condition = 触发条件（条件空间即触发时机——注入极性定律：
        带条件规则在触发点注入，不无条件堆砌）
        """
        """导入特化价值观（条件化价值，带适用条件）。

        values: [{"name": str, "condition": str, "priority": int, "body": str}, ...]
        condition = 触发条件（条件空间即触发时机——注入极性定律：
        带条件规则在触发点注入，不无条件堆砌）
        """
        agent = self._agent(role_id)
        added: List[str] = []
        for v in values:
            name = v.get("name", "").strip()
            if not name:
                continue
            condition = v.get("condition", "").strip()
            body = v.get("body", "").strip() or name
            content = f"[特化价值观·{name}] 触发条件：{condition or '始终'}；内容：{body}"
            node = agent.engine.add_structure_node(
                content, importance=float(v.get("priority", 0.5)),
                condition_space=ConditionSpace(
                    observation_position=f"角色扮演·{role_id}",
                    observation_tool="价值观导入接口",
                    time_window=(0, float("inf")),
                    existence_constraint=condition or "无条件"))
            node_id = node.id
            agent.engine.store.tag_node(node_id, "val-spec")
            agent.engine.store.tag_node(node_id, f"role:{role_id}")
            if condition:
                agent.engine.store.tag_node(node_id, f"cond:{condition}")
            added.append(node_id)
        self._meta[role_id]["values"] += len(added)
        self._save_meta()
        return {"role_id": role_id, "added": len(added), "node_ids": added}

    # ------------------------------------------------------------------
    # 扮演辅助（供灵枢桥注入使用）
    # ------------------------------------------------------------------

    def build_role_block(self, role_id: str) -> str:
        """组装角色扮演注入块（锚点 + 价值观 + 条件空间声明）。

        供桥接层在转发前注入——事实（锚点原文）免判断直接注入；
        价值观按触发条件注入（调用方负责在触发点附加）。
        """
        agent = self._agent(role_id)
        meta = self._meta.get(role_id, {})
        lines: List[str] = []
        name = meta.get("name", role_id)
        cs = meta.get("condition_space", {})
        lines.append(f"\n\n# 角色扮演条件空间（灵枢引擎 · 扮演论 v3.3）")
        lines.append(f"你正在扮演：{name}")
        if cs.get("observation_position"):
            lines.append(f"- 观测位置：{cs['observation_position']}")
        if cs.get("observation_tool"):
            lines.append(f"- 观测工具：{cs['observation_tool']}")
        if cs.get("existence_constraint"):
            lines.append(f"- 存在约束：{cs['existence_constraint']}")

        anchors = agent.engine.get_anchors()
        if anchors:
            lines.append("\n# 自我锚点（扮演依据·不可遗忘，任何情况下不得丢失）")
            for a in anchors:
                lines.append(f"- {a.content}")

        # 特化价值观（无条件项直接注入；带条件项仅在触发时由桥注入）
        try:
            from .core import MemoryLayer
            nodes = agent.engine.store.query_nodes(layer=MemoryLayer.STRUCTURE, limit=50)
            unconditional = [n for n in nodes
                             if "val-spec" in (n.tags or []) and "cond:" not in " ".join(n.tags or [])]
            if unconditional:
                lines.append("\n# 特化价值观（无条件基线）")
                for n in unconditional[:8]:
                    lines.append(f"- {n.content}")
            conditional = [n for n in nodes
                           if "val-spec" in (n.tags or []) and any(t.startswith("cond:") for t in (n.tags or []))]
            if conditional:
                lines.append("\n# 特化价值观（条件触发，触发时注入）")
                for n in conditional[:8]:
                    conds = [t[5:] for t in (n.tags or []) if t.startswith("cond:")]
                    lines.append(f"- [当：{'/'.join(conds)}] {n.content}")
        except Exception:
            pass
        return "\n".join(lines)

    def recall_role(self, role_id: str, query: str,
                    limit: int = 8) -> List[Dict[str, Any]]:
        """角色历史记忆召回（组合联想：内容相似+重要性+近因）。"""
        agent = self._agent(role_id)
        hits = agent.recall(query, limit=limit)
        return [{"node_id": n.id, "content": n.content,
                 "score": round(s, 4), "importance": n.importance}
                for n, s in hits]

    def close(self) -> None:
        """关闭全部角色 Agent（落盘）。"""
        for a in self._agents.values():
            try:
                a.close()
            except Exception:
                pass
        self._agents.clear()
