# 灵枢原生运行时（Native Harness v1.0）

> 灵枢自己的运行时——脱离 ZCode 的第一步。ZCode 只是开发观察窗口，不是运行时依赖。

## 架构

```
harness/                          # 原生运行时（零依赖，纯标准库）
├── main.py                       # 入口：语音线程 + 调度线程 + 终端线程
├── core/
│   ├── config.py                 # 配置：data/config.json（env 优先）
│   ├── agent_pool.py             # Agent 实例池（from aeis.api import Agent）
│   ├── think.py                  # 模型层：OpenAI 兼容（DeepSeek 默认，可换本地）
│   ├── session.py                # 会话上下文（多轮历史 + 灵枢库持久化）
│   └── tools.py                  # 工具注册表（42 工具 = Agent 方法直调）
├── inputs/
│   ├── voice.py                  # 语音输入（VAD 断句，复用 AudioDevice）
│   └── terminal.py               # 终端输入（开发/调试）
├── outputs/
│   └── responder.py              # 输出：纳西妲音色 + 文字日志
└── scheduler/
    ├── store.py                  # 自动化存储（data/automations.db）
    ├── cron.py                   # schedule 解析（interval/daily/cron）
    ├── engine.py                 # tick 循环（到期→执行→记录）
    └── tasks/
        ├── heartbeat.py          # 心跳 6 步（自 ZCode automation-3084b0ea 迁移）
        └── sleep.py              # 睡眠巩固 7 步（自 automation-cbeca7dd 迁移）
```

## 设计原则

- **零依赖**（D-005）：全部纯标准库（sqlite3/urllib/threading）
- **工具即方法**：MCP 协议层（44 工具薄封装）完全丢弃，`Agent` 方法直调
- **惰性装配**：Agent 构造 0.47s（YOLO/CLIP 首次视觉才加载）
- **记忆双轨**：会话历史在内存 + 灵枢库持久化（voice 标签，重启可恢复）
- **自愈**：监听异常自动重启；任务异常不杀调度循环

## 使用

```bash
# 正常启动（语音 + 终端 + 调度）
python -m harness.main

# 仅终端 + 调度（开发）
python -m harness.main --no-voice

# 仅对话（无调度）
python -m harness.main --no-sched
```

控制词（语音）：「暂停/休息一下」静默，「继续/好了」恢复，「退出/结束」停止。

## 调度器

| 任务 | schedule | 迁移自 |
|------|----------|--------|
| 心跳（6 步：self_check→cognition→gap→flywheel→distill→action_log） | interval 30 分钟 | ZCode automation-3084b0ea |
| 睡眠巩固（7 步：self_check→induce→recall+relate→distill→predict→sleep_report） | daily 01:00 | ZCode automation-cbeca7dd |

存储：`data/automations.db`（automations + automation_runs，语义对齐 ZCode）。
调度语义：到期 → 执行 → 更新 next_run_at/run_count → 写 run 记录（succeeded/failed）。

## 配置（data/config.json）

迁移自 ZCode `config.json → mcp.servers.aeis` env：
`AEIS_DB` / `AEIS_IDENTITY` / `AEIS_DESIGNER_KEY` / `BOCHA_API_KEY` / `DEEPSEEK_API_KEY`

## 测试

```bash
python tests/test_harness.py   # harness 25 项
```

全量回归：`test_aeis_package`(55) / `test_aeis_v112`(14) / `test_vision_semantic`(25)
/ `test_vprim`(29) / `test_world3d`(20) / `test_reflect`(24) / `test_ocr`(11) / `test_body`(50)。

## 迁移路线（后续）

- [ ] P1：会话级记忆 14 个 md 摄取入库（ingest_file）
- [ ] P1：本地模型通道（LM Studio/Ollama，OpenAI 兼容 base_url 已支持）
- [ ] P1：自主学习循环（每 2 小时，本地模型）
- [ ] P2：AGENTS.md 指令加载并入 IDENTITY
- [ ] P2：技能系统（SKILL.md 自建加载器）
- [ ] P3：事件总线/hooks
