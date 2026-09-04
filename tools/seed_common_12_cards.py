# -*- coding: utf-8 -*-
"""seed_common_12_cards.py · 通识拓展批次知识卡（幂等）

12：文学-修辞手法/艺术-中国书法/体育-常见球类规则/天文学-恒星与星座
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_rhetoric",
     "常见的修辞手法",
     "基础科学知识点内容（人话接口）", "文学",
     "常见修辞手法：比喻（用相似事物打比方——分明喻/暗喻/借喻）；拟人（把物当"
     "人写，如春风抚摸脸庞）；夸张（故意夸大或缩小，如飞流直下三千尺）；排比"
     "（三个以上结构相似的句子并列，增强气势）；对偶（字数相等结构对称，如两"
     "个黄鹂鸣翠柳一行白鹭上青天）；反问（用疑问形式表达确定意思）；设问（自"
     "问自答引起注意）。",
     ["常见的修辞手法", "什么是比喻", "什么是拟人", "夸张和排比",
      "修辞手法有哪些", "对偶和排比的区别"],
     ["问病句修改", "问文言文修辞"],
     "atomic", "",
     "修辞手法 = 比喻/拟人/夸张/排比/对偶/反问/设问等，核心作用=增强表达效果。"),
    ("kp_card_chinesecalligraphy",
     "中国书法",
     "人文通识知识点内容（人话接口）", "艺术",
     "中国书法是汉字的书写艺术，五大书体：篆书（最古老，秦代官方文字，线条圆"
     "转均匀）、隶书（汉代，蚕头燕尾一波三折）、楷书（唐代鼎盛，端正规范——欧"
     "体/颜体/柳体/赵体四大楷书家）、行书（介于楷草之间，王羲之《兰亭序》天下"
     "第一行书）、草书（张旭/怀素狂放不羁）。文房四宝=笔墨纸砚。",
     ["中国书法", "书法五大书体", "王羲之的兰亭序", "什么是文房四宝",
      "楷书四大家是谁", "中国书法艺术"],
     ["问国画", "问篆刻"],
     "atomic", "",
     "书法五体 = 篆→隶→楷→行→草；王羲之《兰亭序》=天下第一行书；文房四宝=笔墨纸砚。"),
    ("kp_card_ballsports",
     "常见球类运动的基本规则",
     "基础科学知识点内容（人话接口）", "体育学",
     "常见球类运动规则要点：足球=每队11人、除守门员外不得手触球、进球多者胜；"
     "篮球=每队5人、将球投入对方篮筐得分、NBA每节12分钟FIBA每节10分钟；排球="
     "每队6人、最多触球3次过网（拦网不算）、落地得分。乒乓球=11分制每2球换发、"
     "10平后领先2分获胜。",
     ["常见球类运动的规则", "足球篮球排球规则", "足球每队几个人", "排球最多触球几次",
      "乒乓球怎么计分", "篮球比赛时间"],
     ["问田径运动", "问游泳规则"],
     "atomic", "",
     "足球11人/篮球5人/排球6人；乒乓球11分制；排球最多触3次（拦网不算）；足球除守门员外禁手。"),
    ("kp_card_constellation",
     "星座与星空观测",
     "基础科学知识点内容（人话接口）", "天文学",
     "星座与星空观测：国际天文学联合会（IAU）将全天划分为88个星座——黄道十二"
     "星座（太阳在一年中经过的星座，即出生时的太阳星座）。北极星（勾陈一）位"
     "于小熊座尾端，通过北斗七星斗口两星连线延长约5倍距离即可找到——始终指示"
     "正北方向，是夜间导航的重要参照。最亮的恒星是天狼星（大犬座）。",
     ["星座", "88个星座", "怎么找北极星", "北斗七星和北极星",
      "黄道十二星座", "最亮的恒星是哪个"],
     ["问行星运动", "问星云"],
     "atomic", "",
     "全天88星座；北极星（小熊座尾端）指示正北——用北斗七星斗口两星连线5倍找；最亮恒星=天狼星。"),
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
                               "level:L2", "status:verified", "batch:通识拓展12"],
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
    return {"inserted": inserted, "updated": updated, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
