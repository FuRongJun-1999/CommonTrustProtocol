# Windows 文件系统操作方式变更 · 设计分析 v0.1（2026-09-03 荣征询）

> 背景：模型写 bash 优于 PowerShell（训练语料分布使然，fauxnix 分析已确认现象真实）。
> 灵枢环境默认 Windows——agent 用文本命令操作文件系统，必然撞 shell 方言墙。
> 荣方向：**对文件系统的操作方式变更**（而非命令翻译层），征询方案。荣提议之一：直接调用 VS Code。

---

## 一、问题本质重新定义

「bash 优于 PowerShell」是表象。**根因是「让模型用文本命令 + 解析文本输出」操作文件系统这个模式本身**：
- 文本命令依赖 shell 方言（bash/PowerShell/cmd 三套语法）
- 输出是人类可读格式，模型还要二次解析
- 错误恢复昂贵（fauxnix 金句：失败模式不是答错，是恢复太贵）

**变更方向：把文件操作从「文本命令」变成「结构化调用」**——模型不再关心 shell 方言，就像它不关心我们 MCP 工具底层是 SQLite 还是内存。

---

## 二、四个候选方案

### 方案 A：结构化文件工具组（业界验证的正解）★ 主推

Agent 不写命令，直接调用结构化工具：`read_file / write_file / edit_file / list_dir / glob_search / grep_content`

- **依据**：Claude Code / Cursor 全是这么做的——它们在 Windows 上文件操作基本不碰 shell。模型写结构化调用（JSON 参数）没有任何方言问题
- 与灵枢 MCP 工具协议**同构**（就是加一组工具），Python pathlib/os 实现天然跨平台
- edit_file 用「精确旧串→新串替换」模式，对模型最友好（无需行号）
- **安全边界**：`AEIS_WORKSPACE_ROOT` 沙箱限定根目录，防逃逸
- 成本：一组新 MCP 工具（约 6 个）+ KCCS 条件补齐

### 方案 B：Python 执行层（灵枢特色增强）

复杂文件操作（批量重命名/正则替换/跨目录整理）由 agent 生成 **Python pathlib 代码**，经已有 `compile_exec` 物理基底执行。

- 依据：模型写 Python 的熟练度同样远超 PowerShell（Python 语料也海量）；灵枢已有中文协议编译器+compile_exec 基建，复用而非新建
- 定位：方案 A 的补充层——A 覆盖 90% 常规操作，B 覆盖长尾复杂操作
- 与「白箱智能」叙事同构：文件操作也走协议化表达

### 方案 C：VS Code 集成（荣提议）—— 可选增值，不作核心依赖

VS Code 的正确用法不是 `code` CLI 改文件，而是**写一个 VS Code 扩展暴露 `vscode.workspace.fs` API**（跨平台文件抽象 + diff 编辑视图）：

- 优点：天然跨平台、UTF-8 正确、编辑有 diff 预览人工确认（安全增值）
- 缺点：要求用户装 VS Code + 扩展 + 常驻——重量级依赖，把灵枢能力绑在 VS Code 存在上
- **定位建议**：可选集成（有 VS Code 的用户体验增值：编辑确认 diff 视图），非核心路径。核心能力不应依赖它

### 方案 D：fauxnix 式命令翻译 —— 已分析，不推荐为主路径

第三方供应链风险 + 只解决「命令方言」不解决「文本命令模式」本身。

---

## 三、推荐组合：A（主）+ B（增强）+ C（可选集成）

| 层 | 覆盖 | 依赖 |
|---|---|---|
| A 结构化文件工具 | 90% 常规操作（读/写/改/列/搜） | 零（pathlib） |
| B Python 执行层 | 复杂批量操作 | compile_exec（已有） |
| C VS Code 扩展 | diff 确认等体验增值 | 用户装 VS Code |

**工具数量说明**（呼应荣「工具不应该越多」原则）：A 组 6 工具不是「越多越多余」——它们替代的是模型本来就要写的 N 条 shell 命令，是把隐式能力显式化、方言化能力结构化；且 C 明确不加。

---

## 四、待荣拍板

1. 方案 A 是否立项（6 工具：read_file/write_file/edit_file/list_dir/glob_search/grep_content，沙箱限定）
2. 方案 B 是否随行（compile_exec 复用）
3. 方案 C 是否留作后续可选集成
