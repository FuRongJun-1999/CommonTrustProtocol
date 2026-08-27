# -*- coding: utf-8 -*-
"""auto_blindspot_loop.py —— 条件空间自举补盲循环 v1（进化搜索协议化）

映射条件空间 7 操作：
  声明条件空间 = 输入主题 + 变体问法清单
  切换条件空间 = 变体问法（换词/改写观测同一知识）
  识别条件边界 = encode fp 命中测试（确定性选择器）
  变异          = 从未命中变体提取特征短语 → 触发词候选
  分离条件空间 = 冲突检测（候选不得撞其他簇触发词/泛词）
  组合条件空间 = 候选与既有触发词合并
  循环条件空间 = 重测 → 收敛（100% 或 max_rounds 或 无新候选）

用法：
  python auto_blindspot_loop.py --theme 彩虹 --variants variants.json [--apply] [--max-rounds 5]
"""
import argparse, json, os, sys, subprocess, tempfile

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")

import semantic_translate as _st

TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"

# ---------------------------------------------------------------- 选择器
def fp_hits(theme, variants):
    """识别条件边界：encode fp 是否命中主题（确定性）。返回 [(variant, hit)]"""
    out = []
    for v in variants:
        fp = _st.encode(v)
        out.append((v, theme in fp))
    return out

def get_cluster_triggers(theme):
    return list(_st.DOMAIN_SYNONYM_CLUSTERS.get(theme, [])) + \
           list(_st.SYNONYM_CLUSTERS.get(theme, []))

# ---------------------------------------------------------------- 变异
def extract_candidates(theme, misses, existing, all_other_triggers):
    """从未命中变体提取触发词候选（变异）：
    ① 滑动窗口 2-6 字 ② 清洗尾部虚词（的/了/？/是/为/么/能/会/下/后…）
    ③ 跨变体共现加权（出现于多个未命中变体优先——组合条件空间）
    ④ 冲突/泛词检查（分离条件空间）。返回 [(词, 覆盖变体数, 长度)]。"""
    # 尾部虚词清洗（可重复剥）+ 内部连接词去除（组合条件空间：彩色的桥→彩色桥）
    # 前缀指示/疑问虚词黑名单（分离条件空间：指示词不构成触发特征）
    PREFIX_NOISE = ("那道", "道彩", "为什", "什么", "怎么", "为什么", "天上", "天空",
                    "雨后", "喷泉", "下完", "谁在", "阳光", "时候", "为什么雨", "为什么会")
    TAIL_NOISE = "的了？?。，、是为什么么能会下后上过中里就都也在"
    # 功能字（实词度评分用：候选必须主体是实义字，功能字占比高=噪声片段）
    FUNC_CHARS = set("的了道能走下面去吗怎么为什过上下中里就都也在会来后挂有变出挂没看进到往")
    def denoise(w):
        # 只处理尾部虚词（在 clean 中）；不去内部「的」——候选必须保留原文
        # 形态（触发词匹配是原文子串：「彩色的桥」≠「彩色桥」）
        return w
    def clean(w):
        w = denoise(w)
        for p in PREFIX_NOISE:
            if w.startswith(p):
                w = w[len(p):]
        while w and w[-1] in TAIL_NOISE:
            w = w[:-1]
        return w
    def solidity(w):
        """实词度：非功能字占比（≥0.7 才视为干净实词触发词）。"""
        if not w:
            return 0.0
        return sum(1 for ch in w if ch not in FUNC_CHARS) / len(w)
    cand = {}
    for v in misses:
        vc = v.strip("？?。， ")
        seen = set()
        for L in range(6, 1, -1):  # 长词优先
            for i in range(0, len(vc) - L + 1):
                w = clean(vc[i:i + L])
                if len(w) < 2 or w in seen:
                    continue
                # 分离条件空间：裸 2 字泛词不自动应用（经验：彩色/电梯/犯困
                # 都曾因 2 字泛词抢答污染路由——v1 只自动应用 ≥3 字实词）
                if len(w) < 3:
                    continue
                # 实词度过滤：功能字占比过高 = 句子片段（不是触发词）
                if solidity(w) < 0.7:
                    continue
                if w in existing:
                    continue
                # 冲突：与其他簇触发词相等（分离条件空间）
                if any(w == t for lst in all_other_triggers.values() for t in lst):
                    continue
                seen.add(w)
                cand[w] = cand.get(w, set())
                cand[w].add(v)
    # 得分：覆盖变体数 × 实词度（跨变体共性优先，实词核心优先），长度次之
    scored = [(w, len(vs), len(w)) for w, vs in cand.items()]
    scored.sort(key=lambda x: (-x[1] * solidity(x[0]), -x[2]))
    return scored

# ---------------------------------------------------------------- 收敛报告
def report(theme, variants, hits, round_no):
    n = len(variants)
    ok = sum(1 for _, h in hits if h)
    print(f"  [round {round_no}] fp 命中: {ok}/{n} ({ok/n*100:.0f}%)")
    return ok / n

def apply_patch(theme, new_triggers):
    """分离+组合：把新触发词写入 DOMAIN_SYNONYM_CLUSTERS[theme]（保留原表）。"""
    src = open(TRANSLATE_PY, encoding="utf-8").read()
    # 定位主题簇定义行（"theme": [...]）
    import re
    m = re.search(r'"%s":\s*\[([^\]]*)\]' % theme, src)
    if not m:
        print(f"  ERROR: 找不到主题簇 {theme}")
        return False
    existing = [t.strip().strip('"').strip("'") for t in m.group(1).split(",") if t.strip()]
    merged = existing + [t for t in new_triggers if t not in existing]
    # 结尾不带逗号——原文本 m.end() 后保留原尾逗号，避免 `],,`
    new_block = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in merged))
    src = src[:m.start()] + new_block + src[m.end():]
    # 保留其余文本（m 只替换该行内列表）
    open(TRANSLATE_PY, "w", encoding="utf-8").write(src)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", required=True)
    ap.add_argument("--variants", required=True)
    ap.add_argument("--max-rounds", type=int, default=5)
    ap.add_argument("--apply", action="store_true", help="自动 patch 触发词表（默认仅报告）")
    args = ap.parse_args()

    variants = [v["q"] for v in json.load(open(args.variants, encoding="utf-8"))["variants"]]
    all_other_triggers = {k: v for k, v in {**_st.DOMAIN_SYNONYM_CLUSTERS, **_st.SYNONYM_CLUSTERS}.items() if k != args.theme}

    print(f"=== 条件空间自举补盲: {args.theme}（{len(variants)} 变体）===")
    added = []
    for rnd in range(1, args.max_rounds + 1):
        existing = get_cluster_triggers(args.theme)
        hits = fp_hits(args.theme, variants)
        rate = report(args.theme, variants, hits, rnd)
        if rate >= 1.0:
            print(f"  收敛: {args.theme} 全部命中（新增触发词 {len(added)} 个: {added}）")
            break
        misses = [v for v, h in hits if not h]
        cands = extract_candidates(args.theme, misses, existing, all_other_triggers)
        if not cands:
            print(f"  无新候选（剩余 {len(misses)} 个未命中需人工：{misses}）")
            break
        top = [w for w, _, _ in cands[:5]]
        print(f"  未命中 {len(misses)}: {[v[:18] for v in misses]}")
        print(f"  变异候选(前5): {top}")
        if args.apply:
            if apply_patch(args.theme, top):
                added.extend(top)
                # 重新加载模块
                import importlib
                importlib.reload(_st)
                all_other_triggers = {k: v for k, v in {**_st.DOMAIN_SYNONYM_CLUSTERS, **_st.SYNONYM_CLUSTERS}.items() if k != args.theme}
                print(f"  已 patch: +{top}")
            else:
                print("  patch 失败，停止")
                break
        else:
            print("  (未 --apply，仅报告；可加 --apply 自动写入)")
            break
    else:
        print(f"  达 max-rounds={args.max_rounds}，未完全收敛")

if __name__ == "__main__":
    main()
