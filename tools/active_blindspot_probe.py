# -*- coding: utf-8 -*-
"""主动盲区探测（v1.22 · Ornith 自生成课程借鉴 → 知识飞轮主动化）

思路（对齐信息差理论）：Ornith 用「目标成功率 0.2」维持在能力边界训练；
白箱用「信息差 D_norm 维持在高位」探测盲区——图谱已有卡的边缘生成
边界问题，检索信息差大的 = 真盲区 = 最大学习价值区。

流程：
  1. 从图谱知识卡提取知识点名（种子）
  2. 模板生成边界探测问题（什么是X / X和Y区别 / 为什么X / X的条件）
  3. graph_retrieve 检索 → 计算 D_norm（top score 弱 = 信息差大）
  4. 盲区判定：D_norm 高 + top 卡不相关 → 候选盲区
  5. 输出盲区报告（人工审核后补卡，走 flywheel 审核闸门）

用法：
  python tools/active_blindspot_probe.py --top 30 --threshold 0.15
"""
import sys
import os
import json
import time
import argparse
import sqlite3
import random
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")

MAIN_DB = r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db"
BLIND_DB = MAIN_DB  # 盲区注册表在主库


def load_kp_names(db, limit=400):
    """从图谱提取知识点名（种子源）：有 name 的 knowledge 卡。

    v1.22 过滤：排除「XX知识点内容（按骨架填充）」这类合成卡名
    （卡名不是知识点，生成的探测问题无意义——「计算机组成原理/人工
    智能知识点内容的原理是什么」）。只保留干净的学科/知识点名。
    """
    conn = sqlite3.connect(db)
    names = []
    for (sa,) in conn.execute(
            "SELECT state_attributes FROM nodes WHERE layer='knowledge' "
            "AND state_attributes LIKE '%name%' LIMIT 5000"):
        try:
            d = json.loads(sa) if sa else {}
            n = d.get("name")
            if not n or len(n) < 2 or n.startswith("node_"):
                continue
            # 过滤合成卡名（按骨架填充/知识点内容/学科知识卡）
            if any(t in n for t in ("知识点内容", "骨架填充", "学科知识卡",
                                    "人话接口", "按骨架")):
                continue
            names.append(n)
        except Exception:
            pass
    conn.close()
    # 去重保序
    seen = set()
    out = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out[:limit]


def gen_probe_questions(names, seed=42):
    """模板生成边界探测问题（Ornith 课程生成器 → 白箱边界问题）。"""
    random.seed(seed)
    templates = [
        ("什么是{0}？", "定义"),
        ("{0}和{1}有什么区别？", "对比"),
        ("为什么{0}？", "原因"),
        ("{0}在什么条件下成立？", "条件"),
        ("{0}是怎么工作的？", "机制"),
        ("{0}有什么用途？", "用途"),
        ("{0}属于哪个领域？", "归属"),
        ("{0}的原理是什么？", "原理"),
    ]
    probes = []
    # 从种子两两配对生成（对比类最易暴露跨界盲区）
    for i in range(0, len(names) - 1, 2):
        a, b = names[i], names[i + 1]
        probes.append(("{}和{}有什么区别？".format(a, b), "对比", (a, b)))
    # 单知识点定义/机制类（只用单槽模板）
    single_templates = [t for t in templates if "{1}" not in t[0]]
    # v1.22：「原理/机制」只对学科级概念用（>=5字且非纯数学操作词）——
    # 否则「导数的原理是什么」爆炸成凸透镜错配（无意义问句）。
    _MATH_OPS = ("导数", "积分", "极限", "运算法则", "概念", "换元",
                 "分部", "二重", "定积分", "特征值", "特征向量", "公式",
                 "定理", "法则", "性质")
    for n in names:
        is_subject_level = (len(n) >= 5 and not any(m in n for m in _MATH_OPS))
        allowed = [t for t in single_templates
                   if t[1] not in ("原理", "机制") or is_subject_level]
        for tpl, kind in random.sample(allowed, min(3, len(allowed))):
            q = tpl.format(n)
            # 过滤无意义问句：「为什么控制论」对学科名不成立
            if kind == "原因" and len(n) <= 4:
                continue
            probes.append((q, kind, (n,)))
    return probes


def compute_dnorm(hits):
    """信息差 D_norm：top 命中质量的反向指标。

    D_norm = 1 - top_score_norm，其中 top_score_norm = score/(1+score)（soft 压缩）。
    高 D_norm = 检索弱 = 信息差大 = 可能盲区。
    """
    if not hits:
        return 1.0
    top = hits[0].get("score") or 0
    return 1.0 - top / (1.0 + top)


def probe(question, dex, st):
    """单问题探测：graph_retrieve → (hits, dnorm, top_name, top_direct)。"""
    try:
        hits = st.graph_retrieve(dex, question, limit=3)
    except Exception:
        return [], 1.0, None, None
    if not hits:
        return [], 1.0, None, None
    top = hits[0]
    return (hits, compute_dnorm(hits),
            top.get("name"), top.get("direct_answer") or "")


def _relevant(question, top_name, top_direct, parts):
    """相关性校验：top 卡与问题真相关才算命中（防错配充数）。

    相关 = top 卡名/直答含问题关键词，或 parts 中的知识点名出现。
    """
    q_text = question
    for p in parts:
        if p and len(p) >= 2 and p in q_text:
            # 知识点名出现在问题里 → 相关卡必须含它
            if p in (top_name or "") or p in (top_direct or ""):
                return True
            return False
    # 通用词：卡名/直答与问题关键词有 2 字以上共现
    import re as _re
    qchars = set(_re.sub(r"[^\u4e00-\u9fff]", "", q_text))
    top_text = (top_name or "") + (top_direct or "")
    topchars = set(_re.sub(r"[^\u4e00-\u9fff]", "", top_text))
    inter = qchars & topchars
    return len(inter) >= 2  # 2 字共现算相关（防「热力学」漏判）


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=30, help="输出盲区数")
    ap.add_argument("--threshold", type=float, default=0.55,
                    help="D_norm 阈值（> 阈值判盲区）")
    ap.add_argument("--seeds", type=int, default=200, help="种子知识点数")
    ap.add_argument("--db", default=MAIN_DB, help="图谱库")
    ap.add_argument("--only-new", action="store_true",
                    help="只输出未在盲区注册表的问题")
    args = ap.parse_args()

    import wisdom_book as wb
    import semantic_translate as st
    dex = wb.ConditionDex(db_path=args.db, fresh=False)

    names = load_kp_names(args.db, limit=args.seeds)
    print(f"种子知识点: {len(names)}")
    probes = gen_probe_questions(names)
    print(f"生成探测问题: {len(probes)}")

    # 已登记盲区（去重用）
    conn = sqlite3.connect(BLIND_DB)
    existing = set()
    try:
        for (desc,) in conn.execute("SELECT description FROM blindspots"):
            existing.add(desc[:30])
    except Exception:
        pass

    results = []
    t0 = time.time()
    for i, (q, kind, parts) in enumerate(probes, 1):
        hits, dnorm, top_name, top_direct = probe(q, dex, st)
        # v1.22 真盲区判定：信息差大（dnorm>阈值）AND top 卡不相关
        # （错配 = 真盲区；相关但分低 = 弱命中不算盲区）
        if dnorm > args.threshold:
            relevant = _relevant(q, top_name, top_direct, parts)
            if not relevant:
                results.append({
                    "question": q, "kind": kind, "parts": parts,
                    "dnorm": round(dnorm, 3), "top_name": top_name,
                    "top_direct": (top_direct or "")[:60],
                })
        if i % 200 == 0:
            print(f"  [{i}/{len(probes)}] 用时 {time.time()-t0:.0f}s "
                  f"盲区候选 {len(results)}", flush=True)

    # 排序：D_norm 最高 = 最盲
    results.sort(key=lambda x: -x["dnorm"])
    print(f"\n=== 盲区候选 {len(results)}（D_norm>{args.threshold}）===")
    shown = 0
    for r in results[: args.top]:
        shown += 1
        print(f"  [{r['dnorm']:.2f}] ({r['kind']}) {r['question'][:44]}")
        print(f"       top卡: {r['top_name']} | direct: {r['top_direct'][:44]}")
    print(f"\n显示 {shown}/{len(results)}")

    # 保存报告
    out = os.path.join(HERE, "..", "logs", "active_blindspot_report.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"generated": len(probes), "blindspots": results[:200],
                   "threshold": args.threshold,
                   "time": time.strftime("%Y-%m-%d %H:%M")},
                  f, ensure_ascii=False, indent=1)
    print(f"报告已存: {out}")
    dex.close()
    conn.close()


if __name__ == "__main__":
    main()
