# -*- coding: utf-8 -*-
"""seed_common_06_cards.py · 通识拓展批次知识卡（幂等）

06：生物-神经元与神经系统/化学-燃烧三要素/物理-杠杆原理/地理-地球自转与公转
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_neuron",
     "神经元与神经系统",
     "基础科学知识点内容（人话接口）", "生物学",
     "神经元（神经细胞）是神经系统结构和功能的基本单位，由细胞体、树突（接收"
     "信号）和轴突（传导信号）组成。神经系统分中枢神经系统（脑和脊髓）和周围"
     "神经系统。神经元之间通过突触传递信息（神经递质）。反射弧=感受器→传入神"
     "经→神经中枢→传出神经→效应器，是神经调节的基本方式。",
     ["什么是神经元", "神经元", "神经系统的组成", "什么是反射弧",
      "神经系统分哪几部分", "神经元怎么传递信息"],
     ["问大脑结构", "问内分泌系统"],
     "atomic", "",
     "神经元 = 细胞体+树突（收）+轴突（传）；突触传递；反射弧=感受器→传入→中枢→传出→效应器。"),
    ("kp_card_combustion",
     "燃烧的三要素",
     "基础科学知识点内容（人话接口）", "化学",
     "燃烧的三要素（火三角）：①可燃物（能燃烧的物质如纸、木材、汽油）；②助"
     "燃剂（通常是氧气）；③着火源（达到着火点的热量，如火柴、电火花）。三者缺"
     "一不可——灭火的原理就是破坏其中任何一个：隔离可燃物、隔绝氧气（用灭火器"
     "或湿布盖灭）、降温到着火点以下（用水浇）。",
     ["燃烧的三要素", "燃烧需要什么条件", "什么是可燃物", "灭火的原理",
      "燃烧三要素", "火三角"],
     ["问灭火器种类", "问化学爆炸"],
     "atomic", "",
     "燃烧三要素 = 可燃物+助燃剂（氧气）+着火源（达着火点）；灭火=破坏任一要素。"),
    ("kp_card_earthrotation",
     "地球的自转与公转",
     "基础科学知识点内容（人话接口）", "地理学",
     "地球的两种基本运动：自转=地球绕地轴旋转，方向自西向东，周期约 24 小时，"
     "产生昼夜交替；公转=地球绕太阳运行，周期约 365.25 天，产生四季更替。地轴"
     "倾斜约 23.5°，使太阳直射点在南北回归线间移动——导致昼夜长短变化和四季"
     "更替。夏至直射北回归线（北半球昼最长），冬至直射南回归线。",
     ["地球的自转和公转", "地球自转产生了什么", "地球公转周期", "为什么有四季变化",
      "自转方向", "地轴倾斜多少度"],
     ["问月球运动", "问经纬度"],
     "atomic", "",
     "自转 24h 产生昼夜；公转 365.25 天产生四季（地轴倾斜 23.5° 导致太阳直射点移动）。"),
    ("kp_card_blockchain",
     "区块链的基本原理",
     "信息技术知识点内容（人话接口）", "计算机",
     "区块链：一种去中心化的分布式账本技术——数据以区块为单位按时间顺序链式"
     "连接，每个区块包含前一块的哈希值，任何修改都会破坏后续所有区块的哈希链，"
     "因此数据极难篡改。网络中每个节点都保存完整账本副本（去中心化），新数据需"
     "要经过共识机制（如工作量证明/权益证明）验证后才能写入。应用：比特币等加"
     "密货币、智能合约、供应链溯源。",
     ["什么是区块链", "区块链原理", "区块链去中心化", "区块怎么连接",
      "区块链有什么用", "比特币的底层技术"],
     ["问智能合约细节", "问加密算法细节"],
     "atomic", "",
     "区块链 = 去中心化分布式账本，区块含前块哈希链式连接极难篡改；共识机制验证写入。"),
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
                               "level:L2", "status:verified", "batch:通识拓展06"],
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
