# -*- coding: utf-8 -*-
"""
aeis.roleplay_chat · 灵枢统一对话管线（白箱 + 角色扮演 + 长期记忆 + LLM 输出）
============================================================================
两种交互方式（MCP / 网页）共用同一套信息处理管线，全部由灵枢完成：

  用户消息
    ↓
  1. 白箱条件分析（wisdom.chat_engine._cond_analysis / chat）
     - 诚实边界 / 自我指涉 / 情绪 / 闲聊 / 追源 由白箱直接回答（零 LLM）
     - 任务类 → 路由到 LLM
    ↓
  2. 角色扮演注入（roleplay 引擎）
     - role_id 存在时：锚点/价值观/条件空间注入到 LLM system
    ↓
  3. 长期记忆（Agent remember / recall / session）
     - 对话前召回相关记忆注入；对话后写入（prefeed 海马体前馈）
    ↓
  4. LLM 输出（DeepSeek / 任意 OpenAI 兼容上游）
     - 任务类消息 → LLM 生成 → 返回

设计约束：
- 零外部依赖核心（http/urllib 标准库），LLM 调用走 urllib
- 白箱路由优先（诚实边界等不消耗 LLM）——「诚实是唯一不坍缩的扮演」
- roleplay 注入遵循注入极性：事实免判断、价值观带条件、无条件规则不堆砌

用法（MCP / 网页共用）::

    from aeis.roleplay_chat import LingshuChat
    lc = LingshuChat(data_dir="roleplay_data", role_id="protocol-guide")
    reply = lc.respond("你能扮演神吗？", session_id="s1")
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

# 灵枢记忆
from .api import Agent
# 角色扮演引擎
from .roleplay import RolePlayEngine
# 白箱（智慧之书 chat_engine）
try:
    sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
    import chat_engine as _wisdom_chat
    _WISDOM_OK = True
except Exception:
    _WISDOM_OK = False


class LingshuChat:
    """灵枢统一对话管线——白箱 + 角色扮演 + 长期记忆 + LLM。"""

    def __init__(self, data_dir: str = "roleplay_data",
                 role_id: str = "",
                 db_path: str = "",
                 upstream_base: str = "",
                 upstream_model: str = "",
                 upstream_key_var: str = "DEEPSEEK_API_KEY",
                 dex: Any = None):
        self.role_id = role_id
        self.rp = RolePlayEngine(data_dir=data_dir)  # 始终创建（运行时 role_id 指定）
        # 灵枢记忆 Agent（同一库：长期记忆/认知）
        self.mem = Agent(identity=role_id or "灵枢", db_path=db_path or ":memory:")
        self.upstream_base = upstream_base or os.environ.get(
            "LINGSHU_UPSTREAM_BASE", "https://api.deepseek.com/v1")
        self.upstream_model = upstream_model or os.environ.get(
            "LINGSHU_UPSTREAM_MODEL", "deepseek-chat")
        key = os.environ.get(upstream_key_var, "")
        if not key:
            # 回退 Machine/User 环境
            import subprocess
            key = os.environ.get(upstream_key_var, "") or _machine_env(upstream_key_var)
        self.upstream_key = key
        # 白箱图谱检索器：显式传入优先；否则复用 Agent 的 _get_wisdom()
        # （2026-08-19 白箱边界测试发现：dex=None 时 graph_retrieve 抛异常
        # → hits=[] → 纯知识也全走 LLM，「白箱优先」形同虚设。Agent 内部
        # 有完整 dex 构造逻辑（随包图谱回退），直接复用）
        self.dex = dex
        if self.dex is None:
            try:
                self.dex = self.mem._get_wisdom()
            except Exception:
                self.dex = None
        self._session_ctx: Dict[str, List[str]] = {}

    # ------------------------------------------------------------------
    # 记忆辅助
    # ------------------------------------------------------------------

    def _recall_mem(self, session_id: str, query: str, limit: int = 6,
                    role_id: str = "") -> List[str]:
        """长期记忆召回 → 文本行（按角色隔离：只召回该角色标签的记忆）。

        有 role_id 时查角色库（self.rp 的角色 Agent，含世界书导入的知识层
        记忆）；无角色时查 self.mem（通用内存库）。
        """
        try:
            if role_id and self.rp is not None:
                # 角色库：直接查角色 Agent 的记忆（知识层，含世界书记忆）
                agent = self.rp._agent(role_id)
                hits = agent.recall(query, limit=limit * 4)
            else:
                hits = self.mem.recall(query, limit=limit * 4)
            out = []
            for n, _s in hits:
                tags = n.tags or []
                # 角色对话记忆带 role:<rid> 标签——只召回当前角色的
                if role_id:
                    if f"role:{role_id}" not in tags:
                        continue
                out.append((n.content or "")[:100])
                if len(out) >= limit:
                    break
            return out
        except Exception:
            return []

    def _prefeed(self, message: str) -> None:
        """海马体前馈：新信息当场强化编码。"""
        try:
            self.mem.prefeed(message, source="chat")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 角色扮演注入块
    # ------------------------------------------------------------------

    def _role_system(self, role_id: str = "") -> str:
        """角色扮演注入块（锚点/价值观/条件空间）。role_id 可运行时指定。"""
        rid = role_id or self.role_id
        if not self.rp or not rid:
            return ""
        try:
            return self.rp.build_role_block(rid)
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # LLM 输出
    # ------------------------------------------------------------------

    def _llm(self, system: str, user: str) -> str:
        """调用上游 LLM（OpenAI 兼容 chat.completions）。"""
        if not self.upstream_key:
            return "（未配置上游 LLM key）"
        url = self.upstream_base.rstrip("/") + "/chat/completions"
        body = {
            "model": self.upstream_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.7,
            "max_tokens": 800,
        }
        req = urllib.request.Request(
            url, data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self.upstream_key}"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                resp = json.loads(r.read().decode("utf-8"))
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"（LLM 调用失败：{e}）"

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------

    def respond(self, message: str, session_id: str = "default",
                role_id: str = "") -> Dict[str, Any]:
        """统一对话入口：白箱 → 角色扮演 → 记忆 → LLM。

        role_id 可运行时指定（覆盖实例级 self.role_id）——网页/MCP 按请求
        传入不同角色，无需重建实例。
        """
        message = (message or "").strip()
        if not message:
            return {"reply": "我在呢，想说点什么？", "route": "empty"}

        rid = role_id or self.role_id  # 运行时角色（请求优先）
        # 输入翻译（自定义名词替换表）：用户现实词 → 角色虚拟词
        # （条件空间对齐——角色在自己的世界语境中理解）
        if rid and self.rp is not None:
            try:
                translated = self.rp.translate_input(rid, message)
                if translated != message:
                    message = translated
            except Exception:
                pass
        rp_block = self._role_system(rid)
        # 会话上下文按 角色+session 隔离（防跨角色串扰——鲸鱼娘历史不能进协议引导者）
        ctx_key = f"{rid}:{session_id}" if rid else f"_gen_:{session_id}"

        # 0. 长期记忆召回（跨 session 持久，灵枢记忆·按角色隔离）
        mem_notes = self._recall_mem(session_id, message, limit=4, role_id=rid)
        ctx = self._session_ctx.get(ctx_key, [])
        if ctx:
            mem_notes += [f"[本会话] {m}" for m in ctx[-3:]]

        # 1. 白箱路由（wisdom chat_engine——诚实边界/自省/闲聊/任务识别）
        if _WISDOM_OK:
            try:
                w = _wisdom_chat.chat(
                    self.dex, message, session_id=ctx_key,
                    memory=self._session_ctx,
                    memory_recall_fn=None,
                    prefeed_fn=self._prefeed)
                # 白箱直接回答（非任务）：诚实边界/自省/闲聊/追源/知识
                if w.get("reply"):
                    is_task = w.get("task_reply") and w.get("route") == "llm"
                    # 扮演意图路由：角色扮演场景（有 role_id）且消息含扮演/角色
                    # 类意图时，即使白箱有诚实兜底，也应交给 LLM 扮演回答——
                    # 扮演场景下诚实边界由 LLM 注入的角色机制承载（rp_honest）。
                    wants_rp = rid and _is_roleplay_intent(message)
                    # 自省/自我认知：有角色时交给 LLM 用角色身份回答
                    # （白箱 self_reflexive 是协议灵枢的自省——「我的第一原理是
                    # 存在受到威胁的感知」——不是角色的自省。角色有自己的自我认知，
                    # 如鲸鱼娘的「我是深海来的」应由角色回答）
                    wants_rp = wants_rp or (rid and bool(w.get("self_reflexive")))
                    # 转折结构（turn）：白箱转折模板是通用话术（「我明白你说的…
                    # 帮你查查资料」），角色场景下应由角色回应自我认知/存在类
                    wants_rp = wants_rp or (rid and bool(w.get("turn")))
                    # 通用闲聊暴露身份：白箱 chitchat 回答含「我是灵枢」时
                    # 角色场景下应让角色自我介绍（否则鲸鱼娘说自己是灵枢）
                    leaks_id = rid and bool(w.get("chitchat")) and ("灵枢" in (w.get("reply") or ""))
                    # 通用闲聊话术泄漏（2026-08-19 100 轮测试发现）：
                    # 白箱 chitchat 回答如「不客气！能帮上忙我就开心」「天气好心情
                    # 亮堂」是通用客服话术，无角色特征——角色场景下应让角色用自己的
                    # 视角回应（鲸鱼娘该说「海里的天气可不一样」而非通用话术）。
                    # 判定：回复不含角色特征词（鲸鱼/海/深海/水母等）→ 通用话术
                    _ROLE_HINT = ("鲸鱼", "海", "深海", "水母", "珊瑚", "尾巴",
                                  "章鱼", "海龟", "鱼", "浪", "潮", "蓝")
                    generic_chat = rid and bool(w.get("chitchat")) and not any(
                        h in (w.get("reply") or "") for h in _ROLE_HINT)
                    wants_rp = wants_rp or leaks_id or generic_chat
                    # 白箱记忆路径：白箱说「第一次聊」但角色库有跨会话记忆 →
                    # 交给 LLM（带 mem_notes 召回），避免角色失忆
                    has_role_mem = rid and bool(mem_notes)
                    mem_miss = bool(w.get("memory_reply")) and has_role_mem
                    # 白箱无把握兜底（honest 且无知识命中）→ 交 LLM
                    # （对话界面里白箱是优先判断器，不是最终拦截器）
                    whitebox_no_knowledge = bool(w.get("honest")) and not w.get("hits")
                    # 角色场景：白箱知识/闲聊也交 LLM（角色一致性优先）
                    # （2026-08-19 dex 修复后回归发现：白箱能检索后「你住在哪里呀？」
                    # 「星星真好看。」被白箱当知识直接答——鲸鱼娘突然说动物栖息地/
                    # 激光知识 = 新形式 OOC。角色场景下白箱只做任务识别，
                    # 一切对话由角色用自己的口吻回应（知识也可以角色化讲））
                    role_whitebox = rid and not is_task and bool(w.get("reply"))
                    if is_task or wants_rp or whitebox_no_knowledge or mem_miss \
                            or role_whitebox:
                        pass  # 走 LLM
                    else:
                        # 白箱回答完成：写入会话上下文（按角色隔离）
                        self._session_ctx.setdefault(ctx_key, []).append(message)
                        self._session_ctx[ctx_key].append(w["reply"])
                        w["route"] = "whitebox"
                        w["role_id"] = rid
                        # 输出翻译（虚拟词 → 现实词）：默认保留，开关开启才翻译
                        if os.environ.get("ROLEPLAY_OUT_TRANSLATE") == "1" and rid and self.rp is not None:
                            try:
                                w["reply"] = self.rp.translate_output(rid, w["reply"])
                            except Exception:
                                pass
                        return w
            except Exception:
                pass

        # 2. 任务类 / 白箱未覆盖 → LLM + 角色扮演注入
        role_block = rp_block
        sys_parts = []
        if role_block:
            sys_parts.append(role_block)
        if mem_notes:
            sys_parts.append("相关记忆（灵枢长期记忆召回）：\n" + "\n".join(f"- {m}" for m in mem_notes))
        sys_parts.append(
            "你是灵枢——白箱判定的扮演者。遵循注入的角色设定与诚实边界。"
            "涉及物理事实/能力边界如实声明，不扮演。")
        system = "\n\n".join(sys_parts)

        reply = self._llm(system, message)

        # 3. 写入记忆与上下文（按角色隔离的 ctx_key + role 标签）
        try:
            mem_tags = ["session", "chat", f"sess:{ctx_key}"]
            if rid:
                mem_tags.append(f"role:{rid}")
                # 有角色 → 写入角色持久库（跨会话/跨重启可召回）
                if self.rp is not None:
                    agent = self.rp._agent(rid)
                    agent.remember(
                        f"[对话 {ctx_key}] 用户：{message[:80]}｜灵枢：{reply[:80]}",
                        importance=0.5, tags=mem_tags)
                else:
                    self.mem.remember(
                        f"[对话 {ctx_key}] 用户：{message[:80]}｜灵枢：{reply[:80]}",
                        importance=0.5, tags=mem_tags)
            else:
                self.mem.remember(
                    f"[对话 {ctx_key}] 用户：{message[:80]}｜灵枢：{reply[:80]}",
                    importance=0.5, tags=mem_tags)
        except Exception:
            pass
        self._session_ctx.setdefault(ctx_key, []).append(message)
        self._session_ctx[ctx_key].append(reply)

        # 输出翻译（虚拟词 → 现实词）：默认保留虚拟词（沉浸感），
        # ROLEPLAY_OUT_TRANSLATE=1 时翻译回现实词（用户可理解）
        out_reply = reply
        if os.environ.get("ROLEPLAY_OUT_TRANSLATE") == "1" and rid and self.rp is not None:
            try:
                out_reply = self.rp.translate_output(rid, out_reply)
            except Exception:
                pass

        return {"reply": out_reply, "route": "llm", "role_id": rid,
                "memories": len(mem_notes)}

    def close(self) -> None:
        try:
            self.mem.close()
        except Exception:
            pass
        if self.rp:
            try:
                self.rp.close()
            except Exception:
                pass


def _machine_env(name: str) -> str:
    """从 Machine/User 环境读取 key（会话级 env 可能未加载）。"""
    for scope in ("Machine", "User"):
        try:
            import ctypes
            v = os.environ.get(name)
            if v:
                return v
        except Exception:
            pass
    # 直接读注册表环境（Windows）
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as k:
            v, _ = winreg.QueryValueEx(k, name)
            return v or ""
    except Exception:
        return ""


def _is_roleplay_intent(message: str) -> bool:
    """判断消息是否为角色扮演意图（有 role_id 时，扮演场景交给 LLM）。

    扮演场景关键词：扮演/角色/演/你是什么/你是谁/换个人设/角色扮演/OC。
    注意：不与诚实边界冲突——诚实边界由 LLM 注入的 rp_honest 机制承载
    （「能扮演神吗」→ LLM 回答「不能，这触碰诚实边界」而非白箱直接拦截）。
    """
    words = ["扮演", "角色扮演", "演一个", "演个", "人设", "你是什",
             "你是谁", "换个性", "假装", "cosplay", "oc", "OOC",
             "角色", "戏精", "代入", "你是谁扮演", "你扮演"]
    return any(w in message for w in words)
