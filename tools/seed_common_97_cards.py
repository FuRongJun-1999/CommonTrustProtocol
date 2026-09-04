# -*- coding: utf-8 -*-
"""seed_common_97_cards.py · 通识拓展批次97知识卡+题库（幂等）

97：物理学-无线电通信/化学-氧化还原反应/生物学-动物的行为/地理学-铁路干线
KCCS 四要素+题干原句触发词。出卡前先按 id 查库防撞。
"""
import json
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_radiocm",
     "无线电波传递信息的原理",
     "基础科学知识点内容（人话接口）", "物理学",
     "无线电通信的链路：①**调制**——把声音/图像等低频信号「装载」到高频载波上"
     "（调幅 AM=让载波振幅随信号变；调频 FM=让载波频率随信号变——FM 抗干扰强"
     "音质好）；②天线发射高频电磁波；③接收端天线捕捉电波；④**解调**（检波）——"
     "从载波上「卸下」信号还原成声音图像。就像：货物（信号）装上卡车（载波）运"
     "输再卸货。手机/WiFi/蓝牙/广播/电视/卫星导航全是这一原理的不同频段应用。频"
     "谱是稀缺资源（各国统一分配——5G 用更高频段带宽更大）。电磁波的发射需要开"
     "放电路（天线），频率越高越容易有效发射。",
     ["无线电波怎么传递信息", "什么是调制和解调", "调幅和调频的区别",
      "手机通信的原理", "5G为什么用更高频段", "载波是什么"],
     ["问数字调制 QAM", "问频谱分配制度"],
     "atomic", "",
     "无线电链路=调制(信号装载波·AM 幅/FM 频)→天线发射→接收→解调(卸货)；类比货装卡车运输；手机/WiFi/北斗皆同原理异频段；频谱稀缺统一分配。"),
    ("kp_card_redox",
     "氧化还原反应：得失氧与电子转移",
     "基础科学知识点内容（人话接口）", "化学",
     "氧化还原反应的本质是**电子转移**（初中学段从「得失氧」入门）：初定义——"
     "得到氧的反应叫氧化反应（被氧化），失去氧的反应叫还原反应（被还原）；两者"
     "同时发生（有失必有得）。例：H₂+CuO→(Δ)Cu+H₂O——H₂ 得氧被氧化（还原剂），"
     "CuO 失氧被还原（氧化剂）。进阶本质：电子得失/偏移——失电子者被氧化（是还"
     "原剂），得电子者被还原（是氧化剂）。记忆口诀：「升失氧、降得还」——化合价"
     "升高、失电子、被氧化、是还原剂。应用：炼铁（CO 还原氧化铁）、呼吸作用（葡"
     "萄糖被氧化供能）、电池（负极氧化正极还原）、燃烧与防腐蚀本质都是氧化还原。",
     ["什么是氧化还原反应", "氧化反应和还原反应的关系", "还原剂是被氧化还是被还原",
      "升失氧降得还是什么意思", "呼吸作用是氧化反应吗", "炼铁中什么是还原剂"],
     ["问化合价升降法配平", "问电化学衔接"],
     "atomic", "",
     "氧化还原=电子转移(初学从得失氧入门)：还原剂失电子被氧化、氧化剂得电子被还原——同时发生；口诀「升失氧降得还」；应用=炼铁/呼吸供能/电池/防腐。"),
    ("kp_card_animalbeh",
     "先天性行为与学习行为",
     "基础科学知识点内容（人话接口）", "生物学",
     "动物行为按获得途径分两类：①**先天性行为**（本能行为）——生来就有、由遗传"
     "物质决定（蜜蜂采蜜/蜘蛛结网/鸟类孵卵/婴儿吮吸/缩手反射）——不需学习、适"
     "应相对稳定的环境；②**学习行为**（后天性行为）——在遗传因素基础上、通过环"
     "境因素作用由生活经验和学习获得（蚯蚓走 T 形迷宫、黑猩猩取香蕉、小狗算术、"
     "老马识途）——动物越高等学习能力越强（人类学习行为最复杂）。经典实验：绕道"
     "取食（蚯蚓要 200 多次尝试，黑猩猩几次即会）；劳伦兹「印随」（灰雁跟"
     "随出生后见到的移动物体）。意义：先天行为适应稳定环境，学习行为适应复杂多"
     "变环境。判断标准：看是否需要后天经验（与生俱来=先天性）。",
     ["动物行为分为哪两类", "什么是先天性行为", "学习行为的例子",
      "蚯蚓走迷宫实验", "动物越高等学习能力越强", "印随行为是谁发现的"],
     ["问三大行为辨析题", "问动物通讯行为复习"],
     "atomic", "",
     "行为两类：先天性=本能(遗传决定·蛛网吮吸)vs 学习=经验获得(迷宫·黑猩猩取食·老马识途)；越高等学习越强；绕道取食=蚯蚓 200 次/黑猩猩数次；劳伦兹印随。"),
    ("kp_card_railline",
     "中国主要铁路干线",
     "人文通识知识点内容（人话接口）", "地理学",
     "中国铁路干线「五纵三横」：**五纵（南北向）**——①京哈—京广线（北京→哈尔滨"
     "/北京→广州，经过石家庄郑州武汉长沙）；②京沪线（北京→上海，经天津济南南"
     "京）；③京九线（北京→香港九龙，经南昌）；④焦柳线（焦作→柳州）；⑤宝成—成"
     "昆线（宝鸡→成都→昆明）。**三横（东西向）**——①京包—包兰线；②陇海—兰新"
     "线（连云港→乌鲁木齐，第二亚欧大陆桥中国段）；③沪杭—浙赣—湘黔—贵昆线"
     "（上海→昆明，沪昆通道）。铁路命名：起点终点各取一字（京广=北京-广州、陇海"
     "=陇西-海州）。高铁时代「八纵八横」网：京沪/京广/哈大/沪昆等通道，复兴号"
     " 350km/h 商业运营世界最快。青藏铁路是世界海拔最高的铁路。",
     ["京广线连接哪两个城市", "五纵三横是什么", "陇海线的起止点",
      "京九线的终点是哪里", "高铁八纵八横", "铁路命名规则"],
     ["问枢纽城市郑州株洲", "问一带一路铁路通道"],
     "atomic", "",
     "五纵=京哈京广/京沪/京九/焦柳/宝成成昆；三横=京包包兰/陇海兰新(第二亚欧桥)/沪昆；命名=起讫城市各取一字；高铁八纵八横·复兴号 350km/h 世界最快。"),
]

QUESTIONS = [
    ("QB-521", "无线电波怎么传递信息", "物理学", "技术直答",
     ["调制", "载波", "解调"], "通识拓展97"),
    ("QB-522", "什么是氧化还原反应", "化学", "技术直答",
     ["电子转移", "得失氧"], "通识拓展97"),
    ("QB-523", "动物行为分为哪两类", "生物学", "技术直答",
     ["先天性", "学习行为"], "通识拓展97"),
    ("QB-524", "京广线连接哪两个城市", "地理学", "技术直答",
     ["北京", "广州"], "通识拓展97"),
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
                               "level:L2", "status:verified", "batch:通识拓展97"],
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
    bank["version"] = "v1.89"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
