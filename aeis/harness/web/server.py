# -*- coding: utf-8 -*-
"""harness.web.server · Web 宿主服务（零依赖 http.server）
================================================
路由：
  GET  /                  → index.html
  POST /api/chat          → {text} → 投递队列 → 等待回复（≤60s）→ {reply}
  GET  /api/poll?since=   → 增量消息（语音对话同步可见）
  GET  /api/status        → 身份/节点/心跳/插件/子体/语音状态
  GET  /api/memory?q=     → 记忆检索
  POST /api/agents        → {prompt} 子体派发 → 结果
  GET  /api/logs?n=       → 日志尾部
"""
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


def build_status(agent, supervisor, plugin_manager, hub) -> dict:
    """状态聚合（/api/status）。"""
    st = {"identity": getattr(agent, "identity", "灵枢"),
          "ts": time.time(), "running": True}
    try:
        check = agent.self_check()
        if isinstance(check, dict):
            st["memory"] = {"nodes": check.get("nodes"),
                            "edges": check.get("edges"),
                            "blindspots": check.get("blindspots")}
    except Exception:
        pass
    st["chat"] = {"messages": len(hub.history())}
    if supervisor is not None:
        results = supervisor.results(since=time.time() - 3600)
        st["agents"] = {"pool": supervisor.pool_size,
                        "recent_tasks": [t.status for t in results][-5:]}
    if plugin_manager is not None:
        st["plugins"] = plugin_manager.health()
    try:
        import sqlite3
        c = sqlite3.connect(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "automations.db"))
        rows = c.execute(
            "SELECT title, run_count, last_run_at FROM automations "
            "ORDER BY last_run_at DESC LIMIT 4").fetchall()
        c.close()
        st["scheduler"] = [{"title": r[0], "runs": r[1],
                            "last": r[2]} for r in rows]
    except Exception:
        st["scheduler"] = []
    return st


class WebHandler(BaseHTTPRequestHandler):
    agent = None
    hub = None
    supervisor = None
    plugin_manager = None
    logger = None

    # ---- 基础 ----

    def log_message(self, fmt, *args):
        pass  # 静默（日志走 logger）

    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        fp = os.path.normpath(os.path.join(STATIC_DIR, path.lstrip("/")))
        if not fp.startswith(STATIC_DIR):
            self._json({"error": "forbidden"}, 403)
            return
        if not os.path.isfile(fp):
            self._json({"error": "not found"}, 404)
            return
        ctype = "text/html; charset=utf-8"
        if fp.endswith(".js"):
            ctype = "application/javascript; charset=utf-8"
        elif fp.endswith(".css"):
            ctype = "text/css; charset=utf-8"
        with open(fp, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---- 路由 ----

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        q = parse_qs(parsed.query)
        if path == "/":
            return self._static("/index.html")
        if path == "/api/status":
            return self._json(build_status(self.agent, self.supervisor,
                                           self.plugin_manager, self.hub))
        if path == "/api/poll":
            since = float(q.get("since", ["0"])[0])
            msgs = [m for m in self.hub.recent(since_ts=since) if m["role"] != "system"]
            return self._json({"messages": msgs})
        if path == "/api/memory":
            query = q.get("q", [""])[0]
            try:
                results = self.agent.search(query, 10) if query else []
                # STNode 序列化：仅取 content/tags（零依赖 JSON 安全）
                items = [{"content": c.content,
                          "tags": list(c.tags or [])} for c, _ in results]
                return self._json({"results": items})
            except Exception as exc:
                return self._json({"error": str(exc)}, 500)
        if path == "/api/logs":
            n = int(q.get("n", ["30"])[0])
            tail = getattr(self.logger, "tail", [])[-n:]
            return self._json({"logs": tail})
        return self._static(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            return self._json({"error": "非法 JSON"}, 400)
        if path == "/api/chat":
            text = str(body.get("text", "")).strip()
            if not text:
                return self._json({"error": "empty text"}, 400)
            input_id = self.hub.send(text, source="web")
            reply = self.hub.wait_for_reply(input_id, timeout=60)
            if reply is None:
                return self._json({"error": "等待回复超时"}, 504)
            return self._json({"reply": reply["content"],
                               "input_id": input_id,
                               "ts": reply["ts"]})
        if path == "/api/agents":
            if self.supervisor is None:
                return self._json({"error": "子体未启用"}, 400)
            prompt = str(body.get("prompt", "")).strip()
            if not prompt:
                return self._json({"error": "empty prompt"}, 400)
            from harness.agents.task import AgentTask
            task = AgentTask(prompt, agent_role=str(body.get("role", "研究员")))
            self.supervisor.dispatch(task, timeout=120)
            self.supervisor.aggregate([task.task_id])
            return self._json({"task_id": task.task_id, "status": task.status,
                               "result": task.result, "error": task.error})
        return self._json({"error": "not found"}, 404)


def start_web_server(agent, hub, supervisor=None, plugin_manager=None,
                     log=None, port: int = 8000) -> threading.Thread:
    """启动 Web 宿主（线程）。返回线程对象（.stop() 停止）。"""
    WebHandler.agent = agent
    WebHandler.hub = hub
    WebHandler.supervisor = supervisor
    WebHandler.plugin_manager = plugin_manager
    WebHandler.logger = log or (lambda *a: None)

    httpd = ThreadingHTTPServer(("127.0.0.1", port), WebHandler)

    def _run():
        httpd.serve_forever()

    t = threading.Thread(target=_run, daemon=True)
    t._httpd = httpd

    def stop():
        try:
            httpd.shutdown()
            httpd.server_close()
        except Exception:
            pass

    t.stop = stop
    t.start()
    t._started = time.time()
    return t


if __name__ == "__main__":
    # 独立运行（测试/开发）
    from harness.core.agent_pool import AgentPool
    from harness.core.hub import MessageHub
    import os as _os
    pool = AgentPool({"AEIS_DB": _os.environ.get("AEIS_DB", "")})
    agent = pool.get()
    hub = MessageHub()
    t = start_web_server(agent, hub, port=8000)
    print("Web 宿主：http://localhost:8000（Ctrl+C 停止）")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        t.stop()
        pool.close()
