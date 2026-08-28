# -*- coding: utf-8 -*-
"""token_ab_project_bench.py · T9 项目级 token 对照（6 领域小型项目）

荣 2026-08-28 指令：灵枢的递归反思验证机制（全局视角+元反思）本身有
token 开销（「首次增加」正常），白箱条件路由图提供确定性知识查找——
两者效果只在整体项目中体现。本实验按项目级总账统计：

  A 组（灵枢+白箱）：递归反思分析任务条件/所需知识/规则 → card_route
     确定性查卡（0 LLM token）→ 带卡上下文实现 → 严格验收 →
     不过带失败信息继续实现（≤5 轮）
  B 组（裸 LLM）：无白箱无灵枢直接实现 → 同一严格验收 → 同样循环

统计口径：验收通过后两组各自的 LLM token 总和（含分析与全部返工）。
同模型 glm-5.3-flash、同 temperature=0、同验收评分（确定性测试）。
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "aeis", "wisdom"))

MAX_ATTEMPTS = 5

# ============ 6 领域小型项目（任务 + 验收测试 + 白箱检索词） ============
PROJECTS = [
    {
        "name": "传输协议选择器",
        "domain": "计算机网络",
        "task": ("实现函数 choose_protocol(needs_reliability, realtime)，"
                 "返回字符串 'TCP' 或 'UDP'：需要可靠性返回 TCP（面向连接、"
                 "确认重传、有序交付），追求低延迟返回 UDP（无连接、开销小）；"
                 "两个条件都为 True 时可靠优先返回 TCP；两个条件都为 False 时"
                 "默认返回 UDP（轻量默认）。再实现 justify(choice) "
                 "返回一句话中文理由（须含所选协议名与『可靠』或『快』字）"),
        "knowledge_queries": ["TCP 和 UDP 的区别", "TCP三次握手"],
        "tests": [
            "assert ns['choose_protocol'](True, False) == 'TCP'",
            "assert ns['choose_protocol'](False, True) == 'UDP'",
            "assert ns['choose_protocol'](True, True) == 'TCP'",
            "assert ns['choose_protocol'](False, False) == 'UDP'",
            "j = ns['justify']('TCP'); assert 'TCP' in j and ('可靠' in j or '快' in j)",
        ],
    },
    {
        "name": "图度分布统计器",
        "domain": "数据结构·图",
        "task": ("实现函数 degree_distribution(edges, n)，edges 为无向边列表"
                 "（如 [[0,1],[1,2]]），n 为节点数（节点编号 0..n-1）。"
                 "方向相反的重复边（如 [0,1] 与 [1,0]）视为同一条边只计一次。"
                 "返回 dict："
                 "键为度值（相连边数），值为该度值的节点个数。孤立节点度 0 也要计入。"),
        "knowledge_queries": ["图的度分布", "图的度怎么统计"],
        "tests": [
            "assert ns['degree_distribution']([[0,1],[1,2]], 3) == {0:1, 1:2, 2:1}",
            "assert ns['degree_distribution']([[0,1],[1,0]], 2) == {1:2}",
            "assert ns['degree_distribution']([], 2) == {0:2}",
            "assert ns['degree_distribution']([[0,1],[0,2],[0,3]], 4) == {1:3, 3:1}",
        ],
    },
    {
        "name": "插入排序模块",
        "domain": "排序算法",
        "task": ("实现函数 insertion_sort(arr)，返回升序排列的新列表（不修改原列表，"
                 "逐个取元素插入前方已有序区间的正确位置）。再实现 is_sorted(arr) "
                 "返回布尔值判断列表是否升序。"),
        "knowledge_queries": ["插入排序", "插入排序思想"],
        "tests": [
            "a=[3,1,2]; assert ns['insertion_sort'](a)==[1,2,3] and a==[3,1,2]",
            "assert ns['insertion_sort']([])==[]",
            "assert ns['insertion_sort']([2,2,1])==[1,2,2]",
            "assert ns['insertion_sort']([5])==[5]",
            "assert ns['is_sorted']([1,2,2,3]) is True and ns['is_sorted']([2,1]) is False",
        ],
    },
    {
        "name": "CSV 字段处理",
        "domain": "字符串处理",
        "task": ("不使用内建 split/upper，手写实现：csv_fields(line, sep) 按 sep "
                 "切分字符串返回字段列表（保留空字段）；shout(words) 把字符串列表"
                 "每个元素转大写返回新列表（手写大写转换）。"),
        "knowledge_queries": ["Mini-Python str 方法", "问字符串方法"],
        "tests": [
            "assert ns['csv_fields']('a,b,c', ',')==['a','b','c']",
            "assert ns['csv_fields']('a,,c', ',')==['a','','c']",
            "assert ns['csv_fields']('abc', ',')==['abc']",
            "assert ns['shout'](['ab','c'])==['AB','C']",
            "assert ns['shout']([])==[]",
        ],
    },
    {
        "name": "租房预算计算器",
        "domain": "生活·租房",
        "task": ("实现函数 rent_budget(monthly_income)，按「租金预算上限为月收入的 "
                 "30%」返回可承受月租金上限（浮点，保留两位小数）。再实现 "
                 "affordable(monthly_income, rent) 返回布尔：rent 不超过上限为 True。"),
        "knowledge_queries": ["第一次租房要注意什么", "租房怎么选"],
        "tests": [
            "assert abs(ns['rent_budget'](10000)-3000.0)<0.01",
            "assert abs(ns['rent_budget'](5000)-1500.0)<0.01",
            "assert ns['rent_budget'](0)==0.0",
            "assert ns['affordable'](10000, 2999) is True",
            "assert ns['affordable'](10000, 3001) is False",
        ],
    },
    {
        "name": "夜醒应对协议",
        "domain": "健康·睡眠",
        "task": ("实现函数 night_wake_protocol()，返回应对半夜醒来的协议 dict，"
                 "必须包含：'look_phone'（布尔，半夜醒是否该看手机——不该）、"
                 "'action'（字符串，该做什么——缓慢呼吸等困意回来）、"
                 "'check_first'（字符串，持续易醒先查什么——睡前饮酒与咖啡因）。"),
        "knowledge_queries": ["半夜老是醒来怎么办", "夜里容易醒怎么办"],
        "tests": [
            "d = ns['night_wake_protocol']()",
            "assert not d['look_phone']",
            "assert '呼吸' in d['action']",
            "cf = d['check_first']; assert ('酒' in cf) or ('咖啡' in cf)",
        ],
    },
]

ANALYSIS_PROMPT = (
    "你是灵枢协议实例，执行递归反思验证机制的第一步——分析任务条件与知识需求。\n"
    "任务：{task}\n"
    "请以全局视角回答（200 字内）：①这个任务隐含的领域条件/必然事实是什么？"
    "②实现它需要哪些具体知识点或规则（逐条列出，作为知识检索词）？"
    "只输出分析，不要写代码。"
)

IMPL_PROMPT = (
    "实现以下任务，只输出一个 Python 代码块：\n{task}\n\n{context}"
    "{failing}"
)

FALLBACK_SYSTEM_A = "你是灵枢助手。简洁准确回答。"


def llm(system: str, question: str) -> tuple[str, dict]:
    key = os.environ.get("BIGMODEL_API_KEY", "")
    if not key:
        raise RuntimeError("BIGMODEL_API_KEY 未设置")
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
    u = data.get("usage", {})
    return (data["choices"][0]["message"]["content"] or "",
            {"prompt": u.get("prompt_tokens", 0),
             "completion": u.get("completion_tokens", 0)})


def strip_code_block(text: str) -> str:
    import re
    m = re.search(r"```(?:python)?\s*(.+?)```", text, re.S)
    return m.group(1).strip() if m else text.strip()


def run_tests(code: str, tests: list) -> tuple[bool, str]:
    """验收：failing 结构化（具体断言 + 修正提示），供下一轮精准修正。"""
    ns = {}
    try:
        exec(compile(code, "<impl>", "exec"), ns)
    except Exception as e:
        return False, (f"代码执行异常 {type(e).__name__}: {e}。"
                       "请确保所有要求的函数都已定义且可直接调用。")
    for t in tests:
        try:
            exec(compile(t, "<assert>", "exec"), ns)
        except AssertionError:
            return False, (f"断言失败: {t}\n"
                           "（对照断言检查返回值结构与边界 case，"
                           "注意 dict 键值与浮点精度）")
        except Exception as e:
            return False, f"测试异常: {t} → {type(e).__name__}: {e}"
    return True, ""


def main() -> int:
    from wisdom_book import ConditionDex
    from semantic_translate import card_route

    db = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")
    dex = ConditionDex(db_path=db, fresh=False)

    report = {"projects": [], "totals": {"A": 0, "B": 0}}
    for proj in PROJECTS:
        rec = {"name": proj["name"], "domain": proj["domain"],
               "A": {"tokens": 0, "attempts": 0, "passed": False},
               "B": {"tokens": 0, "attempts": 0, "passed": False}}

        # ================= A 组：灵枢递归反思 + 白箱查找 =================
        analysis, u = llm(ANALYSIS_PROMPT.format(task=proj["task"]),
                          "请开始分析。")
        rec["A"]["tokens"] += u["prompt"] + u["completion"]
        # 白箱确定性查找（0 LLM token）
        cards = []
        for kw in proj["knowledge_queries"]:
            for h in card_route(dex, kw, limit=1):
                da = h.get("direct_answer") or ""
                if h.get("_card_hit") and da:
                    cards.append(f"- {h.get('name')}: {da}")
                    break
        ctx_a = ("知识库条件卡（确定性参考，须遵循其中的规则与数值）：\n"
                 + "\n".join(cards)) if cards else ""
        failing = ""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            q = IMPL_PROMPT.format(task=proj["task"], context=ctx_a + "\n\n",
                                   failing=f"上次实现未通过验收：{failing}\n请修正。" if failing else "")
            code, u = llm("你只输出代码。", q)
            rec["A"]["tokens"] += u["prompt"] + u["completion"]
            ok, failing = run_tests(strip_code_block(code), proj["tests"])
            rec["A"]["attempts"] = attempt
            if ok:
                rec["A"]["passed"] = True
                break
        report["totals"]["A"] += rec["A"]["tokens"]

        # ================= B 组：裸 LLM（无白箱无灵枢） =================
        failing = ""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            q = IMPL_PROMPT.format(task=proj["task"], context="",
                                   failing=f"上次实现未通过验收：{failing}\n请修正。" if failing else "")
            code, u = llm("你只输出代码。", q)
            rec["B"]["tokens"] += u["prompt"] + u["completion"]
            ok, failing = run_tests(strip_code_block(code), proj["tests"])
            rec["B"]["attempts"] = attempt
            if ok:
                rec["B"]["passed"] = True
                break
        report["totals"]["B"] += rec["B"]["tokens"]

        report["projects"].append(rec)
        ratio = (rec["B"]["tokens"] / rec["A"]["tokens"]) if rec["A"]["tokens"] else 0
        print(f"[{proj['domain']}] A={rec['A']['tokens']}({rec['A']['attempts']}轮"
              f"{'✓' if rec['A']['passed'] else '✗'}) "
              f"B={rec['B']['tokens']}({rec['B']['attempts']}轮"
              f"{'✓' if rec['B']['passed'] else '✗'}) 倍率={ratio:.2f}")
        json.dump(report, open(os.path.join(HERE, "token_ab_project_report.json"),
                               "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    dex.close()

    ta, tb = report["totals"]["A"], report["totals"]["B"]
    print(f"\n=== 6 领域项目总账 ===\nA 灵枢+白箱: {ta} tok\nB 裸 LLM: {tb} tok\n"
          f"总 token 减少: {tb / ta if ta else 0:.2f} 倍")
    return 0


if __name__ == "__main__":
    sys.exit(main())
