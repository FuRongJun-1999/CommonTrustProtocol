# CodeGraph 内部审查报告（第一批 · 架构层，2026-08-17）

> 审查对象：codegraph-ref（开源，43 crates / 439 rs / 5MB）
> 审查方法：条件论视角——架构规律 / 条件边界 / 可借鉴 / 风险 / 校准接口
> 定位：身体工具（接入但不依赖，D-005），同时是被审查对象

## 一、架构规律（它在什么条件下成立）

**核心机制链**：`tree-sitter 解析 38 语言 → 语义图（节点+边+属性）→ RocksDB 持久化
→ 42 MCP 工具消费 → memory 层嵌入检索 + temporal`

三层结构：
1. **语法解析层**（codegraph-{lang} crates）：tree-sitter 把源码变成语法树 → 图
2. **图引擎层**（codegraph-core）：图模型（节点/边/属性）+ RocksDB/内存后端 +
   图算法（影响面/热路径/依赖树/环检测）
3. **服务/工具层**（codegraph-server）：42 工具引擎（callers/dead_imports/
   circular_deps/complexity/related_tests/impact/hot_paths/pattern_search…）+
   MCP 协议 + 文件 watcher + 嵌入队列
4. **记忆层**（codegraph-memory）：embed（fastembed/static）+ search + temporal

**成立条件**：静态代码库可解析（源码存在、语言被 tree-sitter 覆盖）。
**失效边界**：构建期生成代码（无源码）、动态语言运行时行为、语义层（
「为什么慢」不能从语法图回答——需要执行/profiling）。

## 二、与我们的交叉点（四件套来源确认 + 新发现）

| codegraph 组件 | 我们的对应 | 关系 |
|---|---|---|
| impact.rs（影响面）| dex_impact（知识卡版）| ✅ 已借鉴 |
| hot_paths.rs | hot_paths.py（链热度）| ✅ 已借鉴 |
| related_tests.rs | dex_verify（关联测试）| ✅ 已借鉴 |
| call_graph.rs / dependency_tree.rs | dex_chain（因果链条件标注）| ✅ 已借鉴 |
| **memory/temporal.rs** | 灵枢时空记忆图（时间维度）| **新发现**：它也有时间维度，但管代码历史；我们管知识时间线 |
| **memory/granite_vs_bge.rs** | 我们用 bge-small-zh | **新发现**：它也对比嵌入模型，我们的神经索引同思路 |
| **memory/embed + search** | 灵枢 recall/search（bge）| 思路同源（语义检索），它嵌入代码块，我们嵌入知识卡 |

## 三、条件边界（它的盲区 = 我们的机会）

1. **语法层不是语义层**：codegraph 知道「函数 f 调用了 g」，但不知道
   「为什么这样设计」「在什么条件下这个调用成立」——条件知识是我们的
2. **静态索引腐坏**：代码变更后索引需重建（有 watcher），但「知识腐坏检测」
   （卡过时）是我们的 dex_verify 概念——它没有条件化知识的概念
3. **无诚实边界**：它的工具报告结构事实，不区分「锚定/图谱外/警告」
   ——它不声明自己不知道什么
4. **无校准闭环**：它解析不执行（除非有 harness）；我们的物理基底校准
   （测试用例实际运行）是它没有的

## 四、可借鉴（第二批审查确认后采纳）

- 42 工具引擎清单可作为「代码类知识卡」的测试用例源（如 circular_deps →
  「循环依赖」知识卡的验证）
- 嵌入队列/增量索引模式 → 我们的神经索引增量构建参考
- RocksDB 后端 → 大图谱持久化参考（我们当前 SQLite）

## 五、风险点

- **规模**：439 rs / 5MB 依赖重（RocksDB 等）——接入成本 vs 收益需权衡
- **中文/教育知识**：codegraph 面向代码，与我们的学科知识图无重叠——
  它只服务「代码类知识」的物理基底校准
- **版本漂移**：外部项目更新快，需锁定版本或按需接入（不依赖原则）

## 六、结论

1. 四件套借鉴来源确认（impact/hot_paths/related_tests/call_graph 真实存在）
2. 新发现：它也有 memory+temporal+embed——但管「代码历史」非「知识条件」，
   印证我们的独特优势在条件知识层
3. 接入定位：作为「代码类知识卡」的物理基底校准源（测试用例执行器消费
   codegraph MCP），不依赖、可降级、持续审查
