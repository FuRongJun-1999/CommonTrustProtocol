# -*- coding: utf-8 -*-
"""seed_common_17_cards.py · 通识拓展批次17知识卡+题库（幂等）

17：音乐-乐器分类/艺术-世界名画/天文学-黑洞/计算机科学-机器学习基础
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_instruments",
     "乐器的分类",
     "人文通识知识点内容（人话接口）", "音乐",
     "乐器按发声与演奏方式分类：西洋乐器——键盘（钢琴/管风琴/手风琴）、弦乐"
     "（小提琴/中提琴/大提琴/低音提琴，弓拉或拨弦发声）、木管（长笛/单簧管/"
     "双簧管/萨克斯）、铜管（小号/圆号/长号/大号）、打击乐（定音鼓/小军鼓/"
     "镲）。中国民族乐器——拉弦（二胡/高胡）、弹拨（古筝/琵琶/扬琴/阮）、吹管"
     "（笛子/箫/唢呐/笙）、打击（锣/鼓/钹）。「钢琴属于键盘乐器而非弦乐器」是"
     "常见考点——虽有琴弦但以键盘击弦发声。",
     ["钢琴和小提琴分别属于什么类型的乐器", "乐器怎么分类", "钢琴是弦乐器吗",
      "二胡属于什么乐器", "民族乐器有哪些", "小提琴是弦乐器吗"],
     ["问乐理五线谱", "问著名作曲家生平"],
     "atomic", "",
     "乐器分类：西洋=键盘(钢琴)/弦乐(小提琴)/木管/铜管/打击；民族=拉弦(二胡)/弹拨(古筝琵琶)/吹管(笛箫)/打击。"),
    ("kp_card_famouspaintings",
     "世界著名绘画作品",
     "人文通识知识点内容（人话接口）", "艺术",
     "世界名画：《蒙娜丽莎》——列奥纳多·达·芬奇作，藏法国卢浮宫，以「神秘的"
     "微笑」闻名；《星空》（又译星月夜）——文森特·梵高作，藏纽约现代艺术博物"
     "馆，旋转的星云笔触是后印象派代表；《呐喊》——爱德华·蒙克作，表现主义先"
     "声；《格尔尼卡》——巴勃罗·毕加索作，控诉法西斯轰炸的立体主义巨作；中国"
     "十大传世名画之首《清明上河图》——北宋张择端作，描绘汴京市井繁华。",
     ["蒙娜丽莎是谁画的", "世界名画有哪些", "星空是谁画的", "蒙娜丽莎藏在哪个博物馆",
      "清明上河图是谁画的", "格尔尼卡的作者"],
     ["问印象派流派史", "问绘画技法细节"],
     "atomic", "",
     "名画=蒙娜丽莎(达芬奇·卢浮宫)+星空(梵高·MoMA)+呐喊(蒙克)+格尔尼卡(毕加索)+清明上河图(张择端·北宋)。"),
    ("kp_card_blackhole",
     "黑洞与事件视界",
     "基础科学知识点内容（人话接口）", "天文学",
     "黑洞是引力极强的一种天体——逃逸速度超过光速，连光都无法逃出，因此「看"
     "不见」；其边界叫事件视界，越过视界的任何信息都无法返回。恒星级黑洞由大"
     "质量恒星（约20倍太阳质量以上）燃料耗尽后核心坍缩形成；星系中心普遍存在"
     "超大质量黑洞，银河系中心为 人马座A*（约400万倍太阳质量）。2019 年事件视"
     "界望远镜（EHT）公布人类首张黑洞照片（M87*），2022 年又公布银心人马座A*"
     "照片。",
     ["黑洞是什么", "黑洞为什么连光都逃不出来", "什么是事件视界",
      "黑洞是怎么形成的", "第一张黑洞照片", "银河系中心的黑洞"],
     ["问霍金辐射细节", "问白洞虫洞"],
     "atomic", "",
     "黑洞=逃逸速度超光速故光不可逃；边界=事件视界；成因=大质量恒星坍缩；银心=人马座A*；首照=EHT 2019(M87*)。"),
    ("kp_card_machinelearning",
     "机器学习基础",
     "基础科学知识点内容（人话接口）", "计算机科学",
     "机器学习是人工智能的一个分支：不靠人工写出全部规则，而是让程序从数据中"
     "自动学习规律——普通编程是「人写规则+输入→输出」，机器学习是「输入+输出"
     "（数据）→学出规则」。按学习方式分三类：监督学习（用带标注的数据训练，如"
     "垃圾邮件分类）、无监督学习（无标注数据中找结构，如聚类）、强化学习（靠"
     "环境奖励试错学习，如 AlphaGo）。典型应用：图像识别/语音识别/推荐系统/"
     "大语言模型。",
     ["机器学习和普通编程有什么区别", "什么是机器学习", "监督学习和无监督学习的区别",
      "什么是强化学习", "机器学习有哪些应用", "人工智能和机器学习的关系"],
     ["问神经网络反向传播细节", "问具体算法实现"],
     "atomic", "",
     "机器学习=从数据自动学规律而非人写规则；三类=监督(标注)/无监督(聚类)/强化(奖励)；应用=识别/推荐/大模型。"),
]

QUESTIONS = [
    ("QB-201", "钢琴和小提琴分别属于什么类型的乐器", "音乐", "技术直答",
     ["键盘乐器", "弦乐器"], "通识拓展17"),
    ("QB-202", "蒙娜丽莎是谁画的", "艺术", "技术直答",
     ["达芬奇", "卢浮宫"], "通识拓展17"),
    ("QB-203", "黑洞是什么", "天文学", "技术直答",
     ["事件视界", "引力", "光"], "通识拓展17"),
    ("QB-204", "机器学习和普通编程有什么区别", "计算机科学", "技术直答",
     ["从数据学习", "规则"], "通识拓展17"),
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
                               "level:L2", "status:verified", "batch:通识拓展17"],
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
                   "added": "2026-09-04"})
        added += 1
    bank["version"] = "v1.9"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
