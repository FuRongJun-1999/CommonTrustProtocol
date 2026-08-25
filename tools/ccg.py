# -*- coding: utf-8 -*-
"""ccg.py · 代码条件路由图（CCG）原型 v0.3

从条件论注释提取索引（注释 = 图的索引）：
  - 功能名行 / 生效条件 / 子功能 / 执行 → 条件词（中文二元组 + 缩写中文全称）
  - R2 同义词边：BFS（广度优先搜索）→ BFS 与「广度优先搜索」都是索引词
检索：问题条件词 → 单元命中（二元组 Jaccard 排序）→ 可解释路径。

对照现状：扁平关键词表 route（「广度优先搜索」→ 域未识别）；
CCG 从注释索引 → 命中 图遍历-BFS。
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def _bigrams(text: str) -> set:
    """中文二元组（含空格归一化）——灵枢中文检索同款。"""
    t = re.sub(r'\s+', '', text)
    return {t[i:i + 2] for i in range(len(t) - 1)}


_ABBR_CN = re.compile(r'([A-Z][A-Z0-9]{1,})[（(]([^）)]+)[）)]')


def extract_comment_index(code: str) -> dict:
    """从代码注释提取索引：{注释文本, 缩写词, 缩写中文全称, 全称二元组}。"""
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    text = ' '.join(lines)
    abbrs = {}
    for m in _ABBR_CN.finditer(text):
        abbrs[m.group(1)] = m.group(2)
    idx = {
        'text': text,
        'abbrs': abbrs,
        'tokens': _bigrams(text) | {w for w in abbrs.values() if len(w) >= 2},
    }
    return idx


def build_graph():
    """建图：六域 681 单元 → 注释索引。"""
    from compiler_code_units import COMPILER_UNITS
    from python_code_units import PYTHON_UNITS
    from graph_db_units import GRAPH_UNITS
    from os_units import OS_UNITS
    from browser_units import BROWSER_UNITS
    from net_units import NET_UNITS
    domains = [('compiler', COMPILER_UNITS), ('pylang', PYTHON_UNITS),
               ('graph', GRAPH_UNITS), ('os', OS_UNITS),
               ('browser', BROWSER_UNITS), ('net', NET_UNITS)]
    nodes = {}  # uid -> {domain, task, index}
    for dname, units in domains:
        for uid, u in units.items():
            nodes[uid] = {'domain': dname, 'task': u.get('task', ''),
                          'index': extract_comment_index(u.get('pattern', ''))}
    return nodes


# 停用词（问题词中无检索价值的二元组——「写一个」类）
_STOP = {"写一", "一个", "个单", "单元", "帮我", "请写", "给我", "实现",
         "一下", "那个", "这个", "还有", "需要", "帮我写"}


def _q_tokens(question: str) -> set:
    """问题条件词：二元组 - 停用词。"""
    return _bigrams(question) - _STOP


# 依赖边（U→U）：域管线 c 端到端组合对（手工维护核心链，后续自动提取）
DEP_EDGES = [
    # graph: 顶点覆盖 → LCA → 条件分解
    ("图算法-顶点覆盖", "图算法-最近公共祖先"),
    ("图算法-最近公共祖先", "条件路由图-条件分解"),
    # compiler: 名实绑定 → 信任流分析 → 短路求值
    ("编译-名实绑定", "编译-信任流分析"),
    ("编译-信任流分析", "VM-短路求值"),
    # pylang: 解包赋值 → 集合推导 → 切片赋值
    ("求值-解包赋值", "推导式-集合推导"),
    ("推导式-集合推导", "语法-切片赋值"),
    # os: 软中断 → 工作窃取 → 模块加载
    ("中断-软中断", "调度-工作窃取"),
    ("调度-工作窃取", "系统-模块加载"),
    # browser: 事件委托 → 弹窗拦截 → 混合内容
    ("事件-事件委托", "浏览器-弹窗拦截"),
    ("浏览器-弹窗拦截", "安全-混合内容"),
    # net: 帧解析 → MAC学习 → 证书校验
    ("网络-帧解析", "网络-MAC学习"),
    ("网络-MAC学习", "网络-证书校验"),
]


def build_dep_graph() -> dict:
    """依赖图：uid -> 后继 uid 列表。"""
    g = {}
    for a, b in DEP_EDGES:
        g.setdefault(a, []).append(b)
    return g


def search(question: str, nodes=None, top: int = 5) -> list:
    """条件检索：问题条件词 → 单元命中（注释索引 + task 加权排序）。"""
    nodes = nodes if nodes is not None else build_graph()
    q = _q_tokens(question)
    scored = []
    for uid, n in nodes.items():
        idx = n['index']
        common = q & idx['tokens']
        if not common:
            continue
        # 命中词数 + task 词命中加权（task 是单元权威名）+ 注释覆盖率
        task_hit = sum(1 for c in _bigrams(n['task']) if c in q)
        score = (len(common) + 2 * task_hit,
                 len(common) / max(1, len(idx['tokens'])))
        scored.append((uid, n['domain'], score, sorted(common)[:8]))
    scored.sort(key=lambda x: (-x[2][0], -x[2][1]))
    return scored[:top]


def compose(question: str, nodes=None, top: int = 5) -> dict:
    """条件编写：多单元命中 → 沿依赖边组装 → 代码（原型：依赖链拼接）。"""
    nodes = nodes if nodes is not None else build_graph()
    dep = build_dep_graph()
    hits = search(question, nodes, top=top)
    if not hits:
        return {"ok": False, "reason": "无命中单元", "chain": [], "code": None}
    # 组装链：首命中单元 → 沿依赖边收集后继（存在则续链）
    chain = [hits[0][0]]
    seen = set(chain)
    cur = chain[0]
    while dep.get(cur):
        nxt = dep[cur][0]
        if nxt in seen:
            break
        chain.append(nxt)
        seen.add(nxt)
        cur = nxt
    # 拼接代码（组装链）
    from compiler_code_units import COMPILER_UNITS
    from python_code_units import PYTHON_UNITS
    from graph_db_units import GRAPH_UNITS
    from os_units import OS_UNITS
    from browser_units import BROWSER_UNITS
    from net_units import NET_UNITS
    _ALL = {}
    for m in (COMPILER_UNITS, PYTHON_UNITS, GRAPH_UNITS,
              OS_UNITS, BROWSER_UNITS, NET_UNITS):
        _ALL.update(m)
    code_parts = []
    for uid in chain:
        u = _ALL.get(uid)
        if u:
            code_parts.append(f"# ===== {uid}（{u.get('task', '')}）=====\n"
                              + u['pattern'])
    return {"ok": True, "chain": chain, "code": "\n\n".join(code_parts),
            "hit_units": [h[0] for h in hits]}


def explain(uid, nodes=None) -> str:
    """可解释路径：单元注释索引文本。"""
    nodes = nodes if nodes is not None else build_graph()
    n = nodes.get(uid)
    if not n:
        return ''
    return f"[{uid}] ({n['domain']} 域) 任务={n['task']}\n  注释: {n['index']['text'][:120]}"


if __name__ == "__main__":
    g = build_graph()
    print(f"CCG 建图: {len(g)} 个单元节点（注释索引）\n")
    for q in ["写一个广度优先搜索单元", "写一个最短路径单元",
              "写一个软中断单元", "写一个帧解析单元"]:
        hits = search(q, g, top=3)
        print(f"=== 检索「{q}」===")
        for uid, dom, (c, _j), words in hits:
            print(f"  命中 {uid} ({dom}) 共词 {c} | 命中词 {words}")
        print()
