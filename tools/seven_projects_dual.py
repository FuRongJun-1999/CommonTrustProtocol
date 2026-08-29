# -*- coding: utf-8 -*-
"""seven_projects_dual.py · 7 终极工程双智能体实测（2026-08-29 荣指令）

反思单元（GLM-5.3-flash）想怎么做（产码/产程序），
验证单元（各域物理裁决）做验证（真执行比对），
fail 带证据回反思迭代——DualAgentSystem 闭环。
产出：tools/seven_projects_dual_report.json
"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))
sys.path.insert(1, os.path.join(ROOT, "aeis", "wisdom"))

from dual_agent import (FixedRecord, FixedOutput, ReflectAgent,
                        VerifyAgent, DualAgentSystem)
from dual_agent_llm import glm_implement  # 反思通道（产 Python 码）

MAX_T = 3

# ============ 各域物理裁决基底（L3 已验证路径复用） ============

def judge_mini_python(src):
    """工程 1：Mini-Python 程序真跑，结果比对。任务要求源码计算 Σi²(1..4)=30。"""
    from mini_python import run_program
    try:
        env = run_program(src)
        got = env.get("result")
        return (got == 30, f"Σi²(1..4) 预期 30，实得 {got}")
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def judge_compiler(src):
    """工程 2：中文源码 → 编译 → VM 运行，比对「结果」。"""
    try:
        sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))
        from core.compiler import compile_source
        from core.condition_vm import ConditionVM
        code, result = compile_source(src, strict=False)
        if not result.get("ok"):
            return False, "编译失败: " + "; ".join(str(x) for x in result.get("errors", [])[:3])
        vm = ConditionVM()
        state = vm.run(code, symbols={})
        got = state.get("symbols", {}).get("结果")
        return (got == 11, f"3加4乘2 预期 11，实得 {got}（halt={state.get('halt')}）")
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def make_graph_judge():
    """工程 6：图 BFS 最短路径——真跑比对（物理：算法执行）。"""
    graph = {1: [2, 3], 2: [4], 3: [4], 4: [5], 5: []}
    def judge(code):
        try:
            ns = {}
            exec(compile(code, "<impl>", "exec"), ns)
            ns["ns"] = ns
            bfs = ns.get("bfs_shortest")
            if bfs is None:
                return False, "未定义 bfs_shortest"
            for start, end, want in ((1, 5, 3), (1, 4, 2), (2, 5, 2), (1, 1, 0)):
                got = bfs(graph, start, end)
                if got != want:
                    return False, f"bfs({start},{end}) 预期 {want} 实得 {got}"
            return True, "4 组最短路径全对（物理执行）"
        except Exception as e:
            return False, f"{type(e).__name__}: {e}"
    return judge


def judge_os(code):
    """工程 4：工作窃取调度——真跑断言（总量守恒+均衡改善）。

    judge 重审修正（2026-08-29）：旧断言「非空队列数不增」与窃取语义
    矛盾——工作窃取的目的恰是让空/闲队列获得任务。真不变量=①总量
    守恒 ②均衡改善（极差缩小）。
    """
    try:
        ns = {}
        exec(compile(code, "<impl>", "exec"), ns)
        fn = ns.get("work_steal")
        if fn is None:
            return False, "未定义 work_steal(queues)"
        queues = [[1, 2, 3], [4, 5], [], [6]]
        total_before = sum(len(q) for q in queues)
        range_before = max(len(q) for q in queues) - min(len(q) for q in queues)
        result = fn([q[:] for q in queues])
        if not isinstance(result, list):
            return False, f"返回类型须为 list，得到 {type(result).__name__}"
        total_after = sum(len(q) for q in result)
        if total_after != total_before:
            return False, f"任务总数不守恒 {total_before}→{total_after}"
        lens = [len(q) for q in result]
        range_after = max(lens) - min(lens)
        if range_after >= range_before:
            return False, f"负载未均衡：极差 {range_before}→{range_after}"
        return True, (f"守恒 {total_after} 任务；极差 {range_before}→{range_after} "
                      f"（物理执行，窃取生效）")
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def judge_net(code):
    """工程 5：校验和——真跑往返一致 + 篡改检测。"""
    try:
        ns = {}
        exec(compile(code, "<impl>", "exec"), ns)
        calc = ns.get("checksum")
        if calc is None:
            return False, "未定义 checksum(data)"
        data = [1, 2, 3, 4]
        cs = calc(data)
        if calc(data) != cs:
            return False, "同数据两次计算不一致"
        if calc(data + [5]) == cs:
            return False, "数据变更校验和未变（无检测能力）"
        return True, f"checksum({data})={cs} 往返一致+篡改可检（物理执行）"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def judge_bt(code):
    """工程 7：蓝牙消息分帧——真跑组帧/解帧往返。"""
    try:
        ns = {}
        exec(compile(code, "<impl>", "exec"), ns)
        frame = ns.get("frame")
        deframe = ns.get("deframe")
        if frame is None or deframe is None:
            return False, "未定义 frame/deframe"
        for payload in ("HELLO", "A", ""):
            fr = frame(payload)
            back = deframe(fr)
            if back != payload:
                return False, f"分帧往返失败 {payload!r}→{fr!r}→{back!r}"
        return True, "3 组分帧往返全对（物理执行）"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


# ============ 七域任务定义 ============
DOMAINS = [
    {"name": "1-中文编程语言",
     "task": {"desc": "用 Mini-Python 语法写一段程序（变量/def/for/算术），"
                      "计算 1²+2²+3²+4² 的值并存入变量 result。"
                      "语法：赋值 x = 表达式；def 名(参数): 换行缩进 return；for i in range(n): 换行缩进",
              "lang": "mini-python"},
     "judge": judge_mini_python,
     "py": False},
    {"name": "2-中文编译器",
     "task": {"desc": "输出一行中文语法的程序源码（仅此一行；禁止输出解释器、函数、"
                      "注释或任何说明文字）：结果 = 3 加 4 乘 2；止。"
                      "规则：中文运算词 加/减/乘/除 组成表达式，分号后以「止。」结束。"
                      "你的全部输出必须恰好是这一行：结果 = 3 加 4 乘 2；止。",
              "lang": "中文"},
     "judge": judge_compiler,
     "py": False},
    {"name": "6-图数据库",
     "task": {"desc": "实现 Python 函数 bfs_shortest(graph, start, end)，"
                      "用 BFS 求无权图最短路径步数（start==end 返回 0，不可达返回 -1）。"
                      "graph 为 {节点: [邻居]} 字典。只输出代码块。"
                      "函数签名：def bfs_shortest(graph, start, end)",
              "lang": "python"},
     "judge": make_graph_judge(),
     "py": True},
    {"name": "4-操作系统",
     "task": {"desc": "实现 Python 函数 work_steal(queues)：工作窃取调度——"
                      "从任务多的队列偷任务给空队列，使负载均衡；不新增/丢失任务。"
                      "queues 为任务列表的列表，返回调度后的列表的列表。"
                      "示例：[[1,2,3],[4,5],[],[6]] → 总任务 6 个重新均衡。"
                      "硬性要求：顶层必须有 def work_steal(queues): 定义（调用方 exec 后"
                      "直接按名调用），只输出一个代码块。函数签名：def work_steal(queues)",
              "lang": "python"},
     "judge": judge_os,
     "py": True},
    {"name": "5-网络协议栈",
     "task": {"desc": "实现 Python 函数 checksum(data)：对整数列表计算校验和"
                      "（如求和取模 256），使同数据结果一致、数据变更结果不同。"
                      "只输出代码块。函数签名：def checksum(data)",
              "lang": "python"},
     "judge": judge_net,
     "py": True},
    {"name": "7-蓝牙互联网",
     "task": {"desc": "实现两个 Python 函数 frame(payload) 和 deframe(frame_data)："
                      "消息分帧/解帧——frame 把字符串加首尾标记成帧，deframe 还原原文，"
                      "往返必须一致（含空字符串）。只输出代码块。"
                      "函数签名：def frame(payload) / def deframe(frame_data)",
              "lang": "python"},
     "judge": judge_bt,
     "py": True},
]

# ============ 双智能体逐域闭环 ============

def main():
    report = {"domains": [], "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    import tempfile
    td = tempfile.mkdtemp(prefix="seven_dual_")
    for dom in DOMAINS:
        name = dom["name"]
        print(f"\n=== {name} ===", flush=True)
        record = FixedRecord(os.path.join(td, name[:8] + ".jsonl"))
        output = FixedOutput(os.path.join(td, name[:8] + "_out.jsonl"))
        # 反思单元：语言 1/2 产对应语法源码；其余产 Python
        if dom["py"]:
            reflect = ReflectAgent(glm_implement)
        else:
            reflect = ReflectAgent(lambda t, att, fail: glm_implement(t, att, fail))
        system = DualAgentSystem(reflect, VerifyAgent(dom["judge"]),
                                 record, output, max_attempts=MAX_T)
        r = system.execute(name, dom["task"])
        print(f"  → {r['status']} attempts={r.get('attempts')} "
              f"evidence={str(r.get('evidence', r.get('last_evidence','')))[:60]}", flush=True)
        report["domains"].append({"name": name, **{k: v for k, v in r.items()
                                                   if k in ("status", "attempts", "evidence", "last_evidence")}})
        json.dump(report, open(os.path.join(HERE, "seven_projects_dual_report.json"),
                               "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok_n = sum(1 for d in report["domains"] if d["status"] == "accepted")
    report["summary"] = f"{ok_n}/{len(DOMAINS)} 域双智能体实测通过"
    json.dump(report, open(os.path.join(HERE, "seven_projects_dual_report.json"),
                           "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n=== 总判定 === {report['summary']}")
    return 0 if ok_n == len(DOMAINS) else 1


if __name__ == "__main__":
    import time
    sys.exit(main())
