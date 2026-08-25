# -*- coding: utf-8 -*-
"""test_verifier_consistency.py · 校验一致率对照（阶段 5 证据）

对六域 681 单元做确定性变异（比较反转 / 返回破坏 / 常量扰动），
同一变异代码分别经「旧三层 verify_code」与「新六层 Verifier」裁决，
统计判定一致性：
  agree      —— 两者判定相同（pass/pass 或 fail/fail）
  directional —— verifier 更严（verify_code pass 而 verifier fail）：
                 六层多了边界/规范层，更严是合理增强，不视为不一致
  reverse    —— verifier 放行而 verify_code 拒绝：严重不一致，必须为 0

目标：reverse == 0 且 一致率（agree+directional 占比）≥ 99%。
"""
import sys, io, ast, copy
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')

from verifier import Verifier, VerifyRequest
from code_compose import verify_code
from compiler_code_units import COMPILER_UNITS
from python_code_units import PYTHON_UNITS
from graph_db_units import GRAPH_UNITS
from os_units import OS_UNITS
from browser_units import BROWSER_UNITS
from net_units import NET_UNITS

DOMAINS = [('compiler', COMPILER_UNITS), ('pylang', PYTHON_UNITS),
           ('graph', GRAPH_UNITS), ('os', OS_UNITS),
           ('browser', BROWSER_UNITS), ('net', NET_UNITS)]

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')


def mutate_cmp_flip(code):
    """变异①：反转第一个比较运算符（> 与 < 互换）。

    注意：代码含 while 时跳过——while 条件反转会把终止条件改坏成死循环
    （L2 样例执行卡死），for 循环的比较反转只影响 if 分支，安全。
    """
    if "while" in code:
        return None
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    changed = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                if isinstance(op, ast.Gt):
                    node.ops[i] = ast.Lt(); changed = True
                elif isinstance(op, ast.Lt):
                    node.ops[i] = ast.Gt(); changed = True
            if changed:
                break
    if not changed:
        return None
    try:
        return ast.unparse(tree)
    except Exception:
        return None


def mutate_return_break(code):
    """变异②：最后一个 return 改为 return None（破坏返回语义）。"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    returns = [n for n in ast.walk(tree) if isinstance(n, ast.Return)]
    if not returns:
        return None
    returns[-1].value = ast.Constant(value=None)
    try:
        return ast.unparse(tree)
    except Exception:
        return None


def mutate_const_bump(code):
    """变异③：第一个数字常量 +1（数值扰动）。"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    bumped = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                and not isinstance(node.value, bool):
            node.value = node.value + 1
            bumped = True
            break
    if not bumped:
        return None
    try:
        return ast.unparse(tree)
    except Exception:
        return None


MUTATORS = [('比较反转', mutate_cmp_flip), ('返回破坏', mutate_return_break),
            ('常量扰动', mutate_const_bump)]

v = Verifier()
agree = directional = reverse = total = 0
reverse_detail = []

for dname, units in DOMAINS:
    for uid, u in units.items():
        kw = {'inject': True} if u.get('needs_inject') else {}
        for mname, mut in MUTATORS:
            mcode = mut(u['pattern'])
            if mcode is None or mcode == u['pattern']:
                continue  # 变异不适用（无比较/无return/无数值）或未生效
            total += 1
            # 旧三层裁决（深拷贝 cases——verify_code 原地修改输入会污染共享对象）
            u_old = dict(u)
            u_old['cases'] = copy.deepcopy(u.get('cases', []))
            ok_old, _ = verify_code(mcode, u_old, "python")
            # 新六层裁决（独立深拷贝，防跨裁决污染）
            r = v.verify(VerifyRequest(task=u['task'], code=mcode, unit_id=uid,
                                       cases=copy.deepcopy(u.get('cases', [])),
                                       expected_structure=kw))
            ok_new = r.ok
            if ok_old == ok_new:
                agree += 1
            elif ok_old and not ok_new:
                directional += 1  # verifier 更严（边界/规范层额外拦截）
            else:
                reverse += 1
                reverse_detail.append((uid, mname, r.reason[:60]))

agree_rate = 100.0 * (agree + directional) / total if total else 0.0
print(f"变异对照: 共 {total} 组（agree {agree} / verifier更严 {directional} / 反向分歧 {reverse}）")
print(f"一致率（agree+更严）: {agree_rate:.2f}%（目标 ≥99%）")
for uid, mname, reason in reverse_detail[:10]:
    print(f"  [反向分歧] {uid} {mname} → {reason}")

check('① 反向分歧为 0（verifier 不放行旧三层拒绝的代码）',
      reverse == 0, f'reverse={reverse}')
check('② 一致率 ≥ 99%（agree + verifier更严）',
      agree_rate >= 99.0, f'{agree_rate:.2f}%')
check('③ 变异有效性：至少 300 组变异成功生成',
      total >= 300, f'{total} 组')

print(f'\n=== 校验一致率对照: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
