# -*- coding: utf-8 -*-
"""t10_project_bench.py · T10 复杂任务场景 token 对照（灵枢主场）

计划书：docs/T10_复杂任务场景token对照_计划书_v0.1.md
A 组灵枢全管线 v2：递归反思分析 + declaration 声明 + 规范型卡执行字段
（层级对齐——T10 预置卡为规范型，不触发诱导）；B 组裸提示词。
MAX_ATTEMPTS=8（深迭代）。P4 为中文编译器组合程序（特殊验收内嵌）。
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))

from semantic_translate import card_route  # noqa: E402（run_group 直接引用）

MAX_ATTEMPTS = 8

PROJECTS = [
    {
        "name": "订单状态机",
        "domain": "规则密集",
        "task": ("实现函数 advance(state, action)。状态集：待支付/已支付/已发货/"
                 "已完成/已取消。合法流转：待支付+支付→已支付；已支付+发货→已发货；"
                 "已发货+确认→已完成；待支付+取消→已取消。非法流转（状态×动作不在"
                 "上表）抛 ValueError，异常信息含当前 state 与 action。"),
        "knowledge_queries": ["订单状态怎么变", "问状态流转规则"],
        "tests": [
            "assert ns['advance']('待支付','支付')=='已支付'",
            "assert ns['advance']('已支付','发货')=='已发货'",
            "assert ns['advance']('已发货','确认')=='已完成'",
            "assert ns['advance']('待支付','取消')=='已取消'",
            "import contextlib",
            "try:\n    ns['advance']('已支付','取消')\n    raised=False\nexcept ValueError:\n    raised=True\nassert raised",
            "try:\n    ns['advance']('已完成','支付')\n    raised=False\nexcept ValueError:\n    raised=True\nassert raised",
        ],
    },
    {
        "name": "日历推算",
        "domain": "规则密集",
        "task": ("实现两个函数：is_leap(year) 判断闰年（被 4 整除不被 100 整除，"
                 "或被 400 整除）；next_day(y, m, d) 返回下一自然日的 (y, m, d) "
                 "元组（正确处理大小月、闰年 2 月 29 天、跨月与跨年）。"),
        "knowledge_queries": ["怎么判断闰年"],
        "tests": [
            "assert ns['is_leap'](2024) is True",
            "assert ns['is_leap'](1900) is False",
            "assert ns['is_leap'](2000) is True",
            "assert ns['next_day'](2024,2,28)==(2024,2,29)",
            "assert ns['next_day'](2023,2,28)==(2023,3,1)",
            "assert ns['next_day'](2023,12,31)==(2024,1,1)",
            "assert ns['next_day'](2024,4,30)==(2024,5,1)",
        ],
    },
    {
        "name": "账单聚合",
        "domain": "多组件",
        "task": ("实现函数 summarize(records)，records 为 dict 列表（键 category "
                 "与 amount）。返回 dict：'total'（amount>0 记录的金额和，保留两位"
                 "小数）、'by_category'（类目→过滤后金额和）、'top'（小计最大的类目，"
                 "并列取字典序首个；无记录为 None）。空输入返回 "
                 "{'total':0.0,'by_category':{},'top':None}。"),
        "knowledge_queries": ["怎么按类目统计金额", "问账单聚合"],
        "tests": [
            "r=[{'category':'食品','amount':100},{'category':'食品','amount':50.5},{'category':'文具','amount':-3},{'category':'文具','amount':20}]\ns=ns['summarize'](r)\nassert abs(s['total']-170.5)<0.01",
            "assert s['by_category']=={'食品':150.5,'文具':20}",
            "assert s['top']=='食品'",
            "e=ns['summarize']([])\nassert e=={'total':0.0,'by_category':{},'top':None}",
            "t=[{'category':'b','amount':10},{'category':'a','amount':10}]\nassert ns['summarize'](t)['top']=='a'",
        ],
    },
    {
        "name": "编译器组合程序",
        "domain": "中文编译器",
        "task": ("实现函数 program_text()，返回一个中文编译器程序字符串（多行），"
                 "程序必须：①定义 面积（r）：返回 r 乘 r 乘 3.14（圆周率取 3.14）；"
                 "②定义 总面积（n）：若 n 等于 0，则 返回 0，否则 返回 面积（n） 加 "
                 "总面积（n 减 1）（递归求和半径 1..n 的圆面积）；③结果 = 总面积（2）；止。"
                 "程序将由中文编译器编译执行，结果应为 15.7。"),
        "knowledge_queries": ["编译 递归", "编译 函数定义"],
        "tests": [
            ("import sys\nsys.path.insert(0, r'D:\\Program Files\\2_ai\\protocol-compiler')\n"
             "from core.compiler import compile_source\n"
             "from core.condition_vm import ConditionVM\n"
             "prog = ns['program_text']()\n"
             "code, r = compile_source(prog, strict=False)\n"
             "assert r.get('ok'), f'编译失败: {r.get(\"errors\")}'\n"
             "vm = ConditionVM(); vm.run(code)\n"
             "assert abs(vm.symbols.get('结果', 0) - 15.7) < 0.01, vm.symbols.get('结果')"),
        ],
    },
]

ANALYSIS_PROMPT = (
    "你是灵枢协议实例，执行递归反思验证机制第一步——分析任务条件与知识需求。\n"
    "任务：{task}\n以全局视角回答（150 字内）：①任务隐含的领域条件/必然事实？"
    "②需要的知识点或规则（逐条列出）？只输出分析，不写代码。"
)

IMPL_PROMPT = "{task}\n\n{context}{failing}"


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


def strip_code_block(text: str) -> str:
    import re
    m = re.search(r"```(?:python)?\s*(.+?)```", text, re.S)
    return m.group(1).strip() if m else text.strip()


def run_tests(code: str, tests: list) -> tuple[bool, str]:
    """验收。T9 数据作废教训：断言引用 ns 必须 ns 自引用注入——否则
    第一轮实现必然 NameError（机制性必败轮），污染整组数据。"""
    ns = {}
    try:
        exec(compile(code, "<impl>", "exec"), ns)
    except Exception as e:
        return False, f"代码执行异常 {type(e).__name__}: {e}。请确保函数已定义。"
    ns['ns'] = ns  # 自引用：断言文本中的 ns[...] 可直接解析
    for t in tests:
        try:
            exec(compile(t, "<assert>", "exec"), ns)
        except AssertionError:
            return False, (f"断言失败: {t}\n"
                           "（对照断言检查返回值结构、边界 case 与浮点精度）")
        except Exception as e:
            return False, f"测试异常: {t[:60]} → {type(e).__name__}: {e}"
    return True, ""


def run_group(group: str, proj: dict, dex) -> dict:
    rec = {"name": proj["name"], "group": group, "tokens": 0, "rounds": 0,
           "passed": False, "rounds_log": []}
    ctx = ""
    if group == "A":
        # 递归反思分析（机制开销如实计入）
        _a, u = llm(ANALYSIS_PROMPT.format(task=proj["task"]), "请分析。")
        rec["tokens"] += u["prompt"] + u["completion"]
        # 白箱查找：declaration 声明 + 规范型执行字段（层级对齐混合注入）
        cards = []
        for kw in proj["knowledge_queries"]:
            for h in (card_route(dex, kw, limit=1) or []):
                if not h.get("_card_hit"):
                    continue
                try:
                    _node = dex.store.get_node(h.get("id"))
                    cm = (_node.state_attributes or {}).get("comment", {}) if _node else {}
                except Exception:
                    cm = {}
                cards.append(
                    f"- 卡「{h.get('name')}」生效条件 {cm.get('生效条件', [])}；"
                    f"不适用条件 {cm.get('不适用条件', [])}；执行规范："
                    f"{cm.get('执行', '')}")
                break
        ctx = ("知识库规范卡（确定性规则，实现须遵循其中的行为规范与边界）：\n"
               + "\n".join(cards)) if cards else ""

    failing = ""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        q = IMPL_PROMPT.format(task=proj["task"], context=ctx + "\n\n" if ctx else "",
                               failing=f"上次实现未通过验收：{failing}\n请修正。" if failing else "")
        code, u = llm("你只输出代码。", q)
        rec["tokens"] += u["prompt"] + u["completion"]
        ok, failing = run_tests(strip_code_block(code), proj["tests"])
        rec["rounds"] = attempt
        rec["rounds_log"].append({"round": attempt, "ok": ok, "why": failing[:120]})
        if ok:
            rec["passed"] = True
            break
    return rec


def main() -> int:
    from wisdom_book import ConditionDex

    if not os.environ.get("BIGMODEL_API_KEY"):
        print("BIGMODEL_API_KEY 未设置", file=sys.stderr)
        return 1
    db = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")
    dex = ConditionDex(db_path=db, fresh=False)

    report = {"projects": [], "totals": {"A": 0, "B": 0, "A_pass": 0, "B_pass": 0}}
    for proj in PROJECTS:
        ra = run_group("A", proj, dex)
        rb = run_group("B", proj, dex)
        report["projects"].append({"name": proj["name"], "domain": proj["domain"],
                                   "A": ra, "B": rb})
        report["totals"]["A"] += ra["tokens"]
        report["totals"]["B"] += rb["tokens"]
        report["totals"]["A_pass"] += ra["passed"]
        report["totals"]["B_pass"] += rb["passed"]
        print(f"[{proj['domain']}] A={ra['tokens']}({ra['rounds']}轮"
              f"{'✓' if ra['passed'] else '✗'}) B={rb['tokens']}({rb['rounds']}轮"
              f"{'✓' if rb['passed'] else '✗'})")
        json.dump(report, open(os.path.join(HERE, "t10_report.json"), "w",
                               encoding="utf-8"), ensure_ascii=False, indent=1)
    dex.close()
    ta, tb = report["totals"]["A"], report["totals"]["B"]
    print(f"\n=== T10 总账 ===\nA 灵枢全管线: {ta} tok（过 {report['totals']['A_pass']}/4）"
          f"\nB 裸 LLM: {tb} tok（过 {report['totals']['B_pass']}/4）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
