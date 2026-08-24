# -*- coding: utf-8 -*-
"""test_mini_python_p1.py · Mini-Python P1 测试（第六阶段·机制训练场）
验证：①算术/优先级 ②幂/一元负号 ③floor 语义 ④逻辑短路+返回操作数 ⑤链式比较
⑥与 CPython eval 对拍 ⑦除零错误"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from mini_python import eval_expr, MiniPyError

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 算术/优先级
check('①a 优先级 2+3*4=14', eval_expr("2+3*4") == 14)
check('①b 括号 (2+3)*4=20', eval_expr("(2+3)*4") == 20)
check('①c 幂右结合 2**3**2=512', eval_expr("2**3**2") == 512)
check('①d 一元负号 -5+3=-2', eval_expr("-5+3") == -2)

# ② 幂与一元负号：-2**2 = -4（** 绑定更紧）
check('② -2**2 = -4', eval_expr("-2**2") == -4)
check('②b 2**-1 = 0.5', eval_expr("2**-1") == 0.5)

# ③ floor 语义（Python）
check('③a 4/2 = 2.0(float)', eval_expr("4/2") == 2.0 and type(eval_expr("4/2")) is float)
check('③b -7//2 = -4', eval_expr("-7//2") == -4)
check('③c -7%2 = 1', eval_expr("-7%2") == 1)

# ④ 逻辑短路 + 返回操作数（Python 语义）
check('④a True or 1/0 短路', eval_expr("True or 1/0") is True)
check('④b 0 and 1/0 短路', eval_expr("0 and 1/0") == 0)
check('④c 0 or 5 → 5(操作数)', eval_expr("0 or 5") == 5)
check('④d 2 and 3 → 3(操作数)', eval_expr("2 and 3") == 3)
check('④e not 1>2 → True', eval_expr("not 1>2") is True)

# ⑤ 链式比较
check('⑤ 1<2<3 → True', eval_expr("1<2<3") is True)

# ⑥ 与 CPython eval 对拍（固定测试表达式，安全）
PAIRS = [
    "2+3*4", "2**3**2", "-2**2", "4/2", "10//3", "-7//2", "-7%2",
    "3>2", "not 1>2", "0 or 5", "2 and 3", "1<2<3", "(2+3)*4",
    "-5+3", "2**-1", "7%3", "6/2", "10-3*2", "2*3+4*5",
]
all_match = True
for e in PAIRS:
    mine = eval_expr(e)
    ref = eval(e)  # CPython 参考（固定表达式）
    if mine != ref or type(mine) is not type(ref):
        all_match = False
        print(f"    对拍不符: {e} → mine={mine!r} cp={ref!r}")
check('⑥ CPython 对拍 19 个表达式', all_match, f'{len(PAIRS)} 个')

# ⑦ 除零错误
try:
    eval_expr("1/0")
    check('⑦ 除零错误', False, '未抛错')
except MiniPyError:
    check('⑦ 除零错误', True, '')

print(f'\n=== Mini-Python P1 测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
