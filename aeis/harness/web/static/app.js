/* 灵枢 Web 宿主前端逻辑：聊天 + 状态面板轮询 */
const $ = (id) => document.getElementById(id);
const chatLog = $("chat-log");
const input = $("input");
let lastTs = Date.now() / 1000 - 30;
const seen = new Set();  // 去重：input_id+role（防本地显示与轮询重复渲染）

function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function fmtTime(ts) {
  const d = new Date(ts * 1000);
  return d.toTimeString().slice(0, 8);
}

function addMsg(role, content, ts, source) {
  const div = document.createElement("div");
  div.className = "msg " + role;
  const tag = source && source !== "web" ? ` · ${source}` : "";
  div.innerHTML = `<div class="meta">${fmtTime(ts)}${tag}</div>${esc(content)}`;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

/* 渲染入口：按 input_id+role 去重（同一消息只显示一次） */
function renderMsg(m) {
  const key = (m.input_id || "") + ":" + (m.role || "");
  if (key !== ":") {
    if (seen.has(key)) return;
    seen.add(key);
  }
  addMsg(m.role, m.content, m.ts, m.source);
}

/* 轮询消息（2s） */
async function pollMessages() {
  try {
    const r = await fetch(`/api/poll?since=${lastTs}`);
    const data = await r.json();
    const msgs = data.messages || [];
    for (const m of msgs) renderMsg(m);
    if (msgs.length) {
      lastTs = Math.max(lastTs, ...msgs.map((m) => m.ts));
    }
  } catch (e) { /* 服务未就绪 */ }
}

/* 状态面板（5s） */
async function pollStatus() {
  try {
    const r = await fetch("/api/status");
    const s = await r.json();
    // 记忆
    const mem = s.memory || {};
    $("memory-info").innerHTML =
      `节点 <span class="ok">${mem.nodes ?? "?"}</span> · 边 ${mem.edges ?? "?"}` +
      ` · 盲区 ${mem.blindspots ?? "?"}`;
    // 心跳（最近调度任务）
    const sched = s.scheduler || [];
    $("heartbeat-info").innerHTML = sched.length
      ? `<ul>${sched.map(t =>
          `<li>${esc(t.title)} · ${t.runs} 次 · ${fmtTime(t.last || 0)}</li>`).join("")}</ul>`
      : "等待首次心跳…";
    // 插件
    const plugs = s.plugins || [];
    $("plugin-info").innerHTML = plugs.length
      ? `<ul>${plugs.map(p =>
          `<li class="${p.ok ? "ok" : "bad"}">${esc(p.name)} · ${p.tools} 工具` +
          (p.error ? ` · ${esc(p.error)}` : "") + `</li>`).join("")}</ul>`
      : "无插件";
    // 子体
    const ag = s.agents || {};
    $("agent-info").innerHTML = ag.pool
      ? `池 ${ag.pool} · 最近任务：${(ag.recent_tasks || []).join(" → ") || "无"}`
      : "未启用";
  } catch (e) { /* ignore */ }
}

async function pollLogs() {
  try {
    const r = await fetch("/api/logs?n=25");
    const d = await r.json();
    $("log-info").textContent = (d.logs || []).join("\n") || "（空）";
  } catch (e) { /* ignore */ }
}

/* 发送：POST 返回后统一渲染（input_id 去重防轮询重复） */
async function send() {
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  try {
    const r = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const d = await r.json();
    if (d.reply) {
      renderMsg({ role: "user", content: text, input_id: d.input_id,
                  ts: Date.now() / 1000 });
      renderMsg({ role: "assistant", content: d.reply, input_id: d.input_id,
                  ts: d.ts || Date.now() / 1000 });
    } else {
      addMsg("assistant", `（错误：${d.error || "无回复"}）`, Date.now() / 1000);
    }
  } catch (e) {
    addMsg("assistant", "（连接失败）", Date.now() / 1000);
  }
}

input.addEventListener("keydown", (e) => { if (e.key === "Enter") send(); });
$("send-btn").addEventListener("click", send);

setInterval(pollMessages, 2000);
setInterval(pollStatus, 5000);
setInterval(pollLogs, 8000);
pollMessages(); pollStatus(); pollLogs();
