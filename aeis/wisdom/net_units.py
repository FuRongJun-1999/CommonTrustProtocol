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
    "蜂群-消息去重": {
        "task": "消息去重",
        "pattern": (
            "def dedup(messages, seen_ids):\n"
            "    # 蜂群消息去重：已见 ID 跳过，新 ID 投递（防重复传播）\n"
            "    new = []\n"
            "    for msg in messages:\n"
            "        if msg['id'] not in seen_ids:\n"
            "            seen_ids.add(msg['id'])\n"
            "            new.append(msg)\n"
            "    return new\n"),
        "cases": [(([{'id': 1}, {'id': 1}, {'id': 2}], set()),
                   [{'id': 1}, {'id': 2}]),
                  (([{'id': 1}], {1}), [])],
        "params": [],
        "calibration": "对照：蜂群协议——消息 ID 去重（多路径重复投递只处理一次）",
    },
    "蜂群-路由表": {
        "task": "路由表",
        "pattern": (
            "def route_table_update(table, node, next_hop):\n"
            "    # 路由表：节点 → 下一跳 维护（更新/查询）\n"
            "    if next_hop is not None:\n"
            "        table[node] = next_hop\n"
            "    return table.get(node)\n"),
        "cases": [(({}, 'A', 'B'), 'B'),
                  (({'A': 'B'}, 'A', None), 'B'),
                  (({'A': 'B'}, 'C', 'D'), 'D')],
        "params": [],
        "calibration": "对照：网络路由表——节点→下一跳（更新与查询）",
    },
    "蜂群-超时重传": {
        "task": "超时重传",
        "pattern": (
            "def retransmit(packets, ack_ids, max_tries=3):\n"
            "    # 蜂群可靠传输：未确认包超时重传（超过重试上限放弃）\n"
            "    need = []\n"
            "    for p in packets:\n"
            "        if p['id'] in ack_ids:\n"
            "            continue\n"
            "        if p.get('tries', 0) >= max_tries:\n"
            "            continue\n"
            "        p['tries'] = p.get('tries', 0) + 1\n"
            "        need.append(p['id'])\n"
            "    return need\n"),
        "cases": [(([{'id': 1, 'tries': 0}, {'id': 2, 'tries': 3}], {2}), [1]),
                  (([{'id': 1, 'tries': 0}], set()), [1]),
                  (([{'id': 1, 'tries': 0}], {1}), [])],
        "params": [],
        "calibration": "对照：可靠传输——未确认包重传，超重试上限放弃（TCP 重传语义）",
    },
    "网络-停等协议": {
        "task": "停等协议",
        "pattern": (
            "def stop_and_wait(send_packets, ack_all=True):\n"
            "    # 停等协议：发送→等确认→再发下一个（ack_all=False 首包后停止）\n"
            "    sent = []\n"
            "    for p in send_packets:\n"
            "        sent.append(p)\n"
            "        if not ack_all:\n"
            "            break\n"
            "    return sent\n"),
        "cases": [(([1, 2, 3], True), [1, 2, 3]),
                  (([1, 2], False), [1]),
                  (( [], True), [])],
        "params": [],
        "calibration": "对照：网络可靠传输——停等协议（逐包确认后再发下一包）",
    },
    "蜂群-消息分帧": {
        "task": "消息分帧",
        "pattern": (
            "def frame_decode(buf, delim=b'\\r\\n'):\n"
            "    # 蜂群会话层：字节流按分隔符分帧（粘包/半包处理）\n"
            "    frames = []\n"
            "    while True:\n"
            "        idx = buf.find(delim)\n"
            "        if idx < 0:\n"
            "            break\n"
            "        frames.append(buf[:idx])\n"
            "        buf = buf[idx + len(delim):]\n"
            "    return frames, buf\n"),
        "cases": [((b'hi\r\nhello\r\n',), ([b'hi', b'hello'], b'')),
                  ((b'partial',), ([], b'partial')),
                  ((b'a\r\nb\r\nc',), ([b'a', b'b'], b'c'))],
        "params": [],
        "calibration": "对照：会话层——字节流分帧（粘包拆帧、半包留待下段）",
    },
    "蜂群-会话状态": {
        "task": "会话状态",
        "pattern": (
            "def session_step(session, event):\n"
            "    # 蜂群会话状态机：LISTEN→SYN_SENT→ESTABLISHED（确认）→CLOSED（结束）\n"
            "    s = session.get('state', 'LISTEN')\n"
            "    if s == 'LISTEN' and event == 'SYN':\n"
            "        return 'SYN_SENT'\n"
            "    if s == 'SYN_SENT' and event == 'ACK':\n"
            "        return 'ESTABLISHED'\n"
            "    if s == 'ESTABLISHED' and event == 'FIN':\n"
            "        return 'CLOSED'\n"
            "    return s\n"),
        "cases": [(({'state': 'LISTEN'}, 'SYN'), 'SYN_SENT'),
                  (({'state': 'SYN_SENT'}, 'ACK'), 'ESTABLISHED'),
                  (({'state': 'ESTABLISHED'}, 'FIN'), 'CLOSED'),
                  (({'state': 'LISTEN'}, 'ACK'), 'LISTEN')],
        "params": [],
        "calibration": "对照：会话层——连接状态机（同步→确认→建立→关闭；非法事件不迁移）",
    },
    "网络-滑动窗口": {
        "task": "滑动窗口",
        "pattern": (
            "def sliding_window(base, next_seq, window_size, ack):\n"
            "    # TCP 滑动窗口：收到 ack 后窗口前移（可发送序号 = [next_seq, base+win)）\n"
            "    # base=已确认序号 next_seq=下一待发 ack=收到的确认\n"
            "    if ack > base:\n"
            "        base = ack\n"
            "    if next_seq < base:\n"
            "        next_seq = base\n"
            "    return {'base': base, 'next_seq': next_seq,\n"
            "            'window': [base + i for i in range(window_size)]}\n"),
        "cases": [((0, 0, 3, 2), {'base': 2, 'next_seq': 2,
                                  'window': [2, 3, 4]}),
                  ((2, 2, 3, 5), {'base': 5, 'next_seq': 5,
                                  'window': [5, 6, 7]}),
                  ((0, 1, 2, 0), {'base': 0, 'next_seq': 1,
                                  'window': [0, 1]})],
        "params": [],
        "calibration": "对照：TCP 可靠传输——滑动窗口（ACK 确认后窗口前移，窗口内可发送）",
    },
    "网络-累积确认": {
        "task": "累积确认",
        "pattern": (
            "def cum_ack(received, seq):\n"
            "    # TCP 累积确认：收到乱序包不确认，连续序列推进 ack（收到 3 则 1,2,3 都确认）\n"
            "    received.add(seq)\n"
            "    ack = 0\n"
            "    while ack + 1 in received:\n"
            "        ack += 1\n"
            "    return ack\n"),
        "cases": [(({1, 2}, 3), 3),
                  (({1, 3}, 2), 3),
                  ((set(), 1), 1),
                  (({2, 3}, 1), 3)],
        "params": [],
        "calibration": "对照：TCP 接收端——累积确认（连续序号推进 ACK；乱序只确认连续前缀）",
    },
    "网络-拥塞控制": {
        "task": "拥塞控制",
        "pattern": (
            "def slow_start(cwnd, ssthresh, acked, lost):\n"
            "    # TCP 拥塞控制：慢启动（cwnd 每 RTT 翻倍）→ 阈值后拥塞避免（线性+1）\n"
            "    # cwnd=拥塞窗口 ssthresh=慢启动阈值 acked=本 RTT 确认数 lost=是否丢包\n"
            "    if lost:\n"
            "        ssthresh = max(cwnd // 2, 1)\n"
            "        cwnd = 1\n"
            "        return {'cwnd': cwnd, 'ssthresh': ssthresh}\n"
            "    if cwnd < ssthresh:\n"
            "        return {'cwnd': min(cwnd + acked, ssthresh), 'ssthresh': ssthresh}\n"
            "    return {'cwnd': cwnd + 1, 'ssthresh': ssthresh}\n"),
        "cases": [((1, 8, 2, False), {'cwnd': 3, 'ssthresh': 8}),
                  ((4, 8, 4, False), {'cwnd': 8, 'ssthresh': 8}),
                  ((8, 8, 8, False), {'cwnd': 9, 'ssthresh': 8}),
                  ((8, 8, 0, True), {'cwnd': 1, 'ssthresh': 4})],
        "params": [],
        "calibration": "对照：TCP 拥塞控制——慢启动指数增长→阈值后线性+1；丢包减半阈值+重置窗口",
    },
    "网络-CIDR": {
        "task": "CIDR子网",
        "pattern": (
            "def cidr_network(ip, prefix):\n"
            "    # IP 子网计算：IP + 前缀长度 → 网络地址/广播地址/主机数\n"
            "    parts = [int(x) for x in ip.split('.')]\n"
            "    mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF\n"
            "    ip_int = (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]\n"
            "    net_int = ip_int & mask_int\n"
            "    bcast_int = net_int | (~mask_int & 0xFFFFFFFF)\n"
            "    def to_ip(v):\n"
            "        return '.'.join(str((v >> s) & 0xFF) for s in (24, 16, 8, 0))\n"
            "    return {'network': to_ip(net_int), 'broadcast': to_ip(bcast_int),\n"
            "            'hosts': max(0, (1 << (32 - prefix)) - 2)}\n"),
        "cases": [(('192.168.1.130', 24),
                   {'network': '192.168.1.0', 'broadcast': '192.168.1.255',
                    'hosts': 254}),
                  (('10.0.0.5', 8),
                   {'network': '10.0.0.0', 'broadcast': '10.255.255.255',
                    'hosts': 16777214})],
        "params": [],
        "calibration": "对照：网络 IP——CIDR 子网计算（/24 网络地址+广播地址+可用主机数）",
    },
    "网络-距离矢量": {
        "task": "距离矢量",
        "pattern": (
            "def distance_vector(routes, neighbor, neighbor_routes):\n"
            "    # 距离矢量路由（RIP）：收到邻居路由表 → 合并（距离+1，取最短）\n"
            "    for dst, dist in neighbor_routes.items():\n"
            "        nd = dist + 1\n"
            "        if dst not in routes or nd < routes[dst]:\n"
            "            routes[dst] = nd\n"
            "    return dict(routes)\n"),
        "cases": [(({'A': 0, 'B': 1}, 'C', {'A': 2, 'D': 1}),
                   {'A': 0, 'B': 1, 'D': 2}),
                  (({'A': 0}, 'B', {'A': 5, 'C': 1}),
                   {'A': 0, 'C': 2})],
        "params": [],
        "calibration": "对照：网络路由——距离矢量（邻居路由表合并，距离+1 取最短——RIP 语义）",
    },
    "网络-NAT": {
        "task": "NAT转换",
        "pattern": (
            "def nat_translate(table, src_ip, src_port, pub_ip):\n"
            "    # NAT：内网地址→公网地址（端口映射表；已映射复用端口）\n"
            "    key = (src_ip, src_port)\n"
            "    if key in table:\n"
            "        return table[key]\n"
            "    pub_port = len(table) + 1024  # 分配新公网端口\n"
            "    table[key] = (pub_ip, pub_port)\n"
            "    return table[key]\n"),
        "cases": [(({}, '192.168.1.10', 5000, '8.8.8.8'),
                   ('8.8.8.8', 1024)),
                  (({('192.168.1.10', 5000): ('8.8.8.8', 1024)},
                    '192.168.1.10', 5000, '8.8.8.8'),
                   ('8.8.8.8', 1024)),
                  (({('192.168.1.10', 5000): ('8.8.8.8', 1024)},
                    '192.168.1.11', 5000, '8.8.8.8'),
                   ('8.8.8.8', 1025))],
        "params": [],
        "calibration": "对照：网络 NAT——内网→公网地址转换（端口映射表，复用已映射端口）",
    },
    "网络-DNS解析": {
        "task": "DNS解析",
        "pattern": (
            "def dns_resolve(cache, domain):\n"
            "    # DNS 解析：域名→IP（缓存命中直返；未命中模拟查询 8.8.8.8）\n"
            "    if domain in cache:\n"
            "        return cache[domain], 'cache'\n"
            "    ip = '8.8.8.8'\n"
            "    cache[domain] = ip\n"
            "    return ip, 'query'\n"),
        "cases": [(({'a.com': '1.1.1.1'}, 'a.com'), ('1.1.1.1', 'cache')),
                  (({}, 'b.com'), ('8.8.8.8', 'query')),
                  (({'a.com': '1.1.1.1'}, 'b.com'), ('8.8.8.8', 'query'))],
        "params": [],
        "calibration": "对照：DNS——域名解析（缓存命中直返/未命中查询，缓存加速语义）",
    },
    "网络-HTTP状态码": {
        "task": "HTTP状态码",
        "pattern": (
            "def http_status_class(code):\n"
            "    # HTTP 状态码分类：2xx 成功/3xx 重定向/4xx 客户端错/5xx 服务端错\n"
            "    if 200 <= code < 300:\n"
            "        return '成功'\n"
            "    if 300 <= code < 400:\n"
            "        return '重定向'\n"
            "    if 400 <= code < 500:\n"
            "        return '客户端错误'\n"
            "    if 500 <= code < 600:\n"
            "        return '服务端错误'\n"
            "    return '未知'\n"),
        "cases": [((200,), '成功'), ((301,), '重定向'),
                  ((404,), '客户端错误'), ((500,), '服务端错误')],
        "params": [],
        "calibration": "对照：HTTP 状态码分类（RFC 9110：2xx/3xx/4xx/5xx）",
    },
    "网络-负载均衡": {
        "task": "负载均衡",
        "pattern": (
            "def load_balance(servers, request_id):\n"
            "    # 负载均衡：轮询调度（请求 → 服务器轮转分配）\n"
            "    if not servers:\n"
            "        return None\n"
            "    return servers[request_id % len(servers)]\n"),
        "cases": [((['s1', 's2', 's3'], 0), 's1'),
                  ((['s1', 's2', 's3'], 4), 's2'),
                  (([], 0), None)],
        "params": [],
        "calibration": "对照：网络负载均衡——轮询调度（请求均匀分布到服务器）",
    },
    "网络-WebSocket握手": {
        "task": "WebSocket握手",
        "pattern": (
            "def ws_handshake(headers):\n"
            "    # WebSocket 握手：HTTP Upgrade: websocket → 101 切换协议\n"
            "    upgrade = headers.get('Upgrade', '').lower()\n"
            "    key_ok = 'Sec-WebSocket-Key' in headers\n"
            "    if upgrade == 'websocket' and key_ok:\n"
            "        return 101, 'Switching Protocols'\n"
            "    return 400, 'Bad Request'\n"),
        "cases": [(({'Upgrade': 'websocket', 'Sec-WebSocket-Key': 'k'},),
                   (101, 'Switching Protocols')),
                  (({'Upgrade': 'http'},), (400, 'Bad Request')),
                  (({},), (400, 'Bad Request'))],
        "params": [],
        "calibration": "对照：WebSocket——HTTP Upgrade 握手（RFC 6455：101 切换协议/400 拒绝）",
    },
    "网络-帧封装": {
        "task": "帧封装",
        "pattern": (
            "def ws_frame(opcode, payload):\n"
            "    # WebSocket 帧：首字节(FIN+opcode) + 长度 + 负载（RFC 6455 简化）\n"
            "    fin_opcode = 0x80 | opcode   # FIN=1 + 4bit opcode\n"
            "    n = len(payload)\n"
            "    if n < 126:\n"
            "        return bytes([fin_opcode, n]) + payload\n"
            "    return bytes([fin_opcode, 126, (n >> 8) & 0xFF, n & 0xFF]) + payload\n"),
        "cases": [((1, b'hi'), b'\x81\x02hi'),
                  ((2, b'hello'), b'\x82\x05hello'),
                  ((1, b'x' * 130), bytes([0x81, 126, 0, 130]) + b'x' * 130)],
        "params": [],
        "calibration": "对照：WebSocket 帧——FIN+opcode+长度+负载（RFC 6455 帧格式）",
    },
    "网络-流式传输": {
        "task": "流式传输",
        "pattern": (
            "def chunked_encode(data, size=4):\n"
            "    # 流式分块传输：数据切块 + 长度前缀（HTTP chunked 语义）\n"
            "    out = []\n"
            "    for i in range(0, len(data), size):\n"
            "        chunk = data[i:i + size]\n"
            "        out.append(f'{len(chunk):X}\\r\\n' + chunk.decode('utf-8', 'ignore') + '\\r\\n')\n"
            "    out.append('0\\r\\n\\r\\n')\n"
            "    return ''.join(out)\n"),
        "cases": [((b'abcdef', 4), '4\r\nabcd\r\n2\r\nef\r\n0\r\n\r\n'),
                  ((b'', 4), '0\r\n\r\n')],
        "params": [],
        "calibration": "对照：HTTP 流式传输——chunked 编码（分块+长度前缀+终止块）",
    },
    "网络-多路复用": {
        "task": "多路复用",
        "pattern": (
            "def stream_mux(streams):\n"
            "    # HTTP/2 多路复用：多流帧交错（流 ID + 数据 → 单连接混合帧）\n"
            "    frames = []\n"
            "    for sid, data in streams:\n"
            "        frames.append((sid, data))\n"
            "    return frames\n"),
        "cases": [(([(1, 'a'), (3, 'b'), (5, 'c')],),
                   [(1, 'a'), (3, 'b'), (5, 'c')]),
                  (([],), [])],
        "params": [],
        "calibration": "对照：HTTP/2 多路复用——单连接多流帧交错（流 ID 区分）",
    },
    "网络-连接池": {
        "task": "连接池",
        "pattern": (
            "def conn_pool(pool, op, host=None):\n"
            "    # 连接池：获取复用/归还/新建（上限控制，避免频繁建连）\n"
            "    if op == 'get':\n"
            "        if pool.get(host):\n"
            "            return pool[host].pop()\n"
            "        return 'new'\n"
            "    if op == 'put':\n"
            "        pool.setdefault(host, []).append(1)\n"
            "        return len(pool[host])\n"
            "    return None\n"),
        "cases": [(({'a.com': [1]}, 'get', 'a.com'), 1),
                  (({}, 'get', 'a.com'), 'new'),
                  (({}, 'put', 'a.com'), 1)],
        "params": [],
        "calibration": "对照：网络连接池——获取复用/归还（空闲复用，避免重复建连）",
    },
    "网络-QUIC握手": {
        "task": "QUIC握手",
        "pattern": (
            "def quic_handshake(cache, client):\n"
            "    # QUIC：0-RTT 快速握手（缓存会话 → 首次往返即发数据）\n"
            "    if client in cache:\n"
            "        return '0-RTT', cache[client]\n"
            "    cache[client] = 'ticket'\n"
            "    return '1-RTT', 'ticket'\n"),
        "cases": [(({}, 'c1'), ('1-RTT', 'ticket')),
                  (({'c1': 'ticket'}, 'c1'), ('0-RTT', 'ticket'))],
        "params": [],
        "calibration": "对照：QUIC——0-RTT 快速握手（缓存会话票据，二次连接免往返）",
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
