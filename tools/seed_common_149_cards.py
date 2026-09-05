# -*- coding: utf-8 -*-
"""seed_common_149_cards.py · 通识拓展批次149知识卡+题库（幂等·两卡精批次）

149：历史学-义和团运动与八国联军/生活常识-户口与居住证
KCCS 四要素+题干原句触发词。三重预检：八国联军在近代史链卡仅一句列举（主题
未展开）、户口主题零覆盖（与身份证卡/居住证提及卡划界）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_yihetuan",
     "义和团运动与八国联军",
     "人文通识知识点内容（人话接口）", "历史学",
     "义和团运动：1898 年前后兴起于山东（前身义和拳），以「**扶清灭洋**」为口"
     "号的反帝爱国运动——但也带有盲目排外色彩（烧教堂杀教士毁铁路电线）。**"
     "1900 年**列强以保护侨民为名组成**八国联军**（英法德俄美日意奥）从天津大"
     "沽登陆，攻陷天津、北京，慈禧携光绪西逃（「庚子国变」）；联军在北京烧杀"
     "抢掠。**1901 年**（辛丑年）清政府被迫签订《**辛丑条约**》——中国近代史"
     "上赔款最多、主权丧失最严重的不平等条约：①赔款白银 **4.5 亿两**（分 39 "
     "年还清，本息合计约 9.8 亿两，「人均一两」羞辱性数字）；②划定北京**东交"
     "民巷**为使馆界，界内驻军、中国人不得居住；③拆毁大沽炮台，京榆铁路沿线"
     "列强驻军；④清政府保证严禁人民反帝组织。**影响**：清政府完全成为列强统"
     "治中国的工具（「洋人的朝廷」），中国**完全**沦为半殖民地半封建社会——"
     "也促使国人认清清廷面目，五年后辛亥革命爆发。",
     ["义和团运动的口号", "八国联军是哪八国", "辛丑条约的内容",
      "赔款最多的条约", "庚子国变", "东交民巷使馆界"],
     ["问鸦片战争（用近代史链前段卡）", "问义和团组织源流考据"],
     "atomic", "",
     "义和团「扶清灭洋」反帝但盲目排外；1900 八国联军(英法德俄美日意奥)攻占京津；1901《辛丑条约》=赔 4.5 亿两(本息 9.8 亿)+东交民巷使馆界驻军+拆大沽炮台+严禁反帝——清廷成「洋人的朝廷」，中国完全沦为半殖民地半封建，五年后辛亥革命。"),
    ("kp_card_hukou",
     "户口与居住证",
     "生活常识知识点内容（人话接口）", "生活常识",
     "三个概念分清：①**户口（户籍）**——登记家庭成员与籍贯的法定簿册（户口"
     "本），由公安机关管理；与教育资源（学区）、购房资格、社保养老地域挂钩；"
     "**户口迁移**=把户籍从 A 地迁到 B 地（常见途径：购房落户/人才引进/积分落"
     "户/投靠亲属，大城市有门槛、中小城市已放宽）；②**居住证**——**非户籍"
     "地**常住人口的登记凭证（住满半年+合法稳定就业/住所即可申领），持证人可"
     "享子女义务教育、医保、考驾照、积分落户等基本公共服务——是「暂住证」的"
     "升级替代；③**身份证**——证明个人身份（全国通用），**户口本**——证明家"
     "庭关系与户籍地（办结婚证/房产过户/入学等常用）。新生儿：出生医学证明→"
     "落户登记→办身份证（满 16 周岁强制，未满可自愿办）。",
     ["户口和居住证有什么区别", "怎么把户口迁到城市", "居住证怎么办",
      "暂住证和居住证", "户口本能做什么用", "新生儿落户流程"],
     ["问身份证办理（用身份证卡）", "问具体城市落户政策"],
     "atomic", "",
     "户口=户籍簿册（学区/购房/社保地域挂钩，迁移走购房/人才引进/积分）；居住证=非户籍地常住凭证（住满半年+稳定就业住所，享子女入学医保驾照等公共服务，暂住证升级版）；身份证证身份/户口本证家庭关系；新生儿=出生证→落户→16 岁办身份证。"),
]

QUESTIONS = [
    ("QB-708", "《辛丑条约》的赔款总额是多少？为什么说清政府从此成为「洋人的朝廷」？", "历史学", "技术直答",
     ["4.5亿两", "九亿八", "东交民巷", "严禁反帝", "完全"], "通识拓展149"),
    ("QB-709", "居住证和户口有什么区别？办理居住证一般需要什么条件？", "生活常识", "技术直答",
     ["户籍", "常住", "半年", "稳定就业", "公共服务", "学区"], "通识拓展149"),
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
                               "level:L2", "status:verified", "batch:通识拓展149"],
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

    bank = json.load(open(BANK, encoding="utf-8"))
    qs = bank["questions"]
    have = {q["id"] for q in qs}
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-05"})
        added += 1
    bank["version"] = "v4.22"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
