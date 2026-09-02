# -*- coding: utf-8 -*-
"""seed_night4_v2_cards.py · 夜间候选域清单v0.2第四组知识卡（幂等·收官批）

夜批N4：防诈骗/环境科学/农业常识/天文观测 四域各一张，KCCS 四要素+题干原句触发词。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

NODES = [
    ("kp_card_antifraud",
     "冒充公检法诈骗的识别",
     "生活常识知识点内容（人话接口）", "防诈骗",
     "冒充公检法诈骗的识别要点：①公检法机关不会通过电话/QQ/微信办案，更不会"
     "发送「通缉令」图片；②凡要求转账到「安全账户」的都是诈骗——根本没有"
     "安全账户；③凡索要银行卡密码、短信验证码的都是诈骗（验证码等于取款密码）；"
     "④来电显示可被伪造（改号软件），不能只看来电号码。防骗三原则：不听、"
     "不信、不转账；拿不准就挂断后拨打 96110 反诈专线核实。",
     ["怎么识别冒充公检法诈骗", "什么是安全账户骗局", "验证码能告诉别人吗",
      "接到诈骗电话怎么办", "96110是什么", "问防诈骗"],
     ["问刷单返利细节", "问杀猪盘案例"],
     "atomic", "",
     "识别要点 = 公检法不电话办案/无安全账户/验证码绝不外泄/来电可伪造；不听不信不转账，96110 核实。"),
    ("kp_card_greenhouse",
     "温室效应的原理",
     "基础科学知识点内容（人话接口）", "环境科学",
     "温室效应的原理：太阳短波辐射穿透大气到达地面使地表升温；地表以长波（红外）"
     "辐射向外散热时，被大气中的温室气体（二氧化碳、甲烷、水蒸气等）吸收并"
     "部分反射回地面——如同温室玻璃「进得来、出不去」，使地表维持适宜温度。"
     "温室效应本身是自然现象（没有它地球平均温度约 -18°C）；问题在于人类活动"
     "排放的二氧化碳等过量增强温室效应导致全球变暖。可再生能源（太阳能/风能等）"
     "替代化石燃料是主要减排途径。",
     ["温室效应的原理", "什么是温室效应", "温室气体有哪些", "全球变暖的原因",
      "二氧化碳与温室效应", "问碳中和"],
     ["问臭氧层空洞", "问酸雨成因"],
     "atomic", "",
     "温室效应 = 温室气体吸收地表红外辐射再反射回地面；本身是自然现象，过量排放致全球变暖。"),
    ("kp_card_hybridrice",
     "杂交水稻与袁隆平",
     "生活常识知识点内容（人话接口）", "农业常识",
     "杂交水稻：利用水稻杂种优势——两个遗传性不同的亲本杂交，后代（F1）在"
     "产量、抗性上超过双亲。关键难点是水稻自花授粉、花小，人工去雄不现实；"
     "袁隆平团队 1970 年在海南发现野生雄性不育株「野败」，建立三系法"
     "（不育系/保持系/恢复系）实现大规模杂交制种，1973 年配套成功。杂交稻"
     "比常规稻增产约 20%，为中国乃至世界粮食安全做出重大贡献；袁隆平因此"
     "被称为「杂交水稻之父」。",
     ["什么是杂交水稻", "袁隆平的贡献", "杂交水稻原理", "为什么杂交水稻产量高",
      "三系法是什么", "问粮食安全"],
     ["问转基因技术", "问海水稻细节"],
     "atomic", "",
     "杂交水稻 = 利用杂种优势，三系法（不育系/保持系/恢复系）突破制种难关，增产约 20%，袁隆平团队 1973 年配套成功。"),
    ("kp_card_moonphase",
     "月相变化",
     "基础科学知识点内容（人话接口）", "天文观测",
     "月相变化：月球不发光，靠反射太阳光；随月球绕地球公转（约 29.5 天一个"
     "朔望月），日地月相对位置变化使我们看到月球被照亮部分不断变化——新月"
     "（朔，初一，看不见）→ 上弦月（初七初八，右半亮）→ 满月（望，十五六）→ "
     "下弦月（廿二三，左半亮）→ 再回新月。上弦月黄昏时在南方天空、下弦月半夜"
     "才升起；「上上上西西、下下下东东」是记忆口诀。",
     ["月相变化的原因", "什么是新月满月", "上弦月下弦月", "月亮为什么有阴晴圆缺",
      "朔望月是多少天", "问月相"],
     ["问日食月食成因", "问潮汐"],
     "atomic", "",
     "月相 = 日地月相对位置变化（29.5 天朔望月）：新月→上弦→满月→下弦循环；月球反射太阳光。"),
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
                "name": f"{name}（{dgroup}·生活与科学知识卡）",
                "生效条件": conds,
                "子功能": f"{name}——生活与科学高频问题知识条目",
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
                               "level:L2", "status:verified", "batch:夜间v0.2第四组"],
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
