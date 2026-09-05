# -*- coding: utf-8 -*-
"""aeis.grill · 访谈式需求澄清（design tree + frontier 轮次）
================================================
荣指令（2026-09-05）：AI 先提问、确认要做什么，直到完全清楚；共识固化入认知图。
机制迁移自 mattpocock/skills grilling（skills-ref 已入库，2026-09-05）。
灵枢差异：状态机进引擎（meta 快照跨会话可恢复）+ 产出固化进认知图（非静态文件）
+ 未完全清楚拒绝固化（白箱 DEFER 纪律的访谈版）。

访谈纪律（grill_start 返回给宿主模型，宿主按此执行人机对话）：
  1. 第一问必须是目标（要做什么）——goal 节点
  2. design tree：每个决策分叉出挂在它下面的子决策（depends_on 表达依赖）
  3. frontier 轮次：每轮向用户提出全部前置已落定的问题，编号 + 推荐答案；
     等用户答完再重算 frontier 进入下一轮
  4. 事实自查：环境里能查到的（文件/工具/网络）不问用户；决策归用户
  5. 听到一个决策分支 → grill_node add 登记；用户答完 → grill_node resolve 落定
  6. grill_frontier 返回 done=true → 与用户确认共识 → grill_finish 固化
  7. frontier 非空时 grill_finish 会被引擎拒绝——「不完全清楚就不固化」
"""

import json
import time
import uuid

# 节点类型 → 固化 importance / tag
_KIND_PROFILE = {
    "goal": (0.8, "goal"),
    "decision": (0.7, "decision"),
    "term": (0.6, "term"),
    "fact": (0.5, "fact"),
}

_META_PREFIX = "grill_"

_DISCIPLINE = (
    "访谈纪律（直到完全清楚才结束）：\n"
    "1. 第一问必须是目标：用户到底要做什么（kind=goal）。\n"
    "2. design tree：每个决策分叉出挂在它下面的子决策；子问题用 depends_on 挂到其父问题。\n"
    "3. frontier 轮次：每轮向用户提出全部前置已落定的开放问题，编号并给出推荐答案，"
    "等用户全部答完再重算 frontier 进入下一轮；依赖本轮未决问题的 belonged 下一轮。\n"
    "4. 事实自查：环境里能查到的（文件/工具/网络）不问用户，kind=fact 由你自己 resolve；决策归用户。\n"
    "5. 每听到一个决策分支就 grill_node action=add 登记；用户答完立即 grill_node action=resolve 落定。\n"
    "6. grill_frontier 返回 done=true 时：向用户复述全部已决共识，确认无误后 grill_finish 固化入认知图。\n"
    "7. 引擎在 frontier 非空时拒绝 finish——不完全清楚就不固化。"
)


class GrillNode:
    """设计树上的一个节点 = 一个待澄清的决策/术语/事实"""

    def __init__(self, node_id, title, question, kind="decision",
                 depends_on=None, recommended="",
                 conditions="", negative="", execution=""):
        if kind not in _KIND_PROFILE:
            kind = "decision"
        self.id = node_id
        self.title = title
        self.question = question
        self.kind = kind
        self.depends_on = list(depends_on or [])   # 四要素·子内容(subgraph)：树上即生效条件
        self.recommended = recommended
        # 四要素补全（与认知图节点完全同构——荣裁定 2026-09-05：
        # 访谈 = 对条件进行确认、递归确认子内容、如何执行、不适用条件是什么）
        self.conditions = conditions               # 四要素·生效条件（正路由）
        self.negative = negative                   # 四要素·不适用条件（负路由）
        self.execution = execution                 # 四要素·如何执行
        self.answer = None
        self.who = None          # user=用户裁定 / agent=事实自查
        self.resolved_at = None

    @property
    def resolved(self):
        return self.answer is not None

    def to_dict(self):
        return {"id": self.id, "title": self.title, "question": self.question,
                "kind": self.kind, "depends_on": self.depends_on,
                "recommended": self.recommended,
                "conditions": self.conditions, "negative": self.negative,
                "execution": self.execution, "answer": self.answer,
                "who": self.who, "resolved": self.resolved,
                "resolved_at": self.resolved_at}

    @classmethod
    def from_dict(cls, d):
        n = cls(d["id"], d["title"], d["question"], d.get("kind", "decision"),
                d.get("depends_on"), d.get("recommended", ""),
                d.get("conditions", ""), d.get("negative", ""),
                d.get("execution", ""))
        n.answer = d.get("answer")
        n.who = d.get("who")
        n.resolved_at = d.get("resolved_at")
        return n


class GrillSession:
    """一次访谈 = 一棵 design tree"""

    def __init__(self, topic, context="", session_id=None):
        self.id = session_id or ("grill-" + uuid.uuid4().hex[:8])
        self.topic = topic
        self.context = context
        self.created_at = time.time()
        self.nodes = {}          # id -> GrillNode（插入序 = dict 序）
        self.finished = False
        self.abandoned = False

    def add(self, title, question, kind="decision", depends_on=None,
            recommended="", conditions="", negative="", execution=""):
        nid = "n%d" % (len(self.nodes) + 1)
        node = GrillNode(nid, title, question, kind, depends_on, recommended,
                         conditions, negative, execution)
        self.nodes[nid] = node
        return node

    def resolve(self, node_id, answer, who="user"):
        node = self.nodes[node_id]
        node.answer = answer
        node.who = who
        node.resolved_at = time.time()
        return node

    def frontier(self):
        """前置全部落定的开放节点 = 现在就能问的问题"""
        out = []
        for node in self.nodes.values():
            if node.resolved:
                continue
            deps = [self.nodes[d] for d in node.depends_on if d in self.nodes]
            if all(d.resolved for d in deps):
                out.append(node)
        return out

    def stats(self):
        kinds = {}
        for node in self.nodes.values():
            kinds[node.kind] = kinds.get(node.kind, 0) + 1
        resolved = sum(1 for n in self.nodes.values() if n.resolved)
        return {"total": len(self.nodes), "resolved": resolved,
                "open": len(self.nodes) - resolved, "kinds": kinds}

    def done(self):
        return (not self.abandoned and len(self.nodes) > 0
                and not self.frontier())

    def to_dict(self):
        return {"id": self.id, "topic": self.topic, "context": self.context,
                "created_at": self.created_at, "finished": self.finished,
                "abandoned": self.abandoned,
                "nodes": [n.to_dict() for n in self.nodes.values()]}

    @classmethod
    def from_dict(cls, d):
        s = cls(d["topic"], d.get("context", ""), session_id=d["id"])
        s.created_at = d.get("created_at", s.created_at)
        s.finished = d.get("finished", False)
        s.abandoned = d.get("abandoned", False)
        for nd in d.get("nodes", []):
            n = GrillNode.from_dict(nd)
            s.nodes[n.id] = n
        return s


class GrillManager:
    """访谈管理器：会话生命周期 + 认知图固化（MCP grill_* 工具的后端）"""

    def __init__(self, agent):
        self.agent = agent
        self.sessions = {}
        self._restore()

    # ---- 持久化（meta 快照：访谈进行中跨 server 重启可恢复） ----

    def _restore(self):
        try:
            meta = self.agent.engine.store.get_meta() or {}
            for key, val in meta.items():
                if key.startswith(_META_PREFIX) and isinstance(val, str):
                    try:
                        d = json.loads(val)
                    except Exception:
                        continue
                    if d.get("finished") or d.get("abandoned"):
                        continue
                    self.sessions[d["id"]] = GrillSession.from_dict(d)
        except Exception:
            pass

    def _persist(self, session):
        try:
            self.agent.engine.store.set_meta(
                _META_PREFIX + session.id,
                json.dumps(session.to_dict(), ensure_ascii=False))
        except Exception:
            pass

    # ---- 工具后端 ----

    def start(self, topic, context=""):
        session = GrillSession(topic, context)
        self.sessions[session.id] = session
        self._persist(session)
        related = []
        try:
            related = self.agent.recall(topic, limit=3)
        except Exception:
            related = []
        return {
            "session_id": session.id,
            "discipline": _DISCIPLINE,
            "related_memory": [
                {"content": getattr(n, "content", "")[:120], "score": round(s, 3)}
                for n, s in (related or [])],
            "next": "先用 recall 背景向用户开场，然后提出第一问（目标，kind=goal）。",
        }

    def node_add(self, session_id, title, question, kind="decision",
                 depends_on=None, recommended="",
                 conditions="", negative="", execution=""):
        session = self._get(session_id)
        if session.finished or session.abandoned:
            raise ValueError("session %s already closed" % session_id)
        if not title or not question:
            raise ValueError("title and question are required")
        unknown = [d for d in (depends_on or []) if d not in session.nodes]
        if unknown:
            raise ValueError("unknown depends_on: %s" % ",".join(unknown))
        node = session.add(title, question, kind, depends_on, recommended,
                           conditions, negative, execution)
        self._persist(session)
        return {"node": node.to_dict(),
                "frontier_hint": "登记成功。把它加入当前或下一轮的提问队列"
                                 "（取决于其依赖是否已全部落定）。"}

    def node_resolve(self, session_id, node_id, answer, who="user"):
        session = self._get(session_id)
        if node_id not in session.nodes:
            raise ValueError("unknown node: %s" % node_id)
        if not answer:
            raise ValueError("answer is required")
        node = session.resolve(node_id, answer, who)
        self._persist(session)
        st = session.stats()
        return {"resolved": node.to_dict(), "stats": st,
                "done": session.done(),
                "next": ("frontier 已空：与用户确认共识后 grill_finish 固化。"
                         if session.done() else
                         "重算 frontier，继续下一轮提问。")}

    def frontier(self, session_id):
        session = self._get(session_id)
        fr = session.frontier()
        return {"session_id": session_id, "topic": session.topic,
                "stats": session.stats(), "done": session.done(),
                "frontier": [n.to_dict() for n in fr]}

    def finish(self, session_id, summary="", abandon=False):
        session = self._get(session_id)
        if session.finished:
            raise ValueError("session already finished (固化一次性，防重复写入)")
        if abandon:
            session.abandoned = True
            self._persist(session)
            return {"abandoned": True, "session_id": session_id,
                    "note": "访谈已放弃，未固化任何内容（可逆）。"}
        if session.abandoned:
            raise ValueError("session already abandoned")
        fr = session.frontier()
        if fr:
            # 白箱 DEFER 纪律：不完全清楚就不固化
            open_all = [n for n in session.nodes.values() if not n.resolved]
            frontier_ids = {n.id for n in fr}
            return {"fixed": False,
                    "open_questions": [{"id": n.id, "title": n.title,
                                        "question": n.question,
                                        "askable_now": n.id in frontier_ids}
                                       for n in open_all],
                    "note": "存在未决问题——还没有完全清楚，拒绝固化。"
                            "继续访谈直到 done=true，或用 abandon 放弃。"}
        return self._fixate(session, summary)

    # ---- 固化（认知图写入） ----

    def _fixate(self, session, summary):
        st = session.stats()
        node_ids = {}
        for node in session.nodes.values():
            imp, tag = _KIND_PROFILE[node.kind]
            # KCCS 四要素结构化（与认知图节点同构；子内容=树边，不入文本）
            content = "[grill] %s · %s：%s → %s" % (
                session.topic, node.title, node.question, node.answer)
            if node.conditions:
                content += chr(10) + "生效条件: " + node.conditions
            if node.negative:
                content += chr(10) + "不适用条件: " + node.negative
            if node.execution:
                content += chr(10) + "如何执行: " + node.execution
            # skip_dedup：用户确认的决策节点需要独立节点身份
            # （同 v1.26c 快照/里程碑写入同理，防 M5 去重合并丢结构）
            r = self.agent.engine.add_perception(
                content, importance=imp,
                tags=["grill", session.topic, tag],
                entities=[session.topic], skip_dedup=True)
            nid = getattr(r, "id", None) or (
                r.get("id") if isinstance(r, dict) else None)
            node_ids[node.id] = nid
        # 层级边：子决策 → 其依赖（design tree 结构入图）
        edges = 0
        for node in session.nodes.values():
            for dep in node.depends_on:
                src, dst = node_ids.get(node.id), node_ids.get(dep)
                if src and dst:
                    try:
                        self.agent.relate(src, dst, relation="hierarchical",
                                          confidence=0.9,
                                          source_evidence="extracted")
                        edges += 1
                    except Exception:
                        pass
        session.finished = True
        self._persist(session)
        result = {"fixed": True, "session_id": session.id,
                  "topic": session.topic, "stats": st,
                  "node_memory_ids": node_ids, "tree_edges": edges,
                  "note": "共识已固化入认知图（知识层）。决策树以 hierarchical 边连接。"}
        if summary:
            self.agent.remember(
                "[grill 总结] %s —— %s" % (session.topic, summary),
                importance=0.6,
                tags=["grill", "session", session.topic],
                entities=[session.topic])
            result["summary_saved"] = True
        return result

    def _get(self, session_id):
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError("unknown session: %s（server 重启后未完成访谈"
                             "会从 meta 快照恢复；否则该 id 无效）" % session_id)
        return session
