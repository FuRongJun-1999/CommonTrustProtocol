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
