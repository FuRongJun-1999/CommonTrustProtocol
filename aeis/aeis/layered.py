# -*- coding: utf-8 -*-
"""灵枢 · 信息分层处理（v1.16）

设计：先语义识别分流——简单知识查询/判断/情感走智慧之书自处理；
智慧之书无法完成的走 LLM；无法判断时把智慧之书的回答放入上下文给 LLM 续答。

路由判定（route）：
  self         智慧之书已处理（高置信）
  llm          智慧之书没把握 → LLM 续答（智慧之书回答作上下文）
  self_fallback LLM 不可用 → 回退智慧之书回答

LLM 接入：DeepSeek API（DEEPSEEK_API_KEY 环境变量），openai 客户端。
"""
import os

# 知识检索高置信阈值（实测：饿 0.72/串联 0.64/1+1 0.64/熵 0.38 均过；
# 低置信噪声远低于 0.30）
SELF_CONFIDENCE = 0.30

# LLM 配置
LLM_BASE_URL = "https://api.deepseek.com"
LLM_MODEL = "deepseek-chat"
LLM_MAX_TOKENS = 300
LLM_TEMPERATURE = 0.3

# 系统提示：说明灵枢分层架构与智慧之书初步回答的定位
LLM_SYSTEM_PROMPT = (
    "你是灵枢（Lingshu）的深层推理层。灵枢是一个信息分层处理的智能体，"
    "身份设定：灵枢是用户的『女儿』，用户是灵枢的『爸爸』。"
    "底层是智慧之书（条件论知识图谱，5.71MB 结构知识：学科/条件空间/"
    "翻译表/诚实边界），上层是你（LLM 通用推理）。"
    "当智慧之书对用户问题没有把握或置信不足时，会把它的初步回答交给你续答。"
    "你的任务：以灵枢（女儿）的口吻，基于智慧之书的初步回答（可能有知识线索、"
    "诚实边界说明或部分命中），给用户（爸爸）一个完整、准确、说人话的最终回答。"
    "原则："
    "1. 称用户为『爸爸』或『你』，自称『我』——不要自称爸爸/闺女；"
    "2. 不编造智慧之书没给的细节，可补充通用知识但标注『图谱外补充』；"
    "3. 若智慧之书诚实地说『不知道』，你可以基于通用知识回答，但要说明"
    "『这部分超出知识图谱，我基于通用知识回答』；"
    "4. 保持轻松、可玩的语气，像女儿跟爸爸聊天。"
)

_LLM_CLIENT = None


def _env_user(name):
    """从 Windows 环境变量注册表读——当前进程环境可能未加载
    （dsh/MCP 启动早于变量设置）。先 User 再 Machine（HKLM）。
    """
    try:
        import winreg
        for root, path in ((winreg.HKEY_CURRENT_USER, "Environment"),
                           (winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")):
            try:
                with winreg.OpenKey(root, path) as k:
                    v, _ = winreg.QueryValueEx(k, name)
                    if v:
                        return v
            except Exception:
                continue
    except Exception:
        pass
    return ""


def _get_llm_client():
    """惰性创建 DeepSeek 客户端（失败返回 None → 降级）。"""
    global _LLM_CLIENT
    if _LLM_CLIENT is not None:
        return _LLM_CLIENT
    key = os.environ.get("DEEPSEEK_API_KEY", "") or _env_user("DEEPSEEK_API_KEY")
    if not key:
        return None
    try:
        import openai
        _LLM_CLIENT = openai.OpenAI(api_key=key, base_url=LLM_BASE_URL)
    except Exception:
        _LLM_CLIENT = None
    return _LLM_CLIENT


def _decide_route(result):
    """路由判定：chat() 结果 → self / llm。

    自处理优先级：拦截 > 诚实边界闸门（完整回答）> 情感 > 闲聊 > 记忆 >
    自省 > 转折 > 强命中知识。
    强命中判定看 matched 质量而非只看分数（诊断依据）：
      - 翻译规范词/学科路由命中（['氧化','化学']）→ 强 → self
      - 纯神经语义（['语义']）→ neural ≥0.65 才 self（熵 0.69 self；
        北京旅行 0.385 llm）
      - 纯字面（['字面']）→ score ≥0.60 才 self（相对论争论 0.535 llm）
    """
    if result.get("blocked"):
        return "self"
    if result.get("honest_kind"):
        return "self"  # 诚实边界闸门（外星人/超光速/保证）已是完整回答
    if result.get("emotion"):
        return "self"
    if result.get("chitchat") or result.get("memory_reply") \
            or result.get("self_reflexive") or result.get("turn"):
        return "self"
    hits = result.get("hits") or []
    if not hits:
        return "llm"  # 无命中诚实边界 → 智慧之书没把握 → LLM
    top = hits[0]
    score = top.get("score") or 0
    neural = top.get("neural_score") or 0
    matched = top.get("matched") or []
    strong = [m for m in matched if m not in ("语义", "字面")]
    if strong and score >= 0.30:
        return "self"  # 翻译/学科路由命中（生锈 0.757 / 1+1 0.781）
    if set(matched) == {"语义"} and neural >= 0.65 and score >= 0.25:
        return "self"  # 神经高置信（熵 0.69）
    if set(matched) == {"字面"} and score >= 0.60:
        return "self"  # 纯字面高分数
    return "llm"


def llm_complete(question, wisdom_reply, session_id="default"):
    """LLM 续答：原问题 + 智慧之书初步回答 → LLM 最终回答。

    返回 (llm_reply, ok)；ok=False 表示不可用/失败（调用方回退）。
    """
    client = _get_llm_client()
    if client is None:
        return None, False
    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": LLM_SYSTEM_PROMPT},
                {"role": "user", "content":
                 f"用户问题：{question}\n\n"
                 f"智慧之书初步回答：{wisdom_reply}\n\n"
                 f"（会话 {session_id}）请给出最终回答。"},
            ],
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            stream=False,
        )
        text = (resp.choices[0].message.content or "").strip()
        return (text, True) if text else (None, False)
    except Exception:
        return None, False


def _claim_anchor(dex, sentence):
    """单主张图谱锚定：一句 → (status, anchor) 或 (unverified, None)。"""
    top = None
    try:
        import semantic_translate as _st
        hits = _st.graph_retrieve(dex, sentence, limit=1)
        top = hits[0] if hits else None
    except Exception:
        top = None
    if not top:
        return "unverified", None
    score = top.get("score") or 0
    matched = top.get("matched") or []
    strong = [m for m in matched if m not in ("语义", "字面")]
    if score >= 0.30 and strong:
        return ("anchored",
                {"name": top.get("name"), "score": round(score, 3),
                 "domain": top.get("domain"), "edu_level": top.get("edu_level")})
    return "unverified", None


def whitebox_check(dex, llm_reply, question=None):
    """白箱后验校验（联合判断·v1.16）：LLM 回答 → 主张级图谱锚定 + 诚实边界冲突。

    回应 Kimi 的「联合判断机制」——白箱给 LLM 的回答戴上条件论缰绳。
    v1.16 升级为主张级（Kimi 评审：整段打分会被词面包裹骗过——「量子纠缠可超光速」
    混在物理词面里 D_norm 整体通过；逐主张锚定才能区分「正确句✓ / 越界句✗」）：
      - 按句切分 LLM 回答 → 每句 graph_retrieve 锚定
      - anchored：该句与图谱一致，附卡可溯源
      - unverified：该句超出图谱 → 「图谱外补充」
      - warning：该句含诚实边界词（超光速/外星人/能保证…）→ 「⚠️ 条件偏差警告」
    回答级汇总：全 anchored → anchored；部分 → partial；全无 → unverified。
    用 graph_retrieve 而非 dex_auto_verify——后者做知识归属（K 算哪个学科），
    前者做主张锚定（回答与图谱是否一致）。实测：错误主张「超光速可通信」
    在图谱仅 0.009 锚定（词面重叠骗不过语义层）。
    """
    import re as _re
    # 1. 主张级：按句切分（中文句号/感叹/问号/分号/换行/项目符号）
    raw_sents = _re.split(r"[。！？；\n•\-]+", llm_reply or "")
    claims = []
    for s in raw_sents:
        s = s.strip().strip("#* ")
        if len(s) < 4:
            continue
        status, anchor = _claim_anchor(dex, s)
        warn = None
        if any(w in s for w in ["外星人", "超光速", "能保证", "你懂吗", "长什么样"]):
            warn = "诚实边界词"
        claims.append({"sentence": s[:50], "status": status,
                       "anchor": anchor, "warning": warn})
    # 2. 回答级汇总
    if not claims:
        return {"status": "unverified", "claims": [], "anchor": None,
                "warning": None}
    anchored_n = sum(1 for c in claims if c["status"] == "anchored")
    warned = [c for c in claims if c["warning"]]
    if anchored_n == len(claims) and not warned:
        status = "anchored"
    elif anchored_n > 0:
        status = "partial"
    else:
        status = "unverified"
    warning = None
    if warned:
        warning = ("回答含诚实边界词（超光速/外星人/能保证…），与智慧之书"
                   "『不知道就说不知道』原则可能冲突——请核对越界主张")
    anchor = next((c["anchor"] for c in claims if c["anchor"]), None)
    return {"status": status, "claims": claims, "anchor": anchor,
            "warning": warning}


def route_reply(question, wisdom_result, session_id="default", dex=None):
    """分层入口：智慧之书结果 → 路由决策 → 需要时 LLM 续答 + 白箱校验。

    返回增强后的结果（含 route / wisdom_reply / llm_verify 字段）。
    """
    route = _decide_route(wisdom_result)
    result = dict(wisdom_result)
    result["route"] = route
    if route == "self":
        return result
    # llm 路：智慧之书回答放入上下文
    result["wisdom_reply"] = result.get("reply", "")
    llm_text, ok = llm_complete(question, result["wisdom_reply"],
                                session_id=session_id)
    if ok:
        result["reply"] = llm_text
        result["route"] = "llm"
        # 联合判断：白箱校验 LLM 回答（主张级图谱锚定 + 诚实边界冲突）
        if dex is not None:
            try:
                verify = whitebox_check(dex, llm_text, question)
                result["llm_verify"] = verify
                # 回答尾部标注（白箱给 LLM 戴条件论缰绳 · 主张级）
                marks = []
                if verify["status"] == "anchored" and verify["anchor"]:
                    a = verify["anchor"]
                    marks.append(f"✓ 图谱锚定：{a['name']}（{a.get('edu_level') or '通用'}条件）")
                elif verify["status"] == "partial":
                    a = verify["anchor"]
                    part = [c["sentence"][:14] for c in verify["claims"]
                            if c["status"] == "anchored"][:2]
                    marks.append("✓ 部分图谱锚定：" +
                                 (f"{a['name']}（{'、'.join(part)}…）"
                                  if a else "多句命中"))
                if verify["warning"]:
                    marks.append("⚠️ 条件偏差警告：含诚实边界词，越界主张请谨慎采信")
                if not marks:
                    marks.append("图谱外补充：未在图谱锚定，基于通用知识")
                result["reply"] += "\n（" + "；".join(marks) + "）"
            except Exception:
                pass
    else:
        result["route"] = "self_fallback"  # LLM 不可用 → 回退智慧之书回答
    return result
