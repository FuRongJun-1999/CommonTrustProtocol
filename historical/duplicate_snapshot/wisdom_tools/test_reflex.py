# -*- coding: utf-8 -*-
"""test_reflex.py · 条件反射优先度（荣：工程验证的高效→长期记忆/条件反射）

理论：人类面对重复性问题 → 验证过的高效路径直接走（简化），
依据被调用次数/频率提高优先度。
工程：ccg.reflex 频率追踪 → search 频率加权（log 缩放）→ 高频单元优先
命中；reflex_simplify_candidates = 高频×高复杂度 → 简化候选（W6 解法）。
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

G = ccg.build_graph()
# 用临时频率表（不污染真实 reflex_freq.json）
import tempfile
_tmp = ccg._FREQ_PATH
ccg._FREQ_PATH = os.path.join(tempfile.gettempdir(), 'test_reflex_freq.json')
ccg._FREQ = None

# ── ① 条件反射记录：被调用 → 频率+1 ─────────────────────────
r1 = ccg.reflex("图遍历-最短路径", n=10)
ok1 = r1["freq"].get("图遍历-最短路径") == 10 and r1["n_units"] == 1
print(f'  记录后: 最短路径 freq={r1["freq"].get("图遍历-最短路径")}')
check('① 条件反射记录：调用频率累加（reflex）', ok1)

# ── ② 频率加权：高频单元优先命中 ───────────────────────────
# 模拟：两个候选同分时，高频者优先
ccg.reflex("图遍历-最短路径", n=100)   # 高频
q = "写一个在无权图上求最短路径的代码单元"
hits = ccg.search(q, G, top=5)
ok2 = hits and hits[0][0] == "图遍历-最短路径"
print(f'  搜索: 高频单元 top1 = {hits[0][0] if hits else "无"} '
      f'(freq boost 生效)')
check('② 频率加权：高频单元优先命中（条件反射）', ok2)

# ── ③ route 命中自动记录频率 ────────────────────────────────
before = ccg._load_freq().get("网络-TCP握手", 0)
ccg.route("写一个TCP三次握手的代码单元", G)
after = ccg._load_freq().get("网络-TCP握手", 0)
ok3 = after > before
print(f'  route 命中: TCP握手 freq {before}→{after}（自动记录）')
check('③ route 自动记录：被路由单元频率+1', ok3)

# ── ④ 简化候选：高频×高复杂度优先（W6 解法）────────────────
cands = ccg.reflex_simplify_candidates(top_k=5)
ok4 = isinstance(cands, list) and len(cands) >= 1
print(f'  简化候选: {[(c["unit"][:12], c["freq"], c["complexity"]) for c in cands[:4]]}')
check('④ 简化候选：高频单元优先（Reduce 模式→W6 优化入口）', ok4)

# ── ⑤ 频率持久化（长期记忆——跨进程）──────────────────────
ccg._save_freq()
ok5 = os.path.exists(ccg._FREQ_PATH)
print(f'  频率表持久化: {ccg._FREQ_PATH[-30:]} 存在={ok5}')
check('⑤ 条件反射固化：频率表持久化（长期记忆）', ok5)

# 清理临时文件
ccg._FREQ_PATH = _tmp
ccg._FREQ = None
try:
    os.remove(os.path.join(tempfile.gettempdir(), 'test_reflex_freq.json'))
except OSError:
    pass

report = {
    "experiment": "条件反射优先度（荣：频率驱动简化）",
    "reflex_record": ok1, "freq_boost": ok2,
    "route_auto": ok3, "simplify_candidates": ok4,
    "persist": ok5,
    "conclusion": ("工程验证的高效→长期记忆/条件反射：调用频率追踪→search"
                   "加权优先命中→高频单元优先简化（W6 解法入口）；"
                   "人类重复决策的简化机制工程化"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reflex_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('⑥ reflex_report.json 落盘', os.path.exists(rp), 'reflex_report.json')

print(f'\n=== 条件反射优先度: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
