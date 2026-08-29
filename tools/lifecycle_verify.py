# -*- coding: utf-8 -*-
"""lifecycle_verify.py · 白箱完整生命周期端到端验证

认知图（条件路由命中）→ 条件代码图（SKILL）→ MCP 工具（compile_exec）→ 本地编译执行（结果）
验证四个阶段全部打通。
"""
import sys, os, json, subprocess, time

def setup_stdout():
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

setup_stdout()

CTP = r"D:\Program Files\2_ai\CommonTrustProtocol"
WISDOM = os.path.join(CTP, "aeis", "wisdom")

# ---- 阶段 1：认知图（条件路由命中单元）----
print("===== 阶段 1：认知图（条件路由）=====")
sys.path.insert(0, WISDOM)
import compiler_code_units as ccu
q = "写一个递归函数计算阶乘"
unit = ccu.route_compiler_unit(q)
print(f"  问题「{q}」→ 命中单元: {unit}（触发词索引检索面）")
assert unit == "编译-递归", f"认知图路由失败: {unit}"

# ---- 阶段 2：条件代码图（SKILL 五要素）----
print("\n===== 阶段 2：条件代码图（SKILL）=====")
import json as _json
trig = _json.load(open(os.path.join(WISDOM, "trigger_words_index.json"), encoding="utf-8"))
triggers = trig["compiler"].get(unit, [])
print(f"  {unit} 触发词: {triggers}")
skill_md = open(os.path.join(CTP, "aeis", "skills", "skills", "compile-recursive", "SKILL.md"), encoding="utf-8").read()
assert "克制条款" in skill_md and "not_applicable" in skill_md[:800]
print(f"  SKILL 三通道 ✓（触发词/克制条款/not_applicable）")

# ---- 阶段 3+4：MCP 工具 → 本地编译执行 ----
print("\n===== 阶段 3+4：MCP compile_exec → 本地编译执行 =====")
sys.path.insert(0, os.path.join(CTP, "aeis"))
from aeis.mcp.server import AEISServer

server = AEISServer()
import aeis.mcp.server as _srv_mod
from aeis.mcp.server import _tools as _tools_fn
tools = _tools_fn()
print(f"  server 模块: {_srv_mod.__file__}")
print(f"  _tools() 返回 {len(tools)} 个; compile_exec in: {'compile_exec' in [t['name'] for t in tools]}")
assert "compile_exec" in [t["name"] for t in tools], f"compile_exec 未注册（工具数 {len(tools)}）"
print(f"  compile_exec 已注册（工具总数 {len(tools)}）")

# 直接调用分发（等价 MCP tools/call）
def call(name, **params):
    a = {"name": name, "arguments": params}
    if hasattr(server, "_call_tool"):
        result = server._call_tool(name, params)
    else:
        result = server.call_tool(a)
    text = result.get("content", [{}])[0].get("text", "")
    return json.loads(text)

# 阶乘程序（编译-递归单元验证）
factorial = "定义 阶乘（数）：若 数 小于 2，则 返回 1，否则 返回 数 乘 阶乘（数 减 1）；结果 = 阶乘（5）；止。"
r = call("compile_exec", source=factorial)
print(f"  阶乘程序 → {r}")
assert r["ok"] and abs(r["symbols"].get("结果", 0) - 120.0) < 0.01, f"阶乘结果错: {r}"

# 算术优先级（compile-assign）
r2 = call("compile_exec", source="结果 = 3 加 4 乘 2；止。")
print(f"  算术程序 → {r2}")
assert r2["ok"] and abs(r2["symbols"].get("结果", 0) - 11.0) < 0.01

# 负例：语法错误应 ok=False
r3 = call("compile_exec", source="结果 = 1 加 加；止。")
print(f"  坏程序 → {r3}")
assert not r3["ok"], "坏程序应编译失败"

print(f"\n===== 完整生命周期验证 ✅ =====")
print("认知图（条件路由命中）→ 条件代码图（SKILL 五要素）→ MCP compile_exec → 本地编译执行（结果）")
print("阶乘=120 / 算术=11 / 坏程序拒绝——白箱确定性闭环")
