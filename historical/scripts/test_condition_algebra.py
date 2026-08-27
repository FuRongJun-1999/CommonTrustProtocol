# -*- coding: utf-8 -*-
"""test_condition_algebra.py · 条件代数工程化测试
验证：①影响雅可比构建 ②条件独立性（混合偏导=0 图判定）③链式传播 ④组合生成"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import compose_engine as ce
from condition_algebra import (build_influence_jacobian,
                               condition_independence,
                               chain_rule_propagate)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

J, knowledges, conditions = build_influence_jacobian(ce.CONDITION_UNITS)

# ① 雅可比构建
check('①a 雅可比矩阵构建（知识×条件）', J.shape[0] == len(ce.CONDITION_UNITS)
      and J.shape[1] == len(conditions), f'{J.shape}')
check('①b 沸点-气压 依赖气压（∂沸点/∂气压≠0）',
      J[knowledges.index('沸点-气压'), conditions.index('气压')] == 1.0)
check('①c 沸点-气压 不依赖光照（∂沸点/∂光照=0）',
      J[knowledges.index('沸点-气压'), conditions.index('光照')] == 0.0)

# ② 条件独立性（混合偏导=0 图判定）
indep, _ = condition_independence(J, conditions, '气压', '光照')
check('②a 气压 vs 光照 独立（可并行组合）', indep)
indep2, _ = condition_independence(J, conditions, '温度', '通风')
check('②b 温度 vs 通风 相关（共享蒸发-条件）', not indep2)
indep3, _ = condition_independence(J, conditions, '光照', '候鸟')
check('②c 光照 vs 候鸟 独立', indep3)

# ③ 链式法则传播
steps = chain_rule_propagate(J, conditions, '气压')
check('③ 链式传播（气压→沸点-气压）', len(steps) >= 1
      and '沸点-气压' in [knowledges[k] for k in steps[0][1]])

# ④ 组合生成（条件链 = 链式法则语义）
r = ce.route_compose('为什么高原上煮饭不容易熟？')
check('④a 组合生成（高原煮饭）', r.get('ok') and '沸点' in r.get('answer', ''),
      r.get('answer', '?')[:40])
r2 = ce.route_compose('为什么植物要放在有阳光的地方？')
check('④b 组合生成（植物光合）', r2.get('ok') and '光合' in r2.get('answer', ''))

# ⑤ 条件独立性 → 并行化判定（不同域可并行）
parallel = [('气压', '光照'), ('温度', '候鸟'), ('通风', '季节')]
all_indep = all(condition_independence(J, conditions, a, b)[0] for a, b in parallel)
check('⑤ 跨域条件独立（组合可并行化）', all_indep)

print(f'\n=== 条件代数测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
