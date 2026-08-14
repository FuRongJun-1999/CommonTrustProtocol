#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检索增强回归（v1.14：同义词扩展 + 查询重叠率）
==============================================
词汇鸿沟缓解：用户查询（图像）与存储文本（视觉）词面不同也能召回。
check 框架。
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = 0
TOTAL = 0


def check(name, cond, detail=""):
    global PASS, TOTAL
    TOTAL += 1
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {detail}")
    else:
        print(f"  [FAIL] {name} {detail}")


def test_synonym_expand():
    from aeis.core import LayeredStore
    terms = LayeredStore.expand_query_terms("图像到语义")
    check("同义词展开（图像→视觉）", "视觉" in terms and "图像到语义" in terms,
          str(terms[:4]))
    check("同义词展开（语义→含义）", "含义" in terms)
    terms2 = LayeredStore.expand_query_terms("无关查询abc")
    check("无命中组保持原词", terms2 == ["无关查询abc"])


def test_synonym_recall():
    """词汇鸿沟：查询「图像识别」应召回内容为「视觉…检测」的节点。"""
    from aeis.api import Agent
    db = os.path.join(tempfile.mkdtemp(), "mem.db")
    agent = Agent(identity="检索测试", db_path=db)
    agent.remember("视觉语义识别 v1 实验：YOLO-World 开放词汇集成成功",
                   tags=["vision", "experiment"])
    agent.remember("今天天气很好适合散步", tags=["life"])
    r = agent.search("图像识别", 5)
    contents = [n.content for n, _ in r]
    check("同义词召回（图像→视觉）", any("视觉语义识别" in c for c in contents),
          str(contents[:2])[:60])
    check("无关节点不混淆", any("散步" in c for c in contents) is False)
    agent.close()


def test_overlap_ratio_ranking():
    """重叠率评分：相关节点分数显著高于无关节点。"""
    from aeis.api import Agent
    db = os.path.join(tempfile.mkdtemp(), "mem.db")
    agent = Agent(identity="检索测试2", db_path=db)
    agent.remember("语音对话能力：VAD 断句识别麦克风", tags=["voice"])
    agent.remember("睡眠巩固循环执行完成", tags=["sleep"])
    r = agent.search("语音识别", 5)
    check("有结果", len(r) > 0)
    top_content = r[0][0].content if r else ""
    check("语音查询命中语音节点", "语音对话" in top_content or "VAD" in top_content,
          top_content[:40])
    agent.close()


def test_basic_still_works():
    """原行为保留：精确子串仍召回。"""
    from aeis.api import Agent
    db = os.path.join(tempfile.mkdtemp(), "mem.db")
    agent = Agent(identity="检索测试3", db_path=db)
    agent.remember("飞轮蒸馏产出可复用模式", tags=["flywheel"])
    r = agent.search("飞轮蒸馏", 5)
    check("精确子串召回", len(r) >= 1 and "飞轮蒸馏" in r[0][0].content)
    agent.close()


def main():
    print("===== 检索增强回归（v1.14） =====")
    test_synonym_expand()
    test_synonym_recall()
    test_overlap_ratio_ranking()
    test_basic_still_works()
    print(f"\n===== 检索增强: {PASS}/{TOTAL} 通过 =====")
    return 0 if PASS == TOTAL else 1


if __name__ == "__main__":
    sys.exit(main())
