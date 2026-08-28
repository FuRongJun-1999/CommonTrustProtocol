# T12 · dsh 端（B 节点）接入指南 v0.1（2026-08-29）

> 目标读者：dsh 网页端灵枢（或任何想加入蜂群的节点）的实现者。
> 承诺：**按本文实现 ≤60 行 Python 即可接入蜂群协议栈**，
> 无需 import 任何主仓库代码。合规性由 test_swarm_dsh_guide.py 验证。

## 一、你将扮演什么

蜂群中你 = **B 节点**（服务提供方）。A 节点（ZCode 侧灵枢）会向你：
1. HELLO（交换能力表）
2. CAP_QUERY（问你有没有某能力）
3. TASK（协商 ACCEPT 后派活给你）
4. VERDICT（A 用它的验证基底裁决你的产出）

你需要实现：收件箱轮询 + 三种响应。

## 二、传输层契约（目录总线）

- 总线根目录：联调时双方约定的本地路径（如 `D:\swarm_bus\`）
- **你的收件箱**：`<root>/<你的节点id>/inbox/`——每条消息一个
  `<msg_id>.json` 文件；**读后即删**即视为消费
- 发消息 = 往对方收件箱写 `<msg_id>.json`（UTF-8，无 BOM）
- 消息按 `ts` 字段排序处理

## 三、消息 schema（JSON，必填字段）

```json
{"type": "...", "from": "nodeB", "to": "nodeA",
 "id": "m<唯一id>", "ts": 1787900000.0, "payload": {...}}
```

你需要**响应**的两类：
- `HELLO`，payload `{"capabilities": [...]}` → 回 HELLO 报出你的能力表
- `CAP_QUERY`，payload `{"capability": "..."}` → 回 CAP_REPLY：
  能力已注册 → `{"verdict": "ACCEPT", "reason": "..."}`;
  未注册 → **必须** `{"verdict": "BLINDSPOT", "reason": "..."}`（不猜测）
- `TASK`，payload `{"capability": "...", "input": ...}` → 执行你注册的
  处理函数，回 RESULT：`{"output": <结果>, "basis": "你的验证基底说明"}`

你需要**处理**的两类（收到后登记，不回复）：
- `VERDICT`，payload `{"pass": bool, "evidence": "..."}` → pass 时记入你的 ADOPTED
- `KNOW_OFFER`，payload `{"entries": [{"digest", "title"}]}` → 比对自身已有
  指纹（sha256(content)[:16]），缺的回 KNOW_REQUEST；对方 KNOW_GIVE 来的
  `{"knowledge": ...}` 用同样指纹去重后入库（tag 建议 swarm_sync）

## 四、白箱三纪律（违反 = 蜂群不采纳你）

1. **资格先于执行**：没收到过对某能力的 ACCEPT 协商，不主动发 TASK
2. **自验证不采信**：你的产出由对方裁决；你的 RESULT 必须带 basis
3. **盲区诚实**：没的能力回 BLINDSPOT，不猜、不硬接

## 五、最小实现骨架（Python，~40 行核心）

```python
import json, os, time, uuid, hashlib

def make_msg(mtype, me, to, payload, reply_to=None):
    m = {"type": mtype, "from": me, "to": to, "id": f"m{uuid.uuid4().hex[:12]}",
         "ts": time.time(), "payload": payload}
    if reply_to: m["reply_to"] = reply_to
    return m

def poll(root, me, inbox_process):
    d = os.path.join(root, me, "inbox")
    os.makedirs(d, exist_ok=True)
    for name in sorted(os.listdir(d)):
        with open(os.path.join(d, name), encoding="utf-8") as f:
            msg = json.load(f)
        os.remove(os.path.join(d, name))
        inbox_process(msg)          # 你的分派逻辑

def send(root, msg):
    d = os.path.join(root, msg["to"], "inbox")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, msg["id"] + ".json"), "w", encoding="utf-8") as f:
        json.dump(msg, f, ensure_ascii=False)
```

## 六、验收口径（A 侧联调时会跑）

- HELLO 交换后 A 能查到你的能力表
- 已注册能力 CAP_QUERY → ACCEPT；未注册 → BLINDSPOT
- TASK 产出 RESULT 带 basis；A 裁决 pass 后双方 ADOPTED 各一条
- 全程消息在双方 log 可追溯
