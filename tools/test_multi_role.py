# -*- coding: utf-8 -*-
"""test_multi_role.py · 多角色扩展测试
验证：①新增角色（猫娘）场景组合生成（零 LLM，含角色特征）
②鲸鱼娘回归正常 ③防污染：角色特征词隔离（鲸鱼娘不答猫娘内容，反之亦然）"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import role_compose as rc

WHALE_HINTS = ['磷虾', '喷水', '浪花', '水柱', '鳞片', '珊瑚']
CAT_HINTS = ['小鱼干', '喵', '猫粮', '咕噜', '窗台', '爪子', '毛线球']

print('=== ① 猫娘场景组合生成（零 LLM） ===')
CAT_QS = [
    '你是谁？', '你住在哪里？', '你吃什么？', '你有尾巴吗？',
    '今天天气不错', '你喜欢什么？', '你是人类吗？',
]
cat_ok = 0
for q in CAT_QS:
    r = rc.role_route(q, '猫娘')
    if not r.get("ok"):
        print(f'[✗] {q} -> {r.get("reason")}')
        continue
    txt = r['answer']
    has_cat = any(h in txt for h in CAT_HINTS)
    no_whale = not any(h in txt for h in WHALE_HINTS)
    ok = has_cat and no_whale
    if ok:
        cat_ok += 1
    mark = '✓' if ok else '✗'
    print(f'[{mark}] ({r.get("route")}) {q}')
    print(f'   -> {txt[:70]}')

print('\n=== ② 鲸鱼娘回归 ===')
r = rc.role_route('你是谁？', '鲸鱼娘')
whale_ok = r.get("ok") and any(h in r["answer"] for h in WHALE_HINTS) \
    and not any(h in r["answer"] for h in CAT_HINTS)
print(f'[{"✓" if whale_ok else "✗"}] 鲸鱼娘你是谁 -> {r["answer"][:50]}')

print('\n=== ③ 防污染（角色特征隔离） ===')
# 鲸鱼娘角色问猫娘特征词 → 应回答鲸鱼娘内容（不泄漏猫娘）
r1 = rc.role_route('你有小鱼干吗？', '鲸鱼娘')
no_cat_leak = r1.get("ok") and not any(h in (r1.get("answer") or '') for h in CAT_HINTS)
print(f'[{"✓" if no_cat_leak else "✗"}] 鲸鱼娘被问小鱼干 -> 不含猫娘特征')
# 猫娘角色问鲸鱼娘特征词 → 应回答猫娘内容（不泄漏鲸鱼娘）
r2 = rc.role_route('你会喷水吗？', '猫娘')
no_whale_leak = r2.get("ok") and not any(h in (r2.get("answer") or '') for h in WHALE_HINTS)
print(f'[{"✓" if no_whale_leak else "✗"}] 猫娘被问喷水 -> 不含鲸鱼娘特征')

print(f'\n=== 判定 ===')
print(f'猫娘白箱命中: {cat_ok}/{len(CAT_QS)}（目标≥80%）| 鲸鱼娘回归: {"✓" if whale_ok else "✗"} | 防污染: {"✓✓" if no_cat_leak and no_whale_leak else "✘"}')
