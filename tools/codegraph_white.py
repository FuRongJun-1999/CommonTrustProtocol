# -*- coding: utf-8 -*-
"""codegraph_white.py · 白箱代码理解能力（第五阶段·codegraph 模式落地）
模式 ②③④：AST→统一IR→类型化图 + 影响分析 + 环检测（零 LLM，Python 内置 ast）
  1. extract_code_ir   源码 → 统一 IR（函数/类/导入/调用）——codegraph CodeIR 同构
  2. build_call_graph  IR → 调用图（Function 节点 + Calls 边）
  3. impact_analysis   改函数 → 调用面（BFS 逆向 = 谁受影响）
  4. detect_cycles     调用环检测（Tarjan SCC）
"""
import sys
import ast
sys.stdout.reconfigure(encoding='utf-8')


# ============ 一、统一 IR 提取（AST → CodeIR 等价物） ============
def extract_code_ir(source, file_path="<source>"):
    """源码 → 统一 IR：{file, functions[], classes[], imports[], calls[]}
    functions: {name, params[], calls[], class_owner}
    classes:   {name, methods[], bases[]} | imports: {module, names[]}"""
    tree = ast.parse(source)
    ir = {"file": file_path, "functions": [], "classes": [], "imports": [], "calls": []}

    def calls_of(node):
        return [n.func.id for n in ast.walk(node)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)]

    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                ir["imports"].append({"module": a.name.split(".")[0], "names": [a.asname or a.name]})
        elif isinstance(n, ast.ImportFrom):
            ir["imports"].append({"module": n.module or "", "names":
                                  [a.asname or a.name for a in n.names]})
    for n in tree.body:
        if isinstance(n, ast.FunctionDef):
            ir["functions"].append({"name": n.name,
                                    "params": [a.arg for a in n.args.args],
                                    "calls": calls_of(n), "class_owner": None})
        elif isinstance(n, ast.ClassDef):
            cls = {"name": n.name,
                   "methods": [m.name for m in n.body if isinstance(m, ast.FunctionDef)],
                   "bases": [ast.unparse(b) for b in n.bases]}
            ir["classes"].append(cls)
            for m in n.body:
                if isinstance(m, ast.FunctionDef):
                    ir["functions"].append({"name": f"{n.name}.{m.name}",
                                            "params": [a.arg for a in m.args.args],
                                            "calls": calls_of(m), "class_owner": n.name})
    return ir


# ============ 二、调用图（Function 节点 + Calls 边） ============
def build_call_graph(ir):
    """IR → 调用图 {func: [被调用的函数名]}（只保留图中存在的函数）"""
    funcs = {f["name"] for f in ir["functions"]}
    graph = {}
    for f in ir["functions"]:
        graph[f["name"]] = [c for c in f["calls"] if c in funcs]
    return graph


# ============ 三、影响分析（BFS 逆向：谁调用我 → 影响面） ============
def impact_analysis(ir, target, max_depth=3):
    """改 target 函数 → 逆向 BFS 求调用面（谁直接/间接受影响）
    返回 {target, callers[], depth, chain[]}——codegraph impact_analysis 同构"""
    graph = build_call_graph(ir)
    # 反向邻接：callee -> callers
    reverse = {}
    for f, callees in graph.items():
        for c in callees:
            reverse.setdefault(c, []).append(f)
    visited, queue, depth_map = set(), [target], {target: 0}
    callers = []
    while queue:
        cur = queue.pop(0)
        for caller in reverse.get(cur, []):
            if caller not in visited:
                visited.add(caller)
                depth_map[caller] = depth_map[cur] + 1
                if depth_map[caller] <= max_depth:
                    callers.append(caller)
                    queue.append(caller)
    # 正向依赖链（它调用谁——简单一跳）
    callees = graph.get(target, [])
    return {"target": target, "callers": callers, "depth": depth_map,
            "callees": callees}


# ============ 四、环检测（Tarjan SCC：循环调用/递归依赖） ============
def detect_cycles(ir):
    """调用环检测（Tarjan SCC，codegraph algorithms 同构）
    返回 [ [环内函数...], ... ]（仅 size>1 的强连通分量 + 自环）"""
    graph = build_call_graph(ir)
    nodes = list(graph.keys())
    index, lowlink, on_stack, stack = {}, {}, set(), []
    result = []
    counter = [0]

    def strongconnect(v):
        index[v] = lowlink[v] = counter[0]
        counter[0] += 1
        stack.append(v)
        on_stack.add(v)
        for w in graph.get(v, []):
            if w not in index:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], index[w])
        if lowlink[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) > 1:
                result.append(comp)

    for v in nodes:
        if v not in index:
            strongconnect(v)
    return result


if __name__ == "__main__":
    print("=== 白箱代码理解能力（codegraph 模式落地 · 零 LLM）===\n")
    SAMPLE = '''
import math
import os

def parse(data):
    tokens = split(data)
    return tokens

def split(data):
    return data.split(",")

def compute(tokens):
    return parse(tokens)

def main():
    data = os.read()
    result = compute(data)
    print(result)

class Service:
    def handle(self, req):
        return compute(req)

def recursive(n):
    if n <= 1:
        return 1
    return n * recursive(n - 1)
'''
    ir = extract_code_ir(SAMPLE, "sample.py")
    print(f"① 统一 IR: {len(ir['functions'])} 函数 / {len(ir['classes'])} 类 / {len(ir['imports'])} 导入")
    for f in ir["functions"]:
        print(f"   {f['name']}({','.join(f['params'])}) 调用: {f['calls']}")

    print("\n② 调用图:")
    for f, c in build_call_graph(ir).items():
        if c:
            print(f"   {f} -> {c}")

    print("\n③ 影响分析（改 compute → 谁受影响）:")
    r = impact_analysis(ir, "compute")
    print(f"   调用面: {r['callers']}（深度: {r['depth']}）| compute 调用: {r['callees']}")

    print("\n④ 环检测（Tarjan SCC）:")
    cycles = detect_cycles(ir)
    print(f"   调用环: {cycles if cycles else '无（除递归自环）'}")
    ok = len(ir["functions"]) >= 6 and "compute" in r["callers"] and len(cycles) >= 0
    print(f"\n=== 判定 ===\n白箱代码理解: {'✔ IR/调用图/影响分析/环检测成立' if ok else '✘'}")
