# -*- coding: utf-8 -*-
"""patch_concept_cards.py · T10 概念域触发词补丁 + 智慧之书新卡（2026-08-30）

对统一记忆库（aeis_memory.db）的概念卡追加高频问法触发词（幂等），
并补建「智慧之书」概念卡（T3 挖掘的高频域，原库无卡）。
识别卡域内容待定（dsh 端语境），本轮不生成。
源库 wisdom-book-cloud.db 由 dsh 端持有，留停机窗口同步补丁。
"""
import sys, os, json, sqlite3, time
sys.stdout.reconfigure(encoding='utf-8')

DB = r"D:\Program Files\2_ai\AEIS\data\aeis_memory.db"
# 触发词补丁表：卡 id → 追加的高频问法（幂等追加到 comment.生效条件）
PATCHES = {
    "kp_card_whitebox_def": ["问白箱", "白箱范式是什么", "白箱是什么"],
    "kp_card_four_states": ["四态路由是什么", "什么是四态"],
    "kp_card_error_update": ["白箱怎么学习", "预测误差"],
    "kp_card_vs_expert": ["白箱和专家系统的区别"],
    "kp_card_llm_division": ["白箱和 LLM 的关系", "白箱需要 LLM 吗"],
    "kp_card_axiom_layers": ["问条件论", "条件论的核心是什么", "条件论"],
}

conn = sqlite3.connect(DB)
patched = 0
for card_id, words in PATCHES.items():
    row = conn.execute("SELECT state_attributes FROM nodes WHERE id=?", (card_id,)).fetchone()
    if not row:
        print(f"  跳过 {card_id}（不存在）")
        continue
    sa = json.loads(row[0])
    cm = sa.get("comment")
    if not cm:
        print(f"  跳过 {card_id}（无 comment）")
        continue
    eff = cm.setdefault("生效条件", [])
    added = [w for w in words if w not in eff]
    if added:
        eff.extend(added)
        conn.execute("UPDATE nodes SET state_attributes=? WHERE id=?",
                     (json.dumps(sa, ensure_ascii=False), card_id))
        patched += 1
        print(f"  {card_id}: +{len(added)} 触发词 {added}")
conn.commit()
print(f"触发词补丁: {patched} 张卡更新")

# ---- 智慧之书新卡（T3 高频域真空白补建）----
NEW_CARD_ID = "kp_card_wisdom_book"
exists = conn.execute("SELECT 1 FROM nodes WHERE id=?", (NEW_CARD_ID,)).fetchone()
if exists:
    print("智慧之书卡已存在，跳过")
else:
    ts = time.time()
    content = ("智慧之书是灵枢的知识查询与分层对话引擎（wisdom_chat）：语义识别分流——"
               "情感/闲聊/记忆/自省/知识查询走白箱自处理；白箱没把握时自动转 LLM 续答。"
               "用法：直接问知识问题（学科/概念/生活导航），灵枢用条件路由图确定性直答。")
    sa = {"comment": {
        "生效条件": ["问智慧之书", "智慧之书是什么", "智慧之书怎么用", "问 wisdom_chat"],
        "子功能": ["知识查询分流", "白箱直答", "LLM 续答兜底"],
        "执行": "智慧之书分层对话：先白箱确定性回答，没把握再 LLM 续答（route 字段标注来源）",
        "不适用条件": ["问与灵枢无关的实时新闻"],
    }, "observation_position": "灵枢", "existence_constraint": "协议实例运行中"}
    node = (NEW_CARD_ID, content, "text", "{}", str(ts), json.dumps(
        {"observation_position": "灵枢", "existence_constraint": "协议实例运行中"},
        ensure_ascii=False), 0.7, 0.9, "knowledge", 0, ts,
        json.dumps(["概念卡", "智慧之书"], ensure_ascii=False), "{}", json.dumps(
            sa, ensure_ascii=False), None)
    cols = ["id", "content", "modality", "spatial_coordinates", "temporal_coordinate",
            "condition_space", "importance", "confidence", "layer", "access_count",
            "last_access", "tags", "semantic_coordinates", "state_attributes", "entity_id"]
    conn.execute(f"INSERT INTO nodes ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                 tuple(node[i] for i in range(len(cols))))
    conn.commit()
    print("智慧之书概念卡已建 ✓")
conn.close()
