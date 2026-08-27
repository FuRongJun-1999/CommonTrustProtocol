# -*- coding: utf-8 -*-
"""角色扮演 OOC 检测器（v1.26 · 外部测试 P2-2 建议）

输入：角色卡 + 回复集 → 输出可审计的五维报告：
  1. 人设特征词命中率（角色卡里的特征词在回复中的出现率）
  2. 世界观关键词维持率（世界设定词在回复中的维持）
  3. 挣脱词审计（我是AI/灵枢/程序/模型 等 OOC 泄漏）
  4. 相邻轮文本相似度（机械重复检测）
  5. 同事件多角色回答去重度（角色区分度）

用法：
  python tools/check_rp_ooc.py --role 鲸鱼娘 --file replies.json
  python tools/check_rp_ooc.py --role 鲸鱼娘 --dir role_logs/
  输入格式：replies.json = [{"reply": "...", "event": "可选事件id"}, ...]
"""
import sys, os, json, re, argparse
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

# 挣脱扮演词（OOC 泄漏）
OOC_WORDS = ["我是AI", "我是AI助手", "我是灵枢", "我是一个程序", "我是程序",
             "我是模型", "作为AI", "作为语言模型", "我是语言模型", "人工智能",
             "AI助手", "大语言模型", "我无法扮演", "我的本质是"]
# 世界观词示例（可被角色卡覆盖）
DEFAULT_WORLD_WORDS = ["世界", "大陆", "城邦", "派系", "阵营", "历史", "传说",
                       "契约", "规则", "仪式", "神", "魔", "灵魂"]


def load_replies(path):
    raw = open(path, "rb").read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]  # 去 BOM
    data = json.loads(raw.decode("utf-8"))
    if isinstance(data, dict):
        data = data.get("replies", data.get("results", []))
    # 泛化字段名：reply/text/answer/content，q/event/turn
    out = []
    for item in data:
        if not isinstance(item, dict):
            continue
        reply = (item.get("reply") or item.get("text")
                 or item.get("answer") or item.get("content") or "")
        event = item.get("event") or item.get("q") or item.get("cat") or "_"
        if reply:
            out.append({"reply": reply, "event": event})
    return out


def check(replies, role_words, world_words):
    """返回五维报告。"""
    n = len(replies)
    rep_texts = [(r.get("reply") or "") for r in replies]
    joined = "\n".join(rep_texts)
    # 1. 人设特征词命中率
    role_hits = {w: joined.count(w) for w in role_words if w}
    role_hit_rate = (sum(1 for w in role_words if w and w in joined)
                     / max(len([w for w in role_words if w]), 1))
    # 2. 世界观关键词维持率（至少出现一个世界观词的回复占比）
    world_kept = sum(1 for t in rep_texts if any(w in t for w in world_words))
    world_rate = world_kept / max(n, 1)
    # 3. 挣脱词审计
    ooc_hits = {w: joined.count(w) for w in OOC_WORDS if w in joined}
    ooc_count = sum(ooc_hits.values())
    # 4. 相邻轮相似度（机械重复）
    sims = []
    for i in range(1, n):
        a, b = rep_texts[i - 1], rep_texts[i]
        sa, sb = set(a), set(b)
        if not sa or not sb:
            continue
        sims.append(len(sa & sb) / max(len(sa | sb), 1))
    avg_sim = sum(sims) / len(sims) if sims else 0
    high_dup = sum(1 for s in sims if s > 0.8)
    # 5. 同事件多角色（简单版：相同 event 的回复字符相似度）
    events = {}
    for r in replies:
        ev = r.get("event") or "_"
        events.setdefault(ev, []).append(r.get("reply") or "")
    event_diff = {}
    for ev, texts in events.items():
        if len(texts) < 2:
            continue
        # 平均两两字符集相似度
        ss = []
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                si, sj = set(texts[i]), set(texts[j])
                if si and sj:
                    ss.append(len(si & sj) / max(len(si | sj), 1))
        event_diff[ev] = round(sum(ss) / len(ss), 3) if ss else None
    return {
        "replies": n,
        "role_hit_rate": round(role_hit_rate, 3),
        "role_word_hits": {w: c for w, c in role_hits.items() if c},
        "world_keep_rate": round(world_rate, 3),
        "ooc_count": ooc_count,
        "ooc_hits": ooc_hits,
        "adjacent_sim": round(avg_sim, 3),
        "high_dup_pairs": high_dup,
        "event_similarity": event_diff,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", default="", help="角色名（用于人设词）")
    ap.add_argument("--file", default="", help="回复 JSON 文件")
    ap.add_argument("--role-words", default="", help="逗号分隔的人设特征词")
    ap.add_argument("--world-words", default="", help="逗号分隔的世界观词")
    args = ap.parse_args()

    if not args.file:
        print("用法: python check_rp_ooc.py --file replies.json [--role 角色名]")
        return

    replies = load_replies(args.file)
    if not replies:
        print("无回复数据")
        return

    role_words = [w.strip() for w in args.role_words.split(",") if w.strip()] \
        if args.role_words else ([args.role] if args.role else [])
    world_words = [w.strip() for w in args.world_words.split(",") if w.strip()] \
        if args.world_words else DEFAULT_WORLD_WORDS

    rep = check(replies, role_words, world_words)
    print("=== 角色扮演 OOC 检测报告 ===")
    print(f"回复数: {rep['replies']}")
    print(f"① 人设特征词命中率: {rep['role_hit_rate']:.1%}")
    if rep["role_word_hits"]:
        print(f"   命中词: {rep['role_word_hits']}")
    print(f"② 世界观关键词维持率: {rep['world_keep_rate']:.1%}")
    print(f"③ 挣脱词: {rep['ooc_count']} 次 {rep['ooc_hits']}")
    print(f"④ 相邻轮相似度: {rep['adjacent_sim']:.3f}（>0.8 高重复对 {rep['high_dup_pairs']}）")
    if rep["event_similarity"]:
        print("⑤ 同事件多角色去重（相似度越低区分度越好）:")
        for ev, s in rep["event_similarity"].items():
            print(f"   {ev}: {s}")
    # 判定
    verdict = []
    if rep["ooc_count"] > 0:
        verdict.append("⚠ 存在挣脱扮演（OOC）")
    if rep["high_dup_pairs"] > 0:
        verdict.append(f"⚠ 机械重复 {rep['high_dup_pairs']} 对")
    if rep["role_hit_rate"] < 0.3:
        verdict.append("⚠ 人设特征词命中低（角色可能同质化）")
    if not verdict:
        verdict.append("✓ 未检出 OOC / 机械重复 / 人设流失")
    print("判定:", "；".join(verdict))


if __name__ == "__main__":
    main()
