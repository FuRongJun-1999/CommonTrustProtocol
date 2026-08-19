# -*- coding: utf-8 -*-
"""
aeis.roleplay_web · 灵枢角色扮演网页服务（REST · 零外部依赖）
===========================================================
第二种交互方式：网页服务直接调用白箱 + 灵枢（信息处理全部由灵枢完成）。

- 对话界面：GET / → 内置 HTML（角色扮演对话 UI）
- 对话 API：POST /api/chat  {message, session_id, role_id} → {reply, route}
- 角色 API：POST /api/roles / /api/roles/<id>/{memory,anchor,values}（三导入接口）
- 角色注入块：GET /api/roles/<id>/block

运行：
    python -m aeis.roleplay_web --port 8793 --data-dir roleplay_data
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

from .api import Agent
from .roleplay import RolePlayEngine
from .roleplay_chat import LingshuChat

CHAT: LingshuChat | None = None
RP: RolePlayEngine | None = None

# 内置对话界面（单文件 HTML，无外部依赖）
PAGE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>灵枢 · 角色扮演对话</title>
<style>
  body { font-family: system-ui, sans-serif; max-width: 760px; margin: 0 auto;
         padding: 16px; background: #14141c; color: #e8e8f0; }
  h1 { font-size: 20px; color: #8ab4f8; border-bottom: 1px solid #2a2a3a; padding-bottom: 8px; }
  #chat { height: 52vh; overflow-y: auto; border: 1px solid #2a2a3a; border-radius: 8px;
          padding: 12px; background: #1a1a24; margin-bottom: 12px; }
  .msg { margin: 8px 0; padding: 8px 12px; border-radius: 8px; white-space: pre-wrap; }
  .user { background: #2a3a5a; text-align: right; }
  .bot { background: #23233a; }
  .route { font-size: 11px; color: #6a6a8a; display: block; margin-top: 4px; }
  .controls { display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap; }
  select, button, input { background: #23233a; color: #e8e8f0; border: 1px solid #3a3a5a;
          border-radius: 6px; padding: 6px 10px; font-size: 14px; }
  #input { flex: 1; }
  .info { font-size: 12px; color: #8a8aaa; }
</style>
</head>
<body>
<h1>灵枢 · 角色扮演对话 <span class="info">（白箱 + 灵枢 · 扮演论 v3.3）</span></h1>
<div class="controls">
  <select id="roleSel"><option value="">通用（无角色）</option></select>
  <button id="newRole">新建角色</button>
  <input id="roleName" placeholder="角色名（新建时用）" style="width:140px">
  <span class="info" id="routeInfo"></span>
</div>
<div class="rp-editor" style="border:1px solid #2a2a3a;border-radius:8px;padding:10px;margin-bottom:12px;background:#1a1a24;">
  <div style="margin-bottom:6px;color:#8ab4f8;font-size:14px;">人设编辑器（自我锚点 / 价值观 / 记忆）— 当前角色: <b id="editRole">—</b></div>
  <div class="controls" style="margin-bottom:6px;">
    <span class="info">编辑模式（开发者）：</span>
    <input id="editKey" type="password" placeholder="ROLEPLAY_EDIT_KEY" style="width:160px">
    <button id="btnEditMode">进入编辑模式</button>
    <span class="info" id="editModeInfo"></span>
  </div>
  <div class="controls" style="margin-bottom:6px;" id="editPanel" style="display:none;">
    <select id="editKind">
      <option value="anchor">自我锚点（人设核心·不可遗忘）</option>
      <option value="values">特化价值观（带触发条件）</option>
      <option value="memory">历史记忆（背景经历）</option>
    </select>
    <input id="editContent" placeholder="内容…（锚点如：我是谁/性格核心/底线）" style="flex:1">
  </div>
  <div class="controls" id="condRow" style="display:none;margin-bottom:6px;">
    <input id="editCond" placeholder="触发条件（价值观用，如：涉及物理事实时）" style="flex:1">
    <input id="editImportance" placeholder="重要性 0-1" value="1.0" style="width:100px">
  </div>
  <div class="controls" id="editBtns" style="display:none;">
    <button id="btnAdd">＋ 加入人设</button>
    <button id="btnClear">清空人设</button>
    <span class="info" id="editInfo"></span>
  </div>
  <div class="controls" id="importRow" style="display:none;margin-top:6px;">
    <span class="info">文件导入：</span>
    <select id="impKind">
      <option value="values">特化价值观</option>
      <option value="memory">历史记忆</option>
      <option value="anchor">自我锚点</option>
    </select>
    <input type="file" id="impFile" accept=".json,.md,.txt" style="flex:1">
    <button id="btnImpFile">导入文件</button>
  </div>
  <div class="controls" style="margin-top:6px;">
    <button id="btnView">查看当前人设（只读）</button>
    <button id="btnManage">管理锚点（列表+删除）</button>
    <span class="info" id="editModeInfo2"></span>
  </div>
  <pre id="editOut" style="font-size:12px;color:#9a9abc;white-space:pre-wrap;max-height:160px;overflow-y:auto;margin:6px 0 0;"></pre>
</div>
<div id="chat"></div>
<div class="controls">
  <input id="input" placeholder="说点什么…" autocomplete="off">
  <button id="send">发送</button>
</div>
<script>
const chatEl = document.getElementById("chat");
const inputEl = document.getElementById("input");
const roleSel = document.getElementById("roleSel");
const routeInfo = document.getElementById("routeInfo");
let sessionId = "web-" + Date.now();

function addMsg(text, who, route) {
  const d = document.createElement("div");
  d.className = "msg " + who;
  d.textContent = text;
  if (route) {
    const r = document.createElement("span");
    r.className = "route";
    r.textContent = "route: " + route;
    d.appendChild(r);
  }
  chatEl.appendChild(d);
  chatEl.scrollTop = chatEl.scrollHeight;
}

async function api(path, body) {
  const r = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body || {}),
  });
  return r.json();
}

function showErr(msg) {
  const el = document.getElementById("routeInfo");
  if (el) el.textContent = "⚠️ " + msg;
  console.error(msg);
}

async function loadRoles() {
  try {
    const r = await fetch("/api/roles");
    if (!r.ok) { showErr("角色列表加载失败 HTTP " + r.status); return; }
    const data = await r.json();
    roleSel.innerHTML = '<option value="">通用（无角色）</option>';
    (data.roles || []).forEach(x => {
      const o = document.createElement("option");
      o.value = x.role_id; o.textContent = x.name + " (" + x.role_id + ")";
      roleSel.appendChild(o);
    });
    if (data.roles && data.roles.length === 0) showErr("角色库为空");
  } catch (e) { showErr("无法连接灵枢服务: " + e.message); }
}

async function send() {
  const text = inputEl.value.trim();
  if (!text) return;
  inputEl.value = "";
  addMsg(text, "user");
  const roleId = roleSel.value;
  try {
    const r = await api("/api/chat", {message: text, session_id: sessionId, role_id: roleId});
    addMsg(r.reply || "(无回复)", "bot", r.route);
    routeInfo.textContent = "route: " + (r.route || "?");
  } catch (e) { showErr("对话失败: " + e.message); }
}

document.getElementById("send").onclick = send;
inputEl.addEventListener("keydown", e => { if (e.key === "Enter") send(); });
document.getElementById("newRole").onclick = async () => {
  const name = document.getElementById("roleName").value.trim();
  if (!name) { alert("先输入角色名"); return; }
  const rid = "role-" + Date.now();
  try {
    const r = await api("/api/roles", {role_id: rid, name: name});
    if (r.error) { showErr("新建失败: " + r.error); return; }
    if (r.role_id) { await loadRoles(); roleSel.value = rid; syncEditRole(); }
    else showErr("新建失败: 无 role_id 返回");
  } catch (e) { showErr("新建失败: " + e.message); }
};

// ---- 人设编辑器（编辑模式 / 交互模式） ----
const editKind = document.getElementById("editKind");
const editContent = document.getElementById("editContent");
const editCond = document.getElementById("editCond");
const editImportance = document.getElementById("editImportance");
const condRow = document.getElementById("condRow");
const editOut = document.getElementById("editOut");
const editInfo = document.getElementById("editInfo");
const editRole = document.getElementById("editRole");
const editKey = document.getElementById("editKey");
const editModeInfo = document.getElementById("editModeInfo");
const editModeInfo2 = document.getElementById("editModeInfo2");
const editPanel = document.getElementById("editPanel");
const editBtns = document.getElementById("editBtns");
const importRow = document.getElementById("importRow");

let editMode = false;  // 交互模式默认（人设只读）
let editKeyVal = "";

function setEditMode(on) {
  editMode = on;
  editPanel.style.display = on ? "flex" : "none";
  editBtns.style.display = on ? "flex" : "none";
  importRow.style.display = on ? "flex" : "none";
  editModeInfo.textContent = on ? "✓ 编辑模式（可增删改+文件导入）" : "交互模式（人设只读）";
}

editKind.onchange = () => { condRow.style.display = (editKind.value === "values") ? "flex" : "none"; };

document.getElementById("btnEditMode").onclick = () => {
  const k = editKey.value.trim();
  if (!k) { alert("输入编辑密钥"); return; }
  editKeyVal = k;
  setEditMode(true);
  editKey.value = "";
};

function syncEditRole() {
  editRole.textContent = roleSel.value ? roleSel.value : "（先选择/新建角色）";
  editOut.textContent = "";
  setEditMode(false);  // 切角色回到交互模式
}

roleSel.onchange = syncEditRole;

document.getElementById("btnAdd").onclick = async () => {
  if (!editMode) { alert("先进入编辑模式（输入密钥）"); return; }
  const rid = roleSel.value;
  if (!rid) { alert("先在顶部选择或新建角色"); return; }
  const content = editContent.value.trim();
  if (!content) { alert("输入内容"); return; }
  const kind = editKind.value;
  const body = {role_id: rid, kind: kind, items: [], edit_key: editKeyVal};
  if (kind === "anchor") {
    body.items = [{content: content, immutable: true, importance: parseFloat(editImportance.value) || 1.0}];
  } else if (kind === "values") {
    body.items = [{name: content.split("：")[0] || content, condition: editCond.value.trim(),
                   priority: parseFloat(editImportance.value) || 0.8, body: content}];
  } else {
    body.items = [{content: content, importance: parseFloat(editImportance.value) || 0.6, tags: ["背景"]}];
  }
  const r = await api("/api/roles/" + rid + "/" + kind, body);
  if (r.error) { editInfo.textContent = "✗ " + r.error; return; }
  editInfo.textContent = (r.added !== undefined) ? "✓ 已加入 " + r.added + " 条" : JSON.stringify(r);
  editContent.value = ""; editCond.value = "";
  await viewRole();
};

document.getElementById("btnClear").onclick = async () => {
  if (!editMode) { alert("先进入编辑模式"); return; }
  const rid = roleSel.value;
  if (!rid || !confirm("清空该角色全部人设？")) return;
  const r = await api("/api/roles/" + rid + "/clear", {edit_key: editKeyVal});
  editInfo.textContent = r.removed ? "✓ 已清空 " + JSON.stringify(r.removed) : JSON.stringify(r);
  await viewRole();
};

document.getElementById("btnView").onclick = viewRole;

// 文件导入（编辑模式）
document.getElementById("btnImpFile").onclick = async () => {
  if (!editMode) { alert("先进入编辑模式"); return; }
  const rid = roleSel.value;
  if (!rid) { alert("先选择角色"); return; }
  const fileInput = document.getElementById("impFile");
  if (!fileInput.files.length) { alert("选择文件"); return; }
  const file = fileInput.files[0];
  const text = await file.text();
  const kind = document.getElementById("impKind").value;
  const r = await api("/api/roles/" + rid + "/import", {
    kind: kind, filename: file.name, content: text, edit_key: editKeyVal
  });
  if (r.error) { editInfo.textContent = "✗ " + r.error; return; }
  editInfo.textContent = "✓ 导入完成 " + JSON.stringify(r);
  fileInput.value = "";
  await viewRole();
};

async function viewRole() {
  const rid = roleSel.value;
  if (!rid) { alert("先选择角色"); return; }
  editOut.textContent = "读取中…";
  const r = await fetch("/api/roles/" + rid + "/block");
  const data = await r.json();
  editOut.textContent = data.block || "(空)";
}

// 管理锚点：列表 + 删除（编辑模式可删）
document.getElementById("btnManage").onclick = async () => {
  const rid = roleSel.value;
  if (!rid) { alert("先选择角色"); return; }
  const r = await fetch("/api/roles/" + rid + "/anchors");
  const data = await r.json();
  const list = data.anchors || [];
  if (!list.length) { editOut.textContent = "（无锚点）"; return; }
  const lines = list.map((a, i) => {
    const delBtn = editMode ? `  [删:${a.node_id.slice(-6)}]` : "";
    return `${i + 1}. ${a.content}${delBtn}`;
  });
  editOut.textContent = lines.join("\n") + (editMode ? "\n\n（删除格式：输「删:<后6位>」后点查看）" : "\n\n（编辑模式可删除）");
  if (editMode) {
    const delId = prompt("输入要删除的锚点后 6 位：");
    if (delId) {
      const target = list.find(a => a.node_id.slice(-6) === delId.trim());
      if (target) {
        const dr = await api("/api/roles/" + rid + "/anchor/delete", {node_id: target.node_id, edit_key: editKeyVal});
        editOut.textContent = JSON.stringify(dr);
      } else { editOut.textContent = "未找到该锚点"; }
    }
  }
};

loadRoles();
syncEditRole();
setEditMode(false);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, status: int, body: Any) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self, text: str) -> None:
        data = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self._send_html(PAGE)
            return
        if parsed.path == "/api/roles":
            roles = [{"role_id": rid,
                      "name": (RP.get_role(rid) or {}).get("name", rid)}
                     for rid in (RP.list_roles() if RP else [])]
            self._send_json(200, {"roles": roles})
            return
        if parsed.path.endswith("/block") and RP:
            rid = parsed.path[len("/api/roles/"):-len("/block")]
            if rid in RP.list_roles():
                self._send_json(200, {"role_id": rid, "block": RP.build_role_block(rid)})
                return
            self._send_json(404, {"error": "role not found"})
            return
        # 锚点列表（只读，无需密钥——交互模式可查看）
        if parsed.path.endswith("/anchors") and parsed.path.startswith("/api/roles/") and RP:
            rid = parsed.path[len("/api/roles/"):-len("/anchors")]
            if rid in RP.list_roles():
                self._send_json(200, {"role_id": rid,
                                      "anchors": RP.list_anchors(rid)})
                return
            self._send_json(404, {"error": "role not found"})
            return
        self._send_json(404, {"error": f"not found: {self.path}"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except Exception:
            body = {}

        parsed = urlparse(self.path)
        path = parsed.path

        # 对话
        if path == "/api/chat":
            message = body.get("message", "")
            if not message:
                self._send_json(400, {"error": "message required"})
                return
            role_id = body.get("role_id", "")
            session_id = body.get("session_id", "default")
            if CHAT is None:
                self._send_json(500, {"error": "chat pipeline not ready"})
                return
            result = CHAT.respond(message, session_id=session_id, role_id=role_id)
            self._send_json(200, result)
            return

        # 创建角色
        if path == "/api/roles":
            role_id = body.get("role_id", "")
            if not role_id:
                self._send_json(400, {"error": "role_id required"})
                return
            if RP is None:
                self._send_json(500, {"error": "roleplay not ready"})
                return
            r = RP.create_role(role_id, name=body.get("name", ""),
                               scenario=body.get("scenario", ""),
                               first_mes=body.get("first_mes", ""))
            self._send_json(200, r)
            return

        # 三导入接口（编辑模式：需 edit_key——角色人设=嵌套扮演设定，开发者权限）
        for action, fn in (("memory", "import_memory"), ("anchor", "import_anchor"),
                           ("values", "import_values")):
            suffix = f"/{action}"
            if path.startswith("/api/roles/") and path.endswith(suffix):
                rid = path[len("/api/roles/"):-len(suffix)]
                if RP is None or rid not in RP.list_roles():
                    self._send_json(404, {"error": f"role not found: {rid}"})
                    return
                # 写入人设 = 编辑操作，需编辑密钥
                if not RP.check_edit_key(body.get("edit_key", "")):
                    self._send_json(403, {"error": "编辑权限不足：需要 ROLEPLAY_EDIT_KEY（编辑模式）"})
                    return
                items = body.get("items", [])
                r = getattr(RP, fn)(rid, items if isinstance(items, list) else [])
                self._send_json(200, r)
                return

        # 编辑模式：文件导入（values/memory/anchor，需 edit_key）
        if path.endswith("/import") and path.startswith("/api/roles/"):
            rid = path[len("/api/roles/"):-len("/import")]
            if RP is None or rid not in RP.list_roles():
                self._send_json(404, {"error": f"role not found: {rid}"})
                return
            if not RP.check_edit_key(body.get("edit_key", "")):
                self._send_json(403, {"error": "编辑权限不足：需要 ROLEPLAY_EDIT_KEY"})
                return
            kind = body.get("kind", "values")
            filename = body.get("filename", "import.txt")
            content = body.get("content", "")
            # 写入临时文件（带正确扩展名以识别格式）
            import tempfile as _tf
            suffix = Path(filename).suffix or ".txt"
            tmp = _tf.NamedTemporaryFile("w", suffix=suffix, encoding="utf-8",
                                         delete=False, dir=_tf.gettempdir())
            tmp.write(content)
            tmp.close()
            try:
                r = RP.import_file(rid, tmp.name, kind=kind)
            finally:
                try:
                    os.remove(tmp.name)
                except Exception:
                    pass
            self._send_json(200, r)
            return

        # 编辑模式：修改锚点（需 edit_key）
        if path.endswith("/anchor/update") and path.startswith("/api/roles/"):
            rid = path[len("/api/roles/"):-len("/anchor/update")]
            if RP is None or rid not in RP.list_roles():
                self._send_json(404, {"error": f"role not found: {rid}"})
                return
            if not RP.check_edit_key(body.get("edit_key", "")):
                self._send_json(403, {"error": "编辑权限不足：需要 ROLEPLAY_EDIT_KEY"})
                return
            r = RP.update_anchor(rid, body.get("node_id", ""),
                                 content=body.get("content"),
                                 importance=body.get("importance"))
            self._send_json(200, r)
            return

        # 编辑模式：删除锚点（需 edit_key）
        if path.endswith("/anchor/delete") and path.startswith("/api/roles/"):
            rid = path[len("/api/roles/"):-len("/anchor/delete")]
            if RP is None or rid not in RP.list_roles():
                self._send_json(404, {"error": f"role not found: {rid}"})
                return
            if not RP.check_edit_key(body.get("edit_key", "")):
                self._send_json(403, {"error": "编辑权限不足：需要 ROLEPLAY_EDIT_KEY"})
                return
            r = RP.delete_anchor(rid, body.get("node_id", ""))
            self._send_json(200, r)
            return

        # 编辑模式：清空人设（需 edit_key）
        if path.endswith("/clear") and path.startswith("/api/roles/"):
            rid = path[len("/api/roles/"):-len("/clear")]
            if RP is None or rid not in RP.list_roles():
                self._send_json(404, {"error": f"role not found: {rid}"})
                return
            if not RP.check_edit_key(body.get("edit_key", "")):
                self._send_json(403, {"error": "编辑权限不足：需要 ROLEPLAY_EDIT_KEY"})
                return
            r = RP.clear_role(rid, body.get("kind", "all"))
            self._send_json(200, r)
            return

        self._send_json(404, {"error": f"not found: {self.path}"})

    def log_message(self, fmt: str, *args: Any) -> None:
        if os.environ.get("ROLEPLAY_QUIET") == "1":
            return
        super().log_message(fmt, *args)


def main() -> None:
    global CHAT, RP
    ap = argparse.ArgumentParser(description="灵枢角色扮演网页服务")
    ap.add_argument("--port", type=int, default=int(os.environ.get("ROLEPLAY_WEB_PORT", "8793")))
    ap.add_argument("--data-dir", default=os.environ.get(
        "AEIS_ROLEPLAY_DATA",
        r"D:\Program Files\2_ai\knowledge-base\roleplay_data"))
    ap.add_argument("--host", default=os.environ.get("ROLEPLAY_HOST", "127.0.0.1"))
    args = ap.parse_args()

    RP = RolePlayEngine(data_dir=args.data_dir)
    CHAT = LingshuChat(data_dir=args.data_dir, role_id="",
                       db_path=":memory:")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[灵枢角色扮演网页] http://{args.host}:{args.port}/")
    print(f"[灵枢角色扮演网页] 角色库: {RP.list_roles() or '（空）'}")
    print(f"[灵枢角色扮演网页] 对话管线: 白箱 + 灵枢（LLM 输出）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n关闭中...")
        if CHAT:
            CHAT.close()
        if RP:
            RP.close()
        server.server_close()


if __name__ == "__main__":
    main()
