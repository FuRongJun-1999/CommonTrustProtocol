# -*- coding: utf-8 -*-
"""seed_common_429_cards.py · 通识拓展批次429知识卡+题库（幂等）

429：3 张新卡·未来科技三连（脑机接口 kp_card_bci /
    虚拟现实 kp_card_vr / 自动驾驶 kp_card_autodrive）。
KCCS 四要素+题干原句触发词。预检已过（QB-1525~1527 可用，
三主题题库卡库双零）。
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
             "Dijkstra", "Bellman", "Floyd", "logV", "LIGO", "SVM",
             "MTBF", "SQA", "IMC", "HMO", "JD", "STAR", "Word", "offer",
             "XMind", "HDR", "Robotaxi"}


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
    ("kp_card_bci",
     "脑机接口",
     "前沿科技知识点内容（人话接口）", "科学技术",
     "脑机接口——大脑与机器的直接对话：①**是什么**——在大脑与外部设备"
     "之间建立直接连接通路，绕过语言和肢体；②**两类**——非侵入式（头"
     "戴电极帽读取脑电波，安全但信号弱）与侵入式（手术植入电极到脑内，"
     "信号精确但有手术风险）；③**怎么工作**——读取神经元电信号 → 算法"
     "解码「意图」→ 控制光标、机械臂或打字；反向还能电刺激传递感觉；"
     "④**应用**——渐冻症、高位截瘫患者用意念打字交流、操控机械臂；"
     "癫痫的脑内电刺激治疗；⑤**挑战**——信号的长期稳定性、带宽（远低"
     "于人脑）、隐私伦理（「读心」的边界）与手术安全性。",
     ["脑机接口是什么", "脑机接口原理", "意念控制机械臂",
      "侵入式和非侵入式", "脑机接口应用", "渐冻症患者"],
     ["问人工智能", "问神经科学"],
     "atomic", "",
     "脑机接口=大脑与外部设备直接连接绕过语言肢体+非侵入头戴电极帽安"
     "全信号弱侵入式植入精确有风险+读取神经元电信号解码意图控制光标机"
     "械臂+渐冻症截瘫意念打字癫痫电刺激治疗+挑战长期稳定性带宽隐私伦"
     "理手术安全。"),
    ("kp_card_vr",
     "虚拟现实",
     "前沿科技知识点内容（人话接口）", "科学技术",
     "虚拟现实（VR）——戴上头显进入另一个世界：①**VR/AR/MR**——VR"
     "完全沉浸在虚拟世界（头显遮挡现实）；AR 把虚拟内容叠加在现实上"
     "（手机看家具摆家里）；MR 混合两者，虚拟物可与现实互动；②**立体"
     "原理**——左右眼看到略有差异的画面（双目视差），大脑自动合成"
     "立体感；头显追踪头部转动实时调整画面，产生「身临其境」；③**"
     "应用**——游戏娱乐、飞行与消防的职业培训（零风险练危险操作）、"
     "恐高症暴露疗法、远程看房与虚拟展厅；④**晕动症**——画面在动而"
     "身体没动，视觉与前庭觉不匹配导致头晕——提高刷新率、降低延迟可"
     "缓解；⑤**趋势**——更轻的头显、裸手交互、眼动追踪让虚拟世界越"
     "来越「真」。",
     ["VR是什么", "虚拟现实原理", "VR和AR区别",
      "晕动症怎么回事", "VR能用来做什么", "双目视差"],
     ["问游戏机", "问三维动画"],
     "atomic", "",
     "VR虚拟现实=头显完全沉浸遮挡现实AR叠加现实MR混合互动+双目视差"
     "大脑合成立体+头追踪实时调整身临其境+游戏职业培训零风险练危险恐"
     "高暴露疗法远程看房+晕动症画面动身体没动视觉前庭不匹配提高刷新"
     "率缓解+更轻裸手交互眼动追踪。"),
    ("kp_card_autodrive",
     "自动驾驶",
     "前沿科技知识点内容（人话接口）", "科学技术",
     "自动驾驶——让汽车自己开：①**分级（L0-L5）**——L2 是「辅助驾驶」"
     "（人必须随时接管：车道保持+自适应巡航），L4 高度自动驾驶（限定"
     "区域内可无人），L5 完全无人（任何场景）——目前量产车最高到 L2/"
     "L2+，Robotaxi 试点在限定城市运营；②**三大模块**——感知（激光"
     "雷达/摄像头/毫米波雷达多传感器融合，各有所长互补盲区）、决策"
     "（AI 算法预测路况规划路径）、控制（转向油门刹车执行）；③**难点"
     "——「长尾问题」：99% 的场景好解决，剩下的暴雨黑夜、突发加塞、"
     "交警手势等千奇百怪的场景占了 99% 的难度；④**争议**——事故责任"
     "归车主还是车企、道德两难（紧急避险怎么选）；⑤**价值**——减少"
     "人为失误（酒驾疲劳驾驶占事故大头）、释放驾驶时间。",
     ["自动驾驶分级", "L2辅助驾驶和L4", "自动驾驶用什么传感器",
      "激光雷达", "自动驾驶的难点", "自动驾驶安全吗"],
     ["问新能源车", "问人工智能"],
     "atomic", "",
     "自动驾驶=L0到L5分级L2辅助需接管L4限定区域L5完全无人量产最高L2+"
     "感知激光雷达摄像头毫米波融合决策AI规划控制执行+难点长尾问题99%"
     "场景好解决剩下的占99%难度+争议责任归属道德两难+价值减少人为失"
     "误酒驾疲劳。"),
]

QUESTIONS = [
    ("QB-1525", "脑机接口是什么？它有哪些实际应用？",
     "科学技术", "技术直答",
     ["脑机接口", "意念", "电极", "应用"], "通识拓展429"),
    ("QB-1526", "VR、AR、MR 有什么区别？为什么玩 VR 会头晕？",
     "科学技术", "技术直答",
     ["VR", "AR", "区别", "晕"], "通识拓展429"),
    ("QB-1527", "自动驾驶分为哪几级？L2 和 L4 有什么区别？",
     "科学技术", "技术直答",
     ["自动驾驶", "分级", "L2", "L4"], "通识拓展429"),
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
                               "level:L2", "status:verified", "batch:通识拓展429"],
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
    bank["version"] = "v7.00"
    json.dump(bank, open(BANK, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return {"cards_inserted": inserted, "cards_updated": updated,
            "cards_skipped": skipped, "questions_added": added,
            "total_questions": len(qs)}


if __name__ == "__main__":
    print(json.dumps(ensure_seed(), ensure_ascii=False))
