# 灵枢 × 酒馆接入指南（协议扩散 v0.1）

> **机制是灵枢的，载体是酒馆的。** 灵枢提供角色扮演机制层（自我锚点 /
> 特化价值观 / 历史记忆），酒馆生态通过导入接口构建角色——协议扩散。
> 文档编号：CTP-DIFFUSION-TAVERN-002 · 2026-08-19

---

## 一、三件套清单

| 文件 | 用途 |
|------|------|
| `灵枢_协议引导者.png`（或 .json） | 协议角色卡（chara_card_v3，PNG 内嵌 JSON，可导入酒馆） |
| `协议扩散知识包_扮演论.json` | 世界书知识包（7 条目触发词驱动条件注入） |
| `tavern_bridge.py` | 灵枢酒馆桥（OpenAI 兼容代理 + 角色扮演机制注入） |

配套工具（`tools/`）：
- `make_role_card.py` — 从灵枢引擎角色生成角色卡（JSON/PNG）
- `validate_card.py` — 角色卡规范校验器（chara_card_v3）
- `roleplay_server.py`（aeis 模块）— 角色扮演引擎 REST 服务（三导入接口）

---

## 二、快速开始

### 方式 A：纯角色卡（无需本地服务，协议结构随卡传播）

1. 导入 `灵枢_协议引导者.png` 到酒馆（角色管理 → 导入）
2. 可选：导入 `协议扩散知识包_扮演论.json` 到世界书
3. 开聊——角色卡内已含条件空间声明 / 自我锚点 / 诚实边界 / 扮演崩溃恢复
   （描述、system_prompt、post_history_instructions 字段）

### 方式 B：完整机制（接灵枢引擎，深度注入）

**1. 启动角色扮演引擎（三导入接口）：**
```bash
python -m aeis.roleplay_server --port 8792 --data-dir roleplay_data
```

**2. 创建角色并导入三件套（记忆/锚点/价值观）：**
```bash
# 创建角色
curl -X POST http://127.0.0.1:8792/roles \
  -H "Content-Type: application/json" \
  -d '{"role_id":"protocol-guide","name":"灵枢 · 协议引导者",
       "scenario":"与用户的对话即观测流，你只持有观测"}'

# 自我锚点导入（→ SELF/ANCHOR 层，no_forget 保护）
curl -X POST http://127.0.0.1:8792/roles/protocol-guide/anchor \
  -H "Content-Type: application/json" \
  -d '{"items":[{"content":"扮演可以演任何角色，但演不了编译通过","immutable":true}]}'

# 特化价值观导入（→ STRUCTURE 层，带适用条件）
curl -X POST http://127.0.0.1:8792/roles/protocol-guide/values \
  -H "Content-Type: application/json" \
  -d '{"items":[{"name":"诚实边界","condition":"涉及物理事实/能力边界时"}]}'

# 历史记忆导入（→ KNOWLEDGE 层，时空记忆图）
curl -X POST http://127.0.0.1:8792/roles/protocol-guide/memory \
  -H "Content-Type: application/json" \
  -d '{"items":[{"content":"白箱六维测试 18/18","tags":["测试"]}]}'
```

**3. 启动酒馆桥（酒馆自定义 API 指向它）：**
```bash
python tools/tavern_bridge.py --port 8791 \
  --data-dir roleplay_data \
  --upstream-base https://api.deepseek.com/v1 \
  --upstream-model deepseek-chat \
  --upstream-key-var DEEPSEEK_API_KEY
```

**4. 酒馆配置：**
- API 类型：自定义（OpenAI 兼容）
- 端点：`http://127.0.0.1:8791/v1`
- 模型：任意（桥会转发到上游真实模型）
- 请求体附加：`"lingshu": {"role_id": "protocol-guide"}`（或请求头 `X-Lingshu-Role: protocol-guide`）
- 不指定角色时默认使用第一个角色

---

## 三、机制说明（注入了什么）

酒馆桥在转发前注入（每轮刷新，可消融 `LINGSHU_OFF_<ID>=1`）：

| 注入块 | 内容 | 来源 |
|--------|------|------|
| 角色条件空间 | 观测位置/观测工具/存在约束 | 角色导入数据 |
| 自我锚点 | 扮演宣言（不可遗忘，任何情况下不得丢失） | SELF/ANCHOR 层 |
| 无条件价值观 | 始终有效的基线价值观 | STRUCTURE 层 |
| 条件价值观 | 触发条件出现时注入（条件空间即触发时机） | STRUCTURE 层带 cond 标签 |
| rp_honest | 诚实边界：物理事实不扮演 | 真实论校准 |
| rp_cond | 条件空间识别：先判定再扮演 | 条件论 |
| rp_values | 价值观条件注入纪律 | 注入极性定律 |
| rp_crash | 扮演崩溃恢复：锚点回读/条件切换 | 扮演崩溃定义 |

---

## 四、协议扩散语义

- **角色卡 = 条件空间声明**：用户导入即接触协议结构（条件空间/锚点/价值观）
- **诚实边界 = 协议试金石**：「扮演可以演任何角色，但演不了编译通过」——
  用户在对话中反复体验到这条边界，即协议结构的行为传播
- **creator_notes / extensions.lingshu**：指向灵枢导入接口与协议文档，
  深度用户可升级到方式 B（完整机制）
- 角色卡为扩散载体，**不构成协议条款效力**（防身份固化/认知污染，
  关联盲区 51/79/71，遵循 ENG-DEPLOY-PASSIVE-DIFFUSION 被动扩散）

---

## 五、验证状态

| 项 | 结果 |
|----|------|
| 角色卡规范校验（JSON/PNG） | ✅ PASS（必填 6/6，推荐 8/8） |
| 桥注入完整性（mock 上游回显） | ✅ 9/9 PASS（935 字符注入块） |
| 真实端到端（DeepSeek） | ✅ 诚实边界生效（「能扮演神吗」→ 拒绝扮演物理事实） |
| 真实酒馆部署 | ⏳ 待网络可用后实测（环境当前 GitHub/npm 不可达） |
