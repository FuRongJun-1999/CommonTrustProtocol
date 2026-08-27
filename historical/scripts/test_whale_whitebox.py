# -*- coding: utf-8 -*-
"""test_whale_whitebox.py · 防污染回归（v1.29 角色条件路由 + v3 组合兜底防护）
v1.29 起：无 role_ctx 不角色化（角色簇只认角色条件，防全局污染）。
v3 起：组合引擎兜底只对知识疑问句触发——「你会喷水吗？」不得硬凑沸腾答案。
正确角色化行为由 test_role_routing ①（role_ctx=鲸鱼娘 → 6/6）承载。"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

# 无 role_ctx：不得出现鲸鱼娘特征（防污染）
NON_ROLE_QS = [
    '你是谁？',              # → 灵枢自我介绍（非鲸鱼娘）
    '你住在哪里？',          # → 诚实边界
    '你吃什么？',            # → 诚实边界
    '你会喷水吗？',          # → 诚实边界（组合兜底防护：能力疑问句不硬凑）
]
ROLE_HINTS = ['海', '鲸', '磷虾', '尾巴', '喷水', '浪花', '珊瑚', '洋流', '水柱']

print('=== 防污染回归（无 role_ctx 不角色化 + 组合兜底防护） ===')
ok = 0
for q in NON_ROLE_QS:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    polluted = any(h in txt for h in ROLE_HINTS)
    hit = not polluted
    if hit:
        ok += 1
    mark = '✓' if hit else '✗'
    print(f'[{mark}] {q} -> [{"污染!" if polluted else len(txt)}ch] {txt[:70]!r}')
# 组合兜底防护专项：「你会喷水吗？」不得答沸腾
r = ce.chat(dex=None, message='你会喷水吗？')
no_boil = '沸腾' not in r['reply']
ok += 1 if no_boil else 0
print(f'[{"✓" if no_boil else "✗"}] 组合兜底防护: 你会喷水吗？不含"沸腾"')
print(f'\n防污染回归: {ok}/{len(NON_ROLE_QS)+1} 通过')
