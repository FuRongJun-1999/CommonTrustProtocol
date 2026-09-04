# -*- coding: utf-8 -*-
"""seed_n10_v3_cards.py · 知识域拓展第五批知识卡（幂等）

夜批N10：计量学-单位制/科技史-四大发明/地理之最/时间计量 四域各一张，
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_siunit",
     "国际单位制（SI）基本单位",
     "基础科学知识点内容（人话接口）", "计量学",
     "国际单位制（SI）七个基本单位：米 m（长度）、千克 kg（质量）、秒 s（时间）、"
     "安培 A（电流）、开尔文 K（热力学温度）、摩尔 mol（物质的量）、坎德拉 cd"
     "（发光强度）。其他单位都是基本单位的导出组合（如牛顿 N=kg·m/s²）。统一"
     "单位是科学交流与工程制造的前提——历史上单位混乱曾导致卫星发射失败等事故。",
     ["国际单位制七个基本单位", "SI单位", "基本单位有哪些", "米千克秒是什么单位",
      "国际单位制", "物质的量单位是什么"],
     ["问英制单位换算", "问单位历史"],
     "atomic", "",
     "SI 七基本单位 = m/kg/s/A/K/mol/cd；导出单位皆由其组合；统一单位是科学与工程的前提。"),
    ("kp_card_4inventions",
     "中国古代四大发明",
     "人文通识知识点内容（人话接口）", "科技史",
     "中国古代四大发明：造纸术（东汉蔡伦改进，用树皮麻头等廉价材料造纸）、"
     "印刷术（隋唐雕版印刷，北宋毕昇发明活字印刷）、指南针（战国司南演化，"
     "宋代用于航海）、火药（唐代炼丹意外产物，宋代用于军事）。四大发明经阿拉"
     "伯人传向欧洲，深刻推动了世界文明进程（造纸印刷促进知识传播、指南针开启"
     "大航海、火药改变战争形态）。",
     ["中国古代四大发明", "四大发明是什么", "造纸术是谁改进的", "活字印刷是谁发明的",
      "四大发明有哪些", "指南针的发明"],
     ["问丝绸之路细节", "问郑和下西洋"],
     "atomic", "",
     "四大发明 = 造纸术（蔡伦改进）/印刷术（毕昇活字）/指南针/火药——经阿拉伯传向世界。"),
    ("kp_card_georecords",
     "世界地理之最",
     "基础科学知识点内容（人话接口）", "地理学",
     "世界地理之最：最高峰珠穆朗玛峰（8848.86 米）；最长河尼罗河（约 6650 公里"
     "，一说亚马逊）；最大洋太平洋（约占地球表面积三分之一）；最大沙漠撒哈拉"
     "（约 900 万平方公里）；最大平原亚马逊平原；最深海沟马里亚纳海沟（约 11034"
     " 米）；最大湖泊里海（咸水湖）；最高的高原青藏高原（平均 4000 米以上，"
     "「世界屋脊」）。",
     ["世界地理之最", "最高的山峰", "最长的河流", "最大的海洋", "最大的沙漠",
      "最深的海沟", "世界屋脊是哪里"],
     ["问各国首都", "问大陆漂移"],
     "atomic", "",
     "地理之最 = 珠峰最高 8848.86m / 尼罗河最长 / 太平洋最大 / 马里亚纳海沟最深 / 青藏高原=世界屋脊。"),
    ("kp_card_timemeasure",
     "时间的计量与历法",
     "基础科学知识点内容（人话接口）", "计量学",
     "时间的计量：地球自转一周为一天（24 小时），月球绕地球一圈为一月（约 29.5"
     " 天朔望月），地球绕太阳一圈为一年（约 365.24 天回归年）。公历（格里高利历）"
     "通过 4 年一闰、百年不闰、四百年再闰规则使历年与回归年对齐。现代最精准的"
     "计时工具是原子钟（利用铯原子振动频率定义秒，千万年误差不到一秒）。",
     ["时间是怎么计量的", "闰年是怎么来的", "一年为什么是365天", "什么是原子钟",
      "公历的规则", "历法怎么制定"],
     ["问二十四节气", "问农历规则"],
     "atomic", "",
     "时间计量 = 自转定日/月球定月（29.5 天）/公转定年（365.24 天）；公历闰年规则对齐回归年；原子钟最准。"),
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
                               "level:L2", "status:verified", "batch:拓展第五批"],
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
