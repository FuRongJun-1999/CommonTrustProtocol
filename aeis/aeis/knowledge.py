#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.knowledge · 外部知识摄取（第 3 项：记忆含外部知识）
=========================================================
- ingest_text：文本摄取 → 知识层
- ingest_file：文件摄取（txt/md/json/py 等，按扩展名处理）
- ingest_url：URL 内容摄取（urllib 零依赖）
- 摄取内容带 source 标签（可追溯来源）· 可检索 · 可参与蒸馏
"""

import json
import os
import re
import urllib.request
from typing import Dict, List, Optional

# 文件扩展名 → 语言/类型标签
EXT_TAGS = {
    ".txt": "text", ".md": "markdown", ".rst": "rst",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml",
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".html": "html", ".css": "css", ".c": "c", ".cpp": "cpp",
    ".java": "java", ".go": "go", ".rs": "rust", ".sh": "shell",
    ".csv": "csv", ".xml": "xml",
}

MAX_CHUNK = 1500  # 长文本分块（避免单节点过大）


def _chunk_text(text: str, max_len: int = MAX_CHUNK) -> List[str]:
    """按段落/长度分块"""
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_len:
        return [text]
    chunks, cur = [], ""
    for para in re.split(r"\n\s*\n", text):
        if len(cur) + len(para) + 2 > max_len and cur:
            chunks.append(cur)
            cur = para
        else:
            cur = f"{cur}\n\n{para}" if cur else para
    if cur:
        chunks.append(cur)
    return chunks


def _extract_entities(text: str, max_entities: int = 8) -> List[str]:
    """简单实体提取：中文专名（书名号/引号内）+ 英文大写词"""
    entities = set()
    for m in re.findall(r"[《「『\"']([^》」』\"']{2,20})[》」』\"']", text):
        entities.add(m.strip())
    for m in re.findall(r"\b[A-Z][A-Za-z0-9_-]{3,}\b", text):
        entities.add(m)
    return list(entities)[:max_entities]


def ingest_text(engine, content: str, source: str = "manual",
                tags: Optional[List[str]] = None,
                importance: float = 0.6) -> Dict:
    """文本摄取：内容 → 知识层（分块 · source 标签 · 实体提取）"""
    chunks = _chunk_text(content)
    if not chunks:
        return {"status": "empty", "nodes": 0}
    nodes = []
    base_tags = list(tags or []) + [f"source:{source}", "knowledge_ingest"]
    for i, chunk in enumerate(chunks):
        entities = _extract_entities(chunk)
        node = engine.add_perception(
            chunk, importance=importance,
            tags=base_tags + ([f"chunk:{i}"] if len(chunks) > 1 else []),
            entities=entities or None)
        nodes.append(node.id)
    return {"status": "ok", "nodes": len(nodes), "node_ids": nodes,
            "chars": sum(len(c) for c in chunks), "chunks": len(chunks)}


def ingest_file(engine, path: str, tags: Optional[List[str]] = None,
                importance: float = 0.6) -> Dict:
    """文件摄取：按扩展名处理（文本类直接读；json 摘要）"""
    if not os.path.exists(path):
        return {"status": "not_found", "path": path}
    ext = os.path.splitext(path)[1].lower()
    ftype = EXT_TAGS.get(ext, "text")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        return {"status": "read_error", "error": str(e)}
    if ext == ".json":
        try:
            data = json.loads(content)
            content = json.dumps(data, ensure_ascii=False, indent=1)[:MAX_CHUNK * 3]
        except Exception:
            pass  # 非标准 JSON 按文本处理
    r = ingest_text(engine, content, source=f"file:{os.path.basename(path)}",
                    tags=(tags or []) + [f"filetype:{ftype}"], importance=importance)
    r["file"] = path
    r["filetype"] = ftype
    return r


def ingest_url(engine, url: str, tags: Optional[List[str]] = None,
               importance: float = 0.6, timeout: int = 30) -> Dict:
    """URL 摄取：抓取页面文本 → 知识层（零依赖 urllib）"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "aeis-kb/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return {"status": "fetch_error", "url": url, "error": str(e)}
    # 简单 HTML 去标签
    text = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", raw)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 20:
        return {"status": "empty_content", "url": url}
    r = ingest_text(engine, text, source=f"url:{url}",
                    tags=(tags or []) + ["web"], importance=importance)
    r["url"] = url
    return r
