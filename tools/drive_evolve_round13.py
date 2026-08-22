# -*- coding: utf-8 -*-
"""round13 生物域条件延伸：感冒/光合作用/遗传/萌发 —— LLM 变异器"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

THEMES = {
    "感冒": "感冒是病毒感染上呼吸道（鼻病毒等），受凉降低免疫力是帮凶，普通感冒7-10天自愈，预防靠洗手通风锻炼睡眠",
    "光合作用": "植物光合作用：叶绿体用阳光+二氧化碳+水制造葡萄糖和氧气，叶子绿是叶绿素反射绿光，晚上只呼吸不光合",
    "遗传": "孩子基因一半来自爸爸一半来自妈妈，基因重新组合使兄弟姐妹不同，遗传决定倾向环境决定表现",
    "萌发": "种子发芽三要素水+空气+适宜温度，浇水唤醒种子激活代谢，多数种子不需要光，种子自带养分",
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
print("=== round13 条件延伸报告 ===")
for t, r in REPORT.items():
    print(f"  {t}: {r}")
