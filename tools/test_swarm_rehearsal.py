# -*- coding: utf-8 -*-
"""test_swarm_rehearsal.py · M1 真实接入联调彩排（可重复版，2026-08-29）

B 守护（dsh-memory/llm-adapter-poc/swarm_b/swarm_b_node.py）以真实子进程
运行，A 侧协议栈经总线目录异步交互——验证进程间全链路（非同进程模拟）。
前置：B 守护脚本存在（dsh-memory 与主仓库同机部署）。
"""
import sys, os, shutil, tempfile, time, json, subprocess
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from swarm_m1 import Bus, Node, make_msg

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


B_SCRIPT = r"D:\Program Files\2_ai\dsh-memory\llm-adapter-poc\swarm_b\swarm_b_node.py"
if not os.path.exists(B_SCRIPT):
    print(f"[✘] B 守护脚本缺失: {B_SCRIPT}")
    sys.exit(1)

tmp = tempfile.mkdtemp(prefix="swarm_rehearsal_")
root = os.path.join(tmp, "bus")
proc = None
try:
    proc = subprocess.Popen(
        [sys.executable, B_SCRIPT, "--root", root, "--me", "nodeB",
         "--peer", "nodeA", "--interval", "0.4"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace")
    time.sleep(2)  # B 守护启动并广播 HELLO

    bus = Bus(root)
    a = Node("nodeA", bus, ["校验"])
    a.poll()  # 收 B 的 HELLO
    check("HELLO 跨进程到达", a.peers.get("nodeB") == ["info"],
          f"got {a.peers}")

    # CAP_QUERY：发→等 B 轮询回复（异步，轮询窗口 8s）
    q = make_msg("CAP_QUERY", "nodeA", "nodeB", {"capability": "info"})
    bus.send(q)
    reply = None
    deadline = time.time() + 8
    while time.time() < deadline and not reply:
        for m in bus.recv("nodeA"):
            if m["type"] == "CAP_REPLY" and m.get("reply_to") == q["id"]:
                reply = m["payload"]
        time.sleep(0.4)
    check("CAP_QUERY 异步回复 ACCEPT", bool(reply) and reply["verdict"] == "ACCEPT",
          str(reply)[:60])

    # TASK → RESULT
    task = make_msg("TASK", "nodeA", "nodeB", {"capability": "info", "input": None})
    bus.send(task)
    result = None
    deadline = time.time() + 8
    while time.time() < deadline and not result:
        for m in bus.recv("nodeA"):
            if m["type"] == "RESULT":
                result = m["payload"]
        time.sleep(0.4)
    check("TASK 异步执行 RESULT 带 basis",
          bool(result) and "basis" in result, str(result)[:60])
finally:
    if proc:
        proc.terminate()
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"联调彩排: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
