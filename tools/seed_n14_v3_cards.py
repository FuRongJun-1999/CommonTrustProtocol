# -*- coding: utf-8 -*-
"""seed_n14_v3_cards.py · 知识域拓展第八批知识卡（幂等）

夜批N14：数学-百分数/语文-标点符号/安全-用电安全/历史-丝绸之路 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_percent",
     "百分数",
     "基础科学知识点内容（人话接口）", "数学",
     "百分数（百分比）：表示一个数是另一个数的百分之几的数，用 % 号表示——"
     "百分数只表示比例关系，不带单位。换算：50% = 0.5 = 一半；百分数转小数去"
     "掉 % 号小数点左移两位。常见应用：折扣（七折=原价的 70%）、增长率、合格"
     "率。注意百分数不能相加超过 100% 除非表示增长率（增长率可以超过 100%）。",
     ["什么是百分数", "百分数", "百分数怎么算", "折扣怎么计算",
      "百分数和小数怎么换算", "百分数表示什么"],
     ["问利率计算", "问统计图表"],
     "atomic", "",
     "百分数 = 一个数占另一个数的百分之几（%）；折扣/增长率常用；换算：去 % 小数点左移两位。"),
    ("kp_card_punctuation",
     "常用标点符号的用法",
     "基础科学知识点内容（人话接口）", "语文",
     "常用标点符号用法：句号（陈述句末尾）、问号（疑问句末尾）、叹号（感叹/祈"
     "使句末尾）、逗号（句内停顿）、顿号（并列词语之间的停顿，比逗号短）、冒号"
     "（提示下文）、分号（并列分句之间）、引号（引用/特殊含义）、书名号《》（书"
     "籍文章名）。标点是文字的呼吸——用错会改变句意（如「下雨天留客天」的经典"
     "断句歧义）。",
     ["常用标点符号的用法", "标点符号", "顿号和逗号的区别", "冒号怎么用",
      "书名号什么时候用", "问标点"],
     ["问修辞手法", "问病句修改"],
     "atomic", "",
     "标点 = 句号/问号/叹号（句末）+ 逗号/顿号（停顿长短）+ 冒号（提示）+ 引号书名号（标示）。"),
    ("kp_card_electricsafety",
     "安全用电常识",
     "生活常识知识点内容（人话接口）", "安全用电",
     "安全用电常识：不用湿手触摸开关和电器（水导电）；电器着火先断电、不能直接"
     "泼水；不超负荷用电（一个插排不要插太多大功率电器）；发现电线破损及时更换"
     "；雷雨天不站在大树下、不使用室外天线。触电急救：先切断电源或用干燥木棍挑"
     "开电线，绝不能直接用手拉触电者。",
     ["安全用电常识", "怎么安全用电", "湿手能不能碰开关", "电器着火怎么办",
      "有人触电怎么急救", "安全用电"],
     ["问灭火器选用", "问雷电防护"],
     "atomic", "",
     "安全用电 = 不用湿手/不超负荷/电器火先断电；触电急救先断电源或用干木棍挑开，绝不能直接拉。"),
    ("kp_card_silkroad",
     "丝绸之路",
     "人文通识知识点内容（人话接口）", "历史",
     "丝绸之路：汉代张骞出使西域（公元前 138 年起两次）后开通的连接中国与中亚、"
     "西亚直至欧洲的陆上贸易通道——中国输出丝绸、瓷器、茶叶，输入汗血宝马、香料、"
     "玻璃与宗教文化（佛教沿此东传）。海上丝绸之路则经南海印度洋通向波斯湾与红海"
     "。丝绸之路不仅是商路，更是东西方文明交流的桥梁。",
     ["什么是丝绸之路", "丝绸之路", "张骞出使西域", "丝绸之路的起点和终点",
      "丝绸之路有什么作用", "谁开通了丝绸之路"],
     ["问郑和下西洋", "问唐朝对外交流"],
     "atomic", "",
     "丝绸之路 = 张骞凿空后开通的东西方通道；丝绸瓷器茶叶西去、佛教文化东来——文明交流的桥梁。"),
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
                               "level:L2", "status:verified", "batch:拓展第八批"],
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
