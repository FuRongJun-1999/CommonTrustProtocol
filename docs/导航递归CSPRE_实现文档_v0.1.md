# 导航递归（CSPRE 条件空间导航）实现文档 v0.1【历史版本】

> **【版本标注 · 2026-08-29】** 本文档的 CSPRE（搜索=导航）核心与智能论 v3.4 第七章一致；
> graph_retrieve 四路融合实现细节为历史版本。最新权威：《智能论3.4.md》第七章 7.3（CSPRE）+ 第六章 6章.2（条件路由）。

> 状态：**待实现**（⏳ 设计已确认，代码未落地）
> 设计来源：
> - 《三步递归分形·任意分层性与深度边界》（2026-08-20，荣深化判断）
> - 《回答必须走条件路由图·设计原则》（2026-08-26）
> - 条件路由表理论：智能 = ①发现问题条件 → ②**递归匹配子条件** → ③当前条件下精准执行
> 实施方：zcode

---

## 一、问题定义（做什么）

### 1.1 现状缺口

灵枢检索当前是**两层递归**（已实现）：
```
第一层：graph_retrieve 定位学科卡（四路融合 → top 卡）
第二层：卡内 content 条目匹配 direct_answer（卡⊃kp 单层归属）
```

**缺的是「导航递归」**（设计文档明确 ⏳ 待实现）：
```
问题Q → 条件空间A → 规则R1 命中
     → R1 是子问题入口 → 子条件空间A' → 规则R2...
     直到叶节点（原子知识）→ 答案
```

**一句话**：现有递归是「沿卡链/卡内容走」，缺的是「**进入知识内部的条件路由再导航**」——即「知识描述知识 = 条件路由图的子递归」。

### 1.2 目标

实现 `navigate_retrieve()`：在 `graph_retrieve` 命中的知识节点上，判断是否「复合知识」（含子条件路由），若是则递归进入子路由，直到叶节点或深度上限。返回**完整导航链**（每层的条件空间/规则/置信度）。

---

## 二、理论依据（必须遵守）

### 2.1 三步递归分形（《三步递归分形》文档）

> 「三步不是线性序列，而是递归嵌套：每次找到的规则可能开启子条件空间，循环在子空间中重来」

### 2.2 递归深度边界（智能论 3.3 / core.py 硬约束）

```
递归深度 ≤ 3（3.12 运行约束，超出 = 结构性盲区）
默认 3 层；复杂场景可申请临时扩展至 5 层（验证单元门控）
```

**复用现有机制**（core.py L2718/L2734）：
```python
def navigate_retrieve(question, dex, depth=0, max_depth=3, chain=None):
    if depth >= max_depth:
        return {"status": "structural_blindspot", ...}  # 复用 core.py 模式
```

### 2.3 智能的第二个过程（条件路由表）

> ②递归匹配子条件——找到条件对应的规则和知识，是递归过程
> 精准执行 = 路由正确 ∧ 规则适用 ∧ 执行结果通过验证（三闸门）

---

## 三、设计

### 3.1 知识节点分类（新增判定）

每个知识节点增加子路由判定（写入 state_attributes）：

```python
# 节点状态属性扩展
state_attributes = {
    "name": "婆媳相处",
    "kind": "knowledge_point",
    "knowledge_type": "composite",   # ← 新增：composite（复合，含子路由）| atomic（原子）
    "sub_route": "conditions:婆媳相处",  # ← 新增：子路由入口条件空间（复合节点才有）
    # 原子节点：无 sub_route，直接 content 即答案
}
```

- **原子知识**（叶）：`content` 直接是答案（如「三角形内角和=180度」）
- **复合知识**（含子图）：`sub_route` 指向子条件空间——命中它后，需进入子路由再导航

### 3.2 导航递归算法（navigate_retrieve）

```python
def navigate_retrieve(question, dex, depth=0, max_depth=3, chain=None):
    """
    条件空间导航递归：graph_retrieve 命中 → 判复合/原子 → 递归进入子路由。
    返回：导航链（每层条件空间/规则/置信度）+ 最终答案。
    """
    chain = chain or []

    # 0. 深度上限（复用 core.py 约束：≤3，超出=structural_blindspot）
    if depth >= max_depth:
        return {"status": "structural_blindspot",
                "note": f"递归深度已达上限 {max_depth}（3.12 约束）",
                "chain": chain}

    # 1. 第一层：graph_retrieve 定位（现有机制）
    hits = graph_retrieve(dex, question, limit=5)
    if not hits:
        return {"status": "no_route", "chain": chain,
                "reason": "条件路由图无命中（诚实边界：未覆盖）"}

    top = hits[0]
    entry = {
        "depth": depth,
        "condition_space": top.get("domain_group") or top.get("domain"),
        "rule": top.get("name"),
        "confidence": top.get("score"),
        "node_id": top.get("id"),
    }
    chain.append(entry)

    # 2. 判复合/原子
    node = load_node(top.get("id"))  # 从 dex 读节点 state_attributes
    if node.state_attributes.get("knowledge_type") == "composite":
        # 复合知识：进入子条件空间递归（子路由入口=该节点的条件）
        sub_question = refine_question(question, node)  # 条件收窄（见 3.3）
        return navigate_retrieve(sub_question, dex, depth+1, max_depth, chain)

    # 3. 原子知识：返回答案
    return {
        "status": "resolved",
        "chain": chain,
        "answer": node.content,          # 原子知识直接内容
        "direct_answer": top.get("direct_answer"),
        "navigation": "→".join(c["rule"] for c in chain),
        "depth_used": len(chain),
    }
```

### 3.3 子问题条件收窄（refine_question）

复合知识进入子路由时，用父节点条件空间收窄子问题（防子路由重新发散）：

```python
def refine_question(question, parent_node):
    """用父节点条件空间收窄子问题：
    父「婆媳相处」→ 子路由按「婆媳 相处 情境」等条件空间索引，
    而非重走全图。"""
    cond = parent_node.state_attributes.get("sub_route", "")
    # 简单实现：问题 + 父条件空间词（触发子路由索引）
    return f"{question} {cond}"  # 具体实现见 3.4 索引
```

### 3.4 子路由索引（复用 KCCS 注释索引）

**不新建索引体系**——复用现有 KCCS 四要素注释索引：

```
子路由 = 以「sub_route 条件空间词」为生效条件的一组 kp/卡
- 复合节点的 sub_route 词 → 子空间内 KCCS 注释命中（现有 card_route 机制）
- 子空间内同判定：再命中复合 → 再递归（depth+1）
- 命中原子 → 返回
```

### 3.5 返回结构（导航链可审计）

```python
{
  "status": "resolved",           # resolved | structural_blindspot | no_route
  "navigation": "问题→婆媳相处→沟通策略→倾听共情",  # 可读导航链
  "chain": [                      # 结构化导航链（每层可审计）
    {"depth": 0, "condition_space": "家庭关系", "rule": "婆媳相处",
     "confidence": 7, "node_id": "..."},
    {"depth": 1, "condition_space": "沟通情境", "rule": "倾听共情",
     "confidence": 5, "node_id": "..."},
  ],
  "answer": "...最终原子知识...",
  "direct_answer": "...",
  "depth_used": 2,
  "fingerprint": "sha256(导航链canonical)",   # 对接指纹化（zcode 已实现）
}
```

---

## 四、实现清单（按序）

### 4.1 数据层：knowledge_type + sub_route 字段
- [ ] `nodes.state_attributes` 支持 `knowledge_type`（composite/atomic，缺省 atomic）
- [ ] 支持 `sub_route`（复合节点的子路由条件空间词）
- [ ] 迁移脚本：现有 2846 kp 默认 atomic（`knowledge_type: "atomic"`），手工标注首批复合节点

### 4.2 检索层：navigate_retrieve 主函数
- [ ] 实现 `navigate_retrieve()`（3.2 算法）
- [ ] 实现 `refine_question()`（3.3 条件收窄）
- [ ] 深度上限复用 core.py 约束（≤3，超出 structural_blindspot）
- [ ] 子路由复用 KCCS 注释索引（card_route，不新建）

### 4.3 集成层：接入现有检索链路
- [ ] `graph_retrieve` 命中复合节点时 → 调用 `navigate_retrieve` 续导航
- [ ] `chat_engine` 回答组装：导航链作为「为什么这么答」证据（对接 archify 认知图可视化）
- [ ] 返回 `navigation` + `chain` + `fingerprint`

### 4.4 测试（对齐白箱纪律：先失败回归）
- [ ] 单元测试：复合→原子 2 层导航（如「婆媳相处」→「沟通策略」→「倾听共情」）
- [ ] 深度测试：3 层命中 resolved / 3 层未命中 structural_blindspot（复用 test_reflect.py 模式）
- [ ] 原子节点直答不递归（回归：三角形内角和仍 = 180度）
- [ ] 全量回归：域管线 + 基准测试（不破坏现有 98.1% 对话命中率）

### 4.5 示例（首批复合节点，建议 3-5 个）
| 复合节点 | 子路由 | 子路由叶 |
|---|---|---|
| 婆媳相处 | 沟通情境 | 倾听共情 / 边界设定 |
| 理财亏损 | 风险场景 | 风险承受 / 分散投资 |
| 育儿冲突 | 冲突类型 | 隔代观念差 / 教育方式分歧 |

---

## 五、验证标准（完成定义）

1. **功能**：`navigate_retrieve("婆媳矛盾怎么处理")` 返回 2 层导航链 + 原子答案（如「先倾听共情，再边界设定」）
2. **深度边界**：3 层内 resolved；超限 structural_blindspot（对齐 core.py）
3. **回归**：现有 graph_retrieve / chat_engine 行为不变（原子节点不递归）
4. **可审计**：返回 navigation 链（每层条件空间/规则/置信度）+ fingerprint
5. **可视化对接**：导航链可喂给 archify（cognition 图类型）渲染

---

## 六、边界（诚实声明）

- 导航递归验证「路由路径确定性」，**不改变知识正确性**（知识质量是另一范畴）
- 复合节点标注是**增量手工**（首批 3-5 个），不自动推断——防止误标污染路由
- 深度 3 层是保护（防无限迷宫），不是缺陷——超限触发结构性盲区 → 盲区飞轮接管（补知识/改入口）

---

*本实现文档遵循条件路由图规范：生效条件=检索命中复合知识节点；子功能=递归导航至原子知识；
执行=4.x 实现清单；不适用条件=原子节点不递归（直答）、深度超限转盲区。*
