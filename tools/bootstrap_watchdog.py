# -*- coding: utf-8 -*-
"""bootstrap_watchdog.py · bootstrap_loop 停转检测与守护（2026-09-03 睡眠巩固落地）

背景：2026-09-02 发现 tools/bootstrap_loop.py 停转约 17h 无自动恢复
（见学习任务 node_4c97142a）。本脚本解决「日志新鲜度巡检」纯人工依赖：
每次运行 = 检测 + (停转则自动恢复)，供 Windows 计划任务每 10 分钟调度。

检测口径：bootstrap_log.jsonl 末条 ts 距今 > 2×interval（+120s 缓冲）判定停转；
恢复流程：进程卡死(存在但日志陈旧) → 先杀再拉起；进程缺失 → 直接拉起；
拉起命令与现跑实例一致：<python> tools/bootstrap_loop.py --interval 600，GAP_DEBUG=1。
用法：
  python bootstrap_watchdog.py            # 检测 + 停转自动恢复
  python bootstrap_watchdog.py --check-only  # 只报告不动作（心跳巡检用）
日志：tools/bootstrap_watchdog.jsonl
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG = os.path.join(HERE, "bootstrap_log.jsonl")
WLOG = os.path.join(HERE, "bootstrap_watchdog.jsonl")
PY = sys.executable or "python"
# 与现跑实例同解释器（ZCode Python310）
if "Python310" not in PY and os.path.exists(
    r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\python.exe"
):
    PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\python.exe"
BOOTSTRAP = os.path.join(HERE, "bootstrap_loop.py")
TS_FMT = "%Y-%m-%d %H:%M:%S"
GRACE = 120  # 额外缓冲秒


def log_watch(evt: dict) -> None:
    evt["ts"] = _dt.datetime.now().strftime(TS_FMT)
    try:
        with open(WLOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(evt, ensure_ascii=False) + "\n")
    except Exception:
        pass


def last_log_ts() -> tuple[float | None, dict | None]:
    """读 bootstrap_log.jsonl 末条记录，返回 (epoch_ts, 原始行 dict)。"""
    try:
        with open(LOG, "r", encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        if not lines:
            return None, None
        last = json.loads(lines[-1])
        ts = _dt.datetime.strptime(last.get("ts", ""), TS_FMT).timestamp()
        return ts, last
    except Exception:
        return None, None


def find_bootstrap_procs() -> list[dict]:
    """仅按命令行匹配 bootstrap_loop.py 的 python 进程。

    ⚠ 只认命令行含 bootstrap_loop.py 的进程——绝不 kill 其他 python
    （MCP server 等同解释器进程共存，宽匹配会误杀）。wmic 输出行尾
    \\r 干扰 PID 提取，一律 python re 提取（2026-08-31 教训固化）。
    """
    procs = []
    try:
        out = subprocess.run(
            ["wmic", "process", "where", "name like '%python%'",
             "get", "processid,commandline", "/format:csv"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace")
        import re
        pat = re.compile(r"(\d+)\s*$")
        for line in out.stdout.splitlines():
            if "bootstrap_loop.py" not in line:
                continue
            m = pat.search(line.strip())
            if m:
                procs.append({"pid": m.group(1),
                              "cmd": line.strip()[:200].replace("\r", "")})
    except Exception:
        pass
    return procs


def restart(check_only: bool) -> dict:
    """拉起 bootstrap_loop（与现跑实例一致：--interval 600, GAP_DEBUG=1）。"""
    env = dict(os.environ)
    env["GAP_DEBUG"] = "1"
    cmd = [PY, BOOTSTRAP, "--interval", "600"]
    if check_only:
        return {"action": "would_restart", "cmd": cmd}
    try:
        proc = subprocess.Popen(
            cmd, cwd=ROOT, env=env, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS
            | subprocess.CREATE_NO_WINDOW
            if os.name == "nt" else 0)
        # 等 6s 验证 loop_start 落地
        time.sleep(6)
        ts, last = last_log_ts()
        ok = last and last.get("round") == "loop_start"
        return {"action": "restarted", "pid": proc.pid,
                "verify": "loop_start_seen" if ok else "no_loop_start_yet",
                "last_round": (last or {}).get("round")}
    except Exception as e:
        return {"action": "restart_failed", "error": str(e)[:200]}


def main() -> int:
    ap = argparse.ArgumentParser(description="bootstrap_loop 停转检测与守护")
    ap.add_argument("--interval", type=int, default=600)
    ap.add_argument("--check-only", action="store_true", help="只报告不动作")
    args = ap.parse_args()

    stale_limit = 2 * args.interval + GRACE
    now = time.time()
    last_ts, last = last_log_ts()
    report = {"round": "watchdog", "interval": args.interval,
              "stale_limit_s": stale_limit}
    if last_ts is None:
        report.update({"status": "no_log", "detail": "日志缺失或不可解析"})
        log_watch(report)
        print(json.dumps(report, ensure_ascii=False))
        return 1

    age = now - last_ts
    report["log_age_s"] = round(age, 1)
    report["last_round"] = last.get("round")
    report["last_ts"] = last.get("ts")

    if age <= stale_limit:
        report.update({"status": "alive", "detail": f"日志新鲜 {age:.0f}s ≤ {stale_limit}s"})
        log_watch(report)
        print(json.dumps(report, ensure_ascii=False))
        return 0

    # 停转：查进程后恢复
    procs = find_bootstrap_procs()
    report["procs"] = [{"pid": p["pid"]} for p in procs]
    if procs:
        report["proc_status"] = "stale_running"
        log_watch(report)
        if not args.check_only:
            for p in procs:
                subprocess.run(["taskkill", "/F", "/PID", p["pid"]],
                               capture_output=True, timeout=30)
    else:
        report["proc_status"] = "not_running"
        log_watch(report)
    res = restart(args.check_only)
    report.update(res)
    report["status"] = "recovered" if res.get("action") == "restarted" else (
        "would_recover" if res.get("action") == "would_restart" else "recover_failed")
    log_watch(report)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] in ("recovered", "would_recover") else 2


if __name__ == "__main__":
    sys.exit(main())
