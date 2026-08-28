# Copyright 2026 灵枢 (Lingshu) · MIT
"""mini_browser.py · 白箱教学级浏览器 F1/F2（复现层第 8 条目，2026-08-28）

条件卡：docs/T11_完整版条件卡_浏览器.md（网络域应用层扩展）。
白箱口径：URL 解析与 HTTP 请求**显式实现**（不借 urllib.parse / http.client
黑箱），每一步可追溯——这本身就是「复现浏览器」的教学内容。

- F1 parse_url：scheme/host/port/path 拆分；默认端口补全；非法显式报错
- F2 http_get：socket 显式构造 GET 请求行/头；响应解析（状态行/头/体）；
  超时与连接失败显式报错

验证：test_mini_browser_v1.py（V1 URL 边界 / V2 本地服务器对齐 / 连接失败报错）。
"""

from __future__ import annotations

import re
import socket


class BrowserError(Exception):
    """浏览器白箱错误（URL 非法/网络失败/响应畸形）。"""


# ---------------------------------------------------------------------------
# F3 内容解析 / F4 结构化渲染 / V6 相对 URL（第二批 2026-08-28）
# ---------------------------------------------------------------------------

_RE_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_RE_A = re.compile(r"<a\s[^>]*?href=(\"([^\"]*)\"|'([^']*)')[^>]*>(.*?)</a>",
                   re.IGNORECASE | re.DOTALL)
_RE_STRIP = {"script": re.compile(r"<script\b.*?</script>", re.IGNORECASE | re.DOTALL),
             "style": re.compile(r"<style\b.*?</style>", re.IGNORECASE | re.DOTALL),
             "tag": re.compile(r"<[^>]+>")}
_ENTITIES = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'"}


def _unescape_basic(text: str) -> str:
    """基本 HTML 实体（显式白名单，教学口径不做全量实体表）。"""
    for k, v in _ENTITIES.items():
        text = text.replace(k, v)
    return text


def extract(html: str) -> dict:
    """F3 内容解析：HTML → {title, links, text}（显式规则可追溯）。

    - title：<title> 文本（缺省 None——显式而非静默空串）
    - links：[(href, text)]（引号形态单双皆收；无 href 的 <a> 不收）
    - text：去 script/style/标签后的压缩正文（空白折叠）
    """
    m = _RE_TITLE.search(html)
    title = _unescape_basic(m.group(1)).strip() if m else None
    links = []
    for m in _RE_A.finditer(html):
        href = m.group(2) if m.group(2) is not None else m.group(3)
        text = _RE_STRIP["tag"].sub(" ", m.group(4))
        links.append((href, " ".join(text.split())))
    stripped = _RE_STRIP["tag"].sub(" ", _RE_STRIP["style"].sub(
        " ", _RE_STRIP["script"].sub(" ", html)))
    text = " ".join(stripped.split())
    return {"title": title, "links": links, "text": _unescape_basic(text)}


def render(page: dict) -> str:
    """F4 结构化渲染：标题行 + 链接表 [n] text -> href + 正文（按序文本）。"""
    lines = []
    lines.append(f"# {page['title']}" if page.get("title") else "# (无标题)")
    for i, (href, text) in enumerate(page.get("links", []), 1):
        lines.append(f"[{i}] {text} -> {href}")
    if page.get("text"):
        lines.append("")
        lines.append(page["text"])
    return "\n".join(lines)


def resolve_url(base: str, href: str) -> str:
    """V6 相对 URL 解析（教学子集：绝对/根相对/相对/同级）。"""
    if "://" in href:
        return href
    info = parse_url(base)
    root = f"{info['scheme']}://{info['host']}:{info['port']}"
    if href.startswith("/"):
        return root + href
    if href.startswith("#"):
        return base.split("#", 1)[0] + href
    # 相对路径：基于当前 path 的目录
    cur_dir = info["path"].rsplit("/", 1)[0]
    stack = []
    for part in (cur_dir + "/" + href).split("/"):
        if part == "..":
            if stack:
                stack.pop()
        elif part not in ("", "."):
            stack.append(part)
    return root + "/" + "/".join(stack)


class Browser:
    """F5 导航（历史栈后退）+ F6 页面缓存（第三批 2026-08-28）。

    白箱口径：历史栈与缓存都是显式数据结构——历史 = 已访问页序列，
    缓存 = URL → 页面字典，命中与否由请求计数外部可验证。
    """

    def __init__(self) -> None:
        self.history: list = []      # F5：后退栈（visit 链）
        self.current: dict | None = None
        self.cache: dict = {}        # F6：URL → page

    def visit(self, url: str, use_cache: bool = True) -> dict:
        """访问页面：缓存命中则不发起请求（F6）；刷新用 use_cache=False。"""
        if use_cache and url in self.cache:
            self.current = self.cache[url]
            return self.current
        resp = http_get(url)
        page = extract(resp["body"])
        page["url"] = url
        page["status"] = resp["status"]
        if self.current is not None and self.current["url"] != url:
            self.history.append(self.current)
        self.current = page
        self.cache[url] = page
        return page

    def refresh(self) -> dict:
        """F6 显式刷新：绕过缓存重新请求当前页。"""
        if self.current is None:
            raise BrowserError("无当前页可刷新")
        return self.visit(self.current["url"], use_cache=False)

    def back(self) -> dict:
        """F5 后退：弹出历史栈顶为当前页。"""
        if not self.history:
            raise BrowserError("无历史可后退")
        self.current = self.history.pop()
        return self.current

    def follow(self, n: int) -> dict:
        """F5 跟随第 n 个链接（1 起）：相对 URL 先经 resolve_url。"""
        if self.current is None:
            raise BrowserError("无当前页，无法跟随链接")
        if not (1 <= n <= len(self.current["links"])):
            raise BrowserError(f"链接编号越界: {n}（共 {len(self.current['links'])} 个）")
        href, _ = self.current["links"][n - 1]
        return self.visit(resolve_url(self.current["url"], href))


_DEFAULT_PORTS = {"http": 80, "https": 443}


def parse_url(url: str) -> dict:
    """F1 URL 解析：scheme://host[:port]/path。

    显式规则（可追溯，对照 WHATWG URL 常识形态的教学子集）：
    - 无 scheme → BrowserError（显式报错，不猜测）
    - scheme 仅接受 http/https（教学口径，见条件卡限制显式）
    - port 缺省补全（http=80, https=443）；非数字端口 → 报错
    - path 缺省为 /
    """
    if not isinstance(url, str) or "://" not in url:
        raise BrowserError(f"非法 URL（缺少 scheme）: {url!r}")
    scheme, rest = url.split("://", 1)
    if scheme not in _DEFAULT_PORTS:
        raise BrowserError(f"不支持的 scheme: {scheme!r}（教学口径仅 http/https）")
    if not rest:
        raise BrowserError(f"非法 URL（缺少 host）: {url!r}")
    host_part, _, path = rest.partition("/")
    port = _DEFAULT_PORTS[scheme]
    if ":" in host_part:
        host, _, port_s = host_part.rpartition(":")
        if not host:
            raise BrowserError(f"非法 URL（host 为空）: {url!r}")
        if not port_s.isdigit():
            raise BrowserError(f"非法端口: {port_s!r}（须为数字）")
        port = int(port_s)
        if not (0 < port < 65536):
            raise BrowserError(f"端口越界: {port}（须 1-65535）")
    else:
        host = host_part
    if not host:
        raise BrowserError(f"非法 URL（host 为空）: {url!r}")
    return {"scheme": scheme, "host": host, "port": port, "path": "/" + path}


def _recv_all(sock: socket.socket) -> bytes:
    """接收至对端关闭（Connection: close 口径）。"""
    chunks = []
    while True:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            raise BrowserError("响应超时（接收阶段）")
        if not chunk:
            break
        chunks.append(chunk)
    return b"".join(chunks)


def parse_response(raw: bytes) -> dict:
    """F2 响应解析：状态行/头/体（显式拆分，畸形响应报错）。"""
    try:
        text = raw.decode("utf-8", errors="replace")
    except Exception:
        raise BrowserError("响应解码失败")
    head, sep, body = text.partition("\r\n\r\n")
    if not sep:
        raise BrowserError("畸形响应（缺少头体分隔）")
    lines = head.split("\r\n")
    status_line = lines[0]
    parts = status_line.split(" ", 2)
    if len(parts) < 2 or not parts[1].isdigit():
        raise BrowserError(f"畸形状态行: {status_line!r}")
    status = int(parts[1])
    headers = {}
    for line in lines[1:]:
        if ":" in line:
            k, _, v = line.partition(":")
            headers[k.strip().lower()] = v.strip()
    return {"status": status, "headers": headers, "body": body}


def http_get(url: str, timeout: float = 5.0) -> dict:
    """F2 HTTP GET：显式构造请求（教学口径 HTTP/1.1 + Connection: close）。

    返回 {"status", "headers", "body", "url"}；连接失败/超时报 BrowserError。
    """
    info = parse_url(url)
    if info["scheme"] == "https":
        raise BrowserError("HTTPS 教学口径未实现（见条件卡限制显式；V-P4 时代挂账）")
    try:
        sock = socket.create_connection((info["host"], info["port"]), timeout=timeout)
    except (OSError, socket.gaierror) as e:
        raise BrowserError(f"连接失败 {info['host']}:{info['port']} — {e}")
    try:
        request = (
            f"GET {info['path']} HTTP/1.1\r\n"
            f"Host: {info['host']}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode("utf-8"))
        raw = _recv_all(sock)
    except socket.timeout:
        raise BrowserError("请求超时（发送阶段）")
    finally:
        sock.close()
    resp = parse_response(raw)
    resp["url"] = url
    return resp


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1:
        r = http_get(sys.argv[1])
        print(f"status={r['status']} bytes={len(r['body'])}")
