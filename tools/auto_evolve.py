# -*- coding: utf-8 -*-
"""auto_evolve.py —— 白箱自进化循环 v1（条件延伸迁移）

让已有知识在不同条件下的延伸都能迁移：
  变异器: 模板变异（条件词×现象词，确定性白箱）| LLM 变异（生成式，可选）
  选择器: encode fp 命中主题（确定性，可复现）
  补盲:   未命中变体 → 触发词候选提取（实词度+冲突过滤）→ 自动 patch → 重测
  收敛:   全部命中 或 无新候选（剩余人工）

用法:
  python auto_evolve.py --theme 彩虹 --knowledge "阳光穿过水滴折射反射色散,背对太阳,高度角<42度" \
    [--count 15] [--apply] [--mode template|llm]
"""
import argparse, json, os, re, sys, urllib.request

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
import semantic_translate as _st

TRANSLATE_PY = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
OLLAMA = "http://127.0.0.1:11434/api/generate"
MODEL = "ornith-1.5-9b:latest"

# ================================================================ 变异器
# 条件/环境词（通用——主题无关，同一知识在不同条件出现）
CONDITIONS = ["喷泉", "露珠", "瀑布", "水雾", "雾天", "油膜", "冰晶", "霓虹",
              "月光", "灯光", "水花", "雨幕", "洒水车", "喷水壶", "海边水汽",
              "温泉", "玻璃", "三棱镜", "泡沫", "湖面"]
# 现象词（主题相关——从该簇触发词/知识提炼，禁含主题字）
PHENOMENA = ["七色的光带", "彩色的光圈", "彩色的圆弧", "七彩的光", "彩色的桥",
             "彩色的弧线", "彩色的光带", "光弧", "彩带", "七色光", "彩色光环"]
TEMPLATES = [
    "为什么{cond}边会有{phen}？",
    "{cond}里的{phen}是什么原理？",
    "为什么{cond}会出现{phen}？",
    "{cond}上的{phen}是怎么回事？",
    "为什么{cond}会有{phen}？",
]

def gen_template_variants(theme, knowledge, count=15):
    """变异（模板）：条件词×现象词确定性组合。"""
    out = []
    for c in CONDITIONS:
        if theme in c:
            continue
        for p in PHENOMENA:
            if theme in p:
                continue
            for t in TEMPLATES:
                q = t.format(cond=c, phen=p)
                if q not in out:
                    out.append(q)
                    break
        if len(out) >= count:
            break
    return out[:count]

def llm_generate(prompt, max_tokens=800, temperature=0.7):
    body = json.dumps({
        "model": MODEL, "prompt": prompt, "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }).encode("utf-8")
    req = urllib.request.Request(OLLAMA, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read().decode("utf-8"))
        return data.get("response", "")
    except Exception as e:
        print(f"  [LLM] 不可用: {e}")
        return ""

def gen_llm_variants(theme, knowledge, count=15):
    """变异（LLM）：生成式条件延伸问法（v2 可选）。"""
    prompt = (
        f"你是一个知识变异器。给定知识主题「{theme}」及其原理：{knowledge}\n"
        f"请生成 {count} 个「不同条件下」的延伸问法——同样的原理出现在不同环境/介质/场景\n"
        f"（如水滴、露珠、喷泉、瀑布、油膜、冰晶、水雾、霓虹、月光等变体），\n"
        f"以普通人的困惑口吻提问（如「为什么XX会XX？」）。\n"
        f"【硬性要求】所有问法【禁止出现】「{theme}」二字——用现象描述替代。\n"
        f"只输出 JSON 数组字符串，如 [\"为什么喷泉边会有彩色？\",\"...\"]，不要其他文字。"
    )
    text = llm_generate(prompt)
    if not text:
        return []
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        print("  [LLM] 未解析到 JSON 数组，原文:", text[:120])
        return []
    try:
        items = json.loads(m.group(0))
        out = []
        for x in items:
            s = str(x).strip()
            if s and s not in ("...", "…", "……") and len(s) >= 6 and theme not in s:
                out.append(s)
        return out
    except Exception as e:
        print("  [LLM] JSON 解析失败:", e, "|", text[:100])
        return []

def gen_variants(theme, knowledge, count, mode):
    if mode == "llm":
        return gen_llm_variants(theme, knowledge, count)
    return gen_template_variants(theme, knowledge, count)

# ================================================================ 选择器
def fp_test(theme, variants):
    return [(v, theme in _st.encode(v)) for v in variants]

# ================================================================ 补盲（提取+patch）
PREFIX_NOISE = ("那道", "道彩", "为什", "什么", "怎么", "为什么", "天上", "天空",
                "雨后", "喷泉", "下完", "谁在", "阳光", "时候", "为什么雨", "为什么会")
TAIL_NOISE = "的了？?。，、是为什么么能会下后上过中里就都也在"
FUNC_CHARS = set("的了道能走下面去吗怎么为什过上下中里就都也在会来后挂有变出没看进到往")

def clean(w):
    for p in PREFIX_NOISE:
        if w.startswith(p):
            w = w[len(p):]
    while w and w[-1] in TAIL_NOISE:
        w = w[:-1]
    return w

def solidity(w):
    if not w:
        return 0.0
    return sum(1 for ch in w if ch not in FUNC_CHARS) / len(w)

def extract_candidates(theme, misses, existing, all_other):
    cand = {}
    for v in misses:
        vc = v.strip("？?。， ")
        seen = set()
        for L in range(6, 1, -1):
            for i in range(0, len(vc) - L + 1):
                w = clean(vc[i:i + L])
                if len(w) < 3 or w in seen or w in existing:
                    continue
                if solidity(w) < 0.7:
                    continue
                if any(w == t for lst in all_other.values() for t in lst):
                    continue
                seen.add(w)
                cand[w] = cand.get(w, set())
                cand[w].add(v)
    scored = [(w, len(vs), len(w)) for w, vs in cand.items()]
    scored.sort(key=lambda x: (-x[1] * solidity(x[0]), -x[2]))
    return scored

def apply_patch(theme, new_triggers):
    src = open(TRANSLATE_PY, encoding="utf-8").read()
    m = re.search(r'"%s":\s*\[([^\]]*)\]' % theme, src)
    if not m:
        print(f"  ERROR: 找不到主题簇 {theme}")
        return False
    existing = [t.strip().strip('"').strip("'") for t in m.group(1).split(",") if t.strip()]
    merged = existing + [t for t in new_triggers if t not in existing]
    new_block = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in merged))
    src = src[:m.start()] + new_block + src[m.end():]
    open(TRANSLATE_PY, "w", encoding="utf-8").write(src)
    return True

# ================================================================ 主循环
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", required=True)
    ap.add_argument("--knowledge", default="")
    ap.add_argument("--count", type=int, default=15)
    ap.add_argument("--max-rounds", type=int, default=4)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--mode", choices=["template", "llm"], default="template")
    ap.add_argument("--phenomena", default=None, help="主题现象词 JSON 数组（默认彩虹词表）")
    ap.add_argument("--conditions", default=None, help="条件词 JSON 数组（默认通用表）")
    args = ap.parse_args()

    global CONDITIONS, PHENOMENA, TEMPLATES
    if args.conditions:
        CONDITIONS = json.loads(args.conditions)
    if args.phenomena:
        PHENOMENA = json.loads(args.phenomena)

    all_other = {k: v for k, v in {**_st.DOMAIN_SYNONYM_CLUSTERS, **_st.SYNONYM_CLUSTERS}.items() if k != args.theme}

    print(f"=== 白箱自进化: {args.theme}（条件延伸迁移, mode={args.mode}）===")
    print(f"[变异] 生成 {args.count} 个条件延伸问法…")
    variants = gen_variants(args.theme, args.knowledge, args.count, args.mode)
    variants = [v for v in variants if args.theme not in v]
    if not variants:
        print("  变异器无产出，中止")
        return
    print(f"  变体({len(variants)}):")
    for v in variants:
        print(f"    - {v}")

    added = []
    for rnd in range(1, args.max_rounds + 1):
        hits = fp_test(args.theme, variants)
        ok = sum(1 for _, h in hits if h)
        print(f"  [round {rnd}] fp 命中: {ok}/{len(variants)} ({ok/len(variants)*100:.0f}%)")
        if ok == len(variants):
            print(f"  收敛: {args.theme} 条件延伸全部迁移（新增触发词 {len(added)}: {added}）")
            return
        misses = [v for v, h in hits if not h]
        existing = list(_st.DOMAIN_SYNONYM_CLUSTERS.get(args.theme, []))
        cands = extract_candidates(args.theme, misses, existing, all_other)
        if not cands:
            print(f"  无新候选（剩余 {len(misses)} 个需人工/新直答: {misses}）")
            return
        top = [w for w, _, _ in cands[:5]]
        print(f"  未命中 {len(misses)}: {[v[:24] for v in misses]}")
        print(f"  变异候选(前5): {top}")
        if args.apply and apply_patch(args.theme, top):
            added.extend(top)
            print(f"  已 patch: +{top}")
            import importlib
            importlib.reload(_st)
            all_other = {k: v for k, v in {**_st.DOMAIN_SYNONYM_CLUSTERS, **_st.SYNONYM_CLUSTERS}.items() if k != args.theme}
        else:
            print("  (未 --apply 或 patch 失败)")
            return
    print(f"  达 max-rounds={args.max_rounds}")

if __name__ == "__main__":
    main()
