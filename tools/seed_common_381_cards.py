# -*- coding: utf-8 -*-
"""seed_common_381_cards.py · 通识拓展批次381知识卡+题库（幂等）

381：3 张新卡（硬币货币史/智能锁/有氧与无氧运动）+ 3 题（QB-1381~1383）。
KCCS 四要素+题干原句触发词。预检已过（QB-1381~1383 可用，三主题
题库 0 覆盖——有氧呼吸题 QB-1063 为细胞呼吸生物题，与运动健身不重），
卡库无同名卡。
"""
import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "..", "aeis", "wisdom", "wisdom-book-cloud.db")
BANK = os.path.join(HERE, "question_bank.json")

WHITELIST = {"Havilland", "Maillard", "reaction", "CPAP", "OSA", "Mpemba",
             "effect", "OR6A2", "ghrelin", "DOMS", "DHT", "frisson",
             "AlphaGo", "CFOP", "Transformer", "LLM", "GPT", "BERT",
             "CYP3A4", "ACID", "CNN", "RNN", "LSTM", "Krebs", "NADH",
             "FADH2", "Vmax", "Km", "RNA", "DNA", "mRNA", "KCL", "KVL",
             "BCS", "B2H6", "borrow", "Rust", "sin", "cos", "tan",
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM"}


def foreign_word_check(text: str) -> list:
    """西里尔字符一律报警；长英文词(≥4)非白名单报警。只扫中文内容字段。"""
    bad = []
    if re.search(r"[\u0400-\u04FF]", text):
        bad.append("cyrillic:" + re.search(r"[\u0400-\u04FF]+", text).group())
    for w in re.findall(r"[A-Za-z]{4,}", text):
        if w not in WHITELIST:
            bad.append("latin:" + w)
    return bad


NODES = [
    ("kp_card_coin",
     "硬币（金属货币小史）",
     "货币常识知识点内容（人话接口）", "历史与文明",
     "硬币——金属铸造的货币：①**中国起源**——春秋战国已有布币（铲形）"
     "刀币（刀形）等金属铸币，形似生产工具；②**圆形方孔**——秦始皇统一"
     "货币为「半两钱」：外圆内方（天圆地方观念），方孔便于串绳携带和"
     "打磨修整，此后两千多年中国铜钱形制基本不变；③**重要节点**——汉"
     "五铢钱（沿用七百余年）、唐开元通宝（开创「通宝」钱制，不再以重量"
     "为名）；④**材质与成本**——现代硬币用钢芯镀镍/铝/铜合金，耐磨损"
     "流通寿命远长于纸币；小面值硬币曾出现「铸币成本高于面值」的倒挂"
     "现象（故小面额硬币多改用更便宜的钢芯）；⑤**与纸币关系**——硬币"
     "负责小额找零高流通，纸币负责大额，两者互补。",
     ["硬币是谁发明的", "圆形方孔钱的由来", "半两钱是什么",
      "硬币为什么中间有孔", "开元通宝", "硬币和纸币的区别"],
     ["问交子", "问五铢钱"],
     "atomic", "",
     "硬币=金属铸币春秋战国布币刀币起源+秦统一圆形方孔半两钱外圆内方"
     "象征天圆地方方孔便串绳打磨+汉五铢七百年唐开元通宝开创通宝制+现代"
     "钢芯镀镍寿命长于纸币+小面额铸币成本倒挂改钢芯+硬币小额纸币大额"
     "互补。"),
    ("kp_card_smartlock",
     "智能锁",
     "生活科技知识点内容（人话接口）", "生活常识",
     "智能锁——电子化开锁的门锁：①**开锁方式**——指纹（半导体电容"
     "传感器识别纹路+活体检测，光学式易被照片骗，半导体式更安全）、"
     "密码（防窥可加前后乱码位——在正确密码前后随意补位再按）、NFC"
     "卡片、手机蓝牙、远程临时密码（给访客限时开门）；②**锁芯才是"
     "防盗核心**——智能再强，机械应急锁孔弱就白搭：选 C 级锁芯（防"
     "技术开启时间最长）；③**应急设计**——所有智能锁都保留机械钥匙"
     "孔（电子失效/没电时用），多数支持外接充电宝应急供电；④**使用"
     "提示**——冬天低温/手指潮湿会降低指纹识别率；录入多个手指备用；"
     "密码定期更换。",
     ["智能锁安全吗", "指纹锁原理", "C级锁芯是什么",
      "智能锁没电了怎么办", "密码防窥乱码", "智能锁怎么选"],
     ["问监控摄像头", "问门禁卡"],
     "atomic", "",
     "智能锁=指纹半导体电容式带活体检测比光学安全+密码防窥前后加乱码"
     "位+NFC蓝牙临时密码多方式+防盗核心看锁芯选C级+机械应急锁孔标配"
     "支持充电宝应急供电+低温潮湿指纹识别率下降录多指备用。"),
    ("kp_card_cardio",
     "有氧运动与无氧运动",
     "运动健康知识点内容（人话接口）", "健康与身体",
     "有氧 vs 无氧——按供能方式区分的两大运动类型：①**有氧运动**——"
     "中低强度、持续时间长，氧气充足参与供能（糖+脂肪有氧氧化）：快走/"
     "慢跑/游泳/骑车/跳操；特点是可连续做几十分钟；②**无氧运动**——"
     "短时高强度，氧气来不及参与，靠无氧糖酵解供能（产生乳酸所以肌肉"
     "酸胀）：百米冲刺/举重/短距离快速爬楼/大重量力量训练；③**心率"
     "参考**——最大心率约等于 220 减年龄，有氧燃脂区间大约是最大心率"
     "的 60%~80%；④**怎么练**——有氧练心肺耐力与燃脂，无氧练肌肉力量"
     "与基础代谢；健康成人每周约 150 分钟中等强度有氧+两次力量训练；"
     "同一节课「先无氧后有氧」组合效率更高（先耗糖原再燃脂）；⑤**"
     "误区**——出汗多不等于减脂效果好，强度看心率不看汗。",
     ["有氧运动和无氧运动的区别", "有氧心率区间多少", "什么运动是有氧",
      "先力量还是有氧", "每周运动多少分钟", "燃脂心率怎么算"],
     ["问力量训练", "问马拉松训练"],
     "atomic", "",
     "有氧无氧区别=有氧中低强度长时间氧气充足供能快走慢跑游泳骑车+无氧"
     "短时高强度无氧糖酵解产乳酸冲刺举重大重量力量+最大心率220减年龄"
     "有氧区间60%到80%+每周150分钟中等有氧加两次力量先无氧后有氧+出汗"
     "多不等于减脂看心率。"),
]

QUESTIONS = [
    ("QB-1381", "圆形方孔钱是怎么来的？硬币为什么中间有孔？",
     "历史与文明", "技术直答",
     ["硬币", "方孔钱", "半两", "秦统一"], "通识拓展381"),
    ("QB-1382", "智能锁有哪些开锁方式？智能锁没电了怎么办？",
     "生活常识", "技术直答",
     ["智能锁", "指纹", "锁芯", "应急"], "通识拓展381"),
    ("QB-1383", "有氧运动和无氧运动有什么区别？燃脂心率怎么算？",
     "健康与身体", "技术直答",
     ["有氧", "无氧", "心率", "燃脂"], "通识拓展381"),
]


def ensure_seed() -> dict:
    for nid, *_ in NODES:
        conn = sqlite3.connect(DB)
        row = conn.execute("SELECT id FROM nodes WHERE id=?", (nid,)).fetchone()
        conn.close()
        assert not row, f"id 撞车：{nid} 已存在"
    bank = json.load(open(BANK, encoding="utf-8"))
    have = {q["id"] for q in bank["questions"]}
    for qid, *_ in QUESTIONS:
        assert qid not in have, f"QB 撞车：{qid} 已存在"

    all_text = ""
    for n in NODES:
        all_text += n[1] + " " + n[4] + " " + " ".join(n[5]) + " " \
            + " ".join(n[6]) + " " + n[9] + " "
    for q in QUESTIONS:
        all_text += q[1] + " " + " ".join(q[4]) + " "
    bad = foreign_word_check(all_text)
    assert not bad, f"外文词混入：{bad}"

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
                               "level:L2", "status:verified", "batch:通识拓展381"],
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

    qs = bank["questions"]
    added = 0
    for qid, question, domain, qtype, keywords, source in QUESTIONS:
        if qid in have:
            continue
        qs.append({"id": qid, "question": question, "domain": domain,
                   "type": qtype, "keywords": keywords, "source": source,
                   "added": "2026-09-07"})
        added += 1
    bank["version"] = "v6.51"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
