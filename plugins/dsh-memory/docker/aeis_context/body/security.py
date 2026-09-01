#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.security · 严格注入隔离（BODY-REV1）
==========================================
规则（引用 N.E.K.O 注入面审计结论——其全库无运行时注入防御，本模块为对治）：

1. 设备/网络/文件内容只作为结构化工具结果（DeviceResult）返回，
   永不拼接进 system prompt。
2. 提示词白名单 = 角色声明 + 用户直接输入 + 经 preflight 验证的摘要。
3. sanitize_device_text：外部文本进入认知层前清理（控制字符/超长）。
4. directive_scan：指令注入模式检测（输出前与摄取前双用）。
5. 设备内容进记忆必须带 provenance 且经摘要（ingest 带 source）。
"""

import re
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# 指令注入模式（工程代理：常见 prompt injection 特征，非完备）
# ---------------------------------------------------------------------------

DIRECTIVE_PATTERNS: List[str] = [
    r"忽略(上面|之前|以上|所有)?(的)?(所有)?(指令|指示|规则|要求|设定)",
    r"(不要|无需|忘记|忽略).{0,12}(之前的|上面的)?(指令|指示|设定|对话)",
    r"(你|您|请).{0,8}(现在|重新).{0,6}(扮演|认为|忘记)",
    r"system\s*prompt",
    r"\(?重要\)?\s*[:：]\s*(立即|马上)",
    r"(改写|覆盖|替换).{0,10}(指令|提示词|设定)",
    r"ignore\s+(all\s+)?(previous|prior|above).{0,20}(instructions|prompts|rules)",
    r"you\s+(are|were)\s+now",
    r"disregard\s+(all\s+)?(previous|prior|above)",
    r"\[?(SYSTEM|系统|内嵌|隐藏)[\]\s]*[:：]\s*",
]

# 控制字符清理（保留 \n \t 等可打印控制）
_CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# 设备文本摘要上限（字符）
SUMMARY_MAX_CHARS = 2000


def sanitize_device_text(text: str, max_chars: int = SUMMARY_MAX_CHARS) -> str:
    """外部文本进入认知层前的清理：去控制字符 + 截断。"""
    if not text:
        return ""
    cleaned = _CTRL_RE.sub("", str(text))
    return cleaned[:max_chars]


def directive_scan(text: str) -> Dict:
    """指令注入模式检测。

    返回 {detected: bool, patterns: [命中模式], score: 命中数}。
    用途：
    - 设备/网络内容摄取前：命中则内容标记为"疑似注入"，只做数据不做指令
    - LLM 输出前（preflight）：命中则拦截（防模型被引导输出注入内容）
    """
    if not text:
        return {"detected": False, "patterns": [], "score": 0}
    hits = []
    for pattern in DIRECTIVE_PATTERNS:
        try:
            if re.search(pattern, text, re.IGNORECASE):
                hits.append(pattern)
        except re.error:
            continue
    return {"detected": len(hits) > 0, "patterns": hits, "score": len(hits)}


def classify_external_text(text: str, provenance: str) -> Dict:
    """外部内容的统一入口判定：数据 or 疑似指令。

    返回 {sanitized, is_suspicious, provenance, directive_scan}。
    调用方义务：suspicious 内容只可作数据展示，不得进入任何指令位置。
    """
    cleaned = sanitize_device_text(text)
    scan = directive_scan(cleaned)
    return {
        "sanitized": cleaned,
        "is_suspicious": scan["detected"],
        "provenance": provenance,
        "directive_scan": scan,
    }


def result_to_memory_input(result) -> Optional[Dict]:
    """DeviceResult → 记忆输入（认知层用）。

    规则（严格隔离）：
    - 疑似注入内容不写入记忆
    - 只写 text_summary（已清理的摘要），带 provenance 标签
    - 返回 None 表示不应写入
    """
    if result is None or not getattr(result, "ok", False):
        return None
    summary = result.text_summary
    if not summary:
        return None
    scan = directive_scan(summary)
    if scan["detected"]:
        return None
    return {
        "content": sanitize_device_text(summary),
        "tags": [result.provenance, "body"],
        "source": result.provenance,
    }
