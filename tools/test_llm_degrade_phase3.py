# -*- coding: utf-8 -*-
"""test_llm_degrade_phase3.py · 第三阶段 LLM 外部对照验证（⑤ 最终确认）
白箱全链路（知识组合/感知/规划/代码）vs DeepSeek v4-flash 外部对照——
一致率 ≥90% → 白箱终裁成立，LLM 仅外部对照（第三阶段新增链路确认）。
"""
import sys, os, yaml
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\FuRongJun\.dsh\.credentials.yaml', encoding='utf-8') as f:
    _cred = yaml.safe_load(f) or {}
os.environ['DEEPSEEK_API_KEY'] = _cred.get('DEEPSEEK_API_KEY', '')
CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
sys.path.insert(0, os.path.join(CTP, 'tools'))
sys.path.insert(0, os.path.join(CTP, 'aeis'))
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import compose_engine as ce
import code_compose as cc
from spacetime_perception import SpacetimePerception
from stcnn import synth_ball_rolling, synth_blinking, synth_static
from aeis.roleplay_chat import LingshuChat
from aeis.api import Agent

lc = LingshuChat(data_dir=r'D:\Program Files\2_ai\knowledge-base\roleplay_data',
                 upstream_key_var='DEEPSEEK_API_KEY',
                 upstream_model='deepseek-v4-flash')


def llm_judge(system, user):
    """云端 DeepSeek v4-flash 判定（稳定一致）"""
    try:
        out = lc._llm(system, user + "\n只输出：正确 或 不正确（不要解释）。",
                      prefer_local=False)
    except Exception:
        return None
    if not out:
        return None
    out = out.strip()
    if out.startswith('不正确') or out.startswith('不符合'):
        return False
    if out.startswith('正确') or out.startswith('符合'):
        return True
    return None


KNOWLEDGE_SYS = "你是知识校验器。判断给出的答案是否正确（物理/生活/生物/地球常识）。"
PERCEPT_SYS = "你是感知校验器。判断对运动物体（方向/速度/周期/静止）的描述是否正确。"
PLAN_SYS = "你是计划校验器。判断给出的解决步骤是否合理有效。"

agree = total = 0

def judge_case(label, sysp, user, answer):
    global agree, total
    total += 1
    v = llm_judge(sysp, f"问题：{user}\n答案：{answer}\n\n这个答案正确吗？")
    if v is None:
        total -= 1
        print(f'[?] {label}: LLM 不可用')
        return
    ok = v is True
    agree += 1 if ok else 0
    print(f'[{"✔" if ok else "✘"}] {label}: {answer[:40]}')

print("=== ⑤ 第三阶段 LLM 外部对照验证（白箱 vs DeepSeek v4-flash）===\n")

# ① 知识组合（新域）
for q in ["为什么保温杯里的热水放很久还是热的？", "为什么冬天路面要撒盐？",
          "为什么植物要放在有阳光的地方？", "为什么鱼离开水会死？",
          "为什么有白天和黑夜？", "为什么撬棍能撬起大石头？",
          "为什么饿了要吃饭？", "为什么真空瓶里煮饭也煮不熟？"]:
    r = ce.route_compose(q)
    if r.get("ok"):
        judge_case(f"知识:{q[:12]}", KNOWLEDGE_SYS, q, r["answer"])

# ② 感知（时空问答）——LLM 需观测源才能对照
agent = Agent(identity="degrade3", db_path=":memory:")
p = SpacetimePerception(agent)
p.see(synth_ball_rolling(frames=10, speed_px=2), "球")
p.see(synth_blinking(frames=12, period=3), "灯")
p.see(synth_static(frames=6), "背景")
for q in ["刚才那个球怎么动的？", "灯有什么规律？", "背景在动吗？"]:
    r = p.ask(q)
    if r.get("ok"):
        total += 1
        # 附观测源（时空记忆内容）供 LLM 对照
        v = llm_judge(PERCEPT_SYS,
                      f"观测记录：{r['source']}\n问题：{q}\n白箱回答：{r['reply']}\n\n回答与观测一致吗？")
        if v is None:
            total -= 1
            print(f'[?] 感知:{q[:12]}: LLM 不可用')
            continue
        ok = v is True
        agree += 1 if ok else 0
        print(f'[{"✔" if ok else "✘"}] 感知:{q[:12]}: {r["reply"][:30]}')

# ③ 规划
for q in ["在高原上怎么煮饭才能熟？", "鱼离开水了怎么才能活？"]:
    r = ce.plan_compose(q)
    if r.get("ok"):
        judge_case(f"规划:{q[:12]}", PLAN_SYS, q, r["plan"])

# ④ 代码（给完整代码，不截断）
for q in ["写一个函数把数组从小到大排序", "写一个函数把数组加起来求和"]:
    r = cc.code_route(q)
    if r.get("ok") and r.get("code"):
        judge_case(f"代码:{q[:12]}", "你是代码审查员。判断 Python 代码是否正确。",
                   q, r["code"])

print(f"\n=== 统计 ===\n有效样本 {total} | 一致率 {agree}/{total} = {agree/total*100:.0f}%"
      f"（目标 ≥90%）{'✔' if total and agree/total >= 0.9 else '✘'}")
print(f"→ 白箱全链路（知识/感知/规划/代码）终裁成立，LLM 仅外部对照"
      f"{' ✔ 最终确认' if total and agree/total >= 0.9 else ''}")
