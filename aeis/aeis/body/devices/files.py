#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
body.devices.files · 文件系统设备（BODY-REV1）
==============================================
动作：
- list: 列出目录（名称/大小/修改时间，不递归）
- read: 读文本文件（截断，默认 10KB）
- write: 写文本文件（默认追加关闭）
- exists: 路径存在性

安全边界：所有路径必须落在工作区内（resolve 后前缀校验），越权拒绝。
输出为 DeviceResult：文件内容是数据（provenance=device:files）。
"""

import os
import time
from typing import Dict, Optional

from ..base import BodyDevice, DeviceResult

DEFAULT_READ_MAX = 10_000  # 单次读上限（字符）
LIST_LIMIT = 200           # 单次列目录上限


class FilesDevice(BodyDevice):
    """文件系统设备（感知模态 text，工作区受限）。"""

    name = "files"
    modality = "text"
    description = "文件系统（工作区白名单内 list/read/write/exists，越权拒绝）"

    # ---- 接口 ----

    def check(self) -> Dict:
        if not self.workspace:
            return {"available": True, "detail": "无工作区限制（所有路径可用）"}
        if os.path.isdir(self.workspace):
            return {"available": True, "detail": f"工作区: {self.workspace}"}
        return {"available": False, "detail": f"工作区不存在: {self.workspace}"}

    def invoke(self, action: str, params: Optional[Dict] = None) -> DeviceResult:
        p = params or {}
        try:
            if action == "list":
                return self._list(p)
            if action == "read":
                return self._read(p)
            if action == "write":
                return self._write(p)
            if action == "exists":
                return self._exists(p)
        except PermissionError as exc:
            return self._fail(str(exc))
        except Exception as exc:
            return self._fail(f"{action} 异常: {exc}")
        return self._fail(f"未知动作 {action}（可用: list/read/write/exists）")

    # ---- 路径校验 ----

    def _resolve(self, path: str) -> str:
        """解析路径并强制工作区边界。"""
        if not path:
            raise PermissionError("路径为空")
        if self.workspace:
            ws = os.path.abspath(self.workspace)
            target = os.path.abspath(os.path.join(ws, path))
            if not (target == ws or target.startswith(ws + os.sep)):
                raise PermissionError(f"路径越出工作区: {path}")
            return target
        return os.path.abspath(path)

    # ---- 动作 ----

    def _list(self, p: Dict) -> DeviceResult:
        path = self._resolve(p.get("path", "."))
        if not os.path.isdir(path):
            return self._fail(f"不是目录: {p.get('path')}")
        entries = []
        try:
            names = sorted(os.listdir(path))[:LIST_LIMIT]
        except PermissionError:
            return self._fail(f"无权访问: {p.get('path')}")
        for name in names:
            full = os.path.join(path, name)
            try:
                st = os.stat(full)
                entries.append({
                    "name": name,
                    "is_dir": os.path.isdir(full),
                    "size": st.st_size,
                    "mtime": round(st.st_mtime, 1),
                })
            except OSError:
                entries.append({"name": name, "is_dir": False, "size": 0, "mtime": 0})
        summary = f"目录 {p.get('path', '.')}: {len(entries)} 项"
        return self._r(entries, "list", text_summary=summary)

    def _read(self, p: Dict) -> DeviceResult:
        path = self._resolve(p.get("path", ""))
        max_chars = int(p.get("max_chars", DEFAULT_READ_MAX))
        if not os.path.isfile(path):
            return self._fail(f"不是文件: {p.get('path')}")
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read(max_chars + 1)
        except OSError as exc:
            return self._fail(f"读取失败: {exc}")
        truncated = len(text) > max_chars
        text = text[:max_chars]
        summary = f"已读 {p.get('path')}（{len(text)} 字符{'，已截断' if truncated else ''}）"
        return self._r(
            {"path": p.get("path"), "content": text, "truncated": truncated,
             "chars": len(text)},
            "read", text_summary=summary,
        )

    def _write(self, p: Dict) -> DeviceResult:
        path = self._resolve(p.get("path", ""))
        content = str(p.get("content", ""))
        append = bool(p.get("append", False))
        mode = "a" if append else "w"
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)
        summary = f"已写入 {p.get('path')}（{len(content)} 字符{'，追加' if append else ''}）"
        return self._r(
            {"path": p.get("path"), "chars": len(content), "append": append},
            "write", text_summary=summary,
        )

    def _exists(self, p: Dict) -> DeviceResult:
        path = self._resolve(p.get("path", ""))
        exists = os.path.exists(path)
        summary = f"{p.get('path')} 存在" if exists else f"{p.get('path')} 不存在"
        return self._r(
            {"path": p.get("path"), "exists": exists,
             "is_dir": os.path.isdir(path) if exists else False},
            "exists", text_summary=summary,
        )
