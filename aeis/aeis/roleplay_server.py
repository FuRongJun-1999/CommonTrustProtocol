# -*- coding: utf-8 -*-
"""
aeis.roleplay_server · 灵枢角色扮演引擎 HTTP 服务（REST · 零外部依赖）
====================================================================
对外暴露角色扮演机制的三导入接口 + 角色管理 + 注入块获取，
酒馆（SillyTavern）生态或其他角色扮演前端通过 REST 调用。

路由：
  GET  /health                        存活探测
  GET  /roles                        角色列表
  GET  /roles/<role_id>              角色元数据（含条件空间声明）
  POST /roles                        创建角色
  POST /roles/<role_id>/memory       记忆导入（历史 → KNOWLEDGE 层）
  POST /roles/<role_id>/anchor       自我锚点导入（→ SELF/ANCHOR 层，no_forget）
  POST /roles/<role_id>/values       特化价值观导入（→ STRUCTURE 层，带条件）
  GET  /roles/<role_id>/block        角色扮演注入块（供桥接层注入）
  GET  /roles/<role_id>/recall?q=..  角色历史召回

启动：
  python -m aeis.roleplay_server --port 8792 --data-dir roleplay_data
  # 或
  AEIS_ROLEPLAY_DATA=roleplay_data python -m aeis.roleplay_server

设计约束：
- 零外部依赖（http.server + urllib，纯标准库）
- 每角色独立记忆库（data_dir/roleplay/<role_id>.db）——蜂群结构隔离
- 工程层实现，不构成理论定理（协议纪律）
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict
from urllib.parse import parse_qs, unquote, urlparse

from .roleplay import RolePlayEngine

ENGINE: RolePlayEngine


# ---------------------------------------------------------------------------
# 请求处理
# ---------------------------------------------------------------------------

def _read_body(handler: BaseHTTPRequestHandler) -> Dict[str, Any]:
    length = int(handler.headers.get("Content-Length", 0))
    raw = handler.rfile.read(length) if length else b"{}"
    try:
        body = json.loads(raw.decode("utf-8"))
        return body if isinstance(body, dict) else {}
    except Exception:
        return {}


def _route(handler: BaseHTTPRequestHandler, path: str, method: str) -> bool:
    """路由分发；处理成功返回 True，未匹配返回 False。"""
    global ENGINE

    # GET /health
    if method == "GET" and path == "/health":
        handler._send_json(200, {"status": "ok", "roles": len(ENGINE.list_roles())})
        return True

    # GET /roles
    if method == "GET" and path == "/roles":
        roles = []
        for rid in ENGINE.list_roles():
            meta = ENGINE.get_role(rid) or {}
            roles.append({"role_id": rid, "name": meta.get("name", rid),
                          "anchors": meta.get("anchors", 0),
                          "values": meta.get("values", 0),
                          "memories": meta.get("memories", 0)})
        handler._send_json(200, {"roles": roles})
        return True

    # POST /roles  （创建角色）
    if method == "POST" and path == "/roles":
        body = _read_body(handler)
        role_id = body.get("role_id", "").strip()
        if not role_id:
            handler._send_json(400, {"error": "role_id required"})
            return True
        r = ENGINE.create_role(role_id, name=body.get("name", ""),
                               scenario=body.get("scenario", ""),
                               first_mes=body.get("first_mes", ""))
        handler._send_json(200, r)
        return True

    # GET /roles/<role_id>（不含子路径）
    if method == "GET" and path.startswith("/roles/") and "/" not in path[len("/roles/"):]:
        rid = unquote(path[len("/roles/"):])
        if rid in ENGINE.list_roles():
            handler._send_json(200, {"role_id": rid, "meta": ENGINE.get_role(rid)})
            return True
        handler._send_json(404, {"error": f"role not found: {rid}"})
        return True

    # 子路由：POST /roles/<rid>/memory|anchor|values
    for action, fn in (("memory", ENGINE.import_memory),
                       ("anchor", ENGINE.import_anchor),
                       ("values", ENGINE.import_values)):
        prefix = f"/roles/"
        suffix = f"/{action}"
        if method == "POST" and path.startswith(prefix) and path.endswith(suffix):
            rid = unquote(path[len(prefix):-len(suffix)])
            if rid in ENGINE.list_roles():
                body = _read_body(handler)
                items = body.get("items") or body.get(action + "s") or []
                result = fn(rid, items if isinstance(items, list) else [])
                handler._send_json(200, result)
                return True
            handler._send_json(404, {"error": f"role not found: {rid}"})
            return True

    # GET /roles/<rid>/block
    if method == "GET" and path.endswith("/block"):
        rid = unquote(path[len("/roles/"):-len("/block")])
        if rid in ENGINE.list_roles():
            handler._send_json(200, {"role_id": rid, "block": ENGINE.build_role_block(rid)})
            return True
        handler._send_json(404, {"error": f"role not found: {rid}"})
        return True

    # GET /roles/<rid>/recall?q=..
    if method == "GET" and "/recall" in path:
        base, _, _ = path.partition("/recall")
        rid = unquote(base[len("/roles/"):])
        qs = parse_qs(urlparse(path).query)
        q = (qs.get("q") or [""])[0]
        if rid in ENGINE.list_roles():
            hits = ENGINE.recall_role(rid, q, limit=8)
            handler._send_json(200, {"role_id": rid, "hits": hits})
            return True
        handler._send_json(404, {"error": f"role not found: {rid}"})
        return True

    return False


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, status: int, body: Any) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if not _route(self, parsed.path, "GET"):
            self._send_json(404, {"error": f"not found: {self.path}"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if not _route(self, parsed.path, "POST"):
            self._send_json(404, {"error": f"not found: {self.path}"})

    def log_message(self, fmt: str, *args: Any) -> None:
        if os.environ.get("ROLEPLAY_QUIET") == "1":
            return
        super().log_message(fmt, *args)


def main() -> None:
    global ENGINE
    ap = argparse.ArgumentParser(description="灵枢角色扮演引擎 — REST 服务")
    ap.add_argument("--port", type=int, default=int(os.environ.get("ROLEPLAY_PORT", "8792")))
    ap.add_argument("--data-dir", default=os.environ.get("AEIS_ROLEPLAY_DATA", "roleplay_data"))
    ap.add_argument("--host", default=os.environ.get("ROLEPLAY_HOST", "127.0.0.1"))
    args = ap.parse_args()

    ENGINE = RolePlayEngine(data_dir=args.data_dir)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"[灵枢角色扮演引擎] listening on http://{args.host}:{args.port} (data={args.data_dir})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[灵枢角色扮演引擎] 关闭中...")
        ENGINE.close()
        server.server_close()


if __name__ == "__main__":
    main()
