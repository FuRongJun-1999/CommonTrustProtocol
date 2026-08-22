# -*- coding: utf-8 -*-
"""round14 化学/生物域条件延伸：燃烧/溶解/汽水气泡/血液循环 —— LLM 变异器"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

THEMES = {
    "燃烧": "燃烧是可燃物+氧气+着火点三条件缺一不可的剧烈氧化，灭火破坏条件（水降温/盖隔氧/移走可燃物），油锅电器着火不能用水",
    "溶解": "溶解是物质分散成微粒均匀混在溶剂里不是消失，盐溶解变咸糖溶解变甜，溶解≠融化，热水溶解快，搅拌加热碾碎加速",
    "汽水气泡": "汽水气泡是二氧化碳高压压进水里的，打开减压溶解度降低跑出来，放久没气，摇晃喷出，喝汽水打嗝是二氧化碳释放",
    "血液循环": "心脏是泵把血液泵到全身输送氧气养分，运动时肌肉需更多氧气心跳加快，心跳快慢跟需求走，心脏健康靠运动饮食睡眠",
}

REPORT = {}
for theme, knowledge in THEMES.items():
    print(f"\n{'='*56}\n=== 主题: {theme} (LLM 变异) ===")
    variants = ae.gen_llm_variants(theme, knowledge, 12)
    variants = [v for v in variants if theme not in v]
    seen, uniq = set(), []
    for v in variants:
        if v not in seen:
            seen.add(v); uniq.append(v)
    variants = uniq[:12]
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
print("=== round14 条件延伸报告 ===")
for t, r in REPORT.items():
    print(f"  {t}: {r}")
