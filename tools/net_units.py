# -*- coding: utf-8 -*-
"""net_units.py · 蓝牙和互联网白箱单元库（第六阶段·目标7 初级复现）
用户设想：终极目标「蜂群连接网络」← 初级复现「蓝牙和互联网」。
网络核心：IP 分片/TCP 握手/UDP 校验/局域网发现/蜂群消息中继。
单元：{任务 → 代码模式模板 + 验证样例 + 校准基准}——白箱自举（外部只校准）。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

NET_UNITS = {
    "网络-IP分片": {
        "task": "IP分片",
        "pattern": (
            "def ip_fragment(packet_size, mtu):\n"
            "    # IP 分片：包大小 + MTU → 分片数（每片含 20B IP 头）\n"
            "    import math\n"
            "    if packet_size <= mtu:\n"
            "        return 1\n"
            "    payload = mtu - 20\n"
            "    return math.ceil(packet_size / payload)\n"),
        "cases": [((1000, 500), 3),
                  ((100, 500), 1),
                  ((500, 100), 7)],
        "params": [],
        "calibration": "对照：网络 IP——超过 MTU 需分片（每片 20B 头）",
    },
    "网络-TCP握手": {
        "task": "TCP握手",
        "pattern": (
            "def tcp_handshake(states):\n"
            "    # TCP 三次握手：CLOSED → SYN → SYN-ACK → ESTABLISHED\n"
            "    state = 'CLOSED'\n"
            "    for ev in states:\n"
            "        if state == 'CLOSED' and ev == 'SYN':\n"
            "            state = 'SYN_SENT'\n"
            "        elif state == 'SYN_SENT' and ev == 'SYN-ACK':\n"
            "            state = 'ESTABLISHED'\n"
            "    return state\n"),
        "cases": [((['SYN', 'SYN-ACK'],), 'ESTABLISHED'),
                  ((['SYN'],), 'SYN_SENT'),
                  (( [],), 'CLOSED')],
        "params": [],
        "calibration": "对照：网络 TCP——三次握手状态机（CLOSED→SYN_SENT→ESTABLISHED）",
    },
    "网络-校验和": {
        "task": "校验和",
        "pattern": (
            "def checksum(data):\n"
            "    # UDP 校验和（简化）：16 位和进位折叠 → 取反\n"
            "    total = 0\n"
            "    for b in data:\n"
            "        total += b\n"
            "        if total > 0xFFFF:\n"
            "            total = (total & 0xFFFF) + 1\n"
            "    return (~total) & 0xFFFF\n"),
        "cases": [((bytes([1, 2, 3, 4]),), (~10) & 0xFFFF),
                  ((bytes([]),), 0xFFFF),
                  ((bytes([0xFF, 0xFF]),), (~510) & 0xFFFF)],
        "params": [],
        "calibration": "对照：网络 UDP——校验和（和取反，接收端校验出错）",
    },
    "网络-局域网发现": {
        "task": "局域网发现",
        "pattern": (
            "def discover(devices, heartbeat_ttl=3):\n"
            "    # 局域网发现：设备表+心跳 → 在线设备（心跳超时剔除）\n"
            "    online = []\n"
            "    for dev in devices:\n"
            "        if dev.get('ttl', 0) > 0:\n"
            "            online.append(dev['name'])\n"
            "    return sorted(online)\n"),
        "cases": [(([{'name': 'A', 'ttl': 2}, {'name': 'B', 'ttl': 0}],), ['A']),
                  (([{'name': 'X', 'ttl': 1}],), ['X']),
                  (( [],), [])],
        "params": [],
        "calibration": "对照：局域网发现——设备心跳在线判定（TTL 超时离线）",
    },
    "网络-蜂群中继": {
        "task": "蜂群中继",
        "pattern": (
            "def swarm_relay(neighbors, source, message=None):\n"
            "    # 蜂群消息：源节点 → 邻居递归中继（seen 防回环）\n"
            "    delivered = set()\n"
            "    def relay(node, seen):\n"
            "        if node in seen:\n"
            "            return\n"
            "        seen.add(node)\n"
            "        delivered.add(node)\n"
            "        for nxt in neighbors.get(node, []):\n"
            "            relay(nxt, seen)\n"
            "    relay(source, set())\n"
            "    return sorted(delivered)\n"),
        "cases": [(({'A': ['B', 'C'], 'B': ['D'], 'C': []}, 'A'), ['A', 'B', 'C', 'D']),
                  (({'A': ['B'], 'B': ['A']}, 'A'), ['A', 'B']),
                  (({'A': []}, 'A'), ['A'])],
        "params": [],
        "calibration": "对照：蜂群网络——消息经邻居递归中继，seen 防回环（去中心化传播）",
    },
}


def route_net_unit(question):
    """任务识别（问题 → 网络单元）"""
    best, best_len = None, 0
    for uid, u in NET_UNITS.items():
        for kw in (u["task"], uid):
            if kw in question and len(kw) > best_len:
                best, best_len = uid, len(kw)
    return best


if __name__ == "__main__":
    print("=== 蓝牙和互联网白箱单元库（目标7 · 蜂群网络初级复现）===\n")
    for uid, u in NET_UNITS.items():
        print(f"[{uid}] 任务={u['task']} 样例数={len(u['cases'])}")
        print(f"    校准: {u['calibration']}")
    print(f"\n=== 判定 ===\n网络单元库: "
          f"{'✔ 5 单元就绪（IP/TCP/UDP/发现/蜂群中继）' if len(NET_UNITS) >= 4 else '✘'}")
