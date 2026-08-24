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
