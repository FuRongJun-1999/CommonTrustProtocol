# -*- coding: utf-8 -*-
"""test_compiler_compose.py · 编译原理概念测试（第四阶段·代码深学）
验证：①八概念组合生成 ②概念核心词自校验 ③方向识别 ④非编译问题回落"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from compiler_compose import compiler_route, identify_compiler_direction

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 八概念组合生成（答案含核心词≥2 由自校验保证，这里再验关键语义词）
QS = {
    "为什么要词法分析？": ("词法", "token"),
    "什么是语法分析？": ("语法", "AST"),
    "什么是中间表示（IR）？": ("中间表示", "后端"),
    "类型检查有什么好处？": ("类型", "编译期"),
    "编译优化是什么？": ("优化", "语义"),
    "代码生成阶段做什么？": ("代码生成", "目标"),
    "符号表是什么？": ("符号表", "作用域"),
    "编译器怎么处理错误？": ("错误", "定位"),
}
for q, (kw1, kw2) in QS.items():
    r = compiler_route(q)
    ans = r.get("answer", "")
    ok = r.get("ok") and kw1 in ans and kw2 in ans
    check(f'① 概念生成: {q[:14]}…', ok, ans[:36])

# ② 方向识别（最长关键词：中间表示 len4 > 表示）
check('②a 词法识别', identify_compiler_direction("词法分析有什么用") == "词法")
check('②b 中间表示识别', identify_compiler_direction("IR 是什么") == "中间表示")
check('②c 类型检查识别', identify_compiler_direction("静态类型的好处") == "类型检查")

# ③ 非编译问题回落
r = compiler_route("什么是碳中和？")
check('③ 非编译问题回落', not r.get("ok") and "落回" in r.get("reason", ""))

# ④ 跨域不串扰：软件工程问题不命中编译域
r = compiler_route("为什么要写单元测试？")
check('④ 软件工程问题不串扰', not r.get("ok"))

print(f'\n=== 编译原理概念测试: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
