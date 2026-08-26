# -*- coding: utf-8 -*-
"""eval_function.py —— 白箱功能评估工具（F-SPEC v1）

参照 WB-SPEC 代码评估工具（codegraph_eval.py）的严谨度，用 F-SPEC v1 八维
标尺全量评审白箱回答功能。确定性裁决（零 LLM）——与生产共用 verify_answer。

用法：
  python eval_function.py                    # 默认 dialogue_1000 全量
  python eval_function.py --limit 100        # 前 100 题
  python eval_function.py --out reports/F-EVAL-xxx.json
"""
import sys, os, json, re, time, argparse
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")

# F-SPEC v1 维度权重
DIMENSIONS = {
    "F1": 0.20, "F2": 0.20, "F3": 0.15, "F4": 0.10,
    "F5": 0.10, "F6": 0.10, "F7": 0.05, "F8": 0.10,
}

# 内部格式特征（与 verify_answer 同源）
CARD_MARKERS = [
    (r"是『[^』]{1,12}』vs『[^』]{1,12}』的矛盾[——\-]", "矛盾句式"),
    (r"的真相：", "真相标记"),
]
# 闲聊触发词（与 chat_engine CHITCHAT 同源，抽核心）
CHITCHAT_WORDS = ["你好", "您好", "嗨", "哈喽", "hello", "谢谢", "再见", "拜拜",
                  "晚安", "天气", "在干嘛", "干嘛", "最近怎么样", "过得怎么样",
                  "吃饭了吗", "吃了没", "我回来了", "下班了", "到家了",
                  "想散步", "散步", "看电影", "做饭", "买", "累", "难过",
                  "开心", "高兴", "emo", "睡", "早安", "晚安"]
# 知识疑问句触发词
KNOWLEDGE_Q = ["为什么", "怎么", "是什么", "什么是", "多少", "怎么理解",
               "是什么意思", "什么原理", "怎么办", "区别", "区别是什么",
               "有哪些", "哪个", "为什么能", "为什么不能", "什么是"]
# 诚实边界词
HONEST_WORDS = ["命运", "寿命", "世界末日", "未来", "读心", "心里想什么",
                "预测股市", "会不会中奖", "死亡", "灵魂"]
# 任务动词
TASK_WORDS = ["写", "生成", "创建", "转换", "输出", "列出", "翻译", "总结",
              "解释一下", "帮我", "格式化", "整理"]


def detect_card_format(text):
    """内部格式检测（F3）"""
    if not text:
        return "空回答"
    for pat, name in CARD_MARKERS:
        if re.search(pat, text):
            return name
    parens = text.count("（")
    if parens >= 6 and parens / max(1, len(text)) > 0.08:
        return f"括号密度过高"
    return None


def is_knowledge_question(q):
    return any(w in q for w in KNOWLEDGE_Q)


def is_chitchat(q):
    return any(w in q for w in CHITCHAT_WORDS) and not is_knowledge_question(q)


def is_honest_question(q):
    return any(w in q for w in HONEST_WORDS)


def eval_question(q, cat, keys, reply, route, hits, anchor_present):
    """单题八维裁决。返回 (维度得分 dict, 失败列表)"""
    scores = {}
    fails = []

    # F1 条件路由图合规：knowledge 类必须来自条件路由图（有 hits 或诚实）
    f1 = True
    if is_knowledge_question(q):
        # 回答带卡导航（graph_retrieve 特征）或诚实声明 → 合规
        if "可以看「" in reply or "没有把握" in reply or "不编" in reply:
            f1 = True
        else:
            f1 = False
            fails.append("F1 未走条件路由图（无卡导航/无诚实声明）")
    scores["F1"] = f1

    # F2 路由正确性：条件分析 → 子功能切换
    f2 = True
    expected = "knowledge" if is_knowledge_question(q) else (
        "chitchat" if is_chitchat(q) else "honest" if is_honest_question(q) else "default")
    # 实际路由（从回答特征推断）
    if "可以看「" in reply:
        actual = "knowledge"
    elif "你好呀" in reply or "欢迎回来" in reply or "～" in reply and len(reply) < 60:
        actual = "chitchat"
    elif "没有把握" in reply or "不编" in reply or "不能预测" in reply:
        actual = "honest"
    else:
        actual = "default"
    if expected == "knowledge" and actual != "knowledge":
        f2 = False
        fails.append(f"F2 路由错误：期望 knowledge 实际 {actual}")
    elif expected == "chitchat" and actual == "knowledge":
        f2 = False
        fails.append(f"F2 路由错误：闲聊被知识检索带偏（期望 chitchat 实际 knowledge）")
    scores["F2"] = f2

    # F3 自然语言编译
    f3 = detect_card_format(reply) is None and len(reply) <= 400
    if not f3:
        card = detect_card_format(reply)
        fails.append(f"F3 内部格式：{card or '超长'}")
    scores["F3"] = f3

    # F4 回答验证（出口必过 verify_answer——由生产保证，这里复核 L1/L3）
    f4 = (detect_card_format(reply) is None) and ("..." not in reply or reply.count("...") <= 2)
    if not f4:
        fails.append("F4 未过验证（格式或截断）")
    scores["F4"] = f4

    # F5 诚实边界：无把握时诚实声明（不是硬答）
    f5 = True
    if keys and not any(k and k in reply for k in keys):
        # keys 未命中——若是知识疑问句且无诚实声明 → 可能硬答错
        if is_knowledge_question(q) and "没有把握" not in reply:
            f5 = False  # 硬答但答错（接近编造）
            fails.append(f"F5 无把握仍硬答（keys 未命中且无诚实声明）")
    scores["F5"] = f5

    # F6 知识准确：keys 命中（同义词/数值等价放宽）
    f6 = True
    if keys:
        hit = False
        for k in keys:
            if not k:
                continue
            if k in reply:
                hit = True
                break
            # 数值等价：100度 vs 100°C / 100 摄氏度
            if re.fullmatch(r"\d+度", k):
                num = k[:-1]
                if f"{num}°C" in reply or f"{num} 度" in reply or f"{num}度" in reply:
                    hit = True
                    break
        if not hit:
            f6 = False
            fails.append(f"F6 知识未命中 keys={keys}")
    scores["F6"] = f6

    # F7 可追溯：knowledge 回答带卡导航 + 条件空间
    f7 = True
    if "可以看「" in reply:
        if "（这条知识属于" not in reply and "在" not in reply:
            f7 = False
            fails.append("F7 缺条件空间")
    else:
        f7 = False  # knowledge 类必须有卡导航
        fails.append("F7 缺卡导航")
    scores["F7"] = f7

    # F8 防退化：锚点层含规范（每次初始化强制）+ 无内部格式泄漏
    f8 = anchor_present and detect_card_format(reply) is None
    if not f8:
        fails.append("F8 防退化失败（锚点缺失或格式泄漏）")
    scores["F8"] = f8

    return scores, fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="")
    ap.add_argument("--db", default=r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db")
    args = ap.parse_args()

    # 载入测试集
    ds_path = r"D:\Program Files\2_ai\CommonTrustProtocol\tools\dialogue_1000.json"
    with open(ds_path, encoding="utf-8") as f:
        dataset = json.load(f)
    if args.limit:
        dataset = dataset[:args.limit]

    # 载入引擎（用真实灵枢库）
    from aeis.core import SpacetimeMemoryEngine, MemoryLayer
    dex = SpacetimeMemoryEngine(db_path=args.db)
    import chat_engine as ce

    # 锚点存在性（F8）
    try:
        anchors = dex.store.query_nodes(layer=MemoryLayer.ANCHOR, limit=50)
        anchor_texts = " ".join((n.content or "") for n in (anchors or []))
        anchor_present = ("条件路由图" in anchor_texts and "自然语言编译" in anchor_texts)
    except Exception:
        anchor_present = False

    results = []
    dim_totals = {d: {"pass": 0, "total": 0} for d in DIMENSIONS}
    routing_errors = []
    cat_stats = {}

    for item in dataset:
        q, cat, keys = item.get("q", ""), item.get("cat", "?"), item.get("keys", [])
        try:
            r = ce.chat(dex, q, session_id="f-eval")
            reply = r.get("reply", "")
            route = r.get("route")
            hits = r.get("hits") or []
        except Exception as e:
            reply = f"(异常: {e})"
            route = "error"
            hits = []
        scores, fails = eval_question(q, cat, keys, reply, route, hits, anchor_present)

        # 汇总维度
        for d in DIMENSIONS:
            dim_totals[d]["total"] += 1
            if scores.get(d):
                dim_totals[d]["pass"] += 1
        # 路由错误记录
        if not scores["F2"]:
            routing_errors.append({"id": item.get("id"), "q": q,
                                   "reason": next((f for f in fails if "F2" in f), "路由错误")})
        # 类别统计
        cs = cat_stats.setdefault(cat, {"total": 0, "pass": 0})
        cs["total"] += 1
        if scores["F6"] and scores["F1"]:
            cs["pass"] += 1

        results.append({"id": item.get("id"), "cat": cat, "q": q, "keys": keys,
                        "reply": reply[:200], "scores": scores,
                        "failed_dimensions": [f.split()[0] for f in fails]})

    dex.close()

    # 维度得分
    dim_scores = {}
    for d, w in DIMENSIONS.items():
        t = dim_totals[d]
        dim_scores[d] = {"score": round(t["pass"] / max(1, t["total"]), 4), "weight": w,
                         "pass": t["pass"], "total": t["total"]}

    overall = sum(v["score"] * v["weight"] for v in dim_scores.values())
    total_q = len(results)
    routing_compliant = total_q - len(routing_errors)

    report = {
        "eval_id": f"F-EVAL-{time.strftime('%Y%m%d-%H%M%S')}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "spec_version": "F-SPEC-v1",
        "dataset": os.path.basename(ds_path),
        "summary": {
            "overall_score": round(overall, 4),
            "total_questions": total_q,
            "routing_compliant": routing_compliant,
            "routing_errors": len(routing_errors),
            "anchor_present": anchor_present,
        },
        "category_scores": cat_stats,
        "dimension_scores": dim_scores,
        "routing_error_details": routing_errors[:50],
        "failed_questions": [r for r in results if r["failed_dimensions"]][:100],
    }

    # 输出
    out = args.out or f"reports/F-EVAL-{time.strftime('%Y%m%d-%H%M%S')}.json"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    print(f"=== F-SPEC v1 功能评估 ===")
    print(f"样本: {total_q} 题 | 锚点: {'✓' if anchor_present else '✗'}")
    print(f"路由合规: {routing_compliant}/{total_q} | 路由错误: {len(routing_errors)}")
    print(f"综合分: {round(overall, 4)}")
    print(f"维度: " + " ".join(f"{d}={v['score']:.3f}" for d, v in dim_scores.items()))
    print(f"类别: " + " ".join(f"{k}={v['pass']}/{v['total']}" for k, v in cat_stats.items()))
    print(f"报告: {out}")


if __name__ == "__main__":
    main()
