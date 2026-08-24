# 白箱自举第六阶段 · C1：字节码 VM 指令集 + 迷你 VM 骨架

> 文档先行 → 复现纪律（先自设计 → 对照 protocol-compiler 既有语义验证）。
> 中文编译器「原生编译」第一块地基：**智能论字节码 VM**——
> 道德经助记符 → 指令，条件空间/信任 成为 VM 内建状态（非外部运行时调用）。

## 一、指令集（Opcode 编码表）

| 编码 | 指令 | 参数 | 语义（智能论） |
|---|---|---|---|
| 0 | PUSH_CONST | value | 压字面量 |
| 1 | LOAD_NAME | name | 符号表取值（以名举实的读取）|
| 2 | STORE_NAME | name | 栈顶存符号（以名举实的写入）|
| 3 | JUMP | addr | 无条件跳转 |
| 4 | JUMP_IF_FALSE | addr | 栈顶假则跳（若…则…否则）|
| 5 | DAO | name | **道**：创建协议路径（条件空间栈压入）|
| 6 | DE | amount | **德**：信任值累积（信任引擎内建）|
| 7 | ZIRAN | — | **自然**：恢复默认条件空间（弹栈到根）|
| 8 | WUWEI | — | **无为**：让出控制（yield 暂停）|
| 9 | ZHI | — | **止**：停止执行（halt）|
| 10 | ZHIZU | threshold, addr | **知足**：信任≥threshold 跳转（达标判定）|
| 11-13 | CMP_EQ/GT/LT | — | 中文比较词（等于/大于/小于）|
| 14 | ENTER_SHUYUE | — | 进入术曰块（作用域）|
| 15 | RETURN_STEP | — | 步骤返回（出作用域）|

## 二、VM 状态（智能论语义内建）

```
ip             指令指针
stack          值栈
symbols        符号表（名实对应：名→实）
condition_stack 条件空间栈（DAO 压入，ZIRAN 归根——对应灵枢条件路由）
trust_value    信任值寄存器（DE 累积，ZHIZU 判定）
halted / yield 停止/让出状态
```

## 三、汇编器（文本 → 字节码）

```
DAO 新信任路径
DE 0.3
ZHIZU 0.7 @L1
PUSH_CONST 1
STORE_NAME 甲
L1: ZHI
```
支持标签（L1:）与 @L1 引用 → 汇编为指令序列。

## 四、对照验证（C1 判定）

1. 道→德→知足→止：信任 0.3 不达 0.7 不跳，再德 0.5 → 知足跳 → 止 ✔
2. 条件空间栈：DAO×2 → ZIRAN → 回根 ✔
3. JUMP_IF_FALSE：若…则 语义（假跳真续）✔
4. LOAD/STORE：名实符号表读写 ✔
5. WUWEI：让出控制（yield 而非终止）✔
6. 汇编标签解析 ✔
7. 测试全绿 → 提交 → 五副本同步
