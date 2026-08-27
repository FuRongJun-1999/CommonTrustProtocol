# -*- coding: utf-8 -*-
"""drive_evolve_contradiction.py —— 白箱自进化：矛盾类主题条件延伸迁移"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

THEMES = {
    "学习游戏趣味": {
        "conditions": ["考试前", "上班族", "上网课", "自习室", "假期", "考试周"],
        "phenomena": ["学习", "游戏", "不想学习", "学不进去"],
    },
    "学习枯燥": {
        "conditions": ["刷题", "复习", "抄写", "背单词", "晚自习"],
        "phenomena": ["学习枯燥", "学习没意思", "学不进去"],
    },
    "拖延启动": {
        "conditions": ["写作业", "做项目", "写论文", "复习", "早上", "晚上"],
        "phenomena": ["拖延", "先玩游戏", "不想开始", "拖到"],
    },
    "学习意义": {
        "conditions": ["毕业后", "工作时", "失业", "中年", "退休后"],
        "phenomena": ["学习", "用不上", "还要学", "读书"],
    },
    "知识乐趣": {
        "conditions": ["考试后", "离开学校", "带孩子", "工作后"],
        "phenomena": ["知识", "读书", "学习"],
    },
    "游戏机制": {
        "conditions": ["晚上", "周末", "假期", "睡前", "放学后"],
        "phenomena": ["游戏", "上瘾", "停不下来", "一直玩"],
    },
    "游戏责任": {
        "conditions": ["孩子", "学生", "成年人", "家长"],
        "phenomena": ["游戏", "沉迷", "怪游戏", "管不住"],
    },
    "学习娱乐平衡": {
        "conditions": ["期末", "周末", "工作日晚", "备考"],
        "phenomena": ["学习", "游戏", "先玩后学", "学一会玩一会"],
    },
}

REPORT = {}
for theme, cfg in THEMES.items():
    print(f"\n{'='*56}\n=== 主题: {theme} ===")
    ae.CONDITIONS = cfg["conditions"]
    ae.PHENOMENA = cfg["phenomena"]
    ae.TEMPLATES = [
        "为什么{cond}下会{phen}？",
        "{cond}下{phen}是为什么？",
        "在{cond}里{phen}是怎么回事？",
        "为什么{cond}后{phen}？",
    ]
    variants = ae.gen_template_variants(theme, "", 16)
    variants = [v for v in variants if theme not in v]
    seen, uniq = set(), []
    for v in variants:
        if v not in seen:
            seen.add(v); uniq.append(v)
    variants = uniq
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
        print(f"  未命中: {[v[:24] for v in misses]}")
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
print("=== 矛盾类批量自进化报告 ===")
for t, r in REPORT.items():
    print(f"  {t}: {r}")
