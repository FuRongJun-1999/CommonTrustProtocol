# -*- coding: utf-8 -*-
"""验证 v62 3 个错题修复"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

qs = ['2月为什么只有28天？', '星期是怎么来的？', '为什么傍晚天空变红？']
for q in qs:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    bad = any(s in txt for s in ["Let me", "Actually,", "I think", "This is", "I'll",
                                 "I'm", "I would", "I can", "I need", "So I"])
    bad = bad or txt.startswith("你说的这个，可以看") or len(txt) < 15
    print(f'{"OK " if not bad else "MISS"} {q} -> [{len(txt)}ch] {txt[:55]!r}')
