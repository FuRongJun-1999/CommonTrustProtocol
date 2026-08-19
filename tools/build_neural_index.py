# -*- coding: utf-8 -*-
"""智慧之书 · 神经索引构建器（强化智能路径：离线预计算全部内容嵌入）。

把全部知识卡的内容用 bge-small-zh-v1.5 预计算为嵌入向量，
存成 npz 索引（vectors + names + domain + edu + content_hash），
查询时只编码查询向量，全库向量化余弦——不实时编码卡内容。

索引文件：neural_index.npz（向量）+ neural_index.json（元数据）
重建策略：幂等 + 增量（content_hash 变化才重编该卡；--force 全量重建）

用法：
  python -X utf8 build_neural_index.py            # 增量构建
  python -X utf8 build_neural_index.py --force    # 全量重建
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, r'D:\Program Files\1_ai')
sys.path.insert(0, r'D:\Program Files\2_ai\knowledge-base')

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX_NPZ = os.path.join(HERE, 'neural_index.npz')
INDEX_META = os.path.join(HERE, 'neural_index.json')


def content_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]


def collect_cards(dex):
    """收集全部知识条目：优先知识点（knowledge_point），其次学科卡。

    答案在知识点级（「质数」「内角和」是知识点不是卡名）——
    索引知识点才能精确回答具体问题。知识点不足时回退整卡。
    """
    from aeis.core import MemoryLayer
    cards = []
    seen = set()
    # 第一优先：knowledge_point 知识点（含卡名前缀，检索时卡名可溯源）
    for n in dex.store.query_nodes(layer=MemoryLayer.KNOWLEDGE, limit=20000):
        tags = n.tags or []
        sa = n.state_attributes
        name = sa.get('name')
        content = n.content or ''
        if not name or not content:
            continue
        if 'knowledge_point' in tags:
            # 找卡名（card:<prefix> 标签 → 查卡名）
            card_name = ''
            for t in tags:
                if t.startswith('card:'):
                    card_name = t[5:]
                    break
            key = (card_name, name)
            if key in seen:
                continue
            seen.add(key)
            # 知识点内容拼接：卡名 + 知识点名 + 内容（检索上下文）
            full = f"{card_name}·{name}: {content[:400]}"
            cards.append((f"{card_name}·{name}", sa.get('domain'),
                          sa.get('edu_level'), full))
        elif len(cards) < 1000:
            # 兜底：非知识点卡（前 1000，防爆炸）
            key = ('', name)
            if key in seen:
                continue
            seen.add(key)
            cards.append((name, sa.get('domain'), sa.get('edu_level'),
                          content[:600]))
    return cards


def main():
    force = '--force' in sys.argv[1:]
    db_path = None
    if '--db' in sys.argv:
        db_path = sys.argv[sys.argv.index('--db') + 1]
    sys.path.insert(0, HERE)
    from neural_retrieve import NeuralRetriever
    nr = NeuralRetriever()
    if not nr.available():
        print(f"模型不可用: {nr.fail_reason()}")
        return 1

    import wisdom_book as wb
    dex = wb.ConditionDex(db_path=db_path) if db_path else wb.ConditionDex()
    cards = collect_cards(dex)
    print(f"收集 {len(cards)} 张知识卡")

    # 加载旧索引（增量：content_hash 相同的跳过）
    old_meta = {}
    if os.path.exists(INDEX_META) and not force:
        try:
            with open(INDEX_META, encoding='utf-8') as f:
                old_meta = json.load(f)
        except Exception:
            old_meta = {}

    names, domains, edus, hashes = [], [], [], []
    vectors = []
    rebuilt = skipped = 0
    for name, domain, edu, content in cards:
        ch = content_hash(content)
        names.append(name)
        domains.append(domain)
        edus.append(edu)
        hashes.append(ch)
        if not force and name in old_meta and old_meta[name] == ch:
            # 复用旧索引向量
            idx = list(old_meta.keys()).index(name)
            vectors.append(None)  # 占位，稍后从 npz 读
            skipped += 1
            continue
        v = nr.embed(content)
        if v is None:
            print(f"  ! {name}: 嵌入失败")
            continue
        vectors.append(v)
        rebuilt += 1

    print(f"新建 {rebuilt} / 复用 {skipped}")

    # 需要从旧 npz 恢复复用的向量
    import numpy as np
    old_arrays = None
    if os.path.exists(INDEX_NPZ):
        try:
            old_arrays = np.load(INDEX_NPZ, allow_pickle=True)
        except Exception:
            old_arrays = None

    final_vectors = []
    final_names, final_domains, final_edus, final_hashes = [], [], [], []
    for i, (name, domain, edu, ch) in enumerate(zip(names, domains, edus, hashes)):
        v = vectors[i] if i < len(vectors) else None
        if v is None and old_arrays is not None:
            # 尝试从旧索引恢复（按名字）
            onames = list(old_arrays['names'])
            if name in onames:
                j = onames.index(name)
                v = old_arrays['vectors'][j]
        if v is None:
            print(f"  ! {name}: 无向量（跳过）")
            continue
        final_vectors.append(v)
        final_names.append(name)
        final_domains.append(domain)
        final_edus.append(edu)
        final_hashes.append(ch)

    V = np.vstack(final_vectors)
    np.savez(INDEX_NPZ, vectors=V, names=np.array(final_names),
             domains=np.array(final_domains, dtype=object),
             edus=np.array(final_edus, dtype=object))
    meta = {n: h for n, h in zip(final_names, final_hashes)}
    with open(INDEX_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
    dex.close()
    print(f"索引写入: {INDEX_NPZ} ({len(final_names)} 卡, "
          f"维度 {V.shape[1]})")
    print(f"元数据: {INDEX_META}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
