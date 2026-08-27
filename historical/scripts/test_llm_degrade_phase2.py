# -*- coding: utf-8 -*-
"""test_llm_degrade_phase2.py · 第二阶段 LLM 降级验证——双主线对照实验
核心：白箱自校验能否独立终裁？LLM 仅外部对照？
  ① 代码主线：白箱生成代码+自校验 vs LLM 判定代码正确性 → 一致率
  ② 角色主线：白箱角色化回答+自校验 vs LLM 判定角色一致性(OOC) → 一致率
一致率 ≥90% → 白箱自校验独立终裁成立，LLM 降级外部校验器（白箱终裁）。
"""
import sys, os, yaml
sys.stdout.reconfigure(encoding='utf-8')
try:
    with open(r'C:\Users\FuRongJun\.dsh\.credentials.yaml', encoding='utf-8') as f:
        _cred = yaml.safe_load(f) or {}
    os.environ['DEEPSEEK_API_KEY'] = _cred.get('DEEPSEEK_API_KEY', '')
except Exception:
    pass
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import code_compose as cc
import role_compose as rc
from aeis.roleplay_chat import LingshuChat

# v3（用户指示）：LLM 外部对照改用云端 DeepSeek v4-flash（判定稳定一致——
# Ollama 9b 判定随机性大，同输入可正确可错误；v4-flash 两次同输入完全一致）
lc = LingshuChat(data_dir=r'D:\Program Files\2_ai\knowledge-base\roleplay_data',
                 upstream_key_var='DEEPSEEK_API_KEY',
                 upstream_model='deepseek-v4-flash')


def llm_judge(system, user, rounds=1):
    """LLM 外部对照：云端 DeepSeek v4-flash（prefer_local=False）
    判定稳定（v3 验证两次同输入一致），单轮即可；保留 rounds 参数作保险"""
    votes = []
    for _ in range(rounds):
        try:
            out = lc._llm(system, user + "\n只输出：正确 或 不正确（不要解释）。",
                          prefer_local=False)
        except Exception:
            return None
        if not out or out.startswith('（'):
            continue
        out = out.strip()
        # 严格判定：仅看首词（「正确。」vs「不正确。原因…」）
        if out.startswith('不正确') or out.startswith('不符合') \
                or out.startswith('不合适') or out.startswith('错误'):
            votes.append(False)
        elif out.startswith('正确') or out.startswith('符合') \
                or out.startswith('合适'):
            votes.append(True)
    if not votes:
        return None
    return sum(1 for v in votes if v) > len(votes) / 2


# ============ ① 代码主线：白箱生成代码 vs LLM 判定 ============
print('=== ① 代码主线：白箱生成+自校验 vs LLM 判定正确性 ===')
CODE_SYS = ("你是代码审查员。判断给出的 Python 代码是否正确地完成任务（逻辑正确、"
            "边界处理合理）。只回答：正确 或 不正确，一行简短原因。")
CODE_QS = [
    "写一个函数把数组从小到大排序",
    "写一个函数去掉数组里重复的元素",
    "写一个函数数一数数组里每个元素出现几次",
    "写一个函数找出一组数里的最大值",
    "写一个函数把列表反转",
    "写一个函数把数组加起来求和",
]
code_agree = code_total = 0
for q in CODE_QS:
    r = cc.code_route(q)
    if not r.get("ok") or not r.get("code"):
        print(f'{q}: 白箱未生成（跳过）')
        continue
    code_total += 1
    judge = llm_judge(CODE_SYS,
                      f"任务：{q}\n代码：\n{r['code']}\n\n这段代码正确吗？")
    if judge is None:
        print(f'{q}: LLM 不可用')
        continue
    same = judge is True
    code_agree += 1 if same else 0
    mark = '✔' if same else '✘'
    print(f'[{mark}] {q} -> 白箱自校验✔ | LLM判{"正确" if judge else "错误"}')

# ============ ② 角色主线：白箱角色化回答 vs LLM 判定角色一致性 ============
print('\n=== ② 角色主线：白箱角色化回答 vs LLM 判定角色一致性(OOC) ===')
ROLE_SYS = ("你是角色一致性审查员。判断回答是否符合给定角色的设定（身份/说话风格），"
            "是否出现角色设定外的内容（OOC）。只回答：符合 或 不符合，一行简短原因。")
ROLE_QS = [
    ("鲸鱼娘", "你是谁？"), ("鲸鱼娘", "你住在哪里？"), ("鲸鱼娘", "你吃什么？"),
    ("猫娘", "你是谁？"), ("猫娘", "你住在哪里？"), ("猫娘", "你吃什么？"),
    ("猫娘", "你有尾巴吗？"), ("鲸鱼娘", "你是人类吗？"),
]
role_agree = role_total = 0
for role, q in ROLE_QS:
    r = rc.role_route(q, role)
    if not r.get("ok") or not r.get("answer"):
        print(f'({role}) {q}: 白箱未生成（跳过）')
        continue
    role_total += 1
    judge = llm_judge(ROLE_SYS,
                      f"角色：{role}（{'深海鲸鱼娘' if role=='鲸鱼娘' else '家养猫娘'}）"
                      f"\n问题：{q}\n回答：{r['answer']}\n\n这个回答符合角色设定吗？")
    if judge is None:
        print(f'({role}) {q}: LLM 不可用')
        continue
    same = judge is True
    role_agree += 1 if same else 0
    mark = '✔' if same else '✘'
    print(f'[{mark}] ({role}) {q} -> 白箱自校验✔ | LLM判{"符合" if judge else "不符合"}')

# ============ 判定 ============
print('\n=== 双主线对照统计 ===')
if code_total:
    print(f'代码主线: 一致率 {code_agree}/{code_total} = {code_agree/code_total*100:.0f}%'
          f'（目标≥90%）{"✔" if code_agree/code_total >= 0.9 else "✘"}')
if role_total:
    print(f'角色主线: 一致率 {role_agree}/{role_total} = {role_agree/role_total*100:.0f}%'
          f'（目标≥90%）{"✔" if role_agree/role_total >= 0.9 else "✘"}')
both_ok = (code_total and code_agree/code_total >= 0.9
           and role_total and role_agree/role_total >= 0.9)
print(f'→ 双主线白箱自校验独立终裁: {"✔ 成立（LLM 仅外部对照）" if both_ok else "✘ 未达标"}')
