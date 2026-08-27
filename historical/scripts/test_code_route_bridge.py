# -*- coding: utf-8 -*-
"""test_code_route_bridge.py · 代码图↔条件路由图双向映射测试（第五阶段）
验证：①仓库→代码条件单元库 ②雅可比独立性 ③并行测试分组 ④共享依赖隔离 ⑤空边界"""
import sys, os, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from codegraph_white import analyze_repository
from code_route_bridge import (build_code_route_units, code_jacobian_independence,
                               parallel_test_groups)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# 仓库：base 被 a/b 依赖；c 依赖 a（链式）；d 独立
tmp = tempfile.mkdtemp(prefix="crb_")
with open(os.path.join(tmp, "lib.py"), "w", encoding="utf-8") as f:
    f.write("def base(x):\n    return x\n\n"
            "def a():\n    return base(1)\n\n"
            "def b():\n    return base(2)\n\n"
            "def c():\n    return a()\n\n"
            "def d():\n    return 42\n")
repo = analyze_repository(tmp)
units = build_code_route_units(repo)

# ① 代码条件单元库
check('①a 单元库覆盖函数', set(units.keys()) == {"base", "a", "b", "c", "d"},
      str(sorted(units.keys())))
check('①b 依赖=被调函数', units["a"]["conditions"] == ["base"]
      and units["c"]["conditions"] == ["a"] and units["d"]["conditions"] == [],
      str({k: u["conditions"] for k, u in units.items()}))

# ② 雅可比独立性：a×b 共享 base → 不独立；d×a 无共享 → 独立
j = code_jacobian_independence(units)
pair_map = {(a, b): (indep, shared) for a, b, indep, shared in j["pairs"]}
check('②a a×b 共享base不独立', pair_map[("a", "b")][0] is False
      and pair_map[("a", "b")][1] == ["base"], str(pair_map.get(("a", "b"))))
check('②b d×a 独立', pair_map[("a", "d")][0] is True, str(pair_map.get(("a", "d"))))

# ③ 并行测试分组：a/b 共享 base → 不同组；d 独立可并入
groups = parallel_test_groups(units)
flat = [g for g in groups]
check('③a 分组覆盖全部函数', sorted(x for g in flat for x in g) ==
      sorted(units.keys()), str(flat))
check('③b 独立函数并组', any("d" in g and len(g) >= 2 for g in flat), str(flat))

# ④ 共享依赖隔离：a 与 b 不在同组（共享 base）
def same_group(x, y, gs):
    return any(x in g and y in g for g in gs)
check('④ a/b 共享依赖不同组', not same_group("a", "b", flat), str(flat))

# ⑤ 空仓库边界
empty = tempfile.mkdtemp(prefix="crb_e_")
u0 = build_code_route_units(analyze_repository(empty))
check('⑤ 空仓库边界', u0 == {}, '')

shutil.rmtree(tmp, ignore_errors=True)
shutil.rmtree(empty, ignore_errors=True)

print(f'\n=== 代码图↔路由图映射测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
