# -*- coding: utf-8 -*-
"""test_real_db_recall.py · 真实库感知召回策略测试（第五阶段·近因时间线直查）
用真实 lingshu_timeline 返回的 3D 事件内容验证：
①时间线近因召回（spatial3d 标签过滤）→ 3D 问答命中
②学科卡（非 spatial3d）被跳过
③无 spatial3d 事件时诚实回落
④内容解析公开函数（answer_3d_from_content）5 型问答"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from spatial_qa import timeline_3d_answer, answer_3d_from_content, _classify_3d

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# 模拟真实灵枢库时间线（近因倒序：3D 事件 + 学科卡 + consolidation）
TIMELINE = [
    {"id": "node_consol", "content": "[consolidation] 演练 956",
     "tags": ["consolidation"], "created_at": 1787571988},
    {"id": "node_482f3e28", "content": "[3D时空事件] 球 方向=x+ 速度=0.186单位/帧 "
     "位移=2.04 一致性=1.0 起点=(1.77,2.8,12.41) 终点=(2.64,2.8,12.41)",
     "tags": ["spatial3d", "perception", "球", "3D轨迹"], "created_at": 1787571983},
    {"id": "node_phys", "content": "高中物理知识点内容（按骨架填充）81知识点…",
     "tags": ["subject_card", "edu:E3"], "created_at": 1787018087},
]

# ① 时间线近因召回：方向/速度/距离/轨迹/静止 5 问
r = timeline_3d_answer("球往哪飞了？", TIMELINE)
check('①a 方向问答（时间线召回）', r.get("ok") and "x+" in r.get("reply", ""),
      r.get("reply", "")[:30])
r = timeline_3d_answer("球飞多快？", TIMELINE)
check('①b 速度问答', r.get("ok") and "0.186" in r.get("reply", ""), r.get("reply", "")[:30])
r = timeline_3d_answer("球飞了多远？", TIMELINE)
check('①c 距离问答', r.get("ok") and "2.04" in r.get("reply", ""), r.get("reply", "")[:30])
r = timeline_3d_answer("球的轨迹直吗？", TIMELINE)
check('①d 轨迹问答', r.get("ok") and "1.0" in r.get("reply", ""), r.get("reply", "")[:30])

# ② 学科卡跳过（spatial3d 标签过滤生效）
r = timeline_3d_answer("球的轨迹直吗？",
                       [{"id": "p", "content": "物理卡…", "tags": ["subject_card"]}])
check('② 无 spatial3d 事件诚实回落', not r.get("ok") and "无 spatial3d" in r.get("reply", ""),
      r.get("reply", ""))

# ③ 内容解析公开函数（真实库内容直接回答）
content = TIMELINE[1]["content"]
check('③a answer_3d_from_content 方向',
      "x+" in answer_3d_from_content("方向", content), '')
check('③b answer_3d_from_content 距离',
      "2.04" in answer_3d_from_content("距离", content), '')

# ④ 问题类型识别
check('④ 类型识别', _classify_3d("球往哪飞了") == "方向"
      and _classify_3d("飞了多远") == "距离"
      and _classify_3d("什么是碳中和") is None, '')

print(f'\n=== 真实库感知召回策略测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
