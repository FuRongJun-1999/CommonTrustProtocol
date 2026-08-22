# -*- coding: utf-8 -*-
"""drive_evolve_round11.py —— 自进化 round11：回声/影子/结冰 条件延伸迁移
参照静电流程：模板变异（条件×现象）→ fp 命中 → 触发词补盲 → 收敛
"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

THEMES = {
    "回声": {
        "conditions": ["山谷", "山洞", "空房间", "楼道", "隧道", "体育馆", "大礼堂", "桥洞",
                       "悬崖边", "峡谷", "地铁站", "地下车库", "高架桥下", "室内球场"],
        "phenomena": ["有回声", "回音", "喊话有回声", "回声很清楚", "听得到回声", "回声很响",
                      "说话有回音", "有回响"],
    },
    "影子": {
        "conditions": ["中午", "早晨", "傍晚", "路灯下", "台灯下", "月光下", "手电筒下",
                       "蜡烛旁", "阳光下", "阴天", "室内灯", "车灯前", "清晨", "黄昏"],
        "phenomena": ["影子变长", "影子变短", "影子消失", "影子在左边", "影子在右边",
                      "影子跟着我", "影子拉得很长", "影子很淡"],
    },
    "结冰": {
        "conditions": ["冬天", "北方", "下雪天", "清晨", "深冬", "冰箱里", "高山湖",
                       "结冰的河", "零下", "严寒", "冬天早晨", "夜里", "冷库", "高原"],
        "phenomena": ["水面结冰", "河面冻住", "湖面结冰", "水冻成冰", "结冰了", "上冻",
                      "冰面很滑", "窗玻璃结冰"],
    },
}

REPORT = {}
for theme, cfg in THEMES.items():
    print(f"\n{'='*56}\n=== 主题: {theme} ===")
    ae.CONDITIONS = cfg["conditions"]
    ae.PHENOMENA = cfg["phenomena"]
    ae.TEMPLATES = [
        "为什么{cond}下会有{phen}？",
        "在{cond}里看到{phen}是什么原理？",
        "{cond}出现{phen}是为什么？",
        "为什么{cond}时{phen}？",
        "{cond}下的{phen}是怎么回事？",
    ]
    variants = ae.gen_template_variants(theme, "", 16)
    variants = [v for v in variants if theme not in v]
    seen, uniq = set(), []
    for v in variants:
        if v not in seen:
            seen.add(v); uniq.append(v)
    variants = uniq[:16]
    print(f"  变体({len(variants)}): {variants}")
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
print("=== round11 批量自进化报告 ===")
for t, r in REPORT.items():
    print(f"  {t}: {r}")
