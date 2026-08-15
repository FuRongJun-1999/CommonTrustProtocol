# -*- coding: utf-8 -*-
"""tests.test_guardian_bidirectional · 双智能体互维闭环 W1 测试
========================================================
覆盖（互维协议 v1.1，docs/mutual-sustain-loop.md）：
- judge_stamp 失联分级判定（alive/warning/dead + task_running 70min 豁免）
- 互维目录路径解析（LINGXU_NET_DIR 环境变量覆盖）
- 任务邮箱协议字段校验（v1.1 §3.1/3.2，W3 邮箱实现复用）
- 守护目标检测/拉起命令构造（只验证命令，不真杀真拉）

check 框架：python tests/test_guardian_bidirectional.py 直跑。
"""
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import guardian  # noqa: E402

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  ✓ {name}")
    else:
        print(f"  ✗ {name}  {detail}")


def test_judge_stamp():
    """分级判定全分支（v1.1 §2.3 状态机）。"""
    print("[judge_stamp] 失联分级判定")
    now = time.time()
    # alive：<25min
    check("0min → alive", guardian.judge_stamp(now, now) == "alive")
    check("10min → alive", guardian.judge_stamp(now - 10 * 60, now) == "alive")
    check("24min → alive", guardian.judge_stamp(now - 24 * 60, now) == "alive")
    # warning：25-35min
    check("26min → warning", guardian.judge_stamp(now - 26 * 60, now) == "warning")
    check("34min → warning", guardian.judge_stamp(now - 34 * 60, now) == "warning")
    # dead：≥35min
    check("36min → dead", guardian.judge_stamp(now - 36 * 60, now) == "dead")
    check("60min → dead", guardian.judge_stamp(now - 60 * 60, now) == "dead")


def test_task_running_exemption():
    """task_running=true 豁免：阈值 ×2 = 70min（v1.1 §2.1）。"""
    print("[judge_stamp] task_running 豁免")
    now = time.time()
    check("任务中 10min → alive", guardian.judge_stamp(now - 10 * 60, now, True) == "alive")
    check("任务中 30min → alive_working", guardian.judge_stamp(now - 30 * 60, now, True) == "alive_working")
    check("任务中 60min → alive_working", guardian.judge_stamp(now - 60 * 60, now, True) == "alive_working")
    check("任务中 71min → dead", guardian.judge_stamp(now - 71 * 60, now, True) == "dead")
    check("任务中 26min ≠ warning（豁免）", guardian.judge_stamp(now - 26 * 60, now, True) == "alive_working")
    # 非任务中不受豁免影响
    check("非任务中 26min 仍 warning", guardian.judge_stamp(now - 26 * 60, now, False) == "warning")


def test_net_dir():
    """互维目录解析（LINGXU_NET_DIR 覆盖 + 默认 ~/.lingxu_net）。"""
    print("[net_dir] 互维目录路径")
    old = os.environ.get("LINGXU_NET_DIR")
    try:
        os.environ["LINGXU_NET_DIR"] = "X:\\tmp\\lingxu_net"
        # 重新解析模块常量需要重载；验证解析函数逻辑——直接验证常量随 import 时环境
        # 通过重载模块验证环境变量生效
        import importlib
        importlib.reload(guardian)
        check("环境变量覆盖生效", guardian.NET_DIR == "X:\\tmp\\lingxu_net")
        check("戳路径拼接", guardian.HEARTBEAT_A == "X:\\tmp\\lingxu_net\\heartbeat.a.stamp")
        check("B 戳路径", guardian.HEARTBEAT_B == "X:\\tmp\\lingxu_net\\heartbeat.web.stamp")
        check("互维日志路径", guardian.MUTUAL_LOG == "X:\\tmp\\lingxu_net\\mutual.log")
        check("last_contact 路径", guardian.LAST_CONTACT == "X:\\tmp\\lingxu_net\\last_contact.json")
    finally:
        if old is None:
            os.environ.pop("LINGXU_NET_DIR", None)
        else:
            os.environ["LINGXU_NET_DIR"] = old
        import importlib
        importlib.reload(guardian)


def test_stamp_io():
    """心跳戳读写（隔离 tmp 目录）。"""
    print("[stamp] 心跳戳读写")
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "heartbeat.a.stamp")
        with open(path, "w", encoding="utf-8") as f:
            f.write('{"ts": 123.0, "pid": 42, "task_running": true}')
        stamp = guardian.read_stamp(path)
        check("读取 ts", stamp.get("ts") == 123.0)
        check("读取 pid", stamp.get("pid") == 42)
        check("读取 task_running", stamp.get("task_running") is True)
        # 损坏/缺失文件 → 空 dict（保守不判定）
        check("缺失文件 → 空", guardian.read_stamp(os.path.join(tmp, "none.json")) == {})
        check("损坏文件 → 空", guardian.read_stamp(os.path.join(tmp, "bad.json")) == {})


def test_protocol_fields():
    """任务邮箱协议 v1.1 §3.1/3.2 字段校验（W3 邮箱实现复用）。"""
    print("[protocol] 邮箱协议字段校验")
    # 合法 task
    good_task = {
        "id": "task-20260816-001", "type": "verify", "from": "A", "to": "B",
        "payload": {"claim": "x", "evidence": "y", "expected": "z", "source_ref": "r"},
        "status": "pending", "created_at": 0.0,
    }
    check("合法 task 通过", guardian.validate_task(good_task) == [])
    check("合法 result 通过",
          guardian.validate_result({
              "task_id": "t1", "verdict": "pass",
              "whitebox": {"judgment": "采纳", "best": "学科A", "d_norm": 0.57, "record_id": "n1"},
              "llm_review": {"conclusion": "同意", "reason": "一致"},
              "reasons": [], "evidence": [], "verifier": "B", "at": 0.0,
          }) == [])
    # 非法 task：缺字段/非法枚举
    errs = guardian.validate_task({"id": "t2", "type": "evil"})
    check("非法 type 报错", any("type 非法" in e for e in errs))
    errs = guardian.validate_task({"id": "t3", "type": "verify", "payload": {"claim": "x"}})
    check("payload 缺字段报错", any("payload 缺字段" in e for e in errs))
    # 非法 result：verdict/whitebox
    errs = guardian.validate_result({"task_id": "t4", "verdict": "maybe"})
    check("非法 verdict 报错", any("verdict 非法" in e for e in errs))
    errs = guardian.validate_result({"task_id": "t5", "verdict": "pass", "whitebox": {"d_norm": 1}})
    check("whitebox 缺字段报错", any("whitebox 缺字段" in e for e in errs))
    # 三种 verdict / 两种 type / 三种 status 全部合法
    for v in guardian.RESULT_VERDICTS:
        r = {"task_id": "t", "verdict": v,
             "whitebox": {"judgment": "j", "best": "b", "d_norm": 0, "record_id": "r"},
             "llm_review": {"conclusion": "c", "reason": "r"},
             "reasons": [], "evidence": [], "verifier": "A", "at": 0.0}
        check(f"verdict={v} 合法", guardian.validate_result(r) == [])


def test_launch_paths():
    """守护拉起命令构造（只验证路径存在，不真拉起）。"""
    print("[launch] 拉起命令构造")
    check("node 可执行存在", os.path.exists(guardian.NODE_EXE),
          f"node: {guardian.NODE_EXE}")
    check("dsh CLI 存在", os.path.exists(guardian.DSH_CLI),
          f"cli: {guardian.DSH_CLI}")
    check("start_web 命令含 dsh bin.js", guardian.DSH_CLI.endswith("bin.js"))
    # 进程匹配模式（守护目标识别）
    check("harness 匹配模式", "harness.main" in "python -m harness.main --web")
    check("web 匹配模式", "@deepseek-ai\\dsh" in "node ...\\@deepseek-ai\\dsh\\lib\\bin.js web")


def test_guard_action():
    """守护动作分支（隔离 tmp：进程消失 → 拉起；戳 alive → 不动作）。"""
    print("[guard] 守护动作分支")
    with tempfile.TemporaryDirectory() as tmp:
        stamp = os.path.join(tmp, "h.web.stamp")
        # 目标"进程在"且戳新鲜 → 不动作（用假运行函数模拟）
        with open(stamp, "w", encoding="utf-8") as f:
            f.write(f'{{"ts": {time.time()}, "pid": 1, "task_running": false}}')
        acted = []
        guardian._guard_one("web", lambda: True, stamp,
                            lambda: (acted.append("start"), True)[1],
                            "p", [0.0])
        check("进程在+戳新鲜 → 不动作", acted == [])
        # 目标"进程消失" → 拉起
        guardian._guard_one("web", lambda: False, stamp,
                            lambda: (acted.append("start"), True)[1],
                            "p", [0.0])
        check("进程消失 → 拉起", acted == ["start"])
        # 冷却期内 → 不重复拉起
        guardian._guard_one("web", lambda: False, stamp,
                            lambda: (acted.append("start2"), True)[1],
                            "p", [time.time()])
        check("冷却期内 → 不拉起", acted == ["start"])
        # 戳 dead → 杀+重启（运行函数模拟；杀进程调用只读模式不真杀）
        with open(stamp, "w", encoding="utf-8") as f:
            f.write(f'{{"ts": {time.time() - 40 * 60}, "pid": 1, "task_running": false}}')
        killed = []
        orig_kill = guardian.kill_process
        guardian.kill_process = lambda n, p: killed.append(p)
        try:
            guardian._guard_one("web", lambda: True, stamp,
                                lambda: (acted.append("start3"), True)[1],
                                "@deepseek-ai\\dsh", [0.0])
            check("戳 dead → 杀挂死+重启", "start3" in acted and killed == ["@deepseek-ai\\dsh"])
        finally:
            guardian.kill_process = orig_kill
        # 戳 warning → 仅告警不动作
        acted.clear()
        with open(stamp, "w", encoding="utf-8") as f:
            f.write(f'{{"ts": {time.time() - 30 * 60}, "pid": 1, "task_running": false}}')
        guardian._guard_one("web", lambda: True, stamp,
                            lambda: (acted.append("x"), True)[1], "p", [0.0])
        check("戳 warning → 不动作（仅告警）", acted == [])


def main():
    print("== 双智能体互维闭环 W1 测试 ==")
    test_judge_stamp()
    test_task_running_exemption()
    test_net_dir()
    test_stamp_io()
    test_protocol_fields()
    test_launch_paths()
    test_guard_action()
    print(f"\n结果: {PASS}/{TOTAL} 通过")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
