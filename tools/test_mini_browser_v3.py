# -*- coding: utf-8 -*-
"""test_mini_browser_v3.py · 浏览器条件卡 V4/V5 验证用例（2026-08-28）

对照 docs/T11_完整版条件卡_浏览器.md：
- V4 导航链：A → 链接 → B → back → A（历史栈正确）；无历史后退报错
- V5 缓存：同 URL 二次访问命中缓存（请求计数不增）；refresh 后重新请求
- F5 链接编号越界显式报错
"""
import sys, os, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mini_browser import Browser, BrowserError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


PAGE_A = ('<html><head><title>页面A</title></head><body>'
          '<a href="/b.html">去B</a><a href="/c.html">去C</a></body></html>')
PAGE_B = '<html><head><title>页面B</title></head><body><a href="/a.html">回A</a></body></html>'
PAGES = {"/a.html": PAGE_A, "/b.html": PAGE_B, "/c.html": PAGE_B}
HITS = {"count": 0}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        HITS["count"] += 1
        body = PAGES.get(self.path, "<html><title>404</title></html>").encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}"

try:
    # ============ V4 导航链 ============
    b = Browser()
    pa = b.visit(f"{base}/a.html")
    check("V4 访问 A", pa["title"] == "页面A", f"got {pa['title']!r}")
    pb = b.follow(1)  # A → B
    check("V4 follow 到 B", pb["title"] == "页面B", f"got {pb['title']!r}")
    check("V4 follow 走相对解析", pb["url"] == f"{base}/b.html", f"got {pb['url']}")
    pa2 = b.back()
    check("V4 back 回 A", pa2["title"] == "页面A" and b.current["title"] == "页面A",
          f"got {pa2['title']!r}")

    # 无历史后退报错（单页访问后历史栈为空，两次 back 中第二次报错）
    b2 = Browser()
    b2.visit(f"{base}/a.html")
    try:
        b2.back()
        check("V4 无历史后退报错", False, "单页后 back 未抛异常")
    except BrowserError:
        check("V4 无历史后退报错", True)

    # 链接编号越界
    try:
        b2.follow(99)
        check("F5 链接编号越界报错", False, "未抛异常")
    except BrowserError:
        check("F5 链接编号越界报错", True)

    # ============ V5 缓存 ============
    b3 = Browser()
    b3.visit(f"{base}/a.html")
    n1 = HITS["count"]
    b3.visit(f"{base}/a.html")  # 命中缓存
    check("V5 缓存命中不重复请求", HITS["count"] == n1, f"count {n1}->{HITS['count']}")
    b3.refresh()                # 显式刷新 → 重新请求
    check("V5 刷新重新请求", HITS["count"] == n1 + 1, f"count {HITS['count']}")
    b3.follow(1)                # A → B（B 未缓存，真实请求）
    n2 = HITS["count"]
    check("V5 不同 URL 不误命中", HITS["count"] == n2 and b3.current["title"] == "页面B",
          f"count={HITS['count']}")
finally:
    srv.shutdown()

# ============ 判定 ============
print("\n=== 判定 ===")
print(f"V4/V5 验证用例: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
