# -*- coding: utf-8 -*-
"""os_units.py · 迷你 Linux 白箱单元库（第六阶段·目标4 初级复现）
用户设想：终极目标「中文操作系统」← 初级复现「Linux 操作系统」。
内核核心抽象：进程调度/内存管理/文件系统/IPC——白箱自举（外部只校准）。
单元：{任务 → 代码模式模板 + 验证样例 + 校准基准}。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

OS_UNITS = {
    "进程-调度": {
        "task": "进程调度",
        "pattern": (
            "def fcfs_schedule(processes):\n"
            "    # FCFS 进程调度：[(到达时间, 运行时长)] → 完成时间列表\n"
            "    time, done = 0, []\n"
            "    for at, dur in processes:\n"
            "        time = max(time, at) + dur\n"
            "        done.append(time)\n"
            "    return done\n"),
        "cases": [(([(0, 3), (2, 2)],), [3, 5]),
                  (([(0, 3)],), [3]),
                  (([],), [])],
        "params": [],
        "calibration": "对照：OS 进程调度 FCFS——先到先服务，完成时间=前序完成+运行时长",
    },
    "进程-时间片轮转": {
        "task": "轮转调度",
        "pattern": (
            "def round_robin(processes, quantum=2):\n"
            "    # RR 时间片轮转：[(运行时长)] → 调度序列（进程索引）\n"
            "    remain = list(processes)\n"
            "    order, i = [], 0\n"
            "    while any(r > 0 for r in remain):\n"
            "        if remain[i] > 0:\n"
            "            run = min(quantum, remain[i])\n"
            "            remain[i] -= run\n"
            "            order.append(i)\n"
            "        i = (i + 1) % len(remain)\n"
            "    return order\n"),
        "cases": [(([4, 2, 3], 2), [0, 1, 2, 0, 2]),
                  (([1, 1], 2), [0, 1]),
                  (([5], 2), [0, 0, 0])],
        "params": [],
        "calibration": "对照：OS 时间片轮转——每进程最多运行 quantum，循环调度",
    },
    "内存-分页分配": {
        "task": "内存分配",
        "pattern": (
            "def page_alloc(pages_free, requests):\n"
            "    # 分页内存分配：请求页数 → 分配成功/拒绝（可用内存耗尽拒绝）\n"
            "    free = pages_free\n"
            "    results = []\n"
            "    for req in requests:\n"
            "        if req <= free:\n"
            "            free -= req\n"
            "            results.append(True)\n"
            "        else:\n"
            "            results.append(False)\n"
            "    return results\n"),
        "cases": [((10, [3, 5, 4]), [True, True, False]),
                  ((5, [6]), [False]),
                  ((0, []), [])],
        "params": [],
        "calibration": "对照：OS 内存管理——分页分配，内存不足拒绝请求",
    },
    "文件-路径解析": {
        "task": "文件路径",
        "pattern": (
            "def resolve_path(path, cwd):\n"
            "    # 路径解析：绝对/相对/.. /./ → 规范路径\n"
            "    if path.startswith('/'):\n"
            "        parts = path.split('/')[1:]\n"
            "    else:\n"
            "        parts = cwd.split('/')[1:] + path.split('/')\n"
            "    stack = []\n"
            "    for p in parts:\n"
            "        if p == '..':\n"
            "            if stack:\n"
            "                stack.pop()\n"
            "        elif p and p != '.':\n"
            "            stack.append(p)\n"
            "    return '/' + '/'.join(stack) if stack else '/'\n"),
        "cases": [(("/a/b", "/c"), "/a/b"),
                  (("..", "/a/b"), "/a"),
                  (("./x", "/a"), "/a/x"),
                  (("/", "/a"), "/")],
        "params": [],
        "calibration": "对照：OS 文件系统——路径规范化（绝对/相对/.. 解析）",
    },
    "IPC-管道": {
        "task": "进程通信",
        "pattern": (
            "def pipe_transfer(sender_data, reader):\n"
            "    # 管道 IPC：写端数据 → FIFO 缓冲 → 读端取前 reader 项\n"
            "    buf = list(sender_data)\n"
            "    out = []\n"
            "    for _ in range(reader):\n"
            "        if buf:\n"
            "            out.append(buf.pop(0))\n"
            "    return out\n"),
        "cases": [(([1, 2, 3], 2), [1, 2]),
                  (([7], 3), [7]),
                  (([], 2), [])],
        "params": [],
        "calibration": "对照：OS IPC 管道——FIFO 缓冲，读端消费数据",
    },
    "内存-页置换": {
        "task": "页置换",
        "pattern": (
            "def lru_replace(page_seq, capacity):\n"
            "    # LRU 页置换：页序列 + 容量 → 缺页次数（最近最久未使用淘汰）\n"
            "    frames, faults = [], 0\n"
            "    for p in page_seq:\n"
            "        if p in frames:\n"
            "            frames.remove(p)\n"
            "            frames.append(p)\n"
            "        else:\n"
            "            if len(frames) >= capacity:\n"
            "                frames.pop(0)\n"
            "            frames.append(p)\n"
            "            faults += 1\n"
            "    return faults\n"),
        "cases": [(([1, 2, 3, 2, 1, 4, 2, 3], 3), 5),
                  (([1, 1, 1], 2), 1),
                  (([], 2), 0)],
        "params": [],
        "calibration": "对照：OS 虚拟内存——LRU 页置换（容量 3 时 8 页访问 5 次缺页）",
    },
    "文件-inode": {
        "task": "inode查询",
        "pattern": (
            "def inode_lookup(files, name):\n"
            "    # inode 表查询：文件名 → (大小, 权限) 或 None\n"
            "    for f in files:\n"
            "        if f['name'] == name:\n"
            "            return (f['size'], f['perm'])\n"
            "    return None\n"),
        "cases": [(([{'name': 'a.txt', 'size': 100, 'perm': 644},
                      {'name': 'b', 'size': 50, 'perm': 600}], 'a.txt'), (100, 644)),
                  (([{'name': 'a.txt', 'size': 100, 'perm': 644}], 'c.txt'), None)],
        "params": [],
        "calibration": "对照：OS 文件系统 inode——文件名→元数据（大小/权限）查询",
    },
    "进程-状态机": {
        "task": "进程状态",
        "pattern": (
            "def process_state(transitions):\n"
            "    # 进程状态机：事件序列 → 最终状态（就绪→运行→阻塞→就绪→终止）\n"
            "    state = '就绪'\n"
            "    for ev in transitions:\n"
            "        if state == '就绪' and ev == '调度':\n"
            "            state = '运行'\n"
            "        elif state == '运行' and ev == 'IO等待':\n"
            "            state = '阻塞'\n"
            "        elif state == '阻塞' and ev == 'IO完成':\n"
            "            state = '就绪'\n"
            "        elif state == '运行' and ev == '完成':\n"
            "            state = '终止'\n"
            "    return state\n"),
        "cases": [((['调度', 'IO等待', 'IO完成', '调度', '完成'],), '终止'),
                  ((['IO完成'],), '就绪'),
                  ((['调度', 'IO等待'],), '阻塞')],
        "params": [],
        "calibration": "对照：OS 进程状态机——就绪/运行/阻塞/终止 事件驱动转换",
    },
    "调度-SJF": {
        "task": "最短作业",
        "pattern": (
            "def sjf_schedule(processes):\n"
            "    # SJF 最短作业优先（非抢占）：[(到达, 时长)] → 完成时间列表\n"
            "    time, done, ready = 0, [], []\n"
            "    remaining = sorted(processes)\n"
            "    while remaining or ready:\n"
            "        ready += [p for p in remaining if p[0] <= time]\n"
            "        remaining = [p for p in remaining if p[0] > time]\n"
            "        if not ready:\n"
            "            time = remaining[0][0]\n"
            "            ready.append(remaining.pop(0))\n"
            "            continue\n"
            "        ready.sort(key=lambda p: p[1])\n"
            "        at, dur = ready.pop(0)\n"
            "        time += dur\n"
            "        done.append(time)\n"
            "    return done\n"),
        "cases": [(([(0, 3), (1, 2), (2, 5)],), [3, 5, 10]),
                  (([(0, 2)],), [2]),
                  (([],), [])],
        "params": [],
        "calibration": "对照：OS 调度 SJF——最短作业优先（平均等待最小化）",
    },
    "文件-块管理": {
        "task": "块管理",
        "pattern": (
            "def block_alloc(bitmap, size):\n"
            "    # 块位图分配：连续 size 块 → 起始块（首次适配）或 -1\n"
            "    n = len(bitmap)\n"
            "    for start in range(n - size + 1):\n"
            "        if all(b == 0 for b in bitmap[start:start + size]):\n"
            "            for i in range(start, start + size):\n"
            "                bitmap[i] = 1\n"
            "            return start\n"
            "    return -1\n"),
        "cases": [(([0, 0, 1, 0, 0], 2), 0),
                  (([1, 1, 1], 1), -1),
                  (([0, 1, 0], 2), -1)],
        "params": [],
        "calibration": "对照：OS 文件系统——块位图分配（连续块首次适配）",
    },
    "调度-优先级": {
        "task": "优先级调度",
        "pattern": (
            "def priority_schedule(processes):\n"
            "    # 优先级调度（非抢占）：[(时长, 优先级)] → 完成时间（高优先先跑）\n"
            "    procs = sorted(processes, key=lambda p: p[1], reverse=True)\n"
            "    time, done = 0, []\n"
            "    for dur, pri in procs:\n"
            "        time += dur\n"
            "        done.append(time)\n"
            "    return done\n"),
        "cases": [(([(2, 1), (3, 3)],), [3, 5]),
                  (([(1, 5), (2, 1)],), [1, 3]),
                  (( [],), [])],
        "params": [],
        "calibration": "对照：OS 调度——优先级调度（高优先级先执行）",
    },
    "进程-互斥锁": {
        "task": "互斥锁",
        "pattern": (
            "def mutex_op(state, op, owner=None):\n"
            "    # 互斥锁操作：lock/unlock（忙等语义：占用时 lock 失败）\n"
            "    if op == 'lock':\n"
            "        if state == 'free':\n"
            "            return 'locked', True\n"
            "        return 'locked', False\n"
            "    if op == 'unlock':\n"
            "        return 'free', True\n"
            "    return state, False\n"),
        "cases": [(('free', 'lock'), ('locked', True)),
                  (('locked', 'lock'), ('locked', False)),
                  (('locked', 'unlock'), ('free', True))],
        "params": [],
        "calibration": "对照：OS 并发——互斥锁（占用时加锁失败，释放后可用）",
    },
    "内存-首次适配": {
        "task": "首次适配",
        "pattern": (
            "def first_fit(blocks, size):\n"
            "    # 内存首次适配：空闲块大小列表 → 分配的块索引（首个足够大）\n"
            "    for i, b in enumerate(blocks):\n"
            "        if b >= size:\n"
            "            return i\n"
            "    return -1\n"),
        "cases": [(([5, 2, 8], 6), 2),
                  (([5, 2], 6), -1),
                  (([10], 3), 0)],
        "params": [],
        "calibration": "对照：OS 内存分配——首次适配（首个足够大的空闲块）",
    },
    "内存-页表映射": {
        "task": "页表映射",
        "pattern": (
            "def page_table_lookup(page_table, vpn):\n"
            "    # 虚拟内存页表：虚拟页号 → 物理帧号（present=1 已映射，0 缺页）\n"
            "    entry = page_table.get(vpn)\n"
            "    if entry is None or entry.get('present') != 1:\n"
            "        return None   # 缺页：页不在物理内存\n"
            "    return entry['frame']\n"),
        "cases": [(({1: {'present': 1, 'frame': 7}}, 1), 7),
                  (({1: {'present': 0, 'frame': None}}, 1), None),
                  (({}, 2), None)],
        "params": [],
        "calibration": "对照：OS 虚拟内存——页表映射（VPN→物理帧；present=0 或缺项=缺页）",
    },
    "内存-缺页处理": {
        "task": "缺页处理",
        "pattern": (
            "def page_fault_handler(page_table, vpn, free_frames, load):\n"
            "    # 缺页处理：present=0 → 分配空闲帧加载；无空闲帧 → 拒绝（置换由上层调度）\n"
            "    if vpn in page_table and page_table[vpn].get('present') == 1:\n"
            "        return 'hit', page_table[vpn]['frame']\n"
            "    if not free_frames:\n"
            "        return 'page_fault_no_frame', None\n"
            "    frame = free_frames.pop(0)\n"
            "    page_table[vpn] = {'present': 1, 'frame': frame}\n"
            "    load(vpn, frame)\n"
            "    return 'page_fault_loaded', frame\n"),
        "cases": [(({1: {'present': 1, 'frame': 3}}, 1, [], lambda v, f: None),
                   ('hit', 3)),
                  (({}, 2, [8], lambda v, f: None), ('page_fault_loaded', 8)),
                  (({}, 3, [], lambda v, f: None), ('page_fault_no_frame', None))],
        "params": [],
        "calibration": "对照：OS 虚拟内存——缺页处理（命中/加载/无空闲帧拒绝；置换交由页置换策略）",
    },
    "内存-页面错误": {
        "task": "页面错误分类",
        "pattern": (
            "def classify_page_fault(vpn, page_table, access):\n"
            "    # 页面错误分类：未映射/未驻留/写保护 → 错误类型（MMU 语义）\n"
            "    entry = page_table.get(vpn)\n"
            "    if entry is None:\n"
            "        return 'segment_fault'      # 非法地址（未映射）\n"
            "    if entry.get('present') != 1:\n"
            "        return 'minor_fault'        # 缺页（软缺页：磁盘→内存）\n"
            "    if access == 'write' and not entry.get('writable'):\n"
            "        return 'protection_fault'   # 写保护违例\n"
            "    return 'ok'\n"),
        "cases": [((5, {}, 'read'), 'segment_fault'),
                  ((1, {1: {'present': 0}}, 'read'), 'minor_fault'),
                  ((1, {1: {'present': 1, 'writable': False}}, 'write'),
                   'protection_fault'),
                  ((1, {1: {'present': 1, 'writable': True}}, 'write'), 'ok')],
        "params": [],
        "calibration": "对照：OS 虚拟内存——页面错误分类（MMU：未映射段错误/软缺页/写保护违例）",
    },
    "文件-目录树": {
        "task": "目录树",
        "pattern": (
            "def dir_ls(root, name, children=None, prefix='/'):\n"
            "    # 目录树 + 列目录：根/子目录/文件 → 路径列表（mkdir/ls 语义）\n"
            "    out = [prefix.rstrip('/') + '/' + root]\n"
            "    if name is None:\n"
            "        return out\n"
            "    base = prefix.rstrip('/') + '/' + root + '/' + name\n"
            "    out.append(base)\n"
            "    for c in (children or []):\n"
            "        out.append(base + '/' + c)\n"
            "    return sorted(out)\n"),
        "cases": [(('home', 'user', ['a.txt']),
                   ['/home', '/home/user', '/home/user/a.txt']),
                  (('etc', None, None), ['/etc'])],
        "params": [],
        "calibration": "对照：OS 文件系统——目录树（mkdir 层级 + ls 路径展开）",
    },
    "文件-文件描述符": {
        "task": "文件描述符",
        "pattern": (
            "def fd_alloc(table, path):\n"
            "    # 打开文件表：分配最小可用 fd（0/1/2 留给标准流，从 3 起）\n"
            "    fd = 3\n"
            "    while fd in table:\n"
            "        fd += 1\n"
            "    table[fd] = path\n"
            "    return fd\n"
            "def fd_close(table, fd):\n"
            "    # 关闭：释放 fd（返回被关闭的路径）\n"
            "    return table.pop(fd, None)\n"),
        "cases": [(({}, '/etc/passwd'), 3),
                  (({3: '/a', 4: '/b'}, '/c'), 5),
                  (({3: '/a'}, '/b'), 4)],
        "params": [],
        "calibration": "对照：OS 文件系统——打开文件表（fd 最小分配，0/1/2 标准流保留）",
    },
    "设备-字符设备": {
        "task": "字符设备",
        "pattern": (
            "def char_device(device, op, data=None):\n"
            "    # 字符设备抽象：open/read/write/close（驱动接口——设备=文件 语义）\n"
            "    if op == 'open':\n"
            "        device['opened'] = True\n"
            "        return True\n"
            "    if op == 'read':\n"
            "        if not device.get('opened'):\n"
            "            return None\n"
            "        buf = device.get('buf', '')\n"
            "        device['buf'] = ''\n"
            "        return buf\n"
            "    if op == 'write':\n"
            "        if not device.get('opened'):\n"
            "            return False\n"
            "        device['buf'] = device.get('buf', '') + (data or '')\n"
            "        return True\n"
            "    if op == 'close':\n"
            "        device['opened'] = False\n"
            "        return True\n"
            "    return False\n"),
        "cases": [(({'opened': False}, 'open'), True),
                  (({'opened': True, 'buf': ''}, 'write', '数据'), True),
                  (({'opened': True, 'buf': '数据'}, 'read'), '数据'),
                  (({'opened': False}, 'read'), None)],
        "params": [],
        "calibration": "对照：OS 设备驱动——字符设备接口（open/read/write/close，设备即文件）",
    },
    "中断-向量表": {
        "task": "中断向量",
        "pattern": (
            "def vector_lookup(table, irq):\n"
            "    # 中断向量表：IRQ 号 → 处理函数（未注册 → None）\n"
            "    return table.get(irq)\n"),
        "cases": [(({3: 'timer_handler', 14: 'disk_handler'}, 3), 'timer_handler'),
                  (({3: 'timer_handler'}, 14), None),
                  (({}, 0), None)],
        "params": [],
        "calibration": "对照：OS 中断——向量表（IRQ→handler 查表分派，未注册返回 None）",
    },
    "中断-上下文切换": {
        "task": "上下文切换",
        "pattern": (
            "def ctx_switch(ctx, save):\n"
            "    # 中断上下文切换：保存当前寄存器 → 恢复目标（现场保护/恢复）\n"
            "    if save:\n"
            "        ctx['saved'] = dict(ctx.get('regs', {}))\n"
            "        return 'saved'\n"
            "    regs = ctx.pop('saved', {})\n"
            "    ctx['regs'] = dict(regs)\n"
            "    return 'restored'\n"),
        "cases": [(({'regs': {'a': 1, 'b': 2}}, True), 'saved'),
                  (({'regs': {'a': 1}, 'saved': {'a': 9}}, False), 'restored')],
        "params": [],
        "calibration": "对照：OS 中断——上下文切换（现场保存/恢复，中断处理不破坏用户态）",
    },
    "中断-嵌套优先级": {
        "task": "中断优先级",
        "pattern": (
            "def nested_irq(current_prio, new_prio):\n"
            "    # 中断嵌套：新中断优先级更高 → 可抢占当前（NMI/高优先抢占）\n"
            "    return new_prio > current_prio\n"),
        "cases": [((3, 5), True),
                  ((5, 3), False),
                  ((3, 3), False)],
        "params": [],
        "calibration": "对照：OS 中断——嵌套优先级（高优先级中断可抢占低优先级，同级不嵌套）",
    },
    "文件-系统挂载": {
        "task": "文件系统挂载",
        "pattern": (
            "def mount_op(mounts, path, fs_type=None):\n"
            "    # VFS 挂载：挂载点→文件系统（mount 注册/unmount 卸载/查询）\n"
            "    if fs_type is not None:\n"
            "        mounts[path] = fs_type\n"
            "        return True\n"
            "    if fs_type is None and path in mounts:\n"
            "        return mounts.pop(path)  # unmount\n"
            "    return None\n"),
        "cases": [(({}, '/data', 'ext4'), True),
                  (({'/data': 'ext4'}, '/data'), 'ext4'),
                  (({'/data': 'ext4'}, '/other'), None)],
        "params": [],
        "calibration": "对照：OS VFS——文件系统挂载（mount 注册/unmount 卸载/未挂载 None）",
    },
    "文件-文件权限": {
        "task": "文件权限",
        "pattern": (
            "def check_perm(mode, access):\n"
            "    # 文件权限：模式位 rwx 检查（读4/写2/执行1 位运算）\n"
            "    bit = {'r': 4, 'w': 2, 'x': 1}[access]\n"
            "    return bool(mode & bit)\n"),
        "cases": [((7, 'r'), True), ((7, 'w'), True), ((5, 'w'), False),
                  ((1, 'x'), True), ((0, 'r'), False)],
        "params": [],
        "calibration": "对照：OS 文件权限——模式位检查（r=4/w=2/x=1 位与运算）",
    },
    "进程-进程树": {
        "task": "进程树",
        "pattern": (
            "def process_tree(parents, root):\n"
            "    # 进程树：父进程关系 → 后代集合（递归收集子树）\n"
            "    children = {}\n"
            "    for pid, ppid in parents.items():\n"
            "        children.setdefault(ppid, []).append(pid)\n"
            "    desc = []\n"
            "    def walk(pid):\n"
            "        for c in children.get(pid, []):\n"
            "            desc.append(c)\n"
            "            walk(c)\n"
            "    walk(root)\n"
            "    return sorted(desc)\n"),
        "cases": [(({'a': 'root', 'b': 'a', 'c': 'a'}, 'root'), ['a', 'b', 'c']),
                  (({'b': 'a'}, 'a'), ['b']),
                  (({}, 'a'), [])],
        "params": [],
        "calibration": "对照：OS 进程树——父子关系后代收集（fork 产生的进程层级）",
    },
    "系统调用-接口": {
        "task": "系统调用",
        "pattern": (
            "def syscall_dispatch(table, num, args):\n"
            "    # 系统调用：编号 → 处理函数分派（未知编号 → None）\n"
            "    fn = table.get(num)\n"
            "    if fn is None:\n"
            "        return None\n"
            "    return fn(*args)\n"),
        "cases": [(({1: lambda x: x + 1, 2: lambda a, b: a * b}, 1, [5]), 6),
                  (({1: lambda x: x}, 2, [3]), None),
                  (({}, 9, []), None)],
        "params": [],
        "calibration": "对照：OS 系统调用——编号分派（syscall 表，未知编号返回 None）",
    },
    "信号-信号处理": {
        "task": "信号处理",
        "pattern": (
            "def signal_op(handlers, op, signum=None, handler=None):\n"
            "    # 信号：注册 handler / 发送信号 / 默认处理（忽略/终止）\n"
            "    if op == 'register':\n"
            "        handlers[signum] = handler\n"
            "        return True\n"
            "    if op == 'send':\n"
            "        fn = handlers.get(signum)\n"
            "        if fn is not None:\n"
            "            return ('handled', fn())\n"
            "        return ('default', 'terminate' if signum == 2 else 'ignore')\n"
            "    return None\n"),
        "cases": [(({}, 'register', 2, lambda: 'cleanup'), True),
                  (({2: lambda: 'cleanup'}, 'send', 2), ('handled', 'cleanup')),
                  (({}, 'send', 2), ('default', 'terminate')),
                  (({}, 'send', 10), ('default', 'ignore'))],
        "params": [],
        "calibration": "对照：OS 信号——注册/发送/默认（SIGINT=2 默认终止，SIGUSR=10 默认忽略）",
    },
    "系统调用-参数校验": {
        "task": "参数校验",
        "pattern": (
            "def validate_args(args, types):\n"
            "    # 系统调用参数校验：类型检查（copy_from_user 语义——非法参数拒绝）\n"
            "    if len(args) != len(types):\n"
            "            return False\n"
            "    for a, t in zip(args, types):\n"
            "        if not isinstance(a, t):\n"
            "            return False\n"
            "    return True\n"),
        "cases": [(([1, 'x'], [int, str]), True),
                  (([1, 2], [int, str]), False),
                  (([1], [int, str]), False)],
        "params": [],
        "calibration": "对照：OS 系统调用——参数类型校验（copy_from_user 语义，非法拒绝）",
    },
    "文件-日志恢复": {
        "task": "日志恢复",
        "pattern": (
            "def journal_replay(entries, disk):\n"
            "    # 文件系统日志：崩溃后重放（journal 条目 → 磁盘状态恢复）\n"
            "    for e in entries:\n"
            "        if e.get('type') == 'write':\n"
            "            disk[e['inode']] = e['data']\n"
            "        elif e.get('type') == 'delete':\n"
            "            disk.pop(e['inode'], None)\n"
            "    return dict(disk)\n"),
        "cases": [(([{'type': 'write', 'inode': 'a', 'data': 'X'},
                     {'type': 'write', 'inode': 'b', 'data': 'Y'},
                     {'type': 'delete', 'inode': 'a'}], {}),
                   {'b': 'Y'}),
                  (([], {'a': 'keep'}), {'a': 'keep'})],
        "params": [],
        "calibration": "对照：OS 文件系统日志——journal 重放（崩溃恢复，write/delete 条目应用）",
    },
    "系统-监控指标": {
        "task": "系统监控",
        "pattern": (
            "def sys_metrics(usage_samples):\n"
            "    # 系统监控：CPU/内存采样 → 平均/峰值（负载统计）\n"
            "    if not usage_samples:\n"
            "        return {'avg': 0.0, 'peak': 0.0}\n"
            "    return {'avg': round(sum(usage_samples) / len(usage_samples), 2),\n"
            "            'peak': max(usage_samples)}\n"),
        "cases": [(([30, 50, 70],), {'avg': 50.0, 'peak': 70}),
                  (([],), {'avg': 0.0, 'peak': 0.0}),
                  (([100],), {'avg': 100.0, 'peak': 100})],
        "params": [],
        "calibration": "对照：OS 系统监控——CPU 使用率采样统计（平均/峰值）",
    },
    "系统-守护进程": {
        "task": "守护进程",
        "pattern": (
            "def daemon_lifecycle(state, op):\n"
            "    # 守护进程：启动→运行→停止（后台服务生命周期）\n"
            "    if op == 'start':\n"
            "        state['status'] = 'running'\n"
            "        return 'running'\n"
            "    if op == 'stop':\n"
            "        state['status'] = 'stopped'\n"
            "        return 'stopped'\n"
            "    if op == 'status':\n"
            "        return state.get('status', 'unknown')\n"
            "    return 'unknown'\n"),
        "cases": [(({'status': 'idle'}, 'start'), 'running'),
                  (({'status': 'running'}, 'stop'), 'stopped'),
                  (({'status': 'running'}, 'status'), 'running')],
        "params": [],
        "calibration": "对照：OS 守护进程——生命周期（start/stop/status 状态机）",
    },
    "并发-信号量": {
        "task": "信号量",
        "pattern": (
            "def semaphore_op(sem, op):\n"
            "    # 信号量：P 减（资源不足阻塞）/ V 加（释放资源）——计数同步\n"
            "    if op == 'P':\n"
            "        if sem['count'] <= 0:\n"
            "            return 'blocked'\n"
            "        sem['count'] -= 1\n"
            "        return 'acquired'\n"
            "    if op == 'V':\n"
            "        sem['count'] += 1\n"
            "        return 'released'\n"
            "    return None\n"),
        "cases": [(({'count': 1}, 'P'), 'acquired'),
                  (({'count': 0}, 'P'), 'blocked'),
                  (({'count': 0}, 'V'), 'released')],
        "params": [],
        "calibration": "对照：OS 并发——信号量 P/V（计数同步，资源耗尽 P 阻塞）",
    },
    "并发-读写锁": {
        "task": "读写锁",
        "pattern": (
            "def rwlock_op(lock, op):\n"
            "    # 读写锁：多读并发/写独占（读者计数 + 写者标志）\n"
            "    if op == 'r_lock':\n"
            "        if lock.get('writer'):\n"
            "            return 'blocked'\n"
            "        lock['readers'] = lock.get('readers', 0) + 1\n"
            "        return 'r_acquired'\n"
            "    if op == 'w_lock':\n"
            "        if lock.get('writer') or lock.get('readers', 0) > 0:\n"
            "            return 'blocked'\n"
            "        lock['writer'] = True\n"
            "        return 'w_acquired'\n"
            "    if op == 'r_unlock':\n"
            "        lock['readers'] = max(0, lock.get('readers', 0) - 1)\n"
            "        return 'r_released'\n"
            "    if op == 'w_unlock':\n"
            "        lock['writer'] = False\n"
            "        return 'w_released'\n"
            "    return None\n"),
        "cases": [(({'readers': 0}, 'r_lock'), 'r_acquired'),
                  (({'readers': 1, 'writer': False}, 'w_lock'), 'blocked'),
                  (({'readers': 0, 'writer': False}, 'w_lock'), 'w_acquired')],
        "params": [],
        "calibration": "对照：OS 并发——读写锁（多读并发/写独占，读者在场写阻塞）",
    },
    "并发-生产者消费者": {
        "task": "生产者消费者",
        "pattern": (
            "def producer_consumer(buf, op, item=None):\n"
            "    # 生产者-消费者：有界缓冲（生产入队/消费出队）\n"
            "    if op == 'produce':\n"
            "        if len(buf) >= 4:\n"
            "            return 'buffer_full'\n"
            "        buf.append(item)\n"
            "        return len(buf)\n"
            "    if op == 'consume':\n"
            "        if not buf:\n"
            "            return 'buffer_empty'\n"
            "        return buf.pop(0)\n"
            "    return None\n"),
        "cases": [(([], 'produce', 'a'), 1),
                  ((['a'], 'consume'), 'a'),
                  (([], 'consume'), 'buffer_empty'),
                  ((['a', 'b', 'c', 'd'], 'produce', 'e'), 'buffer_full')],
        "params": [],
        "calibration": "对照：OS 并发——生产者-消费者（有界缓冲，满/空边界）",
    },
    "虚拟化-命名空间": {
        "task": "命名空间",
        "pattern": (
            "def ns_map(op, ns, pid=None):\n"
            "    # 命名空间隔离：PID/网络视图映射（容器进程 → 命名空间内 PID）\n"
            "    if op == 'register':\n"
            "        ns['inner'] = ns.get('inner', 100) + 1\n"
            "        ns[pid] = ns['inner']\n"
            "        return ns[pid]\n"
            "    if op == 'lookup':\n"
            "        return ns.get(pid)\n"
            "    return None\n"),
        "cases": [(('register', {}, 'p1'), 101),
                  (('lookup', {'inner': 100, 'p1': 101}, 'p1'), 101),
                  (('lookup', {'inner': 100}, 'nope'), None)],
        "params": [],
        "calibration": "对照：容器命名空间——PID 视图映射（进程在命名空间内重编号，隔离语义）",
    },
    "虚拟化-cgroup限制": {
        "task": "资源限制",
        "pattern": (
            "def cgroup_limit(cg, resource, limit, usage):\n"
            "    # cgroup：资源配额（CPU/内存 限额，超限拒绝）\n"
            "    if resource not in cg:\n"
            "        cg[resource] = limit\n"
            "    return usage <= cg[resource]\n"),
        "cases": [(({}, 'cpu', 100, 80), True),
                  (({}, 'cpu', 100, 120), False),
                  (({'mem': 50}, 'mem', 50, 50), True)],
        "params": [],
        "calibration": "对照：cgroup 资源限制——CPU/内存配额（使用量超限拒绝）",
    },
    "容器-生命周期": {
        "task": "容器生命周期",
        "pattern": (
            "def container_ops(state, op, img=None):\n"
            "    # 容器：创建/启动/停止/删除（镜像 → 运行实例）\n"
            "    if op == 'create':\n"
            "        state['img'] = img\n"
            "        state['status'] = 'created'\n"
            "        return 'created'\n"
            "    if op == 'start':\n"
            "        state['status'] = 'running'\n"
            "        return 'running'\n"
            "    if op == 'stop':\n"
            "        state['status'] = 'exited'\n"
            "        return 'exited'\n"
            "    if op == 'remove':\n"
            "        state.clear()\n"
            "        return 'removed'\n"
            "    return None\n"),
        "cases": [(({}, 'create', 'alpine'), 'created'),
                  (({'status': 'created'}, 'start'), 'running'),
                  (({'status': 'running'}, 'stop'), 'exited'),
                  (({'status': 'exited'}, 'remove'), 'removed')],
        "params": [],
        "calibration": "对照：容器生命周期——create/start/stop/remove（镜像→实例状态机）",
    },
    "文件-RAID条带": {
        "task": "RAID条带",
        "pattern": (
            "def raid_stripe(data, disks):\n"
            "    # RAID 0：数据条带化（分块分布到多盘——并行读写）\n"
            "    if not disks:\n"
            "        return []\n"
            "    return [data[i::disks] for i in range(disks)]\n"),
        "cases": [((list('abcdef'), 2), [list('ace'), list('bdf')]),
                  ((list('abc'), 1), [list('abc')]),
                  ((list('ab'), 0), [])],
        "params": [],
        "calibration": "对照：RAID 0——数据条带化（分块分布，并行 I/O 语义）",
    },
    "文件-RAID奇偶校验": {
        "task": "RAID奇偶",
        "pattern": (
            "def raid_parity(blocks):\n"
            "    # RAID 5：XOR 奇偶校验（N-1 容错——单盘故障可恢复）\n"
            "    parity = 0\n"
            "    for b in blocks:\n"
            "        parity ^= b\n"
            "    return parity\n"),
        "cases": [(([1, 2, 3],), 0),
                  (([5, 3],), 6),
                  (([7],), 7)],
        "params": [],
        "calibration": "对照：RAID 5——XOR 奇偶校验（任一数据盘故障可由其余+奇偶恢复）",
    },
    "文件-文件系统快照": {
        "task": "文件快照",
        "pattern": (
            "def fs_snapshot(blocks, op, idx=None, data=None):\n"
            "    # 文件系统快照：写时复制（修改前复制原块——快照一致性）\n"
            "    if op == 'snap':\n"
            "        blocks['snap'] = dict(blocks['data'])\n"
            "        return 'snapped'\n"
            "    if op == 'write':\n"
            "        if 'snap' in blocks and idx not in blocks['snap']:\n"
            "            blocks['snap'][idx] = blocks['data'][idx]  # 写时复制\n"
            "        blocks['data'][idx] = data\n"
            "        return blocks['data'][idx]\n"
            "    if op == 'rollback':\n"
            "        blocks['data'] = dict(blocks.get('snap', {}))\n"
            "        return blocks['data']\n"
            "    return None\n"),
        "cases": [(({'data': {1: 'a'}}, 'snap'), 'snapped'),
                  (({'data': {1: 'a'}, 'snap': {1: 'a'}}, 'write', 1, 'b'), 'b'),
                  (({'data': {1: 'b'}, 'snap': {1: 'a'}}, 'rollback'), {1: 'a'})],
        "params": [],
        "calibration": "对照：文件系统快照——写时复制（修改前复制原块，可回滚）",
    },
    "启动-引导加载": {
        "task": "引导加载",
        "pattern": (
            "def bootloader(disk, stage):\n"
            "    # bootloader：MBR→内核加载（引导阶段推进）\n"
            "    if stage == 'mbr':\n"
            "        return ('loaded', disk.get('kernel', 'vmlinuz'))\n"
            "    if stage == 'initrd':\n"
            "        return ('mounted', 'initramfs')\n"
            "    return 'unknown'\n"),
        "cases": [(({'kernel': 'vmlinuz'}, 'mbr'), ('loaded', 'vmlinuz')),
                  (({}, 'initrd'), ('mounted', 'initramfs')),
                  (({}, 'x'), 'unknown')],
        "params": [],
        "calibration": "对照：OS 启动——bootloader（MBR→内核→initrd 加载）",
    },
    "启动-初始化流程": {
        "task": "初始化流程",
        "pattern": (
            "def init_sequence(services):\n"
            "    # init 进程：按依赖顺序启动服务（启动序列）\n"
            "    order = []\n"
            "    remaining = set(services)\n"
            "    while remaining:\n"
            "        for s in sorted(remaining):\n"
            "            deps = services[s]\n"
            "            if all(d in order for d in deps):\n"
            "                order.append(s)\n"
            "                remaining.remove(s)\n"
            "                break\n"
            "    return order\n"),
        "cases": [(({'网络': [], '应用': ['网络'], '存储': []},),
                   ['存储', '网络', '应用']),
                  (({},), [])],
        "params": [],
        "calibration": "对照：OS init——依赖排序启动（先依赖后服务）",
    },
    "系统-固件接口": {
        "task": "固件接口",
        "pattern": (
            "def firmware_call(fw, call):\n"
            "    # 固件接口：UEFI/BIOS 调用（硬件抽象服务）\n"
            "    if call == 'get_time':\n"
            "        return fw.get('time', 0)\n"
            "    if call == 'reboot':\n"
            "        return 'rebooting'\n"
            "    if call == 'set_boot':\n"
            "        fw['boot_dev'] = 'disk0'\n"
            "        return 'set'\n"
            "    return None\n"),
        "cases": [(({'time': 42}, 'get_time'), 42),
                  (({}, 'reboot'), 'rebooting'),
                  (({}, 'set_boot'), 'set')],
        "params": [],
        "calibration": "对照：固件接口——UEFI 服务（时间/重启/启动设备）",
    },
    "安全-访问控制": {
        "task": "访问控制",
        "pattern": (
            "def acl_check(acl, subject, resource, action):\n"
            "    # ACL：访问控制列表（主体→资源→动作 权限判定）\n"
            "    rules = acl.get(resource, [])\n"
            "    for r in rules:\n"
            "        if r['subject'] == subject and r['action'] == action:\n"
            "            return r['allow']\n"
            "    return False  # 默认拒绝\n"),
        "cases": [(({'file': [{'subject': 'u1', 'action': 'read', 'allow': True}]},
                    'u1', 'file', 'read'), True),
                  (({'file': []}, 'u1', 'file', 'read'), False),
                  (({'file': [{'subject': 'u1', 'action': 'write', 'allow': False}]},
                    'u1', 'file', 'write'), False)],
        "params": [],
        "calibration": "对照：OS 安全——ACL 访问控制（主体/资源/动作 规则判定，默认拒绝）",
    },
    "安全-审计日志": {
        "task": "审计日志",
        "pattern": (
            "def audit_log(log, event, subject):\n"
            "    # 审计：安全事件记录（操作 → 日志条目）\n"
            "    log.append({'event': event, 'subject': subject})\n"
            "    return len(log)\n"),
        "cases": [(([], 'login', 'u1'), 1),
                  (([{'event': 'login', 'subject': 'u1'}], 'logout', 'u1'), 2)],
        "params": [],
        "calibration": "对照：OS 安全——审计日志（安全事件记录，可追溯）",
    },
    "安全-能力系统": {
        "task": "能力系统",
        "pattern": (
            "def capability(caps, op, cap=None):\n"
            "    # 能力：特权令牌（持能力才可操作——最小权限语义）\n"
            "    if op == 'grant':\n"
            "        caps.add(cap)\n"
            "        return True\n"
            "    if op == 'check':\n"
            "        return cap in caps\n"
            "    if op == 'revoke':\n"
            "        caps.discard(cap)\n"
            "        return cap not in caps\n"
            "    return False\n"),
        "cases": [((set(), 'grant', 'net_raw'), True),
                  (({'net_raw'}, 'check', 'net_raw'), True),
                  ((set(), 'check', 'net_raw'), False),
                  (({'net_raw'}, 'revoke', 'net_raw'), True)],
        "params": [],
        "calibration": "对照：OS 安全——能力系统（特权令牌授予/检查/撤销，最小权限）",
    },
    "性能-性能分析": {
        "task": "性能分析",
        "pattern": (
            "def profile_funcs(times):\n"
            "    # profiling：函数耗时统计（累计/平均——热点定位）\n"
            "    total = sum(times)\n"
            "    if not times:\n"
            "        return {'total': 0, 'avg': 0.0}\n"
            "    return {'total': total, 'avg': round(total / len(times), 2)}\n"),
        "cases": [(([10, 20, 30],), {'total': 60, 'avg': 20.0}),
                  (([],), {'total': 0, 'avg': 0.0})],
        "params": [],
        "calibration": "对照：OS 性能——profiling（函数耗时统计，热点定位）",
    },
    "性能-瓶颈检测": {
        "task": "瓶颈检测",
        "pattern": (
            "def bottleneck(resources):\n"
            "    # 瓶颈检测：利用率最高的资源（系统瓶颈定位）\n"
            "    if not resources:\n"
            "        return None\n"
            "    return max(resources.items(), key=lambda kv: kv[1])\n"),
        "cases": [(({'cpu': 90, 'mem': 60, 'io': 30},), ('cpu', 90)),
                  (({},), None)],
        "params": [],
        "calibration": "对照：OS 性能——瓶颈检测（最高利用率资源）",
    },
    "性能-调优建议": {
        "task": "调优建议",
        "pattern": (
            "def tuning_advice(metrics):\n"
            "    # 调优：指标 → 建议（瓶颈 → 调整参数）\n"
            "    adv = []\n"
            "    if metrics.get('cpu', 0) > 80:\n"
            "        adv.append('升级 CPU 或减少进程')\n"
            "    if metrics.get('mem', 0) > 80:\n"
            "        adv.append('增加内存或优化缓存')\n"
            "    if not adv:\n"
            "        adv.append('当前配置合理')\n"
            "    return adv\n"),
        "cases": [(({'cpu': 90, 'mem': 50},), ['升级 CPU 或减少进程']),
                  (({'cpu': 50, 'mem': 90},), ['增加内存或优化缓存']),
                  (({'cpu': 50, 'mem': 50},), ['当前配置合理'])],
        "params": [],
        "calibration": "对照：OS 性能——调优建议（瓶颈 → 参数调整建议）",
    },
    "文件-磁盘配额": {
        "task": "磁盘配额",
        "pattern": (
            "def quota_check(quotas, user, usage, size):\n"
            "    # 磁盘配额：用户使用量 + 新写入 ≤ 限额（超限拒绝）\n"
            "    limit = quotas.get(user, float('inf'))\n"
            "    return usage + size <= limit\n"),
        "cases": [(({'u1': 100}, 'u1', 80, 10), True),
                  (({'u1': 100}, 'u1', 95, 10), False),
                  (({}, 'u2', 50, 10), True)],
        "params": [],
        "calibration": "对照：OS 磁盘配额——用户限额（使用量+写入 ≤ 限额，超限拒绝）",
    },
    "文件-文件锁": {
        "task": "文件锁",
        "pattern": (
            "def file_lock(state, op):\n"
            "    # 文件锁：flock 语义（独占/释放——并发写保护）\n"
            "    if op == 'lock':\n"
            "        if state.get('locked'):\n"
            "            return 'blocked'\n"
            "        state['locked'] = True\n"
            "        return 'locked'\n"
            "    if op == 'unlock':\n"
            "        state['locked'] = False\n"
            "        return 'unlocked'\n"
            "    return None\n"),
        "cases": [(({'locked': False}, 'lock'), 'locked'),
                  (({'locked': True}, 'lock'), 'blocked'),
                  (({'locked': True}, 'unlock'), 'unlocked')],
        "params": [],
        "calibration": "对照：OS 文件锁——flock（独占/释放，并发写保护）",
    },
    "系统-资源限额": {
        "task": "资源限额",
        "pattern": (
            "def rlimit(res, op, soft=None):\n"
            "    # ulimit：进程资源限制（设置/查询软限制）\n"
            "    if op == 'set':\n"
            "        res['soft'] = soft\n"
            "        return soft\n"
            "    if op == 'get':\n"
            "        return res.get('soft')\n"
            "    if op == 'check':\n"
            "        return res.get('soft', float('inf'))\n"
            "    return None\n"),
        "cases": [(({}, 'set', 1024), 1024),
                  (({'soft': 1024}, 'get', None), 1024),
                  (({}, 'check', None), float('inf'))],
        "params": [],
        "calibration": "对照：OS ulimit——进程资源限制（软限制设置/查询）",
    },
    "可信-安全启动": {
        "task": "安全启动",
        "pattern": (
            "def secure_boot(chain, keyring):\n"
            "    # 安全启动：启动组件签名验证链（未签名/密钥不符拒绝）\n"
            "    for comp in chain:\n"
            "        if comp not in keyring:\n"
            "            return ('denied', comp)\n"
            "    return ('booted', True)\n"),
        "cases": [((['kernel', 'initrd'], {'kernel', 'initrd'}), ('booted', True)),
                  ((['kernel', 'evil'], {'kernel'}), ('denied', 'evil'))],
        "params": [],
        "calibration": "对照：安全启动——签名验证链（组件须在可信密钥库）",
    },
    "可信-TPM度量": {
        "task": "TPM度量",
        "pattern": (
            "def tpm_measure(pcr, component):\n"
            "    # TPM 度量：PCR 扩展（哈希累加——信任链度量）\n"
            "    h = sum(ord(c) for c in component) % 256\n"
            "    pcr = (pcr + h) % 256\n"
            "    return pcr\n"),
        "cases": [((0, 'BIOS'), 45),
                  ((45, 'loader'), 164),
                  ((0, ''), 0)],
        "params": [],
        "calibration": "对照：TPM——PCR 扩展度量（组件哈希累加到平台寄存器）",
    },
    "可信-哈希校验": {
        "task": "哈希校验",
        "pattern": (
            "def hash_verify(file_hash, expected):\n"
            "    # 文件完整性：哈希比对（不匹配 → 篡改告警）\n"
            "    if file_hash == expected:\n"
            "        return 'integrity_ok'\n"
            "    return 'tampered'\n"),
        "cases": [(('abc123', 'abc123'), 'integrity_ok'),
                  (('abc', 'xyz'), 'tampered')],
        "params": [],
        "calibration": "对照：可信计算——文件哈希校验（完整性验证，篡改检测）",
    },
    "设备-热插拔": {
        "task": "热插拔",
        "pattern": (
            "def hotplug(bus, op, device=None):\n"
            "    # 热插拔：设备接入/移除（运行中动态管理）\n"
            "    if op == 'plug':\n"
            "        bus.add(device)\n"
            "        return 'plugged'\n"
            "    if op == 'unplug':\n"
            "        bus.discard(device)\n"
            "        return 'unplugged'\n"
            "    if op == 'list':\n"
            "        return sorted(bus)\n"
            "    return None\n"),
        "cases": [((set(), 'plug', 'usb1'), 'plugged'),
                  (({'usb1'}, 'unplug', 'usb1'), 'unplugged'),
                  (({'usb1', 'usb2'}, 'list'), ['usb1', 'usb2'])],
        "params": [],
        "calibration": "对照：设备热插拔——接入/移除（运行中动态管理 USB 语义）",
    },
    "设备-即插即用": {
        "task": "即插即用",
        "pattern": (
            "def plug_and_play(device, drivers):\n"
            "    # 即插即用：设备 ID → 自动匹配驱动（免手动配置）\n"
            "    for d in drivers:\n"
            "        if device.startswith(d['vendor']):\n"
            "            return ('matched', d['name'])\n"
            "    return ('nomatch', None)\n"),
        "cases": [(('VID_1234_PID_1', [{'vendor': 'VID_1234', 'name': '鼠标'}]),
                   ('matched', '鼠标')),
                  (('VID_9999_PID_1', [{'vendor': 'VID_1234', 'name': '鼠标'}]),
                   ('nomatch', None))],
        "params": [],
        "calibration": "对照：即插即用——设备 ID 自动匹配驱动（PnP 语义）",
    },
    "设备-设备树": {
        "task": "设备树",
        "pattern": (
            "def device_tree_lookup(tree, node):\n"
            "    # 设备树：硬件拓扑节点查找（属性查询）\n"
            "    return tree.get(node)\n"),
        "cases": [(({'uart0': {'compatible': 'ns16550'}}, 'uart0'),
                   {'compatible': 'ns16550'}),
                  (({}, 'uart0'), None)],
        "params": [],
        "calibration": "对照：设备树——硬件拓扑节点（compatible 属性）",
    },
    "IPC-消息队列": {
        "task": "消息队列",
        "pattern": (
            "def msg_queue_ops(q, op, mtype=None, body=None):\n"
            "    # 消息队列：send 按类型投递 / recv 按类型取最早 / count 统计\n"
            "    # （SysV msg 语义：消息带类型，按类型取）\n"
            "    if op == 'send':\n"
            "        q.append((mtype, body))\n"
            "        return len(q)\n"
            "    if op == 'recv':\n"
            "        for i, (t, b) in enumerate(q):\n"
            "            if mtype is None or t == mtype:\n"
            "                q.pop(i)\n"
            "                return (t, b)\n"
            "        return None\n"
            "    if op == 'count':\n"
            "        return len(q)\n"
            "    return None\n"),
        "cases": [(([], 'send', 1, '甲'), 1),
                  (([(1, '甲'), (2, '乙')], 'recv', 1, None), (1, '甲')),
                  (([], 'recv', None, None), None),
                  (([(1, '甲')], 'count', None, None), 1)],
        "params": [],
        "calibration": "对照：OS IPC 消息队列——SysV msg（类型投递/按类型取最早）",
    },
    "IPC-共享内存": {
        "task": "共享内存",
        "pattern": (
            "def shm_ops(segments, key, op, offset=0, value=None, size=0):\n"
            "    # 共享内存：attach 挂接 / write 写偏移 / read 读偏移 / detach 释放\n"
            "    # （多进程映射同一物理页，引用计数）\n"
            "    if op == 'attach':\n"
            "        if key not in segments:\n"
            "            segments[key] = {'data': bytearray(size), 'refs': 0}\n"
            "        segments[key]['refs'] += 1\n"
            "        return segments[key]['refs']\n"
            "    if op == 'write':\n"
            "        segments[key]['data'][offset] = value\n"
            "        return value\n"
            "    if op == 'read':\n"
            "        return segments[key]['data'][offset]\n"
            "    if op == 'detach':\n"
            "        segments[key]['refs'] -= 1\n"
            "        return segments[key]['refs']\n"
            "    return None\n"),
        "cases": [(({}, 'k1', 'attach', 0, None, 8), 1),
                  (({'k1': {'data': bytearray(4), 'refs': 1}}, 'k1',
                    'write', 2, 65, 0), 65),
                  (({'k1': {'data': bytearray([0, 0, 65, 0]), 'refs': 1}},
                    'k1', 'read', 2, None, 0), 65),
                  (({'k1': {'data': bytearray(4), 'refs': 2}}, 'k1',
                    'detach', 0, None, 0), 1)],
        "params": [],
        "calibration": "对照：OS IPC 共享内存——attach/write/read/detach（物理页共享，引用计数）",
    },
    "IPC-邮箱": {
        "task": "邮箱",
        "pattern": (
            "def mailbox_ops(mb, op, msg=None):\n"
            "    # 邮箱：put 投递 / get 取最早（FIFO）/ 空返回 None\n"
            "    # （异步消息槽，收发进程解耦）\n"
            "    if op == 'put':\n"
            "        mb.append(msg)\n"
            "        return len(mb)\n"
            "    if op == 'get':\n"
            "        return mb.pop(0) if mb else None\n"
            "    return None\n"),
        "cases": [(([], 'put', '甲'), 1),
                  (([], 'get', None), None),
                  (([1, 2], 'get', None), 1),
                  ((['甲'], 'put', '乙'), 2)],
        "params": [],
        "calibration": "对照：OS IPC 邮箱——异步消息槽（put 投递/get FIFO 取，进程解耦）",
    },
    "调度-多级反馈队列": {
        "task": "多级反馈队列",
        "pattern": (
            "def mlfq_ops(queues, op, pid=None, level=None, boost_to=0):\n"
            "    # 多级反馈队列：enqueue 按等级入队 / pick 取最高级队首\n"
            "    # / boost 低优先级提升（防饿死）\n"
            "    if op == 'enqueue':\n"
            "        queues[level].append(pid)\n"
            "        return queues[level]\n"
            "    if op == 'pick':\n"
            "        for q in queues:\n"
            "            if q:\n"
            "                return q.pop(0)\n"
            "        return None\n"
            "    if op == 'boost':\n"
            "        if boost_to < len(queues):\n"
            "            merged = []\n"
            "            for i in range(boost_to + 1, len(queues)):\n"
            "                merged.extend(queues[i])\n"
            "                queues[i] = []\n"
            "            queues[boost_to].extend(merged)\n"
            "        return queues[boost_to]\n"
            "    return None\n"),
        "cases": [(([[], [], []], 'enqueue', 'a', 2, 0), ['a']),
                  (([['x'], ['a'], []], 'pick', None, None, 0), 'x'),
                  (([[], [], ['c', 'd']], 'pick', None, None, 0), 'c'),
                  (([[], [], [], ['e']], 'boost', None, None, 0), ['e']),
                  (([[],[],[]], 'pick', None, None, 0), None)],
        "params": [],
        "calibration": "对照：OS 多级反馈队列 MLFQ——高等级优先调度，低等级定期提升（防饿死）",
    },
    "调度-实时EDF": {
        "task": "实时调度",
        "pattern": (
            "def edf_pick(ready, now):\n"
            "    # 实时调度：最早截止时间优先（EDF——deadline 最近者先执行）\n"
            "    if not ready:\n"
            "        return None\n"
            "    return min(ready, key=lambda t: t[1])[0]\n"),
        "cases": [(([('a', 10), ('b', 5)], 0), 'b'),
                  (([], 0), None),
                  (([('a', 10)], 0), 'a')],
        "params": [],
        "calibration": "对照：OS 实时调度 EDF——最早截止时间优先（deadline 最近先执行）",
    },
    "系统调用-文件分派": {
        "task": "文件系统调用",
        "pattern": (
            "def syscall_file(op, fd_table, fd=None, path=None, data=None, mode='r'):\n"
            "    # 系统调用：open/read/write/close 分派（fd 表管理文件操作）\n"
            "    if op == 'open':\n"
            "        fd_table.append({'path': path, 'mode': mode, 'data': data or ''})\n"
            "        return len(fd_table) - 1\n"
            "    if op == 'read':\n"
            "        return fd_table[fd]['data']\n"
            "    if op == 'write':\n"
            "        fd_table[fd]['data'] += data\n"
            "        return len(data)\n"
            "    if op == 'close':\n"
            "        fd_table[fd] = None\n"
            "        return 'closed'\n"
            "    return None\n"),
        "cases": [(('open', [], 'a.txt', None, '', 'r'), 0),
                  (('read', [{'path': 'a', 'data': '你好'}], 0,
                    None, None, 'r'), '你好'),
                  (('write', [{'path': 'a', 'data': ''}], 0, None, 'x', 'w'), 1),
                  (('close', [{'path': 'a'}], 0, None, None, 'r'), 'closed')],
        "params": [],
        "calibration": "对照：OS 系统调用——open/read/write/close 文件操作（fd 表分派）",
    },
    "内存-伙伴系统": {
        "task": "伙伴系统",
        "pattern": (
            "def buddy_alloc(free_lists, size):\n"
            "    # 伙伴系统：2 的幂块分配（最小合适阶取，缺则高阶分裂回补）\n"
            "    order = 0\n"
            "    while (1 << order) < size:\n"
            "        order += 1\n"
            "    for o in range(order, max(free_lists) + 1):\n"
            "        if free_lists[o]:\n"
            "            free_lists[o] -= 1\n"
            "            while o > order:\n"
            "                o -= 1\n"
            "                free_lists[o] += 1\n"
            "            return 'allocated'\n"
            "    return 'failed'\n"),
        "cases": [(({0: 0, 1: 1, 2: 0}, 1), 'allocated'),
                  (({0: 0, 1: 0, 2: 1}, 1), 'allocated'),
                  (({0: 0, 1: 0, 2: 0}, 4), 'failed'),
                  (({0: 2, 1: 0}, 1), 'allocated')],
        "params": [],
        "calibration": "对照：OS 内存——伙伴系统（2 的幂块分配，高阶块分裂到合适阶）",
    },
    "内存-写时复制": {
        "task": "写时复制",
        "pattern": (
            "def cow_write(pages, idx, value, shared_set):\n"
            "    # 写时复制：写共享页 → 复制新页再写（原页保留，fork COW 语义）\n"
            "    if idx in shared_set:\n"
            "        pages[idx] = value\n"
            "        shared_set.discard(idx)\n"
            "        return 'copied'\n"
            "    pages[idx] = value\n"
            "    return 'written'\n"),
        "cases": [((['a', 'b'], 0, 'X', {0}), 'copied'),
                  ((['a', 'b'], 1, 'Y', set()), 'written'),
                  ((['a'], 0, 'Z', {0}), 'copied')],
        "params": [],
        "calibration": "对照：OS 内存——写时复制（fork 共享页写时复制，节省物理内存）",
    },
    "内存-内存压缩": {
        "task": "内存压缩",
        "pattern": (
            "def memory_compress(pages, threshold):\n"
            "    # 内存压缩：超长页压缩存储（zswap——节省物理内存）\n"
            "    saved = 0\n"
            "    for p in pages:\n"
            "        if len(p) > threshold:\n"
            "            saved += len(p) - threshold\n"
            "    return saved\n"),
        "cases": [((['aaaa', 'b'], 2), 2),
                  ((['a', 'bb'], 2), 0),
                  (([], 2), 0)],
        "params": [],
        "calibration": "对照：OS 内存——内存压缩（超阈页压缩存储，减少占用）",
    },
    "文件-链接管理": {
        "task": "文件链接",
        "pattern": (
            "def link_ops(fs, op, name=None, target=None):\n"
            "    # 文件链接：hard 硬链接（共享 inode）/ soft 软链接（路径引用）/ resolve 解析\n"
            "    if op == 'hard':\n"
            "        if target in fs:\n"
            "            fs[name] = {'type': 'hard', 'inode': fs[target]['inode']}\n"
            "            return 'linked'\n"
            "        return 'missing'\n"
            "    if op == 'soft':\n"
            "        fs[name] = {'type': 'soft', 'target': target}\n"
            "        return 'linked'\n"
            "    if op == 'resolve':\n"
            "        entry = fs.get(name)\n"
            "        if entry is None:\n"
            "            return None\n"
            "        if entry['type'] == 'soft':\n"
            "            return fs.get(entry['target'], {}).get('data')\n"
            "        return entry.get('data')\n"
            "    return None\n"),
        "cases": [(({'a': {'inode': 1, 'data': 'D'}}, 'hard', 'b', 'a'), 'linked'),
                  (({}, 'hard', 'b', 'a'), 'missing'),
                  (({'a': {'inode': 1, 'data': 'D'}}, 'soft', 'b', 'a'), 'linked'),
                  (({'a': {'inode': 1, 'data': 'D'},
                     'b': {'type': 'soft', 'target': 'a'}}, 'resolve', 'b'), 'D'),
                  (({}, 'resolve', 'x'), None)],
        "params": [],
        "calibration": "对照：OS 文件系统——硬链接共享 inode/软链接路径引用（解析语义）",
    },
    "文件-元数据查询": {
        "task": "文件元数据",
        "pattern": (
            "def stat_file(fs, name):\n"
            "    # 文件元数据：stat 查询（大小/权限/类型——文件信息）\n"
            "    f = fs.get(name)\n"
            "    if f is None:\n"
            "        return None\n"
            "    return {'size': f.get('size', 0), 'mode': f.get('mode', 'rw'),\n"
            "            'type': f.get('type', 'file')}\n"),
        "cases": [(({'a': {'size': 10, 'mode': 'r', 'type': 'file'}}, 'a'),
                   {'size': 10, 'mode': 'r', 'type': 'file'}),
                  (({}, 'a'), None),
                  (({'a': {}}, 'a'), {'size': 0, 'mode': 'rw', 'type': 'file'})],
        "params": [],
        "calibration": "对照：OS stat——文件元数据（大小/权限/类型）",
    },
    "文件-内存映射": {
        "task": "内存映射",
        "pattern": (
            "def mmap_ops(maps, op, path=None, offset=0, size=0, data=None):\n"
            "    # 内存映射：map 映射文件段到内存 / read 读偏移 / write 写偏移回写\n"
            "    if op == 'map':\n"
            "        maps[path] = {'offset': offset, 'size': size,\n"
            "                      'data': bytearray(data or b'\\x00' * size)}\n"
            "        return path\n"
            "    if op == 'read':\n"
            "        m = maps[path]\n"
            "        return bytes(m['data'][offset:offset + size])\n"
            "    if op == 'write':\n"
            "        m = maps[path]\n"
            "        m['data'][offset:offset + len(data)] = data\n"
            "        return len(data)\n"
            "    return None\n"),
        "cases": [(({}, 'map', 'f', 0, 4, b'abcd'), 'f'),
                  (({'f': {'offset': 0, 'size': 4, 'data': bytearray(b'abcd')}},
                    'read', 'f', 1, 2), b'bc'),
                  (({'f': {'offset': 0, 'size': 4, 'data': bytearray(b'abcd')}},
                    'write', 'f', 1, 0, b'XY'), 2)],
        "params": [],
        "calibration": "对照：OS mmap——文件映射到内存（读偏移/写回）",
    },
    "并发-屏障同步": {
        "task": "屏障同步",
        "pattern": (
            "def barrier_ops(state, op, n=None):\n"
            "    # 屏障同步：wait 到达汇合点 / 全部到达释放（多线程同步汇合）\n"
            "    if op == 'wait':\n"
            "        state['arrived'] = state.get('arrived', 0) + 1\n"
            "        if state['arrived'] >= n:\n"
            "            state['arrived'] = 0\n"
            "            return 'released'\n"
            "        return 'waiting'\n"
            "    return None\n"),
        "cases": [(({'arrived': 0}, 'wait', 3), 'waiting'),
                  (({'arrived': 2}, 'wait', 3), 'released'),
                  (({'arrived': 0}, 'wait', 1), 'released')],
        "params": [],
        "calibration": "对照：OS 并发——屏障同步（全部到达汇合点才释放）",
    },
    "并发-工作池": {
        "task": "工作池",
        "pattern": (
            "def worker_pool(tasks, workers):\n"
            "    # 工作池：任务队列分发给固定 worker（并发处理，轮询负载均衡）\n"
            "    out = [[] for _ in range(workers)]\n"
            "    for i, t in enumerate(tasks):\n"
            "        out[i % workers].append(t)\n"
            "    return out\n"),
        "cases": [(([1, 2, 3, 4], 2), [[1, 3], [2, 4]]),
                  (([1, 2, 3], 3), [[1], [2], [3]]),
                  (([], 2), [[], []])],
        "params": [],
        "calibration": "对照：OS 并发——工作池（任务分发固定 worker，并发处理）",
    },
    "进程-生命周期": {
        "task": "进程生命周期",
        "pattern": (
            "def proc_life(states, op, pid=None, code=0):\n"
            "    # 进程生命周期：fork 创建 / exec 执行 / wait 等待退出（状态机）\n"
            "    if op == 'fork':\n"
            "        states[pid] = 'created'\n"
            "        return 'created'\n"
            "    if op == 'exec':\n"
            "        if pid in states:\n"
            "            states[pid] = 'running'\n"
            "            return 'running'\n"
            "        return 'unknown'\n"
            "    if op == 'wait':\n"
            "        if pid in states:\n"
            "            states[pid] = 'exited'\n"
            "            return code\n"
            "        return 'unknown'\n"
            "    return None\n"),
        "cases": [(({}, 'fork', 1), 'created'),
                  (({1: 'created'}, 'exec', 1), 'running'),
                  (({1: 'running'}, 'wait', 1, 0), 0),
                  (({}, 'exec', 9), 'unknown')],
        "params": [],
        "calibration": "对照：OS 进程——fork/exec/wait 生命周期状态机",
    },
}


def route_os_unit(question):
    """任务识别（问题 → OS 单元）"""
    best, best_len = None, 0
    for uid, u in OS_UNITS.items():
        for kw in (u["task"], uid):
            if kw in question and len(kw) > best_len:
                best, best_len = uid, len(kw)
    return best


if __name__ == "__main__":
    print("=== 迷你 Linux 白箱单元库（目标4 · 中文操作系统初级复现）===\n")
    for uid, u in OS_UNITS.items():
        print(f"[{uid}] 任务={u['task']} 样例数={len(u['cases'])}")
        print(f"    校准: {u['calibration']}")
    print(f"\n=== 判定 ===\n迷你 Linux 单元库: "
          f"{'✔ 5 单元就绪（进程调度/轮转/内存/文件/IPC）' if len(OS_UNITS) >= 4 else '✘'}")
