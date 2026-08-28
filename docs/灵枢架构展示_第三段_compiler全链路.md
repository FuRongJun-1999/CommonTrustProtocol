# protocol-compiler 全链路演示 · 一个中文程序的完整生命

**源程序**：`定义 阶乘（n）：若 n 小于 2，则 返回 1，否则 返回 n 乘 阶乘（n 减 1）；结果 = 阶乘（5）；止。`

---

## 阶段 1 · 词法分析（字符流 → 记号流）

每个记号可对照词法规则溯源——中文标识符、全角括号、中文运算词（加/减/乘/大于/等于）各自成类。

```
记号总数: 36（词法错误: 0）
前 12 个记号:
  Token(DINGYI, '定义', L1:C1)
  Token(IDENTIFIER, '阶乘', L1:C4)
  Token(LPAREN, '（', L1:C6)
  Token(IDENTIFIER, 'n', L1:C7)
  Token(RPAREN, '）', L1:C8)
  Token(COLON, '：', L1:C9)
  Token(RUO, '若', L1:C10)
  Token(IDENTIFIER, 'n', L1:C12)
  Token(XIAOYU, '小于', L1:C14)
  Token(NUMBER, '2', L1:C18)
  Token(COMMA, '，', L1:C18)
  Token(ZE, '则', L1:C19)
  …
```

## 阶段 2 · 字节码（语法树 → 栈机指令）

函数定义编译为「跳过函数体 + 入口标签」结构；调用编译为 CALL 指令（携带参数个数与参数名——名实校验的载体）。

```
指令总数: 20
    0  JUMP           16
    1  LOAD_NAME      'n'
    2  PUSH_CONST     2.0
    3  CMP_LT
    4  JUMP_IF_FALSE  8
    5  PUSH_CONST     1.0
    6  RETURN
    7  JUMP           15
    8  LOAD_NAME      'n'
    9  LOAD_NAME      'n'
   10  PUSH_CONST     1.0
   11  SUB
   12  CALL           (1, ['n'])
   13  MUL
   14  RETURN
   15  RETURN
   16  PUSH_CONST     5.0
   17  CALL           (1, ['n'])
   18  STORE_NAME     '结果'
   19  ZHI
```

**可读性注解**：`LOAD_NAME n` 读取参数；`CALL (1, ['n'])` 自调用（1 个参数 n——递归）；`MUL` 相乘；`RETURN` 返回；主流程 `PUSH_CONST 5.0` → `CALL (1, ['n'])` → `STORE_NAME 结果` → `ZHI`（止）。

## 阶段 3 · VM 执行（栈机 → 符号表）

```
执行完成。符号表: {'结果': 120.0}
「结果」= 120.0  （期望 120.0）
```

## 阶段 4 · 验收（T9-2 自验收基准）

| 任务 | 期望 | 实测 |
|---|---|---|
| 递归阶乘 | 120.0 | 120.0 ✓ |
| 递归累加 | 15.0 | 15.0 ✓ |
| 算术优先级 | 11.0 | 11.0 ✓ |
| 条件判断 | 1.0 | 1.0 ✓ |
| 双递归斐波那契 | 8.0 | 8.0 ✓ |

## 诚实面 · 可解释性的自证

白箱不等于没有缺陷——等于**缺陷也可定位**。本轮实测发现四个调用限制（多参数/嵌套调用/若则体非递归调用/多函数定义），定位方法：逐变体 dump 字节码对照（字符串化 vs CALL 指令），每一步证据可复现。黑箱系统的同类问题只能看到「输出不对」。
