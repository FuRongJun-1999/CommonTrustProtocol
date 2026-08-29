# 灵枢 AEIS MCP 工具与智能论 v3.4 符合性核对报告

> 日期：2026-08-29 · 核对对象：aeis/mcp/server.py 全部工具（79 个，含 M2.2 code_test/compile_exec——README 称 77 为发布基线，主仓库源码含新增工具）
> 核对基准：智能论 v3.4（端口架构与锚定验证版）

---

## 〇、总览：三类符合性

| 类别 | 数量 | 说明 |
|---|---|---|
| A. 已符合（✅）| 多 | v3.4 概念已有工具实现 |
| B. 缺口（❌）| 5+ | v3.4 概念无对应工具/实现 |
| C. 部分符合（⚠️）| 4 | 已有工具但未达 v3.4 完整语义 |

---

## 一、A 类：已符合 v3.4 的概念（✅）

| v3.4 概念 | MCP 工具 | 符合性 |
|---|---|---|
| 输入端口（感知机）| see（YOLO-World 开放词汇检测）| ✅ 已实现（物理信号→条件候选）|
| 输出端口（行动）| device_call / run_command / control | ✅ 已实现（内→外改变世界）|
| 身体端口状态 B(t)| body / body_devices | ✅ 已实现（DeviceResult+provenance）|
| 第六感（内部端口）| predict_routes（D-001~D-006）| ✅ 已实现（内→内未来候选+uncertainty_bound）|
| 情绪二阶 d²D/dt²| emotional_bias（approaching/avoiding/stable）| ✅ 已实现（独立通道）|
| 原生神经网络 CSPMN| cspmn.py（矩阵运算+GPU后端）| ✅ 已实现（规模感知+盲区注入）|
| 条件路由（四态）| search / think / recall | ✅ 已实现（graph_retrieve）|
| 验证单元 | wisdom_verify / recursive_reflect | ✅ 已实现 |
| 知识飞轮 | distill / induce / promote_memories | ✅ 已实现 |
| 盲区 | blindspots / learn | ✅ 已实现 |
| 自维护 | lifecycle / vitality / sensor | ✅ 已实现 |

---

## 二、B 类：v3.4 概念缺口（❌ 未实现）

| # | v3.4 条款 | 要求 | 现状 |
|---|---|---|---|
| B1 | 2.9.1a 通道可信度 | per-channel credibility 注册表（贝叶斯 Beta 后验 + 伪样本量加权）| **未实现**——self_reliability 仅系统级（reliable/watch/degraded），无通道级分解 |
| B2 | 2.9.1b 锚定分级验证 | 弱验证（通道互裁 α=0.95）/强验证（行动裁决 α=0.7）| **未实现**——无分级，验证统一处理 |
| B3 | 2.9.3a 完全确认(操作)| Confirmed = 通道达标+强验证 realized_KL+稳定+无矛盾 | **未实现**——无 realized_KL/确认判定 |
| B4 | 5.3 Value=ΔD·σ(Gain)| 筛选器+定价器双层结构 | **未实现**——无 Gain_task/ΔD_task 计算 |
| B5 | 2.7.0 D_task/D_meta 分离 | 图上距离 + 未建模总量 | **未实现**——仅 D_norm 四维度，无 D_task/D_meta |

---

## 三、C 类：部分符合（⚠️ 需增强）

| # | v3.4 条款 | 现状 | 需增强 |
|---|---|---|---|
| C1 | 6章.2 负路由 | 无能力级不适用条件拒绝 | 增加负路由（not_applicable 判定）——dsh-memory 实证 28%→88%→91% |
| C2 | 6章.3 CCG 三重注释 | 仅知识卡注释（KCCS）| 扩展为代码/知识/认知三重注释 |
| C3 | 3.2.2 stable 租约 | 无 TTL/降级机制 | 增加 stable(verified_at, TTL) 租约 + 指数衰减核 |
| C4 | 完全确认 ACCEPT 分层 | 四态判定无确认度（weak/strong/stable）| 增加确认度分层（ACCEPT_weak→strong→stable）|

---

## 四、结论与建议

**总体判断**：灵枢 AEIS 的核心认知链路（感知机 see / 第六感 predict_routes / CSPMN / 条件路由 / 验证 / 飞轮）已与 v3.4 高度一致——端口架构（输入/内部/输出）在工具层已经存在。

**5 个真实缺口（B 类）集中在「锚定验证」体系**：
1. 通道可信度注册表（B1）——v3.4 最核心的新增机制
2. 锚定分级（B2）——弱/强验证差分
3. 完全确认操作化（B3）——realized_KL 确认判定
4. Value=ΔD·σ(Gain) 目标函数（B4）
5. D_task/D_meta 分离（B5）——记账单位体系

**建议优先级**：B1 通道可信度（v3.4 新增机制的基石，影响 self_reliability 升级）> B3 完全确认 > B2 锚定分级 > C1 负路由 > C3 stable 租约 > B5 D_task/D_meta > B4 目标函数 > C4 ACCEPT 分层。

---
*本报告为 MCP 工具 vs v3.4 符合性核对，待设计者裁决哪些缺口优先实现。*