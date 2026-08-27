# -*- coding: utf-8 -*-
"""LLM 自然表达触发词补全：拖延启动（人工终裁挑选干净口语触发词）"""
import re, ast, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
import semantic_translate as _st

# 人工终裁：从 LLM 自然变体提取的表达核心（专属拖延、非泛词）
NEW = ["拖到最后一刻", "磨蹭", "卡在哪", "静不下来", "明天再做",
       "不动手", "从哪下手", "拆成小块", "逼自己开始", "进入状态",
       "大项目", "脑子空白"]

# 冲突检查
others = {k: v for k, v in {**_st.DOMAIN_SYNONYM_CLUSTERS, **_st.SYNONYM_CLUSTERS}.items() if k != "拖延启动"}
for w in NEW:
    clash = [k for k, lst in others.items() if any(w == t for t in lst)]
    if clash:
        print(f"冲突: {w} -> {clash}")
print("冲突检查完成（无输出=干净）")
print("将加入:", NEW)
