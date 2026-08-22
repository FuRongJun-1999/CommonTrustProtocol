# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
from aeis.knowledge import _chunk_text

# 场景1: 多个代码块 + 段落混合
md = """开头。

```py
a = 1

b = 2
```

中间文字。

```js
x = 1;
y = 2;
```

结尾。"""
chunks = _chunk_text(md, max_len=2000)
print("场景1 chunks:", len(chunks))
for i, c in enumerate(chunks):
    has_code = "```" in c
    print(f"  chunk{i} len={len(c)} has_code={has_code} head={c[:24]!r}")

# 场景2: 超长代码块按行切分（保序不拆行）
code = "```py\n" + "\n".join(f"line_{i} = {i}" for i in range(400)) + "\n```"
chunks2 = _chunk_text(code, max_len=1500)
print("场景2 chunks:", len(chunks2), "(超长代码块被切成多段)")
for i, c in enumerate(chunks2[:3]):
    lines = c.splitlines()
    print(f"  chunk{i} len={len(c)} lines={len(lines)} first={lines[1][:14]!r} last={lines[-1][:14]!r}")
# 每行完整（未被截断）
lines_ok = True
for c in chunks2:
    for ln in c.splitlines():
        if ln.startswith("line_"):
            parts = ln.split(" = ")
            if len(parts) != 2 or not parts[1].isdigit():
                lines_ok = False
                print("  断行:", ln)
print("  所有行完整:", lines_ok)
