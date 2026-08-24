# 白箱自举第六阶段 · Mini-Python P1：词法 + 语法 + 表达式求值

> 文档先行 → 复现纪律（先自设计 → 对照 CPython 行为验证）。
> 第一个项目「复现 Python」的 P1：**表达式求值器**（词法→语法→AST→求值）。
> 设计原则：行为对照 CPython（`x or y` 返回操作数而非布尔；`/` 返回 float；`//` floor；
> `**` 右结合且优先级高于一元负号：`-2**2 = -4`）。

## 一、词法（token 类型）

| 类型 | 例子 |
|---|---|
| NUMBER | 42 / 3.14 |
| 运算符 | + - * / // % ** == != < > <= >= |
| 逻辑 | and or not |
| 括号 | ( ) |
| 关键字 | True False None |
| EOF | — |

## 二、文法（Python 优先级，低→高）

```
expr      → or_expr
or_expr   → and_expr ('or' and_expr)*          # 返回操作数（Python 语义）
and_expr  → not_expr ('and' not_expr)*
not_expr  → 'not' not_expr | comparison
comparison→ arith (('=='|'!='|'<'|'>'|'<='|'>=') arith)*
arith     → term (('+'|'-') term)*
term      → factor (('*'|'/'|'//'|'%') factor)*
factor    → ('-'|'+') factor | power            # 一元负号在外层：-2**2 = -(2**2)
power     → atom ('**' factor)?                 # 右结合：2**2**3 = 2**(2**3)
atom      → NUMBER | True | False | None | '(' expr ')'
```

## 三、求值规则（对照 CPython）

| 规则 | Python 行为 |
|---|---|
| 真值 | False/None/0/0.0 → 假，其余真 |
| or/and | 返回操作数本身（`0 or 5` → 5；`2 and 3` → 3），短路 |
| / | 返回 float（`4/2` → 2.0） |
| // % | floor 除 / floor 模（`-7//2` → -4；`-7%2` → 1） |
| ** | 右结合；`-2**2` → -4；`2**-1` → 0.5 |
| 除零 | 运行时错误（短路避免：`True or 1/0` 不报错） |

## 四、对照验证

测试 helper：`assert_eq(src, expect)` + **CPython eval 对照**（固定测试表达式，
非用户输入——安全边界）：`assert_matches_cpython(src)` 用 Python 内建 eval 对拍。

## 五、判定标准（P1）

1. 算术/优先级：2+3*4=14、2**3**2=512、-2**2=-4 ✔
2. 比较链：1<2<3=True（链式比较 Python 语义）✔
3. 逻辑短路：True or 1/0 不报错返回 True；0 and 1/0 → 0 ✔
4. or/and 返回操作数：0 or 5 → 5 ✔
5. floor 语义：-7//2=-4、-7%2=1、4/2=2.0 ✔
6. CPython 对拍 ≥10 表达式全一致 ✔
7. 测试全绿 → 提交 → 五副本同步
