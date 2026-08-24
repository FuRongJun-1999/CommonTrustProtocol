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
