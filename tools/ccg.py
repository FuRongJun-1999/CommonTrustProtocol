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
    """从条件论注释提取索引：{注释文本, 子功能词, 生效条件词, 不适用条件词, 缩写同义词}。

    三要素行分离（语义时空图·结构面）：
      子功能行（内部功能分解）→ sub_tokens
      生效条件行（前置条件）→ cond_tokens
      不适用条件行（盲区声明·负路由）→ not_tokens（任务与其冲突 → 排除）
      功能名/执行行 → tokens（主索引）
    """
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    text = ' '.join(lines)
    sub_lines = [ln for ln in lines if ln.startswith('子功能')]
    cond_lines = [ln for ln in lines if ln.startswith('生效条件')]
    not_lines = [ln for ln in lines if ln.startswith('不适用条件')]
    abbrs = {}
    for m in _ABBR_CN.finditer(text):
        abbrs[m.group(1)] = m.group(2)
    syn = {w for w in abbrs.values() if len(w) >= 2}
    # 不适用条件通用词剔除：自动生成草稿的「为空/非法/越界/参数/返回」等
    # 泛化词与任务描述词易重叠 → 误排除正常单元（盲测 Top-1 100%→76% 教训）
    _NOT_GENERIC = {"为空", "空非", "非法", "法时", "越界", "界时", "参数",
                    "数为", "输入", "入不", "不满", "满足", "足生", "生效",
                    "件时", "返回", "回N", "None", "不执", "执行", "不适用",
                    "适用", "条件", "时返", "则不"}
    idx = {
        'text': text,
        'abbrs': abbrs,
        'tokens': _bigrams(text) | syn,
        'sub_tokens': _bigrams(' '.join(sub_lines)),
        'cond_tokens': _bigrams(' '.join(cond_lines)),
        # 负路由只统计中文二元组：英文 bigram（'DUP'→'DU','UP'）是无语义噪声，
        # 会与任务英文词误重叠 → 误排除正常单元（盲测 Top-1 76% 教训）
        'not_tokens': {b for b in _bigrams(' '.join(not_lines)) - _NOT_GENERIC
                       if any('\u4e00' <= c <= '\u9fff' for c in b)},
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
    nodes = {}  # uid -> {domain, task, head, index}
    for dname, units in domains:
        for uid, u in units.items():
            idx = extract_comment_index(u.get('pattern', ''))
            nodes[uid] = {'domain': dname, 'task': u.get('task', ''),
                          'head': _semantic_head(u.get('pattern', '')),
                          'index': idx}
    # 能力级负路由（GPT：参数级=能不能执行，能力级=该不该执行）：
    # 同域 head 高重叠单元互斥——A 不负责 B → B 的【独有词】进 A 的排除集
    # （B 独有词 = B head - A head；正任务含 A 词不含 B 独有词 → 不误伤；
    #  对抗任务（B 描述含 B 独有词）→ 与 A 的 not_tokens 重叠 → A 排除）。
    for uid, n in nodes.items():
        best, best_j = None, 0.0
        for oid, on in nodes.items():
            if oid == uid or on['domain'] != n['domain']:
                continue
            j = _jaccard(n['head'], on['head'])
            if j > best_j:
                best, best_j = oid, j
        if best and best_j >= 0.12:
            own = _bigrams(n['head'])
            n['index']['not_tokens'] |= _bigrams(nodes[best]['head']) - own
    return nodes


def _semantic_head(code: str) -> str:
    """语义化首行描述（跳过三要素标记行）。"""
    lines = [ln.strip().lstrip('#').strip()
             for ln in code.splitlines() if ln.strip().startswith('#')]
    head = next((ln for ln in lines
                 if not ln.startswith(('生效条件', '子功能', '执行',
                                       '不适用条件', '返回', '功能条件'))), '')
    # 保留冒号前的语义名（「列表推导式：」→ 列表推导式 是任务判别词，
    # 剥掉会丢容器/算法词 → 缺失条件无法辨识（Missing Condition 教训））
    # name 先去括号（「BFS 遍历（广度优先搜索）」→ BFS 遍历）再判长度，
    # 否则带同义词括号的语义名超长被丢（页置换/本地存储 教训）
    name, body = '', head
    if '：' in head:
        name, _, body = head.partition('：')
    elif ':' in head:
        name, _, body = head.partition(':')
    if name:
        clean_name = re.sub(r'[（(][^）)]*[）)]', '', name).strip()
        if len(clean_name) <= 8 and body.strip():
            desc = clean_name + ' ' + body.strip()
        else:
            desc = body
    else:
        desc = body
    return re.sub(r'[（(][^）)]*[）)]', '', desc).strip()


def _jaccard(a: str, b: str) -> float:
    sa, sb = _bigrams(a), _bigrams(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


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
        # 负路由（盲区声明·条件冲突排除）：任务条件词与候选「不适用条件」
        # 重叠 ≥2 → 该候选不适用当前任务 → 排除（条件不满足 → 不路由）
        not_hit = len(q & idx.get('not_tokens', set()))
        if not_hit >= 2:
            continue
        # 命中词数 + task 权威名加权（task == core 或 core 以 task 结尾——
        # 「路径解析」是「文件系统路径解析」的动作后缀 ✓，「文件系统」是
        # 前缀修饰非动作 ✗——动作词优先，避免修饰词误加权）+ 注释覆盖率
        # 注：子功能词加权（sub_hit）经消融实验验证为负优化（D 97% < C 100%，
        # 子功能行泛化词干扰排序）——已移除，统一全注释 tokens 加权
        task_hit = 2 if n['task'] and (n['task'] == core
                                       or core.endswith(n['task'])) else 0
        # task 权威名共享（「字节码编码」vs task「字节码序列化」共享 字节码
        # 前缀 → 序列化破 tie 胜指令大小；编码=序列化动作语义）
        task_shared = 1 if n['task'] and (
            _bigrams(n['task']) & _bigrams(core)) else 0
        # task 权威名精确匹配：核心词与 task 完全相等（「最短路径」== task，
        # 「条件跳转编译」≠「条件跳转」——避免子串误加分）→ 强加分
        exact = 1 if n['task'] and n['task'] == core else 0
        score = (len(common) + 2 * task_hit + task_shared + 5 * exact,
                 len(common) / max(1, len(idx['tokens'])))
        scored.append((uid, n['domain'], score, sorted(common)[:8]))
    scored.sort(key=lambda x: (-x[2][0], -x[2][1]))
    return scored[:top]


def _diff_condition(a: str, b: str, nodes, query: str = '') -> str:
    """DEFER 缺失条件：候选 a/b 的条件差异（head 独有侧的能力描述）。

    缺失条件 = 决定两能力边界的信息（a 有 b 没有 / b 有 a 没有的 head 侧）。
    方向对齐任务（扰动实验教训）：query 含哪侧独有词 → 缺失条件指哪侧，
    否则 DEFER 递归会偏航到错误一侧（累积任务 → 阈值检查）。
    """
    ha = nodes.get(a, {}).get('head', '')
    hb = nodes.get(b, {}).get('head', '')
    if not ha and not hb:
        return '细分条件'
    # 语义名方向（扰动实验教训）：task 权威名独有词（列表推导-字典推导 →
    # 独有「字典」）与 query 重叠 → 缺失条件指该侧。head bigram 差集会
    # 被碎片（「导式」=推导式尾巴）干扰 tie，task 名干净无碎片。
    ta, tb = nodes.get(a, {}).get('task', ''), nodes.get(b, {}).get('task', '')
    qb = _bigrams(query)
    # 混合条件冲突（扰动实验 ②）：query 同时含两侧独有条件词
    # （累积 与 门槛放行）→ 不强行选边 → BLINDSPOT 声明。
    # task 名独有词 + head 独有词 都纳入（门槛/放行 在 head 不在 task 名）
    da_t, db_t = _bigrams(ta) - _bigrams(tb), _bigrams(tb) - _bigrams(ta)
    da_h, db_h = _bigrams(ha) - _bigrams(hb), _bigrams(hb) - _bigrams(ha)
    hit_at, hit_bt = len(qb & da_t), len(qb & db_t)
    hit_ah, hit_bh = len(qb & da_h), len(qb & db_h)
    # 并集去重（「字典」同时在 task 独有和 head 独有 → 只算一次，
    # 否则同一证据重复计数造成假冲突）
    hit_a, hit_b = len(qb & (da_t | da_h)), len(qb & (db_t | db_h))
    # 混合条件冲突需多重证据：两侧都命中且总命中 ≥3。
    # 单侧碎片（「导式」=推导式公共后缀的不对称碎片，1 个）不构成冲突；
    # 真冲突（累积 + 门槛放行）至少一侧 ≥2。
    if hit_a and hit_b and (hit_a + hit_b) >= 3:
        return '混合条件冲突'
    # 方向判定优先 task 权威名（干净无碎片：列表 vs 字典）；
    # task 无命中时退回 head 独有（碎片 tie 风险，但 task 命中优先已消除）
    if hit_at or hit_bt:
        if hit_bt > hit_at:
            return (hb[:24] + '（而非 ' + ha[:12] + '）') if ha else hb[:24]
        return (ha[:24] + '（而非 ' + hb[:12] + '）') if hb else ha[:24]
    if hit_ah or hit_bh:
        if hit_bh > hit_ah:
            return (hb[:24] + '（而非 ' + ha[:12] + '）') if ha else hb[:24]
        return (ha[:24] + '（而非 ' + hb[:12] + '）') if hb else ha[:24]
    da, db = da_h, db_h
    # 任务方向：query 与哪侧独有词重叠更多 → 缺失条件指该侧
    hit_a, hit_b = len(qb & da), len(qb & db)
    prefer_b = (hit_b > hit_a and db) or (not hit_a and not hit_b and
                                          len(db) >= len(da) and db)
    if prefer_b:
        return (hb[:24] + '（而非 ' + ha[:12] + '）') if ha else hb[:24]
    if da:
        return (ha[:24] + '（而非 ' + hb[:12] + '）') if hb else ha[:24]
    return '细分条件'


_DF_CACHE = None


def _word_df(nodes) -> dict:
    """词文档频率：出现该词的单元数（泛化词检测——判别力）。"""
    global _DF_CACHE
    if _DF_CACHE is not None:
        return _DF_CACHE
    df = {}
    for n in nodes.values():
        for w in n['index']['tokens']:
            df[w] = df.get(w, 0) + 1
    _DF_CACHE = df
    return df


def route(question: str, nodes=None, top: int = 5, depth: int = 3) -> dict:
    """四态递归路由（GPT：ACCEPT/REJECT/DEFER/BLINDSPOT + 缺失条件递归）。

    ACCEPT：top1 分差显著 且 命中词数 ≥3 且 有效词（低 df 判别词）≥2。
    REJECT：任务与候选不适用条件冲突（search 已排除）。
    DEFER：top1/top2 分差小（邻域相关）→ 识别缺失条件 → 递归检索。
    BLINDSPOT：递归到底仍无法归属（记录 任务/候选/缺失条件/路径——盲区声明）。
    """
    nodes = nodes if nodes is not None else build_graph()
    df = _word_df(nodes)
    hits = search(question, nodes, top=top)
    if not hits:
        return {"state": "BLINDSPOT", "reason": "无候选",
                "path": [question[:30]]}
    top1 = hits[0]
    top2 = hits[1] if len(hits) > 1 else None
    gap = (top1[2][0] - top2[2][0]) if top2 else 99
    # 有效词（低 df 判别词）——泛化词（功能/存在/检查 等多单元共现）不算
    meaningful = [w for w in top1[3] if df.get(w, 99) <= 11]
    if (gap >= 2 or top2 is None) and top1[2][0] >= 3 and len(meaningful) >= 2:
        return {"state": "ACCEPT", "unit": top1[0], "score": top1[2][0],
                "path": [question[:30]]}
    # DEFER 前置：任务判别力不足（有效词 0）→ BLINDSPOT（盲区声明，
    # 不强行递归——「不存在的功能」仅泛化词命中，无真实邻域可递归）
    if not meaningful:
        return {"state": "BLINDSPOT",
                "reason": "判别力不足（仅泛化词命中）",
                "candidates": [h[0] for h in hits[:3]],
                "path": [question[:30]]}
    # DEFER：候选邻域相关（top1/top2 分差小）→ 缺失条件方向对齐任务
    missing = _diff_condition(top1[0], top2[0], nodes, question)
    # 混合条件冲突：任务同时含两侧独有条件词（累积+门槛放行）→ 盲区声明，
    # 不强行选边（扰动实验 ②——条件冲突不该被递归掩盖）
    if missing == '混合条件冲突':
        return {"state": "BLINDSPOT", "reason": "混合条件冲突（任务同时含两侧独有条件）",
                "candidates": [h[0] for h in hits[:3]],
                "missing": missing, "path": [question[:30], f"缺:{missing}"]}
    if depth <= 1:
        return {"state": "BLINDSPOT", "candidates": [h[0] for h in hits[:3]],
                "missing": missing, "path": [question[:30], f"缺:{missing}"]}
    # 递归只带缺失侧描述（「（而非 …）」是另一侧，带入会重新引入噪声词
    # → 递归偏航——扰动实验教训）
    miss_side = missing.split('（而非')[0].split('(而非')[0].strip() or missing
    new_q = f"写一个{miss_side}的代码单元"
    r = route(new_q, nodes, top, depth - 1)
    r["path"] = [question[:30], f"缺:{missing}"] + r.get("path", [])
    r["defer_from"] = [top1[0], top2[0]]
    return r


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
