# -*- coding: utf-8 -*-
"""test_graph_qa_in_chat.py · 条件图数据库问答进 chat_engine 主路由（第六阶段）
验证：①图问题自动走图查询通道（graph_qa=True）②非图问题不劫持 ③无 graph_qa_fn 正常"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
sys.path.insert(0, CTP + r'\aeis\wisdom')
sys.path.insert(0, CTP + r'\aeis')
import wisdom.chat_engine as ce
import compose_engine as cc
from graph_qa import ConditionGraphQA

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

qa = ConditionGraphQA(cc.CONDITION_UNITS)
gqa_fn = lambda q: qa.ask(q)

# ① 图问题自动走图查询通道
r1 = ce.chat(dex=None, message="气压会影响哪些规律？", graph_qa_fn=gqa_fn)
check('①a 影响面走图通道', r1.get("graph_qa") and "沸点-气压" in r1.get("reply", ""),
      r1.get("reply", "")[:36])
r2 = ce.chat(dex=None, message="气压 和 沸点-气压 有关系吗？", graph_qa_fn=gqa_fn)
check('①b 关系查询走图通道', r2.get("graph_qa") and "有关联" in r2.get("reply", ""),
      r2.get("reply", "")[:36])
r3 = ce.chat(dex=None, message="从 气压 到 沸点-气压 怎么走？", graph_qa_fn=gqa_fn)
check('①c 路径查询走图通道', r3.get("graph_qa") and "路径" in r3.get("reply", ""),
      r3.get("reply", "")[:36])

# ② 非图问题不劫持
r4 = ce.chat(dex=None, message="你好呀", graph_qa_fn=gqa_fn)
check('② 非图问题不劫持', not r4.get("graph_qa"))

# ③ 无 graph_qa_fn 正常流程
r5 = ce.chat(dex=None, message="气压会影响哪些规律？")
check('③ 无 graph_qa_fn 正常流程', not r5.get("graph_qa") and r5.get("reply", ""),
      r5.get("reply", "")[:24])

print(f'\n=== 条件图数据库进主路由测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
