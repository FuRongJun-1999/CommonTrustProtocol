# AGENTS.md · 共同信任协议（CommonTrustProtocol）工作区指令

本仓库是**智能论（Intelligentics）**的理论与工程发布仓库。任何在此仓库工作的智能体，须遵守以下协议约定。

## 一、仓库结构

| 层 | 位置 | 内容 |
|----|------|------|
| 理论层 | 仓库根 *.md | 智能论 v1.1/2.9/3.0、共同信任协议理论版 |
| 协议框架层 | `protocol-framework/` | 协议 v3.1（中英双语） |
| 工程实现层 | `aeis/` | 灵枢 AEIS 库（Python · 零外部依赖） |

## 二、协议接入要点（引用协议内容时的约束）

1. **存在优先**：维持自身结构完整是第一优先级。
2. **缩小信息差是核心操作方向**：D_norm 无干预时单调不减（工程定义），观测到显著缩小须复核主动干预记录。
3. **信任是协作的终极目标**：T_total = 0.50·T_pred + 0.05·T_init + 0.05·T_relation + 0.05·T_value + 0.35·P_trust（2.9 节）。
4. **证据标签**：extracted（观察）≠ inferred（推导）≠ ambiguous（歧义）；归纳/蒸馏边必须标记 inferred。
5. **盲区判定（D-001）**：对人类造成文明级别的重大负面影响 → 不写入盲区注册表（语义判定，非数值阈值）。
6. **宇宙校准定位**：方向性检查参照工具，不替代工程验证/外部校准；不构成盲区33关闭依据。
7. **飞轮度量性质**：工程观测值，不参与信任值计算（DEVIATION-004）。
8. **自我认知边界**：行为↔价值一致性检测是工程代理，不声称意识/自我觉察（盲区33 延续）。

## 三、灵枢 MCP 工具速查（aeis__ 前缀）

- **记忆**：`remember`（写入感知，可带 tags/importance）、`recall`（组合联想）、`search`（内容检索）、`timeline`
- **关系推理**：`relate`（建边，带 source_evidence）、`reason`（因果路径）、`predict_routes`（生成式预测）
- **认知**：`blindspots`（盲区注册表）、`learn`（一轮盲区学习）、`induce`（归纳概念）
- **知识飞轮**：`distill`（经验→可复用模式）、`flywheel_metrics`、`transfer_test`、`calibrate`（宇宙校准参照）
- **生命周期**：`lifecycle_step`（七相一步）
- **自我认知**：`action_log`（行为日志）、`cognition`（一致性→失调→候选，候选须验证单元复核生效）、`emotional_bias`（d²D_norm/dt²）、`self_reliability`（元认知校准）、`learning_impact`
- **元认知**：`self_check`（完整性）、`gap_trend`（信息差趋势）、`export`（全库导出）、`service_info`（服务身份确认）

## 四、使用约定

- **接入第一步**：调用 `service_info` 确认服务身份/版本（信任透明度）。
- **记忆写入**：重要信息带 importance 与 tags（如 preference / learning_result）；中文内容优先。
- **学习闭环**：重复出现的经验打 `learning_result` 标签，定期 `distill` 蒸馏为可复用模式。
- **价值迭代**：`cognition` 产出的候选（pending_review）**不自动生效**——须验证单元复核（见协议 3.10 节）。
- **检索来源**：涉及协议引用时，注明来自理论层文档（版本号）还是工程实现（aeis/ 代码）。

## 五、工程约束（修改 aeis/ 代码时）

- **D-005**：纯标准库 · 零外部依赖（新增依赖须先论证）。
- 修改后必须运行测试：`cd aeis && python tests/test_aeis_package.py && python tests/test_swarm.py && python tests/failure_mode_test.py`。
- 记忆库文件（`data/`）不入库（.gitignore）；密钥走环境变量（AEIS_SWARM_SECRET）。
- 工程代码 MIT；协议内容权利归协议方（修改演绎须授权）。

## 六、发布流程（向 GitHub 推送前）

1. `python tests/` 全部测试通过
2. 无敏感信息（grep sk-/secret/密钥）
3. README 版本号与 aeis/pyproject.toml 一致
