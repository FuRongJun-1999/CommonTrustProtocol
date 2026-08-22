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
    """变异（LLM 生成式）：生成自然的中文条件延伸问法（矛盾情境域用）。
    输出解析：按行取（每行一问），过滤英文/编号/占位符。"""
    prompt = (
        f"你是一个中文知识变异器。主题「{theme}」，原理：{knowledge}\n"
        f"请生成 {count} 个【自然的中文问句】，表达「不同情境下关于这个主题的普通人困惑」\n"
        f"（例如不同场景、人群、时机、场合下的提问）。\n"
        f"要求：\n"
        f"1. 全部是日常口语问句，自然流畅（像普通人真的会问）\n"
        f"2. 每题不超过 25 个字\n"
        f"3. 不要出现「{theme}」这几个字当主题词（可以用现象/情境描述）\n"
        f"4. 禁止英文、禁止编号、禁止引号、禁止解释\n"
        f"输出格式：每行恰好一个问题，共 {count} 行，不要任何其他文字。"
    )
    text = llm_generate(prompt, max_tokens=600, temperature=0.9)
    if not text:
        return []
    out = []
    for line in text.splitlines():
        s = line.strip()
        s = s.lstrip("0123456789.、-· ")
        s = s.strip('"\'“”「」')
        if not s or len(s) < 6 or len(s) > 28:
            continue
        if any(ord(ch) > 127 for ch in s) is False:  # 纯 ASCII（英文）跳过
            continue
        if theme in s:
            continue
        if any(w in s for w in ("...", "…", "……")):
            continue
        if s not in out:
            out.append(s)
    return out[:count]

def gen_variants(theme, knowledge, count, mode):
    if mode == "llm":
        return gen_llm_variants(theme, knowledge, count)
    return gen_template_variants(theme, knowledge, count)

# ================================================================ 选择器
def fp_test(theme, variants):
    return [(v, theme in _st.encode(v)) for v in variants]

# ================================================================ 补盲（提取+patch）
PREFIX_NOISE = ("那道", "道彩", "为什", "什么", "怎么", "为什么", "天上", "天空",
                "雨后", "喷泉", "下完", "谁在", "阳光", "时候", "为什么雨", "为什么会",
                "候", "时", "的时候")
TAIL_NOISE = "的了？?。，、是为什么么能会下后上过中里就都也在"
FUNC_CHARS = set("的了道能走下面去吗怎么为什过上下中里就都也在会来后挂有变出没看进到往候太时大")

def clean(w):
    # 去模板噪声「的时候」（条件延伸模板产物，非触发特征）
    w = w.replace("的时候", "")
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

# 2 字候选黑名单（曾污染路由的裸泛词，经验：彩色/电梯/犯困/激光）
BLACKLIST_2CHAR = {"彩色", "电梯", "犯困", "激光", "天气", "颜色", "温度", "时间", "时候",
                   "我家", "一层", "那个", "这个", "什么", "怎么", "为什么", "一个",
                   "上面", "下面", "里面", "外面", "旁边", "时候", "东西"}
# 代词/量词/功能字（2 字候选若全由这些构成则丢弃——LLM 自然问法的口语碎片）
FRAGMENT_CHARS = set("我你他她它们这那哪个些层块片张条根只个点下上里外旁前后左右")
PUNCT = set("，。、！？；：,.!?;:（）()「」『』\"'·…—")


def extract_candidates(theme, misses, existing, all_other):
    cand = {}
    for v in misses:
        vc = v.strip("？?。， ")
        seen = set()
        for L in range(6, 1, -1):
            for i in range(0, len(vc) - L + 1):
                w = clean(vc[i:i + L])
                if len(w) < 2 or w in seen or w in existing:
                    continue
                # 分离条件空间：2 字裸泛词黑名单；≥3 字要求实词度
                if len(w) == 2 and w in BLACKLIST_2CHAR:
                    continue
                if len(w) == 2 and all(ch in FRAGMENT_CHARS for ch in w):
                    continue
                if any(ch in PUNCT for ch in w):
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
