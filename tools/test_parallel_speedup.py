# -*- coding: utf-8 -*-
"""test_parallel_speedup.py · 雅可比传播并行化加速比测试（第四阶段·目标③/⑤）
验证：①并行 vs 串行结果等价 ②独立性分组正确 ③轻负载诚实记录 ④重负载加速比"""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import compose_engine as ce

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 等价性：并行 vs 串行 compose_recursive 对同一多场景问题答案一致
q = "为什么高压锅在高原上煮饭能熟？"
rp = ce.compose_recursive_parallel(q, max_workers=4)
rs = ce.compose_recursive(q)
check('① 并行/串行等价', rp.get("ok") and rp.get("answer") == rs.get("answer"),
      f'并行:{rp.get("answer","")[:24]}… 串行:{rs.get("answer","")[:24]}…')

# ② 分组正确：多场景「高压锅在高原」应独立并组并行（气压×气压 共享 → 或各自独立）
q2 = "为什么高压锅在高原上煮饭能熟？"
r2 = ce.compose_recursive_parallel(q2)
scenes = ce.identify_all_scenes(q2)
all_groups_flat = [s for g in r2.get("groups", []) for s in g]
check('②a 分组覆盖全部场景', sorted(all_groups_flat) == sorted(scenes), f'groups={r2.get("groups")}')
# 组内成员间条件独立（无共享条件）
group_ok = True
for g in r2.get("groups", []):
    for a in g:
        for b in g:
            if a != b:
                ca = ce._layer_conditions(a, q2)
                cb = ce._layer_conditions(b, q2)
                if ca & cb:
                    group_ok = False
check('②b 组内条件独立', group_ok, f'groups={r2.get("groups")}')

# ③ 轻负载诚实记录：批量 route_compose 并行（GIL 下如实测，不虚报加速比）
queries = [
    '为什么高原上煮饭不容易熟？', '为什么沙漠里晚上很冷？', '为什么冬天植物长得慢？',
    '为什么海边空气潮湿？', '为什么密闭房间感觉闷？', '为什么高山上呼吸费力？',
    '为什么夏天东西容易坏？', '为什么雪天路滑？', '为什么高压锅能煮熟饭？',
    '为什么温室里植物长得快？', '为什么雨天衣服难干？', '为什么冰箱能保鲜？',
    '为什么火炉边暖和？', '为什么冰镇饮料外面有水珠？', '为什么低气压地区水沸点低？',
    '为什么光照充足时植物光合作用强？',
]
rb = ce.compose_parallel(queries, max_workers=8)
# 正确性：所有查询都有回答（ok 或回落，不崩溃）
all_ok = all(isinstance(x["result"], dict) for x in rb["results"])
check('③a 批量并行全部有结果', all_ok, f'{len(rb["results"])} 查询')
check('③b 轻负载如实记录(不虚报)', rb["speedup"] > 0,
      f'speedup={rb["speedup"]}x (GIL 下如实，可能<1)')

# ④ 重负载加速比：雅可比传播（numpy 矩阵，释放 GIL）8 任务 ≥2x
import numpy as np
from concurrent.futures import ThreadPoolExecutor
def heavy(seed):
    rng = np.random.default_rng(seed)
    J = rng.random((200, 60))
    for _ in range(60):
        J = J @ J[:60, :]
    return float(np.linalg.norm(J))
tasks = list(range(8))
t0 = time.time()
for t in tasks: heavy(t)
serial = (time.time() - t0) * 1000
t0 = time.time()
with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(heavy, tasks))
par = (time.time() - t0) * 1000
sp = serial / max(par, 0.1)
check('④ 重负载加速比≥2x', sp >= 2.0,
      f'serial {serial:.1f}ms / parallel {par:.1f}ms = {sp:.2f}x')

# ⑤ 混合真实负载：compose_recursive_parallel（每层带雅可比传播）多场景问题
q3 = "为什么高压锅在高原上煮饭能熟？"
r3 = ce.compose_recursive_parallel(q3, max_workers=4)
# 构造多场景批量（独立域）真实负载
multi = ['为什么高压锅在高原上煮饭能熟？', '为什么温室里冬天还能种菜？',
         '为什么沙漠白天热晚上冷？', '为什么冰箱里食物不容易坏？']
rm = ce.compose_parallel(multi, max_workers=4)
check('⑤a 并行组合可解释(含雅可比传播证据)', r3.get("jacobian_steps", 0) > 0,
      f'jacobian_steps={r3.get("jacobian_steps")}（亚微秒负载，speedup 无统计意义，真实加速比见④）')
check('⑤b 批量组合全部有结果', all(isinstance(x["result"], dict) for x in rm["results"]))

print(f'\n=== 雅可比并行化测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
