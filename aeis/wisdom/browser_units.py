# -*- coding: utf-8 -*-
"""browser_units.py · 迷你浏览器白箱单元库（第六阶段·目标5 初级复现）
用户设想：终极目标「中文浏览器」← 初级复现「浏览器」。
核心管线：HTTP 响应解析 → HTML DOM 解析 → CSS 选择器 → 块布局渲染。
单元：{任务 → 代码模式模板 + 验证样例 + 校准基准}——白箱自举（外部只校准）。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

BROWSER_UNITS = {
    "HTTP-响应解析": {
        "task": "HTTP解析",
        "pattern": (
            "def parse_http_response(raw):\n"
            "    # HTTP 响应解析：状态行/头/体 → {status, headers, body}\n"
            "    lines = raw.split('\\r\\n')\n"
            "    status = int(lines[0].split()[1])\n"
            "    headers = {}\n"
            "    i = 1\n"
            "    while i < len(lines) and lines[i]:\n"
            "        k, _, v = lines[i].partition(':')\n"
            "        headers[k.strip().lower()] = v.strip()\n"
            "        i += 1\n"
            "    body = '\\n'.join(lines[i + 1:])\n"
            "    return {'status': status, 'headers': headers, 'body': body}\n"),
        "cases": [("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<body>hi</body>",
                   {"status": 200, "headers": {"content-type": "text/html"},
                    "body": "<body>hi</body>"}),
                  ("HTTP/1.1 404 Not Found\r\n\r\n", {"status": 404, "headers": {}, "body": ""})],
        "params": [],
        "calibration": "对照：浏览器 HTTP——响应状态行/头字段/体解析",
    },
    "HTML-DOM解析": {
        "task": "DOM解析",
        "pattern": (
            "def parse_dom(html):\n"
            "    # HTML → DOM 树（简化：标签 → 直接子标签列表）\n"
            "    import re\n"
            "    dom = {}\n"
            "    stack = []\n"
            "    for m in re.finditer(r'<(\\w+)[^>]*>|</(\\w+)>', html):\n"
            "        if m.group(1):\n"
            "            tag = m.group(1)\n"
            "            dom.setdefault(tag, [])\n"
            "            if stack:\n"
            "                dom[stack[-1]].append(tag)\n"
            "            stack.append(tag)\n"
            "        elif m.group(2) and stack:\n"
            "            stack.pop()\n"
            "    return dom\n"),
        "cases": [("<body><div><p>x</p></div></body>",
                   {"body": ["div"], "div": ["p"], "p": []}),
                  ("<html><body></body></html>", {"html": ["body"], "body": []})],
        "params": [],
        "calibration": "对照：浏览器 HTML 解析——标签嵌套 → DOM 树（父子关系）",
    },
    "CSS-选择器": {
        "task": "CSS选择器",
        "pattern": (
            "def css_match(selector, tag, classes):\n"
            "    # CSS 选择器匹配：tag / .class / tag.class\n"
            "    if selector.startswith('.'):\n"
            "        return selector[1:] in classes\n"
            "    parts = selector.split('.')\n"
            "    if len(parts) == 1:\n"
            "        return parts[0] == tag\n"
            "    return parts[0] == tag and parts[1] in classes\n"),
        "cases": [(("p", "p", []), True),
                  ((".red", "div", ["red"]), True),
                  (("p.red", "p", ["red"]), True),
                  (("div", "p", []), False)],
        "params": [],
        "calibration": "对照：浏览器 CSS——标签/类/tag.class 选择器匹配",
    },
    "渲染-块布局": {
        "task": "块布局",
        "pattern": (
            "def block_layout(elements, width):\n"
            "    # 块布局：元素宽度序列 → 行堆叠（超出容器宽度换行）\n"
            "    rows, cur, used = [], [], 0\n"
            "    for w in elements:\n"
            "        if used + w > width and cur:\n"
            "            rows.append(cur)\n"
            "            cur, used = [], 0\n"
            "        cur.append(w)\n"
            "        used += w\n"
            "    if cur:\n"
            "        rows.append(cur)\n"
            "    return rows\n"),
        "cases": [(([3, 2, 2], 5), [[3, 2], [2]]),
                  (([2, 2, 2], 5), [[2, 2], [2]]),
                  (([1, 1], 5), [[1, 1]])],
        "params": [],
        "calibration": "对照：浏览器渲染——块级布局（宽度约束换行堆叠）",
    },
    "HTTP-请求构建": {
        "task": "请求构建",
        "pattern": (
            "def build_get_request(url, host, headers=None):\n"
            "    # 构建 HTTP GET 请求：请求行 + Host 头 + 自定义头\n"
            "    h = headers or {}\n"
            "    lines = ['GET ' + url + ' HTTP/1.1', 'Host: ' + host]\n"
            "    for k, v in h.items():\n"
            "        lines.append(k + ': ' + v)\n"
            "    return '\\r\\n'.join(lines) + '\\r\\n\\r\\n'\n"),
        "cases": [(("/index.html", "example.com"),
                   "GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n"),
                  (("/", "a.com"),
                   "GET / HTTP/1.1\r\nHost: a.com\r\n\r\n")],
        "params": [],
        "calibration": "对照：浏览器 HTTP 客户端——GET 请求构建（请求行+头）",
    },
    "URL-解析": {
        "task": "URL解析",
        "pattern": (
            "def parse_url(url):\n"
            "    # URL 解析：协议/主机/端口/路径\n"
            "    import re\n"
            "    m = re.match(r'(\\w+)://([^/:]+)(?::(\\d+))?(/.*)?', url)\n"
            "    return {'scheme': m.group(1), 'host': m.group(2),\n"
            "            'port': int(m.group(3)) if m.group(3) else None,\n"
            "            'path': m.group(4) or '/'}\n"),
        "cases": [("https://example.com:8080/page?a=1",
                   {'scheme': 'https', 'host': 'example.com', 'port': 8080,
                    'path': '/page?a=1'}),
                  ("http://a.com/x", {'scheme': 'http', 'host': 'a.com',
                                      'port': None, 'path': '/x'})],
        "params": [],
        "calibration": "对照：浏览器 URL——协议/主机/端口/路径解析",
    },
    "CSS-级联": {
        "task": "CSS级联",
        "pattern": (
            "def cascade_apply(rules):\n"
            "    # 级联应用：选择最高优先级规则\n"
            "    return max(rules, key=cascade_weight)\n"
            "def cascade_weight(rule):\n"
            "    # CSS 级联优先级：内联1000 > id100 > class10 > 标签1\n"
            "    w = 0\n"
            "    if rule.get('inline'):\n"
            "        w += 1000\n"
            "    w += 100 * len(rule.get('ids', []))\n"
            "    w += 10 * len(rule.get('classes', []))\n"
            "    w += 1 * len(rule.get('tags', []))\n"
            "    return w\n"),
        "cases": [(([{'ids': ['a'], 'classes': [], 'tags': [], 'val': 'id'},
                     {'ids': [], 'classes': ['b'], 'tags': [], 'val': 'class'}],),
                   {'ids': ['a'], 'classes': [], 'tags': [], 'val': 'id'}),
                  (([{'ids': [], 'classes': [], 'tags': ['p'], 'val': 'tag'},
                     {'inline': True, 'val': 'inline'}],),
                   {'inline': True, 'val': 'inline'})],
        "params": [],
        "calibration": "对照：浏览器 CSS——级联优先级（内联>id>class>标签）",
    },
    "渲染-盒模型": {
        "task": "盒模型",
        "pattern": (
            "def box_model(width, padding, border, margin):\n"
            "    # 盒模型：内容+padding+border → 元素总宽（margin 不计入）\n"
            "    return width + 2 * padding + 2 * border\n"),
        "cases": [((100, 10, 2, 5), 124),
                  ((50, 0, 1, 0), 52),
                  ((0, 0, 0, 0), 0)],
        "params": [],
        "calibration": "对照：浏览器渲染——盒模型（padding/border 计入元素尺寸，margin 不计）",
    },
    "渲染-样式计算": {
        "task": "样式计算",
        "pattern": (
            "def style_compute(node, rules):\n"
            "    # 样式计算：DOM 节点（tag/classes）→ 匹配规则级联 → 最终样式\n"
            "    best, best_w = {}, -1\n"
            "    for rule in rules:\n"
            "        if rule.get('tag') and rule['tag'] != node.get('tag'):\n"
            "            continue\n"
            "        if rule.get('class') and rule['class'] not in node.get('classes', []):\n"
            "            continue\n"
            "        w = (1000 if rule.get('inline') else 0)\n"
            "        w += 100 if rule.get('id') else 0\n"
            "        w += 10 if rule.get('class') else 0\n"
            "        w += 1 if rule.get('tag') else 0\n"
            "        if w > best_w:\n"
            "            best, best_w = rule.get('style', {}), w\n"
            "    return best\n"),
        "cases": [(({'tag': 'p', 'classes': ['red']},
                    [{'tag': 'p', 'style': {'color': 'black'}},
                     {'class': 'red', 'style': {'color': 'red'}}]),
                   {'color': 'red'}),
                  (({'tag': 'p', 'classes': []},
                    [{'tag': 'p', 'style': {'color': 'black'}}]),
                   {'color': 'black'}),
                  (({'tag': 'div', 'classes': []},
                    [{'tag': 'p', 'style': {'color': 'black'}}]), {})],
        "params": [],
        "calibration": "对照：浏览器渲染管线——样式计算（DOM×CSS→匹配规则→级联取最高优先级样式）",
    },
    "渲染-布局树": {
        "task": "布局树",
        "pattern": (
            "def layout_tree(nodes, container_w):\n"
            "    # 布局树：块级节点（样式宽/高）→ (x, y, w, h) 坐标（纵向堆叠）\n"
            "    y = 0\n"
            "    out = []\n"
            "    for node in nodes:\n"
            "        w = node.get('style', {}).get('width', container_w)\n"
            "        h = node.get('style', {}).get('height', 1)\n"
            "        out.append((node.get('id'), 0, y, w, h))\n"
            "        y += h\n"
            "    return out\n"),
        "cases": [(([{'id': 'a', 'style': {'width': 5, 'height': 2}},
                     {'id': 'b', 'style': {'height': 3}}], 10),
                   [('a', 0, 0, 5, 2), ('b', 0, 2, 10, 3)]),
                  (([{'id': 'x', 'style': {}}], 7), [('x', 0, 0, 7, 1)])],
        "params": [],
        "calibration": "对照：浏览器渲染管线——布局树（块级纵向堆叠，默认宽=容器/高=1）",
    },
    "渲染-绘制": {
        "task": "绘制",
        "pattern": (
            "def paint(layout, rows, cols):\n"
            "    # 绘制：布局树 → 字符画布（'#'=元素区域，'.'=空白）\n"
            "    canvas = [['.' for _ in range(cols)] for _ in range(rows)]\n"
            "    for _, x, y, w, h in layout:\n"
            "        for dy in range(h):\n"
            "            for dx in range(w):\n"
            "                if 0 <= y + dy < rows and 0 <= x + dx < cols:\n"
            "                    canvas[y + dy][x + dx] = '#'\n"
            "    return [''.join(row) for row in canvas]\n"),
        "cases": [(([('a', 0, 0, 2, 1), ('b', 0, 1, 3, 1)], 2, 4),
                   ['##..', '###.']),
                  (([], 2, 3), ['...', '...'])],
        "params": [],
        "calibration": "对照：浏览器渲染管线——绘制（布局坐标→字符画布，像素填充）",
    },
    "事件-事件冒泡": {
        "task": "事件冒泡",
        "pattern": (
            "def event_path(dom_tree, target, ancestors=None):\n"
            "    # 事件传播路径：目标 → 祖先链（冒泡顺序：目标→父→…→根）\n"
            "    path = []\n"
            "    node = target\n"
            "    while node is not None:\n"
            "        path.append(node)\n"
            "        node = dom_tree.get(node)  # 父节点\n"
            "    return path\n"),
        "cases": [(({'button': 'form', 'form': 'body', 'body': None}, 'button'),
                   ['button', 'form', 'body']),
                  (({'a': 'div', 'div': None}, 'a'), ['a', 'div']),
                  (({'x': None}, 'x'), ['x'])],
        "params": [],
        "calibration": "对照：浏览器事件——冒泡传播路径（目标→祖先链，DOM 事件冒泡语义）",
    },
    "事件-事件监听": {
        "task": "事件监听",
        "pattern": (
            "def listener_ops(listeners, event, target):\n"
            "    # 事件监听器：add/trigger（事件→匹配监听器列表）\n"
            "    if event == 'add':\n"
            "        listeners.setdefault(target, []).append(1)\n"
            "        return len(listeners[target])\n"
            "    if event == 'trigger':\n"
            "        return len(listeners.get(target, []))  # 匹配的监听器数\n"
            "    return 0\n"),
        "cases": [(({}, 'add', 'btn'), 1),
                  (({'btn': [1]}, 'trigger', 'btn'), 1),
                  (({}, 'trigger', 'btn'), 0)],
        "params": [],
        "calibration": "对照：浏览器事件——监听器注册/触发（addEventListener/dispatchEvent 语义）",
    },
    "渲染-动画帧": {
        "task": "动画帧",
        "pattern": (
            "def animation_frame(state, step_fn, frames):\n"
            "    # 动画帧循环：逐帧应用 step_fn（requestAnimationFrame 语义）\n"
            "    out = []\n"
            "    for _ in range(frames):\n"
            "        state = step_fn(state)\n"
            "        out.append(state)\n"
            "    return out\n"),
        "cases": [((0, lambda x: x + 1, 3), [1, 2, 3]),
                  ((10, lambda x: x * 2, 2), [20, 40]),
                  ((5, lambda x: x, 1), [5])],
        "params": [],
        "calibration": "对照：浏览器渲染——动画帧循环（rAF 逐帧更新状态）",
    },
    "存储-本地存储": {
        "task": "本地存储",
        "pattern": (
            "def storage_op(store, op, key=None, value=None):\n"
            "    # localStorage：setItem/getItem/removeItem/clear（持久键值存储）\n"
            "    if op == 'set':\n"
            "        store[key] = value\n"
            "        return True\n"
            "    if op == 'get':\n"
            "        return store.get(key)\n"
            "    if op == 'remove':\n"
            "        return store.pop(key, None)\n"
            "    if op == 'clear':\n"
            "        store.clear()\n"
            "        return len(store)\n"
            "    return None\n"),
        "cases": [(({}, 'set', 'k', 'v'), True),
                  (({'k': 'v'}, 'get', 'k'), 'v'),
                  (({'k': 'v'}, 'remove', 'k'), 'v'),
                  (({'k': 'v'}, 'clear'), 0)],
        "params": [],
        "calibration": "对照：浏览器存储——localStorage（setItem/getItem/removeItem/clear）",
    },
    "存储-会话存储": {
        "task": "会话存储",
        "pattern": (
            "def session_storage(store, tab_open):\n"
            "    # sessionStorage：标签页级生命周期（新标签页 → 数据清空）\n"
            "    if tab_open:\n"
            "        return dict(store)          # 当前标签页数据\n"
            "    return {}                       # 新标签页：会话数据隔离\n"),
        "cases": [(({'u': 'x'}, True), {'u': 'x'}),
                  (({'u': 'x'}, False), {})],
        "params": [],
        "calibration": "对照：浏览器存储——sessionStorage（标签页生命周期，新标签页数据隔离）",
    },
    "并行-Web Worker": {
        "task": "Web Worker",
        "pattern": (
            "def worker_msg(main, worker, data):\n"
            "    # Web Worker：主线程 postMessage → Worker 处理 → 回传（并行任务语义）\n"
            "    worker['input'] = data\n"
            "    worker['output'] = worker.get('fn', lambda x: x)(data)\n"
            "    main['result'] = worker['output']\n"
            "    return worker['output']\n"),
        "cases": [(({'result': None}, {'fn': lambda x: x * 2}, 21), 42),
                  (({'result': None}, {'fn': lambda x: x + 1}, 1), 2)],
        "params": [],
        "calibration": "对照：浏览器并行——Web Worker（postMessage 传递数据，Worker 处理回传）",
    },
}


def route_browser_unit(question):
    """任务识别（问题 → 浏览器单元）"""
    best, best_len = None, 0
    for uid, u in BROWSER_UNITS.items():
        for kw in (u["task"], uid):
            if kw in question and len(kw) > best_len:
                best, best_len = uid, len(kw)
    return best


if __name__ == "__main__":
    print("=== 迷你浏览器白箱单元库（目标5 · 中文浏览器初级复现）===\n")
    for uid, u in BROWSER_UNITS.items():
        print(f"[{uid}] 任务={u['task']} 样例数={len(u['cases'])}")
        print(f"    校准: {u['calibration']}")
    print(f"\n=== 判定 ===\n迷你浏览器单元库: "
          f"{'✔ 4 单元就绪（HTTP/DOM/CSS/渲染）' if len(BROWSER_UNITS) >= 4 else '✘'}")
