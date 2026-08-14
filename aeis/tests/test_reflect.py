#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REFLECT-REV1 递归验证反思回归测试（协议 3.12 + 1.6.7）
=========================================================
验证：
1. 元反思（结构性后退：标准声明 + 元认知校准）
2. 一级验证（预期 vs 实际 → 偏差 → 触发反思门槛）
3. 问1 隐藏前提（记忆检索 → 前提 + 条件空间边界）
4. 问2 影响（影响评估 + 分级）
5. 三级终裁（可逆性优先 → 重要决策升级设计者）
6. 记录单元归档（反思链 → 记忆 + 行为日志）
7. 递归截断（depth ≥ 3 → structural_blindspot，协议 3.12 约束）
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from aeis.api import Agent  # noqa: E402

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        print(f"  [FAIL] {name} {detail}")


def test_full_reflection():
    a = Agent(identity="reflect-full", db_path=":memory:")
    a.remember("YOLO-World 训练于真实照片，对二次元插画风格敏感度低",
               importance=0.8, tags=["vision", "yoloworld"])
    r = a.recursive_reflect(
        claim="YOLO-World 将画面顶部的满月误检为 balloon，wolf 未检出",
        expected="moon 与 wolf 应被检出",
        actual="balloon 0.52 检出，wolf 未检出")

    check("状态 reflected", r["status"] == "reflected")
    check("元反思存在", "meta_reflection" in r and len(r["meta_reflection"]["standards"]) >= 2)
    check("一级验证偏差", r["verification"]["deviation"] is True
          and r["verification"]["trigger_reflection"] is True)
    check("问1 隐藏前提检索", len(r["reflection"]["hidden_premises"]["premises"]) >= 1)
    check("问1 条件空间边界", "condition_space_boundary" in r["reflection"]["hidden_premises"])
    check("问2 影响评估", "impact" in r["reflection"]
          and r["reflection"]["impact"]["impact_level"] in ("协作", "结构", "存在"))
    check("问2 问题表述", r["reflection"]["impact"]["question"] == "这件事会有什么影响？")
    check("问1 问题表述", r["reflection"]["hidden_premises"]["question"] == "这件事有什么隐藏前提？")
    check("三级终裁", r["verdict"]["principle"].startswith("可逆性优先"))
    check("终裁动作", "action" in r["verdict"])
    check("反思链归档", len([n for n, _ in a.search("反思链", 5)
                           if "reflection_chain" in (n.tags or [])]) >= 1)


def test_irreversible_escalation():
    a = Agent(identity="reflect-escalate", db_path=":memory:")
    r = a.recursive_reflect(
        claim="删除协议核心结构文件以释放空间",
        expected="结构完整", actual="即将删除")
    check("不可逆判定", r["verdict"]["reversibility"] == "不可逆")
    check("结构级影响", r["reflection"]["impact"]["impact_level"] == "结构")
    check("升级设计者", r["verdict"]["needs_designer"] is True
          and "designer_decide" in r["verdict"]["action"])


def test_reversible_no_escalation():
    a = Agent(identity="reflect-rev", db_path=":memory:")
    r = a.recursive_reflect(
        claim="查询当前屏幕状态以验证预期",
        expected="屏幕无变化", actual="屏幕无变化")
    check("可逆判定", r["verdict"]["reversibility"] == "可逆")
    check("不升级", r["verdict"]["needs_designer"] is False)


def test_recursion_limit():
    a = Agent(identity="reflect-limit", db_path=":memory:")
    r = a.recursive_reflect("递归深度测试", depth=3)
    check("递归截断", r["status"] == "structural_blindspot")
    check("协议约束标注", "3.12" in r["note"])


def test_vprim_anchor_injection():
    """VPRIM-REV1：claim 含视觉锚点时注入确定性空间上下文。"""
    a = Agent(identity="reflect-vprim", db_path=":memory:")
    r = a.recursive_reflect(
        claim="moon@(420,52,484,116) 被误检为 balloon，person@(208,220,654,1136) 是主体")
    vctx = r.get("vprim_context")
    check("锚点上下文存在", vctx is not None)
    check("锚点提取", vctx and len(vctx["anchors"]) == 2)
    check("确定性空间关系", vctx and vctx["relations"][0]["relation"] == "above")
    check("普通 claim 无锚点上下文",
          "vprim_context" not in a.recursive_reflect("普通文本反思"))


def test_mcp_tool():
    """MCP recursive_reflect 工具注册（42 工具）。"""
    import json
    import subprocess

    env = dict(os.environ)
    env.setdefault("AEIS_DB", ":memory:")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "aeis.mcp.server"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        env=env, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def send(msg):
        proc.stdin.write(json.dumps(msg).encode() + b"\n")
        proc.stdin.flush()
        return json.loads(proc.stdout.readline())

    def notify(msg):
        proc.stdin.write(json.dumps(msg).encode() + b"\n")
        proc.stdin.flush()

    send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
          "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                     "clientInfo": {"name": "t", "version": "0"}}})
    notify({"jsonrpc": "2.0", "method": "notifications/initialized"})
    r = send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = {t["name"]: t for t in r["result"]["tools"]}
    check("recursive_reflect 工具", "recursive_reflect" in tools)
    check("工具总数 42", len(tools) == 44, f"count={len(tools)}")
    proc.stdin.close()
    proc.wait(timeout=10)


def main():
    test_full_reflection()
    test_irreversible_escalation()
    test_reversible_no_escalation()
    test_recursion_limit()
    test_vprim_anchor_injection()
    test_mcp_tool()
    print(f"\n===== REFLECT-REV1 递归验证反思回归: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
