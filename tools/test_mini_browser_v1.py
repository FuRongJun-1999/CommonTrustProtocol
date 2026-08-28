# -*- coding: utf-8 -*-
"""test_mini_browser_v1.py · 浏览器条件卡 V1/V2 验证用例（2026-08-28）

对照 docs/T11_完整版条件卡_浏览器.md：
- V1 URL 解析边界：无 scheme 报错 / 默认端口补全 / 非法端口报错 / 显式端口
- V2 GET 对齐：本地 http.server 测试页，状态码/体对齐已知内容
- V2 边界：连接拒绝/不支持 scheme 显式报错
"""
import sys, os, threading, socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mini_browser import parse_url, http_get, BrowserError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


# ============ V1 URL 解析边界 ============
try:
    parse_url("example.com/x")
    check("V1 无 scheme 报错", False, "未抛异常")
except BrowserError:
    check("V1 无 scheme 报错", True)

u = parse_url("http://example.com/x")
check("V1 默认端口补全", u["port"] == 80 and u["path"] == "/x" and u["host"] == "example.com",
      f"got {u}")

u = parse_url("https://example.com/")
check("V1 https 默认端口 443", u["port"] == 443, f"got {u}")

u = parse_url("http://example.com:8080/a/b?c=1")
check("V1 显式端口与路径", u["port"] == 8080 and u["path"] == "/a/b?c=1", f"got {u}")

try:
    parse_url("http://example.com:abc/")
    check("V1 非法端口报错", False, "未抛异常")
except BrowserError:
    check("V1 非法端口报错", True)

try:
    parse_url("ftp://example.com/")
    check("V1 不支持 scheme 报错", False, "未抛异常")
except BrowserError:
    check("V1 不支持 scheme 报错", True)

try:
    parse_url("http://:8080/")
    check("V1 空 host 报错", False, "未抛异常")
except BrowserError:
    check("V1 空 host 报错", True)

# ============ V2 GET 对齐（本地测试服务器） ============
PAGE = "<html><head><title>白箱测试页</title></head><body><p>hello lingshu</p></body></html>"
HITS = {"count": 0}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        HITS["count"] += 1
        body = PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

try:
    r = http_get(f"http://127.0.0.1:{port}/test.html")
    check("V2 状态码对齐", r["status"] == 200, f"got {r['status']}")
    check("V2 体对齐", "hello lingshu" in r["body"], f"got {r['body'][:80]!r}")
    check("V2 头解析", r["headers"].get("content-type", "").startswith("text/html"),
          f"got {r['headers']}")
    n1 = HITS["count"]
    r2 = http_get(f"http://127.0.0.1:{port}/test.html")
    check("V2 二次请求真实到达", HITS["count"] == n1 + 1, f"count={HITS['count']}")
except BrowserError as e:
    check("V2 GET 对齐", False, str(e))
finally:
    srv.shutdown()

# 连接拒绝显式报错（用未监听端口）
s = socket.socket()
s.bind(("127.0.0.1", 0))
free_port = s.getsockname()[1]
s.close()
try:
    http_get(f"http://127.0.0.1:{free_port}/", timeout=2)
    check("V2 连接拒绝报错", False, "未抛异常")
except BrowserError as e:
    check("V2 连接拒绝报错", "连接失败" in str(e), str(e))

# ============ 判定 ============
print("\n=== 判定 ===")
print(f"V1/V2 验证用例: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
