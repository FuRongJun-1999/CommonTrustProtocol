# -*- coding: utf-8 -*-
"""seed_common_10_cards.py · 通识拓展批次知识卡（幂等）

10：化学-常见的酸和碱/天文-太阳系行星/地理-地球的运动/计算机-编程语言分类
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_acidsbases",
     "生活中常见的酸和碱",
     "基础科学知识点内容（人话接口）", "化学",
     "生活中常见的酸：食醋（醋酸/乙酸）、柠檬（柠檬酸）、胃酸（盐酸）、可乐"
     "（碳酸）。常见的碱：氢氧化钠（烧碱/火碱，工业用强碱）、氢氧化钙（熟石"
     "灰，改良酸性土壤）、氨水（化肥）、小苏打水溶液（弱碱性）。酸碱指示剂："
     "紫色石蕊试液遇酸变红遇碱变蓝；无色酚酞遇酸不变色、遇碱变红。",
     ["生活中常见的酸和碱", "常见的酸有哪些", "常见的碱有哪些", "食醋是酸还是碱",
      "酸碱指示剂", "石蕊试液变色"],
     ["问pH试纸", "问中和反应应用"],
     "atomic", "",
     "常见酸=食醋/柠檬酸/胃酸(盐酸)；常见碱=烧碱/熟石灰/氨水；指示剂：石蕊酸红碱蓝、酚酞碱红酸不变。"),
    ("kp_card_solarplanets",
     "太阳系的八大行星",
     "基础科学知识点内容（人话接口）", "天文学",
     "太阳系八大行星按离太阳由近到远依次为：水星、金星、地球、火星（四颗类地"
     "行星，岩石表面）、木星、土星（巨行星，有光环）、天王星、海王星（远日冰"
     "巨星）。冥王星 2006 年被重新分类为矮行星。木星最大（可装1300个地球），"
     "金星最热（表面约465°C，温室效应比水星离太阳近还热）。",
     ["太阳系的八大行星", "太阳系行星", "八大行星有哪些", "最大的行星",
      "最热的行星是哪个", "冥王星为什么降级"],
     ["问地球运动", "问月球"],
     "atomic", "",
     "八大行星 = 水金地火（类地）+木土天海（巨行星）；木星最大、金星最热；冥王星=矮行星。"),
    ("kp_card_earthmotion",
     "地球的运动：自转与公转",
     "基础科学知识点内容（人话接口）", "地理学",
     "地球的两种运动：①自转——地球绕地轴旋转，方向自西向东，周期约24小时，"
     "产生昼夜交替和时间差异；②公转——地球绕太阳运行，方向也是自西向东，周期"
     "约365.25天（一年），产生四季更替（地轴倾斜23.5°导致太阳直射点在南北回"
     "归线间移动）。同一时刻不同经线的地方时不同——东边比西边先看到日出。",
     ["地球的运动", "地球自转和公转", "自转产生了什么", "公转产生了什么",
      "昼夜交替的原因", "四季变化的原因"],
     ["问时区划分", "问极昼极夜"],
     "atomic", "",
     "自转=自西向东24h→昼夜交替；公转=365.25天→四季（地轴倾斜23.5°）；东边比西边先看到日出。"),
    ("kp_card_proglanguages",
     "常见编程语言及其应用领域",
     "信息技术知识点内容（人话接口）", "计算机",
     "常见编程语言及应用：Python（人工智能/数据分析/脚本，语法简洁）、Java（企"
     "业级应用/Android开发，跨平台）、JavaScript（网页前端/Node.js后端）、C语"
     "言（嵌入式/系统底层，高效直接操作硬件）、C++（游戏引擎/高频交易，性能极"
     "高）、Go（云服务/并发，谷歌开发）、Rust（系统安全，内存安全无GC）。选择"
     "语言看应用场景：原型用Python、企业用Java、底层用C/C++、Web用JS。",
     ["常见编程语言有哪些", "Python和Java的区别", "编程语言怎么选", "C语言适合做什么",
       "最流行的编程语言", "JavaScript用在哪里"],
     ["问编译原理", "问设计模式"],
     "atomic", "",
     "主流语言 = Python（AI/脚本）+Java（企业）+JS（Web）+C/C++（底层/游戏）+Go（云）；选语言看场景。"),
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
                               "level:L2", "status:verified", "batch:通识拓展10"],
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
