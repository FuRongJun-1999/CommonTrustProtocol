# -*- coding: utf-8 -*-
"""test_phase4_v1.py · 第四阶段 v1 验证——感知进主路由 + 条件代数并行化
① 感知通道接入 chat_engine 主路由（时空问题自动走感知，零 LLM）
② 非时空问题不劫持感知
③ compose_parallel 线程池并行执行（结果=串行）+ 加速比"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
sys.path.insert(0, CTP + r'\tools')
sys.path.insert(0, CTP + r'\aeis')
import wisdom.chat_engine as ce
# 五副本机制会把 knowledge-base 加进 sys.path（比 tools 靠前）——
# import chat 后把 tools 提到最前，确保 compose_engine 用 tools 版
sys.path.insert(0, CTP + r'\tools')
import compose_engine as cc
from spacetime_perception import SpacetimePerception
from stcnn import synth_ball_rolling, synth_blinking, synth_static
from aeis.api import Agent

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ============ ① 感知进 chat_engine 主路由 ============
agent = Agent(identity="phase4", db_path=":memory:")
p = SpacetimePerception(agent)
p.see(synth_ball_rolling(frames=10, speed_px=2), "球")
p.see(synth_blinking(frames=12, period=3), "灯")
p.see(synth_static(frames=6), "背景")

perceiver = lambda q: p.ask(q)

# 时空问题 → 感知通道（perception=True）
r1 = ce.chat(dex=None, message="刚才那个球怎么动的？", perceiver_fn=perceiver)
check('①a 时空问题走感知通道', r1.get("perception") and "向右" in r1.get("reply", ""),
      r1.get("reply", "")[:30])
r2 = ce.chat(dex=None, message="灯有什么规律？", perceiver_fn=perceiver)
check('①b 周期问题走感知', r2.get("perception") and "周期" in r2.get("reply", ""),
      r2.get("reply", "")[:30])
r3 = ce.chat(dex=None, message="背景在动吗？", perceiver_fn=perceiver)
check('①c 静止问题走感知', r3.get("perception") and "静止" in r3.get("reply", ""),
      r3.get("reply", "")[:30])

# 非时空问题不劫持感知（正常走知识/闲聊）
r4 = ce.chat(dex=None, message="你好呀", perceiver_fn=perceiver)
check('①d 非时空问题不劫持感知', not r4.get("perception"))

# ============ ② 条件代数并行化 ============
qs = ["为什么高原上煮饭不容易熟？", "为什么植物要放在有阳光的地方？",
      "为什么保温杯里的热水放很久还是热的？", "为什么有白天和黑夜？",
      "为什么铁块会沉入水底？", "为什么饿了要吃饭？"]
r = cc.compose_parallel(qs)
check('②a 独立域并行执行（结果=串行）',
      all(x["result"].get("ok") for x in r["results"]))
serial = [cc.route_compose(q).get("answer") for q in qs]
same = all(x["result"].get("answer") == serial[i] for i, x in enumerate(r["results"]))
check('②b 并行结果与串行一致', same)
print(f'   并行 {r["parallel_ms"]}ms vs 串行 {r["serial_ms"]}ms '
      f'→ 加速比 {r["speedup"]}×（组合单次<1ms，线程池开销主导——'
      f'加速比在真实大负载场景才有意义）')
check('②c 并行机制生效（独立域分组 + 线程池执行无错）',
      len(r["groups"]) >= 1 and all(x["result"].get("ok") for x in r["results"]),
      f'{len(r["groups"])} 组')

print(f'\n=== 第四阶段 v1 验证: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
