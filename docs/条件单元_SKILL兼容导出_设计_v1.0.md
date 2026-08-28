# 条件单元 → Agent Skills 兼容导出设计（v1.0）

> 设计文档 · 2026-08-28 · 灵枢（AEIS）项目
> 决策（荣）：**标准对接，但把不适用条件直接放到条件中——即使兼容，也不放弃自己的要求。**
> 标准：Agent Skills（agentskills.io/specification）+ Agent Plugins 1.0.0（agent-plugins.org）
> 参照：scientific-agent-skills-ref（K-Dense，163 技能，2026-08-28 本地下载分析）

---

## 〇、设计原则

**兼容是形式（对外可消费），条件是要求（语义不妥协）。**

1. **标准字段用标准语义**：SKILL.md 的 name/description/compatibility/allowed-tools 用标准含义承载我们的对应维度
2. **自有要求结构化保留**：KCCS 四要素（生效条件/子功能/执行/不适用条件）+ 验证 + 条件路由信息——标准没有的字段放 `metadata` / `plugin.json.extensions`（标准允许自由扩展，Agent 会忽略但保留可读）
3. **不适用条件三通道**：检索面（description 显式「Not for」）+ 结构化（metadata.kccs.not_applicable）+ 人类可读（正文「克制条款」章节）——**一个要求，三条通道，永不丢失**

---

## 一、映射表（条件单元 → SKILL）

| 我们的条件单元（KCCS 四要素）| SKILL.md 承载 | 兼容性 |
|---|---|---|
| uid / task（单元名/任务）| `name` | ✅ 标准字段 |
| 条件词（触发/检索面）| `description`（显式触发词列表——借鉴 sci-agent 工程实践）| ✅ 标准字段 |
| 生效条件 | `compatibility`（环境/版本/前置）+ metadata.kccs.when | ✅ 标准字段 + 扩展 |
| 子功能（① ② ③ 分解）| metadata.kccs.sub（结构化）+ 正文小节 | 扩展（标准无）|
| 执行（机制/步骤）| metadata.kccs.execute + 正文「How to execute」| 扩展 + 正文 |
| **不适用条件（克制条款）** | ① description：「Not for X」触发词 ② metadata.kccs.not_applicable ③ 正文「克制条款」章节 | **三通道保留（核心要求）** |
| 验证（物理基底）| 正文「Verification」+ tests/ 目录 | 正文 + 目录（标准允许）|
| 校准（last-reviewed/access_count）| metadata.last-reviewed / calibration | 扩展 |
| 工具纪律（允许的工具）| `allowed-tools`（Read/Write/Edit/Bash——标准字段）| ✅ 标准字段 |
| 条件路由信息（domain/负路由/回退）| plugin.json.extensions.condition-route | 扩展 |

---

## 二、SKILL.md 模板（导出格式）

```markdown
---
name: <uid>                       # 条件单元名，如 compile-recursive
description: >-                   # 触发条件（检索面）——显式触发词列表 + 场景 + 代码导入触发
  <触发词1>/<触发词2>/<缩写>… 用户提到这些词时使用。
  场景：<在什么任务/问题下适用>。
  触发：代码导入 <module> / 引用 <API>。
  【不适用】Not for <X 场景>；not applicable when <Y 条件>。
license: MIT
compatibility: >-                # 生效条件（环境/版本/前置）
  <Python 版本>，<环境要求>，<前置依赖>。
allowed-tools: Read Write Edit Bash   # 工具白名单（工具纪律导出）
metadata:
  version: "1.0"
  skill-author: 灵枢（AEIS）
  last-reviewed: "<日期>"
  kccs:                            # 我们的四要素结构化保留（标准忽略，我们不放弃）
    when: <生效条件>
    sub:
      - <子功能①>
      - <子功能②>
    execute: <执行机制/步骤>
    not_applicable:                # ★ 不适用条件（核心要求）
      - <不适用场景①>
      - <克制条款②>
  calibration: <校准基准/对照>
---

# <单元名>

## When to use
<使用时机>

## 克制条款（不适用条件）
<人类可读的不适用条件/边界声明>

## How to execute
<执行步骤/子功能>

## Verification
<验证方式（物理基底：编译/运行/断言）>

## References
- <参考资料（借 sci-agent 的 references/ 目录实践）>
```

---

## 三、plugin.json 扩展（条件路由图对接）

```json
{
  "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
  "name": "lingshu-condition-units",
  "version": "0.1.0",
  "description": "灵枢条件单元库（Agent Skills 兼容导出）——白箱条件化知识",
  "extensions": {
    "lingshu": {
      "condition-route": {
        "domain": "<六域之一：compiler/pylang/graph/os/browser/net>",
        "unit-count": <n>,
        "kccs-version": "四要素规范版本",
        "negative-route": true,
        "condition-space": "<D(C) 声明：观测位置/工具/时间窗口/存在约束>"
      }
    }
  }
}
```

---

## 四、与 sci-agent 的差异（我们的要求不放弃）

| 维度 | sci-agent（K-Dense）| 我们（灵枢）|
|---|---|---|
| 不适用条件 | 实践存在（description 写「Not for…」）但**未结构化** | **三通道结构化保留**（description + metadata + 正文章节）|
| 条件空间 | 无 D(C) 声明 | 显式 condition-space（观测位置/工具/时间窗口/存在约束）|
| 验证 | tests/ 独立目录 | 验证内建（Verification 章节 + 物理基底）|
| 负路由 | 无 | 显式 negative-route + 回退路径 |
| 校准 | last-reviewed | last-reviewed + access_count + 校准基准 |

---

## 五、落地步骤

1. **导出器**：条件单元库 → SKILL.md + plugin.json 的生成脚本（读 KCCS 单元 → 模板渲染）
2. **示例导出**：compiler 域「编译-递归」→ SKILL 格式示例（验证模板）
3. **合规校验**：导出的 plugin.json 过 agent-plugins.org schema 校验；SKILL.md 过 agentskills.io 规范
4. **生态发布**：作为 Agent Plugins 包发布（GitHub 仓库 + 可选 registry）——对外可被任意 Agent 消费
5. **同步回写**：标准字段（触发词/兼容性）的改进回写 KCCS 规范（借鉴触发词列表工程化）

---

*本设计延续战略：兼容形式不弃要求（白箱纪律）；开源扩散（标准对接减少信息差）；条件路由图精确化（触发词/负路由显式化）。*
