# -*- coding: utf-8 -*-
"""wal_truncate_watch.py · WAL 自动回收窗口监视器（配合 dsh web 手动重启）。

逻辑：每 3 秒探测一次——
  1) 是否存在「父进程为 node（dsh web）的 aeis.mcp.server」→ 有则 dsh 在线，跳过；
  2) 无 dsh 侧连接 → 尝试 wal_checkpoint(TRUNCATE)；
  3) busy=0（归零成功）→ 写结果日志并退出；busy=1 → 继续等。
总时长上限 30 分钟，防止无限挂起。结果写 tools/wal_truncate_watch.log。
"""

import os
import subprocess
import sqlite3
import time

DB = r"D:\Program Files\2_ai\AEIS\data\aeis_memory.db"
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wal_truncate_watch.log")
TIMEOUT = 30 * 60


def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def dsh_mcp_pids():
    """返回父进程为 node（dsh web）的 aeis.mcp.server PID 列表。"""
    try:
        out = subprocess.check_output(
            ["powershell", "-Command",
             "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
             "Where-Object { $_.CommandLine -match 'aeis.mcp.server' } | "
             "ForEach-Object { $p = $_; "
             "$pp = Get-CimInstance Win32_Process -Filter (\"ProcessId=\" + $p.ParentProcessId); "
             "Write-Output ($p.ProcessId.ToString() + '|' + $pp.Name) }"],
            text=True, errors="replace", timeout=20)
        return [int(line.split("|")[0]) for line in out.splitlines()
                if "|" in line and "node" in line.split("|")[1]]
    except Exception:
        return []


def try_truncate():
    conn = sqlite3.connect(DB, timeout=15)
    conn.execute("PRAGMA busy_timeout=15000")
    r = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    conn.close()
    return r


def main():
    log(f"watcher start (pid={os.getpid()}, timeout={TIMEOUT}s)")
    end = time.time() + TIMEOUT
    while time.time() < end:
        pids = dsh_mcp_pids()
        if pids:
            log(f"dsh mcp 在线 {pids} → 等待窗口")
        else:
            try:
                r = try_truncate()
                log(f"TRUNCATE → {r}")
                if r and r[0] == 0:
                    wal = DB + "-wal"
                    size = os.path.getsize(wal) if os.path.exists(wal) else 0
                    log(f"SUCCESS: WAL 归零 (剩 {size} bytes)")
                    return
            except Exception as e:
                log(f"truncate 异常: {str(e)[:80]}")
        time.sleep(3)
    log("timeout 30min 退出")


if __name__ == "__main__":
    main()
