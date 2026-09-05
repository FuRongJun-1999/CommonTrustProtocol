# -*- coding: utf-8 -*-
"""seed_common_164_cards.py · 通识拓展批次164知识卡+题库（幂等）

164：历史学-詹天佑与京张铁路/生活常识-拍照红眼成因/生物学-打哈欠传染
KCCS 四要素+题干原句触发词。三重预检：三主题双库零覆盖（苹果褐变/极昼极夜
命中已有卡弃选）。执行前外文长词检测（批次162教训固化）。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

NODES = [
    ("kp_card_zhantianyou",
     "詹天佑与京张铁路",
     "人文通识知识点内容（人话接口）", "历史学",
     "京张铁路（北京丰台—张家口）：**中国人自主勘察、设计、施工的第一条干线铁"
     "路**（1905-1909），总工程师**詹天佑**（「中国铁路之父」，首批留美幼童）"
     "。难关与巧思：①沿线八达岭段坡度极大；②**「人」字形线路**——在青龙桥设"
     "折返道岔，列车先上行再折返反向爬升，用延展距离化解高差（两台机车前拉后"
     "推）；③**竖井施工法**——八达岭隧道从中部凿竖井分四个工作面同时开凿，缩"
     "短工期；④提前两年完工、省银 28 万两（当时列强嘲笑「能修此路的中国工程"
     "师还没出生」）。纪念：青龙桥站詹天佑铜像与墓；2019 年智能高铁「京张高"
     "铁」（自动驾驶时速 350km）同线通车——百年跨越同一个起点。意义：粉碎「"
     "中国人不能自建铁路」的谬论，是中国近代工程自立的里程碑。",
     ["京张铁路是谁设计的", "詹天佑人字形铁路", "中国第一条自主建设的铁路",
      "竖井开凿法", "中国铁路之父", "京张高铁"],
     ["问高铁技术发展（用高铁卡）", "问清朝洋务运动（时代背景）"],
     "atomic", "",
     "京张铁路=1905-1909 詹天佑主持中国人自主设计施工首条干线（「中国铁路之父」首批留美幼童）：人字形线路折返爬坡化解八达岭大坡+竖井四工作面凿隧道，提前完工省银 28 万两；2019 京张智能高铁同线通车——百年跨越。"),
    ("kp_card_redeye",
     "拍照「红眼」的成因",
     "生活常识知识点内容（人话接口）", "生活常识",
     "「红眼」=闪光灯照片里人的瞳孔变成红色：①暗处**瞳孔放大**（让光多进眼）；"
     "②闪光瞬间来不及收缩，强光直射眼底，**视网膜上密布的血管**反射红光回到"
     "镜头——拍到的是眼底血管的「红」。③**防红眼**：相机「防红眼模式」=**先"
     "预闪数次**让瞳孔提前缩小再正式闪光；或开灯/让眼睛朝向光源旁、避开正对"
     "镜头；拍后软件也可检测矫正。动物「绿眼/蓝眼」同理但颜色不同——猫狗眼底"
     "有反光膜增强夜视，反光是亮绿/蓝色而不是红。健康提示：照片单眼固定发红，"
     "或儿童照片出现**白瞳**，须就医排查眼底疾病（白瞳症可能是严重眼病信号）。",
     ["拍照红眼是怎么形成的", "防红眼模式原理", "为什么晚上红眼更明显",
      "猫的眼睛为什么会反光", "瞳孔放大", "白瞳症"],
     ["问闪光灯使用技巧", "问儿童眼病筛查"],
     "atomic", "",
     "红眼=暗处瞳孔放大+闪光直射眼底视网膜血管反射红光；防红眼=预闪缩瞳/避正对镜头；猫狗绿眼=反光膜夜视增强非红；单眼固定红或儿童白瞳就医排查眼底。"),
    ("kp_card_yawn",
     "打哈欠为什么会传染",
     "基础科学知识点内容（人话接口）", "生物学",
     "打哈欠本身：深吸气+张口+短呼气，主流假说是**给大脑降温**（深吸入冷空气+"
     "拉伸下颌改变颅内血流——哈欠多发生在困倦/无聊时脑温偏高）与**唤醒调节**"
     "（困倦时提神）。**为什么会传染**：看到、听到甚至读到「打哈欠」都会触发"
     "——①**共情/镜像机制**（大脑运动皮层自动模仿他人动作；共情能力强者更易"
     "被传染——自闭谱系研究支持此说）；②**群体同步假说**（灵长类群体同时哈欠"
     "同步警觉水平，进化上利于集体警戒）；③研究趣闻：**狗看到人打哈欠也会打**"
     "（跨物种传染=共情线索）。读到这里 50-70% 的人已经打了哈欠——传染不分"
     "线上线下。打哈欠是正常生理反射，无需憋忍。",
     ["打哈欠为什么会传染", "打哈欠的作用", "共情传染",
      "镜像神经元", "狗会传染打哈欠吗"],
     ["问睡眠卫生（用睡眠卡）", "问动物行为学"],
     "atomic", "",
     "哈欠假说=大脑降温+唤醒调节；传染性=共情镜像机制（共情强者易被传）+群体同步警戒假说；狗看人打哈欠也打=跨物种共情线索；打哈欠是生理反射无需憋忍。"),
]

QUESTIONS = [
    ("QB-747", "京张铁路的总工程师是谁？「人」字形线路是怎么解决八达岭大坡度问题的？", "历史学", "技术直答",
     ["詹天佑", "折返", "爬坡", "两台机车", "青龙桥"], "通识拓展164"),
    ("QB-748", "拍照开闪光灯为什么会出现「红眼」？相机的防红眼功能是怎么工作的？", "生活常识", "技术直答",
     ["视网膜", "血管", "反射", "瞳孔", "预闪"], "通识拓展164"),
    ("QB-749", "打哈欠为什么会传染？目前科学上有哪些解释假说？", "生物学", "技术直答",
     ["共情", "镜像神经元", "传染", "大脑降温", "群体同步"], "通识拓展164"),
]


def foreign_word_check() -> None:
    """批次162事故教训：检测内容中混入的非预期外文长词（西里尔/连续长英文）。"""
    problems = []
    for node in NODES:
        content = node[4]
        cyr = re.findall(r"[\u0400-\u04FF]+", content)
        if cyr:
            problems.append((node[0], f"西里尔字符: {cyr[:2]}"))
        for word in re.findall(r"[A-Za-z]{6,}", content):
            problems.append((node[0], f"长英文词: {word}"))
    if problems:
        raise SystemExit(f"外文长词检测报警: {problems}")


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
                               "level:L2", "status:verified", "batch:通识拓展164"],
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
    bank["version"] = "v4.37"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    foreign_word_check()
    print("外文词检测通过")
    print(json.dumps(ensure_seed(), ensure_ascii=False))
