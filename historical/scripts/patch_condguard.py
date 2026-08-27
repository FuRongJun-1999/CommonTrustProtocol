# -*- coding: utf-8 -*-
"""从条件词防护移除「太空」——误伤「太空探索」等正常概念。"""
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '"气压", "高压", "低压", "潜水", "太空", "深海"'
    new = '"气压", "高压", "低压", "潜水", "深海"'
    n = src.count(old)
    src = src.replace(old, new)
    open(path, "w", encoding="utf-8").write(src)
    print(f"patched {n} 处: {path}")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\chat_engine.py")
