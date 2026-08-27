# -*- coding: utf-8 -*-
"""drive_evolve_all.py —— 白箱自进化批量扩散：全部生活主题条件延伸迁移"""
import sys, os, json, importlib
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"D:\Program Files\2_ai\CommonTrustProtocol\tools")
import auto_evolve as ae

THEMES = {
    "雷声闪电": {
        "conditions": ["近处", "远处", "山里", "高楼", "夏天", "冬天", "夜晚", "雷暴"],
        "phenomena": ["雷声", "闪电", "打雷", "雷声大"],
    },
    "瓶外水珠": {
        "conditions": ["夏天", "冬天", "空调房", "冰箱拿出来", "冰饮料", "冷饮杯", "玻璃杯"],
        "phenomena": ["水珠", "冒汗", "瓶子外", "杯壁"],
    },
    "饺子浮起": {
        "conditions": ["冷水下锅", "开水下锅", "冻饺子", "肉馅", "素馅", "煮太久", "水滚"],
        "phenomena": ["饺子", "浮起来", "沉底"],
    },
    "切洋葱": {
        "conditions": ["冷藏后", "水里切", "刀沾水", "戴眼镜", "通风处", "冰冻过"],
        "phenomena": ["洋葱", "流泪", "辣眼睛"],
    },
    "吸管吸饮料": {
        "conditions": ["高海拔", "太空中", "吸管太长", "漏气", "酸奶", "气泡水"],
        "phenomena": ["吸管", "吸不上来", "吸饮料", "吸住"],
    },
    "泡泡彩色": {
        "conditions": ["阳光", "灯光", "阴天", "加了甘油", "大泡泡", "油膜"],
        "phenomena": ["泡泡", "肥皂泡", "彩色", "彩虹色"],
    },
    "热水瓶保温": {
        "conditions": ["冬天", "夏天", "装冰水", "瓶塞", "倒了热水", "用很久"],
        "phenomena": ["热水瓶", "保温杯", "不凉", "保温"],
    },
    "煮鸡蛋": {
        "conditions": ["冷水煮", "开水煮", "火太大", "煮太久", "放了盐", "刚买回来"],
        "phenomena": ["鸡蛋", "煮硬", "蛋白凝固", "蛋黄"],
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
    variants = ae.gen_template_variants(theme, "", 14)
    variants = [v for v in variants if theme not in v]
    # 去重/过滤空
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
print("=== 批量自进化报告 ===")
for t, r in REPORT.items():
    print(f"  {t}: {r}")
