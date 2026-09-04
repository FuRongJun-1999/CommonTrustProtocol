# -*- coding: utf-8 -*-
"""seed_common_16_cards.py · 通识拓展批次知识卡（幂等）

16：食品-食品安全标志/化学-常见的酸和碱/历史-中国古代四大发明/天文-恒星与星座
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_foodsafety",
     "食品安全标志与食品添加剂",
     "生活常识知识点内容（人话接口）", "食品安全",
     "中国食品安全标志：QS 标志（企业食品生产许可，2015 年后改为 SC 编码）；绿"
     "色食品标志（无污染/安全/优质/营养）；有机食品标志（不使用化学合成农"
     "药/化肥/激素/转基因）；无公害农产品标志。食品添加剂：为改善品质和色香味"
     "加入的物质（防腐剂/着色剂/甜味剂等），合法使用安全，超量或非法添加（如"
     "三聚氰胺）危害健康。阅读配料表是判断食品安全的重要技能——排位越靠前含量"
     "越高。",
     ["食品安全标志有哪些", "绿色食品标志", "有机食品", "食品添加剂安全吗",
      "怎么看食品配料表", "QS标志和SC编码"],
     ["问转基因食品", "问农药残留检测"],
     "atomic", "",
     "食品标志 = QS/SC（生产许可）+绿色食品+有机食品；配料表排位越前含量越高；合法添加剂安全/非法添加有害。"),
    ("kp_card_acidsbases",
     "生活中常见的酸和碱",
     "基础科学知识点内容（人话接口）", "化学",
     "生活中常见的酸：食醋（醋酸/乙酸，约3-5%）、柠檬/柑橘（柠檬酸/维生素C）、"
     "胃酸（盐酸，pH约1-2）、可乐（碳酸/磷酸）。常见的碱：氢氧化钠NaOH（烧碱"
     "/火碱，强腐蚀性工业原料）、氢氧化钙Ca(OH)₂（熟石灰，改良酸性土壤）、氨"
     "水（化肥/清洁剂）、小苏打水溶液（弱碱性，可中和胃酸）。酸碱指示剂：紫色"
     "石蕊试液遇酸变红遇碱变蓝；无色酚酞遇酸不变色、遇碱变红。",
     ["生活中常见的酸和碱", "常见的酸", "常见的碱", "食醋是酸还是碱",
      "酸碱指示剂有哪些", "石蕊和酚酞的变色"],
     ["问pH试纸", "问中和反应应用"],
     "atomic", "",
     "常见酸 = 食醋(乙酸)/柠檬(VC)/胃酸(HCl)；常见碱 = 烧碱/熟石灰/氨水；指示剂 = 石蕊酸红碱蓝、酚酞碱红。"),
    ("kp_card_4inventions_cn",
     "中国古代四大发明",
     "人文通识知识点内容（人话接口）", "历史",
     "中国古代四大发明：造纸术（东汉蔡伦改进，用树皮麻头等廉价材料造纸——知"
     "识传播的革命）；印刷术（隋唐雕版印刷→北宋毕昇发明活字印刷——书籍量产"
     "成为可能）；指南针（战国司南→宋代用于航海——大航海时代的关键工具）；火"
     "药（唐代炼丹意外产物→宋代军事应用——改变战争形态）。四大发明经阿拉伯人"
     "传向欧洲，马克思评价为「资产阶级社会到来的三大预告」。",
     ["中国古代四大发明", "四大发明是什么", "造纸术是谁改进的", "活字印刷是谁发明的",
      "指南针的发明", "火药的发明"],
     ["问丝绸之路细节", "问郑和下西洋"],
     "atomic", "",
     "四大发明 = 造纸术(蔡伦改进)+印刷术(毕昇活字)+指南针(航海)+火药(军事)——推动世界文明进程。"),
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
                               "level:L2", "status:verified", "batch:通识拓展16"],
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
