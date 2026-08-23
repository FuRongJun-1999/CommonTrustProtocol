# -*- coding: utf-8 -*-
"""验证 c14：DOMAIN_ROUTE 完整性 + RD 长度 + 路由命中"""
import sys, re, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.semantic_translate as st
importlib.reload(st)

# 1. DOMAIN_ROUTE 短值还在（DOMAIN_ROUTE 是 key->domain 短字符串）
src = open(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', encoding='utf-8').read()
print('[1] DOMAIN_ROUTE 短值检查:')
for k in ['频率', '波', '振动', '弹性', '能级', '能带', '混凝土']:
    m = re.search('"' + k + r'":\s*"([^"]{2,12})"', src)
    print(f'  {k}: {m.group(1) if m else "未找到"}')

# 2. RD 长度
print('[2] RD 长度:')
for k in ['频率', '波', '振动', '声音不能传播', '弹性', '梁的弯曲', '混凝土', '能级', '能带', '唐诗', '宋词', '绝句']:
    print(f'  {k}: {len(st.REVERSE_DAILY.get(k, ""))}ch')

# 3. 路由命中
import wisdom.chat_engine as ce
importlib.reload(ce)
qs = [
    ('频率', '什么是频率？'),
    ('波', '什么是波？'),
    ('振动', '什么是振动？'),
    ('声音不能传播', '为什么太空听不到声音？'),
    ('弹性', '什么是弹性？'),
    ('梁的弯曲', '什么是梁的弯曲？'),
    ('混凝土', '什么是混凝土？'),
    ('能级', '什么是能级？'),
    ('能带', '什么是能带？'),
    ('唐诗', '什么是唐诗？'),
    ('宋词', '什么是宋词？'),
    ('绝句', '什么是绝句？'),
]
ok = 0
for theme, q in qs:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    hit = len(txt) > 100 and not txt.startswith("你说的这个，可以看")
    if hit: ok += 1
    print(f'  {"OK " if hit else "MISS"} [{theme}] {q} -> [{len(txt)}ch] {txt[:40]!r}')
print(f'命中 {ok}/{len(qs)}')
