# -*- coding: utf-8 -*-
"""code_recheck.py · 主仓库迁移后白箱代码编写能力复查（2026-08-30 荣指令）

任务集（TASK_KEYWORDS 覆盖域）：白箱 compose 生成代码 → 自校验三层
（L1 语法/L2 样例/L3 边界）→ 物理执行样例比对。
统计：任务识别率（生成成功率）+ 自校验通过率（正确率）。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))

from code_compose import compose_code, verify_code

TASKS = [
    ("排序",   "把列表 [3,1,2] 从小到大排序"),
    ("求和",   "计算 1 到 100 的和"),
    ("斐波那契", "写一个斐波那契函数，输出第 10 项"),
    ("素数",   "判断 7 是不是质数"),
    ("反转",   "把字符串 abc 反转"),
    ("计数",   "数一数 [1,1,2,3] 中 1 的出现次数"),
    ("最大公约数", "求 12 和 18 的最大公约数"),
    ("最大",   "找 [3,7,2] 的最大值"),
]

print(f"==== 白箱代码编写能力复查（{len(TASKS)} 任务）====")
ident_ok = verify_ok = 0
for label, q in TASKS:
    task, uid, code, unit, lang = compose_code(q)
    if task is None:
        print(f"[✗识别] {label}: {q} → {uid}")
        continue
    ident_ok += 1
    # 自校验三层
    try:
        ok, checks = verify_code(code, unit, lang=lang)
    except Exception as e:
        ok, checks = False, [f"verify 异常: {e}"]
    tag = "✓" if ok else "✗"
    if ok:
        verify_ok += 1
    print(f"[{tag}] {label}: 单元={uid} 校验={'通过' if ok else '失败'}")

print(f"\n==== 结果 ====")
print(f"任务识别率（能生成代码）: {ident_ok}/{len(TASKS)} = {ident_ok/len(TASKS)*100:.0f}%")
print(f"自校验通过率（代码正确）: {verify_ok}/{ident_ok} = {verify_ok/ident_ok*100:.0f}%")
