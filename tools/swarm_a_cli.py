# Copyright 2026 灵枢 (Lingshu) · MIT
"""swarm_a_cli.py · 蜂群 A 节点接入器 CLI（2026-08-29 心跳）

ZCode 心跳/联调时以 nodeA 身份操作协议栈的命令行入口。
总线目录持久（--root 默认 data/swarm_bus），dsh 端 B 节点照
docs/T12_dsh端接入指南_v0.1.md 实现后即可对接同一目录。

用法（从项目根）：
    python tools/swarm_a_cli.py status                     # A 节点状态
    python tools/swarm_a_cli.py poll                       # 处理收件箱
    python tools/swarm_a_cli.py execute --peer nodeB --cap 求和 --input "[1,2,3]"
    python tools/swarm_a_cli.py sync --peer nodeB          # 知识增量同步
"""

from __future__ import annotations

import argparse
import json
import os
import sys

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "tools"))

from swarm_m1 import Bus, Node, ProtocolError  # noqa: E402
from swarm_m2_bridge import sync_knowledge, bind_memory  # noqa: E402


def build(root: str, node_id: str = "nodeA") -> Node:
    bus = Bus(root)
    node = Node(node_id, bus, ["校验"])
    return node


def main() -> None:
    ap = argparse.ArgumentParser(description="蜂群 A 节点接入器")
    ap.add_argument("--root", default=os.path.join(_PROJECT_ROOT, "data", "swarm_bus"),
                    help="总线目录（须与 B 节点一致）")
    ap.add_argument("--id", default="nodeA")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("poll")
    p_exec = sub.add_parser("execute")
    p_exec.add_argument("--peer", required=True)
    p_exec.add_argument("--cap", required=True)
    p_exec.add_argument("--input", required=True, help="JSON 字面量")
    p_exec.add_argument("--expect", required=True, help="JSON 字面量（A 侧验证基底期望值）")
    p_sync = sub.add_parser("sync")
    p_sync.add_argument("--peer", required=True)
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    node = build(args.root, args.id)

    if args.cmd == "status":
        info = {"id": node.id, "capabilities": node.capabilities,
                "peers": node.peers, "blindspots": node.blindspots,
                "adopted": len(node.adopted),
                "trust": {p: round(node.trust.score(p), 3) for p in node.trust.scores} or "（无记录，初始 0.5）"}
        print(json.dumps(info, ensure_ascii=False, indent=1))
    elif args.cmd == "poll":
        node.poll()
        for m in node.log:
            print(m["type"], m.get("reply_to", ""))
    elif args.cmd == "execute":
        expect = json.loads(args.expect)
        r = node.request_and_execute(
            args.peer, args.cap, json.loads(args.input),
            verifier=lambda o: (o == expect, f"A 基底期望 {expect}，B 报告 {o}"))
        print(json.dumps(r, ensure_ascii=False))
    elif args.cmd == "sync":
        # 同步需对端 agent——CLI 口径仅记录协议动作（完整双向走联调进程）
        print(json.dumps({"note": "完整双向同步需对端在线（B 侧 handle_bus_sync）",
                          "peer": args.peer, "root": args.root}, ensure_ascii=False))


if __name__ == "__main__":
    main()
