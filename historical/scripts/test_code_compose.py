# -*- coding: utf-8 -*-
"""test_code_compose.py · 代码编写主线测试
验证：①组合生成+自校验（6 任务）②自校验能自发现代码错误（语法/逻辑——故意 bug 单元）
③固化闭环（生成→自校验→固化→直出）④判定统计"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import code_compose as cc

print('=== ① 组合生成 + 自校验（零 LLM） ===')
QS = [
    "写一个函数把数组从小到大排序",
    "写一个函数去掉数组里重复的元素",
    "写一个函数数一数数组里每个元素出现几次",
    "写一个函数找出一组数里的最大值",
    "写一个函数把列表反转",
    "写一个函数把数组加起来求和",
]
ok_cnt = 0
for q in QS:
    r = cc.code_route(q)
    ok = r.get("ok") and r.get("code") is not None
    if ok:
        ok_cnt += 1
    mark = '✓' if ok else '✗'
    print(f'[{mark}] {q} -> {r.get("unit")} | {r["checks"][0] if r.get("checks") else ""}')

print('\n=== ② 自校验自发现错误（故意 bug 单元 → 必须被抓） ===')
# 构造错误单元：排序少一层循环（逻辑错）/ 语法错 / 边界错
BUG_UNITS = {
    "求和-初值错": {
        "task": "求和",
        "pattern": "def solve(arr):\n    total = 1\n    for x in arr:\n        total += x\n    return total\n",
        "cases": [([1, 2, 3], 6), ([5], 5)],   # 初值 1 → 结果多 1 → 逻辑错
        "params": ["fn"],
    },
    "排序-语法错": {
        "task": "排序",
        "pattern": "def solve(arr):\n    n = len(arr\n    return arr\n",
        "cases": [([3, 1, 2], [1, 2, 3])],
        "params": ["fn"],
    },
    "最大-边界错": {
        "task": "最大",
        "pattern": "def solve(arr):\n    m = arr[0]\n    for x in arr:\n        if x > m:\n            m = x\n    return m\n",
        "cases": [([3, 1, 2], 3), ([], None)],   # 空数组应返回 None → 边界错
        "params": ["fn"],
    },
}
catch = 0
for name, unit in BUG_UNITS.items():
    ok, checks = cc.verify_code(unit["pattern"], unit)
    caught = not ok  # 自校验应发现错误
    if caught:
        catch += 1
    mark = '✓抓到' if caught else '✘漏过'
    print(f'[{mark}] {name}: {checks[0] if checks else "未报错!"}')

print('\n=== ③ 固化闭环（生成→自校验→固化→直出） ===')
e = cc.code_solidify("写一个函数把数组从小到大排序")
r2 = cc.code_route("写一个函数把数组从小到大排序")
solid = e is not None and r2.get("solidified") is True
print(f'固化+直出: {"✓" if solid else "✗"}（固化 {e is not None} / 再问直出 {r2.get("solidified")}）')

print('\n=== ④ 判定 ===')
print(f'组合生成测试通过率: {ok_cnt}/{len(QS)} = {ok_cnt/len(QS)*100:.0f}%（目标≥80%）')
print(f'自校验自发现错误率: {catch}/{len(BUG_UNITS)} = {catch/len(BUG_UNITS)*100:.0f}%（目标100%）')
print(f'固化闭环: {"✓ 成立" if solid else "✗ 未成立"}')
