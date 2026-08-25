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
    """从条件论注释提取索引：{注释文本, 子功能词, 生效条件词, 缩写同义词}。

    三要素行分离（语义时空图·结构面）：
      子功能行（内部功能分解）→ sub_tokens（问题问内部能力时加权）
      生效条件行（前置条件）→ cond_tokens
      功能名/执行行 → tokens（主索引）
    """
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    text = ' '.join(lines)
    sub_lines = [ln for ln in lines if ln.startswith('子功能')]
    cond_lines = [ln for ln in lines if ln.startswith('生效条件')]
    abbrs = {}
    for m in _ABBR_CN.finditer(text):
        abbrs[m.group(1)] = m.group(2)
    syn = {w for w in abbrs.values() if len(w) >= 2}
    idx = {
        'text': text,
        'abbrs': abbrs,
        'tokens': _bigrams(text) | syn,
        'sub_tokens': _bigrams(' '.join(sub_lines)),
        'cond_tokens': _bigrams(' '.join(cond_lines)),
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


def auto_dep_edges(test_path: str = None) -> list:
    """从域管线 c 端到端段自动提取 U→U 依赖边（115 段 ≈ 200+ 边）。

    解析 test_code_compose_domains.py：按「c 端到端」注释分块，
    每块连续 domain_route("问题") 调用 → 固化直出单元名 → 链边。
    新单元固化后重跑即自动建边（替代手工维护）。
    """
    import re as _re
    from code_compose import domain_route
    test_path = test_path or os.path.join(HERE, 'test_code_compose_domains.py')
    try:
        src = open(test_path, encoding='utf-8').read()
    except OSError:
        return DEP_EDGES
    blocks = _re.split(r'# .*c 端到端', src)
    edges = []
    for block in blocks[1:]:
        calls = _re.findall(r'domain_route\("([^"]+)"\)', block)
        units = []
        for q in calls:
            try:
                r = domain_route(q)
                if r.get('ok') and r.get('unit'):
                    units.append(r['unit'])
            except Exception:
                continue
        if len(units) >= 2:
            edges.extend(zip(units, units[1:]))
    seen, uniq = set(), []
    for e in edges:
        if e not in seen:
            seen.add(e)
            uniq.append(e)
    return uniq or DEP_EDGES


# 依赖边缓存（auto_dep_edges 解析一次）
_DEP_CACHE = None


def build_dep_graph() -> dict:
    """依赖图：uid -> 后继 uid 列表（自动提取 + 手工兜底）。"""
    global _DEP_CACHE
    if _DEP_CACHE is None:
        g = {}
        for a, b in auto_dep_edges():
            g.setdefault(a, []).append(b)
        _DEP_CACHE = g
    return _DEP_CACHE


def _core_task(question: str) -> str:
    """问题核心任务词：去请求前缀/括号注释/尾部「单元」。

    「写一个条件跳转编译单元」→「条件跳转编译」（与 task 完全相等才 exact 加分，
    避免「条件跳转」这类子串误加分——子串会让执行侧 VM-条件跳转 误赢编译侧）。
    """
    import re as _re
    core = _re.sub(r'^(写一个|写个|帮我写|实现一个|请写一个|请实现)', '', question)
    core = _re.sub(r'（.*?）|\(.*?\)|单元$|单元', '', core).strip()
    return core


def search(question: str, nodes=None, top: int = 5) -> list:
    """条件检索：问题条件词 → 单元命中（注释索引 + task 加权排序）。"""
    nodes = nodes if nodes is not None else build_graph()
    q = _q_tokens(question)
    core = _core_task(question)
    scored = []
    for uid, n in nodes.items():
        idx = n['index']
        common = q & idx['tokens']
        if not common:
            continue
        # 命中词数 + task 权威名加权（task 整体出现在核心词 → 强加权；
        # 二元组部分包含不再计——「数据包采样」task 含「数据包」但不代表
        # 「数据包解析」问它，避免平局误判）+ 注释覆盖率
        task_hit = 2 if n['task'] and n['task'] in core else 0
        # 子功能词加权（语义时空图·结构面）：问题问内部子能力（子功能行命中）
        sub_hit = len(q & idx['sub_tokens'])
        # task 权威名精确匹配：核心词与 task 完全相等（「最短路径」== task，
        # 「条件跳转编译」≠「条件跳转」——避免子串误加分）→ 强加分
        exact = 1 if n['task'] and n['task'] == core else 0
        score = (len(common) + 2 * task_hit + sub_hit + 5 * exact,
                 len(common) / max(1, len(idx['tokens'])))
        scored.append((uid, n['domain'], score, sorted(common)[:8]))
    scored.sort(key=lambda x: (-x[2][0], -x[2][1]))
    return scored[:top]


def compose(question: str, nodes=None, top: int = 5) -> dict:
    """条件编写：多单元命中 → 沿依赖边组装 → 代码（多候选择优 + verifier）。

    多分支择优：对 search 前 3 个候选各自沿依赖链扩展，选最长链（验证全过者优先）。
    """
    nodes = nodes if nodes is not None else build_graph()
    dep = build_dep_graph()
    hits = search(question, nodes, top=top)
    if not hits:
        return {"ok": False, "reason": "无命中单元", "chain": [], "code": None}
    # 多候选链：每个命中单元沿依赖边扩展；优先 top1 链（语义最相关），
    # 仅当 top1 无后继（链长 1）时才取更长候选（多分支兜底）
    # max_len 限制：自动依赖边是「c 端到端」三元组，跨链共享单元会让链
    # 串到不相关域——单链最长 6，防跨语义漂移
    MAX_CHAIN = 6
    chains = []
    seen_chains = set()
    for uid in [h[0] for h in hits[:3]]:
        chain = [uid]
        seen = set(chain)
        cur = uid
        while dep.get(cur) and len(chain) < MAX_CHAIN:
            nxt = dep[cur][0]
            if nxt in seen:
                break
            chain.append(nxt)
            seen.add(nxt)
            cur = nxt
        key = tuple(chain)
        if key not in seen_chains:
            seen_chains.add(key)
            chains.append(chain)
    chain = chains[0] if (len(chains[0]) >= 2 or len(chains) == 1) \
        else max(chains, key=len)
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
    code = "\n\n".join(code_parts)

    # verifier 校验闭环：链上每单元经本地校验器（六层，缓存命中零计算）
    # + 组装代码语法检查（生成即校验，零 LLM）
    from verifier import Verifier, VerifyRequest
    v = Verifier()
    results = []
    for uid in chain:
        u = _ALL.get(uid)
        if not u:
            continue
        r = v.verify(VerifyRequest(
            task=u['task'], code=u['pattern'], unit_id=uid,
            cases=list(u.get('cases', [])),
            expected_structure={'inject': True} if u.get('needs_inject') else {}))
        results.append({"unit": uid, "ok": r.ok, "cached": r.cached})
    import ast as _ast
    try:
        _ast.parse(code)
        syntax_ok = True
    except SyntaxError:
        syntax_ok = False
    return {"ok": True, "chain": chain, "code": code,
            "hit_units": [h[0] for h in hits],
            "verify": {"units": results,
                       "all_ok": bool(results) and all(x["ok"] for x in results),
                       "syntax_ok": syntax_ok}}


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
