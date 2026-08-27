# -*- coding: utf-8 -*-
"""驱动：黑色吸热条件延伸自进化"""
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

ae.CONDITIONS = ["阴天", "室内", "阳光下", "阴影里", "冬天", "夏天",
                 "灯光下", "夜里", "暗处", "空调房", "雪地", "车里"]
ae.PHENOMENA = ["黑色衣服", "深色衣服", "黑衣服", "深色"]
ae.TEMPLATES = [
    "为什么{cond}穿{phen}也热？",
    "{cond}穿{phen}会凉快吗？",
    "为什么{cond}里{phen}不热？",
    "{cond}的{phen}是不是吸热？",
    "为什么{cond}穿{phen}更合适？",
]
variants = ae.gen_template_variants("黑色吸热", "", 16)
variants = [v for v in variants if "黑色吸热" not in v]
print("变体:", len(variants))
for v in variants:
    print("  -", v)

added = []
for rnd in range(1, 4):
    hits = ae.fp_test("黑色吸热", variants)
    ok = sum(1 for _, h in hits if h)
    print(f"[round {rnd}] fp 命中: {ok}/{len(variants)} ({ok/len(variants)*100:.0f}%)")
    if ok == len(variants):
        print("收敛! 新增:", added)
        break
    misses = [v for v, h in hits if not h]
    existing = list(ae._st.DOMAIN_SYNONYM_CLUSTERS.get("黑色吸热", []))
    others = {k: v for k, v in {**ae._st.DOMAIN_SYNONYM_CLUSTERS, **ae._st.SYNONYM_CLUSTERS}.items() if k != "黑色吸热"}
    cands = ae.extract_candidates("黑色吸热", misses, existing, others)
    if not cands:
        print("无新候选，剩余:", misses)
        break
    top = [w for w, _, _ in cands[:5]]
    print("  未命中:", [v[:20] for v in misses])
    print("  候选:", top)
    if ae.apply_patch("黑色吸热", top):
        added.extend(top)
        import importlib
        importlib.reload(ae._st)
        ae._st = importlib.import_module("semantic_translate")
    else:
        break
