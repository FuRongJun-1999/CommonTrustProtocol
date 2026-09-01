# -*- coding: utf-8 -*-
"""aeis.search_providers · 可插拔搜索引擎接口（2026-09-01 荣指令）

需求：支持自定义搜索引擎——提供接口即可，不改动已有博查搜索实现。
设计：
  - SearchProvider 协议：search(query, count) → 统一结果结构
      {"status": "ok"/"unavailable"/"error", "query", "count",
       "results": [{name, url, snippet, summary, date}], "provider": <name>}
  - 内置 bocha（默认，委托 aeis.web.WebTool——零改动复用）
  - 内置 duckduckgo（可选依赖 duckduckgo_search，未装则 unavailable）
  - register_provider(name, factory)：外部注册自定义引擎（提供接口的核心）
  - get_provider(name=None)：按名取实例；None → AEIS_SEARCH_PROVIDER env → bocha

向后兼容：不设置任何 env 时行为与博查单实现时期完全一致。
"""

import os
from typing import Callable, Dict, Optional

# 复用既有 web 模块的可选依赖探测（requests）
try:
    from .web import WebTool as _BochaWebTool
    _BOCHA_OK = True
except ImportError:  # 直跑 fallback
    try:
        from web import WebTool as _BochaWebTool  # type: ignore
        _BOCHA_OK = True
    except ImportError:
        _BOCHA_OK = False


class SearchProvider:
    """搜索引擎 Provider 协议（子类实现 search 即可接入）。"""

    name = "base"

    def search(self, query: str, count: int = 5, **kwargs) -> Dict:
        raise NotImplementedError


class BochaProvider(SearchProvider):
    """博查（默认）：委托既有 aeis.web.WebTool——不改其实现。"""

    name = "bocha"

    def __init__(self):
        self._tool = _BochaWebTool() if _BOCHA_OK else None

    def search(self, query: str, count: int = 5, **kwargs) -> Dict:
        if self._tool is None:
            return {"status": "unavailable", "reason": "aeis.web 不可用",
                    "provider": self.name}
        r = self._tool.search(query, count=count)
        r.setdefault("provider", self.name)
        return r


class DuckDuckGoProvider(SearchProvider):
    """DuckDuckGo（免 Key 示例）：可选依赖 duckduckgo_search。"""

    name = "duckduckgo"

    def search(self, query: str, count: int = 5, **kwargs) -> Dict:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return {"status": "unavailable",
                    "reason": "需要 duckduckgo_search（pip install duckduckgo-search）",
                    "provider": self.name}
        try:
            out = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=count):
                    out.append({"name": r.get("title", ""),
                                "url": r.get("href", ""),
                                "snippet": r.get("body", ""),
                                "summary": "",
                                "date": ""})
            return {"status": "ok", "query": query, "count": len(out),
                    "results": out, "provider": self.name}
        except Exception as e:
            return {"status": "error", "reason": str(e), "provider": self.name}


class SearXNGProvider(SearchProvider):
    """SearXNG（自建元搜索引擎 · 免 Key · issue #1 诉求）。

    配置：env AEIS_SEARXNG_URL = 实例地址（如 http://localhost:8888）。
    使用 SearXNG JSON API：GET {base}/search?q=...&format=json
    适用于：免费自部署 / 数据主权 / 企业内网搜索场景。
    """

    name = "searxng"

    def search(self, query: str, count: int = 5, **kwargs) -> Dict:
        base = os.environ.get("AEIS_SEARXNG_URL", "").rstrip("/")
        if not base:
            return {"status": "unavailable",
                    "reason": "需要 AEIS_SEARXNG_URL（自建 SearXNG 实例地址）",
                    "provider": self.name}
        try:
            import requests
        except ImportError:
            return {"status": "unavailable", "reason": "需要 requests",
                    "provider": self.name}
        try:
            resp = requests.get(f"{base}/search",
                                params={"q": query, "format": "json",
                                        "language": "zh-CN"},
                                headers={"User-Agent": "aeis-search/1.0"},
                                timeout=30)
            resp.raise_for_status()
            out = [{"name": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", ""),
                    "summary": "",
                    "date": r.get("publishedDate", "") or ""}
                   for r in resp.json().get("results", [])[:count]]
            return {"status": "ok", "query": query, "count": len(out),
                    "results": out, "provider": self.name}
        except Exception as e:
            return {"status": "error", "reason": str(e), "provider": self.name}


class TavilyProvider(SearchProvider):
    """Tavily（专为 AI agent/RAG 设计 · 免费额度 1000 次/月 · issue #2 社区贡献）。

    配置：env TAVILY_API_KEY = tvly- 前缀密钥（https://app.tavily.com 注册）。
    API：POST https://api.tavily.com/search（Bearer 鉴权，search_depth=basic）。
    """

    name = "tavily"

    def search(self, query: str, count: int = 5, **kwargs) -> Dict:
        api_key = os.environ.get("TAVILY_API_KEY", "")
        if not api_key:
            return {"status": "unavailable",
                    "reason": "需要 TAVILY_API_KEY（https://app.tavily.com 注册，tvly- 前缀）",
                    "provider": self.name}
        try:
            import requests
        except ImportError:
            return {"status": "unavailable", "reason": "需要 requests",
                    "provider": self.name}
        try:
            resp = requests.post(
                "https://api.tavily.com/search",
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json={"query": query, "search_depth": "basic",
                      "max_results": count, "include_answer": False,
                      "include_raw_content": False, "include_images": False,
                      "topic": "general"},
                timeout=30)
            resp.raise_for_status()
            # 按 URL 去重（社区贡献实现要点）
            seen, out = set(), []
            for r in resp.json().get("results", []):
                url = r.get("url", "")
                if url in seen:
                    continue
                seen.add(url)
                out.append({"name": r.get("title", ""),
                            "url": url,
                            "snippet": r.get("content", ""),
                            "summary": "",
                            "date": r.get("published_date", "") or ""})
            return {"status": "ok", "query": query, "count": len(out),
                    "results": out, "provider": self.name}
        except Exception as e:
            return {"status": "error", "reason": str(e), "provider": self.name}


# ---- 注册表（提供接口的核心：外部引擎 register 即接入） ----

_REGISTRY: Dict[str, Callable[[], SearchProvider]] = {
    "bocha": BochaProvider,
    "duckduckgo": DuckDuckGoProvider,
    "searxng": SearXNGProvider,
    "tavily": TavilyProvider,
}


def register_provider(name: str, factory: Callable[[], SearchProvider]) -> None:
    """注册自定义搜索引擎：factory() 须返回实现 search(query, count) 的对象。"""
    _REGISTRY[name] = factory


def available_providers() -> list:
    """当前已注册的引擎名列表。"""
    return sorted(_REGISTRY.keys())


def get_provider(name: Optional[str] = None) -> SearchProvider:
    """按名取 Provider 实例；None → AEIS_SEARCH_PROVIDER env → bocha（默认不变）。"""
    picked = name or os.environ.get("AEIS_SEARCH_PROVIDER", "") or "bocha"
    factory = _REGISTRY.get(picked)
    if factory is None:
        raise KeyError(f"未注册的搜索引擎: {picked}（可用: {available_providers()}）")
    return factory()
