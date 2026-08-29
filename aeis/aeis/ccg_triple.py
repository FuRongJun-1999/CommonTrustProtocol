# -*- coding: utf-8 -*-
"""ccg_triple · 条件注释图三重注释（智能论 v3.4 · 6章.3）
============================================================================
CCG 既是代码的注释，也是知识的注释，还是认知的注释——同一条件论注释
结构作用于三个层面：

| 层面 | 注释对象 | 实 | 图 |
|---|---|---|---|
| 代码 | 函数/类 | 代码实现 | 条件代码图（代码能力索引）|
| 知识 | 知识卡/知识点 | 知识内容 | 条件知识图（知识卡注释索引）|
| 认知 | 认知过程/规则 | 认知机制 | 条件认知图（认知过程注释）|

条件论注释三要素（统一格式）：
  功能名 / 生效条件 / 子功能 / 执行

认知过程同样符合条件路由图：识别条件→路由知识→执行→验证→更新，
每一层都走四态判定与条件链——认知自身的注释即认知的条件代码图。

纯标准库 · 零外部依赖（D-005）
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional


# 三要素标记（与 KCCS 对齐 + 认知层面扩展）
MARKS = {
    "function": r"功能(名)?[:：]",
    "condition": r"生效条件[:：]",
    "subfunc": r"子功能[:：]",
    "execute": r"执行[:：]",
    "not_applicable": r"不适用条件[:：]",
}

LAYERS = ("code", "knowledge", "cognition")


class CCGTriple:
    """三重注释校验器：检查注释是否含条件论三要素。

    - validate(text, layer)：校验单条注释
    - validate_batch(items)：批量校验
    返回 {layer, complete, missing_marks, marks_found}
    """

    def __init__(self):
        pass

    def validate(self, text: str, layer: str = "knowledge") -> Dict:
        """校验注释完整性（三要素齐全 = 完整）。"""
        layer = layer if layer in LAYERS else "knowledge"
        found = {}
        for name, pattern in MARKS.items():
            found[name] = bool(re.search(pattern, text or ""))
        required = ["function", "condition", "subfunc", "execute"]
        missing = [m for m in required if not found[m]]
        return {
            "layer": layer,
            "complete": len(missing) == 0,
            "missing_marks": missing,
            "marks_found": found,
            "has_not_applicable": found["not_applicable"],
        }

    def validate_batch(self, items: List[Dict]) -> Dict:
        """批量校验：items = [{"text", "layer", "id"}]。"""
        results = []
        complete = 0
        for item in items:
            r = self.validate(item.get("text", ""), item.get("layer", "knowledge"))
            r["id"] = item.get("id", "")
            results.append(r)
            if r["complete"]:
                complete += 1
        return {"total": len(items), "complete": complete,
                "coverage": round(complete / max(1, len(items)), 4),
                "results": results}


# 认知层面注释示例（认知过程本身的条件注释）
COGNITION_ANNOTATION_EXAMPLE = """认知过程：条件路由（识别条件→路由知识→执行→验证→更新）
生效条件：存在可用知识路径；四态判定可执行
子功能：① 识别问题条件 ② 并行路由候选 ③ 收敛到资格候选 ④ 执行 ⑤ 验证反馈
执行：四态判定 + 两阶段并行收敛 + 负路由过滤 + 知识飞轮更新
不适用条件：无可用路径（BLINDSPOT）；条件空间未声明"""
