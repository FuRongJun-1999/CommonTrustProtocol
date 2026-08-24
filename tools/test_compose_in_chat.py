# -*- coding: utf-8 -*-
"""test_compose_in_chat.py · 白箱自举接入测试——组合引擎兜底 chat_engine miss 分支
验证：知识检索 miss（dex=None）时，条件化单元组合生成 → 自校验通过 → 直答；
      组合引擎无覆盖的问题 → 仍诚实边界（不编）。"""
import sys, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
import wisdom.chat_engine as ce
importlib.reload(ce)

# 组合引擎应覆盖（知识检索 miss → 组合生成直答，或知识库已覆盖 → 白箱知识直答）
COMPOSE_QS = [
    '为什么金属勺放进热汤会烫手？',   # 未覆盖 → 组合兜底（导热快）
    '为什么木头能浮在水面上？',        # 知识库已覆盖 → 知识直答
    '为什么鞋底要有花纹？',            # 知识库已覆盖 → 知识直答
    '为什么高原上煮饭不容易熟？',      # 知识库已覆盖 → 知识直答
]
# 组合引擎无覆盖 → 诚实边界（不编）
UNCOVERED_QS = [
    '为什么恐龙灭绝了？',
    '为什么猫会踩奶？',
]

print('=== 白箱自举接入测试：组合引擎兜底 chat_engine miss 分支 ===')
ok = 0
for q in COMPOSE_QS:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    honest = r.get('honest', False)
    # 通过标准：非诚实拒绝（直答）——组合兜底直答 或 知识路径直答均可
    hit = (not honest) and len(txt) > 20
    if hit:
        ok += 1
    mark = '✓' if hit else '✗'
    src = '组合兜底' if '（这是按' in txt else ('知识路径' if not honest else '诚实边界')
    print(f'[{mark}] {q}  [{src}]')
    print(f'   -> [{len(txt)}ch] {txt[:100]}')
for q in UNCOVERED_QS:
    r = ce.chat(dex=None, message=q)
    txt = r['reply']
    honest = r.get('honest', False)
    hit = honest and ('没有把握' in txt or '不编' in txt)
    if hit:
        ok += 1
    mark = '✓' if hit else '✗'
    print(f'[{mark}] {q}（应诚实边界）')
    print(f'   -> [{len(txt)}ch] {txt[:100]}')
print(f'\n接入测试: {ok}/{len(COMPOSE_QS)+len(UNCOVERED_QS)} 通过')
