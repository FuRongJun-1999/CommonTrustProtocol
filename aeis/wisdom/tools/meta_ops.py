# -*- coding: utf-8 -*-
"""meta_ops.py · MOS 元操作语法（Kimi 建议 1，协议 §16）

四要素注释 → 机器可读结构化声明（capability/condition_space/
sub_capabilities/execution/invalid_when）→ 一致性验证
（声明 vs 代码 ast 提取实义比对——漂移自动暴露，与 §14 负面闭环联动）。

MOS 是白箱能力的「元声明层」：代码只是能力载体，MOS 把能力结构化
为可路由/可组合/可验证的节点（工作流化的基础，§17）。
"""
import ast
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def extract_mos(code: str, uid: str = '') -> dict:
    """从四要素注释提取 MOS 结构化声明（零 LLM）。"""
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    mos = {"capability": uid, "condition_space": {"requires": [],
                                                  "sub_capabilities": [],
                                                  "execution": "",
                                                  "invalid_when": []},
           "_raw": {"生效条件": [], "子功能": [], "执行": [], "不适用条件": []}}
    cur = None
    for ln in lines:
        matched = None
        for key in ("生效条件", "子功能", "执行", "不适用条件"):
            if ln.startswith(key):
                matched = key
                break
        if matched:
            cur = matched
            body = ln[len(matched):].strip('：: ').strip()
            if body:
                mos["_raw"][matched].append(body)
        elif cur and ln and not any(c in '：:' for c in ln[:8]):
            mos["_raw"][cur].append(ln)
        elif not cur and ln and not mos["capability"]:
            mos["capability"] = ln[:20]
    # 结构化：条目拆分（；/，/、）
    for item in mos["_raw"]["生效条件"]:
        for part in re.split(r'[；;，,。]', item):
            part = part.strip()
            if part:
                mos["condition_space"]["requires"].append(part)
    for item in mos["_raw"]["子功能"]:
        for part in re.split(r'[；;，,。]', item):
            part = part.strip()
            if part:
                mos["condition_space"]["sub_capabilities"].append(part)
    for item in mos["_raw"]["执行"]:
        if item and not mos["condition_space"]["execution"]:
            mos["condition_space"]["execution"] = item[:50]
    for item in mos["_raw"]["不适用条件"]:
        for part in re.split(r'[；;，,。]', item):
            part = part.strip()
            if part:
                mos["condition_space"]["invalid_when"].append(part)
    return mos


def _code_entities(code: str) -> dict:
    """从代码 ast 提取实义实体：函数名/参数名/类名/字符串/调用名。"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {"functions": [], "params": [], "classes": [],
                "strings": [], "calls": []}
    funcs, params, classes, strings, calls = [], [], [], [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            funcs.append(n.name)
            params.extend(a.arg for a in n.args.args)
        elif isinstance(n, ast.ClassDef):
            classes.append(n.name)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) \
                and len(n.value) >= 2:
            strings.append(n.value)
        elif isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name):
                calls.append(f.id)
            elif isinstance(f, ast.Attribute):
                calls.append(f.attr)       # struct.unpack_from → unpack_from
                if isinstance(f.value, ast.Name):
                    calls.append(f.value.id)  # → struct
    return {"functions": funcs, "params": sorted(set(params)),
            "classes": classes, "strings": strings,
            "calls": sorted(set(calls))}


def mos_consistency(code: str, uid: str = '') -> dict:
    """MOS 一致性验证：声明 vs 代码实义比对。

    检查：声明中提及的实体（子功能词/条件词）与代码提取的函数/参数/
    字符串重叠——零重叠 = 声明与实现漂移（Kimi 风险1 的机器可读化）。
    """
    mos = extract_mos(code, uid)
    ents = _code_entities(code)
    text_ents = set(ents["functions"]) | set(ents["params"]) | \
                set(ents["classes"]) | set(ents["strings"]) | \
                set(ents["calls"])
    # 声明侧实体词（中文词 + 代码标识符）
    decl_words = set()
    for item in (mos["condition_space"]["requires"]
                 + mos["condition_space"]["sub_capabilities"]
                 + mos["condition_space"]["invalid_when"]):
        decl_words.add(item)
        for w in re.findall(r'[A-Za-z_][A-Za-z0-9_]*', item):
            decl_words.add(w)
    # 重叠度：声明词是否在代码实义中出现（子串匹配，中文词放宽）
    overlap = []
    for w in decl_words:
        if not w or len(w) < 2:
            continue
        if any(w in e or e in w for e in text_ents if len(e) >= 2):
            overlap.append(w)
    all_cn = [w for w in decl_words
              if any('\u4e00' <= c <= '\u9fff' for c in w)]
    rate = round(len(overlap) / max(1, len(decl_words)), 3)
    return {"uid": uid, "mos": mos, "entities": ents,
            "declared": sorted(decl_words)[:12],
            "overlap": sorted(overlap)[:12],
            "n_declared": len(decl_words), "n_overlap": len(overlap),
            "consistency": rate,
            "has_entities": bool(ents["functions"] or ents["classes"])}


def audit_mos(verbose=False) -> dict:
    """全库 MOS 审计：提取 + 一致性 + 统计。"""
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
    results = []
    n_consistent = 0
    for uid, u in ALL.items():
        code = u.get('pattern', '')
        r = mos_consistency(code, uid)
        # 一致 = 有代码实体 且 声明-实体重叠率 > 0（声明提及实现内容）
        ok = r["has_entities"] and r["n_overlap"] > 0
        r["ok"] = ok
        if ok:
            n_consistent += 1
        results.append(r)
    return {"n": len(results), "n_ok": n_consistent,
            "rate": round(n_consistent / max(1, len(results)), 4),
            "results": results}


if __name__ == "__main__":
    r = audit_mos()
    print(f"MOS 审计: {r['n_ok']}/{r['n']} "
          f"({100.0*r['rate']:.1f}%) 声明-实现一致")
    # 低一致示例
    lows = sorted(r["results"], key=lambda x: x["consistency"])[:6]
    for x in lows:
        print(f'  [{x["uid"]}] 一致率 {x["consistency"]} '
              f'声明 {x["n_declared"]} 重叠 {x["n_overlap"]}')
