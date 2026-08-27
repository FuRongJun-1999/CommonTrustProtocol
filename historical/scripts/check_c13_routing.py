# -*- coding: utf-8 -*-
"""c13 路由验证：语法 + 12 簇自然问法命中"""
import sys, importlib, py_compile
sys.stdout.reconfigure(encoding='utf-8')
py_compile.compile(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', doraise=True)
print('[1] 语法 OK')

sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
importlib.reload(st)
import wisdom.chat_engine as ce
importlib.reload(ce)

qs = [
    ('一年月数', '一年有多少个月？'),
    ('一年月数', '为什么一年有12个月？'),
    ('一周天数', '一周有几天？'),
    ('一天小时', '一天有多少个小时？'),
    ('天空蓝色', '为什么天空是蓝色的？'),
    ('月亮发光', '月亮为什么会发光？'),
    ('船浮水上', '为什么船能浮在水上？'),
    ('应力', '什么是应力？'),
    ('短路', '什么是短路？'),
    ('混凝土钢筋', '为什么混凝土要加钢筋？'),
    ('细胞', '什么是细胞？'),
    ('原子', '什么是原子？'),
    ('介质', '为什么声音需要介质？'),
]
ok = 0
for theme, q in qs:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    hit = len(txt) > 100 and not txt.startswith("你说的这个，可以看")
    if hit: ok += 1
    print(f'{"OK " if hit else "MISS"} [{theme}] {q} -> [{len(txt)}ch] {txt[:48]!r}')
print(f'命中 {ok}/{len(qs)}')
