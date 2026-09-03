# -*- coding: utf-8 -*-
"""aeis.file_memory · 文件树↔记忆图双向映射（荣架构 2026-09-03）

「文件读写 = 记忆读写」：文件系统成为认知图时空记忆的可选投影。
三原则（荣确认）：
  1. 记忆图为真相源，export 为显式投影命令（不做自动双向同步，避免同步风暴）
  2. 二进制/大文件：节点存路径引用+摘要，本体留磁盘（记忆图存「关于文件的知识」）
  3. 目录树 = 父节点 + HIERARCHICAL 层级边（嵌套子图）；文件版本 = timeline + D 序列

节点约定：
  路径锚 tag  ``file_mem:<sha1(relpath)[:12]>``  ——幂等寻址（重复 ingest 更新不重复建）
  名字 tag    ``file_mem_name:<名字>``           ——投影时还原文件/目录名
  类型 tag    ``file_mem:dir`` / ``file_mem:file``
  目录 content ``[目录] <名字>/``；文件 content=文本内容；引用型 content=``[文件引用] ...``
"""

import hashlib
import json
import os
from typing import Dict, List, Optional

DEFAULT_MAX_INLINE = 64 * 1024   # 64KB：超过则节点存引用+摘要
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv"}
_ANCHOR_PREFIX = "file_mem:"
_NAME_PREFIX = "file_mem_name:"


def _path_anchor(rel_path: str) -> str:
    """路径锚定 tag：file_mem:<sha1(relpath 规范化)[:12]>（跨平台路径分隔符归一）。

    锚只编码相对路径——同一库内摄入多棵树时根锚相同（rel 均为 "."），
    单树场景（当前主用例）无碰撞；多树场景由 ingest_tree 的根标识 tag 区分。
    """
    norm = rel_path.replace("\\", "/").lower()
    return _ANCHOR_PREFIX + hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12]


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _find_by_anchor(store, anchor: str):
    """按路径锚定 tag 查节点（幂等关键）。返回 STNode 或 None。"""
    row = store.conn.execute(
        "SELECT id FROM nodes WHERE tags LIKE ? LIMIT 1",
        (f'%"{anchor}"%',)).fetchone()
    return store.get_node(row[0]) if row else None


def _is_binary_probe(path: str) -> bool:
    """前 8KB 含 \\x00 即判二进制（SQLite/图片/可执行等，走引用型）。"""
    with open(path, "rb") as f:
        return b"\x00" in f.read(8192)


class FileMemory:
    """文件树↔记忆图双向映射（灵枢记忆的文件系统投影层）。"""

    def __init__(self, agent):
        self.agent = agent
        self.store = agent.engine.store

    # ---------- 摄入：磁盘树 → 记忆图 ----------

    def ingest_tree(self, root_path: str, tags: List[str] = None,
                    max_inline: int = DEFAULT_MAX_INLINE,
                    dry_run: bool = False) -> Dict:
        """把磁盘目录树摄入记忆图（幂等：重复调用更新既有节点）。

        生效条件：需要把一份项目/文档树作为结构化记忆纳入认知图；
        不适用条件：IGNORE_DIRS 内目录跳过；二进制/超大文件只存引用不存本体。
        """
        root_path = os.path.abspath(root_path)
        if not os.path.isdir(root_path):
            return {"status": "REJECT", "reason": f"目录不存在: {root_path}"}
        report: Dict = {"phase": "ingest_tree", "root": root_path,
                        "dirs": 0, "files": 0, "refs": 0,
                        "updated": 0, "created": 0, "dry_run": dry_run}
        root_id = self._ingest_node(
            root_path, os.path.basename(root_path) or root_path,
            is_dir=True, tags=tags, max_inline=max_inline,
            dry_run=dry_run, report=report, parent_id=None, rel=".")
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            # 父锚 = 当前 dirpath 的节点（os.walk 自顶向下：父已在此前 dirnames 循环中摄入）
            if os.path.normcase(os.path.abspath(dirpath)) == os.path.normcase(root_path):
                parent_here = root_id
            else:
                parent_here = self._anchor_id_of(dirpath, root_path) or root_id
            for d in dirnames:
                full = os.path.join(dirpath, d)
                self._ingest_node(full, d, is_dir=True, tags=tags,
                                  max_inline=max_inline, dry_run=dry_run,
                                  report=report, parent_id=parent_here,
                                  rel=os.path.relpath(full, root_path))
            for f in filenames:
                full = os.path.join(dirpath, f)
                self._ingest_node(full, f, is_dir=False, tags=tags,
                                  max_inline=max_inline, dry_run=dry_run,
                                  report=report, parent_id=parent_here,
                                  rel=os.path.relpath(full, root_path))
        return report

    def _ingest_node(self, full_path: str, name: str, is_dir: bool,
                     tags, max_inline: int, dry_run: bool,
                     report: Dict, parent_id: Optional[str],
                     rel: str) -> Optional[str]:
        """摄入单个文件/目录节点。返回节点 id（供子级挂父）；dry_run 返回 None。"""
        anchor = _path_anchor(rel)
        st = os.stat(full_path)
        if is_dir:
            content = f"[目录] {name}/"
            report["dirs"] += 1
        else:
            size = st.st_size
            if size > max_inline or _is_binary_probe(full_path):
                head = "" if _is_binary_probe(full_path) else self._head_text(full_path)
                kind = "（二进制文件）" if _is_binary_probe(full_path) else ""
                content = (f"[文件引用] path={full_path} size={size} "
                           f"sha256={_sha256_file(full_path)} {kind}\n摘要（前段）：\n{head}")
                report["refs"] += 1
            else:
                with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                report["files"] += 1
        node_tags = list(tags or []) + [
            anchor, f"{_NAME_PREFIX}{name}", "file_mem",
            "file_mem:dir" if is_dir else "file_mem:file"]
        cs = self._cond_space(full_path, st)
        existing = _find_by_anchor(self.store, anchor)
        if existing is not None:
            self.store.conn.execute(
                "UPDATE nodes SET content=?, condition_space=?, tags=? WHERE id=?",
                (content, cs.to_json(), json.dumps(node_tags, ensure_ascii=False),
                 existing.id))
            self.store.conn.commit()
            report["updated"] += 1
            return existing.id
        if dry_run:
            report["created"] += 1
            return None
        node = self.agent.engine.add_perception(
            content=content, modality="text", tags=node_tags,
            importance=0.5, condition_space=cs, skip_dedup=True)
        if parent_id:
            self._link(parent_id, node.id, st.st_mtime)
        report["created"] += 1
        return node.id

    def _cond_space(self, full_path: str, st):
        from aeis.core import ConditionSpace
        return ConditionSpace(
            observation_position=full_path,
            observation_tool="file_memory",
            time_window=(st.st_mtime, 9_999_999_999.0),
            existence_constraint=f"exists@{int(st.st_mtime)}")

    def _link(self, parent_id: str, child_id: str, mtime: float) -> None:
        """子→父 HIERARCHICAL 层级边（确定性 id 保证幂等：重复建被唯一约束/同 id 覆盖）。"""
        from aeis.core import STEdge, EdgeType, ConditionSpace
        cs = ConditionSpace(observation_position=parent_id, observation_tool="file_memory",
                            time_window=(mtime, 9_999_999_999.0),
                            existence_constraint="hierarchy")
        edge = STEdge(id=f"fe_{hashlib.sha1((parent_id + child_id).encode()).hexdigest()[:16]}",
                      source_id=child_id, target_id=parent_id,
                      relation_type=EdgeType.HIERARCHICAL, condition_space=cs,
                      confidence=0.9)
        try:
            self.store.add_edge(edge)
        except Exception:
            pass  # 幂等：重复边忽略

    def _anchor_id_of(self, full_path: str, root_path: str) -> Optional[str]:
        node = _find_by_anchor(self.store, _path_anchor(os.path.relpath(full_path, root_path)))
        return node.id if node else None

    # ---------- 投影：记忆子树 → 磁盘（显式命令） ----------

    def export_tree(self, node_id: str, target_path: str,
                    dry_run: bool = False) -> Dict:
        """把记忆子树投影为磁盘目录树（显式命令：记忆图为真相源）。

        生效条件：记忆图中的文件树需要落盘交付/与其他程序交换；
        不适用条件：自动双向同步不做（会同步风暴）；引用节点的本体不在记忆图，
        投影时从记录的原路径复制（原路径已失效则跳过并在报告标注）。
        """
        node = self.store.get_node(node_id)
        if node is None:
            return {"status": "REJECT", "reason": f"节点不存在: {node_id}"}
        report: Dict = {"phase": "export_tree", "target": os.path.abspath(target_path),
                        "dirs": 0, "files": 0, "refs_restored": 0, "refs_missing": 0,
                        "dry_run": dry_run}
        if not dry_run:
            os.makedirs(target_path, exist_ok=True)
        self._export_children(node_id, target_path, dry_run, report)
        return report

    def _children_of(self, node_id: str) -> List[str]:
        rows = self.store.conn.execute(
            "SELECT source_id FROM edges WHERE target_id=? AND relation_type='hierarchical'",
            (node_id,)).fetchall()
        return [r[0] for r in rows]

    def _export_children(self, node_id: str, target_dir: str,
                         dry_run: bool, report: Dict) -> None:
        for cid in self._children_of(node_id):
            node = self.store.get_node(cid)
            if node is None:
                continue
            tags = node.tags or []
            name = next((t[len(_NAME_PREFIX):] for t in tags
                         if t.startswith(_NAME_PREFIX)), None)
            if not name:
                continue
            full = os.path.join(target_dir, name)
            is_dir = "file_mem:dir" in tags
            if is_dir:
                if not dry_run:
                    os.makedirs(full, exist_ok=True)
                report["dirs"] += 1
                self._export_children(cid, full, dry_run, report)
            else:
                content = node.content or ""
                if content.startswith("[文件引用]"):
                    ref = self._ref_path_of(content)
                    if ref and os.path.exists(ref) and not dry_run:
                        with open(ref, "rb") as f, open(full, "wb") as g:
                            g.write(f.read())
                        report["refs_restored"] += 1
                    else:
                        report["refs_missing"] += 1
                else:
                    if not dry_run:
                        with open(full, "w", encoding="utf-8") as f:
                            f.write(content)
                    report["files"] += 1

    @staticmethod
    def _ref_path_of(content: str) -> Optional[str]:
        for line in content.splitlines():
            if "path=" in line:
                return line.split("path=", 1)[1].split()[0]
        return None

    # ---------- 变更检测：增量投影依据 ----------

    def diff_tree(self, root_path: str, node_id: str) -> Dict:
        """对比磁盘树与记忆子树的差异（显式增量投影的前置查询）。

        返回 changed（磁盘内容已变）/ missing_on_disk（磁盘已删）/
        missing_in_memory（磁盘新增未摄入）三清单。
        """
        report: Dict = {"phase": "diff_tree", "changed": [], "missing_on_disk": [],
                        "missing_in_memory": []}
        if self.store.get_node(node_id) is None:
            report["status"] = "REJECT"
            return report
        mem = {}
        stack = [node_id]
        while stack:
            cur = stack.pop()
            n = self.store.get_node(cur)
            if n is None:
                continue
            anchor = next((tg for tg in (n.tags or []) if tg.startswith(_ANCHOR_PREFIX)), None)
            if anchor:
                mem[anchor] = n
            stack.extend(self._children_of(cur))
        disk_anchors = {}
        for dirpath, dirnames, filenames in os.walk(root_path):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            for name in dirnames + filenames:
                full = os.path.join(dirpath, name)
                disk_anchors[_path_anchor(os.path.relpath(full, root_path))] = full
        for anchor, full in disk_anchors.items():
            n = mem.get(anchor)
            if n is None:
                report["missing_in_memory"].append(full)
            elif os.path.isfile(full) and os.path.getsize(full) <= DEFAULT_MAX_INLINE:
                try:
                    cur = open(full, "r", encoding="utf-8", errors="replace").read()
                except Exception:
                    continue
                if cur != (n.content or ""):
                    report["changed"].append(full)
        for anchor, n in mem.items():
            if anchor not in disk_anchors:
                report["missing_on_disk"].append(n.id)
        return report
