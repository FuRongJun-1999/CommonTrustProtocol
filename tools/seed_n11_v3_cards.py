# -*- coding: utf-8 -*-
"""seed_n11_v3_cards.py · 知识域拓展第六批知识卡（幂等）

夜批N11：计算机-二进制/建筑-桥梁/天文-日食月食/经济-通货膨胀 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_binary",
     "二进制",
     "基础科学知识点内容（人话接口）", "计算机",
     "二进制：只用 0 和 1 两个数码的计数系统，是计算机的底层语言——电路的通/"
     "断、磁性的南北正好对应 1 和 0。二进制进位规则是逢二进一：二进制 1011 = "
     "1×8 + 0×4 + 1×2 + 1×1 = 十进制 11。所有数字、文字、图片在计算机里最终都"
     "以二进制 0/1 序列存储。位（bit）是最小单位，8 位=1 字节（byte）。",
     ["什么是二进制", "二进制", "计算机为什么用二进制", "二进制怎么转换十进制",
      "bit和byte", "二进制逢几进一"],
     ["问十六进制", "问ASCII编码"],
     "atomic", "",
     "二进制只用 0/1，逢二进一（1011₂=11₁₀）；计算机电路通断天然对应——8 bit=1 byte。"),
    ("kp_card_bridge",
     "桥梁的基本结构类型",
     "基础科学知识点内容（人话接口）", "建筑学",
     "桥梁的基本结构类型：梁桥（最古老，桥面像横梁架在桥墩上，靠梁的抗弯承重）；"
     "拱桥（拱圈把压力传向两岸，石料抗压强——赵州桥是古代石拱桥代表）；斜拉桥"
     "（钢索从塔上斜拉桥面，跨度大）；悬索桥（桥面吊在主缆上，跨度最大——如金"
     "门大桥）。不同结构对应不同跨度与地质条件。",
     ["桥梁有哪些类型", "桥梁的结构类型", "什么是拱桥", "赵州桥是什么桥",
      "悬索桥和斜拉桥的区别", "桥梁怎么分类"],
     ["问隧道工程", "问桥梁历史"],
     "atomic", "",
     "桥梁四型 = 梁桥（抗弯）/拱桥（抗压，赵州桥）/斜拉桥（拉索）/悬索桥（主缆，跨度最大）。"),
    ("kp_card_eclipse",
     "日食与月食的成因",
     "基础科学知识点内容（人话接口）", "天文学",
     "日食与月食的成因都是三球一线的遮挡：日食=月球运行到太阳与地球之间，月影"
     "投在地球上，月球挡住太阳光（农历初一可能发生，有日全食/日偏食/日环食）；"
     "月食=地球运行到太阳与月球之间，地球挡住射向月球的阳光，月球进入地影变暗"
     "变红（农历十五可能发生，因红光折射常呈「红月亮」）。日食必在初一、月食必"
     "在十五，但每月未必发生——因为月球轨道面与地球轨道面有约 5° 夹角。",
     ["日食和月食是怎么发生的", "什么是日食", "什么是月食", "日食为什么多在初一",
      "月食为什么是红色的", "三球一线", "日食发生在农历的哪一天", "日食发生在农历",
      "农历哪一天有日食", "问日食发生时间"],
     ["问月相变化", "问潮汐"],
     "atomic", "",
     "日食=月球挡日（初一）；月食=地影遮月（十五，红月亮）；三球一线+轨道夹角 5° 故非每月发生。"),
    ("kp_card_inflation",
     "通货膨胀",
     "基础科学知识点内容（人话接口）", "经济学",
     "通货膨胀：流通中的货币量超过实际需要，导致物价总水平持续上涨、货币购买力"
     "下降的现象。温和通胀（2%-3%）常伴随经济增长；恶性通胀（物价飞涨失控）会"
     "摧毁货币信用与经济秩序。衡量指标常用消费者价格指数（CPI）。成因主要三类："
     "需求拉动（钱多货少）、成本推动（原料工资上涨）、货币超发。",
     ["什么是通货膨胀", "通货膨胀的原因", "通货膨胀", "CPI是什么",
      "钱为什么会贬值", "温和通胀与恶性通胀"],
     ["问通货紧缩", "问货币政策工具"],
     "atomic", "",
     "通胀 = 货币超发致物价持续上涨、购买力下降；CPI 度量；成因=需求拉动/成本推动/货币超发。"),
]


def ensure_seed() -> dict:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    inserted = updated = skipped = 0
    for nid, name, domain, dgroup, content, conds, negs, ktype, sub_route, direct in NODES:
        sa = {
            "name": name,
            "kind": "knowledge_point",
            "knowledge_type": ktype,
            "sub_route": sub_route,
            "domain": domain,
            "domain_group": dgroup,
            "edu_level": "",
            "comment": {
                "name": f"{name}（{dgroup}·通识知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——通识高频问题知识条目",
                "执行": direct or content,
                "不适用条件": negs,
            },
        }
        payload = json.dumps(sa, ensure_ascii=False)
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?",
                          (nid,)).fetchone()
        if row and isinstance(row[0], str) and row[0] == payload:
            skipped += 1
            continue
        if not row:
            tags = json.dumps(["knowledge_point", f"domain:{domain}",
                               "level:L2", "status:verified", "batch:拓展第六批"],
                              ensure_ascii=False)
            cur.execute(
                "INSERT INTO nodes (id, content, modality, tags, importance,"
                " confidence, layer, state_attributes, created_at,"
                " spatial_coordinates, temporal_coordinate, condition_space,"
                " semantic_coordinates) VALUES "
                "(?,?,?,?,?,?,?,?," + "CAST(strftime('%s','now') AS INTEGER),"
                 "'[]', '[0,0,0]', '{}', '{}')",
                (nid, content, "text", tags, 0.8, 1.0, "knowledge", payload))
            inserted += 1
        else:
            cur.execute("UPDATE nodes SET state_attributes=?, content=?, "
                        "created_at=CAST(strftime('%s','now') AS INTEGER) "
                        "WHERE id=?", (payload, content, nid))
            updated += 1
    conn.commit()
    conn.close()
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
