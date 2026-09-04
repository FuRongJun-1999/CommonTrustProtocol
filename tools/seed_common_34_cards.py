# -*- coding: utf-8 -*-
"""seed_common_34_cards.py · 通识拓展批次34知识卡+题库（幂等）

34：物理学-平面镜成像/生活常识-溺水施救/历史-康熙帝/音乐-五线谱
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_mirror",
     "平面镜成像的特点",
     "基础科学知识点内容（人话接口）", "物理学",
     "平面镜成像四特点：像是虚像（不是实际光线会聚，光屏接不到）、与物等大、"
     "与物到镜面距离相等（物像对称于镜面）、左右相反（你举右手镜中人举的是"
     "「左手」）。原理是光的反射：物体发出的光经镜面反射进入眼睛，反向延长线"
     "「会聚」成虚像。应用：穿衣镜/ dental 检查口镜/潜望镜（两块平行平面镜两"
     "次反射改变光路）/楼道转角反光镜。凸面镜（汽车后视镜/路口广角镜）发散发"
     "大视野；凹面镜会聚（太阳灶/手电筒反光碗）——它们成的像与平面镜不同。",
     ["平面镜成像有什么特点", "平面镜成的是实像还是虚像", "为什么镜子里左右是反的",
      "潜望镜的原理", "汽车后视镜为什么用凸面镜", "太阳灶用什么镜子"],
     ["问光的反射定律角度计算", "问球面镜成像公式"],
     "atomic", "",
     "平面镜成像=虚像·等大·等距·左右反（光的反射）；潜望镜=双平面镜；凸面镜扩大视野·凹面镜会聚(太阳灶)。"),
    ("kp_card_drowning",
     "溺水施救的正确步骤",
     "生活常识知识点内容（人话接口）", "生活常识",
     "发现有人溺水，第一原则是「叫、伸、抛、划」不盲目下水：①大声呼救并拨打 "
     "110/120 报警求助；②岸上施救优先——伸竹竿/树枝（趴低重心递给落水者）或"
     "抛救生圈/泡沫板/空塑料瓶等漂浮物；③不谙水性或情况不明时绝不贸然下水，"
     "会游泳者也应从背后接近（避免被抱住），从背后托腋下侧游回岸。救上岸后：清"
     "理口鼻异物、判断呼吸心跳，无呼吸立即心肺复苏（胸外按压+人工呼吸）并持续"
     "到救援到达。预防永远第一：不到野泳水域、不逞强救人、同伴落水先呼救而非手"
     "拉手下水（链条式溺亡多因此发生）。",
     ["发现有人溺水第一步做什么", "不会游泳能救人吗", "溺水者救上岸后怎么处理",
      "手拉手救人为什么危险", "什么是叫伸抛划", "溺水心肺复苏怎么做"],
     ["问心肺复苏按压标准细节", "问水上安全装备"],
     "atomic", "",
     "溺水施救=叫伸抛划不盲目下水：呼救报警→岸上递竿抛浮物→背后接近；上岸后清口鼻+无呼吸即CPR；手拉手下水=链条式溺亡。"),
    ("kp_card_kangxi",
     "康熙帝：在位最久的皇帝",
     "人文通识知识点内容（人话接口）", "历史",
     "康熙帝（爱新觉罗·玄烨，1654-1722）是清朝入关后第二位皇帝，8 岁即位、14 "
     "岁亲政，在位 61 年（1661-1722），是中国历史上在位时间最长的皇帝。主要功"
     "绩：16 岁智擒权臣鳌拜亲政；平定三藩之乱（吴三桂等）；1683 年收复台湾（设"
     "台湾府隶属福建省）；抗击沙俄签订《尼布楚条约》（1689，第一个平等边界条"
     "约）；三征噶尔丹稳定漠西蒙古；治理黄河、推行「滋生人丁永不加赋」。文化上"
     "组织编纂《康熙字典》；对西方科学兴趣浓厚（向南怀仁学几何）。晚年九子夺嫡，"
     "传位第四子胤禛即雍正帝。其孙乾隆在位 60 年（禅位后仍掌权），祖孙缔造「康"
     "乾盛世」。",
     ["在位时间最长的皇帝是谁", "康熙帝的主要功绩", "智擒鳌拜的是谁",
      "尼布楚条约是谁签订的", "康乾盛世指什么", "康熙字典是谁组织编纂的"],
     ["问雍正夺嫡细节", "问清朝皇帝世系"],
     "atomic", "",
     "康熙玄烨：8岁即位·在位61年(1661-1722)最长；擒鳌拜/平三藩/收台湾/签尼布楚/征噶尔丹/编康熙字典；康乾盛世。"),
    ("kp_card_staff",
     "五线谱基础",
     "人文通识知识点内容（人话接口）", "音乐",
     "五线谱是世界通用的记谱法：五条等距平行线组成，线与线之间的四个空隙叫"
     "「间」——自下而上数（第一条线在最下），共五线四间；音符记在线或间上，位"
     "置越高音越高。谱号决定唱名：高音谱号（G 谱号）第二线定为 g1；低音谱号（F "
     "谱号）第四线为 f。附点、升降号（♯升半音/♭降半音）、拍号（如 4/4 拍=以四"
     "分音符为一拍每小节四拍）共同决定节奏与音高变化。中国传统的工尺谱/简谱"
     "（1234567 记谱）在民间与音乐教育中也广泛使用——简谱用数字+高低音点/下"
     "划线记谱，五线谱则能更直观呈现音高空间关系与和声。",
     ["五线谱有几条线", "五线谱怎么数线和间", "高音谱号是什么", "什么是4/4拍",
      "升号和降号是什么意思", "简谱和五线谱的区别"],
     ["问识谱训练方法", "问其他记谱法历史"],
     "atomic", "",
     "五线谱=5线4间自下而上·位置越高音越高；高音G谱号二线为g1/低音F谱号；♯♭升降半音；拍号4/4=四分音符一拍·每小节四拍。"),
]

QUESTIONS = [
    ("QB-269", "平面镜成像有什么特点", "物理学", "技术直答",
     ["虚像", "等大", "等距"], "通识拓展34"),
    ("QB-270", "发现有人溺水第一步做什么", "生活常识", "技术直答",
     ["呼救", "报警"], "通识拓展34"),
    ("QB-271", "在位时间最长的皇帝是谁", "历史", "技术直答",
     ["康熙", "61年"], "通识拓展34"),
    ("QB-272", "五线谱有几条线", "音乐", "技术直答",
     ["5条", "五条"], "通识拓展34"),
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
                               "level:L2", "status:verified", "batch:通识拓展34"],
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
    bank["version"] = "v1.26"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
