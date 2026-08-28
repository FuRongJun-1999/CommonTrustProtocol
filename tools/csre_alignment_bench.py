# -*- coding: utf-8 -*-
"""csre_alignment_bench.py · CSRE 域级排序 ↔ card_route 实际命中 一致性基准

三层路由架构（修正设计）的 L1 接线前置证据：
  L1 域级收敛 = CSRE 分块矩阵乘（rank_domains）
  L2 域内路由 = card_route
  L3 复合下钻 = navigate_retrieve
若 CSRE 的 top 域与 card_route 实际命中卡的 domain 高度吻合（≥80%），
则 L1 可安全接入主检索链做域级预收敛；否则分歧清单即改进证据。

判定口径：域族一致 = CSRE top 域串与命中卡 domain 串相同，
或一方 domain_group 属于另一方的子串（自造域串场景）。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))

QUESTIONS = [
    # 六域（学科骨架）
    "三角形内角和是多少", "光的反射定律是什么", "二重积分换元法",
    "水的电解实验现象", "细胞分裂的过程", "鸦片战争的起因",
    # 计算机域（kp 卡）
    "复合赋值怎么执行", "三次握手过程", "图度分布怎么统计",
    "插入排序怎么写", "TCP 和 UDP 的区别", "工作窃取调度",
    # 导航种子域（生活）
    "婆媳矛盾怎么处理", "理财亏了怎么办", "孩子教育观念冲突",
    "想养宠物怎么开始", "拖延症怎么办", "第一次租房注意什么",
]

CSRE_DOMAIN_ALIAS = {
    # CSRE 域串（学科骨架/自造）→ 归一族
}


def domain_family(d: str) -> str:
    """域族归一：骨架域取主学科词，自造域串取首段。"""
    if not d:
        return ""
    for k in ("数学", "物理", "化学", "生物", "政治", "历史", "地理", "英语", "语文",
              "计算机", "工程", "家庭", "经济", "金融", "心理", "宠物", "管理", "医学"):
        if k in d:
            return k
    return d.split("知识点内容")[0][:6]


def main() -> int:
    from wisdom_book import ConditionDex
    from semantic_translate import card_route
    from csre import Csre

    db = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")
    dex = ConditionDex(db_path=db, fresh=False)
    csre = Csre(db)
    csre.ensure_loaded() if hasattr(csre, "ensure_loaded") else csre.build_index()

    rows = []
    hit = 0
    for q in QUESTIONS:
        routes = card_route(dex, q, limit=3)
        top = routes[0] if routes else None
        card_dom = (top or {}).get("domain") or ""
        card_name = (top or {}).get("name") or ""
        doms = csre.rank_domains(q, top_k=1)
        csre_dom = doms[0]["domain"] if doms else ""
        fam_c = domain_family(card_dom)
        fam_s = domain_family(csre_dom)
        # 空域 = L1 盲（CSRE 零向量），判分歧不豁免
        ok = bool(fam_c) and bool(csre_dom) and (
            fam_c == fam_s or fam_c in csre_dom or fam_s in card_dom)
        hit += ok
        rows.append({"q": q, "card": card_name[:14], "card_dom": card_dom[:18],
                     "csre_dom": csre_dom[:24], "agree": ok})
    dex.close()

    rate = hit / len(QUESTIONS)
    print("=== CSRE ↔ card_route 域级一致性基准 ===\n")
    for r in rows:
        mark = "✓" if r["agree"] else "✗"
        print(f"[{mark}] {r['q'][:16]:<18} 卡={r['card']:<16} 卡域={r['card_dom']:<20} CSRE域={r['csre_dom']}")
    print(f"\n吻合率: {hit}/{len(QUESTIONS)} = {rate:.0%}")
    print("L1 接线判定:", "✓ 安全（≥80%）" if rate >= 0.8 else "△ 分歧清单即改进证据（<80%）")
    json.dump({"rate": rate, "rows": rows},
              open(os.path.join(HERE, "csre_alignment_report.json"), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
