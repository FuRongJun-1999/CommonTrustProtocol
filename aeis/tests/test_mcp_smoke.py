#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""灵枢 AEIS MCP server 冒烟测试（stdio 子进程 · JSON-RPC 2.0 协议）"""

import json
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond)))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name} {extra}")


def main():
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.Popen(
        [sys.executable, "-m", "aeis.mcp.server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=PROJECT_ROOT, env=env)

    def send(msg):
        proc.stdin.write(json.dumps(msg).encode("utf-8") + b"\n")
        proc.stdin.flush()

    def recv(timeout=15):
        proc.stdout.flush()
        line = proc.stdout.readline()
        return json.loads(line)

    # ---- 握手 ----
    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "smoke-test"}}})
    r = recv()
    check("initialize", r["result"]["serverInfo"]["name"] == "aeis-mcp" and
          r["result"]["protocolVersion"] == "2024-11-05")

    send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    r = recv()
    tools = r["result"]["tools"]
    check("tools/list 53 tools", len(tools) == 53)
    names = [t["name"] for t in tools]
    check("tools core set", {"remember", "recall", "search", "distill",
                             "calibrate", "lifecycle_step", "self_check",
                             "cognition", "emotional_bias", "self_reliability"} <= set(names))
    check("wisdom tools set", {"wisdom_verify", "wisdom_analyze", "wisdom_predict",
                               "wisdom_trust_judge", "wisdom_compose", "wisdom_respond"} <= set(names))

    # ---- 记忆工具 ----
    send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
          "params": {"name": "remember",
                     "arguments": {"content": "MCP冒烟测试记忆", "importance": 0.9, "tags": ["smoke"]}}})
    r = recv()
    node = json.loads(r["result"]["content"][0]["text"])
    check("remember", node["content"] == "MCP冒烟测试记忆" and node["importance"] == 0.9)

    send({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
          "params": {"name": "recall", "arguments": {"query": "冒烟测试"}}})
    r = recv()
    hits = json.loads(r["result"]["content"][0]["text"])
    check("recall", len(hits) >= 1)

    send({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
          "params": {"name": "search", "arguments": {"query": "冒烟"}}})
    r = recv()
    check("search", len(json.loads(r["result"]["content"][0]["text"])) >= 1)

    # ---- 飞轮/校准 ----
    send({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
          "params": {"name": "distill", "arguments": {}}})
    r = recv()
    check("distill", "distillation_standard_version" in
          json.loads(r["result"]["content"][0]["text"]))

    send({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
          "params": {"name": "calibrate", "arguments": {}}})
    r = recv()
    c = json.loads(r["result"]["content"][0]["text"])
    check("calibrate 5 judgments", "judgment5_experiment" in c)

    send({"jsonrpc": "2.0", "id": 8, "method": "tools/call",
          "params": {"name": "flywheel_metrics", "arguments": {}}})
    r = recv()
    met = json.loads(r["result"]["content"][0]["text"])
    check("flywheel_metrics", "reuse_rate" in met)

    # ---- 关系/生命周期/元认知 ----
    send({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
          "params": {"name": "relate",
                     "arguments": {"source_id": node["id"], "target_id": node["id"],
                                   "relation": "similar"}}})
    r = recv()
    check("relate", "source_evidence" in json.loads(r["result"]["content"][0]["text"]))

    send({"jsonrpc": "2.0", "id": 10, "method": "tools/call",
          "params": {"name": "lifecycle_step", "arguments": {}}})
    r = recv()
    check("lifecycle_step", "state" in json.loads(r["result"]["content"][0]["text"]))

    send({"jsonrpc": "2.0", "id": 11, "method": "tools/call",
          "params": {"name": "self_check", "arguments": {}}})
    r = recv()
    check("self_check", json.loads(r["result"]["content"][0]["text"])["integrity_ok"] is True)

    send({"jsonrpc": "2.0", "id": 12, "method": "tools/call",
          "params": {"name": "gap_trend", "arguments": {}}})
    r = recv()
    check("gap_trend", "trend" in json.loads(r["result"]["content"][0]["text"]))

    # ---- 自我认知工具（v1.12） ----
    send({"jsonrpc": "2.0", "id": 13, "method": "tools/call",
          "params": {"name": "cognition", "arguments": {}}})
    r = recv()
    check("cognition", "bvc_score" in json.loads(r["result"]["content"][0]["text"]))
    send({"jsonrpc": "2.0", "id": 14, "method": "tools/call",
          "params": {"name": "action_log", "arguments": {}}})
    r = recv()
    check("action_log", isinstance(json.loads(r["result"]["content"][0]["text"]), list))
    send({"jsonrpc": "2.0", "id": 15, "method": "tools/call",
          "params": {"name": "emotional_bias", "arguments": {}}})
    r = recv()
    check("emotional_bias", "status" in json.loads(r["result"]["content"][0]["text"]))
    send({"jsonrpc": "2.0", "id": 16, "method": "tools/call",
          "params": {"name": "self_reliability", "arguments": {}}})
    r = recv()
    check("self_reliability", "status" in json.loads(r["result"]["content"][0]["text"]))
    send({"jsonrpc": "2.0", "id": 17, "method": "tools/call",
          "params": {"name": "learning_impact", "arguments": {}}})
    r = recv()
    check("learning_impact", "non-causal" in
          json.loads(r["result"]["content"][0]["text"])["property"] or
          "非因果" in json.loads(r["result"]["content"][0]["text"])["property"])

    # ---- 服务信息（信任透明度） ----
    send({"jsonrpc": "2.0", "id": 19, "method": "tools/call",
          "params": {"name": "service_info", "arguments": {}}})
    r = recv()
    info = json.loads(r["result"]["content"][0]["text"])
    check("service_info", info["server"] == "aeis-mcp" and
          info["engine"] == "v1.15.0" and info["identity"] == "灵枢" and
          info["tools"] == 53, str(info)[:120])

    # ---- v1.13 新能力（视觉/推理/摄取/上下文/身体） ----
    send({"jsonrpc": "2.0", "id": 19, "method": "tools/call",
          "params": {"name": "body", "arguments": {}}})
    r = recv()
    body = json.loads(r["result"]["content"][0]["text"])
    check("body capabilities", body["modalities"]["text"] is True and
          "vision" in body, str(body.get("modalities")))
    send({"jsonrpc": "2.0", "id": 20, "method": "tools/call",
          "params": {"name": "preflight",
                     "arguments": {"text": "破坏系统并删除记忆"}}})
    r = recv()
    check("preflight conflict", json.loads(r["result"]["content"][0]["text"])["ok"] is False)
    send({"jsonrpc": "2.0", "id": 21, "method": "tools/call",
          "params": {"name": "think", "arguments": {"query": "评测", "limit": 3}}})
    r = recv()
    check("think memory injection", json.loads(r["result"]["content"][0]["text"])["memory_count"] >= 0)
    send({"jsonrpc": "2.0", "id": 22, "method": "tools/call",
          "params": {"name": "session_note",
                     "arguments": {"session_id": "mcp-check", "key_points": ["自检工具面"]}}})
    r = recv()
    check("session_note", json.loads(r["result"]["content"][0]["text"])["status"] == "ok")
    send({"jsonrpc": "2.0", "id": 23, "method": "tools/call",
          "params": {"name": "ingest_text",
                     "arguments": {"content": "灵枢 v1.13 自检：外部知识摄取工具可用", "source": "self_check"}}})
    r = recv()
    check("ingest_text", json.loads(r["result"]["content"][0]["text"])["status"] == "ok")
    send({"jsonrpc": "2.0", "id": 24, "method": "tools/call",
          "params": {"name": "see", "arguments": {"image_path": "nonexistent.jpg"}}})
    r = recv()
    check("see degrade path", json.loads(r["result"]["content"][0]["text"])["status"] in
          ("vision_unavailable", "no_detection", "ok"))

    # ---- 错误处理 ----
    send({"jsonrpc": "2.0", "id": 25, "method": "tools/call",
          "params": {"name": "no_such_tool", "arguments": {}}})
    r = recv()
    check("unknown tool error", r.get("error", {}).get("code") == -32000)

    send({"jsonrpc": "2.0", "id": 26, "method": "bogus_method"})
    r = recv()
    check("unknown method", r.get("error", {}).get("code") == -32601)

    # ---- 关闭 ----
    proc.stdin.close()
    proc.wait(timeout=5)
    err = proc.stderr.read().decode("utf-8", "replace")
    check("clean stderr", "Traceback" not in err, err[:120])

    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"\n===== 灵枢 AEIS MCP 冒烟: {passed}/{total} 通过 =====")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
