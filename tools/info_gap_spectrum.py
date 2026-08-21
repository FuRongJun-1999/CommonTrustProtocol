# -*- coding: utf-8 -*-
"""信息差频谱化（v1.25 · 2026-08-21 · 知识考古复盘工程化 #1）

背景（复盘簇1）：信息差不是标量而是频谱——D(ω)=|F_target-F_current|²。
低频=结构性偏差（世界观/信任根基）、中频=知识偏差（飞轮周期）、
高频=情境偏差（临时误解）。

实现：
  1. 图谱分层频段模型：锚点层=DC、结构层=低频、知识层=中频、情境层=高频
  2. 对一次检索/一次对话序列，计算各频段的 D(ω)
  3. PE-CNN 自迭代停止条件：∀ω D(ω) < θ(ω)（低频严格、高频容忍）

本工具实现「检索信息差频谱」：
  对一次 graph_retrieve，把 hits 按图层/频段聚合，输出各频段 D：
    D_dc    = 锚点层偏差（图谱基底覆盖）
    D_low   = 结构层偏差（学科结构覆盖）
    D_mid   = 知识层偏差（知识点覆盖）
    D_high  = 情境层偏差（上下文覆盖）
  总 D_norm 保留（= ΣD(ω)），新增频谱分解供按频段收敛判定。

用法：
  python tools/info_gap_spectrum.py "什么是香农熵"           # 单问题频谱
  python tools/info_gap_spectrum.py --list                   # 列出分层模型
"""
import sys, os, json, argparse
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")

# 频段 → 图谱层/概念映射（协议五层记忆 → 频段）
# 低频=结构（学科域/信任）、中频=知识（知识点卡）、高频=情境（对话/细节）
BAND_THRESHOLDS = {
    "dc":  0.10,   # 锚点层：基底偏差必须极小（存在基底不可衰减）
    "low": 0.30,   # 结构层：学科结构偏差，较严格
    "mid": 0.45,   # 知识层：知识点偏差，中等
    "high": 0.60,  # 情境层：上下文偏差，容忍更多噪声
}


def band_of_hit(hit):
    """把命中卡映射到频段：domain 级=低频、知识点卡=中频、情境/对话=高频。"""
    name = (hit.get("name") or "")
    dom = (hit.get("domain") or "")
    score = hit.get("score") or 0
    # 情境层（对话记录/情感/人类观察者）
    if any(k in name for k in ("会话", "人类观察者", "情感情绪", "要点")):
        return "high"
    # 结构层（元层卡/学科域卡）
    if dom in ("智能论", "条件论", "存在论", "信息论", "控制论", "复杂系统") \
            or "结构" in name:
        return "low"
    # 锚点层（协议/基底卡）
    if any(k in name for k in ("协议", "锚点", "元公理", "第零")):
        return "dc"
    # 默认：知识层（知识点/学科内容）
    return "mid"


def spectrum_of_hits(hits, question=""):
    """hits → 各频段 D(ω)。D_band = 1 - max(score_norm)（该频段检索质量的反向）。

    v1.25 修复：无命中的频段不一律给 D=1.0——「高频无情境卡」不代表情境偏差。
    按问题是否涉及该层评估：
      - dc：问题含协议/元层词才评估（锚点层），否则跳过
      - low：问题含学科/结构词才评估，否则跳过
      - mid/high：始终评估（知识/情境是常态层）
    """
    bands = {"dc": [], "low": [], "mid": [], "high": []}
    for h in hits:
        b = band_of_hit(h)
        bands[b].append((h.get("score") or 0, h.get("neural_score") or 0))
    D = {}
    # 问题是否涉及各层
    q_involves = {
        "dc": any(k in question for k in ("协议", "锚点", "元公理", "存在", "基底")),
        "low": any(k in question for k in ("学科", "结构", "智能论", "条件论",
                                           "信息论", "控制论", "蜂群", "协议")),
    }
    for b in ("dc", "low", "mid", "high"):
        if b in ("dc", "low") and not q_involves.get(b) and not bands[b]:
            D[b] = None  # 问题不涉及该层且无命中 → 不评估（不惩罚）
            continue
        if not bands[b]:
            D[b] = 1.0  # 涉及但无命中 = 信息差最大
        else:
            top = max(s for s, _n in bands[b])
            D[b] = round(1.0 - top / (1.0 + top), 3)
    # 总 D_norm（保留原定义）：取所有 hits 最高分
    if hits:
        top_all = max((h.get("score") or 0) for h in hits)
        D["total"] = round(1.0 - top_all / (1.0 + top_all), 3)
    else:
        D["total"] = 1.0
    return D, bands


def converged(D, thresholds=BAND_THRESHOLDS):
    """按频段收敛判定：∀ω D(ω) < θ(ω)。返回 (是否收敛, 未收敛频段)。"""
    unconv = {b: D[b] for b in thresholds
              if D.get(b) is not None and D[b] >= thresholds[b]}
    return (not unconv), unconv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?", default=None, help="待分析问题")
    ap.add_argument("--list", action="store_true", help="列出频段模型")
    args = ap.parse_args()

    if args.list:
        print("频段模型（五层记忆 → 频段 → 阈值）：")
        for b, th in BAND_THRESHOLDS.items():
            print(f"  {b}: θ={th}")
        return

    if not args.question:
        print("用法: python info_gap_spectrum.py <问题> 或 --list")
        return

    import wisdom_book as wb
    import semantic_translate as st
    dex = wb.ConditionDex(db_path=r"C:\Users\FuRongJun\.dsh\profiles\web\data\lingshu.db",
                          fresh=False)
    hits = st.graph_retrieve(dex, args.question, limit=10)
    D, bands = spectrum_of_hits(hits, args.question)
    print(f"Q: {args.question}")
    print(f"hits: {len(hits)}")
    print("信息差频谱 D(ω)：")
    for b in ("dc", "low", "mid", "high"):
        th = BAND_THRESHOLDS.get(b)
        dv = D.get(b)
        if dv is None:
            print(f"  {b:5} —（问题不涉及该层）")
            continue
        mark = "✓" if dv < th else "✗"
        print(f"  {b:5} D={dv:.3f} θ={th} {mark}")
    print(f"  total D_norm = {D.get('total', 1.0):.3f}")
    ok, unconv = converged(D)
    print(f"按频段收敛: {'✓ 全频段收敛' if ok else '✗ 未收敛: ' + str(unconv)}")
    dex.close()


if __name__ == "__main__":
    main()
