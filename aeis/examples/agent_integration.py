#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""灵枢 AEIS 智能体接入演示：两种接入方式
1) Python 库直连（Agent API）
2) MCP 协议调用（模拟其他智能体通过 stdio MCP 客户端接入）
"""

import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

import aeis


def via_python_api():
    """方式一：Python 库直连"""
    print("=" * 60)
    print("方式一 · Python 库直连（import aeis）")
    print("=" * 60)
    agent = aeis.Agent(identity="接入智能体-A")
    n = agent.remember("外部智能体通过 Python API 接入协议", importance=0.9)
    hits = agent.search("接入协议")
    print(f"  写入: {n.content}")
    print(f"  检索命中: {len(hits)} 条")
    agent.close()


def via_mcp_stdio():
    """方式二：MCP 协议调用（模拟其他智能体的 MCP 客户端）"""
    print("=" * 60)
    print("方式二 · MCP 协议调用（stdio · JSON-RPC 2.0）")
    print("=" * 60)
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [sys.executable, "-m", "aeis.mcp.server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=PROJECT_ROOT, env=env)

    def send(msg):
        proc.stdin.write(json.dumps(msg).encode("utf-8") + b"\n")
        proc.stdin.flush()

    def recv():
        return json.loads(proc.stdout.readline())

    # 握手
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "agent-demo"}}})
    print(f"  initialize → {recv()['result']['serverInfo']}")
    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = recv()["result"]["tools"]
    print(f"  tools/list → {len(tools)} 项工具")

    # 记忆写入 + 检索 + 蒸馏
    send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
          "params": {"name": "remember",
                     "arguments": {"content": "外部智能体通过 MCP 接入协议", "importance": 0.9}}})
    node = json.loads(recv()["result"]["content"][0]["text"])
    print(f"  remember → {node['content']}")
    send({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
          "params": {"name": "search", "arguments": {"query": "MCP 接入"}}})
    hits = json.loads(recv()["result"]["content"][0]["text"])
    print(f"  search → {len(hits)} 条命中")
    send({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
          "params": {"name": "self_check", "arguments": {}}})
    ok = json.loads(recv()["result"]["content"][0]["text"])
    print(f"  self_check → integrity_ok={ok['integrity_ok']}")

    proc.stdin.close()
    proc.wait(timeout=5)
    print("  MCP 会话正常关闭")


if __name__ == "__main__":
    print(f"灵枢 AEIS v{aeis.__version__} · 智能体接入演示\n")
    via_python_api()
    via_mcp_stdio()
    print("\n两种接入方式均可用 ✅")
