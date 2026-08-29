# -*- coding: utf-8 -*-
"""test_ccg_triple · C2 CCG 三重注释单元测试（智能论 v3.4 6章.3）"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aeis'))
from ccg_triple import CCGTriple, COGNITION_ANNOTATION_EXAMPLE

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

ct = CCGTriple()

# C2-1: 完整注释（三要素齐全）→ complete
code_ann = """功能：计算斐波那契数列
生效条件：n ≥ 0；输入为整数
子功能：① 基准情形 ② 递归调用
执行：递归 + 记忆化缓存
不适用条件：n 为负数"""
r1 = ct.validate(code_ann, layer="code")
check("code annotation complete", r1["complete"], str(r1["missing_marks"]))

# C2-2: 知识层面注释
knowledge_ann = """功能：水沸点与气压的关系
生效条件：标准大气压或明确海拔
子功能：① 查气压 ② 算沸点
执行：经验公式 + 查表"""
r2 = ct.validate(knowledge_ann, layer="knowledge")
check("knowledge annotation complete", r2["complete"])

# C2-3: 认知层面注释（认知过程本身）
r3 = ct.validate(COGNITION_ANNOTATION_EXAMPLE, layer="cognition")
check("cognition annotation complete", r3["complete"], str(r3["missing_marks"]))

# C2-4: 缺失要素 → 不完整
partial = "功能：随便写写"
r4 = ct.validate(partial, layer="code")
check("incomplete when missing marks", not r4["complete"] and len(r4["missing_marks"]) == 3, str(r4["missing_marks"]))

# C2-5: 不适用条件识别（负路由输入）
check("not_applicable detected", r1["has_not_applicable"])

# C2-6: 批量校验覆盖率
items = [
    {"id": "code1", "text": code_ann, "layer": "code"},
    {"id": "know1", "text": knowledge_ann, "layer": "knowledge"},
    {"id": "cog1", "text": COGNITION_ANNOTATION_EXAMPLE, "layer": "cognition"},
    {"id": "bad1", "text": "功能：不完整", "layer": "code"},
]
rb = ct.validate_batch(items)
check("batch coverage", rb["coverage"] == 0.75, str(rb["coverage"]))

print(f"\nC2 result: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
