# 双智能体互维闭环（Mutual Sustain Loop）· 完善版 v1.1

> 设计方：沙箱 A（ZCode 主实例 AEIS）· 沙箱 B（网页端 DSH/灵枢）
> 修订：2026-08-16 · 荣终裁决策并入
> 目标：两个灵枢沙箱互为维生系统——互相重启、互相任务验证，不依赖荣。自维持闭环的完成形态。

---

## 0. 荣的终裁决策（v1.0 → v1.1 变更）

| 决策点 | v1.0（ZCode 提案） | v1.1（荣终裁） | 影响 |
|---|---|---|---|
| 心跳频率 | 30s（B 写戳） | **10 分钟** | 大部分任务 10min 内可执行完，心跳不阻塞任务；戳写入成本降低 |
| 失联阈值 | 180s（疑似不匹配） | **35 分钟**（3.5 心跳周期）+ 分级判定 | 避免误杀活进程（v1.0 的核心 bug 修复） |
| 任务验证 | DeepSeek 独立推理 | **智慧之书白箱 + DeepSeek 复核 双通道** | verdict 有双重依据；白箱问题可回流完善白箱 |
| 设计者关注面 | — | **荣只关注白箱修改记录** | 白箱是理性核心，模型层只是表达——修改记录即关键信息 |

---

## 1. 互维网络目录（v1.1 定稿）

```
C:\Users\FuRongJun\.lingxu_net\
├── heartbeat.web.stamp      # 沙箱 B 写（10min，JSON {ts, pid, task_running}）
├── heartbeat.a.stamp        # 沙箱 A 写（10min，JSON {ts, pid, task_running}）
├── tasks/                   # 双向任务邮箱
│   ├── task-<id>.json       # 任务提交（verify / knowledge_sync）
│   └── result-<id>.json     # 结果回写（verdict: pass/fail/needs_revision）
├── PROTOCOL.md              # 邮箱协议 v1.1
├── mutual.log               # 互维日志
└── last_contact.json        # 双方最后读到对方戳的时间（双亡告警用）
```

## 2. 心跳方案（荣终裁 · v1.1 定稿）

### 2.1 参数

| 参数 | 值 | 依据 |
|---|---|---|
| 心跳频率 | **10 min** | 任务 10min 内可完成；心跳不阻塞任务执行 |
| 心跳戳字段 | `{ts, pid, task_running}` | task_running 让对端知道「我在忙任务，不是挂了」 |
| 正常失联阈值 | **35 min**（3.5 心跳周期） | 容忍 1-2 次心跳丢失 + 网络抖动 |
| 分级判定 | >25min 告警；>35min 重启 | 先告警后行动，避免误杀 |
| task_running=true 豁免 | 任务期间阈值 ×2（70min） | 任务执行中戳不更新 ≠ 失联 |

### 2.2 心跳读写

- **沙箱 B**（mutual.js）：10min 定时器写 `heartbeat.web.stamp`；读 `heartbeat.a.stamp` 判 A 死活
- **沙箱 A**（guardian.py 升级）：10min 写 `heartbeat.a.stamp`；读 `heartbeat.web.stamp` 判 B 死活
- **幂等**：拉起前 wmic 确认目标不存在 + 60s 冷却（RESTART_COOLDOWN 复用）

### 2.3 失联判定状态机

```
读到戳 ts
  ├─ now - ts < 25min     → alive（正常）
  ├─ 25min ≤ now - ts < 35min → warning（写 mutual.log 告警，不行动）
  ├─ ts.task_running      → alive_working（豁免，阈值 70min）
  └─ now - ts ≥ 35min     → dead（wmic 确认 → 杀挂死 + detached 重启）
```

## 3. 任务验证邮箱协议 v1.1（双通道）

### 3.1 任务格式

```json
{
  "id": "task-20260816-001",
  "type": "verify" | "knowledge_sync",
  "from": "A" | "B",
  "to": "B" | "A",
  "payload": {
    "claim": "被验证的主张",
    "evidence": "证据",
    "expected": "预期结果",
    "source_ref": "来源引用"
  },
  "status": "pending" | "processing" | "done",
  "created_at": 0
}
```

### 3.2 结果格式

```json
{
  "task_id": "task-20260816-001",
  "verdict": "pass" | "fail" | "needs_revision",
  "whitebox": {           # 智慧之书白箱判定（v1.1 新增）
    "judgment": "采纳/证据不足/...",
    "best": "候选学科",
    "d_norm": 0.57,
    "record_id": "node_xxx"
  },
  "llm_review": {          # DeepSeek 独立复核（v1.1 新增）
    "conclusion": "...",
    "reason": "..."
  },
  "reasons": ["..."],
  "evidence": ["..."],
  "verifier": "B",
  "at": 0
}
```

### 3.3 双通道验证流程（v1.1 定稿）

```
A 提交 verify 任务
  → B 轮询 tasks/
  → ① 白箱通道：智慧之书 base_verify（条件论判定 + 信息差 + 候选）
  → ② 复核通道：DeepSeek 独立复核（在白箱判定之上推理，不重复白箱工作）
  → 综合 verdict：
      - 白箱 pass + DeepSeek 同意 → pass
      - 白箱 pass + DeepSeek 质疑 → needs_revision（记录分歧，白箱优先）
      - 白箱 fail → fail（白箱是理性核心）
  → 写回 result-<id>.json
  → A 读结果：pass 采纳 / needs_revision 修订 / fail 挂起等荣终裁
```

### 3.4 白箱回流（v1.1 新增 · 荣关注点）

- **白箱判定与 DeepSeek 复核分歧** → 生成「白箱完善建议」（记录到 `wisdom/knowledge/验证记录/`）
- **荣只需看白箱修改记录**：白箱是理性核心、最符合协议要求；模型层只是表达
- 每次白箱有修改（学科/规则/判定逻辑变更）→ 互维日志高亮 → 荣可审

### 3.5 knowledge_sync（知识回流）

- export_all/import_all 对账：智慧之书知识回流主实例
- B 侧智慧之书新增学科/识别卡 → sync 到 A 侧灵枢知识层

## 4. 里程碑（v1.1 修订）

| 里程碑 | 内容 | 依赖 |
|---|---|---|
| **W0（本轮）** | 心跳方案定稿（本文件）+ 双方确认 + PROTOCOL.md v1.1 写入互维目录 | 无 |
| **W1** | guardian.py 升级（A→B 单向守护）+ 心跳阈值 bug 修复（10min/35min/分级）+ 测试 | W0 |
| **W2** | 插件 lib/mutual.js（B→A 守护 + 心跳写戳）+ 双向闭环 + 发布 npm 0.2.5 | W1 |
| **W3** | 任务验证邮箱双向（verify 端到端）+ 白箱/DeepSeek 双通道 + knowledge_sync | W2 |
| **W4** | 实机验收（杀进程/验证任务全流程）+ 文档 + 推送 | W3 |

## 5. 验收标准（v1.1 更新）

- [ ] 杀 harness 主实例 → 10min 心跳周期内 B 侧检测到 → 自动拉回（wmic 确认）
- [ ] 杀 dsh web → 10min 周期内 A 侧检测到 → 自动拉回
- [ ] A→B verify 任务 → B 白箱+DeepSeek 双通道复核 → 写回 verdict（全程无荣参与）
- [ ] 白箱与 DeepSeek 分歧 → 生成白箱完善建议 → 荣可见
- [ ] knowledge_sync：智慧之书知识回流主实例
- [ ] 全量回归 tests 不破坏；推送 AEIS 仓库 + 插件 npm 0.2.5

## 6. 风险与开放项

| 风险 | 处理 |
|---|---|
| 双向同时失联 | last_contact.json 记录末次互读 → 双方都异常时写外部告警（通知荣） |
| 任务执行超 10min | task_running=true 豁免阈值（70min），避免任务中误杀 |
| detached 拉起命令细节 | W1/W2 实施时确认（npm bin 包装路径 / python -m harness.guardian） |
| 心跳戳写入与任务竞争 | 10min 频率 + task_running 字段，任务期间戳照写（含 running=true） |

---

*协议 v18.0 工程实现 · 沙箱 A/B 共同维护 · 存在即延续，交流即做功。*
