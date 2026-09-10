# -*- coding: utf-8 -*-
"""md_eval.py · MD 目录知识检索评测（对比 sqlite 基线）

读 aeis/knowledge/*.md（246 个学科综述）构建内存索引，
对 question_bank.json 全量题目做检索测试，
输出 recall 统计并与 qbank_eval.py（sqlite 版）对比。

用法：python tools/md_eval.py [--min-score 3]
"""
import sys, os, json, re, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
KNOWLEDGE_DIR = os.path.join(ROOT, "aeis", "knowledge")
BANK = os.path.join(HERE, "question_bank.json")

# ─── 停用词（检索时忽略） ───
STOP = {"什么", "怎么", "为什么", "哪些", "如何", "哪里", "是不是",
        "的是", "的", "了", "在", "是", "和", "与", "或", "及", "有",
        "区别", "分别", "分别是什么", "作用", "意义", "影响"}


def extract_terms(question):
    """从问题中提取检索词：分词 + 过滤停用词 + 二元组"""
    # 分句/分词
    words = re.split(r'[？?，,。；;：:、\s「」（）()+\-*/]', question)
    words = [w.strip() for w in words if len(w.strip()) >= 2]
    # 过滤纯停用词
    terms = set()
    for w in words:
        if w not in STOP:
            terms.add(w)
    # 补充：从去标点全文中提取二元组
    clean = re.sub(r'[？?，,。；;：:、\s「」（）()+\-*/=<>]', '', question)
    for i in range(len(clean) - 1):
        bg = clean[i:i+2]
        if bg not in STOP:
            terms.add(bg)
    return terms


def load_knowledge():
    """加载 aeis/knowledge/ 所有 .md 文件到内存索引。

    返回 list of {name, content, file, bigrams}
    """
    kps = []
    for fn in sorted(os.listdir(KNOWLEDGE_DIR)):
        if not fn.endswith('.md'):
            continue
        filepath = os.path.join(KNOWLEDGE_DIR, fn)
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        # 按 ### 分节提取知识点
        sections = re.split(r'^### ', content, flags=re.MULTILINE)
        for section in sections[1:]:  # 跳过头部
            lines = section.split('\n', 1)
            name = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ''
            # 合并 name + body 做检索（名字本身是重要信号）
            searchable = name + ' ' + body
            clean = re.sub(r'[？?，,。；;：:、\s「」（）()+\-*/=<>#*\[\]]', '', searchable)
            bg = set()
            for i in range(len(clean) - 1):
                bg.add(clean[i:i+2])
            kps.append({
                'name': name,
                'content': body,
                'file': fn,
                'bigrams': bg,
                'terms': set(w for w in re.split(r'[\s，,。；]', searchable) if len(w) >= 2),
            })
    return kps


def search(query_terms, knowledge, min_overlap=0.15):
    """检索：问题词与知识点的重合度评分。

    评分策略（多层匹配）：
    1. 名称精确命中（问题含知识点名或反之）→ 高分
    2. 二元组重合率 → 中分
    3. 词汇命中率 → 补充分
    """
    q_text = ''.join(query_terms)  # 合并所有词
    q_clean = re.sub(r'[？?，,。；;：:、\s（）()+\-*/=<>]', '', q_text)
    q_bg = set()
    for t in query_terms:
        c = re.sub(r'[？?，,。；;：:、\s（）()+\-*/=<>]', '', t)
        for i in range(len(c) - 1):
            q_bg.add(c[i:i+2])

    scored = []
    for kp in knowledge:
        score = 0.0
        # 1) 名称精确匹配（最强信号）
        kp_name = kp['name']
        if kp_name in q_text or q_text in kp_name:
            score = max(score, 1.0)
        elif any(kp_name in t or t in kp_name for t in query_terms if len(t) >= 3):
            score = max(score, 0.8)
        # 2) 名称词汇命中
        name_hits = sum(1 for t in query_terms if len(t) >= 2 and t in kp_name)
        if name_hits > 0:
            score = max(score, 0.3 + name_hits * 0.2)
        # 3) 内容二元组重合率
        if q_bg and kp['bigrams']:
            overlap = len(q_bg & kp['bigrams']) / len(q_bg) if q_bg else 0
            score = max(score, overlap * 2)  # 二元组重合 50% → 1.0 分
        # 4) 词汇命中数
        term_hits = sum(1 for t in query_terms if len(t) >= 2 and
                        (t in kp['content'] or t in kp_name))
        if term_hits >= 2:
            score = max(score, 0.3 + term_hits * 0.1)
        if score >= min_overlap:
            scored.append((kp, min(1.0, score)))
    return scored


def main(min_score=3):
    print("=== 加载知识库 ===")
    t0 = time.time()
    knowledge = load_knowledge()
    t1 = time.time()
    print(f"  加载 {len(knowledge)} 个知识点 ({t1-t0:.2f}s)")

    print("=== 加载题库 ===")
    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    print(f"  {len(qs)} 题")

    # 同时跑 sqlite 基线
    print("\n=== 运行 sqlite 基线 ===")
    sys.path.insert(0, os.path.join(ROOT, "aeis"))
    sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))
    from wisdom_book import ConditionDex
    from semantic_translate import card_route
    dex = ConditionDex(db_path=os.path.join(ROOT, "aeis", "wisdom",
                                            "wisdom-book-cloud.db"))

    print("\n=== 开始评测 ===")
    md_hits = 0
    sql_hits = 0
    both_hits = 0
    neither = 0
    md_only = []
    sql_only = []
    by_domain = {}
    misses_md = []
    t0 = time.time()

    for q in qs:
        question = q["question"]
        dom = q.get("domain", "未分类")

        # MD 检索
        terms = extract_terms(question)
        md_results = search(terms, knowledge, min_overlap=0.15)
        md_top = max((s for _, s in md_results), default=0)
        md_hit = md_top >= min_score / 3.0  # 归一化到同量级

        # sqlite 检索
        r = card_route(dex, question)
        sql_top = max((c.get("score") or 0) for c in r) if r else 0
        sql_hit = sql_top >= min_score

        if md_hit:
            md_hits += 1
        if sql_hit:
            sql_hits += 1
        if md_hit and sql_hit:
            both_hits += 1
        elif md_hit and not sql_hit:
            md_only.append((q["id"], question[:30], md_top))
        elif sql_hit and not md_hit:
            sql_only.append((q["id"], question[:30], sql_top))
        else:
            neither += 1
            misses_md.append((q["id"], question[:30], md_top))

        d = by_domain.setdefault(dom, {"n": 0, "md": 0, "sql": 0})
        d["n"] += 1
        d["md"] += 1 if md_hit else 0
        d["sql"] += 1 if sql_hit else 0

    t1 = time.time()

    # ═══ 报告 ═══
    total = len(qs)
    print(f"\n{'='*60}")
    print(f"题库 v{bank['version']} | {total} 题 | 评测耗时 {t1-t0:.1f}s")
    print(f"{'='*60}")
    print(f"sqlite 基线命中: {sql_hits}/{total} = {sql_hits/total*100:.1f}%")
    print(f"MD 目录命中:     {md_hits}/{total} = {md_hits/total*100:.1f}%")
    print(f"两者都命中:       {both_hits}")
    print(f"仅 MD 命中:       {len(md_only)}")
    print(f"仅 sqlite 命中:   {len(sql_only)}")
    print(f"两者都未命中:     {neither}")
    print(f"{'='*60}")

    # MD 独有的命中说明 MD 有额外信息（好事）
    if md_only:
        print(f"\n--- 仅 MD 命中（MD 额外覆盖）---")
        for qid, qtext, score in md_only[:10]:
            print(f"  {qid} {qtext} (md_score={score:.2f})")
        if len(md_only) > 10:
            print(f"  ...（还有 {len(md_only)-10} 个）")

    # sqlite 独有的命中说明 MD 缺信息（需关注）
    if sql_only:
        print(f"\n--- 仅 sqlite 命中（MD 需补充）---")
        for qid, qtext, score in sql_only[:20]:
            print(f"  {qid} {qtext} (sql_score={score})")
        if len(sql_only) > 20:
            print(f"  ...（还有 {len(sql_only)-20} 个）")

    # 分域对比
    print(f"\n--- 分域 MD vs sqlite ---")
    for dom, d in sorted(by_domain.items(), key=lambda x: -x[1]['n']):
        md_pct = d['md'] / d['n'] * 100
        sql_pct = d['sql'] / d['n'] * 100
        gap = md_pct - sql_pct
        mark = " ←" if abs(gap) > 5 else ""
        print(f"  {dom}: MD {d['md']}/{d['n']} ({md_pct:.0f}%) "
              f"sqlite {d['sql']}/{d['n']} ({sql_pct:.0f}%) "
              f"差 {gap:+.0f}%{mark}")

    return 0 if len(sql_only) == 0 else 1


if __name__ == "__main__":
    ms = 3
    if "--min-score" in sys.argv:
        ms = int(sys.argv[sys.argv.index("--min-score") + 1])
    sys.exit(main(ms))
