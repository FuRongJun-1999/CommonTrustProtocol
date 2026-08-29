# -*- coding: utf-8 -*-
"""kccs_lsp.py · KCCS 条件图 LSP 服务器（VS Code 工具线第一批，2026-08-29）

代码图架构战略行动项 3 立项（荣：给优秀程序员提供的生产力帮助）。
两能力（路线 B 渐进）：
1. KCCS 悬停卡：光标处标识符 → 条件路由图查询 → 四要素 Markdown 悬浮
2. KCCS 实时诊断：条件词按 R1-R3 边界规范校验，违规标诊断

运行：
    python kccs_lsp.py --tcp 2087   # TCP 模式（VS Code 客户端连接）
数据源：主仓库条件路由图（wisdom-book-cloud.db，随卡增长实时可查）。
"""
from __future__ import annotations

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis"))
sys.path.insert(1, os.path.join(ROOT, "aeis", "wisdom"))

from pygls.lsp.server import LanguageServer
from lsprotocol import types as lsp

from wisdom_book import ConditionDex
from semantic_translate import card_route

server = LanguageServer("kccs-lsp", "v0.1.0")
_dex = None


def dex() -> ConditionDex:
    global _dex
    if _dex is None:
        _dex = ConditionDex(
            db_path=os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db"),
            fresh=False)
    return _dex


def hover_card(word: str) -> str | None:
    """标识符 → 条件路由图 → KCCS 四要素 Markdown（悬停卡）。"""
    hs = card_route(dex(), f"问{word}", limit=1)
    if not hs or not hs[0].get("_card_hit"):
        return None
    h = hs[0]
    node = dex().store.get_node(h.get("id"))
    cm = (node.state_attributes or {}).get("comment", {}) if node else {}
    lines = [f"**📦 KCCS 条件卡：{h.get('name', word)}**", ""]
    if cm.get("生效条件"):
        lines.append(f"**生效条件**：{'；'.join(map(str, cm['生效条件'][:3]))}")
    if cm.get("子功能"):
        lines.append(f"**子功能**：{cm['子功能']}")
    if cm.get("执行"):
        lines.append(f"**执行**：{str(cm['执行'])[:200]}")
    if cm.get("不适用条件"):
        lines.append(f"**不适用条件**：{'；'.join(map(str, cm['不适用条件'][:3]))}")
    lines.append("")
    lines.append("*来源：灵枢条件路由图（条件化语法，高于语法树一层）*")
    return "\n".join(lines)


# ---- R1-R3 校验（条件词边界规范 v1.0 复用）----

def validate_condition_word(w: str) -> str | None:
    if not w.startswith("问"):
        return "R1 条件词应为「问X」问句形态"
    if "（" in w or "(" in w:
        return "R2 条件词含括号同义词（应拆为独立条件词）"
    if " " in w:
        return "R3 条件词含空格（应合并或拆分）"
    return None


@server.feature(lsp.TEXT_DOCUMENT_HOVER)
def on_hover(ls, params: lsp.HoverParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    line = doc.lines[params.position.line].rstrip("\n") \
        if params.position.line < len(doc.lines) else ""
    # 光标处标识符提取（中英文）
    for m in re.finditer(r"[\w\u4e00-\u9fff]+", line):
        if m.start() <= params.position.character <= m.end():
            word = m.group(0)
            card = hover_card(word)
            if card:
                return lsp.Hover(contents=lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown, value=card))
    return None


@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def on_change(ls, params):
    uri = params.text_document.uri
    doc = ls.workspace.get_text_document(uri)
    diags = []
    # 扫描「# 生效条件：」「# 不适用条件：」行内条件词（KCCS 注释规范）
    for i, line in enumerate(doc.lines):
        m = re.search(r"#\s*(生效条件|不适用条件)[:：]\s*(.+)", line)
        if not m:
            continue
        for w in re.split(r"[；;，,]", m.group(2)):
            w = w.strip().strip("'\"")
            if not w:
                continue
            err = validate_condition_word(w)
            if err:
                diags.append(lsp.Diagnostic(
                    range=lsp.Range(
                        start=lsp.Position(line=i, character=line.index(w)),
                        end=lsp.Position(line=i, character=line.index(w) + len(w))),
                    message=f"KCCS {err}（条件词边界规范 v1.0）",
                    severity=lsp.DiagnosticSeverity.Warning,
                    source="kccs-lsp"))
    ls.text_document_publish_diagnostics(lsp.PublishDiagnosticsParams(
        uri=uri, diagnostics=diags))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tcp", type=int, default=2087)
    ap.add_argument("--stdio", action="store_true")
    args = ap.parse_args()
    if args.stdio:
        server.start_io()
    else:
        server.start_tcp("127.0.0.1", args.tcp)
