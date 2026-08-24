#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_whitebox_final.py · 白箱终裁综合验证（判定④⑤：白箱终裁占比 ≥90%）
综合统计白箱全链路：知识查询 / 角色扮演 / 代码编写 / 感知（时空问答）——
全部零 LLM 白箱终裁；LLM 仅外部对照（对照一致率验证）。
"""
import os, sys
sys.stdout.reconfigure(encoding='utf-8')
CTP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, CTP)
sys.path.insert(0, os.path.join(CTP, 'aeis'))
sys.path.insert(0, os.path.join(CTP, 'tools'))
import compose_engine as ce
import role_compose as rc
import code_compose as cc
from spacetime_perception import SpacetimePerception
from stcnn import synth_ball_rolling, synth_blinking
from aeis.api import Agent

PASS = 0
TOTAL = 0
def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
    print(f'[{"✓" if cond else "✘"}] {name}{" — " + detail if detail else ""}')

# ============ ① 知识查询（组合引擎·零 LLM） ============
KNOWLEDGE_QS = [
    "为什么高原上煮饭不容易熟？", "为什么保温杯里的热水放很久还是热的？",
    "为什么植物要放在有阳光的地方？", "为什么有白天和黑夜？",
    "为什么饿了要吃饭？", "为什么真空瓶里煮饭也煮不熟？",
    "为什么铁块会沉入水底？", "为什么大雁秋天往南飞？",
]
k_ok = sum(1 for q in KNOWLEDGE_QS if ce.route_compose(q).get("ok"))
check(f'① 知识查询白箱终裁: {k_ok}/{len(KNOWLEDGE_QS)}（零 LLM）',
      k_ok / len(KNOWLEDGE_QS) >= 0.8)

# ============ ② 角色扮演（零 LLM） ============
ROLE_QS = ["你是谁？", "你住在哪里？", "你吃什么？", "你有尾巴吗？",
           "你是人类吗？"]
r_ok = sum(1 for q in ROLE_QS if rc.role_route(q, "鲸鱼娘").get("ok"))
check(f'② 角色扮演白箱终裁: {r_ok}/{len(ROLE_QS)}（零 LLM）',
      r_ok / len(ROLE_QS) >= 0.8)

# ============ ③ 代码编写（零 LLM + 语法/样例自校验） ============
CODE_QS = ["写一个函数把数组从小到大排序", "写一个函数去掉数组里重复的元素",
           "写一个函数把数组加起来求和"]
c_ok = sum(1 for q in CODE_QS if cc.code_route(q).get("ok"))
check(f'③ 代码编写白箱终裁: {c_ok}/{len(CODE_QS)}（零 LLM）',
      c_ok / len(CODE_QS) >= 0.8)

# ============ ④ 感知（时空问答·零 LLM） ============
agent = Agent(identity="final", db_path=":memory:")
p = SpacetimePerception(agent)
p.see(synth_ball_rolling(frames=10, speed_px=2), "球")
p.see(synth_blinking(frames=12, period=3), "灯")
PERC_QS = ["刚才那个球怎么动的？", "灯有什么规律？"]
s_ok = sum(1 for q in PERC_QS if p.ask(q).get("ok"))
check(f'④ 感知白箱终裁: {s_ok}/{len(PERC_QS)}（零 LLM）',
      s_ok / len(PERC_QS) >= 0.8)

# ============ ⑤ 综合白箱终裁占比（判定④：≥90%） ============
all_whitebox = k_ok + r_ok + c_ok + s_ok
all_total = len(KNOWLEDGE_QS) + len(ROLE_QS) + len(CODE_QS) + len(PERC_QS)
rate = all_whitebox / all_total
check(f'⑤ 综合白箱终裁占比: {all_whitebox}/{all_total} = {rate*100:.1f}%'
      f'（目标 ≥90%，LLM 仅外部对照）', rate >= 0.9)

print(f"\n=== 白箱终裁综合验证: {PASS}/{TOTAL} 通过 ===")
print("白箱全链路：知识查询 + 角色扮演 + 代码编写 + 感知（时空问答）——"
      "全部零 LLM 白箱终裁，LLM 仅外部对照")
sys.exit(0 if PASS == TOTAL else 1)
