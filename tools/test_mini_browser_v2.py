# -*- coding: utf-8 -*-
"""test_mini_browser_v2.py · 浏览器条件卡 V3/V6 验证用例（2026-08-28）

对照 docs/T11_完整版条件卡_浏览器.md：
- V3 内容提取：已知 <title> 与 3 个链接 → 提取结果逐一相等；正文去标签
- V4 渲染：结构化输出含标题行/链接表/正文
- V6 相对链接：根相对/相对/上级/锚点/绝对逐一解析
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mini_browser import extract, render, resolve_url

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


HTML = """<html><head><title>白箱测试页</title></head>
<body>
<h1>标题一</h1>
<script>var x = "<fake>tag</fake>";</script>
<p>第一段 &amp; 实体。</p>
<a href="/docs/a.html">文档甲</a>
<a href='b.html'>乙页</a>
<a href="https://example.org/abs">绝对链接</a>
<a name="anchor">无 href 不收</a>
<style>p { color: red }</style>
</body></html>"""

# ============ V3 内容提取 ============
page = extract(HTML)
check("V3 title 提取", page["title"] == "白箱测试页", f"got {page['title']!r}")
check("V3 链接数（无 href 不收）", len(page["links"]) == 3, f"got {page['links']}")
check("V3 链接 href 逐一", [h for h, _ in page["links"]] == ["/docs/a.html", "b.html", "https://example.org/abs"],
      f"got {[h for h, _ in page['links']]}")
check("V3 链接文本逐一", [t for _, t in page["links"]] == ["文档甲", "乙页", "绝对链接"],
      f"got {[t for _, t in page['links']]}")
check("V3 正文去标签+实体+script 剔除",
      "第一段 & 实体。" in page["text"] and "fake" not in page["text"] and "color" not in page["text"],
      f"got {page['text'][:120]!r}")
check("V3 无 title 显式 None", extract("<html><body>x</body></html>")["title"] is None)

# ============ V4 结构化渲染 ============
out = render(page)
check("V4 标题行", out.startswith("# 白箱测试页"), f"got {out[:30]!r}")
check("V4 链接表编号", "[1] 文档甲 -> /docs/a.html" in out and "[3] 绝对链接 -> https://example.org/abs" in out,
      out[:200])
check("V4 正文在列", "第一段 & 实体。" in out)

# ============ V6 相对 URL 解析 ============
base = "http://example.com:8080/docs/guide/index.html"
cases = [
    ("/top.html", "http://example.com:8080/top.html"),            # 根相对
    ("b.html", "http://example.com:8080/docs/guide/b.html"),      # 同级相对
    ("../up.html", "http://example.com:8080/docs/up.html"),       # 上级
    ("../../root.html", "http://example.com:8080/root.html"),     # 上两级
    ("http://other.io/x", "http://other.io/x"),                    # 绝对
]
for href, want in cases:
    got = resolve_url(base, href)
    check(f"V6 {href}", got == want, f"got {got}")
check("V6 锚点", resolve_url("http://e.com/a/b.html", "#sec") == "http://e.com/a/b.html#sec",
      resolve_url("http://e.com/a/b.html", "#sec"))

# ============ 判定 ============
print("\n=== 判定 ===")
print(f"V3/V4/V6 验证用例: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
