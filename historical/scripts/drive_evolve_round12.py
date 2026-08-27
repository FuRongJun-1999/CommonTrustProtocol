# -*- coding: utf-8 -*-
"""round12 化学域条件延伸：发酵/氧化 —— LLM 变异器（2字主题现象词必含主题字，模板变异器被过滤）
"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

THEMES = {
    "发酵": "面团发酵是酵母菌吃糖产生二氧化碳气体撑起面团——需要温水(30-40°C)+糖+时间；馒头松软是气泡留下小孔；发霉是坏霉菌",
    "氧化": "铁生锈是铁+氧气+水化学反应生成铁锈(氧化铁)——潮湿水膜加速、盐水更快、干燥慢；防锈靠隔绝水氧(涂油/镀锌/不锈钢/油漆)",
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
print("=== round12 条件延伸报告 ===")
for t, r in REPORT.items():
    print(f"  {t}: {r}")
