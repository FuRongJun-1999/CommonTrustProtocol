# -*- coding: utf-8 -*-
"""c15 路由验证：12 簇自然问法命中"""
import sys, importlib, py_compile
sys.stdout.reconfigure(encoding='utf-8')
py_compile.compile(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', doraise=True)
print('[1] 语法 OK')

sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

qs = [
    ('负反馈', '什么是负反馈？'),
    ('香农熵', '什么是香农熵？'),
    ('傅里叶变换', '什么是傅里叶变换？'),
    ('中心极限定理', '什么是中心极限定理？'),
    ('贝叶斯推断', '什么是贝叶斯推断？'),
    ('梯度下降法', '什么是梯度下降？'),
    ('正则化', '什么是正则化？'),
    ('强化学习', '什么是强化学习？'),
    ('黑洞', '什么是黑洞？'),
    ('免疫系统', '什么是免疫系统？'),
    ('内稳态', '什么是内稳态？'),
    ('行列式', '什么是行列式？'),
]
ok = 0
for theme, q in qs:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    hit = len(txt) > 100 and not txt.startswith("你说的这个，可以看")
    if hit: ok += 1
    print(f'{"OK " if hit else "MISS"} [{theme}] {q} -> [{len(txt)}ch] {txt[:40]!r}')
print(f'命中 {ok}/{len(qs)}')
