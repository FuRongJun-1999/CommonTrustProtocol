# -*- coding: utf-8 -*-
"""test_ccg.py · 代码条件路由图（CCG）对照测试

对照：现状 route（扁平关键词） vs ccg_search（注释索引+同义词边+task加权）。
验证：① 同义词检索（现状必败 → CCG 必中）② 多条件 AND ③ 组装链 ④ 可解释 ⑤ 停用词。
"""
import sys, io
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg
from code_compose import domain_route

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

G = ccg.build_graph()

# ① 同义词检索：BFS ↔ 广度优先搜索（现状 route 域未识别）
q = '写一个广度优先搜索单元'
r_route = domain_route(q)
r_ccg = ccg.search(q, G, top=1)
check('①a 现状 route 无法处理「广度优先搜索」（对照组）',
      not r_route.get('ok'), f"ok={r_route.get('ok')} domain={r_route.get('domain')}")
check('①b CCG 注释索引+同义词边命中 图遍历-BFS',
      r_ccg and r_ccg[0][0] == '图遍历-BFS',
      f"{r_ccg[0][0] if r_ccg else '无'}（命中词 {r_ccg[0][3] if r_ccg else []}）")

# ② 多条件 AND：最短 + 路径
r2 = ccg.search('写一个最短路径单元', G, top=1)
check('② 多条件：最短+路径 → 图遍历-最短路径', r2 and r2[0][0] == '图遍历-最短路径',
      r2[0][0] if r2 else '无')

# ③ 组装链：依赖边自动串联（c 端到端同源）
c = ccg.compose('写一个顶点覆盖单元（边端点选取）', G)
check('③a 组装链：顶点覆盖 → LCA → 条件分解', c['ok'] and len(c['chain']) == 3,
      ' → '.join(c['chain']))
check('③b 组装代码含三单元定义', c['ok'] and 'def vertex_cover' in c['code']
      and 'def lca' in c['code'] and 'def condition_split' in c['code'])
c2 = ccg.compose('写一个软中断单元（延迟工作）', G)
check('③c os 链：软中断 → 工作窃取 → 模块加载', c2['ok'] and len(c2['chain']) == 3,
      ' → '.join(c2['chain']))

# ④ 可解释：命中路径返回注释索引
ex = ccg.explain('图遍历-BFS', G)
check('④ 可解释路径（单元名/域/任务/注释）',
      '图遍历-BFS' in ex and 'graph' in ex and '注释' in ex, ex[:60])

# ⑤ 停用词过滤：『一个』不干扰；task 加权使权威名单元优先
q5 = '写一个顶点覆盖单元（边端点选取）'
hits5 = ccg.search(q5, G, top=3)
check('⑤ 停用词+task加权：顶点覆盖 首中', hits5 and hits5[0][0] == '图算法-顶点覆盖',
      str([h[0] for h in hits5]))

print(f'\n=== 代码条件路由图（CCG）: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
