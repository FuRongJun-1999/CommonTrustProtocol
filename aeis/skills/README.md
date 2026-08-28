# lingshu-skills · 灵枢自我认知技能包

> 灵枢（AEIS · Agent Engineering Implementation Specification）· CommonTrustProtocol 主仓库内部
> **本质：灵枢了解自身的工具**——不是独立仓库，是灵枢项目的一部分。
> 用灵枢自己构建的条件单元，描述灵枢自己如何认知（白箱自举的对外投影）。

---

## 这是什么

一个 **Agent Plugins 1.0.0 兼容包**（agent-plugins.org），内含 **688 个 Agent Skills（六域条件单元）**：

| 域 | 单元数 | 内容 |
|---|---|---|
| compiler | 116 | 中文编译器（词法/语法/编译/VM/调试/分析）|
| pylang | 122 | Python 语言机制（表达式/函数/类/闭包）|
| graph | 117 | 图算法与图数据库 |
| os | 112 | 操作系统（进程/调度/文件系统）|
| browser | 104 | 浏览器与网页 |
| net | 117 | 网络（协议/传输/安全）|
| **合计** | **688** | 白箱六域条件单元 |

每个技能描述灵枢在**什么条件下**能做什么、**怎么执行**、**克制什么**——比标准 Agent Skills 多出
**KCCS 四要素（生效条件/子功能/执行/不适用条件）** 与**不适用条件三通道**（description「Not for」+
metadata.kccs.not_applicable + 正文克制条款章节）。

## 三层关系（知识 → 说明书 → 执行）

```
知识真源（CTP 主仓库）          aeis/wisdom/*_code_units.py（KCCS 四要素，真源）
        ↓ 导出（tools/skill_export.py + skill_export_verify.py 门禁）
说明书（本包）                  aeis/skills/ —— Agent Skills：何时用/怎么用/克制什么
        ↓ 执行
MCP（灵枢 77 工具）             aeis-mcp（MCP stdio）· dsh-memory 插件——物理基底裁决
```

| 层 | 是什么 | 作用 |
|---|---|---|
| 知识真源 | 条件单元库（681 单元）| 知道什么、条件是什么 |
| **本技能包**（说明书）| SKILL.md 技能 | 告诉 agent 何时用、怎么用、克制什么（认知自身）|
| MCP（执行）| 灵枢 77 工具 | 提供实际能力执行（编译/运行/断言 = 物理基底）|

**技能包的 Verification 由灵枢 MCP 工具执行**——技能说「怎么验证」，MCP 负责「真去跑」。

## 为什么是「自我认知」

- 每个技能描述的是**灵枢自己的能力**（如「编译-递归」= 灵枢编译器如何编译递归函数）
- 整包 = 灵枢把自己「会做什么、在什么条件下做、克制什么」显式写成说明书
- 与「认知自身的图」（archify 认知图补强）同思想：图 = 视觉化自我认知，技能包 = 文本化自我认知
- **白箱自举的对外形态**：灵枢用自己构建的条件单元描述自己

## 结构

```
aeis/skills/
├── plugin.json          # Agent Plugins manifest（含 extensions.lingshu：self-cognition/condition-route/mcp）
├── skills/<slug>/       # 116 个技能
│   └── SKILL.md         # frontmatter（name/description/compatibility/allowed-tools/metadata.kccs）+ 正文
└── README.md            # 本文件
```

## 使用

1. **作为 Agent Plugins 包**：任意符合 agentskills.io/agent-plugins.org 规范的 agent 可加载本包
2. **配合灵枢 MCP**：技能的 Verification（物理基底）由灵枢 MCP 工具执行（aeis-mcp）
3. **再生成**：改知识源（单元库）后运行 `tools/skill_export.py --out aeis/skills` 重新导出，
   `tools/skill_export_verify.py` 作为发布门禁（验证全绿才允许提交）

## 验证状态（发布门禁）

- ✅ 688/688 单元通过格式 + 三通道校验（六域）
- ✅ not_applicable / when / execute / 正文克制条款 全部 688/688
- ✅ plugin.json 符合 agent-plugins.org schema（含 extensions 扩展：self-cognition/condition-route/mcp）

## 与主仓库纪律

- 真源 = `aeis/wisdom/*_code_units.py`（R1 主仓库唯一真源）
- 本包 = 生成投影（R3 运行时产物不入库——但本包是发布物，随主仓库版本化）
- 变更须重新导出 + 验证门禁通过（R6 变更验证）

---

*灵枢自我认知技能包 · 白箱条件化知识 · KCCS 四要素不放弃 · MCP 物理基底执行*
