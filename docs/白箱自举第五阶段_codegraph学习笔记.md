# 白箱自举第五阶段 · codegraph-ref 学习笔记（代码编写能力深学）

> 学习对象：D:\Program Files\2_ai\codegraph-ref（CodeGraph：跨语言代码智能的 Rust 工程，
> 38 语言 tree-sitter 解析、语义图、42 MCP 工具、VS Code/JetBrains 插件、持久记忆层）
> 目的：提取可复用的代码编写模式 → 落地白箱代码能力（零 LLM 代码理解）。

## 一、架构模式（crates 模块化）

```
crates/
  codegraph               核心图库（图存储/查询/算法/导出）
  codegraph-{lang}        每语言一 crate 解析器（python/rust/js/... 38 个）
  codegraph-parser-api    统一解析接口（IR/entities/relationships/traits）
  codegraph-server        MCP 服务器（42 工具）
  codegraph-memory        持久记忆层
  codegraph-harness       测试/基准
```

**可复用模式 ①「解析器矩阵」**：一语言一 crate，全部实现统一 parser-api trait ——
新语言 = 新 crate 实现同一接口，主图库零改动。

## 二、统一 IR 模式（CodeIR）

语言特定 AST → **统一中间表示** → 批量入图：

```rust
CodeIR {
  file_path, module, functions, classes, traits,
  calls, imports, inheritance, implementations, type_references
}
```

**可复用模式 ②「AST→IR→图 三级桥」**：语言差异在 IR 层收敛，图库只认 IR。
与白箱「感知原语→记忆」同构：异构输入 → 统一原语 → 统一存储。

## 三、类型化图模型

```
NodeType: CodeFile/Function/Class/Module/Variable/Type/Interface/Generic
EdgeType: Imports/ImportsFrom/Contains/Calls/Invokes/Instantiates/
          Extends/Implements/Uses/Defines/References/RuntimeCalls
```

**可复用模式 ③「节点+边双类型化」**：与灵枢知识图同构（STNode/STEdge 类型化）。
边类型 = 关系语义（调用/依赖/包含/实现）——图查询按边类型定向遍历。

## 四、图算法（BFS/DFS/Tarjan SCC/路径）

- `bfs(graph, start, direction, max_depth)`：可达节点（影响分析/依赖树）
- 迭代式 DFS（防深图栈溢出）
- Tarjan SCC：环检测（循环依赖）
- direction 双向遍历：正向=它调用谁，逆向=谁调用它

**可复用模式 ④「影响分析」**：改函数 → BFS 逆向求调用面（谁受影响）。
这是代码理解对工程的价值：改前先算影响面。

## 五、可插拔存储

`memory`（内存）/ `rocksdb`（持久）/ `namespaced`（命名空间隔离）——统一 Storage trait。
**可复用模式 ⑤「存储后端抽象」**：接口稳定，后端可换（与白箱 5 副本同精神）。

## 六、落地白箱代码能力（本阶段交付）

`tools/codegraph_white.py` —— 白箱代码 IR 提取器 + 调用图 + 影响分析 + 环检测
（Python 内置 ast 模块，零 LLM，模式 ②③④ 落地）：
1. extract_code_ir：源码 → 统一 IR（函数/类/导入/调用）
2. build_call_graph：IR → 调用图（Function 节点 + Calls 边）
3. impact_analysis：改函数 → 调用面（BFS 逆向，同 codegraph impact_analysis 示例）
4. detect_cycles：调用环检测（Tarjan SCC，同 codegraph algorithms）

## 七、与白箱路由图的同构

codegraph 的 EdgeType::Calls（A 调用 B）↔ 白箱条件链（条件 → 规律）；
代码影响分析（谁依赖我）↔ 灵枢因果上游度传播（concept_influence）；
统一 IR ↔ 条件化单元蒸馏（异构知识 → 统一 {条件→规律} 形态）。
