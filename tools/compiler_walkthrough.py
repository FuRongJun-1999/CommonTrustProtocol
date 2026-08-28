# -*- coding: utf-8 -*-
"""compiler_walkthrough.py · protocol-compiler 全链路演示（架构展示第三段）

一个中文程序的完整生命：源码 → 词法 → 字节码 → VM 执行 → 结果。
每阶段产物可追溯——这就是白箱「可解释性」的直观形态。
输出：markdown 演示文档（供架构展示第三段嵌入）。
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
PC = r"D:\Program Files\2_ai\protocol-compiler"
sys.path.insert(0, PC)

from core.compiler import compile_source  # noqa: E402
from core.condition_vm import ConditionVM  # noqa: E402

PROGRAM = ("定义 阶乘（n）：若 n 小于 2，则 返回 1，"
           "否则 返回 n 乘 阶乘（n 减 1）；结果 = 阶乘（5）；止。")

out = []


def w(s=""):
    out.append(s)


w("# protocol-compiler 全链路演示 · 一个中文程序的完整生命")
w("")
w(f"**源程序**：`{PROGRAM}`")
w("")
w("---")
w("")
w("## 阶段 1 · 词法分析（字符流 → 记号流）")
w("")
w("每个记号可对照词法规则溯源——中文标识符、全角括号、中文运算词"
  "（加/减/乘/大于/等于）各自成类。")
w("")
w("```")
code, result = compile_source(PROGRAM, strict=False)
# 重新 tokenize 展示（compile_source 内部已做，这里复现词法输出）
from core.compiler import tokenize  # noqa: E402
tokens, lex_errors = tokenize(PROGRAM)
w(f"记号总数: {len(tokens)}（词法错误: {len(lex_errors)}）")
w("前 12 个记号:")
for t in tokens[:12]:
    w(f"  {t}")
w("  …")
w("```")
w("")
w("## 阶段 2 · 字节码（语法树 → 栈机指令）")
w("")
w("函数定义编译为「跳过函数体 + 入口标签」结构；调用编译为 CALL 指令"
  "（携带参数个数与参数名——名实校验的载体）。")
w("")
w("```")
w(f"指令总数: {len(code)}")
for i, (op, arg) in enumerate(code):
    w(f"  {i:3d}  {op.name:<14} {arg!r}" if arg is not None else f"  {i:3d}  {op.name}")
w("```")
w("")
w("**可读性注解**：`LOAD_NAME n` 读取参数；`CALL (1, ['n'])` 自调用"
  "（1 个参数 n——递归）；`MUL` 相乘；`RETURN` 返回；"
  "主流程 `PUSH_CONST 5.0` → `CALL (1, ['n'])` → `STORE_NAME 结果` → `ZHI`（止）。")
w("")
w("## 阶段 3 · VM 执行（栈机 → 符号表）")
w("")
w("```")
vm = ConditionVM()
vm.run(code)
w(f"执行完成。符号表: {vm.symbols}")
w(f"「结果」= {vm.symbols.get('结果')}  （期望 120.0）")
w("```")
w("")
w("## 阶段 4 · 验收（T9-2 自验收基准）")
w("")
w("| 任务 | 期望 | 实测 |")
w("|---|---|---|")
BASE = {
    "递归阶乘": (PROGRAM, 120.0),
    "递归累加": ("定义 累加（n）：若 n 等于 1，则 返回 1，否则 返回 n 加 累加（n 减 1）；结果 = 累加（5）；止。", 15.0),
    "算术优先级": ("结果 = 3 加 4 乘 2；止。", 11.0),
    "条件判断": ("若 5 大于 3，则 结果 = 1，否则 结果 = 0；止。", 1.0),
    "双递归斐波那契": ("定义 斐波那契（n）：若 n 小于 2，则 返回 n，否则 返回 斐波那契（n 减 1）加 斐波那契（n 减 2）；结果 = 斐波那契（6）；止。", 8.0),
}
for name, (prog, expect) in BASE.items():
    c, r = compile_source(prog, strict=False)
    v = ConditionVM()
    v.run(c)
    got = v.symbols.get("结果")
    ok = got is not None and abs(got - expect) < 0.01
    w(f"| {name} | {expect} | {got} {'✓' if ok else '✘'} |")
w("")
w("## 诚实面 · 可解释性的自证")
w("")
w("白箱不等于没有缺陷——等于**缺陷也可定位**。本轮实测发现四个调用限制"
  "（多参数/嵌套调用/若则体非递归调用/多函数定义），定位方法："
  "逐变体 dump 字节码对照（字符串化 vs CALL 指令），每一步证据可复现。"
  "黑箱系统的同类问题只能看到「输出不对」。")

text = "\n".join(out)
dst = os.path.join(HERE, "..", "docs", "灵枢架构展示_第三段_compiler全链路.md")
open(dst, "w", encoding="utf-8").write(text + "\n")
print(f"演示文档已生成: {dst}（{len(text)} 字）")
