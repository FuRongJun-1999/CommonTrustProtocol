"""realtime 设备实路径验证：本地 mock Realtime 服务器（OpenAI schema 模拟）。

验证：session_start（握手/instructions）→ send_audio（帧推送）→
drain（事件缓冲：转写/文本/音频块）→ session_close 完整状态机。
"""

import json
import os
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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


def run_mock_server(port):
    """简易 WebSocket 服务器：响应 OpenAI Realtime 事件。"""
    import socket
    import base64 as b64

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", port))
    sock.listen(1)
    sock.settimeout(15)
    conn, _ = sock.accept()
    conn.settimeout(10)
    data = b""
    # 握手
    while b"\r\n\r\n" not in data:
        data += conn.recv(4096)
    key = ""
    for line in data.decode("latin1").split("\r\n"):
        if line.lower().startswith("sec-websocket-key:"):
            key = line.split(":", 1)[1].strip()
    import hashlib
    accept = b64.b64encode(hashlib.sha1(
        (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest()).decode()
    conn.sendall((
        "HTTP/1.1 101 Switching Protocols\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Accept: {accept}\r\n\r\n").encode())

    def send_json(obj):
        payload = json.dumps(obj).encode()
        length = len(payload)
        if length < 126:
            header = b"\x81" + bytes([length])
        elif length < 65536:
            header = b"\x81\x7e" + length.to_bytes(2, "big")
        else:
            header = b"\x81\x7f" + length.to_bytes(8, "big")
        conn.sendall(header + payload)  # 服务端帧：FIN+text，无掩码

    def recv_json():
        frame = conn.recv(4096)
        if len(frame) < 2:
            return None
        length = frame[1] & 0x7F
        offset = 2
        if length == 126:
            length = int.from_bytes(frame[2:4], "big"); offset = 4
        mask = frame[offset:offset + 4]; offset += 4
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(frame[offset:offset + length]))
        return json.loads(payload.decode())

    send_json({"type": "session.created", "session": {"id": "mock"}})
    while True:
        try:
            msg = recv_json()
        except Exception:
            break
        if msg is None:
            continue
        t = msg.get("type")
        if t == "session.update":
            send_json({"type": "session.updated"})
            # 模拟服务器 VAD 后回放：转写 + 文本 + 音频块
            send_json({"type": "conversation.item.input_audio_transcription.completed",
                       "transcript": "你好灵枢，这是模拟语音输入"})
            send_json({"type": "response.audio_transcript.delta", "delta": "你好，我在听。"})
            send_json({"type": "response.audio.delta", "delta": "QUJD"})
            send_json({"type": "response.done"})
        elif t == "input_audio_buffer.append":
            send_json({"type": "input_audio_buffer.committed"})
    conn.close()
    sock.close()


def main():
    import subprocess
    from aeis.api import Agent

    # 探测空闲端口并起 mock 服务器
    port = 18765
    t = threading.Thread(target=run_mock_server, args=(port,), daemon=True)
    t.start()
    time.sleep(0.5)

    ws = tempfile.mkdtemp()
    os.environ["AEIS_WORKSPACE"] = ws
    os.environ["OPENAI_REALTIME_URL"] = f"ws://127.0.0.1:{port}"
    os.environ.pop("OPENAI_API_KEY", None)   # 走本地端点免 key 路径
    a = Agent(identity="rt-mock", db_path=":memory:")

    # 1. session_start
    r = a.device_call("realtime", "session_start",
                      {"instructions": "你是灵枢，保持诚实。", "model": "mock-model"})
    check("session_start 就绪", r["ok"] is True and "session" in r["data"],
          f"err={(r.get('error') or '')[:50]}")
    # 2. send_audio（合法 base64）
    import base64 as b64
    frame = b64.b64encode(b"\x00" * 1600).decode()
    r2 = a.device_call("realtime", "send_audio", {"frame": frame})
    check("send_audio 帧推送", r2["ok"] is True and r2["data"]["bytes"] == 1600)
    # 非法 base64
    r3 = a.device_call("realtime", "send_audio", {"frame": "!!!not-base64!!!"})
    check("非法帧拦截", not r3["ok"] and "base64" in r3["error"])
    # 3. drain（事件缓冲：转写/文本/音频块）
    time.sleep(0.8)
    r4 = a.device_call("realtime", "drain", {"timeout": 1.0})
    check("drain 事件缓冲", r4["ok"] and r4["data"]["count"] >= 3,
          f"count={r4['data']['count']}")
    if r4["ok"] and r4["data"]["transcript"]:
        check("转写提取", "模拟语音输入" in r4["data"]["transcript"],
              r4["data"]["transcript"][:60])
    check("音频块计数", r4["ok"] and r4["data"]["audio_blocks"] >= 1)
    # 容器隔离
    check("realtime 容器隔离", r["provenance"] == "device:realtime" and r["is_directive"] is False)
    # 4. session_close
    r5 = a.device_call("realtime", "session_close", {})
    check("session_close", r5["ok"] and r5["data"]["sent"] >= 2,
          f"sent={r5['data'].get('sent')}")
    # 关闭后再发 → 拦截
    r6 = a.device_call("realtime", "send_audio", {"frame": frame})
    check("关闭后拦截", not r6["ok"])

    print(f"\n===== REALTIME 实路径验证: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
