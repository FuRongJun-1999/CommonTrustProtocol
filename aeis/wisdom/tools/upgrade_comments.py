# -*- coding: utf-8 -*-
"""upgrade_comments.py · 条件论注释三要素自动生成器（试点）

从代码结构提取真实语义生成三要素草稿：
  生效条件：参数 + if 分支合法值 + 接口调用（graph.neighbors 等）
  子功能：if/elif op 分支或关键调用序列
  执行：主循环/分派/调用模式
生成质量抽查后全量应用（白箱纪律：生成草稿 + 外部校准）。
"""
import ast
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def _param_names(func):
    return [a.arg for a in func.args.args if a.arg not in ('self', 'cls')]


def _op_branches(func):
    """if x == 'lit' / elif 分支 → {变量: [合法值]}。"""
    ops = {}
    for node in ast.walk(func):
        if isinstance(node, ast.If):
            test = node.test
            if isinstance(test, ast.Compare) and len(test.ops) == 1 \
                    and isinstance(test.ops[0], ast.Eq) \
                    and isinstance(test.left, ast.Name) \
                    and isinstance(test.comparators[0], ast.Constant) \
                    and isinstance(test.comparators[0].value, str):
                v = test.left.id
                ops.setdefault(v, []).append(test.comparators[0].value)
    for v in list(ops):
        ops[v] = sorted(set(ops[v]))
    return ops


def _calls(func):
    """函数内直接调用名（去重保序，排除内置/import 模块名）。"""
    names = []
    for node in ast.walk(func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id not in names:
                names.append(node.func.id)
    return names


def _uses_interface(func):
    """接口调用：仅保留有意义的容器/图接口（去重，过滤 append/pop 等原语噪声）。"""
    NOISE = {"append", "pop", "extend", "add", "update", "remove", "setdefault",
             "get", "set", "items", "values", "keys", "join", "split"}
    hits = []
    for node in ast.walk(func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            base = node.func.value
            if isinstance(base, ast.Name) and node.func.attr not in NOISE:
                iface = f"{base.id}.{node.func.attr}"
                if iface not in hits:
                    hits.append(iface)
    return hits


def gen_cond_comment(code: str) -> tuple:
    """生成三要素草稿 (生效条件, 子功能, 执行)。"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return ("输入合法", "按逻辑处理", "执行主体逻辑")
    funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    if not funcs:
        return ("输入合法", "按逻辑处理", "执行主体逻辑")
    f = funcs[0]
    params = _param_names(f)
    ops = _op_branches(f)
    calls = _calls(f)
    ifaces = _uses_interface(f)
    has_loop = any(isinstance(n, (ast.For, ast.While)) for n in ast.walk(f))
    has_cond = any(isinstance(n, (ast.If, ast.IfExp)) for n in ast.walk(f))

    # 生效条件
    conds = []
    for v, vals in ops.items():
        conds.append(f"{v} ∈ {{{', '.join(vals)}}}")
    for i in ifaces[:2]:
        conds.append(f"{i} 可用")
    cond_str = "；".join(conds) if conds else f"参数 {'/'.join(params) if params else '输入'} 合法"

    # 子功能：op 分支编号 / 调用 / 主逻辑
    CN_NUM = "①②③④⑤⑥⑦⑧⑨⑩"
    if ops:
        subs = "；".join(f"{CN_NUM[i - 1]} {v} 分支处理" for i, v in enumerate(ops, 1))
    elif calls:
        subs = "；".join(f"{CN_NUM[i - 1]} 调用 {c}" for i, c in enumerate(calls[:3], 1))
    elif has_cond:
        subs = "① 条件判定 ② 结果处理"
    else:
        subs = "① 主体逻辑执行"

    # 执行
    exec_parts = []
    if ops:
        exec_parts.append("按 op 分派")
    if has_loop:
        exec_parts.append("循环迭代")
    if calls:
        exec_parts.append("顺序调用")
    if not exec_parts:
        exec_parts.append("顺序执行")
    exec_str = "；".join(exec_parts)

    return cond_str, subs, exec_str


def has_cond_comment(code: str) -> bool:
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    joined = " ".join(lines)
    return all(k in joined for k in ("生效条件", "子功能", "执行"))


def apply_to_file(path: str, units: dict, dry: bool = True) -> int:
    """把未含三要素的单元注释升级写回源文件（在 def 行字面量后插入）。

    pattern 是 `"def f(...):\n"` 拼接字面量——在 def 行后插入三要素字面量行。
    返回升级单元数。
    """
    import re
    text = open(path, encoding='utf-8').read()
    n = 0
    for uid, u in units.items():
        code = u['pattern']
        if has_cond_comment(code):
            continue
        try:
            tree = ast.parse(code)
            func = next((x for x in ast.walk(tree)
                         if isinstance(x, ast.FunctionDef)), None)
        except SyntaxError:
            continue
        if func is None:
            continue
        c, s, e = gen_cond_comment(code)
        esc = lambda t: t.replace('\\', '\\\\').replace('"', '\\"')
        insert = (f'"    # 生效条件：{esc(c)}\\n"\n'
                  f'"    # 子功能：{esc(s)}\\n"\n'
                  f'"    # 执行：{esc(e)}\\n"\n')
        # 定位该单元块内 def 字面量行（含 uid 到 def 之间）
        start = text.find(f'"{uid}": {{')
        if start < 0:
            continue
        end = text.find('"calibration"', start)
        if end < 0:
            end = start + 4000
        block = text[start:end]
        # def 字面量行： "def <func>(...):\n"
        pat = re.compile(r'("def ' + re.escape(func.name) + r'\([^"]*\):\\n"\n)')
        m = pat.search(block)
        if not m:
            continue
        pos = start + m.end(1)
        text = text[:pos] + insert + text[pos:]
        n += 1
    if not dry:
        open(path, 'w', encoding='utf-8').write(text)
    return n


if __name__ == "__main__":
    import os
    HERE = os.path.dirname(os.path.abspath(__file__))
    from compiler_code_units import COMPILER_UNITS
    from python_code_units import PYTHON_UNITS
    from graph_db_units import GRAPH_UNITS
    from os_units import OS_UNITS
    from browser_units import BROWSER_UNITS
    from net_units import NET_UNITS
    FILES = [('compiler_code_units.py', COMPILER_UNITS),
             ('python_code_units.py', PYTHON_UNITS),
             ('graph_db_units.py', GRAPH_UNITS),
             ('os_units.py', OS_UNITS),
             ('browser_units.py', BROWSER_UNITS),
             ('net_units.py', NET_UNITS)]
    mode = sys.argv[1] if len(sys.argv) > 1 else 'dry'
    total = 0
    for fn, units in FILES:
        k = apply_to_file(os.path.join(HERE, fn), units, dry=(mode == 'dry'))
        print(f"{fn}: {k} 个升级（{'dry 预览' if mode == 'dry' else '已写回'}）")
        total += k
    print(f"合计: {total} 个（模式: {mode}）")
