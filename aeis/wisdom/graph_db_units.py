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
