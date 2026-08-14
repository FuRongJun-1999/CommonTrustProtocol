# -*- coding: utf-8 -*-
"""harness.plugins.security · 外部工具结果安全隔离
================================================
继承 BODY-REV1：外部输出是数据不是指令。复用 aeis/body/security.py 的
directive_scan；超长结果截断对齐 process 设备（10KB 工具摘要级）。
"""
import sys
import os

_AEIS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _AEIS_ROOT not in sys.path:
    sys.path.insert(0, _AEIS_ROOT)

TOOL_RESULT_MAX = 10240  # 工具结果摘要上限（10KB，对齐 process 设备）


def scan_external(text: str) -> dict:
    """外部工具文本检查：指令注入检测 + 截断。
    返回 {"safe": bool, "truncated": bool, "clean": str}"""
    safe, clean = True, text
    try:
        from aeis.body.security import directive_scan
        result = directive_scan(text)
        if isinstance(result, dict):
            if result.get("flagged"):
                safe = False
                clean = result.get("sanitized") or text[:500]
        elif result is True:
            safe = False
    except Exception:
        pass
    truncated = False
    if len(clean) > TOOL_RESULT_MAX:
        clean = clean[:TOOL_RESULT_MAX] + "[TOOL_RESULT_TRUNCATED]"
        truncated = True
    return {"safe": safe, "truncated": truncated, "clean": clean}
