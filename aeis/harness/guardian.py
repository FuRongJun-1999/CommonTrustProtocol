#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness.guardian · 灵枢守护进程（自维持第一层）
================================================
职责：检测 harness 心跳新鲜度（data/heartbeat.stamp）→ 失联则自动重启
harness（detached 独立进程）→ 守护日志。

自维持要求：
- harness 崩溃/挂死 → guardian 自动拉起（无需 ZCode/人工）
- 心跳 30 分钟一次；guardian 每 30s 检查，失联阈值 3 分钟（2 个心跳周期）
- 开机自启：由 Windows 计划任务拉起 guardian（登录时）

用法：python -m harness.guardian
"""
import json
import os
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # AEIS 根
sys.path.insert(0, BASE)

STAMP_PATH = os.path.join(BASE, "data", "heartbeat.stamp")
LOG_PATH = os.path.join(BASE, "data", "guardian.log")
PYTHON = sys.executable
CHECK_INTERVAL = 30          # 检查间隔（秒）
STALE_THRESHOLD = 180        # 失联阈值（秒）：心跳 30 分钟，但失联 3 分钟即拉起
RESTART_COOLDOWN = 60        # 重启冷却（防止反复拉起）

_last_restart = 0.0


def log_line(text: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}"
    print(line, flush=True)
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def read_stamp() -> float:
    """读心跳戳时间戳；无文件返回 0。"""
    try:
        with open(STAMP_PATH, "r", encoding="utf-8") as f:
            return float(json.load(f).get("ts", 0.0))
    except Exception:
        return 0.0


def harness_running() -> bool:
    """harness.main 进程是否存活（按命令行精确匹配）。"""
    try:
        out = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'",
             "get", "ProcessId,CommandLine", "/format:list"],
            capture_output=True, text=True, timeout=15).stdout
        return "harness.main" in out
    except Exception:
        return True  # 检测失败不误判（保守：视为存活）


def start_harness() -> bool:
    """detached 启动 harness（独立进程，脱离 guardian 生命周期）。"""
    try:
        subprocess.Popen(
            [PYTHON, "-m", "harness.main", "--web", "--port", "8000"],
            cwd=BASE, creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as exc:
        log_line(f"拉起失败: {exc}")
        return False


def main():
    global _last_restart
    log_line(f"灵枢守护进程启动（间隔 {CHECK_INTERVAL}s，失联阈值 {STALE_THRESHOLD}s）")
    # 启动时检查：若 harness 不在则立即拉起
    if not harness_running():
        log_line("harness 不在运行，立即拉起")
        start_harness()
        _last_restart = time.time()
    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            if not harness_running():
                # 进程不在 → 自动拉起（冷却期内跳过）
                if time.time() - _last_restart > RESTART_COOLDOWN:
                    log_line("检测到 harness 进程消失，自动重启")
                    if start_harness():
                        _last_restart = time.time()
                continue
            # 进程在但心跳可能失联（挂死）
            stamp = read_stamp()
            age = time.time() - stamp
            if stamp > 0 and age > STALE_THRESHOLD \
                    and time.time() - _last_restart > RESTART_COOLDOWN:
                log_line(f"心跳失联（{age:.0f}s 无心跳），重启 harness")
                # 结束挂死进程后重启
                try:
                    subprocess.run(
                        ["powershell", "-NoProfile", "-Command",
                         "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" "
                         "| Where-Object { $_.CommandLine -like '*harness.main*' } "
                         "| ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"],
                        capture_output=True, timeout=15)
                except Exception:
                    pass
                time.sleep(2)
                if start_harness():
                    _last_restart = time.time()
        except Exception as exc:
            log_line(f"守护循环异常: {exc}")


if __name__ == "__main__":
    sys.exit(main())
