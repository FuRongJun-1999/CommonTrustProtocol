# -*- coding: utf-8 -*-
"""verify_drafts_t5.py · T5 通道 B 白箱裁决（外部校准·确定性）

流程（自举任务书 T5）：初稿（Flash=主智能体 / DeepSeek=子智能体）
→ L1 语法（ast.parse）→ L2 样例（规格用例物理执行断言）
→ 通过固化 channel_b_verified_units.json；拒绝写 rejected_log.json 留痕。
LLM 不参与裁决——物理用例结果即终审。
"""
import ast
import hashlib
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
DRAFTS = os.path.join(HERE, "channel_b_drafts")
VERIFIED = os.path.join(HERE, "channel_b_verified_units.json")
REJECTED = os.path.join(HERE, "channel_b_drafts", "rejected_log.json")

# 规格用例（外部校准基准，与 SPEC 一一对应；异常用例以 raises 标记）
CASES = {
    "mini_aug_apply": [
        {"inp": [1, "+=", 2], "exp": 3},
        {"inp": [10, "-=", 4], "exp": 6},
        {"inp": [3, "*=", 5], "exp": 15},
        {"inp": [10, "/=", 4], "exp": 2.5},
        {"inp": ["a", "+=", "b"], "exp": "ab"},
        {"inp": [10, "/=", 0], "raises": "division by zero"},
        {"inp": [1, "**=", 2], "raises": "unknown op"},
    ],
    "mini_split": [
        {"inp": ["a,b,c", ","], "exp": ["a", "b", "c"]},
        {"inp": ["a,,b", ","], "exp": ["a", "", "b"]},
        {"inp": ["", ","], "exp": [""]},
        {"inp": ["abc", ","], "exp": ["abc"]},
        {"inp": ["a;b;c", ";"], "exp": ["a", "b", "c"]},
    ],
}

DRAFT_TASKS = {
    "draft_flash_aug.py": ("mini_aug_apply", "T5复合赋值执行器（Flash主通道初稿）"),
    "draft_deepseek_aug.py": ("mini_aug_apply", "T5复合赋值执行器（DeepSeek子通道初稿）"),
    "draft_flash_split.py": ("mini_split", "T5字符串切分实现（Flash主通道初稿）"),
    "draft_deepseek_split.py": ("mini_split", "T5字符串切分实现（DeepSeek子通道初稿）"),
}


def run_case(fn, case):
    """单用例物理执行：返回 (True, None) 或 (False, 原因)。"""
    try:
        got = fn(*case["inp"])
    except Exception as e:
        if "raises" in case:
            return (case["raises"] in str(e), None)
        return (False, f"异常 {type(e).__name__}: {e}")
    if "raises" in case:
        return (False, f"应抛 {case['raises']} 却返回 {got!r}")
    return (got == case["exp"], None) if got == case["exp"] else \
        (False, f"返回 {got!r} 期望 {case['exp']!r}")


def main():
    verified = json.load(open(VERIFIED, encoding="utf-8")) \
        if os.path.exists(VERIFIED) else {}
    rejected = json.load(open(REJECTED, encoding="utf-8")) \
        if os.path.exists(REJECTED) else []
    table = []
    for fname, (fn_name, task_desc) in DRAFT_TASKS.items():
        path = os.path.join(DRAFTS, fname)
        entry = {"draft": fname, "fn": fn_name, "channel": task_desc}
        if not os.path.exists(path):
            entry["result"] = "缺失"
            table.append(entry)
            continue
        src = open(path, encoding="utf-8").read()
        # L1 语法
        try:
            ast.parse(src)
        except SyntaxError as e:
            entry["result"] = "L1 拒绝"
            entry["why"] = str(e)[:80]
            rejected.append({"draft": fname, "layer": "L1", "why": str(e)[:120],
                             "ts": time.strftime("%Y-%m-%d %H:%M")})
            table.append(entry)
            continue
        # L2 样例（物理执行）
        ns = {}
        exec(compile(src, fname, "exec"), ns)
        fn = ns.get(fn_name)
        if not callable(fn):
            entry["result"] = "L2 拒绝（函数缺失）"
            rejected.append({"draft": fname, "layer": "L2", "why": f"{fn_name} 不存在",
                             "ts": time.strftime("%Y-%m-%d %H:%M")})
            table.append(entry)
            continue
        all_ok = True
        for case in CASES[fn_name]:
            ok, why = run_case(fn, case)
            if not ok:
                entry["result"] = "L2 拒绝"
                entry["why"] = f"inp={case['inp']}: {why}"
                all_ok = False
                break
        if not all_ok:
            rejected.append({"draft": fname, "layer": "L2", "why": entry.get("why", ""),
                             "ts": time.strftime("%Y-%m-%d %H:%M")})
            table.append(entry)
            continue
        # 固化（指纹去重：同 task 同指纹不重复入库）
        key = "task:" + task_desc
        fp = hashlib.sha256(src.encode()).hexdigest()[:16]
        if key in verified and verified[key].get("fingerprint") == fp:
            entry["result"] = "已固化（指纹相同）"
        else:
            verified[key] = {"task": task_desc, "code": src, "ok": True,
                             "fingerprint": fp, "channel": task_desc.split("（")[1].rstrip("）"),
                             "ts": time.strftime("%Y-%m-%d %H:%M")}
            entry["result"] = f"固化 ✓ fp={fp}"
        table.append(entry)

    json.dump(verified, open(VERIFIED, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    json.dump(rejected, open(REJECTED, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("=== T5 白箱裁决表 ===")
    for e in table:
        line = f"[{e['result']}] {e['draft']}"
        if "why" in e:
            line += f" — {e['why']}"
        print(line)
    n_ok = sum(1 for e in table if "固化" in e["result"])
    print(f"\n判定: {n_ok}/{len(table)} 固化，"
          f"拒绝 {len([e for e in table if '拒绝' in e['result']])}（已留痕）")


if __name__ == "__main__":
    main()
