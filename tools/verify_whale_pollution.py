# -*- coding: utf-8 -*-
"""验证：鲸鱼娘簇触发词全局生效的污染——非角色场景「你是谁」是否答鲸鱼娘"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

# 非角色场景（普通灵枢）：「你是谁」「你住在哪里」「你好呀」
for q in ['你是谁？', '你住在哪里？', '你好呀']:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    whale = any(h in txt for h in ['鲸鱼', '深海', '磷虾', '尾巴'])
    print(f'{"污染✗" if whale else "正常✓"} {q} -> {txt[:60]!r}')
