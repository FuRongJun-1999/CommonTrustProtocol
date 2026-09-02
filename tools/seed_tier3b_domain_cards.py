# -*- coding: utf-8 -*-
"""seed_tier3b_domain_cards.py · 候选域清单第三梯队B知识卡（幂等·收官批）

批十一：通信原理/能源科学/教育学/考古人类学 四域各一张，KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_analogdigital",
     "模拟信号与数字信号",
     "工程科学知识点内容（人话接口）", "通信原理",
     "模拟信号与数字信号的区别：模拟信号的取值连续（如麦克风输出的电压波形，"
     "直接对应声音的连续变化）；数字信号取值离散（只有有限个电平，如 0/1 二进制码）。"
     "数字信号的优势是抗干扰能力强（噪声不累积、中继可再生整形）、可加密、可纠错"
     "——现代通信系统（手机/光纤/互联网）都用数字信号；模拟量进数字系统要经过"
     "采样、量化、编码三步（A/D 转换）。",
     ["模拟信号和数字信号的区别", "什么是数字信号", "什么是模拟信号",
      "模拟信号数字信号", "问数字信号为什么抗干扰", "A/D转换"],
     ["问调制解调细节", "问 5G 编码"],
     "atomic", "",
     "模拟连续/数字离散；数字抗干扰（可再生）+可加密纠错；模拟入数字系统走采样-量化-编码。"),
    ("kp_card_fissionfusion",
     "核裂变与核聚变",
     "工程科学知识点内容（人话接口）", "能源科学",
     "核裂变与核聚变：裂变是重核（铀-235/钚-239）被中子撞击分裂成两个较轻核并放出"
     "能量与中子（链式反应，现有核电站原理，放射性废料是难题）；聚变是轻核（氘/氚）"
     "聚合成较重核（太阳的产能方式，能量密度更高、燃料海水中就有、产物放射性小），"
     "但需要上亿度高温克服核间斥力，可控聚变尚未商用（ITER/东方超环在攻关）。"
     "两者单位质量释能都远超化学燃烧（质能方程 E=mc²）。",
     ["核裂变和核聚变的区别", "什么是核聚变", "什么是核裂变",
      "核电站原理", "太阳为什么发光", "问可控核聚变"],
     ["问核武器历史", "问放射性防护"],
     "atomic", "",
     "裂变 = 重核分裂（现有核电，有废料难题）/ 聚变 = 轻核聚合（太阳能来源，可控尚未商用）。"),
    ("kp_card_zpd",
     "最近发展区",
     "社会科学知识点内容（人话接口）", "教育学",
     "最近发展区（ZPD，维果茨基提出）：学习者独立能解决问题的水平与在他人帮助下"
     "能达到的水平之间的差距——教学应瞄准这个区间：太易没有成长，太难够不着。"
     "帮助手段叫「脚手架」（scaffolding）：提示、示范、分解步骤，随学习者能力提升"
     "逐步撤除。与「因材施教」直观对应。",
     ["什么是最近发展区", "最近发展区", "问 ZPD", "维果茨基",
      "什么是脚手架教学", "教学应该教多难的内容"],
     ["问皮亚杰阶段论", "问建构主义流派史"],
     "atomic", "",
     "最近发展区 = 独立水平与助援水平之间的差距，教学瞄准此区间，脚手架随成长撤除。"),
    ("kp_card_c14",
     "碳十四测年",
     "社会科学知识点内容（人话接口）", "考古学",
     "碳十四测年原理：宇宙射线使大气中产生放射性碳-14，生物存活期间与大气持续"
     "交换、体内碳-14 比例恒定；死亡后交换停止，碳-14 按 5730 年半衰期衰变减少——"
     "测量遗骸中剩余碳-14 比例即可推算死亡年代。适用范围约 5 万年以内（更古老"
     "样本碳-14 已衰变殆尽），适合测有机物（骨骼/木炭/织物），不能直接测石头。",
     ["碳十四测年", "碳14测年原理", "考古怎么断代", "问放射性测年",
      "碳十四是什么", "文物年代怎么测定"],
     ["问热释光测年", "问青铜器断代"],
     "atomic", "",
     "碳十四测年 = 死后碳-14 按 5730 年半衰期衰减，测余量推年代；适用 5 万年内有机物。"),
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
                "name": f"{name}（{dgroup}·工程与社科知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——工程与社科高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:候选域第三梯队B"],
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
