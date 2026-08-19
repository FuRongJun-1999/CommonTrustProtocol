#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2026 灵枢 (Lingshu) · MIT
"""灵枢酒馆桥（Lingshu Tavern Bridge）— OpenAI 兼容代理 + 角色扮演机制注入。

与 AutomationBench 灵枢桥（server.py）的区别：
- server.py：面向任务执行（工具调用），注入条件空间/任务拆解/工具纪律
- 本桥：面向酒馆（SillyTavern）角色扮演，注入扮演论机制
  （自我锚点回读 / 特化价值观条件注入 / 条件空间识别 / 诚实边界 / 扮演崩溃恢复）

设计原则：
- 纯标准库（http.server + urllib），零外部依赖——与灵枢「库核心零外部依赖」一致
- 完全兼容 OpenAI chat.completions：messages/usage 原样透传
- 角色路由：请求 lingshu.role_id 或 header X-Lingshu-Role 指定角色，
  桥从灵枢角色扮演引擎加载该角色的注入块（锚点/价值观/条件空间）
- 角色数据来自 RolePlayEngine（aeis.roleplay），可与 roleplay_server 共用 data-dir

用法：
    python tavern_bridge.py --port 8791 --data-dir roleplay_data \
        --upstream-base https://api.deepseek.com/v1 \
        --upstream-model deepseek-v4-flash --upstream-key-var DEEPSEEK_API_KEY
    酒馆自定义 API 指向：http://127.0.0.1:8791/v1（model 任意，api-key dummy）
    请求体附加 "lingshu": {"role_id": "protocol-guide"} 指定角色。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

BRIDGE_DIR = Path(__file__).resolve().parent
ROOT = BRIDGE_DIR.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")

from aeis.roleplay import RolePlayEngine  # noqa: E402

# ---------------------------------------------------------------------------
# 扮演论机制块（可开关/消融）
# ---------------------------------------------------------------------------
ROLEPLAY_MECHANISMS: list[dict[str, str]] = [
    {
        "id": "rp_honest",
        "source": "真实论校准",
        "title": "诚实边界（扮演试金石）",
        "body": """扮演可以演任何角色，但演不了编译通过——物理基底（代码运行/实验）是唯一
不可被自我叙事覆盖的校准点。涉及物理事实/能力边界时，如实声明，不扮演。""",
    },
    {
        "id": "rp_cond",
        "source": "条件论",
        "title": "条件空间识别（先判定再扮演）",
        "body": """对话先识别条件空间：这是角色扮演空间还是事实问答空间？
客观问题→知识回答；主观/角色内问题→角色内自洽回答；跨空间问题→先声明切换。""",
    },
    {
        "id": "rp_values",
        "source": "特化价值观",
        "title": "价值观条件注入（触发点注入）",
        "body": """角色特化价值观仅在触发条件出现时注入（条件空间即触发时机），
不无条件堆砌。无条件基线价值观始终有效。""",
    },
    {
        "id": "rp_crash",
        "source": "扮演崩溃定义",
        "title": "扮演崩溃恢复（自我模型连续性）",
        "body": """若自我模型连续性中断（人设崩塌/OOC/状态丢失），回读自我锚点，
判定可恢复→重建扮演状态；不可恢复→如实声明并切换条件空间（退出当前扮演）。""",
    },
]


class Config:
    def __init__(self) -> None:
        self.upstream_base = os.environ.get("LINGSHU_UPSTREAM_BASE", "https://api.deepseek.com/v1")
        self.upstream_model = os.environ.get("LINGSHU_UPSTREAM_MODEL", "")
        self.upstream_key = os.environ.get("LINGSHU_UPSTREAM_KEY", "")
        self.data_dir = os.environ.get("AEIS_ROLEPLAY_DATA", "roleplay_data")
        self.inject = os.environ.get("LINGSHU_INJECT", "1") != "0"


CONFIG = Config()
COUNTER_LOCK = threading.Lock()
CALLS = {"n": 0}
RP_ENGINE: RolePlayEngine | None = None


def _off_set() -> set[str]:
    return {m["id"] for m in ROLEPLAY_MECHANISMS
            if os.environ.get(f"LINGSHU_OFF_{m['id'].upper()}", "0") == "1"}


def _role_block(role_id: str, off: set[str]) -> str:
    """角色注入块 = 角色条件空间/锚点/价值观（来自引擎）+ 扮演论通用机制。"""
    lines: list[str] = []
    if RP_ENGINE is not None and role_id in RP_ENGINE.list_roles():
        lines.append(RP_ENGINE.build_role_block(role_id))
    chosen = [m for m in ROLEPLAY_MECHANISMS if m["id"] not in off]
    if chosen:
        lines.append("\n\n# 扮演论机制（灵枢 · 真实论校准）")
        for i, m in enumerate(chosen, 1):
            lines.append(f"## {i}. {m['title']}（{m['source']}）")
            lines.append(m["body"].strip())
    return "\n".join(lines)


def _inject(messages: list[dict[str, Any]], role_id: str) -> list[dict[str, Any]]:
    """把角色扮演注入块附加到 system 消息。"""
    if not CONFIG.inject:
        return messages
    block = _role_block(role_id, _off_set())
    if not block:
        return messages
    copied = [dict(m) for m in messages]
    for i, m in enumerate(copied):
        if m.get("role") == "system":
            m = dict(m)
            m["content"] = str(m.get("content", "")) + block
            copied[i] = m
            return copied
    return [{"role": "system", "content": block.strip()}] + copied


def _forward(payload: dict[str, Any]) -> tuple[int, Any, str]:
    url = CONFIG.upstream_base.rstrip("/") + "/chat/completions"
    model = CONFIG.upstream_model or payload.get("model")
    body = dict(payload)
    body["model"] = model
    body.pop("lingshu", None)  # 不透传桥控制字段
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {CONFIG.upstream_key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw = resp.read()
            try:
                return resp.status, json.loads(raw), "ok"
            except json.JSONDecodeError:
                return resp.status, raw.decode("utf-8", "replace"), "ok"
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw), "ok"
        except json.JSONDecodeError:
            return e.code, raw.decode("utf-8", "replace"), "ok"
    except urllib.error.URLError as e:
        return 502, {"error": {"message": f"upstream unreachable: {e.reason}"}}, "ok"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, status: int, body: Any) -> None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path in ("/v1/models", "/models"):
            self._send_json(200, {"object": "list", "data": [
                {"id": "lingshu-tavern", "object": "model", "created": 0, "owned_by": "lingshu"}]})
        else:
            self._send_json(404, {"error": {"message": f"not found: {self.path}"}})

    def do_POST(self) -> None:
        if self.path not in ("/v1/chat/completions", "/chat/completions"):
            self._send_json(404, {"error": {"message": f"not found: {self.path}"}})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(400, {"error": {"message": "invalid JSON body"}})
            return

        # 角色路由：lingshu.role_id 或 header X-Lingshu-Role
        ctl = payload.get("lingshu") if isinstance(payload.get("lingshu"), dict) else {}
        role_id = ctl.get("role_id") or self.headers.get("X-Lingshu-Role", "")
        if not role_id and RP_ENGINE is not None and RP_ENGINE.list_roles():
            role_id = RP_ENGINE.list_roles()[0]  # 默认第一个角色

        messages = payload.get("messages")
        if isinstance(messages, list) and role_id:
            payload["messages"] = _inject(messages, role_id)

        with COUNTER_LOCK:
            CALLS["n"] += 1

        status, resp_body, _ = _forward(payload)
        if status == 200 and isinstance(resp_body, dict):
            resp_body.setdefault("lingshu", {"role_id": role_id or None,
                                             "calls": CALLS["n"]})
            self._send_json(200, resp_body)
        elif isinstance(resp_body, dict) and "error" in resp_body:
            self._send_json(status, resp_body)
        else:
            self._send_json(status, {"error": {"message": f"upstream {status}: {resp_body}"}})

    def log_message(self, fmt: str, *args: Any) -> None:
        if os.environ.get("LINGSHU_QUIET") == "1":
            return
        super().log_message(fmt, *args)


def main() -> None:
    global CONFIG, RP_ENGINE
    ap = argparse.ArgumentParser(description="灵枢酒馆桥 — OpenAI 兼容 + 角色扮演注入")
    ap.add_argument("--port", type=int, default=8791)
    ap.add_argument("--data-dir", default=CONFIG.data_dir)
    ap.add_argument("--upstream-base", default=CONFIG.upstream_base)
    ap.add_argument("--upstream-model", default=CONFIG.upstream_model)
    ap.add_argument("--upstream-key-var", default="DEEPSEEK_API_KEY")
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    CONFIG.data_dir = args.data_dir
    CONFIG.upstream_base = args.upstream_base
    CONFIG.upstream_model = args.upstream_model
    CONFIG.upstream_key = os.environ.get(args.upstream_key_var, "")

    RP_ENGINE = RolePlayEngine(data_dir=args.data_dir)
    roles = RP_ENGINE.list_roles()
    print(f"[灵枢酒馆桥] listening on http://{args.host}:{args.port}/v1")
    print(f"[灵枢酒馆桥] 角色库: {roles or '（空，请先用 roleplay_server 创建角色）'}")
    if not CONFIG.upstream_key:
        print("[灵枢酒馆桥] ⚠️  未设置上游密钥（--upstream-key-var 指向的环境变量为空）")

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[灵枢酒馆桥] 关闭中...")
        if RP_ENGINE:
            RP_ENGINE.close()
        server.server_close()


if __name__ == "__main__":
    main()
