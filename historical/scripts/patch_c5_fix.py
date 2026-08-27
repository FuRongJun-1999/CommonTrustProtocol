# -*- coding: utf-8 -*-
"""补 v3 最后 3 个变体。"""
def patch(path):
    src = open(path, encoding="utf-8").read()
    pairs = [
        ('"课外辅导", "补课", "辅导班", "孩子落后"],',
         '"课外辅导", "补课", "辅导班", "孩子落后",\n                "报了那么多", "补习班成绩", "成绩还是上不去"],'),
        ('"环保成本", "高耗能", "减排"],',
         '"环保成本", "高耗能", "减排",\n                  "转型又不倒闭", "怎么转型", "又不倒闭"],'),
        ('"能源安全", "石油"],',
         '"能源安全", "石油",\n                "怎么摆脱", "摆脱依赖", "单一能源的依赖"],'),
    ]
    for old, new in pairs:
        assert old in src, f"未找到: {old[:30]}"
        src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
