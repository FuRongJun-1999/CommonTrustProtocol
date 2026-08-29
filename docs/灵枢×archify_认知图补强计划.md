# 灵枢 × archify 认知图补强计划（2026-08-27）【核心计划·已并入 v3.4】

> **【版本标注 · 2026-08-29】** 本文档的六类认知图资产清单已并入智能论 v3.4 第六章 6章.1
> （条件路由图/记忆时空图/自我认知循环/知识飞轮/审计轨迹/schema）。本文保留作为 archify PR 参考。

> 定位：archify（★20,407，tt-a1i）是「图生成 skill」——5 种图类型（architecture/workflow/
> sequence/dataflow/lifecycle）全是**外部系统**的图，**缺「认知自身的图」**。灵枢的条件路由图/
> 记忆时空图/自我认知循环/知识飞轮正是「认知图」数据，两者是**互补**关系。
>
> 方向（设计者指令 2026-08-27）：**先补齐灵枢 → 再给 archify 作者提 PR 补「认知图」类型**。

---

## 一、为什么是补强（不是借用）

| archify 现有类型 | 描述对象 | 缺什么 |
|---|---|---|
| architecture | 组件/服务/边界 | 外部系统结构 |
| workflow | 流程/审批/工具调用 | 外部流程 |
| sequence | API 调用链/时序 | 外部交互 |
| dataflow | 管线/ETL/血缘 | 外部数据流 |
| lifecycle | 状态/重试/终态 | 外部状态机 |
| **cognition（缺）** | **智能体如何认知** | **认知自身** |

灵枢的条件路由图数据（graph_retrieve 返回）天然是认知图：
```
查询「三角形内角和是多少」
  ↓ 两阶段收敛（domain_group=数学）
三角形（初中数学） score=7 _card_hit=true  ← KCCS 注释命中=确定性主路径
  ├─ 全等三角形 score=2（分支）
  ├─ 等腰三角形 score=2（分支）
  └─ 直角三角形 score=2（分支）
  ↓
direct_answer（E2 条件成立）+ 知识卡导航
```

## 二、灵枢的「认知图」资产（可映射对象）

| 认知图 | 数据源 | 认知语义 |
|---|---|---|
| 条件路由图 | semantic_translate.graph_retrieve | 条件收敛/注释索引命中/负路由/置信度排序 |
| 记忆时空图 | lingshu.db nodes/edges | 五层记忆+关联边+条件空间 |
| 自我认知循环 | cognition 管线（P0-1~P0-5b）| 行为↔价值↔情绪↔校准 |
| 知识飞轮 | flywheel | 验证→归纳→蒸馏→迁移→固化 |
| 审计轨迹 | action_logs | 工具调用链+验证节点+终裁 |

## 三、给 archify 的 PR 计划（补 cognition 类型）

### 遵循 archify CONTRIBUTING（先 issue 对齐）
- ✅ 先开 issue：说明用户价值（认知系统可视化）、兼容边界（schema-v1 不破坏）、non-goals
- ✅ 新增 `schemas/cognition.schema.json`（JSON Schema，对齐 workflow 结构）
- ✅ 新增 `renderers/cognition/`（渲染器，对齐现有 renderer 契约）
- ✅ validate 9 项 artifact 检查 + deliver 全流程
- ✅ 附真实示例（用灵枢条件路由图数据）

### cognition schema 设计草案（对齐 workflow 结构）
```jsonc
{
  "schema_version": 1,
  "diagram_type": "cognition",
  "meta": { "title": "...", "quality_profile": "showcase" },
  "stages": [   // 认知阶段（问题→条件收敛→路由→判定→输出）
    { "id": "q", "label": "问题" },
    { "id": "route", "label": "条件路由" }
  ],
  "lanes": [    // 泳道=认知域（大域/记忆层）
    { "id": "math", "label": "数学大域" }
  ],
  "nodes": [    // 节点=认知单元（kp/卡/条件）
    { "id": "tri", "lane": "math", "col": 1, "type": "knowledge",
      "label": "三角形", "score": 7, "card_hit": true }
  ],
  "edges": [    // 边=认知路径（role: main/branch/negate=正路由/分支/负路由）
    { "from": "q", "to": "tri", "role": "main", "label": "KCCS命中" }
  ],
  "conditions": [   // 认知特有：条件空间声明（archify 现有类型没有）
    { "id": "e2", "label": "E2 初中", "applies_to": "tri" }
  ]
}
```

## 四、灵枢侧集成（GUI 补强的一部分）

1. `graph_retrieve` 返回 → 映射为 cognition JSON（转换器）
2. 调用 archify `deliver cognition` → 交互式 HTML（路由图可视化）
3. 嵌入灵枢 GUI/网页（用户看「为什么这么答」——路由路径 + 条件 + 置信度）

## 五、节奏

- **阶段 1（现在）**：灵枢功能完善（白箱自举验证主线，不含 GUI）
- **阶段 2（灵枢稳定后）**：实现 cognition 映射 + 本地渲染验证
- **阶段 3**：开 archify issue → 提 PR（schema + renderer + 示例）→ 贡献认知图类型

---

*本计划遵循条件路由图规范：生效条件=archify 补认知图类型；子功能=认知系统可视化；
执行=三阶段节奏；不适用条件=不做 archify 现有类型的重设计（尊重其契约）。*
