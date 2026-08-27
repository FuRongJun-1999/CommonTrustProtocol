# -*- coding: utf-8 -*-
"""功能格类型库最终验证"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

qs = ['怎么让物体匹配目标？', '什么是换形格？', '状态匹配是什么？', '什么是功能格？',
      '旋转格是做什么的？', '换色格有什么用？']
for q in qs:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    ok = len(txt) > 100 and not txt.startswith('你说的这个')
    mark = 'OK ' if ok else 'MISS'
    print(f'{mark} {q} -> [{len(txt)}ch] {txt[:45]!r}')
