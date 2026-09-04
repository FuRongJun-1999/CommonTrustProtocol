# -*- coding: utf-8 -*-
"""aeis.nightly_cleanup · 知识层夜间整理（荣指令 2026-09-01）

睡眠巩固的「整理阶段」：知识层应像认知图/学科知识库——存结构性、有联系、
有意义的信息。低质量运行态快照、无边孤岛迁移到情境层（decay 自然遗忘）。
情境层随机联想——跨层探索不同条件下是否有有价值的联系。

三步：
  1. 分拣迁移：知识层 → 情境层，两条捕获规则：
     ①无边孤岛（无结构标签）→ 情境层（原规则）
     ②外部钩子噪声（有边但 content 命中运行态噪声前缀，或无结构标签且
       importance<0.3）→ 情境层（外部用户反馈修正：dsh/user 自动钩子噪声
       带 自动边 漏过孤岛规则；迁移只换层不删边，无数据丢失）
  2. 联想补边：有结构标签但无边的知识节点 → recall 找关联 → relate
  3. 情境层随机联想：情境层抽样 × 知识层抽样 → 跨层 relate 尝试

用法：
  Agent.nightly_cleanup(dry_run=True)   # 预演（不写库）
  Agent.nightly_cleanup()               # 执行
  aeis__nightly_cleanup (MCP 工具)      # 睡眠巩固 prompt 调用
"""

import json
import random
from typing import Dict, List, Optional

# 结构性标签白名单（保留知识层）
KEEP_TAGS = {
    'domain:', 'reusable_pattern', 'distilled', 'learning_task',
    'sleep_report', 'project_memory', 'migrated', 'protection',
    'sleep_consolidation', 'game_design', 'protocol', 'whitebox',
    'nightly_cleanup', 'subgraph_replace',
    # v1.1 扩容（外部用户库实测反馈：KEEP_TAGS 过窄）：
    'knowledge_point', 'file_mem', 'milestone', 'anchor', 'user_pinned',
    'seed_knowledge', 'kccs',
}

# 运行态噪声模式（content 前缀匹配 → 迁移）
NOISE_PREFIXES = ('[心跳]', '[distill', '[初始记忆播种]', '[对话assistant]',
                  '[对话user]')


def _has_keep_tag(tags: List[str]) -> bool:
    for t in tags:
        for kt in KEEP_TAGS:
            if t == kt or t.startswith(kt):
                return True
    return False


def nightly_cleanup(agent, dry_run: bool = False,
                   联想_sample_size: int = 5) -> Dict:
    """知识层夜间整理：分拣迁移 + 联想补边 + 情境层随机联想。

    Args:
        agent: aeis Agent 实例
        dry_run: True=只统计不写库（预演）
        联想_sample_size: 情境层随机抽样数（跨层联想尝试）
    """
    store = agent.engine.store
    c = store.conn.cursor()
    report: Dict = {
        'phase': 'nightly_cleanup',
        'scanned': 0, 'migrated': 0, 'kept_structural': 0,
        'assoc_edges_added': 0, 'cross_layer_attempts': 0,
        'cross_layer_found': 0, 'dry_run': dry_run,
    }

    # ---- Phase 1: 分拣迁移 ----
    # ① 无边孤岛（原规则+importance 下限 v1.1）：知识层无边 + 无结构标签
    #    + importance < 0.5 → 情境层（外部用户反馈：高重要度孤岛可能是
    #    尚未连线的核心知识，不迁）
    c.execute("""
        SELECT n.id, n.tags FROM nodes n WHERE n.layer='knowledge'
        AND COALESCE(n.importance, 0) < 0.5
        AND NOT EXISTS (SELECT 1 FROM edges e WHERE e.source_id=n.id OR e.target_id=n.id)
    """)
    orphans = c.fetchall()
    report['scanned'] = len(orphans)

    migrate_ids = []
    for nid, tags_str in orphans:
        tags = json.loads(tags_str) if tags_str else []
        if not _has_keep_tag(tags):
            migrate_ids.append(nid)
    report['kept_structural'] = len(orphans) - len(migrate_ids)
    report['migrated'] = len(migrate_ids)  # v1.1 修正：恒 0 bug 根因=从未回写

    # ② 外部钩子噪声迁移（外部用户反馈修正）：有边但满足噪声特征的知识节点
    #    同样迁到情境层（边保留不删，仅换层）——覆盖 dsh/user 自动钩子产生、
    #    带 自动边 所以漏过孤岛规则 的运行态噪声。两条捕获规则：
    #    A. content 前缀命中 NOISE_PREFIXES（明确运行态噪声标识）
    #    B. 无结构标签 + importance < 0.3（低质信号，钩子噪声普遍低重要度）
    c.execute("""
        SELECT n.id, n.tags, n.importance, n.content FROM nodes n WHERE n.layer='knowledge'
        AND EXISTS (SELECT 1 FROM edges e WHERE e.source_id=n.id OR e.target_id=n.id)
    """)
    noisy = c.fetchall()
    report['noisy_scanned'] = len(noisy)
    noisy_migrated = 0
    for nid, tags_str, importance, content in noisy:
        tags = json.loads(tags_str) if tags_str else []
        if _has_keep_tag(tags):
            continue
        is_noise_prefix = isinstance(content, str) and content.startswith(NOISE_PREFIXES)
        is_low_value = (importance is None) or (importance < 0.3)
        if is_noise_prefix or (is_low_value and not _has_keep_tag(tags)):
            migrate_ids.append(nid)
            noisy_migrated += 1
    report['noisy_migrated'] = noisy_migrated

    if not dry_run and migrate_ids:
        for i in range(0, len(migrate_ids), 500):
            batch = migrate_ids[i:i + 500]
            ph = ','.join('?' * len(batch))
            c.execute(f"UPDATE nodes SET layer='context' WHERE id IN ({ph})", batch)
        store.conn.commit()

    # ---- Phase 2: 联想补边（有结构标签但无边的知识节点）----
    c.execute("""
        SELECT n.id, n.content FROM nodes n WHERE n.layer='knowledge'
        AND NOT EXISTS (SELECT 1 FROM edges e WHERE e.source_id=n.id OR e.target_id=n.id)
        LIMIT 20
    """)
    edgeless = c.fetchall()
    for nid, content in edgeless:
        if len(content) < 10:
            continue
        try:
            matches = agent.recall(content[:60], limit=3)
            for m in matches:
                mid = m.get('id', '') if isinstance(m, dict) else str(m)
                if mid and mid != nid and mid.startswith('node_'):
                    if not dry_run:
                        agent.relate(nid, mid, relation='similar',
                                     confidence=0.6, source_evidence='nightly_assoc')
                    report['assoc_edges_added'] += 1
                    break  # 每节点只补一条最强联想
        except Exception:
            pass

    # ---- Phase 3: 情境层随机联想（跨层探索）----
    c.execute("""
        SELECT id, content FROM nodes WHERE layer='context'
        AND length(content) > 20 ORDER BY RANDOM() LIMIT ?
    """, (联想_sample_size,))
    ctx_samples = c.fetchall()
    c.execute("""
        SELECT id, content FROM nodes WHERE layer='knowledge'
        AND length(content) > 20 ORDER BY RANDOM() LIMIT 20
    """)
    k_pool = c.fetchall()

    for ctx_id, ctx_content in ctx_samples:
        for k_id, k_content in k_pool:
            # 简单词交集判定（确定性，零 LLM）
            ctx_words = set(ctx_content[:40])
            k_words = set(k_content[:40])
            overlap = len(ctx_words & k_words)
            if overlap >= 4:  # 至少 4 个字符交集
                report['cross_layer_attempts'] += 1
                if not dry_run:
                    try:
                        agent.relate(ctx_id, k_id, relation='similar',
                                     confidence=0.5, source_evidence='nightly_cross')
                        report['cross_layer_found'] += 1
                    except Exception:
                        pass
                break  # 每个情境节点只尝试一次

    return report
