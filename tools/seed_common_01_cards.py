# -*- coding: utf-8 -*-
"""seed_common_01_cards.py · 日常科学常识批次（幂等）

01：天空为什么是蓝色/冰为什么浮在水面/秋天叶子为什么变黄/微波炉加热原理
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_bluesky",
     "天空为什么是蓝色的",
     "生活常识知识点内容（人话接口）", "自然常识",
     "天空呈现蓝色的原因：太阳光包含七种颜色（红橙黄绿蓝靛紫），进入大气层后"
     "遇到空气分子和微小尘埃发生散射——波长越短散射越强烈，蓝光波长短被散射"
     "得最多，散布到整个天空所以看到蓝色。傍晚偏红则是因为光穿过更厚的大气层"
     "蓝光被散射殆尽、剩下红橙光直达眼睛。",
     ["天空为什么是蓝色的", "为什么天是蓝的", "蓝色天空成因", "天空的颜色",
      "瑞利散射", "为什么晚霞是红的"],
     ["问彩虹成因", "问大气层结构"],
     "atomic", "",
     "天空蓝色 = 蓝光波长短被大气分子散射最强布满天空；傍晚红霞因光线穿更厚大气层蓝光被散射掉。"),
    ("kp_card_icefloat",
     "冰为什么浮在水面上",
     "生活常识知识点内容（人话接口）", "自然常识",
     "冰浮在水面上的原因：水在 4°C 时密度最大（约 1.0 g/cm³），继续降温结冰"
     "时水分子形成六角形晶格结构、分子间距反而变大，导致冰的密度（约 0.92 "
     "g/cm³）小于液态水——密度小的浮在密度大的上面。这一特性对水生生物至关"
     "重要：冰层浮在水面隔绝冷空气，水下仍保持 4°C 液态水，生物得以越冬。",
     ["冰为什么浮在水面上", "冰的密度", "冰和水哪个密度大", "为什么冰会漂浮",
      "水结冰体积变化", "冰浮于水"],
     ["问热胀冷缩反常", "问水的三态"],
     "atomic", "",
     "冰密度(0.92)<水(1.0)因氢键晶格空隙变大，故冰浮于水；4°C 水密度最大、冰层保护水下生物越冬。"),
    ("kp_card_autumnleaf",
     "秋天树叶为什么变黄变红",
     "生活常识知识点内容（人话接口）", "自然常识",
     "秋天树叶变色原理：春夏时叶绿素占主导、叶片呈绿色并制造养分。入秋日照缩"
     "短气温下降，叶绿素分解速度超过合成速度，原本被叶绿素掩盖的类胡萝卜素"
     "（黄色/橙色）显露出来——叶子变黄；部分植物（如枫树）还会在低温下合成花"
     "青素（红色色素）——叶子变红。变色后叶柄基部形成离层，叶子脱落以减少水分"
     "蒸发度过寒冬。",
     ["秋天树叶为什么变黄", "叶子为什么会变色", "树叶变色的原因", "为什么枫叶是红色的",
      "秋天叶子变红变黄", "叶绿素分解"],
     ["问光合作用", "问植物休眠"],
     "atomic", "",
     "叶色变化 = 秋季叶绿素分解、类胡萝卜素（黄）显露+花青素合成（红）；离层形成后落叶。"),
    ("kp_card_microwave",
     "微波炉加热原理",
     "生活常识知识点内容（人话接口）", "自然常识",
     "微波炉加热原理：磁控管产生频率约 2.45GHz 的微波，微波使食物中的水分子"
     "随交变电磁场每秒翻转数十亿次——分子间高速摩擦碰撞产生热量，从内到外同"
     "时加热（传统加热从外向内传导）。注意事项：金属容器反射微波不能放入（会"
     "打火）；密闭容器有爆炸风险（蒸汽无法释放）——加热鸡蛋、密封食品需特别"
     "小心。",
     ["微波炉加热原理", "微波炉怎么加热食物", "微波炉", "为什么金属不能放微波炉",
      "微波炉加热鸡蛋会爆炸吗", "微波炉的工作原理"],
     ["问电磁炉原理", "问红外线加热"],
     "atomic", "",
     "微波炉 = 2.45GHz 微波使水分子高速翻转摩擦生热、从内到外同热；金属反射不可入；密闭物有爆炸风险。"),
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
                "name": f"{name}（{dgroup}·生活常识知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——生活常识高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:生活常识01"],
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
