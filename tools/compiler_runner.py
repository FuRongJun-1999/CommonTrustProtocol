# -*- coding: utf-8 -*-
"""compiler_runner.py · T9-2 中文编译器域 token 对照（GLM 端）

荣指令：读 dsh 端 T9-2 计划书，GLM 模型独立实现，与 deepseek 端交叉验证。
计划书：dsh-memory/llm-adapter-poc/token_test/T9-2_编译器域token对比_计划书_v0.1.md

两组 × 5 任务 × ≤5 轮验收循环（compile_source ok + VM run + 结果±0.01）：
  A 裸 LLM：任务描述 + 中文语法提示
  B 灵枢+白箱：递归反思前置（分析调用）+ 白箱单元语义要点注入
    （来源=compiler_code_units 116 单元的 KCCS 注释——按计划书 §五
     「只给语义要点+语法约束，不给完整代码」）
数据记录：每轮 round/tokens/状态/诊断类别/代码全文（二轮修正点④）。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PC = os.path.join(os.path.dirname(ROOT), "protocol-compiler")
sys.path.insert(0, PC)
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))

from core.compiler import compile_source  # noqa: E402
from core.condition_vm import ConditionVM  # noqa: E402
from compiler_code_units import COMPILER_UNITS  # noqa: E402

MAX_ATTEMPTS = 5

# 语法骨架提示（A/B 共有的底线提示——计划书 §五「中文语法提示」）
GRAMMAR_HINT = (
    "中文语法要点：语句以「；」分隔，程序以「止。」结束；赋值用「结果 = 表达式」；"
    "函数定义「定义 名（参数）：…」；条件「若 条件，则 …，否则 …」；"
    "返回用「返回 表达式」；算术「加 减 乘 除」，比较「大于 小于 等于」。"
)

TASKS = [
    {"name": "递归阶乘", "expect": 120.0,
     "task": "用中文编译器实现：定义 阶乘（n）：若 n 小于 2，则 返回 1，否则 返回 n 乘 阶乘（n 减 1）；结果 = 阶乘（5）；止。输出完整中文程序。",
     "unit_keys": ["编译-递归", "编译-函数定义"]},
    {"name": "递归累加", "expect": 15.0,
     "task": "用中文编译器实现：定义 累加（n）：若 n 等于 1，则 返回 1，否则 返回 n 加 累加（n 减 1）；结果 = 累加（5）；止。输出完整中文程序。",
     "unit_keys": ["编译-递归"]},
    {"name": "算术优先级", "expect": 11.0,
     "task": "用中文编译器实现：结果 = 3 加 4 乘 2；止。（乘必须优先于加）输出完整中文程序。",
     "unit_keys": ["编译-赋值"]},
    {"name": "条件判断", "expect": 1.0,
     "task": "用中文编译器实现：若 5 大于 3，则 结果 = 1，否则 结果 = 0；止。输出完整中文程序。",
     "unit_keys": ["编译-若则"]},
    {"name": "双递归斐波那契", "expect": 8.0,
     "task": "用中文编译器实现：定义 斐波那契（n）：若 n 小于 2，则 返回 n，否则 返回 斐波那契（n 减 1）加 斐波那契（n 减 2）；结果 = 斐波那契（6）；止。输出完整中文程序。",
     "unit_keys": ["编译-递归"]},
]

# 白箱单元语义要点（从 KCCS 注释提取——不给完整代码，计划书 §五）
def unit_semantics(unit_keys: list) -> str:
    points = []
    seen = set()
    for k in unit_keys:
        u = COMPILER_UNITS.get(k)
        if not u or k in seen:
            continue
        seen.add(k)
        pat = u["pattern"]
        comments = "\n".join(l.strip() for l in pat.splitlines()
                             if l.strip().startswith("#"))[:400]
        points.append(f"【{k}】{u.get('task', '')} 要点：\n{comments}")
    return ("\n\n白箱知识单元语义要点（遵循其中的规则与约束）：\n" + "\n\n".join(points)) \
        if points else ""


def llm(system: str, question: str) -> tuple[str, dict]:
    key = os.environ.get("BIGMODEL_API_KEY", "")
    if not key:
        raise RuntimeError("BIGMODEL_API_KEY 未设置")
    body = json.dumps({
        "model": "glm-5.3-flash", "temperature": 0, "max_tokens": 2000,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": question}],
    }).encode()
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    u = data.get("usage", {})
    return (data["choices"][0]["message"]["content"] or "",
            {"prompt": u.get("prompt_tokens", 0),
             "completion": u.get("completion_tokens", 0)})


def extract_program(text: str) -> str:
    """从 LLM 输出提取中文程序（代码块或「定义/结果/若」起始段）。"""
    m = re.search(r"```(?:text|python)?\s*(.+?)```", text, re.S)
    if m:
        text = m.group(1)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    prog = [l for l in lines
            if l.startswith(("定义", "结果", "若", "止")) or "；" in l]
    return "\n".join(prog) if prog else text.strip()


def verify(program: str, expect: float) -> tuple[bool, str, str]:
    """验收三关：编译 → 运行 → 结果。返回 (ok, 诊断类别, 详情)。"""
    code, r = compile_source(program, strict=False)
    if not r.get("ok"):
        return False, "编译错", str(r.get("errors"))[:300]
    try:
        vm = ConditionVM()
        vm.run(code)
    except Exception as e:
        return False, "运行错", f"{type(e).__name__}: {e}"
    got = vm.symbols.get("结果")
    if got is None or abs(got - expect) >= 0.01:
        return False, "结果错", f"结果={got!r} 期望={expect!r}"
    return True, "pass", f"结果={got}"


def run_group(group: str, task: dict) -> dict:
    rec = {"name": task["name"], "group": group, "tokens": 0, "rounds": 0,
           "passed": False, "rounds_log": []}
    system = "你只输出程序文本，不要解释。"
    if group == "A":
        q = task["task"] + "\n\n" + GRAMMAR_HINT
    else:
        # B：递归反思前置（分析调用计入 token——机制开销如实统计）
        _a, u = llm("你是灵枢协议实例。递归反思：分析该任务的条件、需要的知识"
                    "与规则（100 字内，不写代码）。\n" + task["task"], "请分析。")
        rec["tokens"] += u["prompt"] + u["completion"]
        q = task["task"] + "\n" + GRAMMAR_HINT + unit_semantics(task["unit_keys"])
    failing = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        qq = q + (f"\n\n上次未通过验收（{failing}），请修正。" if failing else "")
        text, u = llm(system, qq)
        rec["tokens"] += u["prompt"] + u["completion"]
        program = extract_program(text)
        ok, diag_cat, detail = verify(program, task["expect"])
        rec["rounds"] = attempt
        rec["rounds_log"].append({"round": attempt, "ok": ok, "diag": diag_cat,
                                  "detail": detail[:150], "code": program[:200]})
        if ok:
            rec["passed"] = True
            break
        failing = f"{diag_cat}: {detail}"
    return rec


def main() -> int:
    if not os.environ.get("BIGMODEL_API_KEY"):
        print("BIGMODEL_API_KEY 未设置", file=sys.stderr)
        return 1
    report = {"engine": "glm-5.3-flash", "tasks": [],
              "totals": {"A": 0, "B": 0, "A_pass": 0, "B_pass": 0}}
    for task in TASKS:
        ra = run_group("A", task)
        rb = run_group("B", task)
        report["tasks"].append({"A": ra, "B": rb})
        report["totals"]["A"] += ra["tokens"]
        report["totals"]["B"] += rb["tokens"]
        report["totals"]["A_pass"] += ra["passed"]
        report["totals"]["B_pass"] += rb["passed"]
        print(f"[{task['name']}] A={ra['tokens']}({ra['rounds']}轮"
              f"{'✓' if ra['passed'] else '✗'}) B={rb['tokens']}({rb['rounds']}轮"
              f"{'✓' if rb['passed'] else '✗'})")
        json.dump(report, open(os.path.join(HERE, "compiler_bench_report_glm.json"),
                               "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ta, tb = report["totals"]["A"], report["totals"]["B"]
    print(f"\n=== T9-2 GLM 端总账 ===\nA 裸: {ta} tok（过 {report['totals']['A_pass']}/5）"
          f"\nB 灵枢+白箱: {tb} tok（过 {report['totals']['B_pass']}/5）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
