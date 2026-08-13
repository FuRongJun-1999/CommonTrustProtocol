#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aeis.web · 外部网络能力（博查 API 搜索 + 网页抓取）
=====================================================
- search(query)：博查 Web Search API（多模态混合搜索 + 语义排序）
- fetch_page(url)：网页内容抓取（requests + BeautifulSoup + html2text）
- 为外部知识摄取提供网络路径（自主学习补录）

安全：API key 从环境变量 BOCHA_API_KEY 读取（不硬编码、不入库）
"""

import os
import json
from typing import Dict, List, Optional

# 可选依赖（D-005：核心零依赖，web 为增强扩展）
try:
    import requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

try:
    from bs4 import BeautifulSoup
    _BS4_OK = True
except ImportError:
    _BS4_OK = False

try:
    import html2text
    _HTML2TEXT_OK = True
except ImportError:
    _HTML2TEXT_OK = False

SEARCH_ENDPOINT = "https://api.bochaai.com/v1/web-search"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def _api_key() -> str:
    return os.environ.get("BOCHA_API_KEY", "") or os.environ.get("BOCHA_KEY", "")


class WebTool:
    """网络工具：搜索 + 抓取（博查 API · 可降级）"""

    name = "web"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or _api_key()
        self._search_ok = bool(self.api_key) and _REQUESTS_OK

    # ------------------------------------------------------------------
    # 搜索（博查 Web Search API）
    # ------------------------------------------------------------------

    def search(self, query: str, count: int = 5,
               freshness: str = "noLimit", summary: bool = True) -> Dict:
        """博查搜索：query → 结果列表（name/url/snippet/summary）"""
        if not self._search_ok:
            return {"status": "unavailable",
                    "reason": "需要 BOCHA_API_KEY（环境变量）+ requests"}
        try:
            resp = requests.post(
                SEARCH_ENDPOINT,
                headers={"Authorization": f"Bearer {self.api_key}",
                         "Content-Type": "application/json"},
                json={"query": query, "freshness": freshness,
                      "summary": summary, "count": count},
                timeout=30)
            resp.raise_for_status()
            data = resp.json()
            # 兼容两种响应结构：直接 webPages 或 {code, data:{webPages}}
            if isinstance(data, dict) and "webPages" not in data:
                data = data.get("data", data)
            pages = data.get("webPages", {}).get("value", [])
            results = [{
                "name": p.get("name", ""),
                "url": p.get("url", ""),
                "snippet": p.get("snippet", ""),
                "summary": p.get("summary", ""),
                "date": p.get("datePublished", ""),
            } for p in pages]
            return {"status": "ok", "query": query, "count": len(results),
                    "results": results}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    # ------------------------------------------------------------------
    # 网页抓取（参考 BrowserTool 模式）
    # ------------------------------------------------------------------

    def fetch_page(self, url: str, format: str = "markdown",
                   max_chars: int = 10000) -> Dict:
        """抓取网页内容（markdown/text/html）"""
        if not _REQUESTS_OK:
            return {"status": "unavailable", "reason": "requests 未安装"}
        try:
            resp = requests.get(url, headers={"User-Agent": UA}, timeout=30)
            resp.raise_for_status()
            # 编码修复：按响应头/内容检测（GBK 等页面不乱码）
            if not resp.encoding or resp.encoding.lower() == "iso-8859-1":
                resp.encoding = resp.apparent_encoding
            if format == "text":
                soup = self._soup(resp.text)
                content = soup.get_text(separator="\n").strip()[:max_chars]
                return {"status": "ok", "content": content, "format": "text",
                        "chars": len(content)}
            if format == "markdown":
                soup = self._soup(resp.text)
                if _HTML2TEXT_OK:
                    conv = html2text.HTML2Text()
                    conv.body_width = 0
                    content = conv.handle(str(soup))[:max_chars]
                else:
                    content = soup.get_text(separator="\n").strip()[:max_chars]
                return {"status": "ok", "content": content, "format": "markdown",
                        "chars": len(content)}
            return {"status": "ok", "content": resp.text[:max_chars],
                    "format": "html", "chars": min(max_chars, len(resp.text))}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    @staticmethod
    def _soup(html: str):
        if _BS4_OK:
            return BeautifulSoup(html, "html.parser")
        # 无 bs4 的极简降级
        import re
        return re.sub(r"<[^>]+>", " ", html)

    def search_and_fetch(self, query: str, fetch_top: int = 1) -> Dict:
        """搜索 + 抓取顶部结果全文（自主学习摄取路径）"""
        sr = self.search(query, count=fetch_top + 1)
        if sr["status"] != "ok" or not sr["results"]:
            return sr
        top = sr["results"][0]
        fr = self.fetch_page(top["url"])
        return {"status": "ok", "query": query,
                "search": sr["results"][:fetch_top],
                "top_url": top["url"], "top_title": top["name"],
                "fetch": fr}


# 默认实例（key 从环境变量）
default_web = WebTool()
