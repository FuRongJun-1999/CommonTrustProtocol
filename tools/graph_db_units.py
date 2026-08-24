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
