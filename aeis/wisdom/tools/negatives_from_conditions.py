# -*- coding: utf-8 -*-
"""negatives_from_conditions.py · 不适用条件 → 负面测试闭环（Kimi 建议 B）

把 681 单元的「不适用条件」注释解析为可执行反例，验证单元确实拒绝：
  「op 非 {A,B} 时」→ 传不在集合的 op → 应拒绝（None/异常/False）
  「xxx 为空/非法时」→ 传 None/非法 → 应拒绝
闭环价值（Kimi）：解决「开发者只考虑 happy path」的偏差——不适用条件
不是装饰，是可执行的反例契约。L3 只测泛化边界（None/空/极端），本工具
测【注释声明的具体不适用场景】。
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def extract_not_conditions(code: str) -> list:
    """从注释提取不适用条件条目（结构化）：(类型, 参数, 约束)。"""
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    nots = []
    for ln in lines:
        if not ln.startswith('不适用条件'):
            continue
        body = ln[len('不适用条件'):].strip('：: ')
        for part in re.split(r'[；;]', body):
            part = part.strip()
            if not part:
                continue
            # 模式1：op 非 {A, B} 时 / x 非 {A,B} 时
            m = re.search(r'(\w+)\s*非\s*\{([^}]*)\}', part)
            if m:
                param, vals = m.group(1), [v.strip() for v in m.group(2).split(',')]
                nots.append({"kind": "op_not_in", "param": param,
                             "valid": vals, "text": part[:40]})
                continue
            # 模式2：xxx 为空/非法时
            m2 = re.search(r'(\w+)\s*为空|(\w+)\s*非法', part)
            if m2:
                param = m2.group(1) or m2.group(2)
                nots.append({"kind": "empty_invalid", "param": param,
                             "text": part[:40]})
                continue
            # 模式3：x 越界
            m3 = re.search(r'(\w+)\s*越界', part)
            if m3:
                nots.append({"kind": "out_of_range", "param": m3.group(1),
                             "text": part[:40]})
    return nots


def _neg_input(param: str, kind: str, valid_vals=None):
    """构造反例输入：基于参数名启发（零 LLM）。"""
    p = param.lower()
    if kind == "op_not_in" and valid_vals:
        # 不在合法集合的 op（数字/字符反例）
        return "__INVALID_OP__"
    if kind == "empty_invalid":
        return None
    if kind == "out_of_range":
        return -1
    # 参数名启发兜底
    if any(k in p for k in ("arr", "list", "items", "seq", "stack", "queue", "ready", "servers")):
        return None
    if any(k in p for k in ("graph", "g", "table", "map", "db", "state", "env", "cond")):
        return None
    return None


def _is_reject(got) -> bool:
    """拒绝判定（递归）：None / False / 含 None 组件的元组/列表/字典
    （(None, 0) 是布尔解析的无效标记——顶层非 None 但含 None 组件即拒绝）。
    """
    if got is None or got is False:
        return True
    if isinstance(got, tuple):
        return any(_is_reject(x) for x in got)
    if isinstance(got, list):
        return any(_is_reject(x) for x in got)
    if isinstance(got, dict):
        return any(_is_reject(x) for x in got.values())
    return False


def run_negatives(verbose=False) -> dict:
    """全库负面测试：解析不适用条件 → 构造反例 → 执行断言「拒绝」。

    拒绝 = 调用抛异常 / 返回 None / 返回 False / 返回值含 None 组件。
    """
    from compiler_code_units import COMPILER_UNITS
    from python_code_units import PYTHON_UNITS
    from graph_db_units import GRAPH_UNITS
    from os_units import OS_UNITS
    from browser_units import BROWSER_UNITS
    from net_units import NET_UNITS
    ALL = {}
    for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
              OS_UNITS, BROWSER_UNITS, NET_UNITS):
        ALL.update(m)

    total_cond = parsed = rejected = crashed = skipped = 0
    strong_parsed = strong_rejected = 0
    reject_details = []
    for uid, u in ALL.items():
        code = u.get('pattern', '')
        conds = extract_not_conditions(code)
        if not conds:
            continue
        total_cond += len(conds)
        # 编译执行
        ns = {}
        try:
            exec(compile(code, "<neg>", "exec"), ns)
        except Exception:
            continue
        funcs = [n for n in ast.walk(ast.parse(code))
                 if isinstance(n, ast.FunctionDef)]
        if not funcs:
            continue
        fn_name = funcs[0].name
        if fn_name not in ns:
            continue
        fn = ns[fn_name]
        n_args = len(funcs[0].args.posonlyargs) + len(funcs[0].args.args)
        # 参数名
        arg_names = [a.arg for a in funcs[0].args.args]
        # 注入型判定：单元自带 cases 首参 None（外部依赖注入，如 Graph）
        cases = u.get('cases', [])
        injected_unit = any(
            isinstance(inp, tuple) and len(inp) >= 1 and inp[0] is None
            for inp, _ in cases)
        for cond in conds:
            parsed += 1
            param = cond["param"]
            if param not in arg_names:
                skipped += 1
                continue
            # 构造反例：该参数用非法值；其他参数用最小占位（非 None——
            # None 只用于注入型判定；普通多参单元给空容器/0 占位）
            neg_vals = []
            for an in arg_names:
                if an == param:
                    neg_vals.append(_neg_input(param, cond["kind"],
                                               cond.get("valid")))
                else:
                    # 最小占位：参数名启发（空容器/0/''）——非注入型
                    p = an.lower()
                    if any(k in p for k in ("arr", "list", "items", "seq",
                                            "stack", "queue", "words",
                                            "samples", "routes", "ready",
                                            "servers", "frames", "tokens")):
                        neg_vals.append([])
                    elif any(k in p for k in ("graph", "g", "table", "map",
                                              "db", "state", "env", "cond",
                                              "adj", "nodes", "page")):
                        neg_vals.append({})
                    elif any(k in p for k in ("count", "size", "n", "num",
                                              "capacity", "limit", "depth")):
                        neg_vals.append(0)
                    else:
                        neg_vals.append(0)  # 通用数值占位
            # 注入型（首参 None 外部依赖）→ 无法独立测
            if injected_unit:
                skipped += 1
                continue
            try:
                got = fn(*neg_vals)
                rejected_ok = _is_reject(got)
            except Exception:
                rejected_ok = True  # 异常 = 拒绝
            # 强契约（非{集合}/越界）单独统计——必须拒绝；
            # 弱契约（为空/非法）→ 默认值也是合法（L3 覆盖不崩溃）
            strong = cond["kind"] in ("op_not_in", "out_of_range")
            if strong:
                strong_parsed += 1
                if rejected_ok:
                    strong_rejected += 1
            if rejected_ok:
                rejected += 1
            else:
                crashed += 1
                reject_details.append({"unit": uid, "cond": cond["text"],
                                       "param": param,
                                       "got": str(got)[:40]})
    return {"units_parsed": parsed, "rejected": rejected,
            "crashed": crashed, "skipped": skipped,
            "reject_rate": round(rejected / max(1, parsed), 4),
            "strong": {"parsed": strong_parsed, "rejected": strong_rejected,
                       "rate": round(strong_rejected / max(1, strong_parsed), 4)},
            "details": reject_details[:10],
            "n_details": len(reject_details)}


if __name__ == "__main__":
    r = run_negatives(verbose=True)
    s = r["strong"]
    print(f"解析不适用条件: {r['units_parsed']}")
    print(f"强契约（非{{集合}}/越界——必须拒绝）: {s['rejected']}/{s['parsed']} "
          f"({100.0*s['rate']:.0f}%)")
    print(f"总拒绝（含弱契约默认值）: {r['rejected']} ({100.0*r['reject_rate']:.0f}%)")
    print(f"未拒绝: {r['crashed']} | 跳过（注入型/参数不匹配）: {r['skipped']}")
    for d in r["details"][:6]:
        print(f'  [未拒绝] {d["unit"]}: {d["cond"]} → {d["got"]}')
