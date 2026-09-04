# -*- coding: utf-8 -*-
"""seed_antipure_01_cards.py · 反纯巡检规则生效后首批知识卡（幂等）

反纯巡检批次01：微生物学/光学透镜/心理学-记忆类型/地理-河流 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_microbe",
     "细菌与病毒的区别",
     "基础科学知识点内容（人话接口）", "微生物学",
     "细菌与病毒的核心区别：①细菌是单细胞生物，有细胞壁和细胞器，可独立"
     "代谢繁殖；病毒无细胞结构，只有核酸+蛋白质外壳，必须寄生在活细胞内才"
     "能复制。②细菌用抗生素（如青霉素）治疗有效；病毒用抗生素无效，需抗病"
     "毒药物或靠免疫系统。③细菌有害有益（肠道菌群帮助消化），病毒绝大多数"
     "有害。大小：细菌约 1-5 微米，病毒约 20-300 纳米——病毒比细菌小得多。",
     ["细菌和病毒的区别", "细菌病毒", "病毒和细菌有什么不同", "抗生素对病毒有效吗",
      "细菌有多大", "病毒和细菌哪个大"],
     ["问疫苗原理", "问免疫细胞"],
     "atomic", "",
     "细菌=单细胞可独立代谢+抗生素有效；病毒=寄生复制+抗生素无效+比细菌小得多。"),
    ("kp_card_lens",
     "凸透镜与凹透镜",
     "基础科学知识点内容（人话接口）", "光学",
     "凸透镜与凹透镜：凸透镜中间厚边缘薄，对光线有会聚作用——可成实像（投影"
     "仪、照相机）或虚像（放大镜）；凹透镜中间薄边缘厚，对光线有发散作用——"
     "只能成虚像（近视眼镜用凹透镜）。焦距是从光心到焦点的距离。远视眼用凸透"
     "镜矫正，近视眼用凹透镜矫正。",
     ["凸透镜和凹透镜的区别", "凸透镜", "凹透镜", "什么是会聚透镜",
      "近视眼镜是什么透镜", "透镜成像"],
     ["问光的折射", "问反射定律"],
     "atomic", "",
     "凸透镜=会聚（放大镜/远视矫正）；凹透镜=发散（近视矫正）；焦点/焦距是核心参数。"),
    ("kp_card_memtype",
     "人类的记忆类型",
     "基础科学知识点内容（人话接口）", "心理学",
     "人类的记忆按持续时间分三种：感觉记忆（<1秒，容量大但极短暂）、短时记忆"
     "（约 15-30 秒，容量约 7±2 个组块，如记电话号码）、长期记忆（可终身保持，"
     "容量几乎无限）。长期记忆又分陈述性记忆（事实与事件，可用语言描述）和程"
     "序性记忆（技能与习惯，如骑车、打字）。睡眠对记忆巩固至关重要——海马体"
     "在睡眠中将短时记忆转化为长期记忆。",
     ["人类的记忆类型", "感觉记忆短时记忆长期记忆", "短时记忆容量是多少",
      "记忆的分类", "什么是程序性记忆", "睡眠对记忆的影响"],
     ["问遗忘曲线", "问阿尔茨海默"],
     "atomic", "",
     "记忆三阶段 = 感觉（<1s）→ 短时（15-30s，7±2）→ 长期（终身）；睡眠中海马体巩固。"),
    ("kp_card_rivers",
     "中国主要河流",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国主要河流：长江——中国第一长河（约 6300 公里），世界第三长河，流经"
     "11 个省市；黄河——中国第二长河（约 5464 公里），中华民族母亲河，因含沙"
     "量世界最高水色土黄得名；珠江——南方最大河流；黑龙江——中俄界河；雅鲁"
     "藏布江——世界最高的大河。中国河流趋势：大多自西向东流入太平洋（因西高"
     "东低三级阶梯地势）。",
     ["中国主要河流", "长江和黄河", "中国最长的河流", "黄河为什么是黄色的",
      "中国河流", "雅鲁藏布江"],
     ["问长江三峡", "问南水北调"],
     "atomic", "",
     "长江 6300km 第一/黄河 5464km 第二（含沙最高）/珠江南方最大；地势西高东低河流东流。"),
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
                               "level:L2", "status:verified", "batch:反纯巡检01"],
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
