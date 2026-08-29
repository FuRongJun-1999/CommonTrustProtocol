# -*- coding: utf-8 -*-
"""test_kccs_lsp.py · LSP 两能力冒烟（悬停卡数据源 + R1-R3 诊断函数）"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aeis"))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aeis", "wisdom"))

from kccs_lsp import hover_card, validate_condition_word

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")

# ============ 悬停卡数据源 ============
card = hover_card("插入排序")
check("悬停卡：插入排序命中", card is not None and "KCCS 条件卡" in card, str(card)[:60])
check("悬停卡四要素：生效条件", card and "生效条件" in card)
check("悬停卡四要素：执行", card and "执行" in card)
check("悬停卡四要素：不适用条件", card and "不适用条件" in card)
card2 = hover_card("白箱智能")
check("悬停卡：白箱智能命中", card2 is not None and "白箱" in card2, str(card2)[:60])
check("悬停卡：无关词返回 None", hover_card("qqxyzzy") is None)

# ============ R1-R3 诊断函数 ============
check("诊断 R1 非问句", validate_condition_word("说睡不着") is not None)
check("诊断 R2 括号同义", validate_condition_word("问GIL（全局解释器锁）") is not None)
check("诊断 R3 含空格", validate_condition_word("问1 2 3 是什么") is not None)
check("诊断 合规词通过", validate_condition_word("问插入排序") is None)

print(f"\n=== 判定 ===")
print(f"LSP 能力冒烟: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
