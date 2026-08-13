#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.devices.browser · 浏览器设备（BODY-REV1 批次 3）
========================================================
动作（Playwright 可选依赖，缺失优雅降级）：
- open: 打开 URL（无头浏览器，等待加载）
- snapshot: 页面结构化提取（标题/URL/正文文本/链接数——纯数据，无指令语义）
- screenshot: 页面截图（工作区 browsers/ 下）

安全边界：
- 网页内容 = 外部数据：snapshot 返回的正文/标题经容器化（provenance=device:browser），
  摄取前须过 security.classify_external_text（网页是提示词注入最高发面）
- URL 协议白名单：仅 http/https（禁 file:// 等本地协议）
- 无头模式（不干扰宿主桌面）；页面超时终止
- 依赖缺失优雅降级（check 返回 unavailable + 安装提示）
"""

import os
import time
from typing import Dict, Optional

from ..base import BodyDevice, DeviceResult

PAGE_TIMEOUT = 20_000     # 毫秒
BODY_MAX_CHARS = 10_000   # 正文提取上限


class BrowserDevice(BodyDevice):
    """浏览器设备（无头 · 网页数据提取）。"""

    name = "browser"
    modality = "text"
    description = "浏览器（无头 Playwright：open/snapshot/screenshot）"

    def __init__(self, workspace: str = ""):
        super().__init__(workspace)
        self._sync_playwright = None
        self._probe()

    def _probe(self) -> None:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore

            self._sync_playwright = sync_playwright
        except Exception:
            pass

    # ---- 接口 ----

    def check(self) -> Dict:
        if self._sync_playwright is None:
            return {"available": False,
                    "detail": "playwright 未安装（pip install playwright && playwright install chromium）"}
        return {"available": True, "detail": "playwright 可用"}

    def capabilities(self) -> Dict:
        caps = super().capabilities()
        caps["actions"] = ["open", "snapshot", "screenshot"]
        caps["notes"] = "无头模式；URL 仅 http/https；网页内容为外部数据（须过注入过滤）"
        return caps

    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        p = params or {}
        # 安全边界优先：URL 协议白名单在任何动作前校验（含依赖缺失时）
        try:
            if action in ("open", "snapshot", "screenshot"):
                self._url(p)
        except ValueError as exc:
            return self._fail(str(exc))
        if self._sync_playwright is None:
            return self._fail("浏览器不可用：pip install playwright && playwright install chromium")
        try:
            if action == "open":
                return self._open(p)
            if action == "snapshot":
                return self._snapshot(p)
            if action == "screenshot":
                return self._screenshot(p)
        except Exception as exc:
            return self._fail(f"{action} 异常: {exc}")
        return self._fail(f"未知动作 {action}（可用: open/snapshot/screenshot）")

    # ---- 工具 ----

    def _url(self, p: Dict) -> str:
        url = str(p.get("url", "")).strip()
        if not url:
            raise ValueError("缺少 url")
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL 仅允许 http/https（防本地协议访问）")
        return url

    def _launch(self):
        pw = self._sync_playwright()
        browser = pw.chromium.launch(headless=True)
        return pw, browser

    def _page(self, browser, url: str):
        page = browser.new_page()
        page.goto(url, timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
        page.wait_for_timeout(800)  # 等待渲染
        return page

    def _open(self, p: Dict) -> DeviceResult:
        url = self._url(p)
        pw, browser = self._launch()
        try:
            page = self._page(browser, url)
            title = page.title()
            final_url = page.url
            return self._r({"url": final_url, "title": title}, "open",
                           text_summary=f"已打开 {final_url}（{title}）")
        finally:
            browser.close()
            pw.stop()

    def _snapshot(self, p: Dict) -> DeviceResult:
        """页面结构化提取（纯数据：标题/URL/正文/链接数）。"""
        url = self._url(p)
        pw, browser = self._launch()
        try:
            page = self._page(browser, url)
            title = page.title()
            body_text = page.inner_text("body") if page.locator("body").count() else ""
            links = page.eval_on_selector_all(
                "a[href]", "els => els.map(e => e.getAttribute('href'))")
            data = {
                "url": page.url,
                "title": title,
                "body": body_text[:BODY_MAX_CHARS],
                "body_truncated": len(body_text) > BODY_MAX_CHARS,
                "link_count": len(links),
                "links": [l for l in links if isinstance(l, str)][:50],
            }
            return self._r(data, "snapshot",
                           text_summary=f"页面提取: {title}（正文 {len(body_text)} 字符，链接 {len(links)}）")
        finally:
            browser.close()
            pw.stop()

    def _screenshot(self, p: Dict) -> DeviceResult:
        url = self._url(p)
        shot_dir = os.path.join(self.workspace, "browsers") if self.workspace else ""
        pw, browser = self._launch()
        try:
            page = self._page(browser, url)
            if shot_dir:
                os.makedirs(shot_dir, exist_ok=True)
                path = os.path.join(shot_dir, f"web_{int(time.time() * 1000)}.png")
                page.screenshot(path=path, full_page=False)
                meta = {"path": os.path.abspath(path), "bytes": os.path.getsize(path),
                        "url": page.url}
                return self._r(meta, "screenshot",
                               text_summary=f"页面截图已保存: {meta['path']}")
            buf = page.screenshot(full_page=False)
            return self._r({"bytes": len(buf), "in_memory": True, "url": page.url},
                           "screenshot", text_summary="页面截图（内存）")
        finally:
            browser.close()
            pw.stop()
