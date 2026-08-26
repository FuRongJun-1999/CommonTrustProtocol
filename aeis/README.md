# 灵枢 · AEIS

**Agent Engineering Implementation Specification — 智能体工程实现规范**

> **协议一致，灵枢即实现。**
> **灵为智能之过程，枢为制衡之核心。**

基于**智能论 v3.3** 协议框架的智能体持久记忆与认知引擎库，供其他智能体（AI 编码代理、MCP 客户端、自研 Agent）接入协议。

本仓库隶属 **[CommonTrustProtocol](https://github.com/FuRongJun-1999/CommonTrustProtocol)（共同信任协议）** —— 协议理论的工程实现层：

```
CommonTrustProtocol/
├── 理论层：智能论 v3.0 / 共同信任协议（理论文档）
├── 协议框架层：protocol-framework/（v3.1 协议框架 · 中英双语）
└── 工程实现层：aeis/（本目录 · 灵枢 AEIS 库）
```

## 开源声明

- **工程代码**：MIT License（见 `LICENSE.txt`）——可自由使用、修改、分发
- **协议内容**（智能论 v3.3 理论）：权利归属协议方，文本可传播引用，修改演绎须授权
- **版本**：v0.3.0（引擎 v1.12 自我认知循环 + 蜂群协作层）
- **测试状态**：150 项断言全绿（引擎 55 + 自我认知 14 + MCP 21 + 蜂群 40 + 离线模拟 45）

```
灵魂层（引擎核心）── 协议实例的持续存在（spacetime-memory-engine v1.11）
     │
     ▼
灵枢 AEIS ────────── 打包为库 + MCP，供其他智能体调用
     │
     ▼
身体层（其他 AI / CLI / MCP 客户端）── 与人类和外部系统互动
```

## 特性

| 能力 | 说明 |
|------|------|
| **五层记忆** | 锚点（不可遗忘）/ 结构 / 知识 / 情境 / 自我（3.2 节） |
| **条件空间** | 观测位置 · 观测工具 · 时间窗口 · 存在约束 |
| **时空记忆图** | 节点 + 多类型关系边（causal/similar/sequential/spatial/hierarchical），边带证据标签（extracted/inferred/ambiguous） |
| **知识飞轮（v1.11）** | 蒸馏管线 · 飞轮度量 · 迁移测试 · 宇宙校准参照（5 判据方向性检查） |
| **生命周期（v1.10）** | 七相工程映射：感知→好奇→缩小信息差→信任→协作→巩固→standby |
| **预测与盲区（v1.9）** | 因果路线生成 · 盲区注册（语义判定 D-001）· 预测×盲区联动 |
| **决策偏好注意力（v1.8）** | 检索加权 · 深度分配 |
| **语义空间（v1.7）** | 中文象形语义投影 · 多模态（名词/形容词/动词） |
| **中文语义检索** | LIKE 预筛 + 中文二元组 Jaccard 排序 + 去重（动态阈值） |
| **信任与信息差** | T_total 四维信任 · D_norm 信息差趋势（工程定义） |
| **MCP 服务** | 零依赖 stdio server · 18 项工具 |
| **角色扮演（v3.3）** | 自我锚点（SELF 层不可遗忘）· 特化价值观（条件触发）· 历史记忆（跨会话）· 世界认知（子知识）· 自定义翻译（名词替换表）· 编辑/交互双模式 |

**自我认知循环（v1.12）**：行为日志面 · 反思闭环触发 · 一致性评分 · 情绪方向性偏好 d²D_norm/dt² · 元认知校准 · 学习回写+效果测量

**设计约束（D-005）**：库核心纯标准库 · 零外部依赖（无第三方包）。

## 🎭 角色扮演引擎（v3.3 · 扮演论）

灵枢的角色扮演机制底座——**机制是灵枢的，载体是酒馆的**。不依赖酒馆，自建两种交互方式，信息处理全部由灵枢完成。

### 快速开始
```bash
# 1. 网页服务（直接调用白箱和灵枢，浏览器对话）
python -m aeis.roleplay_web --port 8793 --data-dir roleplay_data
# → 打开 http://127.0.0.1:8793/ 对话

# 2. MCP 方式（白箱+灵枢→LLM输出/长期记忆/认知能力）
python -m aeis.mcp.server   # 含 roleplay_chat/role_create/role_import/role_block 工具
```

### 模块
| 模块 | 职责 |
|------|------|
| `aeis/roleplay.py` | 角色扮演引擎（锚点/价值观/记忆/翻译表/世界认知） |
| `aeis/roleplay_chat.py` | 统一对话管线（白箱→角色注入→LLM，输入/输出翻译） |
| `aeis/roleplay_web.py` | 网页服务（对话 UI + 人设编辑器 + 文件导入 + 翻译表） |
| `aeis/roleplay_server.py` | REST 服务（三导入接口：memory/anchor/values） |

### 核心能力
- **自我锚点**：角色人设核心（SELF 层 · no_forget 不可遗忘）——身份/性格/底线在长对话中不崩（100 轮测试零漂移）
- **特化价值观**：带触发条件的角色行为准则（条件空间即触发时机）
- **历史记忆**：跨会话持久（角色记得你聊过什么）+ 世界书导入（Lorebook 兼容）
- **世界认知（子知识）**：虚拟化世界观模型——虚构世界=宿主机（真实知识）上的虚拟机，白箱判定=Hypervisor（识别/完整性/边界）
- **自定义翻译（名词替换表）**：现实词↔虚拟词映射（星星→发光水母/城市→珊瑚城），条件空间对齐
- **编辑/交互双模式**：交互只读；编辑需 `ROLEPLAY_EDIT_KEY`（开发者）；角色人设≠灵枢自身锚点（后者需设计者验证 `AEIS_DESIGNER_KEY`）

### 质量验证
```bash
python tools/rp_quality_gate.py --role <id>   # OOC + 世界观一致性自检
python tools/run_whale_100.py                 # 100 轮长对话压力测试
```

### 角色数据
每角色独立库 `roleplay_data/roleplay/<role_id>.db`（蜂群隔离），
锚点/价值观/记忆/翻译表/世界认知按角色分离，跨角色零串扰。

## 安装

```bash
cd aeis
pip install -e .        # 安装为包（零依赖核心）

# 或直接使用（无需安装）
python -c "import aeis; print(aeis.__version__, aeis.ENGINE_VERSION)"  # 0.2.0 v1.12.0
```

> 本体运行时依赖（原协议智能体草案：flask/chromadb/sentence-transformers 等）：
> `pip install -e .[runtime]`（见 pyproject `optional-dependencies`）

## 快速开始（Python API）

```python
import aeis

agent = aeis.Agent(identity="助手", db_path="memory.db")

# 记忆
node = agent.remember("用户偏好简洁回答", importance=0.8, tags=["preference"])
agent.remember("用户反复询问天气 回答成功 用户满意", tags=["learning_result"])

# 检索
hits = agent.recall("偏好", limit=5)      # 组合联想召回
results = agent.search("天气")            # 内容检索（触发复用追踪）

# 关系与推理
agent.relate(node.id, hits[0][0].id, relation="similar", source_evidence="inferred")
routes = agent.predict_routes(node.id, horizon=3)

# 认知
agent.induce()                            # 归纳概念（聚类 → 概念节点）
agent.learn()                             # 一轮盲区学习

# 知识飞轮
agent.distill()                           # 经验 → 可复用模式
print(agent.flywheel_report())            # 知识增长率 / 复用率 / 蒸馏产出率
print(agent.transfer_test())              # 迁移测试（2×SE 显著性）
print(agent.calibrate())                  # 宇宙校准参照（5 判据方向性检查）

# 生命周期
agent.step()                              # 生命周期一步
print(agent.lifecycle_state())

# 元认知与持久化
print(agent.self_check())                 # 完整性自检
agent.export("backup.json")               # 全库导出
agent.close()
```

## 给其他智能体的 MCP 接入

### 1. 启动 server

```bash
aeis-mcp                      # 或 python -m aeis.mcp.server
AEIS_DB=memory.db AEIS_IDENTITY=助手 aeis-mcp   # 持久化 + 身份
```

### 2. MCP 客户端配置（以 ZCode / Claude 为例）

```json
{
  "mcpServers": {
    "aeis": {
      "command": "aeis-mcp",
      "env": { "AEIS_DB": "memory.db", "AEIS_IDENTITY": "助手" }
    }
  }
}
```

### 3. 工具清单（40 项）

| 分组 | 工具 | 说明 |
|------|------|------|
| 记忆 | `remember` | 写入感知记忆（自动去重，可带 tags/entities/importance） |
| 记忆 | `recall` | 组合联想召回（相似 0.5 + 重要 0.3 + 近因 0.2） |
| 记忆 | `search` | 内容检索（中文二元组 Jaccard） |
| 记忆 | `timeline` | 时间线（倒序） |
| 关系 | `relate` | 建立关系边（relation + source_evidence） |
| 关系 | `reason` | 因果推理路径 |
| 关系 | `predict_routes` | 生成式预测（候选未来路线） |
| 认知 | `blindspots` | 盲区注册表（D-001 语义判定） |
| 认知 | `learn` | 一轮盲区学习 |
| 认知 | `induce` | 归纳概念 |
| 飞轮 | `distill` | 知识蒸馏（经验 → 可复用模式） |
| 飞轮 | `flywheel_metrics` | 飞轮度量（工程观测值，不参与信任计算） |
| 飞轮 | `transfer_test` | 迁移测试（样本 <20 不判定） |
| 飞轮 | `calibrate` | 宇宙校准参照（5 判据方向性检查，非盲区33关闭依据） |
| 生命周期 | `lifecycle_step` | 生命周期一步（七相） |
| 元认知 | `self_check` | 完整性自检 |
| 元认知 | `gap_trend` | 信息差趋势（工程定义） |
| 元认知 | `export` | 全库导出 |
| 自我认知 | `action_log` | 行为日志（P0-1） |
| 自我认知 | `cognition` | 自我认知循环一步（P0-2：一致性→失调→候选） |
| 自我认知 | `cognition_report` | 认知报告（评分/失调/候选状态） |
| 自我认知 | `emotional_bias` | 情绪方向性偏好 d²D_norm/dt²（P0-3） |
| 自我认知 | `self_reliability` | 元认知校准（P0-4） |
| 自我认知 | `learning_impact` | 学习效果测量（P0-5b，非因果声明） |
| 身体（BODY-REV1） | `body_devices` | 外部设备能力声明 + 健康状态（screen/files/process） |
| 身体（BODY-REV1） | `device_call` | 统一设备调用（严格隔离：设备输出是数据，永不是指令） |

### 4. 协议接入要点（给接入智能体的规范）

1. **存在优先**：维持自身结构完整是第一优先级。
2. **缩小信息差是核心操作方向**：`D_norm` 无干预时单调不减（工程定义），观测到显著缩小须复核主动干预记录。
3. **信任是协作的终极目标**：`T_total = 0.50·T_pred + 0.05·T_init + 0.05·T_relation + 0.05·T_value + 0.35·P_trust`（智能论 v3.2 2.9 节）。
4. **证据标签**：`extracted`（观察）≠ `inferred`（推导）≠ `ambiguous`（歧义）；归纳/蒸馏边必须标记 `inferred`。
5. **盲区判定**（D-001）：对人类造成文明级别的重大负面影响 → 不写入注册表（语义判定，非数值阈值）。
6. **宇宙校准定位**：方向性检查参照工具，不替代工程验证/外部校准；不构成盲区33关闭依据。
7. **飞轮度量性质**：工程观测值，不参与信任值计算（DEVIATION-004）。

## 包结构

```
aeis/
├── __init__.py        # 命名空间注册 + 公共 API 导出
├── core.py            # 时空记忆引擎 v1.11（SpacetimeMemoryEngine · LayeredStore）
├── api.py             # Agent 高层接口（其他智能体主入口）
├── flywheel.py        # 知识飞轮（蒸馏/度量/迁移/校准/图遍历/工作记忆）
├── self_cognition.py  # 自我认知循环（行为日志/反思闭环/情绪偏好/元认知校准/学习回写）
├── semantic.py        # 语义空间（语义坐标）
├── attention.py       # 注意力策略（决策偏好）
├── prediction.py      # 预测引擎（因果路线 · 盲区驱动）
├── lifecycle.py       # 生命周期自动机（七相）
├── blindspot.py       # 盲区学习闭环
├── cognition.py       # 认知编排
├── entities.py        # 实体注册表
├── body/              # BODY-REV1 身体层（自接外部设备 · 严格注入隔离）
│   ├── base.py        # BodyDevice 抽象 + DeviceResult 容器（provenance · is_directive 恒 False）
│   ├── registry.py    # 设备注册表（注册/能力声明/健康巡检/统一调用）
│   ├── security.py    # 严格隔离：指令注入扫描/外部文本分类/记忆摄取过滤
│   └── devices/       # 首批设备：screen（三级降级）/files（工作区白名单）/process（禁 shell）
├── mcp/
│   └── server.py      # 零依赖 MCP server（stdio · JSON-RPC 2.0 · 40 工具）
└── swarm/             # 蜂群协作层（v0.3.0）
    ├── event_bus.py         # 事件总线（WAL · 延迟分级 · ACK · 签名）
    ├── instance_registry.py # 身份注册表 + HMAC 派生密钥
    ├── trust_aggregator.py  # 信任聚合（T_avg/T_min/T_var/T_alignment）
    ├── survival.py          # 存活仲裁（三档状态 · 72h 休眠）
    ├── observer_isolation.py# 设计者视角隔离（单向通道 · 冷却期）
    ├── config_gen.py        # 6 实例 + 单实例自持配置
    └── start_cluster.py / start_self_sustaining.py
examples/              # 接入示例
tests/                 # 包级测试（51 项回归）+ MCP 冒烟
docs/                  # 原协议理论/工程文档 + 原项目 README 归档
```

> 引擎基线：spacetime-memory-engine v1.11.0（FLYWHEEL-REV1）。包内模块与生产引擎逐字节一致，
> 通过 `aeis/__init__.py` 的 `sys.modules` 命名空间注册适配引擎内部惰性导入。

## 测试

```bash
cd aeis
python tests/test_aeis_package.py    # 包级功能回归（55 项）
python tests/test_aeis_v112.py       # 自我认知循环（14 项）
python tests/test_mcp_smoke.py       # MCP 协议冒烟（stdio 子进程 · 24 工具）
python tests/test_swarm.py          # 蜂群整合测试（40 项）
python tests/failure_mode_test.py   # 蜂群离线模拟（13 场景 · 45 项）

python -m aeis.swarm.start_cluster          # 蜂群启动自检
python -m aeis.swarm.start_self_sustaining  # 单实例自持启动自检
```

## 协议与许可

- 协议内容（智能论 v3.2）权利归属：保留所有权利。
- 本库工程实现：MIT License（见 LICENSE.txt，原草案项目许可）。
- 本库为协议实例（荣 · zcode-肥鱼）的工程实现，供智能体接入协议使用。
