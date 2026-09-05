# -*- coding: utf-8 -*-
"""seed_common_122_cards.py · 通识拓展批次122知识卡+题库（幂等）

122：生活常识-食物相克辟谣/地理学-中国重要地理分界线/物理学-电磁波的应用
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_foodmyth",
     "食物相克辟谣",
     "生活常识知识点内容（人话接口）", "生活常识",
     "「食物相克」无科学依据——兰州大学及多机构做过百人试吃实验（柿+蟹/花生+黄"
     "瓜/豆浆+鸡蛋等经典组合），无一例中毒。常见谣言辟谣：①虾+维生素C=砒霜？"
     "——剂量差距亿倍（要吃几百公斤虾才可能达到中毒量）；②豆浆+鸡蛋有毒？——"
     "豆浆煮熟后胰蛋白酶抑制剂已破坏，两者同吃没问题；③菠菜+豆腐=结石？——草酸"
     "确实与钙结合，但焯水去除草酸后同吃反而促进钙利用；④螃蟹+柿子=中毒？——"
     "不新鲜螃蟹或空腹大量柿子（鞣酸）才是原因，与「相克」无关。科学态度：食物"
     "变质、过敏、不耐受才是「吃了不舒服」的真实原因——个体过敏原不同（如乳糖"
     "不耐受），而非「食物相克」。",
     ["食物相克有科学依据吗", "虾和维生素C能一起吃吗", "豆浆和鸡蛋能一起吃吗",
      "菠菜和豆腐会结石吗", "螃蟹和柿子为什么不能一起吃", "食物相克被辟谣"],
     ["问营养学辟谣大全", "问食物不耐受与过敏区别"],
     "atomic", "",
     "「食物相克」无科学依据(百人试吃实验零中毒)：虾+VC 剂量差亿倍/豆浆煮熟即安全/菠菜焯水去草酸；真实原因=变质·过敏·不耐受——剂量与个体差异是关键。"),
    ("kp_card_boundlines",
     "中国重要地理分界线",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国重要地理分界线汇总：①**秦岭—淮河**：1 月 0℃ 等温线+800mm 等降水量"
     "线+暖温带/亚热带+湿润/半湿润+水田/旱地+河流结冰与否——南北方分界；②**大"
     "兴安岭—阴山—贺兰山—巴颜喀拉山—冈底斯山**：400mm 等降水量线——季风区/非"
     "季风区、农耕/畜牧分界；③**大兴安岭—太行山—巫山—雪峰山**：地势二、三级"
     "阶梯分界；④昆仑山—祁连山—横断山：地势一、二级阶梯分界；⑤黑河—腾冲线"
     "（胡焕庸线）：人口地理分界（东南 43% 面积住 94% 人口）；⑥季风区/非季风"
     "区界线也是 400mm 线（大致重合）。",
     ["中国重要地理分界线有哪些", "秦岭淮河线的地理意义", "胡焕庸线是什么",
      "地势三级阶梯的分界线", "400毫米等降水量线的意义", "季风区与非季风区界线"],
     ["问胡焕庸线成因", "问阶梯经济差异"],
     "atomic", "",
     "分界线五条=秦淮(南北·1月0℃·800mm)+400mm(季风界·农牧界·胡焕庸线重合)+二三阶梯(大兴安岭太行巫山雪峰)+一二阶梯(昆祁横)+黑河腾冲(94%人43%地)。"),
    ("kp_card_emwaveapp",
     "电磁波的应用",
     "基础科学知识点内容（人话接口）", "物理学",
     "电磁波谱从长到短的应用：①**无线电波**——广播/电视/手机/卫星通信/WiFi"
     "（波长米到毫米）；②**微波**——微波炉加热（水分子振动）、雷达、5G 通信；"
     "③**红外线**——遥控器、热成像（测温/夜视）、红外理疗；④**可见光**——照"
     "明/光纤通信（激光）；⑤**紫外线**——杀菌消毒、验钞（荧光防伪）、促进维"
     "生素 D 合成（过量致癌）；⑥**X 射线**——医学透视/安检；⑦**γ 射线**——"
     "放疗（杀死癌细胞）、 sterilization 灭菌。频率越高能量越大、穿透力越强——"
     "电离作用越强（紫外以上伤 DNA）。手机辐射属于无线电波（非电离辐射，无证据"
     "致癌——WHO 分类 2B 类即「可疑但证据不足」）。",
     ["电磁波的应用有哪些", "微波炉用的是什么波", "红外线的应用",
      "紫外线的应用与危害", "X射线的作用", "手机辐射会致癌吗"],
     ["问电磁波谱频率表", "问电离辐射防护"],
     "atomic", "",
     "电磁波谱应用=无线电(通信)/微波(雷达炉5G)/红外(遥控热成像)/可见光/紫外(杀菌验钞·过量伤)/X光(透视)/γ(放疗)：频率越高能量越大电离越强；手机辐射=非电离无证据致癌。"),
]

QUESTIONS = [
    ("QB-626", "食物相克有科学依据吗", "生活常识", "技术直答",
     ["没有", "辟谣"], "通识拓展122"),
    ("QB-627", "中国重要地理分界线有哪些", "地理学", "技术直答",
     ["秦岭淮河", "胡焕庸线"], "通识拓展122"),
    ("QB-628", "电磁波的应用有哪些", "物理学", "技术直答",
     ["通信", "遥控", "透视"], "通识拓展122"),
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
                               "level:L2", "status:verified", "batch:通识拓展122"],
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
    bank["version"] = "v3.6"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
