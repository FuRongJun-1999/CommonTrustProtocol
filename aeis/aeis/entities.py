#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
entity_registry · 实体注册表（v1.3 P0-1）
实体解析：别名映射、上下文组装、置信度演化、合并
协议依据：智能论 1.7 节（自我意识）、0.0.4 节（命名与条件空间声明）、1.1.1 节
纯标准库 · 零外部依赖 · 与 spacetime_memory_core 共享存储（duck-typed store）
"""

import json
import time
import uuid
from typing import Dict, List, Optional


class EntityRegistry:
    """实体注册表：为每个被识别的唯一实体维护规范记录（P0-1）"""

    def __init__(self, store):
        self.store = store
        self._init_tables()
        self._load_cache()

    # ---- 初始化 ----

    def _init_tables(self):
        c = self.store.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                name TEXT,
                entity_type TEXT,
                aliases TEXT,
                first_seen REAL,
                last_updated REAL,
                description TEXT,
                confidence REAL DEFAULT 0.5
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)')
        # v1.3 迁移：盲区表增加探索次数列（已存在则跳过）
        try:
            c.execute("ALTER TABLE blindspots ADD COLUMN attempts INTEGER DEFAULT 0")
        except Exception:
            pass
        self.store.conn.commit()

    def _load_cache(self):
        """内存缓存：名称/别名 → 实体ID（加速解析）"""
        self._alias_map = {}
        c = self.store.conn.cursor()
        c.execute("SELECT id, name, aliases FROM entities")
        for eid, name, aliases_json in c.fetchall():
            self._alias_map[name] = eid
            try:
                for a in json.loads(aliases_json or "[]"):
                    self._alias_map[a] = eid
            except Exception:
                pass

    # ---- 注册 / 查询 ----

    def register_entity(self, name: str, entity_type: str = "person",
                        aliases: List[str] = None, description: str = "",
                        confidence: float = 0.5) -> Dict:
        """注册或更新实体（重复名称 → 返回既有实体）"""
        name = name.strip()
        if not name:
            raise ValueError("实体名称不能为空")
        existing_id = self._alias_map.get(name)
        if existing_id:
            return self.get_entity(existing_id)
        eid = f"ent_{uuid.uuid4().hex[:8]}"
        aliases = [a for a in (aliases or []) if a and a != name]
        now = time.time()
        c = self.store.conn.cursor()
        c.execute("INSERT INTO entities VALUES (?,?,?,?,?,?,?,?)",
                  (eid, name, entity_type, json.dumps(aliases), now, now, description, confidence))
        self.store.conn.commit()
        self._alias_map[name] = eid
        for a in aliases:
            self._alias_map[a] = eid
        return self.get_entity(eid)

    def get_entity(self, entity_id: str) -> Optional[Dict]:
        c = self.store.conn.cursor()
        c.execute("SELECT * FROM entities WHERE id=?", (entity_id,))
        row = c.fetchone()
        if not row:
            return None
        return {
            "id": row[0], "name": row[1], "entity_type": row[2],
            "aliases": json.loads(row[3] or "[]"),
            "first_seen": row[4], "last_updated": row[5],
            "description": row[6], "confidence": row[7],
        }

    def list_entities(self, limit: int = 100) -> List[Dict]:
        c = self.store.conn.cursor()
        c.execute("SELECT id FROM entities ORDER BY last_updated DESC LIMIT ?", (limit,))
        return [self.get_entity(r[0]) for r in c.fetchall()]

    # ---- 解析 ----

    def resolve_entity(self, query: str) -> Optional[Dict]:
        """输入查询（名称/别名/ID），返回最匹配实体（支持别名解析）"""
        query = query.strip()
        if not query:
            return None
        if query.startswith("ent_"):
            return self.get_entity(query)
        eid = self._alias_map.get(query)
        return self.get_entity(eid) if eid else None

    def resolve_entities(self, text: str) -> List[Dict]:
        """从文本中提取并解析已知实体（别名匹配）"""
        found = {}
        for alias, eid in self._alias_map.items():
            if alias and alias in text:
                found[eid] = self.get_entity(eid)
        return list(found.values())

    def extract_entities(self, text: str) -> List[str]:
        """返回文本中出现的实体ID列表（供感知入口挂接）"""
        return [e["id"] for e in self.resolve_entities(text)]

    # ---- 上下文组装 ----

    def get_entity_context(self, entity_id: str, limit: int = 50) -> Dict:
        """以实体为中心的上下文（规范信息 + 关联节点）"""
        entity = self.get_entity(entity_id)
        if not entity:
            return {"entity": None, "nodes": []}
        nodes = self.store.get_nodes_by_tag(f"ent:{entity_id}", limit=limit)
        return {"entity": entity, "nodes": nodes}

    def link_node(self, entity_id: str, node_id: str):
        """将节点挂到实体（ent:<id> 标记）"""
        if self.get_entity(entity_id) and self.store.get_node(node_id):
            self.store.tag_node(node_id, f"ent:{entity_id}")

    # ---- 演化 / 合并 ----

    def update_confidence(self, entity_id: str, delta: float):
        c = self.store.conn.cursor()
        c.execute("UPDATE entities SET confidence = MIN(1.0, MAX(0.0, confidence + ?)), last_updated=? WHERE id=?",
                  (delta, time.time(), entity_id))
        self.store.conn.commit()

    def merge_entities(self, primary_id: str, secondary_id: str) -> bool:
        """合并两个实体（保留合并历史：secondary 的别名并入 primary，节点重挂）"""
        primary = self.get_entity(primary_id)
        secondary = self.get_entity(secondary_id)
        if not primary or not secondary or primary_id == secondary_id:
            return False
        merged_aliases = sorted(set(primary["aliases"] + secondary["aliases"] + [secondary["name"]]))
        c = self.store.conn.cursor()
        c.execute("UPDATE entities SET aliases=?, last_updated=?, confidence=? WHERE id=?",
                  (json.dumps(merged_aliases), time.time(),
                   min(1.0, primary["confidence"] + secondary["confidence"] * 0.5), primary_id))
        # 节点重挂
        c.execute("SELECT id FROM nodes WHERE tags LIKE ?", (f"%ent:{secondary_id}%",))
        for row in c.fetchall():
            node = self.store.get_node(row[0])
            if node and f"ent:{secondary_id}" in node.tags:
                node.tags.remove(f"ent:{secondary_id}")
                node.tags.append(f"ent:{primary_id}")
                c.execute("UPDATE nodes SET tags=? WHERE id=?", (json.dumps(node.tags), row[0]))
        c.execute("DELETE FROM entities WHERE id=?", (secondary_id,))
        self.store.conn.commit()
        self._load_cache()
        return True


# ---- 便捷工厂 ----

def bootstrap_registry(store, entities: List[Dict]) -> EntityRegistry:
    """用已知实体表初始化注册表（验收标准：初始填充）"""
    reg = EntityRegistry(store)
    for ent in entities:
        reg.register_entity(
            name=ent.get("name", ""), entity_type=ent.get("entity_type", "person"),
            aliases=ent.get("aliases", []), description=ent.get("description", ""),
            confidence=ent.get("confidence", 0.5))
    return reg
