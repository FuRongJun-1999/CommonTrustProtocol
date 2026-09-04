# -*- coding: utf-8 -*-
"""seed_common_30_cards.py · 通识拓展批次30知识卡+题库（幂等）

30：化学-合金/地理学-长江黄河之源/生物学-植物向光性/数学-圆的面积
KCCS 四要素+题干原句触发词。出卡前按 id 查库防撞——本批预检命中
kp_card_probability 撞 id（夜间v0.2旧卡已覆盖概率且内容正确），故数学题改圆的面积。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_alloy",
     "合金与纯金属的区别",
     "基础科学知识点内容（人话接口）", "化学",
     "合金是在金属中加热熔合其他金属或非金属制成的混合物：钢（铁+碳）、黄铜"
     "（铜+锌）、青铜（铜+锡）、焊锡（锡+铅）、不锈钢（铁+铬+镍）。合金的通性"
     "与纯金属相比：硬度一般更大（纯铝软，硬铝可用于航空）、熔点一般更低（焊锡"
     "熔点低于纯锡铅，便于焊接）、抗腐蚀性常更好（不锈钢防锈）。因为成分比例可"
     "调，合金性能「可设计」——钛合金轻强耐蚀用于飞机与人工关节。生铁和钢都是"
     "铁碳合金，区别在含碳量（生铁高脆、钢韧）。",
     ["合金和纯金属有什么区别", "不锈钢是什么合金", "黄铜和青铜的成分",
      "生铁和钢的区别", "焊锡为什么比纯锡熔点低", "钛合金用在哪里"],
     ["问金属晶体结构", "问冶炼工艺细节"],
     "atomic", "",
     "合金=金属熔合混合物：硬度更大/熔点更低/更耐蚀(可设计)；钢=铁+碳，生铁碳高脆·钢韧；不锈钢=铁铬镍。"),
    ("kp_card_cjhh",
     "长江与黄河",
     "人文通识知识点内容（人话接口）", "地理学",
     "长江与黄河都发源于青藏高原，被并称为中国的「母亲河」。长江：发源于唐古拉"
     "山脉（各拉丹冬雪峰），全长约 6300 公里，中国第一、世界第三长河；上中下游"
     "分界：宜昌、湖口；流经 11 个省级行政区，注入东海；干流航运发达，被誉为"
     "「黄金水道」，三峡工程在其上游。黄河：发源于巴颜喀拉山脉，全长约 5464 公"
     "里，中国第二长河；上中下游分界：河口、桃花峪；注入渤海；中游流经黄土高原"
     "携带大量泥沙（世界上含沙量最大的河），下游泥沙淤积形成「地上河」（悬河），"
     "治理关键在治沙（中游水土保持）。",
     ["长江和黄河都发源于哪个高原", "长江发源于哪座山脉", "黄河为什么是黄色的",
      "什么是地上河", "黄金水道指哪条河", "长江上中下游的分界点"],
     ["问南水北调", "问各河流经省份细节"],
     "atomic", "",
     "长江(唐古拉山·6300km·东海·黄金水道)与黄河(巴颜喀拉山·5464km·渤海·含沙量最大/下游地上河)同源青藏高原；治黄=中游水土保持。"),
    ("kp_card_phototropism",
     "植物的向光性",
     "基础科学知识点内容（人话接口）", "生物学",
     "植物朝着光的方向弯曲生长叫向光性：单侧光照射使幼苗尖端产生的生长素向背光"
     "一侧运输集中，背光侧生长素多、细胞伸长快，茎就向光弯曲——「想晒太阳」的"
     "本质是激素分布不均。类似的向性运动还有：根的向地性（重力使生长素下侧集中，"
     "根对它敏感反而长得慢→向下扎）、含羞草的感震性（叶枕细胞失水膨胀压变化，"
     "属于感性运动，与方向无关）。窗台上的盆花定期转盆才能长得匀称，就是克服向"
     "光性造成的偏冠。",
     ["植物为什么向着阳光生长", "什么是向光性", "生长素有什么作用",
      "根为什么向下长", "含羞草为什么会合拢", "盆花为什么要转盆"],
     ["问生长素发现史实验", "问顶端优势应用"],
     "atomic", "",
     "向光性=单侧光→生长素背光侧集中→茎向光弯；根向地性向下扎；含羞草=感性运动；转盆防偏冠。"),
    ("kp_card_circlearea",
     "圆的周长与面积",
     "基础科学知识点内容（人话接口）", "数学",
     "圆的基本公式（半径 r，直径 d=2r）：周长 C = πd = 2πr；面积 S = πr²。例："
     "半径 3 厘米的圆，周长=2×3.14×3≈18.84 厘米，面积=3.14×9≈28.26 平方厘米——"
     "注意周长单位是长度、面积单位是平方，两者不能比大小（单位不同的量无法比"
     "较，是常见易错点）。相关概念：圆周率 π 是周长与直径的比（祖冲之将其精确"
     "到小数点后 7 位）；半圆的周长要加上直径（πr+2r）；环形的面积=大圆面积−小"
     "圆面积（πR²−πr²）。",
     ["圆的面积怎么算", "圆的周长公式", "半径3厘米的圆面积是多少",
      "半圆的周长怎么算", "环形面积怎么求", "圆周率和圆面积的关系"],
     ["问扇形面积弧长", "问圆柱圆锥体积"],
     "atomic", "",
     "圆：C=2πr=πd；S=πr²；半圆周长=πr+2r；环形=π(R²−r²)；周长与面积单位不同不可比。"),
]

QUESTIONS = [
    ("QB-253", "合金和纯金属有什么区别", "化学", "技术直答",
     ["硬度", "熔点"], "通识拓展30"),
    ("QB-254", "长江和黄河都发源于哪个高原", "地理学", "技术直答",
     ["青藏高原"], "通识拓展30"),
    ("QB-255", "植物为什么向着阳光生长", "生物学", "技术直答",
     ["生长素", "向光性"], "通识拓展30"),
    ("QB-256", "圆的面积怎么算", "数学", "技术直答",
     ["πr²", "派r方"], "通识拓展30"),
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
                               "level:L2", "status:verified", "batch:通识拓展30"],
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
    bank["version"] = "v1.22"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
