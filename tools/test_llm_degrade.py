# -*- coding: utf-8 -*-
"""test_llm_degrade.py · ⑤ LLM 降级验证实验——白箱生成+自校验 vs LLM 外部对照
核心问题：白箱自校验能否替代 LLM 校验？（LLM 降级为外部校验器的依据）
方法：组合引擎生成 17 题答案 → 白箱自校验判定 → LLM(Ollama) 外部对照判定
      统计 LLM 对照一致率——≥90% 则白箱自校验可独立终裁，LLM 降级成立。
"""
import sys, os, yaml
sys.stdout.reconfigure(encoding='utf-8')
# 注入上游 key（云端 DeepSeek 兜底；实验优先本地 Ollama）
try:
    with open(r'C:\Users\FuRongJun\.dsh\.credentials.yaml', encoding='utf-8') as f:
        _cred = yaml.safe_load(f) or {}
    os.environ['DEEPSEEK_API_KEY'] = _cred.get('DEEPSEEK_API_KEY', '')
except Exception:
    pass
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import compose_engine as ce
from aeis.roleplay_chat import LingshuChat

lc = LingshuChat(data_dir=r'D:\Program Files\2_ai\knowledge-base\roleplay_data',
                 upstream_key_var='DEEPSEEK_API_KEY')

# 组合引擎可答的知识问题（4 域 17 题）
QS = [
    '为什么高原上煮饭不容易熟？', '为什么高压锅煮得快？',
    '为什么珠峰上烧水不到100°C就开？', '为什么夏天晾衣服干得快？',
    '为什么有风的时候衣服干得更快？', '冰箱为什么会结霜？',
    '为什么冬天湖面会结冰？', '为什么冬天眼镜会起雾？',
    '樟脑丸为什么放久了变小？', '为什么铁块会沉入水底？',
    '为什么木头能浮在水面上？', '为什么轮船那么大还能浮着？',
    '为什么金属勺放进热汤会烫手？', '为什么木筷不烫手？',
    '为什么刹车能很快停下来？', '为什么滑冰能滑得很快？',
    '为什么鞋底要有花纹？',
]

JUDGE_SYS = ("你是知识校验器。判断给出的答案是否正确（物理学/生活常识）。"
             "只回答：正确 或 不正确，然后一行简短原因。")


def llm_judge(q, answer, rounds=2):
    """LLM 外部对照：判断白箱答案是否正确。多次判定取多数（Ollama 9b
    判定有随机性——v5 实验发现同一答案两次判定可能不同）。"""
    votes = []
    for _ in range(rounds):
        user = f"问题：{q}\n答案：{answer}\n\n这个答案正确吗？"
        try:
            out = lc._llm(JUDGE_SYS, user, prefer_local=True)
        except Exception:
            return None
        if not out or out.startswith('（'):
            continue
        out = out.strip()
        if '不正确' in out or '错误' in out or '不对' in out:
            votes.append(False)
        elif '正确' in out:
            votes.append(True)
    if not votes:
        return None
    return sum(1 for v in votes if v) > len(votes) / 2  # 多数判定


print('=== ⑤ LLM 降级验证：白箱自校验 vs LLM 外部对照 ===\n')
print(f'{"问题":<26}{"自校验":<8}{"LLM对照":<8}{"一致?"}')
agree = 0
total = 0
wb_ok = 0
llm_unavail = 0
for q in QS:
    r = ce.route_compose(q)
    if not r.get("ok") or not r.get("answer"):
        print(f'{q:<26}{"✘未过":<8}{"-":<8}{"跳过(自校验拒)"}')
        continue
    wb_ok += 1
    judge = llm_judge(q, r["answer"])
    if judge is None:
        llm_unavail += 1
        print(f'{q:<26}{"✔":<8}{"不可用":<8}{"-"}')
        continue
    total += 1
    same = judge is True
    agree += 1 if same else 0
    mark = '✔' if same else '✘'
    print(f'{q:<26}{"✔":<8}{"✔正确" if judge else "✘错误":<8}{mark}')

print(f'\n=== 对照统计 ===')
print(f'白箱自校验通过: {wb_ok}/{len(QS)} = {wb_ok/len(QS)*100:.0f}%')
if total:
    print(f'LLM 外部对照有效样本: {total}（Ollama 不可用 {llm_unavail}）')
    print(f'LLM 对照一致率: {agree}/{total} = {agree/total*100:.0f}%')
    print(f'→ 一致率 {"≥90%: LLM 可降级为外部校验器，白箱自校验独立终裁 ✔" if agree/total >= 0.9 else "<90%: 白箱自校验仍须 LLM 主校验"}')
else:
    print('LLM 对照无有效样本（Ollama 不可用？）——检查本地 Ollama 服务')
