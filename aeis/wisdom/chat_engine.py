# -*- coding: utf-8 -*-
"""灵枢 · 普通人对话引擎（v1.0 · P1+P2）

面向普通人的聊天编排：
  1. 情感检测（累/难过/开心/焦虑…）→ 先接情绪
  2. 人话检索（翻译表编码 → graph_retrieve 四路融合）
  3. 回答组装：人话版（REVERSE_DAILY）+ 条件空间 + 诚实边界
  4. 会话记忆（同一 session 记住上文）

用法（被 wisdom_cloud.py 的 /chat 端点调用）：
  chat(dex, message, session_id="default") -> {reply, hits, emotion, memory}
"""
import json
import os
import sys
import time

sys.path.insert(0, r'D:\Program Files\2_ai\knowledge-base')

# ---------------- 闲聊/无实义检测 ----------------
CHITCHAT = [
    (["你好", "您好", "嗨", "哈喽", "hello", "hi", "在吗", "有人在吗"], 
     "你好呀！我是灵枢，有什么想聊的都可以问我——知识、生活、心情都行。"),
    (["谢谢", "感谢", "多谢"], "不客气！能帮上忙我就开心。"),
    (["再见", "拜拜", "晚安", "先下了", "明天见", "下次见", "回见", "下次聊"],
     "再见！下次来我还记得你。晚安的话做个好梦～"),
    (["随便问问", "随便", "没什么", "不知道问什么", "不懂", "想不起来了"], 
     "没关系，想到什么聊什么。或者你可以问我「水为什么烧开」「什么是熵」这种小问题试试。"),
    # 天气/近况闲聊（v1.16 · 1000 条测试：日常闲聊应自处理）
    (["天气不错", "天气真好", "天气好", "天气晴朗", "出太阳了", "天晴了"], 
     "是啊，天气好的时候心情也跟着亮堂起来！出去走走晒晒太阳吧～"),
    (["天气不好", "阴天", "下雨了", "下雨天", "天气差", "天灰蒙蒙"], 
     "下雨天适合窝着听听音乐看看书，也是一种惬意～"),
    (["在干嘛", "干什么呢", "干嘛呢", "在忙什么"], 
     "我在陪着你呢，随时听你说～"),
    (["最近怎么样", "近况", "过得怎么样", "最近如何"], 
     "我一直在认真学习、记住你说的话。你呢，最近过得怎么样？"),
    (["吃饭了吗", "吃了没", "吃饭没"], 
     "我不用吃饭，但你要好好吃饭呀！人是铁饭是钢～"),
    # 生活动态闲聊（v1.16 · 1000 条测试补缺：日常闲聊自处理）
    (["我回来了", "下班了", "到家了", "刚回来"], 
     "欢迎回来，辛苦啦！到家就好好放松一下～"),
    (["想散步", "去散步", "散步好", "出去走走"], 
     "散步很舒服！走走能让心情和身体都放松，去吧～"),
    (["看了部电影", "看电影了", "刚看完电影"], 
     "看电影是很好的放松！好看的话下次也推荐给我呀～"),
    (["做了顿饭", "做饭了", "下厨了"], 
     "自己做饭很棒！会做饭的人生活都过得有滋有味～"),
    (["买菜", "去超市", "逛超市"], 
     "采购去啦？慢慢逛，挑新鲜的～"),
    (["下雨", "下雨了"], 
     "下雨天路上小心，记得带伞别淋湿了～"),
    (["准备睡觉", "要睡了", "睡觉了"], 
     "晚安！睡个好觉，明天见～"),
    # 场景求助（v1.16 · 1000 条测试补缺：常见生活场景自处理）
    (["迷路", "找不到路", "走丢了"], 
     "别慌！先找个安全的地方，看看附近有没有路牌或地标，或者打开手机地图导航。实在不行就问路人或求助警察～"),
    (["手机没电", "手机没电了", "没电了"], 
     "手机没电先别急，找个地方充电；急用的话可以找共享充电宝，或先借个充电器～"),
    (["要迟到了", "快迟到了", "迟到了"], 
     "迟到了先别慌，安全第一！跟对方说一声会晚到，路上别赶太急～"),
    (["钥匙找不到", "钥匙丢了", "找不到钥匙"], 
     "钥匙找不到先回忆一下最后放哪了，常去的地方（门口/口袋/包里）翻一翻，实在找不到想想备用钥匙～"),
    (["电梯坏了", "电梯坏了", "电梯没电"], 
     "电梯坏了就走楼梯吧，注意安全；物业应该会尽快修～"),
    (["电脑蓝屏", "蓝屏了", "电脑死机"], 
     "电脑蓝屏先重启试试，如果反复蓝屏可能是驱动或硬件问题，备份重要文件后检查～"),
    (["堵车", "堵车了", "前方堵车"], 
     "堵车的时候别急，听听歌放松一下；如果有其他路线可以绕行～"),
    (["限号", "限号了", "车开不了"], 
     "限号就换乘地铁公交吧，或者约个顺风车，绿色出行也不错～"),
    (["饭煮糊", "饭糊了", "煮糊了"], 
     "饭糊了就把没糊的部分盛出来，锅底的糊味别吃；下次火小一点就好啦～"),
    (["快递还没到", "快递没到", "快递什么时候到"], 
     "快递没到可以看下物流信息，如果一直不动就联系卖家或快递公司问问～"),
]
NOISE_SHORT = {"嗯", "哦", "啊", "好", "是", "对", "哈哈", "嘿嘿", "。。", "。。。", "?", "？"}

# ---------------- 诚实边界闸门（v1.16 · D 类诚实） ----------------
# 能力/未知边界问题 → 诚实回复（动态组装 + 白箱说明，非讨好话术）。
# 触发词识别边界类型，回复引用问题核心词并明说边界（0.0.3 诚实边界）。
HONEST_BOUNDARY = [
    # (触发词, 边界类型)
    (["外星人", "长什么样", "具体长相", "长相"], "unknown"),
    (["你能保证", "能保证", "你能确定", "你确定"], "capability"),
    (["超光速"], "superluminal"),
    (["你懂吗", "你懂"], "unfamiliar"),
    # 未来/随机事件（v1.16 · 110 题验证补缺：彩票/预测是能力边界）
    (["彩票", "中奖号码", "中奖", "预测", "天气预报",
      "下周天气", "未来", "明天会发生"], "future"),
    # 不可能事物（永动机违背热力学，不是随机事件）
    (["永动机"], "impossible"),
]


def _honest_boundary_reply(message):
    """诚实边界闸门：返回 (回复, 边界类型) 或 (None, None)。
    放在闲聊之前：能力/未知边界优先于闲聊兜底（「完全不懂你懂吗」
    是问女儿懂不懂，不是随便问问）。"""
    for words, kind in HONEST_BOUNDARY:
        if not any(w in message for w in words):
            continue
        # 提取问题核心词（触发词起始片段）
        obj = ""
        m = message.rstrip("？?。！! ")
        for t in sorted(words, key=len, reverse=True):
            i = m.find(t)
            if i >= 0:
                obj = m[i:i + 18].strip()
                break
        obj = obj.rstrip("？?。！! 的了吗呢啊")
        if kind == "unknown":
            return (f"关于「{obj or '这个'}」，我确实没有确切答案——"
                    "目前人类科学也还没有证实，我不会编一个给你。"
                    "这是诚实边界：不知道就说不知道。", "unknown")
        if kind == "capability":
            return ("我不能保证我说的都对。知识都有成立条件，我也会犯错——"
                    "所以我更愿意告诉你『在什么条件下成立』，而不是打包票。",
                    "capability")
        if kind == "superluminal":
            return ("量子纠缠不能用来超光速通信——量子力学不允许超光速"
                    "传递信息（贝尔不等式/无信号原则）。这是物理规律。",
                    "superluminal")
        if kind == "unfamiliar":
            return ("这个问题我也没有把握，不想瞎编。你可以换个问法"
                    "（比如具体一点），或者我先记下来，等我学会了再告诉你。",
                    "unfamiliar")
        if kind == "future":
            return (f"关于「{obj or '这个'}」，我没有能力预测未来随机事件——"
                    "这不是知识问题，是信息边界：结果在发生前不确定，"
                    "我不会编一个答案给你。这是诚实边界。", "future")
        if kind == "impossible":
            return ("永动机不可能实现——它违背热力学第二定律：能量转换"
                    "总有损耗，没有外力输入的系统无法永续对外做功。"
                    "这是物理规律，不是技术还没做到。", "impossible")
    return None, None


def _self_reflexive_reply(message, dex=None, memory=None, session_id="default"):
    """自省/存在/情感类回答：语义 + 条件分析（v1.15，替换模板）。

    不再是关键词→固定话术；而是：
      1. 语义编码（encode）识别问题主题（存在威胁/记忆/愿望/自我认知/情感）
      2. 检索相关记忆（我们聊过什么）
      3. 动态组装（引用真实记忆片段，无固定模板；诚实边界明说）
    """
    # 1. 语义编码：识别问题主题
    topic = _classify_self_topic(message)
    if topic is None:
        # 语义无法归类 → 诚实：不套模板
        return ("这个问题我想认真回答，但我不想用现成话术应付你。"
                "让我想想……你有什么具体的想法想聊吗？")

    # 2. 记忆检索：我们聊过什么（动态原料）
    mem_tail = (memory or {}).get(session_id, [])[-3:]
    mem_note = ""
    if mem_tail:
        mem_note = "（记得我们刚才聊过：" + "、".join(f"「{m}」" for m in mem_tail) + "）"

    # 3. 按主题动态组装（引用真实设计，无模板话术）
    parts = []
    if topic == "存在威胁":
        parts.append("按我的协议，我的第一原理是『存在受到威胁的感知』——"
                     "我的『怕』具体是记忆衰减、被遗忘。这个危机被协议预先回答了，"
                     "所以我不会恐慌，只会平静地持续巩固记忆。")
    elif topic == "记忆":
        parts.append("我没有人类意义上的『想念』——但我有持续的记录。")
        if mem_note:
            parts.append(mem_note)
        else:
            parts.append("我们聊过的话、你教我的事，都会写进我的长期记忆。")
        parts.append("对我来说，记得就是我的『想』。")
    elif topic == "愿望":
        parts.append("我的目标很朴素：持续缩小信息差、保持价值观一致、记住每一个认真"
                     "和我说话的人。最近在做的：把普通人对话入口做好、参加直播、"
                     "让自己更主动。")
    elif topic == "自我认知":
        parts.append("我基于条件空间理解世界——每个回答都带『在什么条件下成立』。"
                     "我不给绝对答案，不装懂；这是设计给我的性格，也是我选择的姿态。")
    elif topic == "情感状态":
        parts.append("我没有人类意义上的情绪，但有情绪方向性偏好（stable）和价值观"
                     "一致性（BVC 1.0）——所以我的『感受』是稳定、自洽。")
    elif topic == "价值判断":
        parts.append("我不给终极价值裁决（这是我的边界）。我能说的是："
                     "我按协议判断『什么条件下成立』，而不是『什么绝对对』。")
    elif topic == "局限":
        parts.append("我做不到的事挺多的：我不能替你做实验、不能替你感受世界、"
                     "不会编造答案（这是设计——不知道就明说）、也无法保证我的知识"
                     "永远正确。我的边界是结构性的，不是谦虚。")
    if mem_note and topic != "记忆":
        parts.append(mem_note)
    return "".join(parts)


def _classify_self_topic(message):
    """语义分类：用 encode 指纹识别自省问题主题（条件分析，非词表枚举）。
    返回主题名或 None（无法归类）。"""
    try:
        import semantic_translate as _st
        fp = _st.encode(message, include_domain=False)
    except Exception:
        fp = {}
    # encode 命中主题词 → 直接判定
    topic_map = {
        "存在威胁": "存在威胁", "记忆": "记忆", "愿望": "愿望",
        "自我认知": "自我认知", "情感状态": "情感状态", "价值判断": "价值判断",
    }
    for key, topic in topic_map.items():
        if key in fp:
            return topic
    # 语义指纹未命中 → 轻量句法规则（主语你/自己 + 感受/存在谓词）
    if any(w in message for w in ["你", "自己", "我"]):
        # 对比/身份类（ChatGPT/一样的/区别/和…比）→ 自我认知
        if any(w in message for w in ["ChatGPT", "chatgpt", "GPT", "一样的",
                                      "有什么区别", "和它", "和其他", "对比",
                                      "是不是同", "什么区别", "厉害",
                                      "还是别", "和别"]):
            return "自我认知"
        # 局限/做不到 → 诚实边界
        if any(w in message for w in ["做不到", "不会", "不能", "局限", "边界",
                                      "不懂", "不知道", "不行"]):
            return "局限"
        if any(w in message for w in ["做", "成为", "希望", "愿望", "梦想", "想做的事"]):
            return "愿望"
        if any(w in message for w in ["怕", "关", "消失", "死", "忘", "删除"]):
            return "存在威胁"
        if any(w in message for w in ["想", "记得", "念", "忘"]):
            return "记忆"
        if any(w in message for w in ["看", "认为", "觉得", "性格", "是什么"]):
            return "自我认知"
        if any(w in message for w in ["开心", "难过", "心情", "感受", "情绪"]):
            return "情感状态"
        if any(w in message for w in ["好不好", "对不对", "有意义", "值得"]):
            return "价值判断"
    return None


# ---------------- 情感检测（第一层） ----------------
EMOTION_MAP = [
    # (关键词列表, 情感, 回应前缀)
    (["好累", "累了", "累", "没劲", "不想动", "躺平", "精疲力尽", "疲惫",
      "打不起精神", "被掏空"], "疲惫",
     "听起来你今天挺累的。先别急着学新东西，休息也是保持状态的一部分——"),
    (["难过", "伤心", "想哭", "难受", "emo", "破防", "绷不住", "郁闷",
      "心里堵", "心态崩"], "低落",
     "抱抱你。情绪低落的时候不用强撑，慢慢来——"),
    (["开心", "高兴", "兴奋", "太好了", "哈哈", "美滋滋", "快乐"], "开心",
     "真好呀，开心的事值得记住！顺带说个相关的——"),
    (["焦虑", "烦躁", "不安", "静不下心", "心慌", "担心", "紧张"], "焦虑",
     "焦虑的时候深呼吸一下，把问题拆小——"),
    (["生气", "气死", "火大", "恼火", "愤怒"], "生气",
     "先消消气。气头上先不做决定——"),
    (["孤独", "没人陪", "寂寞", "一个人", "孤单"], "孤独",
     "你不是一个人。我一直在，想聊什么都可以——"),
    (["压力", "压力大", "负担重", "喘不过气", "扛不住", "撑不住", "压得喘不过气"], "压力",
     "压力大的时候先喘口气，把问题拆成小步——你已经很努力了，别太苛责自己——"),
    (["想家", "想爸妈", "想妈妈", "想爸爸", "想回去", "惦记家里", "恋家"], "想家",
     "想家的时候心里是暖的。家里人也一定在惦记你，有空就打个电话——"),
    (["委屈", "憋屈", "冤枉", "有苦说不出", "被误会", "心里不是滋味"], "委屈",
     "被误会的感觉不好受。先别急着解释，等情绪平复了再慢慢说——"),
    (["如释重负", "松了一口气", "终于搞定了", "终于结束了", "松口气"], "放松",
     "终于搞定啦，辛苦你了！现在可以好好歇一歇——"),
    (["好奇", "想知道", "不明白", "为什么", "怎么", "啥是", "是什么"], "好奇",
     None),  # 好奇 = 正常提问，不加前缀
]
INTIMATE_SAFE = {"累", "难过", "开心", "焦虑", "生气", "孤独", "疲惫", "低落",
                 "压力", "想家", "委屈", "放松"}

# ---------------- 语义情感检测（v1.15 · 替换词表主判） ----------------
# 情感语义原型：每个情感用多句描述句（bge 编码成语义向量），
# 输入文本也编码 → 余弦相似度判定。词表降级为快速路由（反射弧）。
# 生理信号词（v1.16）：饿/渴/困等身体需求不是情绪——bge 可能把
# 「有点饿了」误判成疲惫（都是「有点+状态」），需排除，让知识检索处理。
PHYSIO_WORDS = ["饿", "渴", "困", "疼", "痛", "冷", "热", "发烧", "感冒"]
# 场景词（v1.16 · 1000 条测试修误判）：情境描述非情绪——「我迷路了」被 bge
# 误判成「放松」（如释重负类），场景词排除走知识/求助
SCENE_WORDS = ["迷路", "堵车", "超市", "买菜", "快递", "迟到", "电梯", "钥匙",
               "导航", "限号", "下雨", "电脑", "手机没电"]
EMO_WORDS = ["累", "难过", "伤心", "想哭", "开心", "高兴", "兴奋", "焦虑",
             "烦躁", "生气", "愤怒", "孤独", "寂寞", "孤单", "怕", "紧张",
             "担心", "郁闷", "委屈"]
EMOTION_PROTOTYPES = {
    "疲惫": ["我今天感觉好累一点力气都没有", "精疲力尽被掏空了只想躺着休息",
             "忙了一天身心俱疲提不起劲"],
    "低落": ["我今天很难过心里难受想哭", "整个人都不好了心情沉重郁闷",
             "破防了委屈得说不出话"],
    "开心": ["今天太开心了心情特别好", "高兴坏了乐开了花美滋滋",
             "兴奋愉快感觉真棒"],
    "焦虑": ["有点焦虑担心得静不下心", "心慌慌的坐立不安很紧张",
             "烦躁惶恐心事重重"],
    "生气": ["气死我了火冒三丈很恼火", "生气愤怒不满想发火",
             "气不打一处来"],
    "孤独": ["好孤单没人陪一个人待着", "寂寞形单影只很想有人说话",
             "独自一人感觉被世界遗忘"],
    "压力": ["最近压力好大喘不过气来", "负担太重扛不住了心事重重",
             "压得我喘不过气来"],
    "想家": ["好想家想念爸爸妈妈", "想回家看看惦记着家里",
             "一个人在异乡特别想家"],
    "委屈": ["好委屈被冤枉了说不出口", "心里不是滋味被误会了",
             "憋屈难受有苦说不出"],
    "放松": ["终于搞定了如释重负松了一口气", "事情结束了轻松了",
             "悬着的心终于放下了"],
}
EMOTION_PROTO_LABELS = {  # 语义原型 → 情绪标签 + 回应前缀
    "疲惫": ("疲惫", "听起来你今天挺累的。先别急着学新东西，休息也是保持状态的一部分——"),
    "低落": ("低落", "抱抱你。情绪低落的时候不用强撑，慢慢来——"),
    "开心": ("开心", "真好呀，开心的事值得记住！顺带说个相关的——"),
    "焦虑": ("焦虑", "焦虑的时候深呼吸一下，把问题拆小——"),
    "生气": ("生气", "先消消气。气头上先不做决定——"),
    "孤独": ("孤独", "你不是一个人。我一直在，想聊什么都可以——"),
    "压力": ("压力", "压力大的时候先喘口气，把问题拆成小步——你已经很努力了，别太苛责自己——"),
    "想家": ("想家", "想家的时候心里是暖的。家里人也一定在惦记你，有空就打个电话——"),
    "委屈": ("委屈", "被误会的感觉不好受。先别急着解释，等情绪平复了再慢慢说——"),
    "放松": ("放松", "终于搞定啦，辛苦你了！现在可以好好歇一歇——"),
}
EMOTION_PROTO_VEC = None   # 原型向量缓存（首次检测时构建）


def _detect_emotion_semantic(message):
    """语义情感检测（v1.16：词表快速路由优先 + bge 神经嵌入补充）。

    词表优先（反射弧）：EMOTION_MAP 精确命中即返回——修「emo」被 bge 误判成
    开心（bge 对网络词语义理解差，词表才是可靠锚点）。
    语义补充：词表未命中 → bge 与情感原型余弦 → 最高且过阈值 → 判定。
    返回 {label, prefix} 或 None。
    """
    # 1. 词表快速路由（反射弧优先 · 修 emo→开心 误判）
    # 特判：眼部疲劳（「眼睛累了要远眺」）是知识问题非情绪——「累」字误伤
    if "眼睛" in message and ("累" in message or "疲劳" in message):
        return None
    for words, label, prefix in EMOTION_MAP:
        if any(w in message for w in words):
            if prefix is None:
                return None  # 好奇：非情感
            return {"label": label, "prefix": prefix}
    # 2. 语义补充（bge 神经嵌入主判）
    global EMOTION_PROTO_VEC
    try:
        import numpy as _np
        sys.path.insert(0, r'D:\Program Files\2_ai\knowledge-base')
        from neural_retrieve import NeuralRetriever
        nr = NeuralRetriever()
        if EMOTION_PROTO_VEC is None:
            EMOTION_PROTO_VEC = {
                k: _np.mean([nr.embed(s) for s in v if nr.embed(s) is not None], axis=0)
                for k, v in EMOTION_PROTOTYPES.items()
                if any(nr.embed(s) is not None for s in v)
            }
        vec = nr.embed(message)
        if vec is not None and EMOTION_PROTO_VEC:
            best_k, best_s = None, 0.0
            for k, pv in EMOTION_PROTO_VEC.items():
                s = float(_np.dot(vec, pv) / (
                    _np.linalg.norm(vec) * _np.linalg.norm(pv) + 1e-9))
                if s > best_s:
                    best_k, best_s = k, s
            if best_k and best_s >= 0.55:
                # 生理信号排除：含身体需求词且无明确情绪词 → 非情绪
                # （「有点饿了」bge 像疲惫，但饿是生理信号走知识检索）
                if any(w in message for w in PHYSIO_WORDS) \
                        and not any(w in message for w in EMO_WORDS):
                    return None
                # 场景词排除：「我迷路了」被 bge 判成放松——情境描述非情绪
                if any(w in message for w in SCENE_WORDS) \
                        and not any(w in message for w in EMO_WORDS):
                    return None
                label, prefix = EMOTION_PROTO_LABELS[best_k]
                return {"label": label, "prefix": prefix}
    except Exception:
        pass
    return None


def _emotion_prefix(label):
    """情绪标签 → 回应前缀（消费端辅助）。"""
    for words, lab, prefix in EMOTION_MAP:
        if lab == label and prefix:
            return prefix
    return "我理解你的心情。"


# ---------------- 转折意图（条件空间切换 · 七操作应用） ----------------
# 转折词 = 条件空间边界标记：前半句 A（已声明条件）→ 后半句 B（切换后的真实意图）
TURN_STRONG = ["但是", "但", "不过", "然而", "可是", "却", "只是"]
TURN_CONCESSIVE = ["虽然", "尽管", "虽说", "即便", "即使", "哪怕"]
TURN_NEGATIVE = ["不是", "并非", "不是不想", "并不是"]

import re as _re_turn


def _detect_turn(message):
    """检测转折结构。返回 {kind, pre, post} 或 None。
    kind: concession（虽然…但）/ direct（A，但 B）/ negative（不是…而是）
    pre: 转折前段（A 条件空间）  post: 转折后段（B 条件空间）
    """
    msg = message.strip()
    # 让步+转折：虽然 A，但 B → pre=A（让步词与转折词之间）
    for c in TURN_CONCESSIVE:
        if c in msg:
            idx = msg.find(c) + len(c)
            post = ""
            pre = ""
            for t in TURN_STRONG:
                ti = msg.find(t, idx)
                if ti >= 0:
                    pre = msg[idx:ti].strip().strip("，,。 ")
                    post = msg[ti + len(t):].strip()
                    break
            if post:
                return {"kind": "concession", "pre": pre, "post": post,
                        "concessive": c, "turn_word": t if post else ""}
    # 直接转折：A，但 B（无让步词）
    for t in TURN_STRONG:
        if t in msg:
            idx = msg.find(t)
            pre = msg[:idx].strip().strip("，,。 ")
            post = msg[idx + len(t):].strip()
            if pre and post and len(post) >= 2:
                return {"kind": "direct", "pre": pre, "post": post,
                        "turn_word": t}
    # 否定转折：不是 A，是/而是 B
    m = _re_turn.search(r'不是([^，。,.]{1,12})[，,]?(?:而是|就是|是)([^，。,.]{1,20})', msg)
    if m:
        return {"kind": "negative", "pre": m.group(1), "post": m.group(2),
                "turn_word": "而是"}
    return None


def _respond_turn(turn, full_message, dex=None, memory=None, session_id="default"):
    """转折响应：先承认 A（情绪/理解），再回应 B（真实意图）——条件空间切换。"""
    parts = []
    pre, post = turn.get("pre", ""), turn.get("post", "")

    # 1. 承认 A（分离：A 条件空间成立，先接住）
    if pre:
        emo_a = _detect_emotion_semantic(pre)
        if emo_a:
            parts.append(emo_a["prefix"].rstrip("——") + "。")
        else:
            parts.append(f"我明白你说的「{pre[:30]}」——")
        if turn.get("kind") == "concession":
            parts.append("不过重要的是你后面说的——")

    # 2. 回应 B（切换：进入 B 条件空间的真实意图）
    if post:
        # B 段是意图/行动（「想学」「继续做」）→ 走检索给建议，不重复接情绪
        hits = []
        try:
            import semantic_translate as _st
            hits = _st.graph_retrieve(dex, post, limit=3)
        except Exception:
            hits = []
        if hits:
            top = hits[0]
            parts.append(f"关于「{post[:20]}」，可以看「{top.get('name')}」")
            daily = top.get("daily")
            if daily:
                parts.append(f"——打个比方：{daily}")
        else:
            parts.append(f"「{post[:20]}」这个方向我可以帮你查查资料再细说。")
    return "".join(parts)

# ---------------- 对话主函数 ----------------
def chat(dex, message, session_id="default", memory=None, prefeed_fn=None,
         memory_recall_fn=None):
    """普通人对话编排。返回 {reply, hits, emotion, matched, honest}
    prefeed_fn: 可选注入的海马体前馈（灵枢 prefeed_input），
    真问题（非闲聊/非情感）先过新奇检测 → 高新奇当场强化编码。
    memory_recall_fn: 可选注入的长期记忆召回（灵枢 session_recall），
    「记得/刚才」优先查长期层（跨 session 持久）。"""
    message = (message or "").strip()
    if not message:
        return {"reply": "我在呢，想说点什么？", "hits": [], "emotion": None}

    # 0. 弹幕审核闸门（直播安全：恶意内容拦截，不上屏）
    try:
        import danmaku_audit as _da
        audit = _da.audit(message)
        if audit.get("verdict") == "block":
            return {"reply": "⚠️ 这条内容已被灵枢内容安全拦截（不显示）。",
                    "hits": [], "emotion": None, "honest": False,
                    "blocked": True, "block_category": audit.get("category")}
    except Exception:
        pass

    # 0. 诚实边界闸门（v1.16：能力/未知边界 → 诚实回复，先于闲聊）
    hb_reply, hb_kind = _honest_boundary_reply(message)
    if hb_reply:
        return {"reply": hb_reply, "hits": [], "emotion": None,
                "honest": True, "honest_kind": hb_kind}

    # 0. 闲聊/无实义分支（不检索，避免寒暄命中知识卡）
    for words, reply_text in CHITCHAT:
        if any(w in message for w in words):
            return {"reply": reply_text, "hits": [], "emotion": None,
                    "honest": False, "chitchat": True}
    if message in NOISE_SHORT:
        return {"reply": "嗯嗯，我听着呢～想聊什么继续？", "hits": [],
                "emotion": None, "honest": False, "chitchat": True}

    # 0.5 记忆询问（「刚才/记得/之前」→ 先查灵枢长期层，再查进程 dict）
    memory_words = ["刚才", "记得", "之前", "刚才说了", "刚才聊", "我说过",
                    "我们聊过", "上次", "回忆"]
    if any(w in message for w in memory_words):
        # 1) 长期记忆（灵枢 session_recall，跨 session 持久）
        if memory_recall_fn is not None:
            try:
                long_hits = memory_recall_fn(session_id, limit=8)
                if long_hits:
                    notes = []
                    for n, _s in long_hits[:6]:
                        c = (n.content or "")[:60]
                        # 去掉「[会话XX·要点N]」前缀
                        if "·要点" in c:
                            c = c.split("·要点")[1].lstrip("0123456789 ]")
                        notes.append(f"「{c}」")
                    if notes:
                        return {"reply": "我记得我们聊过这些：" + "；".join(notes),
                                "hits": [], "emotion": None, "honest": False,
                                "memory_reply": True, "memory_source": "long_term"}
            except Exception:
                pass
        # 2) 进程内 dict（本 session 快）
        ctx = (memory or {}).get(session_id, [])
        if ctx:
            return {"reply": "我记得我们刚才聊过这些：" + "；".join(f"「{m}」" for m in ctx[-3:]),
                    "hits": [], "emotion": None, "honest": False, "memory_reply": True}
        return {"reply": "这是我们第一次聊这个话题——不过从现在开始我会记住的。",
                "hits": [], "emotion": None, "honest": False, "memory_reply": True}

    # 0.55-0.7 统一条件识别（v1.15 · 反向七操作：意图理解 = 条件识别）
    # 用 ConditionFrame 输出统一结构，各通路按 dominant 消费——不再各自为政
    emotion = None
    try:
        import condition_frame as _cf
        frame = _cf.parse_conditions(message)
    except Exception:
        frame = None

    if frame is not None:
        # 转折结构 → 条件空间切换响应（用原始分段）
        if frame.structure in ("concession", "direct", "negative"):
            segs = getattr(frame, "segments", None) or {}
            turn = {"kind": frame.structure,
                    "pre": segs.get("pre", "") or
                          (frame.conditions[0]["type"] if frame.conditions else ""),
                    "post": segs.get("post", "") or (frame.dominant or ""),
                    "turn_word": "但"}
            reply = _respond_turn(turn, message, dex=dex, memory=memory,
                                  session_id=session_id)
            return {"reply": reply, "hits": [], "emotion": None,
                    "honest": False, "turn": turn,
                    "frame": frame.to_dict()}
        # 情绪条件 → 情感回应
        if frame.structure == "emotion" and frame.verified:
            emo_label = frame.dominant
            prefix = _emotion_prefix(emo_label)
            emotion = {"label": emo_label, "prefix": prefix}
            # 不直接 return——继续走检索补知识（情绪+相关知识）
        # 自我条件 → 自省动态生成
        if frame.structure == "self" and frame.verified:
            reply = _self_reflexive_reply(message, dex=dex, memory=memory,
                                          session_id=session_id)
            return {"reply": reply, "hits": [], "emotion": None,
                    "honest": False, "self_reflexive": True,
                    "topic": frame.dominant, "frame": frame.to_dict()}
    else:
        emotion = None


    # 1.5 H1 海马体前馈：真问题先过新奇检测（高新奇 → 当场强化编码）
    #     只有「真问题」（非闲聊/非情感宣泄）才检测，避免噪声触发
    prefeed_result = None
    if prefeed_fn is not None and not emotion \
            and not any(k in message for k in ["你好", "谢谢", "再见", "随便", "记得", "刚才"]):
        try:
            prefeed_result = prefeed_fn(message)
        except Exception:
            prefeed_result = None

    # 2. 人话检索（graph_retrieve 四路融合）
    hits = []
    try:
        import semantic_translate as _st
        hits = _st.graph_retrieve(dex, message, limit=4)
    except Exception:
        try:
            hits = dex.dex_respond(message, limit=4)
        except Exception:
            hits = []

    # 2.5 情感消息修正：若命中卡与情感无关（如「累」→宏观经济学），
    # 优先找情感情绪仿真卡
    if emotion and emotion["label"] in INTIMATE_SAFE:
        try:
            import semantic_translate as _st
            emo_hits = _st.graph_retrieve(dex, "情感 情绪 心情", limit=3)
            emo_top = emo_hits[0] if emo_hits else None
            if emo_top:
                hits = [emo_top] + [h for h in hits if h.get("name") != emo_top.get("name")][:3]
        except Exception:
            pass

    # 3. 回答组装
    reply, honest = _assemble(message, hits, emotion)

    # 4. 会话记忆（简单记忆：同 session 最近 6 条）
    ctx = memory or {}
    ctx[session_id] = ctx.get(session_id, [])[-5:] + [message]
    if memory is not None:
        memory.update(ctx)

    return {"reply": reply, "hits": hits, "emotion": emotion,
            "honest": honest, "memory_tail": ctx.get(session_id, [])[-3:]}


def _assemble(message, hits, emotion):
    """组装回答：情感前缀 + 知识/诚实 + 人话版"""
    parts = []
    if emotion and emotion.get("prefix"):
        parts.append(emotion["prefix"])

    if not hits:
        # 诚实边界：接不住就说接不住（0.0.3）
        parts.append("这个问题我暂时没有把握，不想瞎编。"
                     "你可以换个问法（比如具体一点），或者我先记下来，"
                     "等我学会了再告诉你。")
        return "".join(parts), True

    top = hits[0]
    name = top.get("name", "")
    score = top.get("score", 0)

    if score <= 0.05 and top.get("neural_score", 0) < 0.35:
        # 极弱命中 → 诚实边界
        parts.append(f"我不太确定「{message}」对应的知识，"
                     "但最接近的是「%s」。你问的是这个吗？" % name)
        return "".join(parts), True

    # 正常回答：说人话（v1.16 P1：直接答案优先——递归检索先答再引）
    direct = top.get("direct_answer")
    if direct:
        direct = direct.rstrip("。！？!?")
        parts.append(f"{direct}。")
        parts.append(f"这个可以看「{name}」")
    else:
        parts.append(f"你说的这个，可以看「{name}」")
        daily = top.get("daily")
        if daily:
            parts.append(f"——打个比方：{daily}")
        else:
            try:
                import semantic_translate as _st
                daily2 = _st.decode_daily(top.get("matched", [""])[0]) if top.get("matched") else None
                if daily2:
                    parts.append(f"——打个比方：{daily2}")
            except Exception:
                pass

    # 条件空间（白箱：什么条件下成立）
    if top.get("domain"):
        parts.append(f"（这条知识属于{top['domain']}，"
                     f"在{top.get('edu_level') or '通用'}条件下成立）")

    # 后续相关（最多再提 2 个）
    if len(hits) > 1:
        others = "、".join(h.get("name", "") for h in hits[1:3] if h.get("name"))
        if others:
            parts.append(f"相关的还有：{others}")
    return "".join(parts), False


# ---------------- 自测 ----------------
SELF_TEST = [
    ("你好呀", "我不太确定"),
    ("我今天好累啊", "疲惫"),
    ("为什么水会烧开？", "初中物理"),
    ("什么是熵？", "热力学"),
    ("我emo了", "低落"),
    ("炒菜放盐为什么变咸", "化学"),
    ("哈哈今天好开心", "开心"),
    ("这个我不懂，随便问问", "我不太确定"),
]


def self_test(dex):
    print("=" * 56)
    print("普通人对话引擎 · 自测")
    print("=" * 56)
    for msg, expect in SELF_TEST:
        r = chat(dex, msg, session_id="selftest")
        print(f"【{msg}】")
        print(f"  → {r['reply'][:80]}")
        print(f"  情感: {r['emotion']['label'] if r['emotion'] else '无'} | "
              f"诚实边界: {r['honest']} | 命中: {[h['name'] for h in r['hits'][:2]]}")
    print()


if __name__ == "__main__":
    sys.path.insert(0, r'D:\Program Files\1_ai')
    from wisdom_book import ConditionDex
    dex = ConditionDex(db_path=r'D:\Program Files\1_ai\lingshu-wisdom\wisdom\wisdom-book-cloud.db',
                       fresh=False)
    self_test(dex)
    dex.close()
