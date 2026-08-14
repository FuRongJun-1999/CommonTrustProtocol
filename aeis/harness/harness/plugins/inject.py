# -*- coding: utf-8 -*-
"""harness.plugins.inject · 工具注入（外部工具 → harness 统一工具表）
================================================
外部工具以 `mcp__<server>__<tool>` 命名空间注册进工具表扩展区
（EXT_TOOLS），与内置 42 工具同表调用；命名空间天然隔离冲突。
"""
from harness.core import tools as core_tools

# 外部工具扩展区：键 "mcp__<name>__<tool>" → {"plugin": name, "tool": tool}
EXT_TOOLS = {}

PREFIX = "mcp__"


def register(plugin_name: str, tool_name: str, description: str = "") -> str:
    """注册外部工具 → 返回完整键。"""
    key = f"{PREFIX}{plugin_name}__{tool_name}"
    EXT_TOOLS[key] = {"plugin": plugin_name, "tool": tool_name,
                      "description": description}
    return key


def unregister_all(plugin_name: str):
    """移除某插件的全部工具（插件关闭时）。"""
    for k in [k for k in EXT_TOOLS if k.startswith(f"{PREFIX}{plugin_name}__")]:
        EXT_TOOLS.pop(k, None)


def register_plugin_tools(manager, plugin_name: str) -> int:
    """从 PluginManager 拉取某插件工具清单并注册。返回注册数。"""
    client = manager.get(plugin_name)
    if client is None:
        return 0
    n = 0
    for t in client.list_tools():
        register(plugin_name, t.get("name", ""), t.get("description", ""))
        n += 1
    return n


def is_external(tool_name: str) -> bool:
    return tool_name.startswith(PREFIX)


def call_external(manager, tool_name: str, params: dict) -> dict:
    """调用外部工具（manager.call 容器化 + 安全过滤）。"""
    entry = EXT_TOOLS.get(tool_name)
    if entry is None:
        return {"status": "error", "error": f"外部工具未注册: {tool_name}"}
    r = manager.call(entry["plugin"], entry["tool"], params or {})
    if not r["ok"]:
        return {"status": "error", "error": r.get("error", "调用失败")}
    return {"status": "ok", "tool": tool_name, "result": r["data"],
            "flagged": r.get("flagged", False)}


def patch_call_tool(manager):
    """将外部工具路由挂入 core.tools.call_tool（首次调用时装配）。"""
    orig = core_tools.call_tool

    def wrapped(agent, tool_name, params=None):
        if is_external(tool_name):
            return call_external(manager, tool_name, params)
        return orig(agent, tool_name, params)

    core_tools.call_tool = wrapped
