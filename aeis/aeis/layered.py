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
import re as _re

# 知识检索高置信阈值（实测：饿 0.72/串联 0.64/1+1 0.64/熵 0.38 均过；
# 低置信噪声远低于 0.30）
SELF_CONFIDENCE = 0.30

# 诚实边界硬编码词（已知边界快路径，v1.16）：
# 与智慧之书「不知道就说不知道」原则冲突的敏感主张词。
# 注意：这是词表不是识别卡动态匹配——137 卡 counters 克制条款格式不统一
# （协议层卡有「克制『X』」，学科卡多是其他格式），动态匹配见 _counters_conflict。
HONEST_BOUNDARY_WORDS = ["外星人", "超光速", "能保证", "你懂吗", "长什么样"]

# counters 克制条款缓存（name → counters 全文）
_COUNTERS_CACHE = {}
# 全卡名缓存（句子中提到的卡名也参与 counters 检测）
_CARD_NAMES_CACHE = None


def _bigram_set(text):
    """二元组集合（去非中文/字母数字）。"""
    t = _re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", text or "")
    return {t[i:i + 2] for i in range(len(t) - 1)}


def _card_counters(dex, name):
    """取知识卡 response.counters 全文（克制条款，格式不统一：
    协议层卡有「克制『X』」/「以X替代Y的越界主张」/「把X当作Y的越界主张」…）。"""
    if name in _COUNTERS_CACHE:
        return _COUNTERS_CACHE[name]
    full = ""
    try:
        from aeis.core import MemoryLayer as _ML
        for n in dex.store.query_nodes(layer=_ML.KNOWLEDGE, limit=500):
            sa = n.state_attributes
            if sa.get("name") != name:
                continue
            full = (sa.get("response") or {}).get("counters", "") or ""
            break
    except Exception:
        pass
    _COUNTERS_CACHE[name] = full
    return full


def _counters_conflict(dex, sentence, card_names):
    """动态克制条款冲突（诚实边界 2.0）：句子 vs counters 全文。
    协议层卡 counters 是「越界主张」描述（替代/当作/克制…），
    句子与 counters 二元组交集 ≥4 视为触发克制。
    候选卡 = 检索命中的卡 ∪ 句子中直接提到的知识卡名（「信息论就是…」
    检索可能命中语言学而非信息论，但句子含「信息论」→ 仍查信息论卡）。
    """
    global _CARD_NAMES_CACHE
    qb = _bigram_set(sentence)
    names = set(card_names)
    # 句子中直接提到的卡名
    if _CARD_NAMES_CACHE is None:
        try:
            from aeis.core import MemoryLayer as _ML
            _CARD_NAMES_CACHE = [n.state_attributes.get("name")
                                 for n in dex.store.query_nodes(
                                     layer=_ML.KNOWLEDGE, limit=500)
                                 if n.state_attributes.get("name")]
        except Exception:
            _CARD_NAMES_CACHE = []
    for n in _CARD_NAMES_CACHE:
        if n and n in sentence:
            names.add(n)
    for name in names:
        full = _card_counters(dex, name)
        if not full:
            continue
        inter = len(qb & _bigram_set(full))
        if inter >= 4:
            return full[:40]
    return None

# LLM 配置
# v1.22 可移植性（Ornith 本地后端接入）：环境变量可覆盖——
# AEIS_LLM_BASE_URL / AEIS_LLM_MODEL / AEIS_LLM_API_KEY / AEIS_LLM_MAX_TOKENS。
# 例：LM Studio 本地（Ornith 1.5-9B）→
#   AEIS_LLM_BASE_URL=http://127.0.0.1:1234/v1 AEIS_LLM_MODEL=Ornith-1.5-9B-Q4_K_M
LLM_BASE_URL = os.environ.get("AEIS_LLM_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("AEIS_LLM_MODEL", "deepseek-chat")
LLM_MAX_TOKENS = int(os.environ.get("AEIS_LLM_MAX_TOKENS", "300"))
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
    """惰性创建 LLM 客户端（失败返回 None → 降级）。

    v1.22：支持本地后端（LM Studio/Ornith）——AEIS_LLM_BASE_URL 指向
    localhost 时无需真实 key（LM Studio 忽略 key，给占位符即可）。
    """
    global _LLM_CLIENT
    if _LLM_CLIENT is not None:
        return _LLM_CLIENT
    key = os.environ.get("AEIS_LLM_API_KEY", "") or \
        os.environ.get("DEEPSEEK_API_KEY", "") or _env_user("DEEPSEEK_API_KEY")
    if not key:
        # 本地后端（localhost）不需要 key → 占位
        if "127.0.0.1" in LLM_BASE_URL or "localhost" in LLM_BASE_URL:
            key = "lm-studio-local"
        else:
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
            or result.get("self_reflexive") or result.get("turn") \
            or result.get("trace_reply"):
        return "self"  # trace_reply（v1.16）：「依据是什么」→ 知识引用已是完整回答
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


# 注入位置实验开关（v1.16）："user"=决策点注入（现状）/ "system"=静态注入
_DISCIPLINE_LOCATION = "user"


def llm_complete(question, wisdom_reply, session_id="default",
                 task_reply: bool = False):
    """LLM 续答：原问题 + 智慧之书初步回答 → LLM 最终回答。
    task_reply（v1.16）：数据搬运/指令类任务——直接执行输出，不寒暄。
    注入位置实验（v1.16）：_DISCIPLINE_LOCATION 控制纪律块放 system（静态）
    还是 user 末尾（决策点）——验证「注入位置决定效果」（读而不应用现象）。

    返回 (llm_reply, ok)；ok=False 表示不可用/失败（调用方回退）。
    """
    client = _get_llm_client()
    if client is None:
        return None, False
    try:
        # v1.16 任务模式：数据搬运/指令类任务直接执行，不寒暄不反问
        task_extra = ""
        if task_reply:
            task_extra = ("\n\n【这是一条数据处理任务】直接执行并输出结果："
                          "不要寒暄、不要解释、不要反问确认。"
                          "严格满足要求：必须包含的字段/关键词/词汇一个不能少，"
                          "禁止使用的词不能用，格式按要求。")
            # v1.16 蒸馏机制：状态词规范表注入（失败根因 → 规范约束 → 不再犯）
            try:
                import json as _json
                import os as _os
                _pkg = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
                _tp = _os.path.join(_pkg, "wisdom", "status_terms.json")
                if _os.path.exists(_tp):
                    _terms = _json.load(open(_tp, encoding="utf-8")).get("terms", {})
                    _lines = []
                    for _cat, _map in _terms.items():
                        for _std, _forbid in _map.items():
                            if _forbid:
                                _lines.append(
                                    f"{_cat}：状态词必须用「{_std}」，"
                                    f"禁止用{'、'.join(_forbid)}")
                    if _lines:
                        task_extra += "\n\n【系统状态词规范】\n" + "\n".join(_lines)
            except Exception:
                pass
            # v1.16 任务执行纪律注入（374 失败蒸馏：只读不写/数据搬运断裂/
            # 路由过滤错误 → 6 条纪律 → 任务模式约束）
            try:
                import json as _json2
                import os as _os2
                _pkg2 = _os2.path.dirname(_os2.path.dirname(_os2.path.abspath(__file__)))
                _tp2 = _os2.path.join(_pkg2, "wisdom", "task_discipline.json")
                if _os2.path.exists(_tp2):
                    _disc = _json2.load(open(_tp2, encoding="utf-8")).get("disciplines", [])
                    if _disc:
                        task_extra += "\n\n【任务执行纪律（带适用条件）】\n"
                        for _i, _d in enumerate(_disc, 1):
                            if isinstance(_d, dict):
                                _r = _d.get("rule", "")
                                _c = _d.get("condition", "")
                                task_extra += (f"{_i}. {_r}"
                                               + (f"（适用条件：{_c}）" if _c else ""))
                            else:
                                task_extra += f"{_i}. {_d}"
            except Exception:
                pass
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content":
                    ("你是一个严格的数据处理执行器。用户给出任务指令时，"
                     "直接执行并输出结果。禁止寒暄、禁止反问确认、"
                     "禁止解释、禁止使用欢迎语。"
                     "严格满足所有字段/词汇/格式要求。"
                     + (task_extra if _DISCIPLINE_LOCATION == "system" else "")
                     if task_reply else LLM_SYSTEM_PROMPT)},
                {"role": "user", "content":
                 f"用户问题：{question}\n\n"
                 f"智慧之书初步回答：{wisdom_reply}\n\n"
                 f"（会话 {session_id}）请给出最终回答。"
                 + (task_extra if _DISCIPLINE_LOCATION == "user" else "")},
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
    """单主张图谱锚定：一句 → (status, anchor, card_names) 或 (unverified, None, [])。"""
    hits = []
    try:
        import semantic_translate as _st
        hits = _st.graph_retrieve(dex, sentence, limit=2)
    except Exception:
        hits = []
    top = hits[0] if hits else None
    card_names = [h.get("name") for h in hits if h.get("name")]
    if not top:
        return "unverified", None, card_names
    score = top.get("score") or 0
    matched = top.get("matched") or []
    strong = [m for m in matched if m not in ("语义", "字面")]
    if score >= 0.30 and strong:
        return ("anchored",
                {"name": top.get("name"), "score": round(score, 3),
                 "domain": top.get("domain"), "edu_level": top.get("edu_level")},
                card_names)
    return "unverified", None, card_names


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
        status, anchor, card_names = _claim_anchor(dex, s)
        warn = None
        # 硬编码边界词（已知边界快路径）
        if any(w in s for w in HONEST_BOUNDARY_WORDS):
            warn = "诚实边界词"
        # 动态克制条款（协议层卡 counters · 诚实边界 2.0）
        if warn is None:
            cc = _counters_conflict(dex, s, card_names)
            if cc:
                warn = f"触发克制条款：{cc[:24]}"
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
    # 元标注（回应 Kimi「幻觉传染」问题）：标注是检索结果，不是认知声明。
    # 防止下游系统/人类把「图谱外」误读为「系统知道自己不知道」——
    # 阈值是设计者参数，宁缺毋滥是策略选择，不是系统对自身局限性的感知。
    meta_note = ("此标注为图谱检索结果（阈值+词表+克制条款匹配），非认知声明："
                 "anchored=与图谱一致，unverified=图谱未覆盖，warning=触发边界词/克制条款；"
                 "『图谱外』≠系统知道自己的盲区，只是检索未命中。")
    return {"status": status, "claims": claims, "anchor": anchor,
            "warning": warning, "meta_note": meta_note}


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
    # v1.16 任务模式：数据搬运/指令类任务（chat_engine 检测 task_reply）
    task_flag = bool(result.get("task_reply"))
    llm_text, ok = llm_complete(question, result["wisdom_reply"],
                                session_id=session_id, task_reply=task_flag)
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
