# -*- coding: utf-8 -*-
"""test_role_compose_in_chat.py · 角色扮演主线接入测试
验证：chat_engine role_ctx 时——角色簇未覆盖的新问法 → 组合引擎角色生成
（场景×角色单元，零 LLM）；OOC 检测；角色域未覆盖落回通用域（防污染）。"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

# 组合引擎应覆盖的新问法（ROLE_CLUSTERS 触发词未覆盖 → role_compose 生成）
NEW_QS = [
    '你喜欢吃什么？',      # 食物（组合）
    '你住在哪？',          # 住处（组合）
    '你有鳍吗？',          # 特征（组合）
    '你是人类吗？',        # OOC 检测（组合层）
]
# 角色域未覆盖 → 落回通用域（防污染：角色不答通用知识）
UNCOVERED = [
    '什么是碳中和？',
]
ROLE_HINTS = ['海', '鲸', '磷虾', '尾巴', '喷水', '浪花', '珊瑚', '水柱', '鳞片']

print('=== 角色扮演主线接入测试（鲸鱼娘 · 零 LLM） ===')
ok = 0
for q in NEW_QS:
    r = ce.chat(dex=None, message=q, role_ctx='鲸鱼娘')
    txt = r['reply']
    role_reply = r.get('role_reply', False)
    role_compose = r.get('role_compose', False)
    hit = role_reply and any(h in txt for h in ROLE_HINTS)
    if hit:
        ok += 1
    mark = '✓' if hit else '✗'
    src = 'OOC' if r.get('role_route') == 'ooc' else '组合生成' if role_compose else '簇直答'
    print(f'[{mark}] {q}  [{src}]')
    print(f'   -> {txt[:80]}')
for q in UNCOVERED:
    r = ce.chat(dex=None, message=q, role_ctx='鲸鱼娘')
    txt = r['reply']
    # 权威判定：role_reply=False（未走角色分支）+ 无强角色特征（磷虾/尾巴等——
    # 不用「海/鲸」等泛词：碳中和知识含「海洋」会误判污染）
    strong = ['磷虾', '尾巴', '喷水', '浪花', '水柱', '鳞片', '珊瑚', '洋流']
    polluted = any(h in txt for h in strong)
    hit = (not r.get('role_reply', False)) and not polluted
    if hit:
        ok += 1
    mark = '✓' if hit else '✗'
    print(f'[{mark}] {q}（应落回通用域）')
    print(f'   -> {txt[:60]}...')
print(f'\n接入测试: {ok}/{len(NEW_QS)+len(UNCOVERED)} 通过')
