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


# 自举锚点（Bootstrap Anchors，验证单元三盲区 §15.1）：
# 不可再分的底层调度/索引原语——无需被路由，构成路由的启动条件。
# 特性：①原子（无依赖更底层函数）②不参与路由图（search 不含锚点词）
# ③有中文注释（docstring 即声明）④不可再分（无子功能可递归）。
# 锚点失效条件 = 输入类型错误——由 L1 语法层兜底，元级不再需要注释级
# 声明（类型系统裁决，终止哥德尔递归堆叠 §15.2）。
BOOTSTRAP_ANCHORS = {
    "_bigrams",       # 中文二元组切分（原子变换）
    "_q_tokens",      # 问题条件词（停用词过滤）
    "_core_task",     # 任务核心词提取
    "_semantic_head", # 语义化首行（跳过三要素标记行）
    "_jaccard",       # 集合相似度（能力互斥判定）
    "_word_df",       # 词文档频率（判别力检测）
}


def bootstrap_check(nodes=None) -> dict:
    """自举验证（验证单元三盲区 → 锚点机制 §15）。

    检查每个锚点：存在（源码定义）/ 有中文注释（docstring 声明）/
    不参与路由图（search 对锚点名检索不命中能力单元——锚点不是条件
    空间成员，避免「路由路由」递归）。返回完整性报告。
    """
    import inspect as _ins
    src = _ins.getsource(_bigrams)  # 同模块源码
    report = {"anchors": [], "ok": True}
    for name in sorted(BOOTSTRAP_ANCHORS):
        fn = globals().get(name)
        entry = {"name": name}
        # ① 存在
        if fn is None:
            entry["exists"] = False
            entry["doc"] = False
            entry["reason"] = "锚点函数缺失"
            report["ok"] = False
            report["anchors"].append(entry)
            continue
        entry["exists"] = True
        # ② 有中文注释（docstring 含中文）
        doc = (fn.__doc__ or "").strip()
        has_cn = any('\u4e00' <= c <= '\u9fff' for c in doc)
        entry["doc"] = has_cn
        if not has_cn:
            entry["reason"] = "锚点缺中文注释（docstring 声明缺失）"
            report["ok"] = False
        # ③ 原子性（不调用其他锚点/路由函数——不可再分）
        body_src = _ins.getsource(fn)
        calls = [n for n in ("search(", "route(", "compose(", "escalate(")
                 if n in body_src]
        entry["atomic"] = not calls
        if calls:
            entry["reason"] = f"锚点调用了路由函数 {calls}"
            report["ok"] = False
        report["anchors"].append(entry)
    # ④ 锚点不参与路由图：build_graph 的单元库不含锚点（锚点是元层，
    # 非条件空间成员——避免「路由路由自身」递归）
    nodes = nodes if nodes is not None else build_graph()
    anchor_in_graph = [a for a in BOOTSTRAP_ANCHORS if a in nodes]
    report["anchors_in_graph"] = anchor_in_graph
    if anchor_in_graph:
        report["ok"] = False
    report["n_anchors"] = len(BOOTSTRAP_ANCHORS)
    return report


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
    """集合相似度：两串二元组集合的 Jaccard 系数（能力互斥判定）。"""
    sa, sb = _bigrams(a), _bigrams(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# 停用词（问题词中无检索价值的二元组——「写一个」类 + 请求模板词）
_STOP = {"写一", "一个", "个单", "单元", "帮我", "请写", "给我", "实现",
         "一下", "那个", "这个", "还有", "需要", "帮我写",
         # 请求模板词「写一个 X 的代码单元」：代码/的代/码单 是模板结构词，
         # 非任务条件词——若计入，任意任务与「死代码消除」单元 task 独有词
         # 「代码」重叠 → 误判混合条件冲突（反事实实验教训：累积任务误伤）
         "代码", "的代", "码单"}


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
    # 混合条件冲突（扰动实验 ② + 递归协议化）：query 同时含两侧独有条件词
    # （累积 与 门槛放行 / 检查 与 累积）→ 不强行选边 → BLINDSPOT 声明。
    # task 名独有词 + head 独有词 都纳入（门槛/放行 在 head 不在 task 名）。
    # 冲突判定：task 独有词任一侧命中即证据（权威名无碎片）；head 独有词
    # 参与时先剔除「尾缀碎片」（「导式」= 共有词「推导」的尾扩展——列表推导式
    # vs 字典推导 的「式」不对称碎片，见下方 _is_frag 注释）。
    da_t, db_t = _bigrams(ta) - _bigrams(tb), _bigrams(tb) - _bigrams(ta)
    da_h, db_h = _bigrams(ha) - _bigrams(hb), _bigrams(hb) - _bigrams(ha)
    common_h = _bigrams(ha) & _bigrams(hb)

    def _is_frag(w):
        # 尾缀碎片：w 是某共有 bigram 的尾扩展（推导 → 导式：u[1]==w[0]）
        return any(len(u) == 2 and len(w) == 2 and u[1] == w[0]
                   and u[0] != w[0] for u in common_h)

    da_h2 = {w for w in da_h if not _is_frag(w)}
    db_h2 = {w for w in db_h if not _is_frag(w)}
    # 冲突证据：task 独有命中（权威名，无碎片）或 head 独有（已剔碎片）命中。
    # 只统计判别词（df ≤ 15）：请求模板词「代码」与所有单元注释共现无判别力。
    # 且必须命中【反义对】两侧才冲突（无权↔带权 / 累积↔阈值 / 列表↔字典）：
    # 「轮询+调度」是组合相容（负载均衡轮询策略+调度语义），非条件矛盾
    # （反事实教训：加权轮询调度任务被 负载均衡 vs 报文调度 误报冲突）。
    _dfc = _word_df(nodes)
    _ANTI_WORDS = (("无权", "带权", "加权"), ("累积", "阈值", "门槛"),
                   ("列表", "字典"))
    q_hits = set()
    for group in _ANTI_WORDS:
        hit = [w for w in group if any(w in t for t in qb)]
        if hit:
            q_hits.update(hit)
    if len(q_hits) >= 2:
        # query 本身含反义对两侧（无权+带权 / 累积+阈值）→ 任务内矛盾
        ev_a = any(w in q_hits for w in (da_t | da_h2))
        ev_b = any(w in q_hits for w in (db_t | db_h2))
        if ev_a and ev_b:
            return '混合条件冲突'
    # 方向判定优先 task 权威名（干净无碎片：列表 vs 字典）；
    # task 无命中时退回 head 独有（碎片 tie 风险，但 task 命中优先已消除）
    hit_at, hit_bt = len(qb & da_t), len(qb & db_t)
    hit_ah, hit_bh = len(qb & da_h2), len(qb & db_h2)
    if hit_at or hit_bt:
        if hit_bt > hit_at:
            return (hb[:24] + '（而非 ' + ha[:12] + '）') if ha else hb[:24]
        return (ha[:24] + '（而非 ' + hb[:12] + '）') if hb else ha[:24]
    if hit_ah or hit_bh:
        if hit_bh > hit_ah:
            return (hb[:24] + '（而非 ' + ha[:12] + '）') if ha else hb[:24]
        return (ha[:24] + '（而非 ' + hb[:12] + '）') if hb else ha[:24]
    da, db = da_h2, db_h2
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


def _missing_struct(a: str, b: str, nodes, query: str = '') -> dict:
    """结构化缺失条件（GPT 7.1：subject/cond_type/a_side/b_side/polarity）。

    与 Missing Condition Accuracy 的条件结构 GT 同构（见协议 §5/§8.2）。
    fingerprint 用于条件循环检测（递归要求已搜索过的缺失条件 → 终止）。
    """
    ha = nodes.get(a, {}).get('head', '')
    hb = nodes.get(b, {}).get('head', '')
    ta = nodes.get(a, {}).get('task', '')
    tb = nodes.get(b, {}).get('task', '')
    da_t, db_t = _bigrams(ta) - _bigrams(tb), _bigrams(tb) - _bigrams(ta)
    da_h, db_h = _bigrams(ha) - _bigrams(hb), _bigrams(hb) - _bigrams(ha)
    # text 独有词（第三层）：完整注释保留括号条件词（「无权图 BFS」——
    # head 提取会剥括号 → 无权锚点丢失，方向误判 B 侧（递归协议化教训）
    ta_ix, tb_ix = nodes.get(a, {}).get('index', {}).get('text', '') or ha, \
                   nodes.get(b, {}).get('index', {}).get('text', '') or hb
    da_x, db_x = _bigrams(ta_ix) - _bigrams(tb_ix), _bigrams(tb_ix) - _bigrams(ta_ix)
    qb = _bigrams(query)
    hit_at, hit_bt = len(qb & da_t), len(qb & db_t)
    hit_ah, hit_bh = len(qb & da_h), len(qb & db_h)
    hit_ax, hit_bx = len(qb & da_x), len(qb & db_x)
    # 方向：task 权威名优先，head 次之，text 兜底（与 _diff_condition 同序）
    if hit_at != hit_bt:
        side = 'B' if hit_bt > hit_at else 'A'
    elif hit_ah != hit_bh:
        side = 'B' if hit_bh > hit_ah else 'A'
    elif hit_ax != hit_bx:
        side = 'B' if hit_bx > hit_ax else 'A'
    else:
        side = 'B' if len(db_t | db_h | db_x) > len(da_t | da_h | da_x) else 'A'

    def cn(ws):
        return sorted({w for w in ws
                       if any('\u4e00' <= c <= '\u9fff' for c in w)})[:6]
    a_side = cn(da_t | da_h)
    b_side = cn(db_t | db_h)
    # subject：query 与两侧共有词（主体：信任值/边权/容器…），无则取共有 head 词
    common_h = _bigrams(ha) & _bigrams(hb)
    subj = sorted(qb & common_h) or sorted(common_h)
    subject = ''.join(subj)[:10] or (ta or '未知主体')
    cond_type = f"{''.join(a_side[:2]) or '?'} vs {''.join(b_side[:2]) or '?'}"
    polarity = 'A侧' if side == 'A' else 'B侧'
    fingerprint = f"{subject}|{polarity}|{''.join(a_side[:2])}|{''.join(b_side[:2])}"
    return {"subject": subject, "cond_type": cond_type,
            "a_side": a_side, "b_side": b_side, "polarity": polarity,
            "fingerprint": fingerprint, "a": a, "b": b}


def route(question: str, nodes=None, top: int = 5, depth: int = 3,
          _trace=None, _seen=None, _max_depth: int = None) -> dict:
    """四态递归路由 v2（GPT 7.1 递归协议化）。

    ACCEPT：top1 分差显著 且 命中词数 ≥3 且 有效词（低 df 判别词）≥2。
    REJECT：任务与候选不适用条件冲突（search 已排除）。
    DEFER：top1/top2 分差小（邻域相关）→ 识别缺失条件 → 递归检索。
    BLINDSPOT：递归到底仍无法归属（记录 任务/候选/缺失条件/路径）。
    DEFER_EXHAUSTED（新）：递归终止保护触发——深度耗尽 / 条件循环 /
      信息增益不足（递归每一轮必须让条件空间变小，否则终止）。
    四保护（GPT §二）：max_depth（默认 3）/ 循环检测 / 信息增益门槛 / 递归预算。
    """
    nodes = nodes if nodes is not None else build_graph()
    _max_depth = _max_depth if _max_depth is not None else depth
    _trace = _trace if _trace is not None else []
    _seen = _seen if _seen is not None else set()
    df = _word_df(nodes)
    hits = search(question, nodes, top=top)
    if not hits:
        return {"state": "BLINDSPOT", "decision_layer": "L3", "reason": "无候选",
                "path": [question[:30]], "trace": list(_trace),
                "candidate_count": 0}
    # 任务内矛盾检测（GPT §四 C 类 + §7.4 反事实）：
    # ① 词级矛盾：query 同时含反义条件对（无权+带权/加权、累积+阈值检查…）
    # ② 候选冲突：query 同时命中候选能力词与能力级不适用条件词。
    # 被 search 排除的候选（能力级互斥）不在 hits——但任务词内部矛盾
    # 仍可识别（无权 BFS 求带权图 = 自相矛盾 → BLINDSPOT 不强行路由）。
    _ANTI = [
        # (正侧条件词, 负侧条件词)——真正的互斥反义对：
        # 无权(BFS 侧) vs 带权/加权(Dijkstra 侧)
        (("无权",), ("带权", "加权")),
        # 累积 vs 阈值检查/门槛放行（信任引擎两侧）
        (("累积",), ("阈值", "门槛")),
        # 列表 vs 字典（推导式容器两侧）
        (("列表",), ("字典",)),
    ]
    qtoks = _q_tokens(question)
    cand_before = len(hits)
    anti_hit = None
    for pos, neg in _ANTI:
        p_hit = any(any(w in t for w in pos) for t in qtoks)
        n_hit = any(any(w in t for w in neg) for t in qtoks)
        if p_hit and n_hit:
            anti_hit = (pos, neg)
            break
    conflict_not = []
    for h in hits[:3]:
        uid = h[0]
        nt = nodes[uid]['index'].get('not_tokens', set())
        toks = nodes[uid]['index'].get('tokens', set())
        overlap = sorted(qtoks & nt)
        # 能力级不适用条件词：df 低判别词 且 非该单元自身索引词
        # （「导式」∈ 集合推导 tokens=公共后缀碎片，非能力级边界；
        #  「列表/表推」∉ tokens=真边界——集合推导不负责列表推导）
        strong = [w for w in overlap
                  if df.get(w, 99) <= 11
                  and w not in ('不适用', '适用', '条件', '时返', '则不')
                  and w not in toks]
        if strong:
            conflict_not.append({"unit": uid, "conflict_words": strong})
    if anti_hit or conflict_not:
        return {"state": "BLINDSPOT", "decision_layer": "L3", "reason": "任务内矛盾（条件词冲突）",
                "anti_pair": [list(anti_hit[0]) + list(anti_hit[1])]
                if anti_hit else None,
                "conflict": conflict_not,
                "candidates": [h[0] for h in hits[:3]],
                "path": [question[:30], f"矛盾:{anti_hit or conflict_not[:1]}"],
                "trace": list(_trace), "candidate_count": cand_before}
    # 伪造条件检测（GPT §7.4 6 类）：query 含 df=0 的词（条件空间不存在）
    # → 任务声称不存在的条件（「超光速引擎驱动信任累积」——引擎词无单元
    # 覆盖，但「信任累积」真实词会带偏路由）→ BLINDSPOT 不假装存在该能力。
    # 排除停用/模板词（已在 _q_tokens 剔除）；只查中文词（英文标识符/变量
    # 名不参与条件空间判定——df=0 是正常（函数参数名等））
    # 伪造条件检测（GPT §7.4 6 类）：任务声称不存在的条件概念。
    # 真伪造 = 连续未知 2-gram 段 ≥3 且段内词无已知词锚定：
    #   「超光速引擎」= 超光/光速/速引 3 段连续未知，无已知词贯穿
    #   （引擎 df>0 是真实概念「信任引擎」——伪造的是修饰词「超光速」）。
    # 豁免一（动词短语）：「把序列映射成列表」的 列映/射成/成列 3 段未知，
    #   但每个词左右邻接已知词（序列/映射/列表）——跨界词特征。
    # 豁免二（语义空词）：「信任相关功能」的 任相/相关/关功 段含泛化修饰词
    #   （相关/功能/处理）——非伪造概念（超光速是虚构名词，相关是修饰语）。
    _GENERIC = set('相关功能处理涉及有关进行以及关于的与和')
    fabricated = []
    zero_w = sorted({w for w in qtoks
                     if df.get(w, 0) == 0
                     and any('\u4e00' <= c <= '\u9fff' for c in w)})
    used = set()
    for w in zero_w:
        if w in used:
            continue
        seg = {w}
        changed = True
        while changed:
            changed = False
            for x in zero_w:
                if x not in seg and (
                        any(s[1] == x[0] for s in seg)
                        or any(x[1] == s[0] for s in seg)):
                    seg.add(x)
                    changed = True
        used |= seg
        if len(seg) < 3:
            continue
        # 豁免二：段含语义空词字符（相关/功能/处理…）→ 修饰语非伪造
        if any(c in _GENERIC for s in seg for c in s):
            continue
        # 豁免一：段内每个词都邻接已知词（左右端连向已知 2-gram）→ 动词短语
        all_anchored = True
        for s in seg:
            left_ok = any(k[1] == s[0] for k in qtoks if k not in zero_w)
            right_ok = any(s[1] == k[0] for k in qtoks if k not in zero_w)
            if not (left_ok or right_ok):
                all_anchored = False
                break
        if not all_anchored:
            fabricated.extend(seg)
    if fabricated:
        return {"state": "BLINDSPOT", "decision_layer": "L3", "reason": "伪造条件（任务条件词不在条件空间）",
                "fabricated_words": sorted(set(fabricated))[:6],
                "candidates": [h[0] for h in hits[:3]],
                "path": [question[:30], f"伪造:{sorted(set(fabricated))[:3]}"],
                "trace": list(_trace), "candidate_count": cand_before}
    top1 = hits[0]
    top2 = hits[1] if len(hits) > 1 else None
    gap = (top1[2][0] - top2[2][0]) if top2 else 99
    # 有效词（低 df 判别词）——泛化词（功能/存在/检查 等多单元共现）不算
    meaningful = [w for w in top1[3] if df.get(w, 99) <= 11]
    # 情绪方向性偏好工程化（PROP-EMO-DIRECTION-002 + DECISION-LAYER-003）：
    # convergence_bias = 收敛倾向系数（类比情感权重 0.1-0.3 的加速因子）。
    # 决策分层：L1 日常（高置信快速 ACCEPT，0-1 层递归）/
    #           L2 重要（低置信 DEFER 递归）/ L3 存在级（BLINDSPOT 不覆盖）。
    # 情绪不覆盖存在级：BLINDSPOT/冲突不因倾向性强转。
    if (gap >= 2 or top2 is None) and top1[2][0] >= 3 and len(meaningful) >= 2:
        # 路由置信度（DaoTi coherence 吸纳，§daoti）：命中分归一化 [0,1]
        # 连续置信度——DaoTi 用余弦相似度+阈值决定生成与否；我们补
        # 连续置信度字段供上层（escalation/执行计划）按阈值决策
        # （低置信 ACCEPT 可降级 DEFER/人工确认）。不改变硬规则判定。
        _max_possible = max(1.0, top1[2][0] + (gap if top2 else 0))
        confidence = round(min(1.0, top1[2][0] / _max_possible), 3)
        # 决策分层（情绪方向性偏好的工程参数）：
        # L1 日常决策（confidence 高 → 强倾向快速收敛，0-1 层递归）
        decision_layer = "L1" if confidence >= 0.7 else "L2"
        return {"state": "ACCEPT", "unit": top1[0], "score": top1[2][0],
                "confidence": confidence,
                "decision_layer": decision_layer,
                "convergence_bias": round(0.3 - (confidence - 0.5) * 0.5, 3),
                "path": [question[:30]], "trace": list(_trace),
                "candidate_count": 1}
    # DEFER 前置：任务判别力不足（有效词 0）→ BLINDSPOT（盲区声明，
    # 不强行递归——「不存在的功能」仅泛化词命中，无真实邻域可递归）
    if not meaningful:
        return {"state": "BLINDSPOT",
                "reason": "判别力不足（仅泛化词命中）",
                "decision_layer": "L3",
                "candidates": [h[0] for h in hits[:3]],
                "path": [question[:30]], "trace": list(_trace),
                "candidate_count": cand_before}
    # DEFER：候选邻域相关（top1/top2 分差小）→ 缺失条件方向对齐任务
    missing = _diff_condition(top1[0], top2[0], nodes, question)
    mc = _missing_struct(top1[0], top2[0], nodes, question)
    # 混合条件冲突：任务同时含两侧独有条件词（累积+门槛放行）→ 盲区声明，
    # 不强行选边（扰动实验 ②——条件冲突不该被递归掩盖）。
    # 跨候选检测：冲突对可能在 top1/top2 之外（top1=信任检查、top3=VM-信任累积）
    # ——扫描 top3 两两对（递归协议化教训：只查 top1/top2 会漏冲突）
    if missing == '混合条件冲突' or any(
            _diff_condition(hits[i][0], hits[j][0], nodes, question)
            == '混合条件冲突'
            for i in range(min(3, len(hits)))
            for j in range(i + 1, min(3, len(hits)))):
        return {"state": "BLINDSPOT", "decision_layer": "L3", "reason": "混合条件冲突（任务同时含两侧独有条件）",
                "candidates": [h[0] for h in hits[:3]],
                "missing": missing, "missing_struct": mc,
                "path": [question[:30], f"缺:{missing}"],
                "trace": list(_trace), "candidate_count": cand_before}
    # 保护 ① 递归深度上限：剩余 depth ≤1 → 递归耗尽（DEFER_EXHAUSTED）
    if depth <= 1:
        return {"state": "DEFER_EXHAUSTED", "reason": "递归深度耗尽（max_depth 内未收敛）",
                "candidates": [h[0] for h in hits[:3]],
                "missing": missing, "missing_struct": mc,
                "path": [question[:30], f"缺:{missing}"],
                "trace": list(_trace), "candidate_count": cand_before}
    # 保护 ② 条件循环检测：缺失条件已搜索过（fingerprint 命中）→ 不收敛
    fp = mc['fingerprint']
    if fp in _seen:
        return {"state": "DEFER_EXHAUSTED", "reason": "条件循环（缺失条件已搜索过）",
                "candidates": [h[0] for h in hits[:3]],
                "missing": missing, "missing_struct": mc,
                "path": [question[:30], f"缺:{missing}"],
                "trace": list(_trace), "candidate_count": cand_before}
    _seen = _seen | {fp}
    # 递归只带缺失侧描述（「（而非 …）」是另一侧，带入会重新引入噪声词
    # → 递归偏航——扰动实验教训）
    miss_side = missing.split('（而非')[0].split('(而非')[0].strip() or missing
    new_q = f"写一个{miss_side}的代码单元"
    r = route(new_q, nodes, top, depth - 1, _trace, _seen, _max_depth)
    cand_after = r.get("candidate_count", cand_before)
    gain = round((cand_before - cand_after) / cand_before, 3) if cand_before else 0.0
    # 保护 ③ 信息增益门槛：递归后未 ACCEPT 且候选未收敛（gain ≤0）
    # → 无效递归终止（每一轮必须让条件空间变小，否则不继续）
    if r["state"] != "ACCEPT" and gain <= 0:
        r = {"state": "DEFER_EXHAUSTED", "reason": "信息增益不足（候选未收敛）",
             "candidates": [h[0] for h in hits[:3]],
             "missing": missing, "missing_struct": mc,
             "path": [question[:30], f"缺:{missing}"],
             "trace": list(_trace), "candidate_count": cand_after}
    r["path"] = [question[:30], f"缺:{missing}"] + r.get("path", [])
    r["defer_from"] = [top1[0], top2[0]]
    r["trace"] = _trace + [{
        "depth": _max_depth - depth + 1,
        "question": question[:30],
        "state": "DEFER",
        "missing_condition": mc,
        "candidate_count_before": cand_before,
        "candidate_count_after": cand_after,
        "information_gain": gain,
        "next_query": new_q[:40],
    }]
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


def escalate(question: str, nodes=None, top: int = 5, depth: int = 3) -> dict:
    """分层判断（escalation，荣 理论补充 §13）。

    子系统无法识别 → 父系统判断 → 全层无法判断 → BLINDSPOT。
    L1 单层四态路由 → L2 域级判断（父系统：detect_domain 定位域 +
    域内多候选聚合）→ L3 跨域组合判断（更高父：compose 依赖链）→
    L4 终层 BLINDSPOT（escalation_trace 记录每层理由——盲区是所有层的
    共同结论，非第一层失败）。
    """
    nodes = nodes if nodes is not None else build_graph()
    r = route(question, nodes, top=top, depth=depth)
    # 子系统未决（BLINDSPOT / DEFER_EXHAUSTED 递归耗尽）→ 升级父系统；
    # ACCEPT/REJECT/DEFER 已决 → 不升级
    if r["state"] in ("ACCEPT", "REJECT", "DEFER"):
        return r
    # 硬盲区（升级无意义——条件空间外的概念/矛盾，父系统同空间也判不了）：
    # 伪造条件/任务内矛盾/混合冲突 是「概念不存在」或「条件互斥」——
    # 升级到域/组合层不会改变结论（同一条件空间），直接终层 BLINDSPOT
    _HARD = ("伪造条件", "任务内矛盾", "混合条件冲突")
    hard_reason = r.get("reason", "")
    if any(h in hard_reason for h in _HARD):
        r = dict(r)
        r["escalation_trace"] = [{"level": "L1",
                                  "reason": hard_reason,
                                  "note": "硬盲区（条件空间外/互斥）——升级无意义"}]
        r["final"] = "硬盲区：条件空间外概念或互斥条件——所有层同空间，标记盲区"
        return r
    trace = [{"level": "L1", "reason": r.get("reason", r["state"])}]
    qtoks = _q_tokens(question)
    # L2 域级判断（父系统）：任务词能否定位到域 + 域内有候选群
    domain = None
    try:
        from code_compose import detect_domain
        domain = detect_domain(question)
    except Exception:
        domain = None
    if domain:
        dom_cands = [h for h in search(question, nodes, top=top)
                     if h[1] == domain]
        if len(dom_cands) >= 2:
            trace.append({"level": "L2", "reason": f"父系统定位域={domain}"
                          f"（{len(dom_cands)} 候选）——条件仍缺"})
            return {"state": "DEFER", "reason": f"域已定（{domain}）条件仍缺",
                    "domain": domain, "candidates": [h[0] for h in dom_cands[:3]],
                    "escalation_trace": trace, "path": [question[:30]],
                    "trace": r.get("trace", [])}
        trace.append({"level": "L2", "reason": f"定位域={domain} 但候选不足"
                      f"（{len(dom_cands)}）"})
    else:
        trace.append({"level": "L2", "reason": "域无法定位（跨域/泛化）"})
    # L3 跨域组合判断（更高父系统）：compose 能否组装 ≥2 依赖链，
    # 且命中单元覆盖 ≥2 个域（真正跨域组装——auto_dep_edges 会把整个
    # 测试文件串成超长链，任意任务都能「组装」→ 必须要求多域命中才
    # 算组合路径存在，否则连「无意义」任务也 DEFER）。
    # 另要求任务有【中文实义判别词】命中（非全泛化词）：「zzzqqq 功能」
    # 命中全靠泛化词「功能」（df=681）——无实义，不构成组合路径。
    try:
        cp = compose(question, nodes, top=top)
        chain = cp.get("chain", [])
        hit_units = cp.get("hit_units", [])
        doms = {nodes.get(u, {}).get("domain") for u in hit_units}
        doms.discard(None)
        _dfc2 = _word_df(nodes)
        has_meaningful = any(
            w in qtoks and _dfc2.get(w, 99) <= 11
            for h in search(question, nodes, top=top)
            for w in h[3])
        if len(chain) >= 2 and len(doms) >= 2 and has_meaningful:
            trace.append({"level": "L3", "reason": f"跨域组合路径可组装"
                          f"（{len(chain)} 链，域 {sorted(doms)}）"})
            return {"state": "DEFER", "reason": "跨域组合路径存在",
                    "chain": chain, "domains": sorted(doms),
                    "escalation_trace": trace,
                    "path": [question[:30]], "trace": r.get("trace", [])}
        trace.append({"level": "L3", "reason": f"无跨域组合路径"
                      f"（链{len(chain)} 域{len(doms)} "
                      f"实义词={has_meaningful}）"})
    except Exception as e:
        trace.append({"level": "L3", "reason": f"组合判断异常: {str(e)[:30]}"})
    # L4 终层：全层无法判断 → BLINDSPOT（盲区是所有层的共同结论）
    r = dict(r)
    r["escalation_trace"] = trace
    r["final"] = "全层无法判断 → 标记盲区（不强行选择）"
    return r


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
