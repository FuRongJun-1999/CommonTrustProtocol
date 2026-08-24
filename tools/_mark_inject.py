# -*- coding: utf-8 -*-
"""给域单元库的注入型单元加 needs_inject 标记（verify L2 由集成测试覆盖）"""
import sys, re, io
sys.stdout.reconfigure(encoding='utf-8')

TARGETS = {
    r"D:\Program Files\2_ai\CommonTrustProtocol\tools\compiler_code_units.py": ["编译-类型检查"],
    r"D:\Program Files\2_ai\CommonTrustProtocol\tools\python_code_units.py": ["程序-完整执行"],
    r"D:\Program Files\2_ai\CommonTrustProtocol\tools\graph_db_units.py": [
        "图遍历-BFS", "图遍历-路径", "图遍历-路径枚举", "条件路由图-对接",
        "条件路由图-查询", "图灵枢-导出"],
}

for path, uids in TARGETS.items():
    with io.open(path, encoding="utf-8") as f:
        src = f.read()
    for uid in uids:
        # 定位单元块："uid": { ... "calibration": "..." 之前插入 needs_inject
        marker = f'    "{uid}": {{'
        idx = src.find(marker)
        if idx < 0:
            print(f"✘ 未找到 {uid} in {path}")
            continue
        # 找该块内第一个 "calibration"
        cal_idx = src.find('"calibration"', idx)
        if cal_idx < 0:
            print(f"✘ 无 calibration in {uid}")
            continue
        # 检查是否已有 needs_inject
        block = src[idx:cal_idx]
        if '"needs_inject"' in block:
            print(f"= 已有 needs_inject: {uid}")
            continue
        # 在 "calibration" 行前插入
        line_start = src.rfind("\n", 0, cal_idx) + 1
        src = src[:line_start] + '        "needs_inject": true,\n' + src[line_start:]
        print(f"✔ 标记 {uid} in {path}")
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(src)
print("完成")
