# -*- coding: utf-8 -*-
"""seed_common_08_cards.py · 通识拓展批次知识卡（幂等）

08：地理-世界气候类型/历史-文艺复兴/化学-金属腐蚀与防锈/计算机-操作系统基础
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_climatetypes",
     "世界主要气候类型",
     "基础科学知识点内容（人话接口）", "气候学",
     "世界主要气候类型及特征：热带雨林气候（终年高温多雨，如亚马逊）；热带草"
     "原气候（干湿两季分明）；热带沙漠气候（终年炎热干燥，如撒哈拉）；地中海"
     "气候（夏干热、冬温湿，如地中海沿岸）；温带海洋性气候（终年温和多雨，如"
     "西欧）；温带季风气候（夏热多雨、冬冷干燥，如中国北方）；温带大陆性气候"
     "（温差大降水少，如中亚）；极地气候（终年严寒）。",
     ["世界主要气候类型", "气候类型有哪些", "热带雨林气候", "地中海气候的特点",
      "温带海洋性气候", "气候类型怎么判断"],
     ["问洋流", "问气候变化"],
     "atomic", "",
     "主要气候类型 = 热带雨林（终年多雨）/热带草原（干湿两季）/热带沙漠（干燥）/地中海（夏干冬湿）/温带海洋（温和多雨）/温带季风（四季分明）/温带大陆/极地。"),
    ("kp_card_renaissance",
     "文艺复兴",
     "人文通识知识点内容（人话接口）", "世界历史",
     "文艺复兴（14-16世纪）：起源于意大利的人文主义思想文化运动，主张以人为"
     "中心而非以神为中心，肯定人的价值与尊严。文学三杰：但丁（《神曲》）、彼特"
     "拉克、薄伽丘；美术三杰：达芬奇（《蒙娜丽莎》《最后的晚餐》）、米开朗基罗"
     "（大卫雕像）、拉斐尔（圣母像）。文艺复兴推动了科学革命（哥白尼日心说）和"
     "宗教改革，为启蒙运动铺路。",
     ["什么是文艺复兴", "文艺复兴", "文艺复兴三杰", "人文主义是什么",
      "文艺复兴的代表人物", "达芬奇和蒙娜丽莎"],
     ["问启蒙运动", "问宗教改革"],
     "atomic", "",
     "文艺复兴 = 14-16世纪意大利起源的人文主义运动；三杰=但丁/彼特拉克/薄伽丘（文学）+达芬奇/米开朗基罗/拉斐尔（美术）。"),
    ("kp_card_corrosion",
     "金属腐蚀与防锈",
     "基础科学知识点内容（人话接口）", "化学",
     "金属腐蚀：金属与周围环境发生化学反应而损耗的过程。铁生锈的条件=同时接触"
     "氧气和水（潮湿空气中最易生锈），铁锈主要成分是氧化铁（Fe₂O₃）。防锈方法"
     "：①隔绝空气和水（刷漆/涂油/电镀）；②改变金属内部结构（制成不锈钢）；③"
     "牺牲阳极保护法（在船底连上更活泼的锌块，锌先被腐蚀保护铁）。",
     ["金属为什么会生锈", "铁生锈的条件", "怎么防止金属生锈", "金属腐蚀",
      "防锈方法有哪些", "铁锈的主要成分"],
     ["问电镀工艺", "问铝合金"],
     "atomic", "",
     "铁生锈条件 = 同时接触氧气和水；防锈 = 刷漆/涂油/电镀/不锈钢/牺牲阳极保护。"),
    ("kp_card_os",
     "操作系统的基本功能",
     "基础科学知识点内容（人话接口）", "计算机",
     "操作系统（OS）是管理计算机硬件与软件资源的系统软件，是用户与硬件之间的"
     "桥梁。四大核心功能：①进程管理（CPU分配调度）；②存储管理（内存分配与虚"
     "拟内存）；③文件管理（文件系统目录结构）；④设备管理（驱动打印机键盘等外"
     "设）。常见操作系统：Windows、macOS、Linux、Android、iOS。没有操作系统，"
     "应用程序无法直接操控硬件。",
     ["操作系统的作用", "什么是操作系统", "常见的操作系统", "操作系统的功能",
      "OS是什么意思", "操作系统管理什么"],
     ["问编程语言", "问网络协议"],
     "atomic", "",
     "OS 四大功能 = 进程管理+存储管理+文件管理+设备管理；是用户与硬件间的桥梁。"),
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
                               "level:L2", "status:verified", "batch:通识拓展08"],
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
