# -*- coding: utf-8 -*-
"""test_swarm_orchestrator.py · 编排层批 1 验证（V-SO.1/2/3，2026-08-29）"""
import sys, os, shutil, tempfile, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from swarm_orchestrator import Registry, RoleNegotiator, ROLES, ProtocolError
from swarm_m3_trust import TrustLedger

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="so_b1_")
try:
    # ============ V-SO.1 节点注册（三节点，能力/信任/心跳可查） ============
    reg = Registry(os.path.join(tmp, "bus"))
    reg.register("nodeA", ["校验", "编排"])
    reg.register("nodeB", ["求和", "世界模型"])
    reg.register("nodeC", ["求和", "排序"])
    check("V-SO.1 三节点注册", len(reg.nodes) == 3)
    check("V-SO.1 按能力查询", reg.by_capability("求和") == ["nodeB", "nodeC"],
          f"got {reg.by_capability('求和')}")
    dead = reg.prune()
    check("V-SO.1 心跳新鲜不剔除", dead == [])

    # ============ V-SO.2 职责协商（OFFER→ACCEPT→租约；冲突信任高者得） ============
    trust = TrustLedger()
    trust.record("nodeB", True)   # nodeB 建立高信任
    trust.record("nodeC", False)  # nodeC 低信任
    trust.record("nodeC", False)
    neg_a = RoleNegotiator(None, "nodeA", trust)  # 编排者（bus 传 None 走本地断言）
    offer = neg_a.offer("verify", "nodeB")
    check("V-SO.2 ROLE_OFFER 构造", offer["payload"]["role"] == "verify")
    neg_a.confirm("verify", "nodeB")
    check("V-SO.2 租约登记", neg_a.holder("verify") == "nodeB")

    # 冲突：nodeC 也想要 verify → 信任高者得
    winner = neg_a.resolve_conflict("verify", "nodeB", "nodeC")
    check("V-SO.2 冲突信任高者得", winner == "nodeB",
          f"nodeB={trust.score('nodeB'):.2f} nodeC={trust.score('nodeC'):.2f}")

    # vitals 不可协商
    try:
        neg_a.offer("vitals", "nodeB")
        check("V-SO.2 vitals 不可协商", False, "未抛异常")
    except ProtocolError:
        check("V-SO.2 vitals 不可协商", True)

    # ============ V-SO.3 职责衰减（租约到期失效，可重协商） ============
    neg_b = RoleNegotiator(None, "nodeX", trust, ttl_s=1)  # 1s 短租约
    neg_b.confirm("reflect", "nodeX")
    check("V-SO.3 租约期内有效", neg_b.holder("reflect") == "nodeX")
    time.sleep(1.2)
    expired = neg_b.expire()
    check("V-SO.3 到期失效", expired == ["reflect"] and neg_b.holder("reflect") is None)
    neg_b.confirm("reflect", "nodeX")
    check("V-SO.3 重协商恢复", neg_b.holder("reflect") == "nodeX")

    # ============ V-SO.4 任务分解（DAG+环检测） ============
    from swarm_orchestrator import TaskGraph, Dispatcher
    dag = TaskGraph([
        {"id": "stat", "capability": "求和", "input": [1, 2], "depends_on": []},
        {"id": "sort", "capability": "排序", "input": [3, 1], "depends_on": ["stat"]},
        {"id": "verify", "capability": "校验", "input": None, "depends_on": ["sort"]},
    ])
    check("V-SO.4 DAG 拓扑序", dag.order == ["stat", "sort", "verify"], f"got {dag.order}")
    check("V-SO.4 就绪集计算", dag.ready(set()) == ["stat"])
    try:
        TaskGraph([{"id": "a", "capability": "x", "depends_on": ["b"]},
                   {"id": "b", "capability": "x", "depends_on": ["a"]}])
        check("V-SO.4 环显式报错", False, "未抛异常")
    except ProtocolError as e:
        check("V-SO.4 环显式报错", "环" in str(e), str(e))
    try:
        TaskGraph([{"id": "a", "capability": "x", "depends_on": ["ghost"]}])
        check("V-SO.4 未知依赖报错", False, "未抛异常")
    except ProtocolError as e:
        check("V-SO.4 未知依赖报错", "未知子任务" in str(e), str(e))

    # ============ V-SO.5 分派策略（能力过滤+信任排序） ============
    from swarm_orchestrator import Registry as _R
    reg2 = _R(os.path.join(tmp, "bus2"))
    reg2.register("nodeB", ["求和"])
    reg2.register("nodeC", ["求和"])
    disp = Dispatcher(reg2, trust)
    ok, det = disp.pick("求和")
    check("V-SO.5 信任排序选节点", ok and "nodeB" in det, det)
    ok2, det2 = disp.pick("求和", exclude={"nodeB", "nodeC"})
    check("V-SO.5 全排除显式报错", not ok2 and "无节点" in det2, det2)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"编排层批 1+2: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
