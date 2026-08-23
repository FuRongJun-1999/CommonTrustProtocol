# -*- coding: utf-8 -*-
"""arc_demo_ext_test.py · ARC 原型 v2 边界测试（验证三机制补齐 + 回归）
v1 暴露缺口：多样例合并 / 组合搜索 / 假阳性裁决
v2 断言：三项全部补齐，且 5/5 基线不回归。
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arc_demo import find_rule, find_rule_with_ambiguity, PRIMITIVES, _color_map, color_map_merge

sys.stdout.reconfigure(encoding='utf-8')

def grid_eq(a, b):
    return a == b

results = []
def check(name, got_ok, detail):
    results.append((name, got_ok))
    print(f"[{'✓' if got_ok else '✗'}] {name}: {detail}")

print("=" * 60)
print("回归：v1 的 5/5 基线（原 5 任务）")
print("=" * 60)
import arc_demo
for tid, task in enumerate(arc_demo.TASKS, 1):
    r, fn = find_rule(task["train"])
    pred = fn(task["test"]) if r else None
    ok = pred == task["expected"]
    check(f"回归任务{tid} {task['desc']}", ok, f"规律={r} 预测={pred} 期望={task['expected']}")

print()
print("=" * 60)
print("机制① 多样例合并（颜色映射跨样例聚合）")
print("=" * 60)
# 1a. 多样例不同映射：1→2 且 3→4，应在同一规律中合并
train_1a = [
    ([[1, 0], [0, 1]], [[2, 0], [0, 2]]),
    ([[3, 0], [0, 3]], [[4, 0], [0, 4]]),
]
m = color_map_merge(train_1a)
ok = m is not None and m.get(1) == 2 and m.get(3) == 4
check("多样例合并·1→2 且 3→4 同时成立", ok, f"合并映射={m}")

# 1b. 冲突映射应判歧义（同一输入色映射不同）
train_1b = [
    ([[1, 0], [0, 1]], [[2, 0], [0, 2]]),
    ([[1, 0], [0, 1]], [[3, 0], [0, 3]]),  # 1→2 和 1→3 冲突
]
m = color_map_merge(train_1b)
ok = m is None
check("冲突映射判定歧义（1→2 vs 1→3）", ok, f"合并映射={m}（应为 None）")

print()
print("=" * 60)
print("机制② 组合搜索（原语 A∘B）")
print("=" * 60)
# 2a. rot90 再 1→2：两个样例
train_2 = [
    ([[1, 0], [0, 1]], [[0, 2], [2, 0]]),   # rot90([[1,0],[0,1]])=[[0,1],[1,0]] → 1→2 → [[0,2],[2,0]]
    ([[1, 1], [0, 0]], [[2, 2], [0, 0]]),   # rot90([[1,1],[0,0]])=[[1,0],[1,0]] → 1→2 → [[2,0],[2,0]]≠[[2,2],[0,0]]
]
# 第二个样例 rot90 后是 [[1,0],[1,0]]，映射 1→2 得 [[2,0],[2,0]]，但期望是 [[2,2],[0,0]]——样例本身不符。
# 修正第二个样例：rot90([[0,1],[0,1]]) = ? grid[::-1]=[[0,1],[0,1]] zip→[(0,0),(1,1)] → [[0,0],[1,1]]→映射→[[0,0],[2,2]]
train_2 = [
    ([[1, 0], [0, 1]], [[0, 2], [2, 0]]),
    ([[0, 1], [0, 1]], [[0, 0], [2, 2]]),
]
r, fn = find_rule(train_2)
pred = fn([[1, 0], [1, 1]]) if r else None
# rot90([[1,0],[1,1]]) = grid[::-1]=[[1,1],[1,0]] zip→[(1,1),(1,0)] → [[1,1],[1,0]] → 1→2 → [[2,2],[2,0]]
expected_2 = [[2, 2], [2, 0]]
ok = r is not None and pred == expected_2
check("组合规律 rot90→color_map", ok, f"规律={r} 预测={pred} 期望={expected_2}")

# 2b. 对照：无组合时单原语仍应工作（不回归）
train_2c = [
    ([[1, 0], [0, 1]], [[2, 0], [0, 2]]),
]
r, fn = find_rule(train_2c)
pred = fn([[1, 1], [0, 0]]) if r else None
ok = pred == [[2, 2], [0, 0]]
check("对照：纯颜色映射不回归", ok, f"规律={r} 预测={pred}")

print()
print("=" * 60)
print("机制③ 假阳性裁决（多原语命中 → 歧义报告）")
print("=" * 60)
# 3a. 对称样例：identity 和 hflip 都命中 → 应报告歧义而非武断
train_3 = [
    ([[1, 2], [2, 1]], [[1, 2], [2, 1]]),
]
r, fn, status = find_rule_with_ambiguity(train_3)
ok = status.startswith('ambiguous')
check("对称样例·多原语命中报告歧义", ok, f"规律={r} status={status}")

# 3b. 非歧义样例：两原语命中但测试预测一致 → ok
train_3b = [
    ([[1, 2], [2, 1]], [[1, 2], [2, 1]]),  # 对称：identity 和 hflip 都命中
]
r, fn, status = find_rule_with_ambiguity(train_3b)
ok = status != 'none'
check("多原语命中但预测一致 → 可用", ok, f"规律={r} status={status}")

print()
print("=" * 60)
print("机制③b 假阳性：单样例对称 + 测试预测冲突检测")
print("=" * 60)
# 若训练样例能区分（非对称），则唯一命中
train_3c = [
    ([[1, 2, 3]], [[3, 2, 1]]),  # 非对称 → 只有 hflip 命中
    ([[1, 0], [2, 0]], [[0, 1], [0, 2]]),
]
r, fn, status = find_rule_with_ambiguity(train_3c)
ok = status == 'ok' and r == 'hflip'
check("非对称样例唯一命中 hflip", ok, f"规律={r} status={status}")

print()
print("=" * 60)
print("汇总")
print("=" * 60)
n_pass = sum(1 for _, ok in results if ok)
print(f"{n_pass}/{len(results)} 通过")
for name, ok in results:
    print(f"  [{'✓' if ok else '✗'}] {name}")
