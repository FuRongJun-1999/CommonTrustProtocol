# -*- coding: utf-8 -*-
"""test_verifier_pipeline.py · 本地校验器管线级验证（阶段 4/5 证据）

验证：
  ① 零 LLM 静态检查：verifier.py 无任何网络/LLM 客户端依赖
  ② 冷→暖缓存：681 单元首轮全量校验（miss）→ 次轮 681 全命中（零计算）
  ③ 域管线接入：_verify_with_verifier 六层校验 → checks 兼容格式
  ④ 边界扩展回归：字符串/数学新边界族不引入误判（681 全过）
"""
import sys, os, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 零 LLM 静态检查
src = open(os.path.join(os.path.dirname(__file__), 'verifier.py'), encoding='utf-8').read()
FORBIDDEN = ['import openai', 'import requests', 'from openai', 'from requests',
             'import anthropic', 'import urllib', 'http.client', 'import httpx',
             'import aiohttp', 'deepseek', 'api_key', 'API_KEY']
bad = [w for w in FORBIDDEN if w in src]
check('① 零 LLM：verifier.py 无网络/LLM 客户端依赖', not bad, f'违禁词: {bad}')

# ② 冷→暖缓存：681 单元两次全量
from verifier import Verifier, VerifyRequest
from compiler_code_units import COMPILER_UNITS
from python_code_units import PYTHON_UNITS
from graph_db_units import GRAPH_UNITS
from os_units import OS_UNITS
from browser_units import BROWSER_UNITS
from net_units import NET_UNITS

DOMAINS = [('compiler', COMPILER_UNITS), ('pylang', PYTHON_UNITS),
           ('graph', GRAPH_UNITS), ('os', OS_UNITS),
           ('browser', BROWSER_UNITS), ('net', NET_UNITS)]
UNITS = [(d, uid, u) for d, units in DOMAINS for uid, u in units.items()]
TOTAL = len(UNITS)

tmp = os.path.join(tempfile.mkdtemp(), 'cache.json')
v = Verifier(cache=__import__('verifier').VerifyCache(path=tmp))

ok_all = 0
for d, uid, u in UNITS:
    req = VerifyRequest(task=u['task'], code=u['pattern'], unit_id=uid,
                        cases=list(u.get('cases', [])),
                        expected_structure={'inject': True} if u.get('needs_inject') else {})
    if v.verify(req).ok:
        ok_all += 1
s1 = v.cache.stats()
check('②a 冷缓存：681 单元首轮全部通过', ok_all == TOTAL, f'{ok_all}/{TOTAL}')
check('②b 冷缓存：首轮全未命中（misses=681）', s1['misses'] == TOTAL and s1['hits'] == 0,
      f"hits={s1['hits']} misses={s1['misses']}")

v2 = Verifier(cache=__import__('verifier').VerifyCache(path=tmp))
for d, uid, u in UNITS:
    req = VerifyRequest(task=u['task'], code=u['pattern'], unit_id=uid,
                        cases=list(u.get('cases', [])),
                        expected_structure={'inject': True} if u.get('needs_inject') else {})
    v2.verify(req)
s2 = v2.cache.stats()
# 次轮（暖缓存）：v2 为新实例从 0 计数——681 次请求全部命中、零未命中
check('②c 暖缓存：次轮 681 全命中（零计算）', s2['hits'] == TOTAL and s2['misses'] == 0,
      f"hits={s2['hits']} misses={s2['misses']}")

# ③ 域管线接入：_verify_with_verifier 兼容格式
from code_compose import _verify_with_verifier
from graph_db_units import GRAPH_UNITS as GU
ok3 = True
for uid in ['图算法-顶点覆盖', '图算法-最近公共祖先', '条件路由图-条件分解',
            '条件路由图-映射']:
    u = GU[uid]
    o, checks = _verify_with_verifier(u['pattern'], u)
    ok3 &= o and isinstance(checks, list) and all(isinstance(c, str) for c in checks)
check('③ 域管线接入：_verify_with_verifier 返回 (ok, checks列表) 兼容', ok3,
      f'{pass_n} 示例单元')

# ④ 边界扩展回归：新字符串/数学边界族不误判（681 全过，temp 缓存）
v3 = Verifier(cache=__import__('verifier').VerifyCache(path=tmp))
ok4 = 0
for d, uid, u in UNITS:
    req = VerifyRequest(task=u['task'], code=u['pattern'], unit_id=uid,
                        cases=list(u.get('cases', [])),
                        expected_structure={'inject': True} if u.get('needs_inject') else {})
    if v3.verify(req).ok:
        ok4 += 1
check('④ 边界扩展回归：681 单元仍全过（字符串/数学边界族无误判）',
      ok4 == TOTAL, f'{ok4}/{TOTAL}')

print(f'\n=== 本地校验器管线级验证: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
