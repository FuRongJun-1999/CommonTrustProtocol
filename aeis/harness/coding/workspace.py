# -*- coding: utf-8 -*-
"""harness.coding.workspace · 编码工作区（快照/回滚——能恢复）
================================================
修改前自动快照（文件级备份）→ 可随时回滚（宪章：可逆性优先）。
"""
import json
import os
import shutil
import time


class Workspace:
    """编码工作区：文件操作 + 快照/回滚。"""

    def __init__(self, root: str, snapshots_dir: str = None):
        self.root = os.path.abspath(root)
        self.snapshots_dir = snapshots_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "coding_snapshots")
        os.makedirs(self.snapshots_dir, exist_ok=True)

    def resolve(self, rel_path: str) -> str:
        """工作区内路径解析（越权拒绝）。"""
        if not rel_path:
            return ""
        p = os.path.abspath(os.path.join(self.root, rel_path))
        if not (p == self.root or p.startswith(self.root + os.sep)):
            return ""
        return p

    # ---- 文件操作（经身体层设备语义：读/写/存在） ----

    def read_file(self, rel_path: str, max_chars: int = 20000) -> dict:
        """读工作区内文件（相对路径，截断到 max_chars 防大文件）。"""
        p = self.resolve(rel_path)
        if not p or not os.path.isfile(p):
            return {"ok": False, "error": f"文件不存在或越界: {rel_path}"}
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            text = f.read(max_chars + 1)
        truncated = len(text) > max_chars
        return {"ok": True, "path": rel_path, "content": text[:max_chars],
                "truncated": truncated}

    def write_file(self, rel_path: str, content: str, append: bool = False) -> dict:
        """写入（写前自动快照——能恢复）。"""
        p = self.resolve(rel_path)
        if not p:
            return {"ok": False, "error": f"路径越界: {rel_path}"}
        os.makedirs(os.path.dirname(p), exist_ok=True) if os.path.dirname(p) else None
        if not append and os.path.isfile(p):
            self.snapshot(rel_path, note=f"写前备份 {rel_path}")
        with open(p, "a" if append else "w", encoding="utf-8") as f:
            f.write(content)
        return {"ok": True, "path": rel_path, "chars": len(content),
                "append": append}

    def list_files(self, rel_dir: str = ".", max_items: int = 100) -> dict:
        """列工作区内文件清单（相对目录，默认前 100 项）。"""
        p = self.resolve(rel_dir)
        if not p or not os.path.isdir(p):
            return {"ok": False, "error": f"目录不存在或越界: {rel_dir}"}
        items = []
        try:
            for name in sorted(os.listdir(p))[:max_items]:
                fp = os.path.join(p, name)
                items.append({"name": name, "type": "dir" if os.path.isdir(fp) else "file",
                              "size": os.path.getsize(fp) if os.path.isfile(fp) else 0})
        except OSError as exc:
            return {"ok": False, "error": str(exc)}
        return {"ok": True, "dir": rel_dir, "items": items}

    def exists(self, rel_path: str) -> dict:
        """判断工作区内路径是否存在。"""
        p = self.resolve(rel_path)
        return {"ok": True, "path": rel_path, "exists": bool(p and os.path.exists(p))}

    # ---- 快照/回滚 ----

    def snapshot(self, rel_path: str = None, note: str = "") -> str:
        """快照：目标文件（或全工作区文本类文件）→ snapshots/<id>/。
        返回 snapshot_id。"""
        snap_id = f"snap_{int(time.time()*1000)}"
        target = os.path.join(self.snapshots_dir, snap_id)
        os.makedirs(target, exist_ok=True)
        saved = 0
        if rel_path:
            p = self.resolve(rel_path)
            if p and os.path.isfile(p):
                dst = os.path.join(target, "files", rel_path.lstrip("/\\"))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(p, dst)
                saved = 1
        else:
            # 全工作区文本快照（小文件）
            for base, dirs, files in os.walk(self.root):
                dirs[:] = [d for d in dirs if d not in (".git", "__pycache__",
                                                        "node_modules", "models",
                                                        "weights", "data")]
                for fn in files:
                    fp = os.path.join(base, fn)
                    if os.path.getsize(fp) > 200000:
                        continue
                    rel = os.path.relpath(fp, self.root)
                    dst = os.path.join(target, "files", rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(fp, dst)
                    saved += 1
        meta = {"id": snap_id, "ts": time.time(), "note": note,
                "saved": saved, "root": self.root}
        with open(os.path.join(target, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
        return snap_id

    def revert(self, snap_id: str) -> dict:
        """回滚到快照：快照文件复制回工作区。返回恢复文件数。"""
        target = os.path.join(self.snapshots_dir, snap_id)
        meta_path = os.path.join(target, "meta.json")
        if not os.path.isfile(meta_path):
            return {"ok": False, "error": f"快照不存在: {snap_id}"}
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        files_dir = os.path.join(target, "files")
        restored = 0
        if os.path.isdir(files_dir):
            for base, _, files in os.walk(files_dir):
                for fn in files:
                    src = os.path.join(base, fn)
                    rel = os.path.relpath(src, files_dir)
                    dst = os.path.join(self.root, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    restored += 1
        return {"ok": True, "snapshot": snap_id, "restored": restored,
                "note": meta.get("note", "")}

    def list_snapshots(self, limit: int = 20) -> list:
        out = []
        for name in sorted(os.listdir(self.snapshots_dir),
                           reverse=True)[:limit]:
            mp = os.path.join(self.snapshots_dir, name, "meta.json")
            if os.path.isfile(mp):
                try:
                    with open(mp, "r", encoding="utf-8") as f:
                        out.append(json.load(f))
                except Exception:
                    pass
        return out
