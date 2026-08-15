#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness.guardian · 灵枢守护进程（自维持 · 双智能体互维闭环 v1.1）
====================================================================
互维协议 v1.1（docs/mutual-sustain-loop.md，沙箱 A/B 共同维护）：
- A 侧心跳戳由心跳任务写（~/.lingxu_net/heartbeat.a.stamp，10min，{ts,pid,task_running}）
- guardian 检测双方戳新鲜度 + 进程存活，失联分级判定后自动拉起

守护目标：
- harness（A 自身主循环）：进程消失 → 拉起；戳 dead 分级 → 杀挂死 + 重启
- web 实例（B，DSH web profile）：进程消失 → 拉起；heartbeat.web.stamp dead 分级 → 杀挂死 + 重启

失联判定状态机（v1.1 §2.3）：
  now-ts < 25min                  → alive
  25min ≤ now-ts < 35min          → warning（写 mutual.log 告警，不行动）
  ts.task_running=true            → alive_working（豁免，阈值 ×2 = 70min）
  now-ts ≥ 35min（豁免后 70min）   → dead（wmic 确认 → 杀挂死 + detached 重启）

幂等：拉起前确认目标不存在 + 60s 冷却（RESTART_COOLDOWN）。
互维记录：mutual.log（告警/守护动作）+ last_contact.json（读到对方戳的时间，双亡告警用）。

用法：python -m harness.guardian
"""
import json
import os
import shutil
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # AEIS 根
sys.path.insert(0, BASE)

# ---- 互维网络目录（v1.1 §1，环境变量可覆盖） ----
NET_DIR = os.environ.get("LINGXU_NET_DIR",
                         os.path.join(os.path.expanduser("~"), ".lingxu_net"))
HEARTBEAT_A = os.path.join(NET_DIR, "heartbeat.a.stamp")    # A 写（心跳任务）
HEARTBEAT_B = os.path.join(NET_DIR, "heartbeat.web.stamp")  # B 写（mutual.js）
MUTUAL_LOG = os.path.join(NET_DIR, "mutual.log")
LAST_CONTACT = os.path.join(NET_DIR, "last_contact.json")

# ---- 分级判定参数（v1.1 §2.1，荣终裁） ----
ALIVE_MIN = 25          # <25min 正常
WARNING_MIN = 35        # 25-35min 告警
DEAD_MIN = 35           # ≥35min dead
TASK_FACTOR = 2         # task_running=true 时阈值 ×2（70min）

CHECK_INTERVAL = 30          # 检查间隔（秒）
RESTART_COOLDOWN = 60        # 重启冷却（防反复拉起）

# ---- 任务验证邮箱协议字段（v1.1 §3.1/3.2，W3 邮箱实现复用） ----
TASK_FIELDS = {"id", "type", "from", "to", "payload", "status", "created_at"}
TASK_PAYLOAD_FIELDS = {"claim", "evidence", "expected", "source_ref"}
TASK_TYPES = {"verify", "knowledge_sync"}
TASK_STATUSES = {"pending", "processing", "done"}
RESULT_FIELDS = {"task_id", "verdict", "whitebox", "llm_review", "reasons",
                 "evidence", "verifier", "at"}
RESULT_VERDICTS = {"pass", "fail", "needs_revision"}
WHITEBOX_FIELDS = {"judgment", "best", "d_norm", "record_id"}
LLM_REVIEW_FIELDS = {"conclusion", "reason"}

# ---- 进程/启动参数 ----
NODE_EXE = shutil.which("node") or r"C:\Program Files\nodejs\node.exe"
DSH_CLI = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm",
                       "node_modules", "@deepseek-ai", "dsh", "lib", "bin.js")

_last_h = [0.0]  # harness 重启冷却（可变容器，_guard_one 原地更新）
_last_w = [0.0]  # web 重启冷却


# ---------- 互维判定 ----------

def judge_stamp(ts: float, now: float, task_running: bool = False) -> str:
    """失联分级判定（v1.1 §2.3）。返回 alive / warning / alive_working / dead。
    task_running=true：任务执行中戳不更新 ≠ 失联，阈值 ×2（70min）。"""
    age = now - ts
    if age < ALIVE_MIN * 60:
        return "alive"
    if task_running:
        return "alive_working" if age < DEAD_MIN * 60 * TASK_FACTOR else "dead"
    if age < WARNING_MIN * 60:
        return "warning"
    return "dead"


def read_stamp(path: str) -> dict:
    """读心跳戳；无文件/损坏返回空 dict（保守：不判定）。"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def validate_task(task: dict) -> list:
    """邮箱协议 v1.1 §3.1 字段校验。返回缺失/非法字段列表（空 = 合法）。"""
    errs = []
    missing = TASK_FIELDS - set(task)
    if missing:
        errs.append(f"缺字段: {sorted(missing)}")
    if task.get("type") not in TASK_TYPES:
        errs.append(f"type 非法: {task.get('type')}")
    if task.get("status") not in TASK_STATUSES:
        errs.append(f"status 非法: {task.get('status')}")
    payload = task.get("payload") or {}
    if not isinstance(payload, dict):
        errs.append("payload 必须是对象")
    else:
        pmiss = TASK_PAYLOAD_FIELDS - set(payload)
        if pmiss:
            errs.append(f"payload 缺字段: {sorted(pmiss)}")
    return errs


def validate_result(result: dict) -> list:
    """邮箱协议 v1.1 §3.2 字段校验。返回缺失/非法字段列表（空 = 合法）。"""
    errs = []
    missing = RESULT_FIELDS - set(result)
    if missing:
        errs.append(f"缺字段: {sorted(missing)}")
    if result.get("verdict") not in RESULT_VERDICTS:
        errs.append(f"verdict 非法: {result.get('verdict')}")
    wb = result.get("whitebox") or {}
    if not isinstance(wb, dict):
        errs.append("whitebox 必须是对象")
    else:
        wmiss = WHITEBOX_FIELDS - set(wb)
        if wmiss:
            errs.append(f"whitebox 缺字段: {sorted(wmiss)}")
    lr = result.get("llm_review") or {}
    if not isinstance(lr, dict):
        errs.append("llm_review 必须是对象")
    else:
        lmiss = LLM_REVIEW_FIELDS - set(lr)
        if lmiss:
            errs.append(f"llm_review 缺字段: {sorted(lmiss)}")
    return errs


# ---------- 记录 ----------

def log_line(text: str):
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}"
    print(line, flush=True)
    try:
        os.makedirs(NET_DIR, exist_ok=True)
        with open(MUTUAL_LOG, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def touch_contact(partner: str = "B"):
    """记录最后读到对方戳的时间（v1.1 §6 双亡告警用）。"""
    try:
        os.makedirs(NET_DIR, exist_ok=True)
        with open(LAST_CONTACT, "w", encoding="utf-8") as f:
            f.write(json.dumps({"ts": time.time(), "last_partner": partner}))
    except Exception:
        pass


# ---------- 进程检测 / 拉起 / 击杀 ----------

def _ps_ids(name_filter: str, pattern: str) -> list:
    """按可执行名 + CommandLine 子串查进程 id（powershell 只读查询）。"""
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-CimInstance Win32_Process -Filter \"Name='{name_filter}'\" "
             f"| Where-Object {{ $_.CommandLine -like '*{pattern}*' }} "
             f"| Select-Object -ExpandProperty ProcessId"],
            capture_output=True, text=True, timeout=15)
        return [int(x) for x in out.stdout.split() if x.strip().isdigit()]
    except Exception:
        return []


def harness_running() -> bool:
    """harness.main 进程是否存活（按命令行精确匹配）。检测失败不误判（保守）。"""
    return bool(_ps_ids("python.exe", "harness.main"))


def web_running() -> bool:
    """DSH web 实例进程是否存活（node + dsh bin.js web 特征）。"""
    return bool(_ps_ids("node.exe", "@deepseek-ai\\dsh"))


def _detached(cmd: list) -> bool:
    try:
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as exc:
        log_line(f"拉起失败: {exc}")
        return False


def start_harness() -> bool:
    """detached 启动 harness（独立进程，脱离 guardian 生命周期）。"""
    return _detached([sys.executable, "-m", "harness.main", "--web", "--port", "8000"])


def start_web() -> bool:
    """detached 启动 DSH web 实例（沙箱 B：node dsh/bin.js web）。"""
    return _detached([NODE_EXE, DSH_CLI, "web"])


def kill_process(name_filter: str, pattern: str) -> None:
    """按命令行精确匹配杀进程（防误杀：只杀目标模式）。"""
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             f"Get-CimInstance Win32_Process -Filter \"Name='{name_filter}'\" "
             f"| Where-Object {{ $_.CommandLine -like '*{pattern}*' }} "
             f"| ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force }}"],
            capture_output=True, timeout=15)
    except Exception:
        pass


# ---------- 单目标守护 ----------

def _guard_one(name: str, running_fn, stamp_path: str, start_fn, kill_pattern: str,
               last_ref: list):
    """守护单个目标（v1.1 §2.3 状态机）：
    进程消失 → 拉起；进程在但戳 dead 分级 → 杀挂死 + 重启；warning → 仅告警。"""
    if not running_fn():
        if time.time() - last_ref[0] > RESTART_COOLDOWN:
            log_line(f"[守护] {name} 进程消失，自动拉起")
            if start_fn():
                last_ref[0] = time.time()
        return
    stamp = read_stamp(stamp_path)
    if not stamp:
        return  # 无戳不判定（保守）
    judge = judge_stamp(float(stamp.get("ts", 0)), time.time(),
                        bool(stamp.get("task_running", False)))
    if judge == "alive" or judge == "alive_working":
        return
    if judge == "warning":
        log_line(f"[告警] {name} 心跳失联（25-35min 分级），观察中")
        return
    # dead
    if time.time() - last_ref[0] <= RESTART_COOLDOWN:
        return
    log_line(f"[守护] {name} 心跳失联（dead 分级），杀挂死 + 重启")
    kill_process("python.exe" if name == "harness" else "node.exe", kill_pattern)
    time.sleep(2)
    if start_fn():
        last_ref[0] = time.time()


def main():
    log_line(f"灵枢互维守护启动（v1.1：{ALIVE_MIN}/{WARNING_MIN}min 分级，tick {CHECK_INTERVAL}s）")
    # 启动时检查：双目标不在则立即拉起
    if not harness_running():
        log_line("harness 不在运行，立即拉起")
        if start_harness():
            _last_h[0] = time.time()
    if not web_running():
        log_line("web 实例不在运行，立即拉起")
        if start_web():
            _last_w[0] = time.time()
    while True:
        time.sleep(CHECK_INTERVAL)
        try:
            _guard_one("harness", harness_running, HEARTBEAT_A, start_harness,
                       "harness.main", _last_h)
            # 守护 web 时读到 B 戳 → 记录末次互读（双亡告警用）
            _guard_one("web", web_running, HEARTBEAT_B, start_web,
                       "@deepseek-ai\\dsh", _last_w)
            if read_stamp(HEARTBEAT_B):
                touch_contact("B")
        except Exception as exc:
            log_line(f"守护循环异常: {exc}")


if __name__ == "__main__":
    sys.exit(main())
