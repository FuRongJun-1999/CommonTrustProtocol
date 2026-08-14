# 灵枢 Web 宿主（harness v1.2）

> 灵枢稳定运行的网页宿主：聊天 + 状态面板。零依赖 http.server。

## 架构

```
浏览器 (http://localhost:8000)
   │  fetch API
   ▼
harness/web/server.py（ThreadingHTTPServer，零依赖）
   ├─ POST /api/chat      → MessageHub 队列 → 主循环 → 回复（≤60s 同步等待）
   ├─ GET  /api/poll      → 增量消息（语音对话同步可见，2s 轮询）
   ├─ GET  /api/status    → 身份/记忆/心跳/插件/子体（5s 轮询）
   ├─ GET  /api/memory    → 记忆检索
   ├─ POST /api/agents    → 子体派发
   └─ GET  /api/logs      → 日志尾部
   ▲
MessageHub（harness/core/hub.py）：voice/terminal/web 三路输入统一队列
   ▼
主循环线程 → DeepSeek 思考 → 回复（publish + 纳西妲语音）
```

## 启动

```bash
# 全功能（语音 + 终端 + 调度 + 插件 + 子体 + Web）
python -m harness.main --web --port 8000
```

detached 常驻（Windows）：
```powershell
Start-Process -WindowStyle Hidden -FilePath python.exe `
  -ArgumentList '-m','harness.main','--web','--port','8000' `
  -WorkingDirectory 'D:\Program Files\2_ai\AEIS'
```

## 前端

- **聊天区**：消息气泡（用户/灵枢），语音输入对话实时显示（source 标记 voice）
- **状态面板**：记忆节点数、调度任务（心跳/睡眠巩固）、插件健康、子体任务、系统日志
- 深色科技风（纳西妲绿点缀），无框架原生 JS

## API

| 路由 | 方法 | 说明 |
|---|---|---|
| `/` | GET | 页面 |
| `/api/chat` | POST `{text}` | 投递 → 等待回复 → `{reply}` |
| `/api/poll` | GET `?since=` | 增量消息 |
| `/api/status` | GET | 状态聚合 |
| `/api/memory` | GET `?q=` | 记忆检索（content/tags） |
| `/api/agents` | POST `{prompt}` | 子体派发 |
| `/api/logs` | GET `?n=` | 日志尾部 |

## 测试

```bash
python tests/test_web.py   # 10 项（静态页/状态/聊天/轮询/检索/404）
```

## 后续

- SSE 流式回复（现同步等待 ≤60s）
- 桌面应用壳（Tauri/Electron 套 Web 内核）
- 页面内语音（浏览器 Web Speech）作为 VAD 线程的补充通道
