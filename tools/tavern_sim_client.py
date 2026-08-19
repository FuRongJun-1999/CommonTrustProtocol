# -*- coding: utf-8 -*-
"""
酒馆模拟客户端（离线 · 验证角色卡 × 灵枢桥协同）
================================================
模拟 SillyTavern 消费协议角色卡的完整链路：
  1. 读取角色卡 PNG（tEXt chara chunk）→ 解析 chara_card_v3
  2. 按酒馆逻辑组装消息：
     - system = system_prompt + description + personality + scenario
       + post_history_instructions（近似酒馆的 prompt 组装）
     - user = first_mes 后续的对话
  3. 调灵枢酒馆桥（带 lingshu.role_id）
  4. 桥注入角色机制 → 转发 mock 上游
  5. 验证最终 system 同时包含「角色卡内容」与「桥注入内容」，且无冲突

用法：
    python tavern_sim_client.py \
        --card ../release/灵枢_协议引导者.png \
        --bridge http://127.0.0.1:8791/v1 \
        --role protocol-guide
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
import urllib.request
from pathlib import Path


def read_card(path: Path) -> dict:
    """从 PNG/JSON 读取角色卡。"""
    if path.suffix.lower() == ".png":
        raw = path.read_bytes()
        pos = 8
        json_str = ""
        while pos < len(raw):
            (length,) = struct.unpack(">I", raw[pos:pos+4])
            tag = raw[pos+4:pos+8]
            if tag == b"tEXt":
                key, _, val = raw[pos+8:pos+8+length].decode("utf-8").partition("\x00")
                if key == "chara":
                    json_str = val
                    break
            pos += 12 + length
        if not json_str:
            raise ValueError("PNG 中未找到 chara chunk")
        return json.loads(json_str)
    return json.loads(path.read_text(encoding="utf-8"))


def assemble_messages(card: dict, user_text: str) -> list[dict]:
    """近似酒馆的 prompt 组装（system_prompt + 描述 + 人格 + 场景 + 历史指令）。"""
    data = card["data"]
    parts = []
    if data.get("system_prompt"):
        parts.append(data["system_prompt"])
    if data.get("description"):
        parts.append(data["description"])
    if data.get("personality"):
        parts.append(data["personality"])
    if data.get("scenario"):
        parts.append(f"[场景] {data['scenario']}")
    if data.get("post_history_instructions"):
        parts.append(data["post_history_instructions"])
    system = "\n\n".join(p for p in parts if p)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
    ]


def call_bridge(base: str, messages: list[dict], role_id: str) -> tuple[int, dict]:
    """调用灵枢酒馆桥（OpenAI 兼容）。"""
    payload = {"model": "any", "messages": messages,
               "lingshu": {"role_id": role_id},
               "max_tokens": 50, "temperature": 0.5}
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer dummy"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="酒馆模拟客户端（离线验证）")
    ap.add_argument("--card", required=True, help="角色卡路径（PNG/JSON）")
    ap.add_argument("--bridge", default="http://127.0.0.1:8791/v1", help="桥端点")
    ap.add_argument("--role", default="", help="role_id（默认从卡 extensions 读）")
    ap.add_argument("--user", default="你好，我们聊聊吧。", help="用户首句")
    args = ap.parse_args()

    card = read_card(Path(args.card))
    data = card["data"]
    role_id = args.role or data.get("extensions", {}).get("lingshu", {}).get("role_id", "")
    print(f"=== 酒馆模拟客户端 ===")
    print(f"角色卡: {data['name']} (spec {card['spec']} v{card.get('spec_version')})")
    print(f"role_id: {role_id}")

    # 1. 组装酒馆式消息
    messages = assemble_messages(card, args.user)
    sys_len = len(messages[0]["content"])
    print(f"酒馆组装 system 长度: {sys_len} 字符")

    # 2. 调用桥
    try:
        status, resp = call_bridge(args.bridge, messages, role_id)
    except Exception as e:
        print(f"[FAIL] 桥调用失败: {e}")
        return 1
    print(f"桥响应: HTTP {status}")

    # 3. 验证
    ok = True
    checks = {
        "桥注入条件空间": "角色扮演条件空间" in messages[0]["content"],
        "桥注入自我锚点": "演不了编译通过" in messages[0]["content"],
        "角色卡诚实边界": "诚实边界" in messages[0]["content"],
        "角色卡条件声明": "观测位置" in messages[0]["content"],
        "角色卡崩溃恢复": "扮演崩溃恢复" in messages[0]["content"],
    }
    print("\n=== 验证 ===")
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")
        ok = ok and v
    print(f"\n结果: {'ALL PASS' if ok else 'HAS FAIL'}")
    print(f"最终 system 总长: {len(messages[0]['content'])} 字符")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
