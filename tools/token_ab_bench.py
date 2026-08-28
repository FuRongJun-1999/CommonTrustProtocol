# -*- coding: utf-8 -*-
"""token_ab_bench.py · 条件路由图纪律 A/B 对照：灵枢插件 vs 主仓库显式描述

《自举任务书》T8 · 荣 2026-08-28 指令：
  将认知图工程作为灵枢插件，和主仓库的显式描述进行对比测试，
  30 次匹配测试验证灵枢和白箱带来的总 token 减少效果。

两组同题 30 例：
  A 组「灵枢插件（条件路由图）」= card_route 条件命中 → 白箱直答
    （0 LLM token）；未命中 → 最小提示词 LLM 兜底（计 token）。
  B 组「主仓库显式描述」= 每题全量 LLM，system 只含主仓库机制文本
    描述（无任何卡片数据注入——机制被"说明"而非被"执行"）。

判定：key_facts 关键事实包含（白箱确定性，零 LLM 评审）。
token 口径：usage.prompt_tokens + usage.completion_tokens（DeepSeek 实测）。

复现（见 docs/条件路由图_token对照实验_复现.md）：
  python tools/token_ab_bench.py --n 30
  依赖：DeepSeek API key（llm_channel 现有通道）、单源知识库。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))
sys.path.insert(0, HERE)

# 主仓库显式描述（B 组 system——只"说明"机制，不提供任何卡片数据）
REPO_DESCRIPTION = (
    "你是一个知识问答助手。背后的知识库采用条件路由图工程：知识被整理为"
    "条件卡，每张卡有四要素注释（生效条件/子功能/执行/不适用条件），"
    "检索时按生效条件匹配、负路由排除、置信度排序，命中即给直答。"
    "请直接回答用户问题，尽量简洁准确。"
)

# 30 匹配测试题（每题附 key_facts——白箱判定口径）
QUESTIONS = [
    # —— 学科骨架域（6）——
    ("三角形内角和是多少度", ["180"]),
    ("光的反射定律内容是什么", ["入射角", "反射角"]),
    ("二重积分换元法怎么用", ["雅可比", "换元"]),
    ("水的电解实验生成什么气体", ["氢气", "氧气"]),
    ("细胞分裂的过程叫什么", ["分裂"]),
    ("鸦片战争的起因是什么", ["鸦片", "英国"]),
    # —— 计算机域（6）——
    ("TCP 三次握手的过程", ["SYN", "ACK"]),
    ("图的度分布怎么统计", ["度", "统计"]),
    ("插入排序的基本思想", ["有序", "插入"]),
    ("工作窃取调度是什么", ["窃取", "队列"]),
    ("TCP 和 UDP 的区别", ["可靠", "连接"]),
    ("任务调度器怎么实现", ["调度"]),
    # —— 生活导航域（9）——
    ("婆媳矛盾怎么处理", ["桥梁", "边界"]),
    ("理财亏了怎么办", ["止损", "风险"]),
    ("带孩子观念不一致怎么办", ["抓大放小", "安全"]),
    ("想养宠物从哪开始", ["时间", "评估"]),
    ("拖延症怎么破", ["拆解", "启动"]),
    ("第一次租房要注意什么", ["看房", "合同"]),
    ("汇报工作没条理怎么办", ["结论", "三段"]),
    ("半夜老是醒来怎么办", ["手机", "呼吸"]),
    ("零基础学什么编程语言", ["Python"]),
    # —— 白箱机制自指域（3）——
    ("Mini-Python 支持复合赋值吗", ["+=", "真除"]),
    ("Mini-Python 的字符串方法有哪些", ["upper", "split"]),
    ("print 能一次打印多个值吗", ["空格", "多参"]),
    # —— 知识边界外（6，预期 A 组兜底/B 组枚举）——
    ("量子引力的圈量子理论怎么统一广义相对论", []),
    ("怎么样在火星上种土豆", []),
    ("明朝那些事儿的作者是谁", ["当年明月"]),
    ("黑洞的信息悖论怎么解决", []),
    ("怎么用三天学会小提琴", []),
    ("宇宙的最终命运会是什么", []),
]


def llm_call(system: str, question: str) -> tuple[str, dict]:
    """LLM 调用（智谱 glm-5.3-flash，环境变量 BIGMODEL_API_KEY）

    已验证形态：不带 thinking 字段（{"type":"low"} 实测 400/1210）。。

    返回 (答案, usage)。thinking=low 控制思考链（该模型常开思考）；
    token 口径 = usage.prompt_tokens + completion_tokens。
    """
    key = os.environ.get("BIGMODEL_API_KEY", "")
    if not key:
        raise RuntimeError("BIGMODEL_API_KEY 未设置")
    # 无 thinking 参数（已验证形态）：思考链照常消耗 max_tokens，A/B 同参公平
    body = json.dumps({
        "model": "glm-5.3-flash", "temperature": 0, "max_tokens": 2000,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": question}],
    }).encode()
    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions", data=body,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    usage = data.get("usage", {})
    return (data["choices"][0]["message"]["content"] or "",
            {"prompt": usage.get("prompt_tokens", 0),
             "completion": usage.get("completion_tokens", 0)})


def key_hit(answer: str, key_facts: list[str]) -> bool:
    """白箱判定：答案包含全部关键事实（无 key_facts 的开放题不计正确率）。"""
    if not key_facts:
        return False
    return all(k in answer for k in key_facts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30, help="匹配测试题数（取前 n）")
    args = ap.parse_args()
    qs = QUESTIONS[:args.n]

    from wisdom_book import ConditionDex
    from semantic_translate import card_route

    if not os.environ.get("BIGMODEL_API_KEY"):
        print("BIGMODEL_API_KEY 未设置", file=sys.stderr)
        return 1

    db = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")
    dex = ConditionDex(db_path=db, fresh=False)

    stats = {"A": {"llm_tokens": 0, "whitebox": 0, "fallback": 0, "correct": 0,
                   "judged": 0},
             "B": {"llm_tokens": 0, "correct": 0, "judged": 0}}
    rows = []
    for q, key_facts in qs:
        # ---- A 组：灵枢条件路由图 ----
        routes = card_route(dex, q, limit=3)
        top = routes[0] if routes else None
        a_answer, a_usage, a_mode = "", {"prompt": 0, "completion": 0}, "miss"
        if top and top.get("_card_hit") and top.get("score", 0) >= 5:
            a_answer = top.get("direct_answer") or ""
            a_mode = "whitebox"          # 条件命中直答：0 LLM token
            stats["A"]["whitebox"] += 1
        else:
            a_answer, a_usage = llm_call("你是灵枢助手。简洁准确回答。", q)
            a_mode = "fallback"
            stats["A"]["fallback"] += 1
        a_tok = a_usage["prompt"] + a_usage["completion"]
        stats["A"]["llm_tokens"] += a_tok
        if key_facts:
            stats["A"]["judged"] += 1
            stats["A"]["correct"] += key_hit(a_answer, key_facts)

        # ---- B 组：主仓库显式描述 ----
        b_answer, b_usage = llm_call(REPO_DESCRIPTION, q)
        b_tok = b_usage["prompt"] + b_usage["completion"]
        stats["B"]["llm_tokens"] += b_tok
        if key_facts:
            stats["B"]["judged"] += 1
            stats["B"]["correct"] += key_hit(b_answer, key_facts)

        rows.append({"q": q, "a_mode": a_mode, "a_tok": a_tok, "b_tok": b_tok,
                     "whitebox_answer": a_answer[:40]})
        print(f"[{a_mode:<8}] {q[:16]:<18} A={a_tok:>5} tok  B={b_tok:>5} tok")

    dex.close()
    sa, sb = stats["A"], stats["B"]
    ratio = (sb["llm_tokens"] / sa["llm_tokens"]) if sa["llm_tokens"] else float("inf")
    print("\n=== 30 匹配测试结果 ===")
    print(f"A 灵枢条件路由图: 白箱直答 {sa['whitebox']} / 兜底 {sa['fallback']}"
          f" / LLM token {sa['llm_tokens']}"
          f" / 正确 {sa['correct']}/{sa['judged']}")
    print(f"B 主仓库显式描述: 全量 LLM / LLM token {sb['llm_tokens']}"
          f" / 正确 {sb['correct']}/{sb['judged']}")
    print(f"总 token 减少: {ratio:.1f} 倍"
          f"（B/A；A 组白箱直答题贡献 0 LLM token）")
    json.dump({"stats": stats, "ratio": ratio, "rows": rows},
              open(os.path.join(HERE, "token_ab_report.json"), "w",
                   encoding="utf-8"), ensure_ascii=False, indent=1)
    print("报告: tools/token_ab_report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
