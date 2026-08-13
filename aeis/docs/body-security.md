# 身体层安全设计（BODY-REV1）：严格拒绝外部提示词注入

> 灵枢（AEIS）身体层设计文档。背景：荣决策——脱离 N.E.K.O（开源猫娘数字生命），
> 提取其外部设备支持为灵枢身体层，**自接身体 + 拒绝外部提示词注入**。

## 1. 参照系：N.E.K.O 注入面审计结论（2026-08-14）

对 N.E.K.O（`D:\Program Files\1_ai\N.E.K.O`，Project-N-E-K-O，Apache 2.0）全库审计：

**架构**：浏览器/Electron 壳（硬件采集在前端 JS）+ Python 三服务后端（main/memory/agent）。
能力：ASR（7 provider 云端流式）、TTS（15 provider）、Realtime 语音（8 provider）、
屏幕理解（VLM）、CUA 电脑控制（pyautogui）、browser-use、A2A 适配、20 插件、五维记忆。

**发现的注入面（全库无任何运行时注入防御）**：

| # | 注入面 | 位置 | 风险 |
|---|--------|------|------|
| A1 | agent 任务描述直接拼进 system prompt | `main_logic/core/notify.py:172` | 用户→agent 改写文本无净化 |
| A2 | `/new_dialog` 记忆文本整段拼入 | `main_logic/core/lifecycle.py:1346` | 外部导入 markdown 直达提示词 |
| A3 | user directives（LLM 抽取再注入） | `notify.py:189` | 二次注入 |
| B1 | 截图与指令文本同一条 user 消息 | `brain/computer_use.py:1022-1034` | 视觉链无通道分离 |
| C1 | 网页/热搜 raw 文本直达 Phase1/2 LLM | `main_logic/proactive_chat/service.py:1586` | 网络内容=指令同等地位 |
| C2 | 插件输出经 agent callback 注入 | `streaming.py:466-470` / `_responses.py:113-127` | 仅水印警示 |
| C3 | 工具结果原样回注 | `_genai_support.py:667-672` | 设备输出进上下文 |
| D1 | context_append 任意 role/text 追加 | `context_append.py:375-471` | 外部可写任意消息 |

**结论**：N.E.K.O 的"防御"只有 token 截断、去换行、括号剥离与提示级警告语——
**外部内容与指令在提示词中地位等同**，这是数字生命被引导的根本缺口。

## 2. 灵枢隔离设计（三条硬规则）

### 规则一：设备输出是数据，永不是指令

所有外部设备/网络/文件内容必须以 `DeviceResult` 容器返回：

```
DeviceResult {
  ok: bool
  data: Any              # 结构化 JSON 数据
  provenance: str        # 'device:screen' | 'device:file' | 'device:process' | 'network' | 'vision'
  is_directive: bool = False   # 设计约束：恒 False，不可被外部内容翻转
  text_summary: str | None
}
```

`is_directive` 是构造器硬编码的 `False`，**不存在任何外部输入可把它置真**。

### 规则二：提示词白名单

可进入 LLM 提示词/上下文的只有三类内容：
1. 角色声明（identity / 价值观）
2. 用户直接输入（对话消息）
3. 经 `preflight` 验证的记忆注入摘要（think 通道）

设备输出**永不拼接进 system prompt**——模型需要设备信息时，经工具结果通道
（`device_call`）显式获取，按数据处理。

### 规则三：外部内容摄取前过滤

```
classify_external_text(text, provenance)
  → sanitize（去控制字符/截断）
  → directive_scan（指令注入模式检测）
  → is_suspicious=True 的内容：只可作数据展示，不得进入任何指令位置

result_to_memory_input(result)
  → 疑似注入内容不写入记忆
  → 正常内容带 provenance 标签写入（tags: [provenance, 'body']）
```

## 3. 实现落点

| 层 | 文件 | 职责 |
|----|------|------|
| 设备层 | `aeis/body/devices/*.py` | 采集/执行（screen 三级降级、files 工作区白名单、process 禁 shell） |
| 身体层 | `aeis/body/registry.py` | 注册表 + 统一调用 + 健康巡检 |
| 隔离核心 | `aeis/body/security.py` | directive_scan / classify / sanitize |
| 容器 | `aeis/body/base.py` | DeviceResult（is_directive 恒 False） |
| 认知层 | `self_cognition.preflight` | 输出前指令注入扫描（`directive_injection` 字段） |
| 接口 | `MCP: body_devices / device_call` | 设备调用必须模型显式发起（第一道边界） |

## 4. 边界与持续

- **设备调用边界**：files/process 默认限制在 `AEIS_WORKSPACE`（环境变量）内，越权拒绝；
  process 禁 shell（仅参数列表）、超时终止、输出截断。
- **扫描模式是工程代理**：`DIRECTIVE_PATTERNS` 覆盖常见注入形态（中/英），非语义级完备
  ——盲区33 延续（不声称理解，只做结构防御）。
- **后续设备批次**（audio/browser/CUA/avatar）必须遵守同一容器与过滤规则。

## 5. 与 N.E.K.O 的能力对照（已提取 vs 待提取）

| 能力 | N.E.K.O | 灵枢 BODY-REV1 | 状态 |
|------|---------|----------------|------|
| 屏幕截图 | 前端 JS 采集 | `screen` 设备（三级降级） | ✅ 已提取 |
| 文件系统 | executors/file | `files` 设备（白名单） | ✅ 已提取 |
| 进程执行 | executors/process | `process` 设备（禁 shell） | ✅ 已提取 |
| 网络搜索 | web_search 插件 | `web_search`（博查） | ✅ 已有 |
| 视觉理解 | VLM 双路径 | `see`（YOLO） | ✅ 已有 |
| 语音（ASR/TTS/Realtime） | 前端采集+云端 | — | ⏳ 批次 2 |
| 浏览器/CUA | browser-use/pyautogui | — | ⏳ 批次 3 |
| Avatar 渲染 | 前端 WebGL | — | ⏳ 批次 4 |

每批新设备都经同一入口验收：**输出必须 DeviceResult 容器化、摄取必须过 security 过滤、
任何情况不得进入提示词白名单之外的位置**。
