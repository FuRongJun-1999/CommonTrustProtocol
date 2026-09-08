# -*- coding: utf-8 -*-
"""md_dex.py · MD 目录知识库的 ConditionDex 替代品

从 _ccg_dump.json 加载 CCG 注释数据，提供与 ConditionDex 相同的
.store.conn.execute() 接口，使 card_route 无需修改即可工作。

架构：
  aeis/knowledge/*.md  = 知识正本（人读/审计/git）
  aeis/knowledge/_ccg_dump.json = 路由索引（机读/card_route 消费）
  MdConditionDex = 桥接（加载 dump → 模拟 sqlite 接口 → card_route 透明使用）
"""
import json, os


class _FakeCursor:
    """模拟 sqlite cursor.fetchall()"""
    def __init__(self, rows):
        self._rows = rows
    def fetchall(self):
        return self._rows
    def fetchone(self):
        return self._rows[0] if self._rows else None


class _FakeConn:
    """模拟 sqlite connection.execute()"""
    def __init__(self, rows):
        self._rows = rows
    def execute(self, sql, *args):
        # card_route 只有一种查询：全量取带 comment 的节点
        # 预过滤在 dump 时已完成（只含有 comment 的行）
        # 未来如有其他 SQL 查询需求，在此按 SQL 内容分发
        return _FakeCursor(self._rows)


class _FakeStore:
    def __init__(self, rows):
        self.conn = _FakeConn(rows)


class MdConditionDex:
    """MD 目录知识库的 ConditionDex 替代品。

    与 ConditionDex 接口兼容：card_route(dex, question) 无需修改。
    数据源：_ccg_dump.json（从 sqlite 导出的 CCG 注释快照）。

    用法：
      dex = MdConditionDex("aeis/knowledge/_ccg_dump.json")
      results = card_route(dex, question)  # 与 sqlite 版完全一致
    """
    def __init__(self, ccg_dump_path: str):
        with open(ccg_dump_path, encoding="utf-8") as f:
            raw = json.load(f)
        # 还原为 sqlite 行格式：(id, state_attributes_json_str, content)
        self._rows = [
            (r["id"], r["sa_json"], r["content"])
            for r in raw
        ]
        self.store = _FakeStore(self._rows)
        self.db_path = ccg_dump_path  # 兼容 duck typing

    @property
    def row_count(self):
        return len(self._rows)
