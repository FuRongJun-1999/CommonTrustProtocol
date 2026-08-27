# -*- coding: utf-8 -*-
"""drive_evolve_round11b.py —— 影子/结冰 用 LLM 自然问法做条件延伸
（2 字主题的现象词必含主题字，模板变异器被 theme-in-p 过滤清零 → 改用 LLM 变异器）
"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

THEMES = {
    "影子": "影子是光直线传播被物体挡住形成的暗区——光源低影子长、光源高影子短、影子方向与光源相反、正午太阳最高影子最短、灯下/月光下也有影子",
    "结冰": "水在0°C凝固成冰（物理变化）——水面先结冰、冰浮在水上（密度比水小）、撒盐降低冰点、持续低温才冻实",
}

REPORT = {}
for theme, knowledge in THEMES.items():
    print(f"\n{'='*56}\n=== 主题: {theme} (LLM 变异) ===")
    variants = ae.gen_llm_variants(theme, knowledge, 14)
    variants = [v for v in variants if theme not in v]
    seen, uniq = set(), []
    for v in variants:
        if v not in seen:
            seen.add(v); uniq.append(v)
    variants = uniq[:14]
    print(f"  变体({len(variants)}):")
    for v in variants:
        print(f"    - {v}")
    if not variants:
        print("  LLM 无产出")
        continue
    added = []
    start_hit = None
    for rnd in range(1, 4):
        hits = ae.fp_test(theme, variants)
        ok = sum(1 for _, h in hits if h)
        if start_hit is None:
            start_hit = f"{ok}/{len(variants)}"
        print(f"  [round {rnd}] fp 命中: {ok}/{len(variants)} ({ok/len(variants)*100:.0f}%)")
        if ok == len(variants):
            REPORT[theme] = {"variants": len(variants), "start": start_hit, "final": "100%", "added": added}
            break
        misses = [v for v, h in hits if not h]
        existing = list(ae._st.DOMAIN_SYNONYM_CLUSTERS.get(theme, []))
        others = {k: v for k, v in {**ae._st.DOMAIN_SYNONYM_CLUSTERS, **ae._st.SYNONYM_CLUSTERS}.items() if k != theme}
        cands = ae.extract_candidates(theme, misses, existing, others)
        if not cands:
            print(f"  无新候选，剩余: {misses}")
            REPORT[theme] = {"variants": len(variants), "start": start_hit, "final": f"{ok}/{len(variants)}", "added": added, "left": misses}
            break
        top = [w for w, _, _ in cands[:5]]
        print(f"  未命中: {[v[:22] for v in misses]}")
        print(f"  候选: {top}")
        if ae.apply_patch(theme, top):
            added.extend(top)
            ae._st = importlib.import_module("semantic_translate")
            ae._st = importlib.reload(ae._st)
        else:
            break
    else:
        REPORT[theme] = {"variants": len(variants), "start": start_hit, "final": "rounds-exhausted", "added": added}

print("\n" + "="*56)
print("=== round11b 报告 ===")
for t, r in REPORT.items():
    print(f"  {t}: {r}")
