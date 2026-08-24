# -*- coding: utf-8 -*-
"""测试③：上下文裁剪 token 节约（v1.28 信噪比前后对比）
模拟多轮对话积累的记忆 → LLM 请求 system 大小对比"""
import sys, os, yaml
sys.stdout.reconfigure(encoding='utf-8')
try:
    with open(r'C:\Users\FuRongJun\.dsh\.credentials.yaml', encoding='utf-8') as f:
        _cred = yaml.safe_load(f) or {}
    os.environ['DEEPSEEK_API_KEY'] = _cred.get('DEEPSEEK_API_KEY', '')
    os.environ['LINGSHU_UPSTREAM_KEY'] = _cred.get('DEEPSEEK_API_KEY', '')
except Exception:
    pass
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
from aeis.roleplay_chat import LingshuChat, MEM_BUDGET_CHARS
from aeis.roleplay_chat import RECALL_MIN_SCORE

lc = LingshuChat(data_dir=r'D:\Program Files\2_ai\knowledge-base\roleplay_data',
                 upstream_key_var='LINGSHU_UPSTREAM_KEY')

# 模拟：多轮对话后 session_ctx 积累 + 长期记忆召回
SID = 'token-test'
# 先注入 6 轮对话（含无关历史 + 相关历史）
rounds = [
    ('今天天气真不错', '是啊，适合出门走走'),
    ('帮我算一下 15*3', '等于 45'),
    ('晚饭吃什么好', '建议清淡一些'),
    ('怎么学英语？', '从背单词开始，每天 20 个'),
    ('最近工作很累', '注意休息，劳逸结合'),
    ('周末去爬山怎么样', '好主意，记得带水和防晒'),
]
for i, (u, a) in enumerate(rounds):
    r = lc.respond(u, session_id=SID)
    # 强制积累会话上下文（模拟：白箱/LLM 都写入 ctx）
    lc._session_ctx.setdefault(f'_gen_:{SID}', []).extend([u, a])

# 当前问题（与「学英语」相关，与天气/晚饭/爬山无关）
q = '英语听力怎么提高？'
mem_notes = lc._recall_mem(SID, q, limit=4, role_id='')
ctx = lc._session_ctx.get(f'_gen_:{SID}', [])
mem_notes_before = list(mem_notes) + [f'[本会话] {m}' for m in ctx[-3:]]

# 信噪比过滤前：原样注入（旧行为：无过滤无预算）
before_chars = sum(len(m) for m in mem_notes_before)
before_tokens = int(before_chars / 1.5) + 100  # +system 协议开销

# 信噪比过滤后（v1.28）
mem_notes_after = lc._filter_mem_noise(q, mem_notes_before)
mem_notes_after = lc._trim_mem_budget(mem_notes_after)
after_chars = sum(len(m) for m in mem_notes_after)
after_tokens = int(after_chars / 1.5) + 100

print('=== 测试③：上下文裁剪 token 节约 ===')
print(f'注入前记忆: {len(mem_notes_before)} 条 / {before_chars} 字符 (≈{before_tokens} tokens)')
print(f'注入后记忆: {len(mem_notes_after)} 条 / {after_chars} 字符 (≈{after_tokens} tokens)')
print(f'  过滤丢弃: {len(mem_notes_before) - len(mem_notes_after)} 条低相关记忆')
save = (before_tokens - after_tokens) / before_tokens * 100
print(f'  token 节约: {save:.1f}%')
print(f'  预算上限: {MEM_BUDGET_CHARS} 字符, 召回分数门槛: {RECALL_MIN_SCORE}')

# 完整 LLM 请求节约（含 system 其他部分：角色/指令固定 ~300 tokens）
FIXED = 300
full_before = before_tokens + FIXED
full_after = after_tokens + FIXED
print(f'\n完整 LLM 请求: {full_before} -> {full_after} tokens (节约 {(full_before-full_after)/full_before*100:.1f}%)')

lc.close()
