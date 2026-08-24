# -*- coding: utf-8 -*-
"""spacetime_perception.py · 白箱感知通道进对话（第五阶段·⑤闭环）
3D 时空 CNN × 时空记忆图 成为白箱感知通道——看见→记住→时空问答（零 LLM）：
  ask「刚才那个球怎么动的？」→ 召回时空记忆 → 白箱回答「向右滚动，速度2/帧」
感知不再是孤立的模块——时空记忆自动参与对话（感知→记忆→认知闭环）。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from multimodal_bridge import see_and_remember, recall_event
from stcnn import (synth_ball_rolling, synth_blinking, synth_static,
                   extract_spatiotemporal_primitives)


class SpacetimePerception:
    """白箱感知通道：看见（stcnn）→ 记住（灵枢）→ 时空问答（零 LLM）"""

    def __init__(self, agent):
        self.agent = agent

    def see(self, frames, label):
        """看见→记住：帧序列 → 3D 时空 CNN → 灵枢记忆"""
        return see_and_remember(self.agent, frames, label)

    def ask(self, question):
        """时空问答：问题类型识别 → 召回时空记忆 → 白箱回答
        问题类型：方向/速度/周期/静止/发生了什么"""
        qtype = self._classify_question(question)
        if qtype is None:
            return {"ok": False, "reply": "（非时空问题——不属感知通道）", "type": None}
        # 召回时空事件（spatiotemporal 标签）
        hits = recall_event(self.agent, question, limit=3)
        if not hits:
            return {"ok": False, "reply": "（时空记忆中没有相关事件——还没看见什么）",
                    "type": qtype}
        node, score = hits[0]
        content = node.content or ""
        reply = self._answer_by_type(qtype, content, score)
        return {"ok": True, "reply": reply, "type": qtype,
                "source": content[:60], "score": round(score, 3)}

    def _classify_question(self, q):
        """问题类型识别（白箱确定性关键词）"""
        if any(w in q for w in ("方向", "怎么动", "往哪", "向哪", "移动方向")):
            return "方向"
        if any(w in q for w in ("速度", "多快", "快慢", "每秒")):
            return "速度"
        if any(w in q for w in ("周期", "规律", "间隔", "几次", "频率", "闪烁")):
            return "周期"
        if any(w in q for w in ("静止", "在动", "动了", "动吗", "有没有动")):
            return "静止"
        if any(w in q for w in ("刚才", "发生了什么", "看到什么", "怎么回事")):
            return "事件"
        return None

    def _answer_by_type(self, qtype, content, score):
        """按类型组装白箱回答（从时空记忆内容提取）"""
        if qtype == "方向":
            if "向右" in content:
                return "刚才看到的是向右移动的，速度记录在案。"
            if "向左" in content:
                return "刚才看到的是向左移动的。"
            if "静止" in content:
                return "刚才那个是静止的，没有移动。"
            return f"根据时空记忆：{content[:40]}"
        if qtype == "速度":
            for w in ("速度", "运动量"):
                i = content.find(w)
                if i >= 0:
                    return f"它的{content[max(0, i-6):i+12]}——这是时空 CNN 从帧序列提取的。"
            return "速度记录不明确。"
        if qtype == "周期":
            if "周期" in content:
                i = content.find("周期")
                return f"它有{content[i:i+10]}——周期性规律已从时空记忆图识别。"
            return "没有检测到周期性。"
        if qtype == "静止":
            if "静止" in content:
                return "不，那个是静止的（时空 CNN 检测运动量为 0）。"
            return "不，它在运动（有方向/速度记录）。"
        # 事件
        return f"刚才发生的是：{content[content.find(']')+1:].strip()[:60]}"

    def what_happened(self):
        """综合汇报：全部时空记忆（感知通道的回忆入口）"""
        events = []
        try:
            nodes = self.agent.engine.store.get_nodes_by_tag(
                "spatiotemporal", limit=20)
            for n in nodes:
                events.append((n.content or "")[:70])
        except Exception:
            pass
        return events


if __name__ == "__main__":
    sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\aeis')
    from aeis.api import Agent

    print("=== 白箱感知通道：看见→记住→时空问答（零 LLM） ===\n")
    a = Agent(identity="perception-test", db_path=":memory:")
    p = SpacetimePerception(a)

    # 看见三场景
    p.see(synth_ball_rolling(frames=10, speed_px=2), "球")
    p.see(synth_blinking(frames=12, period=3), "灯")
    p.see(synth_static(frames=6), "背景")

    print("① 看见并记住：球（向右）/ 灯（周期3帧）/ 背景（静止）\n")
    print("② 时空问答（感知通道进对话）：")
    for q in ["刚才那个球怎么动的？", "球的速度是多少？", "灯有什么规律？",
              "背景在动吗？", "刚才都发生了什么？"]:
        r = p.ask(q)
        mark = "✔" if r.get("ok") else "✘"
        print(f"  [{mark}] Q: {q}")
        print(f"     A: {r.get('reply', r.get('reply'))}")
        if r.get("score"):
            print(f"     （召回 score={r['score']}，源: {r['source']}）")

    print("\n③ 回忆入口（what_happened）：")
    for e in p.what_happened():
        print(f"  · {e}")

    # 判定
    ok_all = all(p.ask(q).get("ok") for q in
                 ["刚才那个球怎么动的？", "灯有什么规律？", "背景在动吗？"])
    print(f"\n=== 判定 ===\n时空问答白箱命中: {'✔ 感知通道进入对话（零 LLM）' if ok_all else '✘'}")
