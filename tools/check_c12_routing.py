# -*- coding: utf-8 -*-
"""c12 路由验证：语法编译 + 自然问法命中 + 答案长度"""
import sys, io, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')

# 1. 语法编译
import py_compile
py_compile.compile(r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py', doraise=True)
print('[1] 语法编译 OK')

# 2. reload 模块（防缓存）
import wisdom.semantic_translate as st
importlib.reload(st)

# 3. 检查 REVERSE_DAILY 新值
keys = ['手机充电','下雨打伞','晚上睡觉','开水晾凉','饿了吃饭','烧水去氯','窗户起雾',
        '夏天出汗','冬天穿衣','洗手防病','洗澡降温','吃早饭','喝水规律','蔬果营养',
        '垃圾入桶','节约用水','节水节电']
print('[2] REVERSE_DAILY 长度检查:')
for k in keys:
    v = st.REVERSE_DAILY.get(k, '')
    print(f'  {k}: {len(v)}ch')

# 4. 自然问法路由命中（走 chat_engine 主流程）
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

qs = [
    '为什么手机没电了要充电',
    '下雨天为什么要打伞',
    '为什么要晚上睡觉',
    '开水为什么要晾凉再喝',
    '饿了为什么要吃饭',
    '水为什么要烧开了喝',
    '冬天窗户为什么会起雾',
    '夏天为什么容易出汗',
    '冬天为什么要穿厚衣服',
    '为什么要洗手',
    '夏天冲凉能降温吗',
    '为什么吃早饭很重要',
    '为什么要按时喝水',
    '为什么要多吃蔬菜水果',
    '为什么要垃圾分类入桶',
    '为什么要节约用水',
    '为什么要节约用电',
]
print('[3] 自然问法路由命中:')
ok = 0
for q in qs:
    r = ce.chat(dex=None, message=q)
    txt = r['reply'] if isinstance(r, dict) else str(r)
    hit = len(txt) > 100
    if hit: ok += 1
    print(f'  {("OK " if hit else "MISS")} {q} -> [{len(txt)}ch] {txt[:50]!r}')
print(f'命中 {ok}/{len(qs)}')
