# -*- coding: utf-8 -*-
"""test_graph_qa.py · 条件图数据库问答测试（第六阶段·目标6 图查询进对话）
验证：①影响面查询 ②关系查询（路径存在）③路径枚举 ④未识别回落 ⑤诚实边界"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import compose_engine as ce
from graph_qa import ConditionGraphQA

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

qa = ConditionGraphQA(ce.CONDITION_UNITS)

# ① 影响面查询（真实 43 单元图）
r = qa.ask("气压会影响哪些规律？")
check('① 影响面含沸点-气压', r.get("ok") and "沸点-气压" in r.get("reply", ""),
      r.get("reply", "")[:40])
r = qa.ask("光照会影响哪些规律？")
check('①b 光照影响面', r.get("ok") and "光合-光照" in r.get("reply", ""),
      r.get("reply", "")[:40])

# ② 关系查询（路径存在，双向）
r = qa.ask("气压 和 沸点-气压 有关系吗？")
check('②a 路径存在', r.get("ok") and "有关联" in r.get("reply", ""), r.get("reply", "")[:30])
r = qa.ask("沸点-气压 和 气压 有关系吗？")
check('②b 双向关联（反向也有关）', r.get("ok") and "有关联" in r.get("reply", ""),
      r.get("reply", "")[:30])

# ③ 路径枚举
r = qa.ask("从 气压 到 沸点-气压 怎么走？")
check('③ 路径枚举', r.get("ok") and "气压" in r.get("reply", "")
      and "沸点-气压" in r.get("reply", ""), r.get("reply", "")[:50])

# ④ 非图问题回落
r = qa.ask("什么是碳中和？")
check('④ 非图问题回落', not r.get("ok") and r.get("type") is None, r.get("reply", "")[:20])

# ⑤ 诚实边界（未识别名字）
r = qa.ask("量子态会影响哪些规律？")
check('⑤ 未识别名字回落', not r.get("ok") and "未识别" in r.get("reply", ""),
      r.get("reply", "")[:24])

print(f'\n=== 条件图数据库问答测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
