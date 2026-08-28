# -*- coding: utf-8 -*-
"""check_showcase_links.py · 架构展示互链完整性检查（可复用质检）

检查 docs/灵枢架构展示_* 系列的互链有效性：
- markdown 中的 (xxx.html)/(xxx.md) 相对链接 → 目标文件存在
- HTML 中的 href="xxx.html" → 目标文件存在
"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
DOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "docs")

SHOWCASE_FILES = [f for f in os.listdir(DOCS)
                  if f.startswith("灵枢架构展示_")]
bad = 0
checked = 0

for f in sorted(SHOWCASE_FILES):
    p = os.path.join(DOCS, f)
    text = io.open(p, encoding="utf-8").read()
    # markdown 链接 [..](target) 与 HTML href="target"
    links = re.findall(r"\]\(([^)]+\.html|[^)]+\.md)\)", text) + \
        re.findall(r'href="([^"]+\.html)"', text)
    for link in links:
        if link.startswith(("http", "#")):
            continue
        checked += 1
        target = os.path.join(DOCS, link)
        if not os.path.exists(target):
            bad += 1
            print(f"[✘ 断链] {f} → {link}")

print(f"\n互链检查: {checked} 条链接，断链 {bad}")
if bad == 0:
    print("✓ 架构展示互链完整")
sys.exit(0 if bad == 0 else 1)
