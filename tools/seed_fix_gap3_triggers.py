# -*- coding: utf-8 -*-
"""seed_fix_gap3_triggers.py · 三缺口题触发词补齐（幂等）

QB-096 月亮为什么有阴晴圆缺 / QB-184 怎么在夜空中找到北极星 /
QB-019 为什么高原上水不到100度就沸腾了——卡均在库、内容正确，
仅缺题干原句级触发词变体（补卡方法论：生效条件需短触发变体+原句）。
"""
import json
import os
import sqlite3

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                  "..", "aeis", "wisdom", "wisdom-book-cloud.db")

# card_id → 追加触发词（题干原句+短变体）
ADD_CONDS = {
    "kp_card_moonphase": [
        "月亮为什么有阴晴圆缺", "月亮为什么会有阴晴圆缺",
        "阴晴圆缺是怎么回事", "月亮为什么会变圆变缺",
    ],
    "kp_card_constellation": [
        "怎么在夜空中找到北极星", "如何找到北极星", "夜空中找北极星",
    ],
    "kp_card_boiling": [
        "为什么高原上水不到100度就沸腾了", "为什么高原上水不到 100 度就沸腾了",
        "高原上水的沸点是多少", "海拔越高水的沸点越低",
    ],
}


def ensure_fix() -> dict:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    updated = skipped = missing = 0
    for nid, adds in ADD_CONDS.items():
        row = cur.execute("SELECT state_attributes FROM nodes WHERE id=?",
                          (nid,)).fetchone()
        if not row or not row[0]:
            missing += 1
            continue
        sa = json.loads(row[0])
        conds = sa.setdefault("comment", {}).setdefault("生效条件", [])
        new = [c for c in adds if c not in conds]
        if not new:
            skipped += 1
            continue
        conds.extend(new)
        cur.execute("UPDATE nodes SET state_attributes=? WHERE id=?",
                    (json.dumps(sa, ensure_ascii=False), nid))
        updated += 1
    conn.commit()
    conn.close()
    return {"updated": updated, "skipped": skipped, "missing": missing}


if __name__ == "__main__":
    print(json.dumps(ensure_fix(), ensure_ascii=False))
