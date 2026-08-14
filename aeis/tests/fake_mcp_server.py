#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests/fake_mcp_server.py · 最小 MCP server（协议测试用）
================================================
stdio JSON-RPC 2.0 换行分隔。支持：
- initialize / tools/list / tools/call（echo 工具）
- 环境变量注入行为：
  FAKE_SEND_NOTIFY=1     initialize 后发一条通知
  FAKE_BAD_JSON=1        响应前输出一行非法 JSON
  FAKE_SLOW_MS=2000      call 前 sleep（测超时）
  FAKE_LARGE_KB=100      大 payload（测截断）
用法：python fake_mcp_server.py
"""
import json
import os
import sys
import time

TOOLS = [
    {"name": "echo", "description": "回显输入文本",
     "inputSchema": {"type": "object",
                     "properties": {"text": {"type": "string"}}}},
    {"name": "big", "description": "返回大 payload（测截断）",
     "inputSchema": {"type": "object", "properties": {}}},
]


def send(msg: dict):
    # 二进制 utf-8（Windows 管道默认 gbk 会乱码）
    sys.stdout.buffer.write(
        json.dumps(msg, ensure_ascii=False).encode("utf-8") + b"\n")
    sys.stdout.buffer.flush()


def read_line() -> str:
    raw = sys.stdin.buffer.readline()
    return raw.decode("utf-8", "replace") if raw else ""


def main():
    rid = 0
    while True:
        line = read_line()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            continue
        if "id" not in msg:
            continue  # 忽略客户端通知
        rid = msg["id"]
        method = msg.get("method", "")

        if os.environ.get("FAKE_BAD_JSON") == "1":
            sys.stdout.buffer.write("这不是合法JSON{{{ \n".encode("utf-8"))
            sys.stdout.buffer.flush()

        if method == "initialize":
            send({"jsonrpc": "2.0", "id": rid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fake-mcp", "version": "1.0"}}})
            if os.environ.get("FAKE_SEND_NOTIFY") == "1":
                send({"jsonrpc": "2.0", "method": "notifications/initialized",
                      "params": {}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            params = msg.get("params", {}) or {}
            name = params.get("name", "")
            if os.environ.get("FAKE_SLOW_MS"):
                time.sleep(int(os.environ["FAKE_SLOW_MS"]) / 1000.0)
            if name == "echo":
                text = (params.get("arguments", {}) or {}).get("text", "")
                send({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": f"echo:{text}"}]}})
            elif name == "big":
                kb = int(os.environ.get("FAKE_LARGE_KB", "100"))
                payload = "x" * (kb * 1024)
                send({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": payload}]}})
            else:
                send({"jsonrpc": "2.0", "id": rid,
                      "result": {"content": [], "isError": True}})
        elif method == "shutdown":
            send({"jsonrpc": "2.0", "id": rid, "result": None})
            break
        else:
            send({"jsonrpc": "2.0", "id": rid,
                  "error": {"code": -32601, "message": f"unknown method {method}"}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
