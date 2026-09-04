# -*- coding: utf-8 -*-
"""seed_common_04_cards.py · 通识拓展批次知识卡（幂等）

04：化学-金属活动性顺序/生物-遗传与变异/历史-丝绸之路/计算机-算法复杂度
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_metalactivity",
     "金属活动性顺序",
     "基础科学知识点内容（人话接口）", "化学",
     "金属活动性顺序（由强到弱）：钾钙钠镁铝、锌铁锡铅氢、铜汞银铂金——排在氢"
     "前面的金属能置换出酸中的氢（如锌+稀硫酸→硫酸锌+氢气），排在氢后面的不能"
     "；排在前面的金属能把排在后面的金属从其盐溶液中置换出来（如铁+硫酸铜→硫"
     "酸亚铁+铜）。活动性差异源于金属原子失去最外层电子的难易程度。",
     ["金属活动性顺序", "金属活动性", "钾钙钠镁铝", "金属活动性顺序表",
      "哪些金属能和酸反应", "金属活动性排序"],
     ["问化学键类型", "问元素周期表"],
     "atomic", "",
     "活动性顺序：钾钙钠镁铝锌铁锡铅(氢)铜汞银铂金；氢前置换酸中氢、前排换后排。"),
    ("kp_card_genetics",
     "遗传与变异",
     "基础科学知识点内容（人话接口）", "生物学",
     "遗传与变异是生物的基本特征：遗传=亲代将性状传递给子代的现象（由 DNA 上"
     "的基因控制）；变异=亲代与子代间及子代个体间的性状差异。可遗传变异来源："
     "基因突变（碱基对改变）、基因重组（有性生殖中基因重新组合）、染色体变异。"
     "孟德尔用豌豆杂交实验发现了分离定律和自由组合定律——现代遗传学之父。",
     ["什么是遗传", "什么是变异", "遗传和变异", "孟德尔实验", "可遗传变异有哪些",
      "基因突变和基因重组的区别"],
     ["问DNA结构", "问基因工程"],
     "atomic", "",
     "遗传=性状由基因传给子代；变异=性状差异，来源=突变+重组+染色体变异；孟德尔=遗传学之父。"),
    ("kp_card_silkroad",
     "丝绸之路",
     "人文通识知识点内容（人话接口）", "历史",
     "丝绸之路：汉代张骞出使西域（公元前 138 年起两次）后开通的连接中国与中"
     "亚、西亚直至欧洲的陆上贸易通道——中国输出丝绸、瓷器、茶叶，输入汗血宝"
     "马、香料、玻璃与宗教文化（佛教沿此东传）。海上丝绸之路则经南海印度洋通"
     "向波斯湾与红海。丝绸之路不仅是商路，更是东西方文明交流的桥梁。",
     ["什么是丝绸之路", "丝绸之路", "张骞出使西域", "丝绸之路的起点和终点",
      "丝绸之路有什么作用", "谁开通了丝绸之路"],
     ["问郑和下西洋", "问唐朝对外交流"],
     "atomic", "",
     "丝绸之路 = 张骞凿空后开通的东西方通道；丝绸瓷器茶叶西去、佛教文化东来——文明交流的桥梁。"),
    ("kp_card_algorithm_complexity",
     "算法时间复杂度",
     "基础科学知识点内容（人话接口）", "算法",
     "算法时间复杂度用大 O 符号描述算法运行时间随输入规模增长的增长趋势——"
     "O(1) 常数（哈希查找）、O(log n) 对数（二分查找）、O(n) 线性（遍历数组）、"
     "O(n log n) 线性对数（快速排序/归并排序）、O(n²) 平方（冒泡排序）、O(2ⁿ)"
     " 指数（穷举子集）。n 越大低复杂度优势越明显——选对算法比升级硬件更重要。",
     ["什么是时间复杂度", "大O表示法", "常见时间复杂度", "算法复杂度",
      "O(n)和O(log n)的区别", "二分查找的时间复杂度"],
     ["问空间复杂度", "问排序算法对比"],
     "atomic", "",
     "时间复杂度 = O(1)<O(logn)<O(n)<O(nlogn)<O(n²)<O(2ⁿ)；大O描述增长趋势非精确时间。"),
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
                               "level:L2", "status:verified", "batch:通识拓展04"],
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
