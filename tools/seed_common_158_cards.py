# -*- coding: utf-8 -*-
"""seed_common_158_cards.py · 通识拓展批次158知识卡+题库（幂等）

158：语文-谦辞与敬辞/生活常识-宴席座次礼仪/生活常识-挑西瓜的技巧
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（三伏在梅雨卡提及、
孝文帝/南北极等候选命中已有覆盖弃选）。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_politewords",
     "谦辞与敬辞",
     "人文通识知识点内容（人话接口）", "文学",
     "汉语礼貌用语两大体系——**谦辞（贬己）**与**敬辞（尊人）**，核心=「家大"
     "舍小令外人」：①称自己长辈用「**家**」——家父/家母/家兄（对人称自己的父"
     "母哥哥）；②称自己晚辈平辈用「**舍**」——舍弟/舍妹/舍侄（舍=寒舍的自"
     "谦）；③称**对方**亲属用「**令**」——令尊/令堂（对方父母）、令郎/令爱"
     "（对方儿女）——「令」=美好的，绝不能用来称自己家人（「我令尊」是错"
     "误）。其他常用：谦辞=鄙人/拙见/拙作/寒舍/拜读（读对方作）/惠存（请对"
     "方保存）/抛砖引玉；敬辞=令/贵（贵姓/贵公司）/高见/大作/府上/垂询（上"
     "级问下级）/光临/斧正（请对方改文章）。常见错误：「我令郎考得好」❌→「"
     "犬子考得好」✓；「你家父」❌→（家父是自称，说对方父亲直接称「令尊」）。",
     ["令尊是什么意思", "家父和令尊的区别", "谦辞敬辞有哪些",
      "舍弟是什么意思", "惠存和拜读", "拙见是什么意思"],
     ["问成语典故（用成语卡）", "问书信格式"],
     "atomic", "",
     "谦敬体系「家大舍小令外人」：家父/家兄=自称长辈、舍弟舍妹=自称晚辈平辈、令尊令堂令郎令爱=尊称对方亲属（令不可自称）；谦=鄙人拙见寒舍、敬=贵姓大作府上垂询斧正；「我令尊」为典型误用。"),
    ("kp_card_seating",
     "宴席座次礼仪",
     "生活常识知识点内容（人话接口）", "生活常识",
     "中式宴席座次要点：①**主位**——正对房门/包间正中（视野最好、能迎客的位"
     "置）由**主人（请客者）**就座；②**主宾**（最重要的客人）坐**主人右侧**"
     "（以右为尊），副主宾坐主人左侧；**副主人**（陪客方二号）坐主位正对面"
     "（背门位，方便进出招呼上菜）；③座次从主位右手起**顺时针**依次降级排布"
     "；④落座礼仪：等主人示意「入座」再坐、长者先坐；晚辈坐末位（靠门位，便"
     "于传菜跑腿）；⑤转桌礼仪：顺时针慢转、新菜先转到主宾面前、别人夹菜时不"
     "转桌。国际西餐：主人夫妇分坐长桌两端，男女间隔而坐。记不住就一句话：「"
     "**面对门的是主位，主人右手最重要**」。",
     ["宴席主位坐哪里", "主宾坐哪个位置", "中式宴席座次",
      "以右为尊是什么意思", "转桌礼仪", "包间怎么排座次"],
     ["问敬酒顺序礼节", "问西餐刀叉用法"],
     "atomic", "",
     "宴席座次=正对门为主位（主人坐），主宾坐主人右侧以右为尊、副主宾在左，副主人背门坐对面；顺时针依次降级、晚辈靠门位；转桌顺时针慢转新菜先到主宾；一句话=面对门的是主位，主人右手最重要。"),
    ("kp_card_pickmelon",
     "挑西瓜的技巧",
     "生活常识知识点内容（人话接口）", "生活常识",
     "挑熟西瓜五看一听：①**看纹路**——纹路清晰、间隔宽、皮表有「白霜」果粉"
     "（自然成熟标志）；②**看瓜脐**——底部瓜脐（肚脐眼）**小而内凹**的甜（大"
     "而外凸的多皮厚欠熟）；③**看瓜蒂**——蒂弯（卷须状）且新鲜绿=藤上熟瓜，"
     "干枯发黑=摘太久；④**看着地面黄斑**——贴地的「阴面」发黄说明在藤上长够"
     "了熟（白亮=提前采摘）；⑤**拍听声**——熟瓜「**砰砰**」浑浊回弹（振动沉"
     "稳），生瓜「当当」清脆硬响，过熟/空心「噗噗」闷哑；⑥掂重量——同品种大"
     "小选相对轻的（水分足熟透）；⑦瓜形匀称对称、两头一致。储藏：整瓜阴凉放"
     "置，切开覆保鲜膜冷藏且 24 小时内吃完（切面细菌滋生快——「隔夜西瓜」要"
     "切掉表面 1cm 更稳）。",
     ["怎么挑熟西瓜", "拍西瓜听声音", "瓜脐小的是不是更甜",
      "瓜蒂弯的好还是直的好", "隔夜西瓜能吃吗", "西瓜纹路"],
     ["问其他水果挑选", "问西瓜储存温度"],
     "atomic", "",
     "挑西瓜=纹路清晰带果粉+瓜脐小内凹+瓜蒂弯而鲜+贴地黄斑+拍声「砰砰」浑浊（当当生/噗噗过熟）+同大小选轻；切面覆膜冷藏 24h 内吃完、隔夜切掉表面 1cm 更稳。"),
]

QUESTIONS = [
    ("QB-730", "「令尊」「家父」「舍弟」分别指谁？为什么不能说「我令尊」？", "文学", "技术直答",
     ["对方父亲", "自己父亲", "谦辞", "敬辞", "弟弟", "家大舍小令外人"], "通识拓展158"),
    ("QB-731", "中式宴席的主位一般坐哪个位置？主宾应该安排坐在哪里？", "生活常识", "技术直答",
     ["正对门", "面对门", "主人右侧", "以右为尊"], "通识拓展158"),
    ("QB-732", "拍西瓜听声音怎么判断生熟？看瓜脐和瓜蒂分别注意什么？", "生活常识", "技术直答",
     ["砰砰", "浑浊", "瓜脐内凹", "小", "瓜蒂弯"], "通识拓展158"),
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
                               "level:L2", "status:verified", "batch:通识拓展158"],
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
    bank["version"] = "v4.31"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
