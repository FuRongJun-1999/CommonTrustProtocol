# -*- coding: utf-8 -*-
"""seed_common_44_cards.py · 通识拓展批次44知识卡+题库（幂等）

44：物理学-滑轮/化学-碳酸饮料/生物学-心脏的位置/历史-中国古代四大美女
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_pulley",
     "定滑轮与动滑轮",
     "基础科学知识点内容（人话接口）", "物理学",
     "滑轮是绕轴转动的轮子（边缘有槽可绕绳）：①定滑轮——轴固定不动（旗杆顶端"
     "/窗帘滑轮）：不省力也不费力，但能改变力的方向（向下拉绳旗帜向上升）；②动"
     "滑轮——轴随物体一起移动（起重机吊钩组）：省一半力（F=G/2，不计轮重与摩"
     "擦），但费距离（绳端移动 2 倍距离）且不能改变方向；③滑轮组——定滑轮+动滑"
     "轮组合：既省力又能改变方向，几段绳子承担重物就省几分之一力（F=G/n）。原理"
     "都是杠杆的变形（定滑轮=等臂杠杆，动滑轮=动力臂为阻力臂 2 倍的杠杆）。代价"
     "意识：省力必费距离——功的原理（使用任何机械都不省功）。",
     ["动滑轮有什么好处", "定滑轮和动滑轮的区别", "旗杆顶端的滑轮是什么滑轮",
      "滑轮组怎么省力", "使用机械能省功吗", "为什么动滑轮省一半力"],
     ["问斜面省力计算", "问轮轴应用"],
     "atomic", "",
     "定滑轮=不省力改方向(旗杆)；动滑轮=省一半力费两倍距离；滑轮组 F=G/n 既省力又改向；本质=杠杆变形；省力必费距离·不省功。"),
    ("kp_card_soda",
     "碳酸饮料里的气泡",
     "基础科学知识点内容（人话接口）", "化学",
     "可乐/汽水里的气泡是二氧化碳（CO₂）：工厂在高压下把 CO₂ 溶进水里（气体的"
     "溶解度随压强增大而升高、随温度升高而降低）——开瓶的「呲」声是压强骤降，"
     "CO₂ 溶解度瞬间下降，多余的气体以气泡形式涌出；喝进肚里气体排出带走热量，"
     "所以「透心凉」（也是打嗝的原因）。摇晃瓶身会让气泡附着在瓶壁，开瓶更易喷"
     "溅。长期大量饮用碳酸饮料的问题：糖分高（肥胖/龋齿）、碳酸+磷酸影响钙吸收"
     "（增加骨质疏松风险）、胃酸多者胀气。同类原理：啤酒泡沫、香槟开瓶、家里自制"
     "柠檬苏打水。",
     ["可乐里的气泡是什么气体", "为什么开可乐会冒泡", "摇晃过的汽水为什么容易喷",
      "碳酸饮料为什么喝着凉", "碳酸饮料喝多了有什么坏处", "气体溶解度和温度的关系"],
     ["问溶解度曲线", "问无糖碳酸饮料"],
     "atomic", "",
     "汽水气泡=CO₂(高压溶解)；开瓶压强骤降→溶解度下降→气泡涌出；降温增溶；风险=高糖/影响钙吸收/胀气；摇晃=气泡核增多易喷。"),
    ("kp_card_heartpos",
     "心脏的位置与大小",
     "基础科学知识点内容（人话接口）", "生物学",
     "心脏位于胸腔中部、两肺之间、略偏左（2/3 在身体中线左侧）——「心在左边」"
     "是俗话的近似说法，准确说是中纵隔内偏左。大小约与自己的拳头相当（成年人心"
     "脏约 250-300 克）。结构：四个腔（左心房/左心室/右心房/右心室），同侧房室"
     "相通、房连静脉室连动脉——血液循环分体循环（左心室→全身→右心房）和肺循环"
     "（右心室→肺→左心房）。心脏是「不停工的泵」：一生跳动约 25-30 亿次，每次"
     "搏动把血液泵向全身（心率正常静息约 60-100 次/分）。心跳声「扑通」=瓣膜关"
     "闭的声音。",
     ["心脏在人体的哪个位置", "心脏有多大", "心脏有四个腔吗",
      "什么是体循环和肺循环", "正常心率是多少", "心跳的声音是怎么来的"],
     ["问心电图原理", "问冠脉循环"],
     "atomic", "",
     "心脏=胸腔中部两肺间略偏左(2/3 在左)·拳头大(250-300g)；四腔：房连静脉室连动脉；体循环(左室→全身)+肺循环(右室→肺)；一生跳 25-30 亿次。"),
    ("kp_card_beauties",
     "中国古代四大美女",
     "人文通识知识点内容（人话接口）", "历史",
     "中国古代四大美女（对应四美典故）：①西施（春秋·越国）——「沉鱼」（浣纱时"
     "鱼见之沉入水底），越王勾践献吴王夫差的美人计主角；②王昭君（西汉）——「落"
     "雁」（出塞和亲匈奴呼韩邪单于，昭君出塞促进汉匈和平）；③貂蝉（东汉·《三国"
     "演义》人物，正史无载）——「闭月」（司徒王允连环计离间董卓吕布）；④杨玉环"
     "（唐朝）——「羞花」（赏花时花叶卷合的传说），唐玄宗宠妃，安史之乱中马嵬驿"
     "被赐死，白居易《长恨歌》「在天愿作比翼鸟」写她。成语串记：沉鱼落雁、闭月羞"
     "花。注意貂蝉是文学虚构人物，其余三位有史可考。",
     ["中国古代四大美女是谁", "沉鱼落雁闭月羞花分别指谁", "昭君出塞嫁给了谁",
      "貂蝉是真实历史人物吗", "长恨歌写的是谁", "西施是哪个朝代的"],
     ["问四大美人的结局对比", "问古代和亲史"],
     "atomic", "",
     "四大美女：西施(沉鱼·越)/王昭君(落雁·汉·出塞)/貂蝉(闭月·演义虚构)/杨玉环(羞花·唐·长恨歌)；貂蝉无正史载。"),
]

QUESTIONS = [
    ("QB-309", "动滑轮有什么好处", "物理学", "技术直答",
     ["省力", "省一半力"], "通识拓展44"),
    ("QB-310", "可乐里的气泡是什么气体", "化学", "技术直答",
     ["二氧化碳"], "通识拓展44"),
    ("QB-311", "心脏在人体的哪个位置", "生物学", "技术直答",
     ["胸腔", "偏左"], "通识拓展44"),
    ("QB-312", "中国古代四大美女是谁", "历史", "技术直答",
     ["西施", "王昭君", "貂蝉", "杨玉环"], "通识拓展44"),
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
                               "level:L2", "status:verified", "batch:通识拓展44"],
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
    bank["version"] = "v1.36"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
