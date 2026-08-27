# -*- coding: utf-8 -*-
"""v1.29 角色条件路由测试：
①角色场景（role_ctx=鲸鱼娘）角色化（身份/住处/食物/闲聊）
②非角色场景不污染（你是谁→灵枢、你住在哪里→通用）
③角色知识域未覆盖问法落回通用域"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

print('=== ① 角色场景（role_ctx=鲸鱼娘）===')
role_qs = ['你是谁？', '你住在哪里？', '你吃什么？', '你有尾巴吗？', '你好呀', '今天天气不错']
ok = 0
for q in role_qs:
    r = ce.chat(dex=None, message=q, role_ctx='鲸鱼娘')
    txt = r['reply']
    whale = any(h in txt for h in ['鲸鱼', '深海', '磷虾', '尾巴', '浪花', '珊瑚', '喷水'])
    role_ok = r.get('role_reply') or whale
    if role_ok:
        ok += 1
    print(f'  {"✓" if role_ok else "✗"} {q} -> {txt[:55]!r}')
print(f'  角色化: {ok}/{len(role_qs)}')

print('\n=== ② 非角色场景（无 role_ctx，防污染）===')
gen_qs = ['你是谁？', '你住在哪里？']
for q in gen_qs:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    polluted = any(h in txt for h in ['鲸鱼', '深海', '磷虾'])
    print(f'  {"污染✗" if polluted else "正常✓"} {q} -> {txt[:55]!r}')

print('\n=== ③ 角色域未覆盖问法落回通用域 ===')
r = ce.chat(dex=None, message='什么是碳中和？', role_ctx='鲸鱼娘')
txt = r['reply']
print(f'  {"✓" if "碳中和" in txt else "✗"} 角色场景问知识 -> [{len(txt)}ch] {txt[:40]!r}')
