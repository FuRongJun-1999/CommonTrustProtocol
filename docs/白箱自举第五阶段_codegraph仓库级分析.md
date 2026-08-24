# 白箱自举第五阶段 · codegraph 仓库级分析（代码理解能力深化）

> 文档先行 → 工程验证。codegraph_white v1（单文件 IR/调用图/影响分析/环检测）已成立；
> 本扩展升级到**仓库级**（多文件）：文件级依赖树 + 跨文件调用解析 + 仓库统计。
> 模式来源：codegraph dependency_tree / call_graph 示例。

## 一、设计

```
仓库目录（多 .py 文件）
  ├─ analyze_repository：逐文件 extract_code_ir → 合并仓库 IR
  │    （functions/classes/imports 带文件归属 file）
  ├─ build_dependency_tree：文件级导入依赖（A imports B → 边）
  └─ cross_file_calls：跨文件调用解析（函数定义在文件 B，被文件 A 调用 → 跨文件边）
```

## 二、模块扩展（codegraph_white.py）

| 函数 | 职责 |
|---|---|
| analyze_repository | 目录 → 仓库 IR（每文件 IR 合并 + 文件归属） |
| build_dependency_tree | 仓库 IR → 文件依赖树（导入边） |
| cross_file_calls | 跨文件调用解析（调用目标定位到定义文件） |
| repo_stats | 仓库统计（文件/函数/类/调用/导入数） |

## 三、判定标准

1. 仓库 IR：3 文件样例 → 函数/类带 file 归属 ✔
2. 依赖树：main→utils/models 导入边正确 ✔
3. 跨文件调用：main 调 utils 的函数 → 定位到 utils.py ✔
4. 仓库统计：文件数/函数数/类数 ✔
5. 测试全绿 → 提交 → 五副本同步

## 四、价值

单文件理解 → 仓库级理解：改一个函数能算出跨文件的调用面（影响分析升级到
跨文件——正是 codegraph 的 impact_analysis 价值，白箱零 LLM 实现）。
