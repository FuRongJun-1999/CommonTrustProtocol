# GPT 审查·白箱纯度核查报告（理论—代码映射）

> 状态：核查完成（2026-08-23）· 基于 GPT 提供的 5 个审查方向对灵枢源码实际核查
> 原则：严格区分「代码实际存在的问题」与「未来可优化点」——不把偏好冒充理论要求
> 核查对象：CTP/aeis（AEIS 灵枢）：prediction.py / flywheel.py / semantic.py / core.py

## 一、理论—代码映射表

| 理论概念 | 当前实现（实际代码） | 核查结论 | 修改/建议 |
|---|---|---|---|
| **条件论**（路由由条件决定，非相似度猜测） | `predict_routes`：从起点沿**因果/时序边** DFS 生成路径（`_branch_candidates` 因果边直通优先）；每条路径标注**条件空间序列**（`_cs_label`：边/节点 existence_constraint）；语义邻近候选须过 **D-002 伪因果过滤门**（有因果链/结构模式/偏好权重才入，标记 `semantic_induced`） | ✔ 条件驱动为主——路径由图结构（因果边+条件空间）决定，相似度候选被过滤门约束 | **已改**：`semantic_induced` 弱门偏好权重 0.5→0.8（减少弱候选）；建议（未做）：`semantic_induced` 候选仅保留有显式因果链的 |
| **盲区**（归属失败≠检索失败） | ① 模态盲区（semantic.py：image/audio/video/tactile **结构性不可处理**）② `recursive_reflect` 深度≥3 → `structural_blindspot`（3.12 运行约束）③ 操作盲区带 `predictability` 分级（predictable/unknowable/pending_assessment，D-003）；`predict_routes` 盲区无锚点返回 `no_anchor`（与盲区区分） | ✔ 结构性归属失败——模态盲区/递归深度盲区/可预测性分级均非「检索不到」 | 无（符合理论） |
| **预测误差→结构变化**（误差发现遗漏条件，非只调权重） | 未命中：`update_prediction_feedback` → **被拒路径登记**（rejected_paths 表，带原因/条件）→ `causal_discover.py` 聚类分析 → 条件/因果发现（条件论对自身：被拒路径→候选→验证闭环）；命中：因果边置信 +0.05；D-006 动态阈值（命中率<mean-2σ 触发反思） | ✔ 闭环存在——错误确实改变认知图结构（被拒路径是结构，且被因果发现消费） | 建议（未做）：被拒路径**自动**条件化（误差直接触发条件空间更新，当前半自动：由飞轮/蒸馏驱动触发） |
| **自迭代可逆可验证**（防认知自激振荡：原始证据→推导→新结构→验证） | `evo_distill_cycle` 模式节点内嵌**证据 trace**（「N 条经验压缩（代表：…）｜证据: …」）+ `dsv:<标准版本>` 标签 + 模式→成员 SIMILAR 边（inferred）→ 可沿证据回滚 | ✔ 证据链可回滚——模式节点自带证据摘要，原始记录可达 | **已补**：flywheel.distill_cycle（另一蒸馏路径）同样内嵌证据 trace（一致性） |
| **知识 vs 条件**（图结构区分条件节点/理论节点/推理规则） | 条件空间（ConditionSpace：observation_position/tool/time_window/existence_constraint）是**节点/边的属性**（内嵌），非独立条件节点；`hierarchical` 边表达知识归属层级（卡⊃知识点） | △ 条件未节点化——符合「每个知识带条件」但未显式化为条件节点 | 建议（对接方向）：条件节点化——白箱自举 `compose_engine` 的条件化单元 `{条件链→规律片段}` 已示范格式，可引入主库（条件节点→适用关系→知识节点） |

## 二、本轮已实施的修改（2 项 + 验证）

1. **flywheel.py distill_cycle**：模式节点 content 内嵌「证据:」摘要（可回滚性——与 evo_distill_cycle 一致）
2. **prediction.py `_branch_candidates`**：semantic_induced 弱门偏好权重 0.5→0.8（白箱纯度：减少非因果弱候选）

**验证**（tests/test_whitebox_purity.py，5/5 通过）：
- ① 蒸馏模式节点内嵌证据 trace ✔
- ② predict_routes 因果主路径不受门槛影响（2 路线）+ 条件空间序列 ✔
- ③ 盲区接口（结构性盲区机制）✔
- ④ 预测未命中 → 被拒路径登记（0→1，误差进入结构）✔
- 回归：test_reflect 23/24（count=73 为既有失败，stash 验证非本次修改引入）

## 二b、GPT 优先级实施（第一/第三优先级，2026-08-23）

**第一优先级：预测误差 → 自动条件化**（`update_prediction_feedback` v1.16 + `_auto_conditionize`）
- 未命中 → 除登记被拒路径外，**自动比较预测/实际节点条件空间 → 发现缺失条件（存在约束/观测位置）→ 写入条件候选节点**（tags: condition_candidate/auto_conditionized）
- 闭环补完整：`错误 → 缺失条件 → 条件候选节点 →（可验证/可继承）`——不再等待飞轮触发
- 验证：构造带「气压低」存在约束的实际节点 → 未命中反馈 → 自动生成 2 个条件候选（气压低 + 高原观测位）✔

**第三优先级：候选路径可信度分层**（`_branch_candidates` v1.16，不砍探索——GPT 明确建议）
- causal（显式因果边）→ 高可信主路径（边置信度）
- structural_causal / structural_pattern（结构推断）→ 中可信探索路径（0.6）
- semantic_induced（注意力偏好）→ 低可信假设路径（0.3）
- 验证：causal 主路径保留 ✔（探索路径保留但认知地位分层）

**白箱纯度核查更新：7/7 通过**（①蒸馏trace ②主路径 ②b条件序列 ③盲区 ④误差→被拒路径 ⑤自动条件化 ⑥分层）

## 三、遗留建议（未做，需设计决策）

1. ~~**semantic_induced 候选仅保留显式因果链**~~ → **已按 GPT 建议改为可信度分层**（不砍探索：因果事实/结构推断/探索假设分层，见二b）
2. ~~**被拒路径自动条件化**~~ → **已实施**（`_auto_conditionize`：错误→缺失条件→条件候选节点，见二b）
3. **条件节点化入主库**（GPT 第二优先级）：把 compose_engine 的条件化单元格式引入语义时空图（条件节点→适用关系→知识节点）——最大工程，对接白箱自举第三阶段
4. **推导过程显式记录**（GPT 第四优先级·克制）：保留可验证认知结构变化的证据链，不做全量过程记录（30MB 白箱结构效率原则）
