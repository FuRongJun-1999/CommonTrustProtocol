#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web 宿主回归测试（W2）
======================
覆盖：静态页/状态 API/聊天端到端（假消费者）/消息轮询/记忆检索/404。
check 框架。
"""
import json
import os
import sys
import tempfile
import threading
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        print(f"  [FAIL] {name} {detail}")


def http_get(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.status, r.read().decode("utf-8", "replace"), r.headers


def http_post(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def start_test_env(port=8123):
    """启动测试 Web 宿主（真实 Agent + 假消费者模拟主循环）。"""
    from harness.web.server import start_web_server
    from harness.core.hub import MessageHub
    from aeis.api import Agent
    agent = Agent(identity="测试灵枢", db_path=":memory:")
    hub = MessageHub()

    def fake_consumer():
        """模拟 harness 主循环：消费 → 回复 echo。"""
        while True:
            try:
                msg = hub.input_queue.get(timeout=1.0)
            except Exception:
                continue
            text = str(msg.get("text", ""))
            hub.publish("assistant", f"echo:{text}", reply_to=msg.get("input_id"))

    t = threading.Thread(target=fake_consumer, daemon=True)
    t.start()
    web = start_web_server(agent=agent, hub=hub, port=port, log=lambda *a: None)
    time.sleep(0.5)
    return agent, hub, web


def test_static_page(base):
    code, body, _ = http_get(base + "/")
    check("首页 200 + HTML", code == 200 and "灵枢" in body, f"code={code}")
    check("前端资源", http_get(base + "/app.js")[0] == 200
          and http_get(base + "/style.css")[0] == 200)


def test_status(base, agent):
    code, body, _ = http_get(base + "/api/status")
    st = json.loads(body)
    check("状态 API", code == 200 and st.get("identity") == "测试灵枢")
    check("状态含记忆", "memory" in st and "chat" in st)


def test_chat_endpoint(base):
    code, data = http_post(base + "/api/chat", {"text": "你好灵枢"})
    check("聊天端到端", code == 200 and data.get("reply") == "echo:你好灵枢",
          str(data.get("reply"))[:40])
    check("聊天返回 input_id", "input_id" in data)


def test_poll_incremental(base):
    code, data = http_post(base + "/api/chat", {"text": "第二条"})
    since = data.get("ts", 0) - 0.01
    code2, body, _ = http_get(f"{base}/api/poll?since={since}")
    msgs = json.loads(body).get("messages", [])
    check("轮询增量", any("第二条" in m.get("content", "") for m in msgs),
          str([m.get("content", "")[:10] for m in msgs]))


def test_memory_search(base, agent):
    agent.remember("测试记忆条目：灵枢的网页宿主", tags=["web", "test"])
    from urllib.parse import quote
    code, body, _ = http_get(base + "/api/memory?q=" + quote("网页宿主"))
    results = json.loads(body).get("results", [])
    check("记忆检索", code == 200 and
          any("网页宿主" in r.get("content", "") for r in results),
          str(results[:1])[:60])


def test_404(base):
    try:
        http_get(base + "/no/such/path")
        check("404 容器化", False)
    except Exception:
        check("404 容器化", True)


def test_agents_api(base):
    # 无 supervisor → 容器化错误
    code, body, _ = http_get(base + "/api/status")
    check("状态在无子体时不崩", code == 200)


def main():
    print("===== Web 宿主（W2）回归 =====")
    port = 8123
    agent, hub, web = start_test_env(port)
    base = f"http://127.0.0.1:{port}"
    try:
        test_static_page(base)
        test_status(base, agent)
        test_chat_endpoint(base)
        test_poll_incremental(base)
        test_memory_search(base, agent)
        test_404(base)
        test_agents_api(base)
    finally:
        web.stop()
        agent.close()
    print(f"\n===== W2 Web 宿主: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
