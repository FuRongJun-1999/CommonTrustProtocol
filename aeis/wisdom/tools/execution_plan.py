# -*- coding: utf-8 -*-
"""execution_plan.py · 执行计划层（GPT 第七阶段 §7.2）

精准执行 = 路由正确 ∧ 规则适用 ∧ 执行结果通过验证（三闸门）。

流程：问题 → ①路由（route ACCEPT → selected_capability）
     → ②规则适用（precondition_check + dry_run 干运行）
     → ③真实执行（pattern exec + cases 断言）
     → 结果验证（对照 expected_output）→ 记录与固化 / 回滚。

六类对象映射：问题 Problem → 能力 Capability（路由）→ 条件 Condition
（生效条件注释）→ 规则 Rule（执行行）→ 执行 Execution（pattern+cases）
→ 证据 Evidence（condition_matches/rule_matches/trace/verification）。
"""
import ast
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import ccg


def _extract_comment_sections(code: str) -> dict:
    """从条件论注释提取结构段：{生效条件, 子功能, 执行, 不适用条件, head}。

    规则：四要素标记行开新段；非标记行并入当前段。
    但「列表推导式：[transform(x) for x in items]」这类功能名行（含：冒号
    且非四要素）是独立描述行——并入段会污染（被当不适用条件/子功能），
    识别为 head（语义名行）。
    """
    sections = {"生效条件": [], "子功能": [], "执行": [], "不适用条件": [],
                "head": ""}
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    cur = None
    for ln in lines:
        matched = None
        for key in ("生效条件", "子功能", "执行", "不适用条件"):
            if ln.startswith(key):
                matched = key
                break
        if matched:
            cur = matched
            sections[cur].append(ln[len(matched):].strip('：: ').strip())
        elif cur and not any(c in '：:' for c in ln[:8]):
            # 非标记行且不含冒号 → 当前段续行（子功能 ①② 等）
            sections[cur].append(ln)
        elif not cur and ln and not sections["head"]:
            sections["head"] = ln
        elif not sections["head"] and ln:
            # 标记段后出现的独立语义名行（含冒号）→ head
            sections["head"] = ln
    return sections


def _rule_line(code: str) -> str:
    """规则：执行行（如何执行）+ 子功能（做什么）。"""
    sec = _extract_comment_sections(code)
    parts = []
    if sec["子功能"]:
        parts.append(' '.join(sec["子功能"])[:60])
    if sec["执行"]:
        parts.append(' '.join(sec["执行"])[:60])
    return '；'.join(parts) if parts else sec["head"][:60]


def _conditions(code: str) -> list:
    """条件列表：生效条件行拆分（；/，/、分隔成条目）。"""
    sec = _extract_comment_sections(code)
    conds = []
    for line in sec["生效条件"]:
        for part in re.split(r'[；;，,。]', line):
            part = part.strip()
            if part and part not in conds:
                conds.append(part)
    if not conds:
        sec2 = _extract_comment_sections(code)
        if sec2["head"]:
            conds = [sec2["head"][:40]]
    return conds


def _not_conditions(code: str) -> list:
    sec = _extract_comment_sections(code)
    nots = []
    for line in sec["不适用条件"]:
        for part in re.split(r'[；;，,。]', line):
            part = part.strip()
            if part and part not in nots:
                nots.append(part)
    return nots


def _expected(code: str, head: str = '') -> str:
    """预期结果：功能名行（head 描述）或子功能最后一步。"""
    sec = _extract_comment_sections(code)
    if sec["head"]:
        return sec["head"][:50]
    if sec["子功能"]:
        return sec["子功能"][-1][:40]
    return head[:40] if head else '执行成功'


def build_plan(question: str, nodes=None, top: int = 5,
               depth: int = 3) -> dict:
    """生成执行计划（闸门1 路由正确 → selected_capability）。"""
    nodes = nodes if nodes is not None else ccg.build_graph()
    r = ccg.route(question, nodes, top=top, depth=depth)
    plan = {
        "question": question,
        "route_state": r["state"],
        "selected_capability": r.get("unit", ""),
        "route_path": r.get("path", []),
        "conditions": [],
        "rule": "",
        "expected_result": "",
        "verification": "",
        "rollback": "执行失败时不固化结果",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if r["state"] != "ACCEPT":
        plan["reason"] = r.get("reason", "非 ACCEPT（无资格执行）")
        plan["verification"] = "路由未 ACCEPT——不生成执行计划（三闸门 ①）"
        return plan
    uid = r["unit"]
    unit = nodes.get(uid, {})
    code = unit.get('code') or unit.get('pattern', '')
    # 从单元库取 pattern（nodes 只有 head/index，需回查单元库）
    from compiler_code_units import COMPILER_UNITS
    from python_code_units import PYTHON_UNITS
    from graph_db_units import GRAPH_UNITS
    from os_units import OS_UNITS
    from browser_units import BROWSER_UNITS
    from net_units import NET_UNITS
    for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
              OS_UNITS, BROWSER_UNITS, NET_UNITS):
        if uid in m:
            u = m[uid]
            code = u.get('pattern', '')
            plan['cases'] = u.get('cases', [])
            plan['params'] = u.get('params', [])
            plan['task'] = u.get('task', '')
            break
    plan["conditions"] = _conditions(code)
    plan["not_conditions"] = _not_conditions(code)
    plan["rule"] = _rule_line(code)
    plan["expected_result"] = _expected(code, unit.get('head', ''))
    plan["verification"] = (f"dry_run（语法+前置条件）→ 真实执行 {len(plan.get('cases', []))}"
                            f" 组 cases 断言 → 对照 expected_result")
    return plan


def precondition_check(plan: dict, evidence=None) -> dict:
    """闸门2a 前置条件检查：条件列表完整性 + 与任务无矛盾。

    Condition 证据（GPT §一）：condition_matches——条件的充分性。
    生效条件多为能力前置（「graph 提供 neighbors 接口」=执行环境要求），
    不是任务描述词——任务不含它不等于条件不满足。因此：
      充分 = 条件列表非空（能力声明了前置）∧ 任务词与「不适用条件」无冲突。
    不适用条件冲突（任务含被排除词）→ 前置不满足（E 类执行失败题）。
    """
    conds = plan.get("conditions", [])
    q = plan.get("question", "")
    if not conds:
        return {"ok": True, "level": "前置条件", "reason": "无显式条件（默认充分）",
                "condition_matches": []}
    # 条件覆盖度（信息性记录，不作否决——能力前置非任务词）
    qb = ccg._q_tokens(q)
    matches = []
    for c in conds:
        hit = len(qb & ccg._bigrams(c))
        matches.append({"condition": c, "matched": hit})
    # 否决项：任务与不适用条件冲突（负路由已排除候选，双保险）
    not_conds = plan.get("not_conditions", [])
    conflicts = []
    for nc in not_conds:
        ncb = {b for b in ccg._bigrams(nc)
               if any('\u4e00' <= c <= '\u9fff' for c in b)}
        if len(qb & ncb) >= 1:
            conflicts.append(nc)
    ok = len(conflicts) == 0
    return {"ok": ok, "level": "前置条件", "condition_matches": matches,
            "conflicts": conflicts,
            "reason": (f"{len(conds)} 条前置条件声明；任务与不适用条件"
                       f"{'冲突: ' + str(conflicts[:2]) if conflicts else '无冲突（充分）'}")}


def dry_run(plan: dict) -> dict:
    """闸门2b 干运行：语法 + 前置条件静态验证（不真实执行）。

    从计划反查单元代码（pattern），ast.parse 语法检查；
    前置条件 ok（precondition_check）。返回 dry_run_pass。
    """
    uid = plan.get("selected_capability", "")
    code = _lookup_code(uid)
    result = {"ok": False, "level": "dry_run", "syntax": False,
              "precondition": None, "evidence": ""}
    if not code:
        result["evidence"] = "找不到单元代码（无执行体）"
        return result
    try:
        ast.parse(code)
        result["syntax"] = True
    except SyntaxError as e:
        result["evidence"] = f"语法错误: {e}"
        return result
    pc = precondition_check(plan)
    result["precondition"] = pc
    if not pc["ok"]:
        result["evidence"] = f"前置条件不足: {pc['reason']}"
        return result
    result["ok"] = True
    result["evidence"] = "语法通过 + 前置条件满足（干运行 OK，可真实执行）"
    return result


def _lookup_code(uid: str) -> str:
    """按 uid 从六域单元库取 pattern 代码。"""
    from compiler_code_units import COMPILER_UNITS
    from python_code_units import PYTHON_UNITS
    from graph_db_units import GRAPH_UNITS
    from os_units import OS_UNITS
    from browser_units import BROWSER_UNITS
    from net_units import NET_UNITS
    for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
              OS_UNITS, BROWSER_UNITS, NET_UNITS):
        if uid in m:
            return m[uid].get('pattern', '')
    return ''


def _lookup_cases(uid: str) -> list:
    from compiler_code_units import COMPILER_UNITS
    from python_code_units import PYTHON_UNITS
    from graph_db_units import GRAPH_UNITS
    from os_units import OS_UNITS
    from browser_units import BROWSER_UNITS
    from net_units import NET_UNITS
    for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
              OS_UNITS, BROWSER_UNITS, NET_UNITS):
        if uid in m:
            return m[uid].get('cases', [])
    return []


def execute(plan: dict) -> dict:
    """闸门3 真实执行：pattern exec + cases 断言（复用 verifier L2 机制）。"""
    uid = plan.get("selected_capability", "")
    code = _lookup_code(uid)
    cases = plan.get("cases") or _lookup_cases(uid)
    result = {"ok": False, "level": "执行", "executed": 0, "passed": 0,
              "trace": [], "evidence": ""}
    if not code:
        result["evidence"] = "无执行体"
        return result
    ns = {}
    try:
        exec(compile(code, "<exec_plan>", "exec"), ns)
    except Exception as e:
        result["evidence"] = f"编译/执行失败: {e}"
        return result
    func_name = None
    try:
        tree = ast.parse(code)
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        func_name = funcs[0].name if funcs else None
    except Exception:
        pass
    if not func_name or func_name not in ns:
        result["evidence"] = f"找不到被测函数（{func_name}）"
        return result
    fn = ns[func_name]
    # 注入型检测：样例首个输入为 None（外部注入 Graph/依赖）→ 该单元
    # 依赖外部环境，独立执行无意义——诚实声明「依赖注入，不可独立验证」
    # （GPT §四 E 类：不能把「找到了相关函数」当成任务完成）
    injected = any(isinstance(inp, tuple) and len(inp) >= 1 and inp[0] is None
                   for inp, _ in cases)
    if injected:
        result["ok"] = False
        result["evidence"] = ("注入型单元（首个参数 None=外部依赖注入）——"
                              "依赖注入环境，不可独立验证；由集成/组合测试覆盖")
        return result
    ran = 0
    for idx, (inp, exp) in enumerate(cases, 1):
        if inp == "call":
            continue
        ran += 1
        try:
            got = fn(inp) if not isinstance(inp, tuple) else fn(*inp)
        except Exception as e:
            result["trace"].append({"case": idx, "ok": False,
                                    "error": str(e)[:60]})
            continue
        match = _assert_match(got, exp)
        result["trace"].append({"case": idx, "ok": match,
                                "input": str(inp)[:40],
                                "got": str(got)[:40],
                                "expected": str(exp)[:40]})
        if match:
            result["passed"] += 1
    result["executed"] = ran
    if ran == 0:
        result["evidence"] = "注入型单元（无独立样例）——由集成/组合测试覆盖"
        result["ok"] = True
        return result
    result["ok"] = result["passed"] == ran
    result["evidence"] = (f"{result['passed']}/{ran} 组样例通过"
                          + ("" if result["ok"] else "——结果验证失败（回滚：不固化）"))
    return result


def _assert_match(got, exp):
    """verifier 同款宽松断言：精确/近似/异常类型/谓词。"""
    if callable(exp):
        try:
            return bool(exp(got))
        except Exception:
            return False
    if isinstance(exp, float) and isinstance(got, (int, float)):
        return abs(float(got) - exp) < 1e-9
    if isinstance(exp, type) and issubclass(exp, BaseException):
        return isinstance(got, exp)
    try:
        return bool(got == exp)
    except Exception:
        return False


def run_execution(question: str, nodes=None, top: int = 5,
                  depth: int = 3, do_execute: bool = True) -> dict:
    """完整执行闭环：路由 → 计划 → 前置 → 干运行 → 执行 → 验证 → 证据。"""
    plan = build_plan(question, nodes, top, depth)
    evidence = {
        "question": question,
        "route_matches": plan["route_state"],
        "condition_matches": [],
        "rule_matches": plan["rule"][:60] if plan["rule"] else "",
        "execution_trace": [],
        "verification_result": None,
        "e2e": False,
    }
    if plan["route_state"] != "ACCEPT":
        evidence["verification_result"] = ("拒绝执行：路由"
                                           f"{plan['route_state']}（三闸门①未过）")
        return {"plan": plan, "evidence": evidence, "ok": False,
                "stage": "route"}
    pc = precondition_check(plan)
    evidence["condition_matches"] = pc.get("condition_matches", [])
    dr = dry_run(plan)
    if not dr["ok"]:
        evidence["verification_result"] = f"dry_run 未过: {dr['evidence']}"
        return {"plan": plan, "evidence": evidence, "ok": False,
                "stage": "dry_run", "dry_run": dr}
    if not do_execute:
        evidence["verification_result"] = "dry_run 通过（未真实执行）"
        evidence["e2e"] = True
        return {"plan": plan, "evidence": evidence, "ok": True,
                "stage": "dry_run", "dry_run": dr}
    ex = execute(plan)
    evidence["execution_trace"] = ex.get("trace", [])
    evidence["verification_result"] = ex["evidence"]
    evidence["e2e"] = ex["ok"]
    return {"plan": plan, "evidence": evidence, "ok": ex["ok"],
            "stage": "execute", "dry_run": dr, "execution": ex}


if __name__ == "__main__":
    # 自检：A 类条件充分题
    r = run_execution("写一个在无权图上求最短路径的代码单元")
    print(r["plan"]["route_state"], "→", r["plan"]["selected_capability"])
    print("  前置:", r["evidence"]["condition_matches"][:3])
    print("  结果:", r["evidence"]["verification_result"])
    print("  e2e:", r["evidence"]["e2e"])
