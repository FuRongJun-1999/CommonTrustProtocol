# -*- coding: utf-8 -*-
"""结冰 第二轮：清理后的簇 + 加固提取器，重跑 LLM 条件延伸"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

theme = "结冰"
knowledge = "水在0°C凝固成冰（物理变化）——水面先结冰、冰浮在水上（密度比水小）、撒盐降低冰点、持续低温才冻实"
variants = [
    "为什么我家窗户玻璃上总会出现一层白霜，把整个窗子都糊住了",
    "冬天水管冻裂了，是不是温度太低把里面的水冻住了",
    "我家水缸里的水总是上面先冻住，下面的水还是液态的",
    "冰箱里的冰块为什么浮在水面上，不会沉到底",
    "大冬天的河面结了薄薄一层冰，人踩上去为什么会裂开",
    "为什么鱼塘里的水只冻住表层，鱼儿还能在下面游",
    "我家屋顶的瓦片上结满了冰凌，会不会压坏房子",
]
variants = [v for v in variants if theme not in v]
print(f"变体({len(variants)}):")
for v in variants:
    print(f"  - {v}")

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
    print(f"  未命中: {[v[:20] for v in misses]}")
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
