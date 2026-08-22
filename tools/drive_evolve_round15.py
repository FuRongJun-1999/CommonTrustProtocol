# -*- coding: utf-8 -*-
"""round15 条件延伸：降落伞/秋千/反射/蒸发 —— LLM 变异器"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

THEMES = {
    "降落伞": "降落伞靠大伞面兜住空气产生空气阻力对抗重力，阻力=重力时匀速慢降，伞大慢伞小快，小鸟轻终端速度低摔不死",
    "秋千": "秋千靠惯性保持摆动重力来回拉，越荡越高是最低点蹬腿补充能量，越来越低是摩擦耗能，钟摆同是单摆摆长定周期",
    "反射": "镜子成像是光的反射，像与物关于镜面对称左右相反上下不变，虚像看得见摸不着，平面镜不变形曲面镜变形，倒影是水面反射",
    "蒸发": "蒸发是水变成水蒸气跑到空气里不是消失，任何温度都蒸发，温度高风大面积大蒸发快，蒸发是慢汽化沸腾是快汽化",
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
print("=== round15 条件延伸报告 ===")
for t, r in REPORT.items():
    print(f"  {t}: {r}")
