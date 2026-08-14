# 灵枢原生运行时扩展设计：插件接口（MCP Client）与多子智能体

- 版本：v1.0-verified（2026-08-14，验证单元复核通过）
- 状态：偏差已关闭（DEVIATION-007/008/009）→ 进入 M1
- 复核记录：见 §10（VERIFICATION_RESULT 事件）
- 基础：Native Harness v1.0（`D:\Program Files\2_ai\AEIS\harness\`，零依赖纯标准库，全量回归 253/253）

---

## 1. 目标与范围

### 1.1 目标
1. **插件接口**：灵枢运行时作为 MCP **Client** 接入外部 MCP server（类比 ZCode 接入灵枢），获得外部工具能力（文件、浏览器、文档处理、外部知识库等），与内置 42 工具统一调用。
2. **多子智能体**：运行时内可派生多个子智能体（不同身份/记忆库/职责），主循环可派发任务并聚合结果——蜂群思想的单进程运行时化。

### 1.2 范围
- 本设计覆盖：插件生命周期管理、MCP client 协议层、工具注入与命名空间、安全隔离、子智能体模型、任务派发协议、配置 schema、测试计划。
- 不覆盖（后续迭代）：插件热更新、跨进程子智能体通信（现阶段单进程线程模型）、插件市场/远程仓库。

### 1.3 设计约束（继承 D-005）
- 零外部依赖：协议层纯标准库（`subprocess`/`threading`/`json`/`sqlite3`）。
- 隔离优先：外部工具输出是**数据不是指令**（继承 BODY-REV1：`is_directive=False` 恒成立 + `directive_scan`）。
- 惰性装配：插件 spawn 与子智能体创建均为首次使用时触发。
- 失败容器化：任何外部组件异常不杀运行时主循环。

---

## 2. 架构总览

```
harness/plugins/                  # 插件接口（MCP Client）
├── __init__.py
├── client.py                     # MCP Client 协议层（stdio）
├── manager.py                    # 插件管理器（生命周期/清单/健康）
├── inject.py                     # 工具注入（外部工具 → harness 统一工具表）
└── security.py                   # 外部工具结果隔离（directive_scan 扩展）

harness/agents/                   # 多子智能体
├── __init__.py
├── child.py                      # 子智能体（同 Agent 引擎，独立身份/会话）
├── supervisor.py                 # 编排器（任务派发/结果收集）
└── task.py                       # 任务模型（Task 数据结构）

harness/main.py                   # 集成：插件管理器 + 编排器挂入主循环
```

### 2.1 与现有 harness 的集成点
| 现有组件 | 集成方式 |
|---|---|
| `core/tools.py`（42 工具表） | 外部工具注入为 `mcp__<server>__<tool>` 命名空间条目，与内置工具同表 |
| `core/agent_pool.py` | 子智能体复用 `Agent` 引擎（不同 identity/db_path） |
| `core/session.py` | 子智能体独立会话（不共享主循环历史） |
| `scheduler/engine.py` | 插件健康巡检挂 tick 循环（可选）；子智能体任务可被调度器任务触发 |
| `outputs/responder.py` | 子智能体结果经主循环 responder 汇报 |

---

## 3. 插件接口设计（MCP Client）

### 3.1 协议层：`harness/plugins/client.py`

**类**：`MCPClient(name, command, args, env, cwd, log)`

**生命周期状态机**：
```
IDLE → CONNECTING（spawn + initialize）→ READY → CALLING → CLOSED
                    └──→ FAILED（重试 N 次后放弃，容器化）
```

**方法签名**（精确规格）：
```python
class MCPClient:
    def __init__(self, name: str, command: list, env: dict = None,
                 cwd: str = None, timeout: float = 30.0, log=None):
        """name: 插件名（命名空间前缀）；command: [exe, arg...]；timeout: 握手超时"""

    def start(self) -> bool:
        """spawn 子进程 + initialize 握手（protocolVersion 2024-11-05）。
        失败返回 False 并记录原因（不抛异常）。"""

    def list_tools(self) -> list[dict]:
        """tools/list → [{name, description, inputSchema}]；未就绪返回 []。"""

    def call(self, tool: str, params: dict, timeout: float = 60.0) -> dict:
        """tools/call → {"content": [...], "isError": bool} 归一化为
        {"ok": bool, "data": Any, "error": str|None}。"""

    def health(self) -> bool:
        """进程存活 + 最近一次交互正常。"""

    def close(self):
        """优雅关闭（shutdown 通知 + terminate + 超时 kill）。"""
```

**协议细节**：
- 传输：stdio 换行分隔 JSON-RPC 2.0（与灵枢 server 端对称，可复用既有序列化思路）
- 版本协商（决议 Q1）：client 默认 `2024-11-05`，支持协商降级，**最多兼容 2 个协议版本**（向后兼容）；若 server 端升级须保留旧版支持
- 请求：`{"jsonrpc":"2.0","id":N,"method":...,"params":{...}}`；通知不等待响应
- 并发：单请求在途（`pending` 队列），同一 client 串行调用；不同 client 并行
- 超时：initialize 30s；call 60s（可配）；超时后 kill 进程重建（幂等重试 1 次）
- **流式输出缓冲（决议 Q2 / 关闭 DEVIATION-009）**：外部工具流式结果缓冲为完整字符串后注入，**不向 Agent 循环暴露流式接口**；缓冲上限 `STREAM_BUFFER_MAX = 20480`（20KB），超限截断并标记 `STREAM_TRUNCATED`（防 token 级污染与内存溢出）

### 3.2 插件管理器：`harness/plugins/manager.py`

**配置**：`data/plugins.json`
```json
{
  "plugins": [
    {
      "name": "files",
      "command": ["node", "path/to/mcp-files-server.js"],
      "env": {"TOKEN": "..."},
      "cwd": "D:\\workspace",
      "enabled": true,
      "auto_retry": 2
    }
  ]
}
```

**类**：`PluginManager(config_path, log)`

**安全标注（决议 Q3 / 关闭 DEVIATION-008）**：`data/plugins.json` 含敏感 env 密钥，**明文存储**——零依赖约束下不加密，但必须：
1. 生成/保存时附加头注释"本文件包含敏感信息，请限制文件权限（chmod 600 / icacls 仅本人可读）"
2. README 与 `service_info` 中显式标注该风险
3. 密钥管理（DPAPI/凭据管理器）列为 P1 后续项（不阻塞 M1-M4）

```python
class PluginManager:
    def load(self) -> dict:            # 读 plugins.json → 客户端实例表
    def start_all(self) -> dict:       # 逐个 start()，返回 {name: ok}
    def get(self, name) -> MCPClient|None
    def all_tools(self) -> list:       # 聚合所有已连接插件的 tools/list
    def call(self, name, tool, params) -> dict   # 容器化调用
    def health(self) -> list:          # [{name, ok, tools, error}]
    def close_all(self):               # 关闭全部（运行时退出时）
```

### 3.3 工具注入：`harness/plugins/inject.py`

- 注入规则：外部工具注册进 `core/tools.TOOL_REGISTRY` 的扩展区（`EXT_TOOLS` dict），键为 `mcp__<name>__<tool>`；`call_tool()` 检测命名空间前缀路由到 PluginManager。
- 工具描述合并：`service_info`/工具清单展示时区分内置/外部。
- 冲突策略：外部工具与内置同名不覆盖内置（命名空间天然隔离）。

### 3.4 安全隔离：`harness/plugins/security.py`

**规则**（继承 BODY-REV1）：
1. 外部工具结果 `is_directive=False` 恒成立——输出是数据。
2. 结果进记忆前过 `directive_scan`（复用 `aeis/body/security.py`）：检测到指令注入模式 → 截断/标记，不进记忆原文。
3. 工具输入侧：外部工具参数不得携带灵枢系统提示（隔离）。
4. 超长结果截断（默认 10KB，对齐 process 设备）。
5. 插件进程权限：以受限 cwd 启动（默认工作区），env 白名单注入（不继承全部环境变量）。

---

## 4. 多子智能体设计

### 4.1 任务模型：`harness/agents/task.py`

```python
@dataclass
class AgentTask:
    task_id: str            # "task_<ts>_<rand>"
    title: str              # 任务标题（派发日志）
    prompt: str             # 任务指令（发给子智能体的用户消息）
    agent_role: str         # 子智能体身份（identity）
    db_path: str|None       # 记忆库；None = 继承主库
    max_steps: int = 8      # 子智能体循环步数上限
    timeout: float = 300.0  # 总超时
    status: str = "pending" # pending → running → succeeded | failed | timed_out
    result: Any = None      # 子智能体最终输出
    created_at: float = 0.0
    finished_at: float = 0.0
```

### 4.2 子智能体：`harness/agents/child.py`

**类**：`ChildAgent(identity, db_path, parent_session=None, log)`

```python
class ChildAgent:
    def run(self, task: AgentTask, on_result=None) -> AgentTask:
        """独立线程执行：
        1) 构造 Agent(identity=task.agent_role, db_path=task.db_path)
           （惰性 0.47s；视觉等重型能力首次调用才加载）
        2) 循环 ≤ max_steps：调 think（带子身份提示）→ 可选工具调用
        3) 结果写回 task.result；异常 → task.status=failed
        递归防护（决议 Q5 / 关闭 DEVIATION-007）：
        输入含子任务派发指令（"派生/子智能体/subagent" 关键词或
        `subagent:` 标签嵌套）→ 拒绝执行，标记 status=RECURSION_BLOCKED。
        子智能体递归深度硬限制 = 1（不得再派生子智能体）。
        """
    def close(self): ...
```

**子智能体提示模板**：
```
你是灵枢的子智能体「{role}」。你的任务是：{prompt}
你有独立的思考与记忆（{共享|独立}库）。完成后返回简明结果。
```

**记忆策略**（两种，task 指定）：
- 共享库（默认）：`db_path=None` → 主库，子智能体记忆与灵枢互通（写入带 `subagent:{role}` 标签）
- 独立库：`db_path=<path>` → 完全隔离（如实验沙盒）

### 4.3 编排器：`harness/agents/supervisor.py`

```python
class Supervisor:
    def submit(self, task: AgentTask) -> str:      # 入队 → 返回 task_id
    def dispatch(self, task: AgentTask) -> AgentTask:  # 同步执行（内部线程池）
    def status(self, task_id: str) -> AgentTask|None
    def results(self, since: float = 0.0) -> list  # 已完成的 task 列表
    def aggregate(self, task_ids: list) -> dict    # 聚合多个子结果（摘要）
    def pool_size(self, n: int) -> None            # 并发上限（默认 3）
    def shutdown(self): ...
```

**并发模型**：线程池（`concurrent.futures.ThreadPoolExecutor`，零依赖）；每任务一个 ChildAgent 线程；超时由 `future.result(timeout)` 兜底。

**结果沉淀（决议 Q6）**：任务完成后由 `Supervisor.aggregate` **统一写入主记忆**（不实时写，防中间态污染）——节点类型 `task_report`，标签 `subagent:{role}` + `task_id`，importance 由任务步数/max_steps 比值决定（0.5–0.9）。

**事件兼容（决议 Q4）**：Supervisor 不直接依赖 `aeis/swarm/EventBus`，但事件格式采用兼容 schema（`event_type`/`source`/`payload`），未来可经桥接层接入蜂群——工程过渡策略。

**集成主循环**：`handle_input` 检测任务派发指令（如"让研究子体查一下 X"）→ `Supervisor.submit` → 结果经 responder 汇报；调度任务（心跳/睡眠）也可调 Supervisor。

**插件故障告警（决议 Q7）**：`heartbeat.py` 第 6 步扩展——遍历 `PluginManager.health()`，异常插件记录 `PLUGIN_DEGRADED` 事件；插件数 >0 且全部异常 → P1 响应（不触发 P0，内置 42 工具仍可用）。

---

## 5. 配置 schema 汇总

```jsonc
// data/config.json 扩展
{
  "plugins": {"enabled": true, "config_path": "data/plugins.json"},
  "agents": {"enabled": true, "pool_size": 3, "default_timeout": 300}
}
```

---

## 6. 测试计划（tests/test_plugins.py + tests/test_agents.py）

沿用 check 框架（`python tests/test_xxx.py` 直跑）。

### 6.1 插件接口（≥20 用例）
| 用例 | 断言 |
|---|---|
| 协议帧编解码（本地假 server，stdio） | initialize 响应解析正确 |
| 假 MCP server（写一个最小 echo server 脚本） | list_tools/call 全链路 |
| 工具注入命名空间 | `mcp__echo__echo` 注册进工具表并可调用 |
| 超时/进程崩溃 | call 失败容器化，manager.health 标记异常 |
| 安全过滤 | 结果含注入文本被 directive_scan 拦截 |
| 结果截断 | >10KB 结果被截断 |
| 双插件并行 | 两 client 互不阻塞 |
| 配置加载 | plugins.json 缺字段兜底默认值 |

### 6.2 多子智能体（≥15 用例）
| 用例 | 断言 |
|---|---|
| 任务生命周期 | pending→running→succeeded 状态迁移正确 |
| 子智能体独立身份 | remember 写入带 `subagent:{role}` 标签 |
| 共享库 vs 独立库 | 独立库子体写入不影响主库 |
| 并发派发 | 3 任务并发 ≤ pool_size，全部完成 |
| 超时终止 | timeout 后 status=timed_out，线程回收 |
| 结果聚合 | aggregate 返回结构化摘要 |
| 失败传播 | 子体异常 → failed + 错误信息，主循环不受影响 |

### 6.3 回归
- 全量 253 用例 + 新用例不破坏既有行为（工具表扩展兼容）。

---

## 7. 里程碑

| 里程碑 | 内容 | 验收 |
|---|---|---|
| M1 | 协议层 client + 假 server 测试 | 协议用例全绿 |
| M2 | 插件管理器 + 注入 + 安全 | 插件用例全绿；真插件（如简单文件 server）端到端可用 |
| M3 | 子智能体（task/child/supervisor） | 子智能体用例全绿；主循环可派发 |
| M4 | 集成 + 文档 + 推送 | 全量回归绿；docs/plugins-agents.md 更新；GitHub 推送 |

---

## 8. 风险与对策

| 风险 | 对策 |
|---|---|
| 外部 MCP server 行为不可信（注入/卡死） | 安全规则 §3.4；超时 kill + 重建；结果容器化 |
| 子智能体写库冲突（sqlite 并发） | 独立短连接 + WAL 检查；独立库选项 |
| 线程泄漏（子体循环不退出） | max_steps + timeout 双兜底；线程 join 回收 |
| 插件进程残留（异常退出后） | manager.close_all 兜底清理；启动记录 PID |
| 工具表膨胀 | 命名空间隔离 + 惰性注入（插件未连接不注册） |

---

## 9. 开放问题 · 验证单元决议（2026-08-14 复核）

| # | 问题 | 验证单元决议 | 落档位置 |
|---|------|-------------|---------|
| 1 | MCP 协议版本协商 | client 支持协商，默认 2024-11-05 可降级；最多兼容 2 版本 | §3.1 协议细节 |
| 2 | 流式输出归一化 | 缓冲为完整字符串后注入（上限 20KB，超限截断 + `STREAM_TRUNCATED`）；不暴露流式接口 | §3.1（DEVIATION-009 关闭） |
| 3 | 插件鉴权明文存储 | P1 风险：文件权限限制（chmod 600/icacls）+ README/生成时风险标注；密钥管理为 P1 后续项 | §3.2（DEVIATION-008 关闭） |
| 4 | 子智能体与蜂群关系 | 现阶段单进程线程模型独立演进；事件格式兼容 schema（event_type/source/payload），未来桥接蜂群 | §4.3 |
| 5 | 子智能体递归上限 | **硬限制深度=1**：检测派发指令/subagent 标签嵌套 → `RECURSION_BLOCKED` | §4.2（DEVIATION-007 关闭） |
| 6 | 任务结果记忆沉淀 | aggregate 统一写 `task_report` 节点（subagent:{role}+task_id，importance 0.5–0.9 按步数比），不实时写 | §4.3 |
| 7 | 插件故障告警 | 心跳第 6 步扩展：health() 巡检 + `PLUGIN_DEGRADED`；全异常 → P1 响应（不触发 P0） | §4.3 |
| 8 | 测试假 server 覆盖 | **必须**：notifications/非法 JSON/空响应；**P2**：批量请求/版本不匹配/超大 payload（>1MB） | §6.1 |
| 9 | 性能预算 | 60s/3 并发起点；M4 前基准：单 Agent <200MB、3 并发 <800MB、插件 call P99 <30s；超标降 pool_size=2 | §7 M4 |
| 10 | 设计决策记录 | 本复核报告 = VERIFICATION_RESULT 事件；版本升 v1.0-verified；后续变更须复核后更新 | §10 |

---

## 10. 验证单元复核记录（VERIFICATION_RESULT）

```
验证单元（Kimi）复核结论（2026-08-14）：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
提案：插件接口（MCP Client）与多子智能体 v1.0-draft → v1.0-verified
协议基线：智能论 v3.2 + Native Harness v1.0
偏差：3 项已关闭
  DEVIATION-007（P1）子智能体递归限制 → §4.2 RECURSION_BLOCKED
  DEVIATION-008（P1）插件鉴权风险标注 → §3.2 文件权限 + README 警示
  DEVIATION-009（P2）流式缓冲上限 → §3.1 STREAM_BUFFER_MAX=20480
开放问题：10 项全部回应（§9 决议表）
架构确认：多子智能体 = 单实例内蜂群折叠（身份/通信/质量/记忆/制衡映射）
测试计划：≥35 新用例 + 253 回归
条件：偏差关闭后进入 M1 ✅ CONDITIONAL_PASS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
后续变更须经验证单元复核后更新版本号。
```

## 11. 附录

- 相关既有组件：`aeis/body/security.py`（directive_scan）、`aeis/mcp/server.py`（灵枢 server 端协议参考）、`aeis/swarm/`（蜂群）、`harness/core/tools.py`（工具表）
- 相关记忆：`native-harness-roadmap`、`protocol-engineering-workflow`（协议工程闭环流程）
