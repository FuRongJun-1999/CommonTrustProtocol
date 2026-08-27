# -*- coding: utf-8 -*-
"""鸟的飞行 LLM 条件延伸"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

theme = "鸟的飞行"
knowledge = "鸟能飞靠翅膀+羽毛+空心骨架：翅膀上凸下平产生升力(伯努利)，扇动产生推力，羽毛轻密增大升力面积，空心骨轻而强；人太重没翅膀肌肉差，结构不适合飞行，要借助飞机"

variants = ae.gen_llm_variants(theme, knowledge, 14)
variants = [v for v in variants if "鸟的飞行" not in v]
seen, uniq = set(), []
for v in variants:
    if v not in seen:
        seen.add(v); uniq.append(v)
variants = uniq[:14]
print(f"变体({len(variants)}):")
for v in variants:
    print(f"  - {v}")
if not variants:
    print("LLM 无产出")
    sys.exit(0)

added = []
all_other = {k: v for k, v in {**ae._st.DOMAIN_SYNONYM_CLUSTERS, **ae._st.SYNONYM_CLUSTERS}.items() if k != theme}
for rnd in range(1, 4):
    hits = ae.fp_test(theme, variants)
    ok = sum(1 for _, h in hits if h)
    print(f"[round {rnd}] fp 命中: {ok}/{len(variants)}")
    if ok == len(variants):
        print("收敛 100%")
        break
    misses = [v for v, h in hits if not h]
    existing = list(ae._st.DOMAIN_SYNONYM_CLUSTERS.get(theme, []))
    cands = ae.extract_candidates(theme, misses, existing, all_other)
    print(f"  未命中: {[v[:22] for v in misses]}")
    if not cands:
        print("  无新候选")
        break
    top = [w for w, _, _ in cands[:5]]
    print(f"  候选: {top}")
    if ae.apply_patch(theme, top):
        added.extend(top)
        ae._st = importlib.import_module("semantic_translate")
        ae._st = importlib.reload(ae._st)
        all_other = {k: v for k, v in {**ae._st.DOMAIN_SYNONYM_CLUSTERS, **ae._st.SYNONYM_CLUSTERS}.items() if k != theme}
    else:
        break
print("added:", added)
