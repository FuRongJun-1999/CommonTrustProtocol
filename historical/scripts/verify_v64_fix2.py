# -*- coding: utf-8 -*-
"""v64 修复完整验证：chat 引擎实际回答（不只 encode 命中）"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

qs = ['生活里有哪些负反馈？', '检测阳性就一定有病吗？']
for q in qs:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    bad = any(s in txt for s in ["Let me", "I think", "This is", "I'm", "I would", "I can", "I need"])
    bad = bad or txt.startswith("你说的这个，可以看") or len(txt) < 15
    print(f'{"OK " if not bad else "MISS"} {q} -> [{len(txt)}ch] {txt[:55]!r}')
