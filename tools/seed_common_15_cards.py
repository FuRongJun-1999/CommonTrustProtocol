# -*- coding: utf-8 -*-
"""seed_common_15_cards.py · 通识拓展批次知识卡（幂等）

15：物理-压强/化学-金属的化学性质/生物-生物分类/地理-时区与日界线
KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_pressure2",
     "压强的概念与应用",
     "基础科学知识点内容（人话接口）", "物理学",
     "压强：物体单位面积上受到的压力，公式 p=F/S，单位帕斯卡（Pa）。增大压强"
     "的方法：增大压力（刀切菜用力按）或减小受力面积（刀刃磨锋利、图钉尖做"
     "尖）；减小压强：减小压力或增大受力面积（书包带做宽、坦克装履带、铁轨铺"
     "枕木）。液体压强随深度增加而增大——大坝上窄下宽因此。大气压强随海拔升高"
     "而减小。",
     ["什么是压强", "压强的公式", "压强的单位", "增大压强的方法",
      "减小压强的方法", "书包带为什么做宽"],
     ["问大气压强", "问液体压强"],
     "atomic", "",
     "压强 p=F/S（Pa）；增大=加力/减面积（刀刃尖），减小=增面积（书包带宽/履带）；液体压强随深度增大。"),
    ("kp_card_metalreact",
     "金属的化学性质",
     "基础科学知识点内容（人话接口）", "化学",
     "金属的化学性质：①大多数金属能与氧气反应（如镁条燃烧发出耀眼白光、铁在"
     "潮湿空气中生锈）；②活泼金属能与稀酸反应产生氢气（如锌+稀硫酸→硫酸锌+"
     "氢气）；③活泼金属能把不活泼金属从其盐溶液中置换出来（如铁放入硫酸铜溶液"
     "表面覆盖红色铜）。金属活动性顺序：钾>钙>钠>镁>铝>锌>铁>锡>铅>(氢)>铜>"
     "汞>银>铂>金——氢前金属能与稀酸反应，前换后。",
     ["金属的化学性质", "金属能与什么反应", "金属活动性顺序", "铁为什么生锈",
      "金属与酸的反应", "金属与盐溶液的反应"],
     ["问合金", "问金属冶炼"],
     "atomic", "",
     "金属化学性质 = 与氧气反应/与稀酸反应产氢/前换后（活动性强换弱）；活动性顺序：钾钙钠镁铝锌铁锡铅氢铜汞银铂金。"),
    ("kp_card_biotaxonomy",
     "生物分类的等级",
     "基础科学知识点内容（人话接口）", "生物学",
     "生物分类的等级从大到小：界、门、纲、目、科、属、种（种是最基本的分类单"
     "位）。分类等级越小，生物之间的共同特征越多、亲缘关系越近。例如人类：动"
     "物界→脊索动物门→哺乳纲→灵长目→人科→人属→智人种。林奈（1707-1778）"
     "创立了双命名法（属名+种加词用拉丁文），是现代生物分类学的奠基人。",
     ["生物分类的等级", "界门纲目科属种", "生物分类", "什么是双命名法",
      "生物分类等级从大到小", "最基本的分类单位是什么"],
     ["问病毒分类", "问植物分类"],
     "atomic", "",
     "分类等级从大到小 = 界→门→纲→目→科→属→种（种为基本单位，越小亲缘越近）；林奈创立双命名法。"),
    ("kp_card_timezone",
     "时区与日界线",
     "基础科学知识点内容（人话接口）", "地理学",
     "时区与日界线：全球按经度分为 24 个时区（每 15° 一个时区，时间差 1 小时"
     "），以本初子午线（0° 经线，经过英国格林尼治天文台）为基准。中国统一使用"
     "北京时间（东八区 UTC+8）。国际日界线大致沿 180° 经线——从东向西跨过日"
     "界线日期加一天，从西向东跨过日期减一天。例如中国比英国早 8 小时。",
     ["时区怎么划分", "什么是时区", "国际日界线", "北京时间是什么时区",
      "为什么有 jet lag", "时区和日界线"],
     ["问经纬度", "问极昼极夜"],
     "atomic", "",
     "24 个时区每 15° 一区差 1 小时；本初子午线 0° 为基准；日界线沿 180°，从西向东跨减一天。"),
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
                               "level:L2", "status:verified", "batch:通识拓展15"],
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
