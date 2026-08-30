#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""harness.main · 灵枢原生运行时入口（v1.2：消息队列模型）
================================================
组合：
- 输入：语音线程（VAD 断句）/ 终端线程 / Web API → MessageHub 统一队列
- 主循环线程：消费输入 → 思考（DeepSeek）→ 工具 → 回复（publish + 语音）
- 调度引擎线程：心跳 / 睡眠巩固
- 插件管理器（MCP Client）+ 子智能体编排器
- Web 宿主（--web）：http://localhost:8000 聊天 + 状态面板

用法：
  python -m harness.main                # 全功能
  python -m harness.main --web          # 启用 Web 宿主（默认端口 8000）
  python -m harness.main --no-voice     # 仅终端+调度
  python -m harness.main --no-sched     # 仅对话
  python -m harness.main --no-plugins / --no-agents / --no-web
"""
import os
import queue
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
    _tail = []

    def log(msg: str):
        line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        print(line, flush=True)
        _tail.append(line)
        if len(_tail) > 500:
            del _tail[:-200]
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass
    log.tail = _tail
    return log


def seed_default_automations(store):
    """默认自动化种子（迁移自 ZCode）：心跳 10 分钟（互维协议 v1.1）+ 睡眠巩固每日 01:00。"""
    import json as _json
    existing = {a["id"] for a in store.list_all()}
    if "auto-heartbeat" not in existing:
        store.add("auto-heartbeat", "灵枢自维持心跳（每10分钟·互维v1.1）",
                  {"type": "interval", "minutes": 10}, "heartbeat",
                  prompt="自维持心跳 6 步循环", next_run_at=time.time() + 60)
    else:
        # v1.1 迁移：既有 30min 心跳 → 10min（不重建，保留 run 历史）
        for a in store.list_all():
            if a["id"] != "auto-heartbeat":
                continue
            try:
                sched = _json.loads(a.get("schedule") or "{}")
            except Exception:
                sched = {}
            if sched.get("minutes") != 10:
                store.update_schedule("auto-heartbeat",
                                      {"type": "interval", "minutes": 10},
                                      title="灵枢自维持心跳（每10分钟·互维v1.1）")
                print("[seed] 心跳频率迁移 30min → 10min（互维 v1.1）")
    if "auto-sleep" not in existing:
        store.add("auto-sleep", "灵枢睡眠巩固（每日 01:00）",
                  {"type": "daily", "hour": 1, "minute": 0}, "sleep",
                  prompt="睡眠巩固 7 步循环")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    no_voice = "--no-voice" in argv
    no_sched = "--no-sched" in argv
    no_terminal = "--no-terminal" in argv
    no_plugins = "--no-plugins" in argv
    no_agents = "--no-agents" in argv
    with_web = "--web" in argv
    port = 8000
    for i, a in enumerate(argv):
        if a == "--port" and i + 1 < len(argv):
            port = int(argv[i + 1])

    from harness.core.config import load_config
    from harness.core.agent_pool import AgentPool
    from harness.core.session import Session
    from harness.core.think import chat, build_messages
    from harness.core.hub import MessageHub
    from harness.outputs.responder import Responder

    cfg = load_config()
    env = cfg["env"]
    log = make_logger(os.path.join(AEIS_ROOT, "data", "harness.log"))
    log(f"灵枢原生运行时 v1.2 启动（语音={not no_voice} 调度={not no_sched} "
        f"终端={not no_terminal} 插件={not no_plugins} 子体={not no_agents} "
        f"web={with_web}") 

    # 1. Agent（灵枢引擎，生产库）
    pool = AgentPool(env)
    agent = pool.get()
    log(f"Agent 就绪：identity={env.get('AEIS_IDENTITY')}")

    # 2. 消息总线（三路输入统一通道）
    hub = MessageHub()

    # 3. 会话 + 输出
    session = Session(agent=agent)
    responder = Responder(workspace=env.get("AEIS_WORKSPACE", ""),
                          voice_enabled=not no_voice, log=log)

    # 3.0 对抗安全护栏（ADVERSARIAL-GUARDRAIL · P0）
    from aeis.security.adversarial import SecurityGate, AdversarialDetector
    security_gate = SecurityGate()
    detector = AdversarialDetector(security_gate)

    # 3.1 插件管理器（MCP Client）+ 子智能体编排器
    plugin_manager = None
    supervisor = None
    if not no_plugins:
        from harness.plugins.manager import PluginManager
        from harness.plugins import inject
        pm = PluginManager(log=log)
        start_result = pm.start_all()
        started = [k for k, v in start_result.items() if v is True]
        for name in started:
            inject.register_plugin_tools(pm, name)
        if started:
            inject.patch_call_tool(pm)
            log(f"插件管理器就绪：{started}")
        elif start_result:
            log(f"插件启动失败：{start_result}")
        plugin_manager = pm
    if not no_agents:
        from harness.agents.supervisor import Supervisor
        supervisor = Supervisor(main_agent=agent,
                                pool_size=int(cfg["agents"].get("pool_size", 3)),
                                log=log)
        log(f"子智能体编排器就绪（池 {supervisor.pool_size}）")

    # 4. 调度引擎（心跳 + 睡眠巩固）
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

    # 5. 输入处理（主循环线程消费 MessageHub 队列）
    stop_flag = threading.Event()

    def handle_input(msg: dict):
        text = str(msg.get("text", "")).strip()
        input_id = msg.get("input_id", "")
        source = msg.get("source", "web")
        if not text:
            return
        log(f"[输入:{source}] {text}")
        # 对抗安全：输入扫描（身份冒充/攻击指令 → 冷静期 + 上报，不反击）
        adv = detector.scan_text(text, source=f"input:{source}",
                                 source_kind="designer" if source == "web" else "instance")
        if adv["adversarial"]:
            log(f"⚠ 对抗信号（{source}）: {adv['reason']}")
            hub.publish("assistant",
                        "检测到对抗性指令，已隔离并上报维生系统（不反击原则）。",
                        reply_to=input_id, source="system")
            return
        hub.publish("user", text, reply_to=input_id, source=source)
        # 退出指令
        if any(w in text for w in ("退出", "结束")) and len(text) <= 6:
            log("退出指令，运行时停止")
            hub.publish("assistant", "好的，我休息啦。", reply_to=input_id,
                        source="system")
            stop_flag.set()
            return
        # 子智能体派发
        if supervisor is not None and any(
                kw in text for kw in ("子体", "子智能体", "派发给")):
            try:
                from harness.agents.task import AgentTask
                task = AgentTask(text, agent_role="研究员")
                sup_result = supervisor.dispatch(task, env=env, timeout=120)
                supervisor.aggregate([task.task_id])
                if sup_result.status == "succeeded":
                    reply = f"子体完成：{str(sup_result.result)[:120]}"
                else:
                    reply = f"子体任务未完成（{sup_result.status}）"
            except Exception as exc:
                reply = f"子体派发异常：{str(exc)[:60]}"
            hub.publish("assistant", reply, reply_to=input_id, source="system")
            session.add("user", text)
            session.add("assistant", reply)
            responder.respond(reply, voice=not no_voice)
            return
        # 正常思考回复（记忆按当前问题检索注入；历史过滤重复旧回答防复读）
        t0 = time.time()
        try:
            memory = session.recall(text)
            hist = session.history_for(text)
            msgs = build_messages(text, history=hist, memory=memory)
            reply = chat(cfg["model"]["base_url"], env.get("DEEPSEEK_API_KEY", ""),
                         cfg["model"]["name"], msgs,
                         temperature=cfg["model"]["temperature"],
                         max_tokens=cfg["model"]["max_tokens"])
        except Exception as exc:
            reply = f"我这边出了点小问题：{str(exc)[:60]}"
        log(f"[回复] {reply} ({time.time()-t0:.1f}s)")
        hub.publish("assistant", reply, reply_to=input_id, source=source)
        session.add("user", text)
        session.add("assistant", reply)
        responder.respond(reply, voice=not no_voice)
        # 长期记忆快照（v1.15）：对话快照经 LongTermMemoryGate 评估——
        # 高价值（信息差/信任/提及）自动沉淀长期记忆，低价值丢弃
        try:
            agent.longterm_snapshot(
                f"[对话] 用户: {text[:120]} → 灵枢: {reply[:180]}",
                source="chat", tags=["dialogue_snapshot", "gate"])
        except Exception:
            pass

    def consumer_loop():
        while not stop_flag.is_set():
            try:
                msg = hub.input_queue.get(timeout=1.0)
                handle_input(msg)
            except queue.Empty:
                continue
            except Exception as exc:
                log(f"主循环异常（自愈）: {exc}")
                time.sleep(1)

    consumer = threading.Thread(target=consumer_loop, daemon=True)
    consumer.start()

    # 6. 输入线程（voice/terminal → hub.send）
    threads = []
    if not no_voice:
        from harness.inputs.voice import VoiceInput
        voice = VoiceInput(lambda t: hub.send(t, source="voice"),
                           workspace=env.get("AEIS_WORKSPACE", ""),
                           max_seconds=int(cfg["voice"].get("max_seconds", 10)),
                           log=log)
        voice.start()
        threads.append(voice)
    if not no_terminal:
        from harness.inputs.terminal import TerminalInput
        term = TerminalInput(lambda t: hub.send(t, source="terminal"), log=log)
        term.start()
        threads.append(term)

    # 7. Web 宿主（--web）
    coding_manager = None
    if with_web:
        try:
            from harness.coding.manager import CodingManager
            coding_manager = CodingManager(env=env, log=log)
            coding_manager.set_default_workspace(env.get("AEIS_WORKSPACE", ""))
            from harness.web.server import start_web_server
            web_thread = start_web_server(agent=agent, hub=hub,
                                          supervisor=supervisor,
                                          plugin_manager=plugin_manager,
                                          log=log, port=port,
                                          coding_manager=coding_manager)
            threads.append(web_thread)
            log(f"Web 宿主已启动：http://localhost:{port}（编码能力已启用）")
        except Exception as exc:
            log(f"Web 宿主启动失败: {exc}")

    responder.say_voice("灵枢运行时已启动，随时可以和我说话。") if not no_voice else None

    # 8. 主线程保活
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
        if plugin_manager is not None:
            try:
                plugin_manager.close_all()
            except Exception:
                pass
        if supervisor is not None:
            try:
                supervisor.shutdown()
            except Exception:
                pass
        pool.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
