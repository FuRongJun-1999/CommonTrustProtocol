# -*- coding: utf-8 -*-
"""v1.28 信噪比验证：记忆注入过滤（低相关本会话记忆丢弃 + 上下文预算裁剪）"""
import sys, os, importlib
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
from aeis.roleplay_chat import LingshuChat, SESS_MIN_OVERLAP, MEM_BUDGET_CHARS

lc = LingshuChat(data_dir=r'D:\Program Files\2_ai\knowledge-base\roleplay_data',
                 upstream_key_var='LINGSHU_UPSTREAM_KEY')

# 1. 词重叠过滤：不相关的本会话记忆被丢弃
print('[1] 词重叠过滤（零重叠的本会话记忆丢弃）:')
noisy = ['[本会话] 用户：今天天气不错｜灵枢：是的']
filtered = lc._filter_mem_noise('如何提高编程效率？', noisy)
print(f'  无关记忆 {len(noisy)} -> 过滤后 {len(filtered)}（应 0）')
assert len(filtered) == 0, '零重叠本会话记忆应被过滤'

# 2. 相关记忆保留
related = ['[本会话] 用户：怎么学编程？｜灵枢：先学基础语法']
kept = lc._filter_mem_noise('编程怎么入门？', related)
print(f'  相关记忆 {len(related)} -> 保留 {len(kept)}（应 1）')
assert len(kept) == 1, '相关记忆应保留'

# 3. 剧情记忆强制保留（零重叠也不丢）
plot = ['[剧情 会话] 鲸鱼娘在深海中前行，寻找海眼']
kept2 = lc._filter_mem_noise('今天吃什么？', plot)
print(f'  剧情记忆（无关问题）-> 保留 {len(kept2)}（应 1，剧情承接硬要求）')
assert len(kept2) == 1, '剧情记忆必须保留'

# 4. 上下文预算：超预算按 剧情>对话 裁剪
print(f'[2] 上下文预算（{MEM_BUDGET_CHARS} 字符）:')
many_ctx = ['[本会话] 对话记录' + '内容' * 200] * 5   # 5×~400字符 = 2000+
trimmed = lc._trim_mem_budget(many_ctx)
total = sum(len(m) for m in trimmed)
print(f'  注入前 {sum(len(m) for m in many_ctx)} 字符 -> 裁剪后 {len(trimmed)} 条 / {total} 字符（≤预算）')
assert total <= MEM_BUDGET_CHARS + 100, '裁剪后应在预算附近'

# 5. 剧情优先：剧情+对话超预算时剧情全保留
plots = ['[剧情] 剧情甲' + '长' * 250] * 2    # 2×~255
ctxs = ['[本会话] 对话' + '长' * 250] * 3      # 3×~255
both = plots + ctxs
t2 = lc._trim_mem_budget(both)
t_plots = [m for m in t2 if m.startswith('[剧情')]
print(f'  剧情 {len(plots)} 条 -> 保留 {len(t_plots)}（应全保留）')
assert len(t_plots) == len(plots), '剧情应全保留'

lc.close()
print('\n=== v1.28 信噪比验证全部通过 ===')
