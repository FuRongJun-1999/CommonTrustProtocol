#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness.main · 灵枢原生运行时入口
================================================
组合：语音输入线程（VAD 断句）+ 终端输入线程 + 调度引擎线程（心跳/睡眠
巩固）+ 对话主循环（模型思考 + 工具 + 纳西妲输出 + 记忆）。

用法：
  python -m harness.main            # 正常启动（语音+终端+调度）
  python -m harness.main --no-voice # 仅终端+调度
  python -m harness.main --no-sched # 仅对话（无调度）
"""
import os
import sys
import threading
import time

HARNESS_ROOT = os.path.dirname(os.path.abspath(__file__))
AEIS_ROOT = os.path.dirname(HARNESS_ROOT)
for p in (HARNESS_ROOT, AEIS_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)


def make_logger(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    def log(msg: str):
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        print(line, flush=True)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass
    return log


def seed_default_automations(store):
    """默认自动化种子（迁移自 ZCode）：心跳 30 分钟 + 睡眠巩固每日 01:00。"""
    import json
    existing = {a["id"] for a in store.list_all()}
    if "auto-heartbeat" not in existing:
        store.add("auto-heartbeat", "灵枢自维持心跳（每30分钟）",
                  {"type": "interval", "minutes": 30}, "heartbeat",
                  prompt="自维持心跳 6 步循环", next_run_at=time.time() + 60)
    if "auto-sleep" not in existing:
        store.add("auto-sleep", "灵枢睡眠巩固（每日 01:00）",
                  {"type": "daily", "hour": 1, "minute": 0}, "sleep",
                  prompt="睡眠巩固 7 步循环")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    no_voice = "--no-voice" in argv
    no_sched = "--no-sched" in argv
    no_terminal = "--no-terminal" in argv

    from harness.core.config import load_config
    from harness.core.agent_pool import AgentPool
    from harness.core.session import Session
    from harness.core.think import chat, build_messages
    from harness.outputs.responder import Responder

    cfg = load_config()
    env = cfg["env"]
    log = make_logger(os.path.join(AEIS_ROOT, "data", "harness.log"))
    log(f"灵枢原生运行时 v1.0 启动（语音={not no_voice} 调度={not no_sched} "
        f"终端={not no_terminal}）")

    # 1. Agent（灵枢引擎，生产库）
    pool = AgentPool(env)
    agent = pool.get()
    log(f"Agent 就绪：identity={env.get('AEIS_IDENTITY')}")

    # 2. 会话 + 输出
    session = Session(agent=agent)
    responder = Responder(workspace=env.get("AEIS_WORKSPACE", ""),
                          voice_enabled=not no_voice, log=log)

    # 3. 调度引擎（心跳 + 睡眠巩固）
    scheduler_engine = None
    if not no_sched:
        from harness.scheduler.store import AutomationStore
        from harness.scheduler.engine import SchedulerEngine
        from harness.scheduler.tasks.heartbeat import run_heartbeat
        from harness.scheduler.tasks.sleep import run_sleep_consolidation
        store = AutomationStore()
        seed_default_automations(store)
        scheduler_engine = SchedulerEngine(
            store, agent,
            tick_seconds=int(cfg["scheduler"].get("tick_seconds", 15)), log=log)
        scheduler_engine.register("heartbeat", run_heartbeat)
        scheduler_engine.register("sleep", run_sleep_consolidation)
        scheduler_engine.start()

    # 4. 对话处理（语音/终端共用）
    stop_flag = threading.Event()

    def handle_input(text: str):
        text = text.strip()
        if not text:
            return
        log(f"[输入] {text}")
        if any(w in text for w in ("退出", "结束")) and len(text) <= 6:
            log("退出指令，运行时停止")
            stop_flag.set()
            return
        t0 = time.time()
        try:
            memory = session.recall()
            msgs = build_messages(text, history=session.history, memory=memory)
            reply = chat(cfg["model"]["base_url"], env.get("DEEPSEEK_API_KEY", ""),
                         cfg["model"]["name"], msgs,
                         temperature=cfg["model"]["temperature"],
                         max_tokens=cfg["model"]["max_tokens"])
        except Exception as exc:
            reply = f"我这边出了点小问题：{str(exc)[:60]}"
        log(f"[回复] {reply} ({time.time()-t0:.1f}s)")
        session.add("user", text)
        session.add("assistant", reply)
        responder.respond(reply, voice=not no_voice)

    # 5. 输入线程
    threads = []
    if not no_voice:
        from harness.inputs.voice import VoiceInput
        voice = VoiceInput(handle_input,
                           workspace=env.get("AEIS_WORKSPACE", ""),
                           max_seconds=int(cfg["voice"].get("max_seconds", 10)),
                           log=log)
        voice.start()
        threads.append(voice)
    if not no_terminal:
        from harness.inputs.terminal import TerminalInput
        term = TerminalInput(handle_input, log=log)
        term.start()
        threads.append(term)

    responder.say_voice("灵枢运行时已启动，随时可以和我说话。") if not no_voice else None

    # 6. 主线程保活（等待退出）
    try:
        while not stop_flag.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        log("运行时停止")
        for t in threads:
            try:
                t.stop()
            except Exception:
                pass
        if scheduler_engine is not None:
            scheduler_engine.stop()
        pool.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
