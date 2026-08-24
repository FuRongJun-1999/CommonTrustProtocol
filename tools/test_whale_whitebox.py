# -*- coding: utf-8 -*-
"""白箱单独角色扮演测试：鲸鱼娘（零 LLM——不走 roleplay_chat 的 LLM 路径）
直接调白箱 chat_engine：角色簇命中 = 角色化回答"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

QS = [
    '你是谁？',                  # → 鲸鱼娘自我介绍
    '你住在哪里？',              # → 深海
    '你吃什么？',                # → 磷虾
    '你有尾巴吗？',              # → 鲸鱼特征
    '你会喷水吗？',              # → 喷水
    '今天天气不错',              # → 闲聊（白箱 chitchat 或角色兜底）
    '你好呀',                    # → 问候
]

print('=== 白箱角色扮演（鲸鱼娘 · 零 LLM） ===')
ok = 0
for q in QS:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    # 角色化判定：回答含鲸鱼娘特征词（海/鲸/磷虾/尾巴/喷水/浪花 等）
    role_hints = ['海', '鲸', '磷虾', '尾巴', '喷水', '浪花', '珊瑚', '洋流', '水柱']
    is_role = any(h in txt for h in role_hints)
    route = r.get('route', 'whitebox')
    if is_role:
        ok += 1
    mark = '✓' if is_role else '✗'
    print(f'[{mark}] {q} -> [{len(txt)}ch] {txt[:70]!r}')
print(f'\n角色化命中: {ok}/{len(QS)}（白箱零 LLM）')
