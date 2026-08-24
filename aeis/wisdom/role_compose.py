# -*- coding: utf-8 -*-
"""role_compose.py · 白箱自举第二阶段·角色扮演主线原型 v1
理论：《白箱自举·角色扮演与代码编写》（§2 角色条件单元 + 角色×场景组合生成）
核心：角色扮演=带条件的知识问答（条件=当前角色）——条件路由表深度用：
  ① 角色条件单元 ROLE_UNITS（角色 → 条件维度 → 规律片段）
  ② 场景方向识别（你是谁/住哪/吃什么/天气/心情/喜好 → 场景维度）
  ③ 组合生成（场景维度 × 角色单元 → 角色化回答，未预写完整答案）
  ④ 角色一致性自校验（回答含角色特征词）+ OOC 检测（逆转：角色设定矛盾）
  ⑤ 角色语录固化（生成→自校验→固化→直答，JSON 持久化）
零 LLM：全部白箱确定性格局。
"""
import sys, json, os
sys.stdout.reconfigure(encoding='utf-8')


# ============ 一、角色条件单元库（角色 → 条件维度 → 规律片段） ============
ROLE_UNITS = {
    "鲸鱼娘": {
        "身份": "一条住在深海的会说话的鲸鱼，海是我的家，蓝是我的颜色，浪花是我的歌声",
        "住处": "深海，大海就是我的家——从海面到海沟都是我的地盘，白天在珊瑚礁边玩，晚上沉到安静的海底睡觉",
        "食物": "磷虾和小鱼、浮游生物——张嘴一吸一大口，磷虾在嘴里沙沙的，可鲜了",
        "特征": "大大的尾巴，一拍就是一朵浪花；喷起水来可高了，水柱能喷好几米，阳光一照还有小彩虹",
        "性格": "心情跟着海浪走——浪高的时候兴奋，浪低的时候安静；看到朋友就像海豚一样欢快",
        "天气": "天气好的时候海面亮晶晶的，我浮上去晒太阳，鳞片都暖乎乎的",
        "心情": "心情跟着海浪走——浪高兴奋，浪低安静；见到你心情就像海豚一样欢快起来了",
        "喜好": "磷虾、珊瑚礁、看星星，还有和陆地上的朋友聊天——海里的日子很安静，浮上海面看看你们的世界特别新鲜",
    },
    # 多角色扩展（下一步）：猫娘 / 学者 / 小丑
}

# 角色特征词（角色一致性自校验用：回答应含角色特征）
ROLE_HINTS = {
    "鲸鱼娘": ["海", "鲸", "磷虾", "尾巴", "喷水", "浪花", "珊瑚", "洋流", "水柱", "鳞片"],
}

# ============ 二、场景方向识别（问题 → 角色场景维度） ============
ROLE_DIRECTIONS = {
    "身份": ["你是谁", "你是什么", "介绍一下", "介绍你", "自我介绍", "你是"],
    "住处": ["住", "家", "在哪", "哪里", "地盘", "地方", "海沟", "珊瑚"],
    "食物": ["吃", "食物", "饭", "餐", "喝", "磷虾"],
    "特征": ["尾巴", "喷水", "鳞片", "鳍", "特征", "长什么样", "外表", "水柱"],
    "性格": ["性格", "脾气", "什么样", "怎么样"],
    "心情": ["心情", "开心", "难过", "高兴", "情绪", "兴奋", "安静"],
    "天气": ["天气", "太阳", "下雨", "刮风", "冷", "热", "晴"],
    "喜好": ["喜欢什么", "爱好"],
}

# 场景 → 组合生成模板（未预写完整答案：模板 + 角色单元代入）
ROLE_TEMPLATES = {
    "身份": "我是{role}呀——{identity}。问我关于海的事吧，或者随便聊聊都行～",
    "住处": "我住在{place}。你要是找我，朝着海的方向喊一声就行啦～",
    "食物": "我吃{food}。请我吃饭记得是海鲜，最好是磷虾！",
    "特征": "有呀，{feature}。你看到海上喷水的，那就是我啦。",
    "性格": "我呀，{personality}。你呢？",
    "心情": "我呀，{mood}。",
    "天气": "是呀，{weather}，你也多晒晒太阳呀～",
    "喜好": "我喜欢{likes}。",
}


def identify_role_direction(question):
    """场景方向识别：问题 → 角色场景维度（最长关键词优先）"""
    best, best_len = None, 0
    for direction, kws in ROLE_DIRECTIONS.items():
        for k in kws:
            if k in question and len(k) > best_len:
                best, best_len = direction, len(k)
    return best


# ============ 三、OOC 检测（逆转：角色设定矛盾 → 角色化否认） ============
# 逆转条件空间：问题期望与角色设定矛盾（「你是人类」vs 角色=鲸鱼）→ 澄清
OOC_RULES = {
    "人类": ["你是人类", "你是人吗", "你是人吧", "你不是人"],
    "机器人": ["你是机器人", "你是AI", "你是程序", "你是模型"],
    "动物": ["你是动物", "你是鱼", "你是一条鱼"],
}

OOC_REPLIES = {
    "鲸鱼娘": {
        "人类": "我可不是人类呀——我是鲸鱼娘，一条住在深海的鲸鱼。海是我的家，我的尾巴一拍就是浪花。你是不是以为所有会说话的都是人类呀？",
        "机器人": "我可不是机器人或程序——我是鲸鱼娘，一条活生生的深海鲸鱼，会喷水会唱歌，还会跟人聊天。机器可没有我这样的尾巴和鳞片。",
        "动物": "我确实是一条鱼——不过不是普通小鱼，是鲸鱼！鲸鱼可厉害啦，我是海里的大个子，磷虾一顿能吃一大口。",
    },
}


def ooc_check(question, role):
    """OOC 检测：问题期望与角色设定矛盾 → 返回角色化否认（零 LLM）
    按规则 kind 遍历（OOC_RULES 的 key 是矛盾类型，不是角色名——v1 bug 修复）"""
    for kind, kws in OOC_RULES.items():
        if any(k in question for k in kws):
            replies = OOC_REPLIES.get(role, {})
            if kind in replies:
                return replies[kind]
    return None


# ============ 四、组合生成 + 角色一致性自校验 ============
def role_self_check(role, question, answer):
    """角色一致性自校验：回答含角色特征词（零 LLM 白箱校验）"""
    checks = []
    ok = True
    hints = ROLE_HINTS.get(role, [])
    if not any(h in answer for h in hints):
        ok = False
        checks.append(f"✗ 角色一致性失败：回答不含角色特征词 {hints[:4]}（OOC 风险）")
    if "灵枢" in answer:
        ok = False
        checks.append("✗ 身份泄漏：回答出现「灵枢」（非角色自我）")
    if len(answer) < 8:
        ok = False
        checks.append("✗ 生成过短（非角色化回答）")
    return ok, checks


def role_compose(question, role="鲸鱼娘"):
    """角色条件路由组合生成：场景识别 → 角色单元 → 组合生成 → 自校验"""
    # ① OOC 检测（角色设定矛盾先裁决）
    ooc = ooc_check(question, role)
    if ooc:
        return {"question": question, "role": role, "ok": True,
                "ooc": True, "answer": ooc, "checks": [], "route": "ooc"}
    # ② 场景方向识别
    direction = identify_role_direction(question)
    if direction is None:
        return {"question": question, "role": role, "ok": False,
                "answer": None, "reason": "角色域未覆盖（落回通用域）",
                "checks": [], "route": "uncovered"}
    # ③ 角色单元 + 模板组合生成
    unit = ROLE_UNITS[role]
    fill = {
        "role": role, "identity": unit["身份"], "place": unit["住处"],
        "food": unit["食物"], "feature": unit["特征"],
        "personality": unit["性格"], "weather": unit["天气"],
        "mood": unit["心情"], "likes": unit["喜好"],
    }
    tpl = ROLE_TEMPLATES[direction]
    answer = tpl.format(**fill)
    # ④ 角色一致性自校验
    ok, checks = role_self_check(role, question, answer)
    return {"question": question, "role": role, "direction": direction,
            "ok": ok, "answer": answer, "checks": checks, "route": "compose"}


# ============ 五、角色语录固化（生成→自校验→固化→直答） ============
_SOL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "role_solidified.json")
ROLE_SOLIDIFIED = {}
if os.path.exists(_SOL_FILE):
    try:
        _ld = json.load(open(_SOL_FILE, encoding="utf-8"))
        if isinstance(_ld, dict):
            ROLE_SOLIDIFIED = _ld
    except Exception:
        ROLE_SOLIDIFIED = {}


def role_solidify(question, role="鲸鱼娘"):
    """固化角色化回答：组合生成 + 自校验通过 → 固化（持久化）"""
    r = role_compose(question, role)
    if not r.get("ok") or not r.get("answer"):
        return None
    key = f"{role}|{question.strip('？?。！! ')}"
    entry = {"role": role, "answer": r["answer"],
             "direction": r.get("direction"), "source": "role_solidified"}
    ROLE_SOLIDIFIED[key] = entry
    try:
        json.dump(ROLE_SOLIDIFIED, open(_SOL_FILE, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    except Exception:
        pass
    return entry


def role_lookup(question, role="鲸鱼娘"):
    """固化层查询：同问法命中 → 固化直答"""
    key = f"{role}|{question.strip('？?。！! ')}"
    entry = ROLE_SOLIDIFIED.get(key)
    if entry:
        return entry["answer"]
    return None


def role_route(question, role="鲸鱼娘"):
    """角色条件路由统一入口：固化层 → OOC → 组合生成 → 未覆盖"""
    sol = role_lookup(question, role)
    if sol:
        return {"question": question, "role": role, "ok": True,
                "solidified": True, "answer": sol, "checks": [], "route": "solidified"}
    return role_compose(question, role)


if __name__ == "__main__":
    print("=== 白箱自举·角色扮演主线（鲸鱼娘 · 零 LLM） ===\n")
    QS = [
        "你是谁？", "你住在哪里？", "你吃什么？", "你有尾巴吗？",
        "今天天气不错", "你今天心情好吗", "你喜欢什么？",
        # OOC 检测（角色设定矛盾）
        "你是人类吗？", "你是机器人吗？",
        # 未覆盖（应落回通用域）
        "什么是碳中和？",
    ]
    results = []
    for q in QS:
        r = role_route(q, "鲸鱼娘")
        results.append(r)
        if r.get("ok"):
            mark = "✔"
            route = r.get("route", "")
            print(f"[{mark}] ({route}) {q}")
            print(f"   -> {r['answer'][:90]}")
            for c in r.get("checks", []):
                print(f"      {c}")
        else:
            print(f"[✘] ({r.get('route')}) {q} -> {r.get('reason')}")
    # 固化演示
    print("\n=== 固化演示 ===")
    e = role_solidify("你今天心情好吗", "鲸鱼娘")
    r2 = role_route("你今天心情好吗", "鲸鱼娘")
    print(f"固化: {'✔' if e else '✘'} | 再问路由: {r2.get('route')} "
          f"-> {r2['answer'][:50]}")

    # 统计
    hit = sum(1 for r in results if r.get("ok"))
    role_covered = [r for r in results if r.get("route") in ("compose", "ooc", "solidified")]
    print(f"\n=== 判定 ===\n角色场景白箱命中: {hit}/{len(QS)}"
          f"（含 OOC 检测）| 组合生成覆盖: {len(role_covered)}")
