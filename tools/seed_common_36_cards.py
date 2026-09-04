# -*- coding: utf-8 -*-
"""seed_common_36_cards.py · 通识拓展批次36知识卡+题库（幂等）

36：物理学-保险丝保护电路/生活常识-煮饺子点凉水/历史-鉴真东渡/语文-四大名著
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_fuse",
     "保险丝与空气开关",
     "基础科学知识点内容（人话接口）", "物理学",
     "保险丝（熔断器） protecting 电路的原理：由电阻率大、熔点低的铅锑合金制成，"
     "串联在火线上——当电路电流过大（短路或同时用电器总功率过大即过载）时，根"
     "据焦耳定律 Q=I²Rt 保险丝产生大量热率先熔断，切断电路保护线路与电器。保险"
     "丝不能用铜丝铁丝代替（熔点太高、电流过大时不断，失去保护作用）——这是"
     "经典安全考点。现代家庭多用空气开关（断路器）：电流过载时电磁脱扣或热脱"
     "扣自动跳闸，排除故障后可复位重合，比保险丝方便可重复使用。两者都保护"
     "「过流」，但不防漏电——防漏电要靠漏电保护器（RCD，检测火线零线电流不平"
     "衡即跳闸）。",
     ["保险丝为什么能保护电路", "保险丝为什么不能用铜丝代替", "空气开关跳闸怎么办",
      "保险丝装在火线还是零线", "什么是过载和短路", "漏电保护器和空气开关的区别"],
     ["问家庭电路布线规范", "问断路器选型参数"],
     "atomic", "",
     "保险丝=铅锑合金(阻大熔点低)串火线，Q=I²Rt 过流先熔断；铜丝代不得(熔点高失效)；空开=可复位断路器；漏电保护=RCD 防漏电不防过载。"),
    ("kp_card_dumpling",
     "煮饺子为什么要点凉水",
     "生活常识知识点内容（人话接口）", "生活常识",
     "煮饺子「三滚饺子两滚面」点凉水的道理：水沸腾后饺子皮熟得快、馅（尤其肉"
     "馅）熟得慢——一直大火沸滚，皮会胀破而馅还生。点入凉水让水暂时停止沸腾降"
     "温：①皮经历过「沸—凉—沸」反复收缩膨胀更筋道不易破；②传热更均匀，馅有"
     "时间熟透；③防止沸水溢锅。饺子浮起不代表熟透——只是气体受热膨胀使密度变"
     "小（生饺子也短暂浮起过），浮起后再点一两次凉水、馅熟才好吃。同类智慧：炖"
     "肉时小火慢炖让热量深入、煮鸡蛋水开转小火。",
     ["煮饺子为什么要加凉水", "饺子浮起来就熟了吗", "饺子皮为什么煮破了",
      "点几次凉水合适", "煮饺子大火还是小火", "什么是三滚饺子两滚面"],
     ["问面食和面技巧", "问其他烹饪控温案例"],
     "atomic", "",
     "点凉水=控温让馅熟透皮不破：沸腾降温反复使皮筋道+防溢锅；饺子浮起≠熟透(气体膨胀密度小)，浮起后再点凉水。"),
    ("kp_card_jianzhen",
     "鉴真东渡",
     "人文通识知识点内容（人话接口）", "历史",
     "鉴真（688-763）：唐代高僧，应日本留学僧荣叡、普照礼请，决心东渡日本传播"
     "佛法——自 743 年起六次东渡，前五次均失败（风浪/官府阻拦/双目失明），尤以"
     "第五次最惨：漂流到海南岛，历时两年辗转回扬州，双目失明仍不改初心；753 年"
     "第六次终于成功抵达日本鹿儿岛。他在日本：传授戒律（在东大寺设戒坛，为圣武"
     "天皇等授戒，是日本律宗初祖）、创建唐招提寺（至今犹存）、带去佛经/医药/建"
     "筑/书法知识（日本医药界曾奉为始祖）。鉴真与玄奘并称：一个西行求法、一个"
     "东渡传法，是唐代中外文化交流的双向象征。1963 年中日双方纪念其圆寂 1200 "
     "周年，唐招提寺鉴真干漆坐像为国宝，1980 年曾回国「探亲」巡展。",
     ["鉴真东渡去了哪里", "鉴真几次东渡才成功", "唐招提寺是谁建的",
      "鉴真和玄奘有什么不同", "鉴真对日本有什么贡献", "鉴真双目为什么失明"],
     ["问日本律宗传承", "问遣唐使制度"],
     "atomic", "",
     "鉴真：六次东渡(前五败·双目失明)753 年成功抵日；创唐招提寺·日本律宗初祖·传医药建筑；与西行求法的玄奘并称双向交流。"),
    ("kp_card_fourclassics",
     "中国古典四大名著",
     "人文通识知识点内容（人话接口）", "语文",
     "中国古典四大名著：①《三国演义》——罗贯中（元末明初），描写东汉末三国争"
     "雄，「桃园三结义」「三顾茅庐」「草船借箭」，中国第一部长篇章回体历史演义"
     "小说；②《水浒传》——施耐庵（元末明初），北宋宋江起义故事，「逼上梁山」"
     "一百单八将；③《西游记》——吴承恩（明代），玄奘取经神魔化，「大闹天宫」"
     "师徒四人八十一难；④《红楼梦》——曹雪芹（清代），贾宝玉林黛玉爱情悲剧与"
     "四大家族兴衰，「满纸荒唐言一把辛酸泪」，被誉为中国古典小说巅峰（红学）。"
     "常考搭配：作者朝代+核心人物+经典情节。《金瓶梅》不在四大名著之列。",
     ["四大名著是哪四部", "三国演义的作者是谁", "红楼梦是谁写的",
      "西游记取经的原型是谁", "水浒传讲的是什么故事", "中国第一部长篇章回体小说"],
     ["问四大名著成书年代争议", "问各名著影视改编"],
     "atomic", "",
     "四大名著：三国演义(罗贯中·元末明初)+水浒传(施耐庵)+西游记(吴承恩·明·玄奘取经原型)+红楼梦(曹雪芹·清·古典巅峰/红学)。"),
]

QUESTIONS = [
    ("QB-277", "保险丝为什么能保护电路", "物理学", "技术直答",
     ["熔点低", "熔断"], "通识拓展36"),
    ("QB-278", "煮饺子为什么要加凉水", "生活常识", "技术直答",
     ["馅熟透", "皮不破"], "通识拓展36"),
    ("QB-279", "鉴真东渡去了哪里", "历史", "技术直答",
     ["日本"], "通识拓展36"),
    ("QB-280", "四大名著是哪四部", "语文", "技术直答",
     ["三国演义", "水浒传", "西游记", "红楼梦"], "通识拓展36"),
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
                               "level:L2", "status:verified", "batch:通识拓展36"],
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
    bank["version"] = "v1.28"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
