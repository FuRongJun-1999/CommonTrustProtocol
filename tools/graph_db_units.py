# -*- coding: utf-8 -*-
"""graph_db_units.py · 图数据库白箱单元库（第六阶段·目标6 条件图数据库的初级复现）
用户设想：终极目标「条件图数据库」← 初级复现「图数据库」。
与白箱条件路由图同构：知识=节点、条件链=边、遍历=条件链组合、持久化=存储层。
单元：{任务 → 代码模式模板 + 验证样例 + 校准基准}——白箱自举（外部只校准）。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

GRAPH_UNITS = {
    "图存储-节点边": {
        "task": "图存储",
        "pattern": (
            "class Graph:\n"
            "    # 图存储：节点 + 有向边（知识=节点，条件链=边）\n"
            "    def __init__(self):\n"
            "        self.nodes = set()\n"
            "        self.edges = {}   # src -> [dst]\n"
            "    def add_node(self, name):\n"
            "        self.nodes.add(name)\n"
            "        self.edges.setdefault(name, [])\n"
            "    def add_edge(self, src, dst):\n"
            "        self.add_node(src)\n"
            "        self.add_node(dst)\n"
            "        if dst not in self.edges[src]:\n"
            "            self.edges[src].append(dst)\n"
            "    def neighbors(self, name):\n"
            "        return list(self.edges.get(name, []))\n"
            "    def remove_edge(self, src, dst):\n"
            "        # 动态图：边删除（增量更新支持）\n"
            "        if src in self.edges and dst in self.edges[src]:\n"
            "            self.edges[src].remove(dst)\n"
            "def graph_ops():\n"
            "    g = Graph()\n"
            "    g.add_edge('气压低', '沸点降')\n"
            "    g.add_edge('沸点降', '煮不熟')\n"
            "    return (sorted(g.nodes), g.neighbors('气压低'))\n"),
        "cases": [("call", (["气压低", "沸点降", "煮不熟"], ["沸点降"]))],
        "params": [],
        "calibration": "对照：条件路由图——知识=节点、条件链=边（气压低→沸点降→煮不熟 条件链）",
    },
    "图遍历-BFS": {
        "task": "图遍历",
        "pattern": (
            "def reachable(graph, start):\n"
            "    # BFS 遍历：从起点出发可达的所有节点（条件链组合——影响传播）\n"
            "    from collections import deque\n"
            "    visited, queue = {start}, deque([start])\n"
            "    while queue:\n"
            "        cur = queue.popleft()\n"
            "        for nxt in graph.neighbors(cur):\n"
            "            if nxt not in visited:\n"
            "                visited.add(nxt)\n"
            "                queue.append(nxt)\n"
            "    return sorted(visited)\n"),
        "cases": [((None, "气压低"), ["气压低", "沸点降", "煮不熟"])],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：条件链组合——从条件出发传播可达的规律（灵枢因果传播同构）",
    },
    "图遍历-路径": {
        "task": "路径查找",
        "pattern": (
            "def has_path(graph, start, end):\n"
            "    # 路径存在性：start 能否到达 end（条件链是否存在）\n"
            "    if start == end:\n"
            "        return True\n"
            "    from collections import deque\n"
            "    visited, queue = {start}, deque([start])\n"
            "    while queue:\n"
            "        cur = queue.popleft()\n"
            "        for nxt in graph.neighbors(cur):\n"
            "            if nxt == end:\n"
            "                return True\n"
            "            if nxt not in visited:\n"
            "                visited.add(nxt)\n"
            "                queue.append(nxt)\n"
            "    return False\n"),
        "cases": [((None, "气压低", "煮不熟"), True),
                  ((None, "煮不熟", "气压低"), False)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：条件链——气压低→沸点降→煮不熟 有路径；反向无（条件链有向）",
    },
    "图持久化-序列化": {
        "task": "图序列化",
        "pattern": (
            "def graph_to_json(graph):\n"
            "    # 图 → JSON 字符串（条件图数据库存储层）\n"
            "    import json\n"
            "    return json.dumps({'nodes': sorted(graph.nodes),\n"
            "                        'edges': {k: v for k, v in sorted(graph.edges.items())}},\n"
            "                       ensure_ascii=False)\n"
            "def graph_from_json(text):\n"
            "    # JSON → 图（存储加载）\n"
            "    import json\n"
            "    data = json.loads(text)\n"
            "    g = Graph()\n"
            "    for n in data['nodes']:\n"
            "        g.add_node(n)\n"
            "    for src, dsts in data['edges'].items():\n"
            "        for d in dsts:\n"
            "            g.add_edge(src, d)\n"
            "    return g\n"),
        "cases": [("call", '{"nodes": [], "edges": {}}')],
        "params": [],
        "calibration": "对照：条件图数据库——图序列化持久化（JSON 存储层）",
    },
    "条件路由图-映射": {
        "task": "条件路由映射",
        "pattern": (
            "def units_to_graph(units):\n"
            "    # 条件单元库 → 条件路由图：知识=节点，conditions=入边（条件→知识）\n"
            "    # units: {知识名: {'conditions': [条件...]}}\n"
            "    g = Graph()\n"
            "    for name, u in units.items():\n"
            "        g.add_node(name)\n"
            "        for c in u.get('conditions', []):\n"
            "            g.add_edge(c, name)   # 条件 → 知识（条件链）\n"
            "    return g\n"),
        "cases": [(({"沸点降": {"conditions": ["气压低"]},
                     "煮不熟": {"conditions": ["沸点降"]}},), ["沸点降"])],
        "params": [],
        "calibration": "对照：条件单元库（{条件→规律}）→ 条件路由图（第4阶段知识图同构）",
    },
    "图持久化-文件": {
        "task": "图文件",
        "pattern": (
            "def save_graph(graph, path):\n"
            "    # 图 → .cgdb 文件（条件图数据库文件）\n"
            "    import json\n"
            "    with open(path, 'w', encoding='utf-8') as f:\n"
            "        json.dump({'nodes': sorted(graph.nodes),\n"
            "                   'edges': {k: v for k, v in sorted(graph.edges.items())}},\n"
            "                  f, ensure_ascii=False)\n"
            "    return path\n"
            "def load_graph(path):\n"
            "    # .cgdb 文件 → 图（条件图数据库加载）\n"
            "    import json\n"
            "    with open(path, 'r', encoding='utf-8') as f:\n"
            "        data = json.load(f)\n"
            "    g = Graph()\n"
            "    for n in data['nodes']:\n"
            "        g.add_node(n)\n"
            "    for src, dsts in data['edges'].items():\n"
            "        for d in dsts:\n"
            "            g.add_edge(src, d)\n"
            "    return g\n"
            "def graph_file_ops():\n"
            "    # 组装：Graph + save + load 往返（条件图数据库持久化）\n"
            "    g = Graph()\n"
            "    g.add_edge('气压低', '沸点降')\n"
            "    path = save_graph(g, 'test.cgdb')\n"
            "    g2 = load_graph(path)\n"
            "    import os\n"
            "    os.remove(path)\n"
            "    return g2.neighbors('气压低')\n"),
        "cases": [("call", ["沸点降"])],
        "params": [],
        "calibration": "对照：条件图数据库——.cgdb 文件持久化（存储层升级：JSON→文件）",
    },
    "图遍历-路径枚举": {
        "task": "路径枚举",
        "pattern": (
            "def all_paths(graph, start, end, max_len=5):\n"
            "    # 枚举 start→end 所有路径（条件链组合——可解释路径）\n"
            "    paths = []\n"
            "    def dfs(cur, path):\n"
            "        if len(path) > max_len:\n"
            "            return\n"
            "        if cur == end:\n"
            "            paths.append(list(path))\n"
            "            return\n"
            "        for nxt in graph.neighbors(cur):\n"
            "            if nxt not in path:\n"
            "                path.append(nxt)\n"
            "                dfs(nxt, path)\n"
            "                path.pop()\n"
            "    dfs(start, [start])\n"
            "    return sorted(paths)\n"),
        "cases": [("call", [["气压低", "沸点降", "煮不熟"],
                            ["气压低", "缺氧", "煮不熟"]])],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：多条件链组合（高压锅在高原=气压低→沸点降 + 气压高→沸点升 两条链的可解释路径）",
    },
    "图遍历-最短路径": {
        "task": "最短路径",
        "pattern": (
            "def shortest_path(graph, start, end):\n"
            "    # 无权图最短路径：BFS 逐层扩散 + 前驱还原（最少条件链跳数）\n"
            "    if start == end:\n"
            "        return [start]\n"
            "    from collections import deque\n"
            "    prev = {start: None}\n"
            "    queue = deque([start])\n"
            "    while queue:\n"
            "        cur = queue.popleft()\n"
            "        for nxt in graph.neighbors(cur):\n"
            "            if nxt not in prev:\n"
            "                prev[nxt] = cur\n"
            "                if nxt == end:\n"
            "                    path = []\n"
            "                    node = nxt\n"
            "                    while node is not None:\n"
            "                        path.append(node)\n"
            "                        node = prev[node]\n"
            "                    return path[::-1]\n"
            "                queue.append(nxt)\n"
            "    return None\n"),
        "cases": [("call", ["气压低", "沸点降", "煮不熟"]),
                  ("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：条件链最短路径——BFS 最少跳数（两链中取最短；反向无路返回 None）",
    },
    "图遍历-加权最短": {
        "task": "加权最短路径",
        "pattern": (
            "def dijkstra(graph, weights, start, end):\n"
            "    # 加权最短路径：Dijkstra 贪心（权重=条件链代价/信任度倒数，小=优）\n"
            "    import heapq\n"
            "    dist = {start: 0}\n"
            "    prev = {start: None}\n"
            "    pq = [(0, start)]\n"
            "    while pq:\n"
            "        d, cur = heapq.heappop(pq)\n"
            "        if d > dist.get(cur, float('inf')):\n"
            "            continue\n"
            "        if cur == end:\n"
            "            break\n"
            "        for nxt in graph.neighbors(cur):\n"
            "            w = weights.get((cur, nxt), 1)\n"
            "            nd = d + w\n"
            "            if nd < dist.get(nxt, float('inf')):\n"
            "                dist[nxt] = nd\n"
            "                prev[nxt] = cur\n"
            "                heapq.heappush(pq, (nd, nxt))\n"
            "    if end not in dist:\n"
            "        return None\n"
            "    path = []\n"
            "    node = end\n"
            "    while node is not None:\n"
            "        path.append(node)\n"
            "        node = prev[node]\n"
            "    return path[::-1], dist[end]\n"),
        "cases": [("call", (["气压低", "缺氧", "煮不熟"], 3))],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：条件链加权最短——Dijkstra 选代价最小链（缺氧路径代价 1+2=3 < 沸点降路径 2+2=4）",
    },
    "条件路由图-查询": {
        "task": "路由查询",
        "pattern": (
            "def route_query(graph, condition):\n"
            "    # 条件路由查询：从条件出发影响传播 → 可达规律（影响面，不含起点）\n"
            "    from collections import deque\n"
            "    visited, queue = set(), deque([condition])\n"
            "    while queue:\n"
            "        cur = queue.popleft()\n"
            "        for nxt in graph.neighbors(cur):\n"
            "            if nxt not in visited:\n"
            "                visited.add(nxt)\n"
            "                queue.append(nxt)\n"
            "    return sorted(visited)\n"),
        "cases": [("call", ["沸点降", "煮不熟", "缺氧"])],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：条件路由查询——条件 → 影响面（规律集合，compose 条件链组合的图查询形态）",
    },
    "条件路由图-对接": {
        "task": "条件单元对接",
        "pattern": (
            "def build_from_condition_units(units):\n"
            "    # compose_engine.CONDITION_UNITS → 条件路由图（知识=单元，conditions=条件入边）\n"
            "    g = Graph()\n"
            "    for name, u in units.items():\n"
            "        g.add_node(name)\n"
            "        for c in u.get('conditions', []):\n"
            "            g.add_edge(c, name)\n"
            "    return g\n"
            "def condition_impact(g, condition):\n"
            "    # 条件 → 影响的知识单元（直接+间接——影响面）\n"
            "    from collections import deque\n"
            "    visited, queue = set(), deque([condition])\n"
            "    while queue:\n"
            "        cur = queue.popleft()\n"
            "        for nxt in g.neighbors(cur):\n"
            "            if nxt not in visited:\n"
            "                visited.add(nxt)\n"
            "                queue.append(nxt)\n"
            "    return sorted(visited)\n"),
        "cases": [(({"沸点-气压": {"conditions": ["气压"]},
                     "密度-浮沉": {"conditions": ["物体", "液体"]}},), 5)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：真实条件单元库（compose_engine 43 单元）→ 条件路由图（条件 → 影响的规律单元）",
    },
    "图查询-模式匹配": {
        "task": "模式匹配",
        "pattern": (
            "def match_pattern(graph, src, rel, dst):\n"
            "    # 图查询语言：MATCH (a)-[r]->(b) 模式 → 匹配的三元组集合\n"
            "    # src/dst 支持 None=任意节点；rel 支持 None=任意边\n"
            "    results = []\n"
            "    for a in sorted(graph.nodes):\n"
            "        if src is not None and a != src:\n"
            "            continue\n"
            "        for b in graph.neighbors(a):\n"
            "            if rel is not None and rel not in (a, b):\n"
            "                continue\n"
            "            if dst is not None and b != dst:\n"
            "                continue\n"
            "            results.append((a, b))\n"
            "    return results\n"),
        "cases": [("call", [('气压低', '沸点降'), ('气压低', '缺氧')])],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图查询语言——MATCH 模式（(a)-[r]->(b)，None=任意，条件路由图三元组查询）",
    },
    "图查询-聚合": {
        "task": "聚合查询",
        "pattern": (
            "def aggregate_by(graph, key_fn):\n"
            "    # 图查询语言：按条件分组聚合（每节点 → 出度计数，GROUP BY 语义）\n"
            "    groups = {}\n"
            "    for node in sorted(graph.nodes):\n"
            "        k = key_fn(node)\n"
            "        groups.setdefault(k, 0)\n"
            "        groups[k] += 1\n"
            "    return groups\n"),
        "cases": [("call", {'气压低': 1, '沸点降': 1, '缺氧': 1, '煮不熟': 1})],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图查询语言——GROUP BY 聚合（按 key_fn 分组计数）",
    },
    "图查询-条件链": {
        "task": "条件链查询",
        "pattern": (
            "def chain_query(graph, condition, max_len=4):\n"
            "    # 图查询语言：从条件出发沿边收集完整链（MATCH (a)-[*]->(b) 路径语义）\n"
            "    chains = []\n"
            "    def walk(cur, path):\n"
            "        if len(path) > max_len:\n"
            "            return\n"
            "        succ = graph.neighbors(cur)\n"
            "        if not succ:\n"
            "            chains.append(list(path))\n"
            "            return\n"
            "        for nxt in succ:\n"
            "            if nxt not in path:\n"
            "                path.append(nxt)\n"
            "                walk(nxt, path)\n"
            "                path.pop()\n"
            "    walk(condition, [condition])\n"
            "    return sorted(chains)\n"),
        "cases": [("call", [['气压低', '沸点降', '煮不熟'],
                            ['气压低', '缺氧', '煮不熟']])],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图查询语言——变长路径 MATCH (a)-[*]->(b)：从条件出发的完整条件链集合",
    },
    "图存储-事务": {
        "task": "图事务",
        "pattern": (
            "def txn_op(state, op, payload=None):\n"
            "    # 图数据库事务：begin 快照 / commit 生效 / rollback 回滚（ACID 原子性）\n"
            "    if op == 'begin':\n"
            "        state['snapshot'] = {k: list(v) if isinstance(v, list) else v\n"
            "                              for k, v in state.get('data', {}).items()}\n"
            "        return 'active'\n"
            "    if op == 'commit':\n"
            "        state['snapshot'] = None\n"
            "        return 'committed'\n"
            "    if op == 'rollback':\n"
            "        if 'snapshot' in state and state['snapshot'] is not None:\n"
            "            state['data'] = state['snapshot']\n"
            "            state['snapshot'] = None\n"
            "        return 'rolled_back'\n"
            "    return 'idle'\n"),
        "cases": [(({'data': {'a': [1]}, 'snapshot': None}, 'begin'), 'active'),
                  (({'data': {'a': [1]}, 'snapshot': {'a': [1]}}, 'commit'),
                   'committed'),
                  (({'data': {'a': [2]}, 'snapshot': {'a': [1]}}, 'rollback'),
                   'rolled_back')],
        "params": [],
        "calibration": "对照：图数据库事务——begin 快照/commit 生效/rollback 回滚（ACID 原子性语义）",
    },
    "图索引-属性索引": {
        "task": "属性索引",
        "pattern": (
            "def index_by_attr(nodes, attr):\n"
            "    # 图数据库索引：按属性值分组 → 快速查找（索引加速语义）\n"
            "    idx = {}\n"
            "    for nid, props in nodes.items():\n"
            "        val = props.get(attr)\n"
            "        if val is not None:\n"
            "            idx.setdefault(val, []).append(nid)\n"
            "    return {k: sorted(v) for k, v in idx.items()}\n"),
        "cases": [(({'a': {'type': '条件'}, 'b': {'type': '规律'}, 'c': {'type': '条件'}},
                    'type'),
                   {'条件': ['a', 'c'], '规律': ['b']}),
                  (({'x': {'t': 1}}, 'none'), {})],
        "params": [],
        "calibration": "对照：图数据库索引——按属性值分组（type 索引：条件→[a,c] 规律→[b]）",
    },
    "图查询-子图匹配": {
        "task": "子图匹配",
        "pattern": (
            "def subgraph_match(graph, pattern):\n"
            "    # 图查询：模式子图匹配（pattern=[(src, dst), ...] 边列表 → 存在性）\n"
            "    # 所有边都在图中存在 → 匹配成功（子图同构简化版）\n"
            "    for s, d in pattern:\n"
            "        if d not in graph.neighbors(s):\n"
            "            return False\n"
            "    return True\n"),
        "cases": [("call", True),
                  ("call", False)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图查询——子图模式匹配（模式边全部存在=匹配；缺边=不匹配）",
    },
    "图算法-PageRank": {
        "task": "PageRank",
        "pattern": (
            "def pagerank(graph, iterations=5, damping=0.85):\n"
            "    # PageRank：权重迭代传播（出链均分，阻尼因子防死端）\n"
            "    nodes = sorted(graph.nodes)\n"
            "    n = len(nodes)\n"
            "    pr = {node: 1.0 / n for node in nodes}\n"
            "    for _ in range(iterations):\n"
            "        new_pr = {node: (1 - damping) / n for node in nodes}\n"
            "        for node in nodes:\n"
            "            out = graph.neighbors(node)\n"
            "            if not out:\n"
            "                continue\n"
            "            share = damping * pr[node] / len(out)\n"
            "            for nxt in out:\n"
            "                new_pr[nxt] += share\n"
            "        pr = new_pr\n"
            "    return pr\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图算法——PageRank（权重迭代传播，入链多者排名高）",
    },
    "图算法-连通分量": {
        "task": "连通分量",
        "pattern": (
            "def connected_components(graph):\n"
            "    # 无向连通分量：BFS 分组（边双向视为连通，互达节点同组）\n"
            "    from collections import deque\n"
            "    # 构建无向邻接（edges 双向化）\n"
            "    adj = {n: set(graph.neighbors(n)) for n in graph.nodes}\n"
            "    for n in list(graph.nodes):\n"
            "        for nxt in graph.neighbors(n):\n"
            "            adj.setdefault(nxt, set()).add(n)\n"
            "    seen = set()\n"
            "    comps = []\n"
            "    for start in sorted(graph.nodes):\n"
            "        if start in seen:\n"
            "            continue\n"
            "        group = set()\n"
            "        queue = deque([start])\n"
            "        seen.add(start)\n"
            "        while queue:\n"
            "            cur = queue.popleft()\n"
            "            group.add(cur)\n"
            "            for nxt in adj.get(cur, set()):\n"
            "                if nxt not in seen:\n"
            "                    seen.add(nxt)\n"
            "                    queue.append(nxt)\n"
            "        comps.append(sorted(group))\n"
            "    return sorted(comps)\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图算法——连通分量（无向互达分组）",
    },
    "图算法-拓扑排序": {
        "task": "拓扑排序",
        "pattern": (
            "def topological_sort(graph):\n"
            "    # 拓扑排序：DAG 依赖顺序（Kahn 算法——入度归零先出）\n"
            "    from collections import deque\n"
            "    indeg = {node: 0 for node in graph.nodes}\n"
            "    for node in graph.nodes:\n"
            "        for nxt in graph.neighbors(node):\n"
            "            indeg[nxt] = indeg.get(nxt, 0) + 1\n"
            "    queue = deque(sorted(n for n, d in indeg.items() if d == 0))\n"
            "    order = []\n"
            "    while queue:\n"
            "        cur = queue.popleft()\n"
            "        order.append(cur)\n"
            "        for nxt in graph.neighbors(cur):\n"
            "            indeg[nxt] -= 1\n"
            "            if indeg[nxt] == 0:\n"
            "                queue.append(nxt)\n"
            "    return order if len(order) == len(graph.nodes) else None\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图算法——拓扑排序（Kahn 入度归零，DAG 依赖顺序；有环返回 None）",
    },
    "图查询-执行计划": {
        "task": "执行计划",
        "pattern": (
            "def query_plan(conditions, stats):\n"
            "    # 查询执行计划：按选择性排序条件（低选择性先执行——查询优化语义）\n"
            "    plan = sorted(conditions, key=lambda c: stats.get(c, 0))\n"
            "    return plan\n"),
        "cases": [((['a', 'b', 'c'], {'a': 10, 'b': 2, 'c': 50}), ['b', 'a', 'c']),
                  ((['x'], {'x': 1}), ['x']),
                  ((['a', 'b'], {}), ['a', 'b'])],
        "params": [],
        "calibration": "对照：图查询优化——执行计划（按选择性升序，低选择性条件先执行）",
    },
    "图存储-批量操作": {
        "task": "批量建图",
        "pattern": (
            "def batch_edges(graph, edges):\n"
            "    # 批量建图：一次添加多条边（批量导入语义）\n"
            "    for src, dst in edges:\n"
            "        graph.add_edge(src, dst)\n"
            "    return len(edges)\n"),
        "cases": [("call", 3)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图数据库批量导入（多条边一次性建图）",
    },
    "图索引-布隆过滤": {
        "task": "布隆过滤",
        "pattern": (
            "def bloom_filter(items, probe):\n"
            "    # 布隆过滤器：多哈希位数组（成员可能判定，误报可接受）\n"
            "    size = 64\n"
            "    bits = [False] * size\n"
            "    def h1(x):\n"
            "        return sum(ord(c) for c in x) % size\n"
            "    def h2(x):\n"
            "        return (len(x) * 7 + sum(ord(c) for c in x)) % size\n"
            "    for it in items:\n"
            "        bits[h1(it)] = bits[h2(it)] = True\n"
            "    return bits[h1(probe)] and bits[h2(probe)]\n"),
        "cases": [((['a', 'b', 'c'], 'b'), True),
                  ((['a', 'b', 'c'], 'z'), False),
                  ((['ab'], 'ab'), True)],
        "params": [],
        "calibration": "对照：图索引——布隆过滤器（多哈希位数组，快速成员判定，可误报）",
    },
    "图算法-节点相似度": {
        "task": "节点相似度",
        "pattern": (
            "def jaccard_similarity(graph, a, b):\n"
            "    # 节点相似度：Jaccard（共同邻居 / 邻居并集）——推荐语义\n"
            "    na = set(graph.neighbors(a))\n"
            "    nb = set(graph.neighbors(b))\n"
            "    if not na and not nb:\n"
            "        return 0.0\n"
            "    return len(na & nb) / len(na | nb)\n"),
        "cases": [("call", 0.0)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图算法——Jaccard 相似度（共同邻居占比，推荐/相似节点语义）",
    },
    "图算法-图同构": {
        "task": "图同构判定",
        "pattern": (
            "def graph_isomorphic(edges_a, edges_b):\n"
            "    # 图同构（简化）：边数+节点度序列 相同 → 可能同构（必要条件）\n"
            "    def deg_seq(edges):\n"
            "        nodes = set()\n"
            "        for s, d in edges:\n"
            "            nodes.add(s)\n"
            "            nodes.add(d)\n"
            "        deg = {n: 0 for n in nodes}\n"
            "        for s, d in edges:\n"
            "            deg[s] += 1\n"
            "            deg[d] += 1\n"
            "        return len(nodes), sorted(deg.values())\n"
            "    return deg_seq(edges_a) == deg_seq(edges_b)\n"),
        "cases": [(([('a', 'b'), ('b', 'c')], [('x', 'y'), ('y', 'z')]), True),
                  (([('a', 'b')], [('x', 'y'), ('y', 'z')]), False)],
        "params": [],
        "calibration": "对照：图算法——同构判定（节点数+度序列必要条件，结构等价检测）",
    },
    "图算法-社区发现": {
        "task": "社区发现",
        "pattern": (
            "def label_propagation(graph, iterations=3):\n"
            "    # 社区发现：标签传播（LPA——节点取邻居多数标签收敛）\n"
            "    labels = {n: n for n in graph.nodes}\n"
            "    for _ in range(iterations):\n"
            "        for n in sorted(graph.nodes):\n"
            "            neigh = graph.neighbors(n)\n"
            "            if not neigh:\n"
            "                continue\n"
            "            from collections import Counter\n"
            "            cnt = Counter(labels[x] for x in neigh)\n"
            "            labels[n] = cnt.most_common(1)[0][0]\n"
            "    return labels\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图算法——标签传播社区发现（LPA，邻居多数标签传播收敛）",
    },
    "图灵枢-导出": {
        "task": "图导出灵枢",
        "pattern": (
            "def graph_to_memories(graph, max_chain=4):\n"
            "    # 条件路由图 → 灵枢记忆条目（每节点=条件链卡，可写入灵枢记忆库）\n"
            "    mems = []\n"
            "    for node in sorted(graph.nodes):\n"
            "        succ = graph.neighbors(node)\n"
            "        if succ:\n"
            "            chain = ' → '.join([node] + succ[:max_chain - 1])\n"
            "            mems.append({'content': '[条件链] ' + chain,\n"
            "                         'tags': ['graph', 'condition-chain', node],\n"
            "                         'importance': 0.7})\n"
            "    return mems\n"),
        "cases": [("call", 1)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图数据库 × 灵枢——条件路由图导出为灵枢记忆条目（条件链卡，可召回重建）",
    },
    "图存储-快照版本": {
        "task": "快照版本",
        "pattern": (
            "def snapshot_ops(repo, op, version=None, state=None):\n"
            "    # 图版本快照：保存/回溯（时间点恢复语义）\n"
            "    if op == 'save':\n"
            "        ver = repo.get('next', 1)\n"
            "        repo['versions'][ver] = dict(state or {})\n"
            "        repo['next'] = ver + 1\n"
            "        return ver\n"
            "    if op == 'restore':\n"
            "        return repo['versions'].get(version)\n"
            "    if op == 'list':\n"
            "        return sorted(repo['versions'].keys())\n"
            "    return None\n"),
        "cases": [(({'versions': {}, 'next': 1}, 'save', None, {'a': 1}), 1),
                  (({'versions': {1: {'a': 1}}, 'next': 2}, 'restore', 1),
                   {'a': 1}),
                  (({'versions': {1: {'a': 1}}, 'next': 2}, 'list'), [1])],
        "params": [],
        "calibration": "对照：图数据库版本管理——快照保存/回溯（时间点恢复）",
    },
    "图查询-时序查询": {
        "task": "时序查询",
        "pattern": (
            "def time_query(history, time):\n"
            "    # 时序图查询：时间点 → 该时刻图状态（快照序列检索）\n"
            "    snaps = sorted(history.keys())\n"
            "    cur = {}\n"
            "    for t in snaps:\n"
            "        if t <= time:\n"
            "            cur = history[t]\n"
            "        else:\n"
            "            break\n"
            "    return cur\n"),
        "cases": [(({1: {'a': 1}, 3: {'a': 2}}, 2), {'a': 1}),
                  (({1: {'a': 1}}, 5), {'a': 1}),
                  (({3: {'a': 2}}, 1), {})],
        "params": [],
        "calibration": "对照：时序图查询——时间点最近快照（快照序列时间回溯）",
    },
    "图算法-增量更新": {
        "task": "增量更新",
        "pattern": (
            "def incr_update(graph, edge, op):\n"
            "    # 动态图增量：边增删（增量维护，不重建全图）\n"
            "    src, dst = edge\n"
            "    if op == 'add':\n"
            "        graph.add_edge(src, dst)\n"
            "        return 'added'\n"
            "    if op == 'remove':\n"
            "        graph.remove_edge(src, dst)\n"
            "        return 'removed'\n"
            "    return None\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：动态图——增量边增删（增量维护语义）",
    },
    "图存储-分区分片": {
        "task": "分区分片",
        "pattern": (
            "def graph_shard(nodes, shards):\n"
            "    # 图分区：节点确定性哈希 → 分片（水平扩展语义）\n"
            "    parts = {i: [] for i in range(shards)}\n"
            "    for n in nodes:\n"
            "        parts[sum(ord(c) for c in n) % shards].append(n)\n"
            "    return {k: sorted(v) for k, v in parts.items()}\n"),
        "cases": [((['a', 'b', 'c', 'd'], 2), {0: ['b', 'd'], 1: ['a', 'c']}),
                  (([], 3), {0: [], 1: [], 2: []})],
        "params": [],
        "calibration": "对照：分布式图——哈希分片（节点分布到分片，水平扩展）",
    },
    "图存储-主从复制": {
        "task": "主从复制",
        "pattern": (
            "def replication(replicas, op, key=None, value=None):\n"
            "    # 主从复制：写主节点 → 同步从节点（读扩展/容错）\n"
            "    if op == 'write':\n"
            "        for r in replicas:\n"
            "            r[key] = value\n"
            "        return len(replicas)\n"
            "    if op == 'read':\n"
            "        return replicas[0].get(key)  # 读主副本\n"
            "    return None\n"),
        "cases": [(([{}, {}], 'write', 'k', 'v'), 2),
                  (([{'k': 'v'}, {'k': 'v'}], 'read', 'k'), 'v'),
                  (([{'k': 'v'}, {'k': 'x'}], 'read', 'k'), 'v')],
        "params": [],
        "calibration": "对照：分布式图——主从复制（写全副本同步，读主副本）",
    },
    "图查询-分布式查询": {
        "task": "分布式查询",
        "pattern": (
            "def dist_query(shards, query_fn):\n"
            "    # 分布式查询：各分片并行查 → 合并结果（MapReduce 语义）\n"
            "    results = []\n"
            "    for shard in shards:\n"
            "        results.extend(query_fn(shard))\n"
            "    return sorted(results)\n"),
        "cases": [(([[1, 3], [2, 4]], lambda s: [x * 2 for x in s]), [2, 4, 6, 8]),
                  (([[], []], lambda s: s), [])],
        "params": [],
        "calibration": "对照：分布式查询——分片并行处理合并（Map 归约语义）",
    },
    "图可视化-力导向布局": {
        "task": "力导向布局",
        "pattern": (
            "def force_layout(nodes, edges, iterations=2):\n"
            "    # 力导向布局：斥力+引力迭代（节点坐标稳定——图可视化）\n"
            "    pos = {n: i * 1.0 for i, n in enumerate(nodes)}  # 初始线性\n"
            "    for _ in range(iterations):\n"
            "        for a in nodes:\n"
            "            for b in nodes:\n"
            "                if a != b and pos[a] < pos[b]:\n"
            "                    pos[a] += 0.1  # 斥力推远\n"
            "                    pos[b] -= 0.1\n"
            "        for a, b in edges:\n"
            "            pos[b] = (pos[a] + pos[b]) / 2  # 引力拉近\n"
            "    return {n: round(pos[n], 2) for n in nodes}\n"),
        "cases": [((['a', 'b'], [('a', 'b')], 1), {'a': 0.1, 'b': 0.5}),
                  ((['x'], [], 1), {'x': 0.0})],
        "params": [],
        "calibration": "对照：图可视化——力导向布局（斥力推离+引力拉近迭代收敛）",
    },
    "图可视化-分层布局": {
        "task": "分层布局",
        "pattern": (
            "def layer_layout(graph):\n"
            "    # 分层布局：按 BFS 深度分层（层次坐标——层级图可视化）\n"
            "    from collections import deque\n"
            "    starts = [n for n in graph.nodes if not any(\n"
            "        n in graph.neighbors(m) for m in graph.nodes)]\n"
            "    if not starts:\n"
            "        starts = [min(graph.nodes)]\n"
            "    layers = {}\n"
            "    for s in starts:\n"
            "        q = deque([(s, 0)])\n"
            "        while q:\n"
            "            n, d = q.popleft()\n"
            "            if n not in layers or d < layers[n]:\n"
            "                layers[n] = d\n"
            "            for nxt in graph.neighbors(n):\n"
            "                if nxt not in layers or d + 1 < layers[nxt]:\n"
            "                    q.append((nxt, d + 1))\n"
            "    return layers\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图可视化——分层布局（BFS 深度分层坐标）",
    },
    "图可视化-邻接矩阵": {
        "task": "邻接矩阵",
        "pattern": (
            "def adjacency_matrix(graph):\n"
            "    # 邻接矩阵：节点 × 节点 0/1（图的结构矩阵表示）\n"
            "    nodes = sorted(graph.nodes)\n"
            "    idx = {n: i for i, n in enumerate(nodes)}\n"
            "    mat = [[0] * len(nodes) for _ in nodes]\n"
            "    for n in nodes:\n"
            "        for nxt in graph.neighbors(n):\n"
            "            mat[idx[n]][idx[nxt]] = 1\n"
            "    return mat\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图可视化——邻接矩阵（0/1 结构矩阵表示）",
    },
    "图存储-备份恢复": {
        "task": "备份恢复",
        "pattern": (
            "def backup_ops(repo, op, data=None):\n"
            "    # 图备份：全量备份/增量合并/恢复（数据安全语义）\n"
            "    if op == 'full':\n"
            "        repo['full'] = dict(data or {})\n"
            "        repo['incr'] = {}\n"
            "        return 'full_backed'\n"
            "    if op == 'incr':\n"
            "        repo['incr'].update(data or {})\n"
            "        return 'incr_backed'\n"
            "    if op == 'restore':\n"
            "        merged = dict(repo.get('full', {}))\n"
            "        merged.update(repo.get('incr', {}))\n"
            "        return merged\n"
            "    return None\n"),
        "cases": [(({'full': None, 'incr': None}, 'full', {'a': 1}), 'full_backed'),
                  (({'full': {'a': 1}, 'incr': {}}, 'incr', {'b': 2}), 'incr_backed'),
                  (({'full': {'a': 1}, 'incr': {'b': 2}}, 'restore'),
                   {'a': 1, 'b': 2})],
        "params": [],
        "calibration": "对照：图备份——全量+增量合并恢复（数据安全）",
    },
    "图存储-一致性检查": {
        "task": "一致性检查",
        "pattern": (
            "def integrity_check(graph):\n"
            "    # 一致性：边两端节点存在 + 无重复边（数据完整性）\n"
            "    errors = []\n"
            "    seen = set()\n"
            "    for src in graph.nodes:\n"
            "        for dst in graph.neighbors(src):\n"
            "            if dst not in graph.nodes:\n"
            "                errors.append(f'悬空边: {src}→{dst}')\n"
            "            if (src, dst) in seen:\n"
            "                errors.append(f'重复边: {src}→{dst}')\n"
            "            seen.add((src, dst))\n"
            "    return errors\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图完整性——一致性检查（悬空边/重复边检测）",
    },
    "图存储-压缩编码": {
        "task": "图压缩",
        "pattern": (
            "def compress_adjacency(graph):\n"
            "    # 图压缩：邻接表 CSR 表示（顶点偏移+邻接数组——紧凑存储）\n"
            "    nodes = sorted(graph.nodes)\n"
            "    offsets, adj = [], []\n"
            "    for n in nodes:\n"
            "        offsets.append(len(adj))\n"
            "        adj.extend(sorted(graph.neighbors(n)))\n"
            "    offsets.append(len(adj))\n"
            "    return {'nodes': nodes, 'offsets': offsets, 'adj': adj}\n"),
        "cases": [("call", None)],
        "params": [],
        "needs_inject": True,
        "calibration": "对照：图压缩——CSR 邻接表（顶点偏移+邻接数组，紧凑存储）",
    },
}


def route_graph_unit(question):
    """任务识别（问题 → 图数据库单元）"""
    best, best_len = None, 0
    for uid, u in GRAPH_UNITS.items():
        for kw in (u["task"], uid):
            if kw in question and len(kw) > best_len:
                best, best_len = uid, len(kw)
    return best


if __name__ == "__main__":
    print("=== 图数据库白箱单元库（目标6 · 条件图数据库初级复现）===\n")
    for uid, u in GRAPH_UNITS.items():
        print(f"[{uid}] 任务={u['task']} 样例数={len(u['cases'])}")
        print(f"    校准: {u['calibration']}")
    print(f"\n=== 判定 ===\n图数据库单元库: "
          f"{'✔ 5 单元就绪（存储/遍历/路径/持久化/条件路由映射）' if len(GRAPH_UNITS) >= 4 else '✘'}")
