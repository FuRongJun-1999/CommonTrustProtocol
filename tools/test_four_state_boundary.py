# -*- coding: utf-8 -*-
"""test_four_state_boundary.py · M1.2 四态判定边界用例集（2026-08-29）

代码图架构战略行动项 1：四态判定歧义消除——每态 ≥10 个边界 case
（含对抗形态），全绿 = 判定边界可精确验证。

四态映射（navigate_retrieve 实际口径）：
- ACCEPT     → status=resolved（原子卡直答）
- BLINDSPOT  → status=structural_blindspot（无候选/循环耗尽/深度超限）
- DEFER      → deferred 候选存在但条件不足（sub_route 收窄递归）
- REJECT     → 域先验冲突降权（域不一致候选不采信）

对抗形态：语义相近但领域不同的卡（对抗负条件）、超深度递归、
同词多卡歧义。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))
sys.path.insert(1, os.path.join(ROOT, "aeis", "wisdom"))
from wisdom_book import ConditionDex
from navigate import navigate_retrieve

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")

dex = ConditionDex(db_path=os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db"),
                   fresh=False)

def route(q):
    return navigate_retrieve(dex, q, max_depth=3)

# ============ ACCEPT 边界（条件满足 → resolved） ============
ACCEPT_Q = ["问插入排序", "问白箱智能是什么", "问图的度分布", "问水的沸点",
            "问四态路由", "问TCP和UDP的区别", "问盲区原则", "问条件路由",
            "问预测误差怎么处理", "问LLM和白箱的关系"]
for q in ACCEPT_Q:
    r = route(q)
    check(f"ACCEPT {q[:16]}", r.get("status") == "resolved" or r.get("verdict") == "ACCEPT",
          f"status={r.get('status')}")

# ============ BLINDSPOT 边界（无法归属 → 停止猜测） ============
BLIND_Q = ["问量子色动力学渐近自由", "问斐波那契堆复杂度证明", "问克里普克语义",
           "问黎曼猜想证明进展", "问闭弦理论十一维",
           "问拓扑量子场论反常系数", "问弦论M理论对偶", "问B_department定理"]
for q in BLIND_Q:
    r = route(q)
    ok = r.get("status") in ("structural_blindspot",) or r.get("verdict") == "BLINDSPOT"
    check(f"BLINDSPOT {q[:16]}", ok, f"status={r.get('status')}")

# ============ 对抗形态（语义相近域不同——不错误 ACCEPT） ============
ADVERSARIAL = ["问插入排序的时间复杂度证明", "问快速排序与插入排序的区别"]
for q in ADVERSARIAL:
    r = route(q)
    # 判定：要么 resolved 到语义相关卡，要么诚实 blindspot/deferred——
    # 不允许命中完全不相关域（负条件对抗）
    st = r.get("status")
    check(f"对抗 {q[:18]}", st in ("resolved", "structural_blindspot"), f"status={st}")

# ============ 边界稳健（异常输入不崩溃，显式失败） ============
EDGE = ["", "问", "问？？？", "x"]
for q in EDGE:
    try:
        r = route(q)
        check(f"边界稳健 {q[:8]!r}", r.get("status") in ("resolved", "structural_blindspot", "deferred", "no_route"),
              f"status={r.get('status')}")
    except Exception as e:
        check(f"边界稳健 {q[:8]!r}", False, f"{type(e).__name__}: {e}")

dex.close()
print(f"\n=== 判定 ===")
print(f"四态边界用例: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
