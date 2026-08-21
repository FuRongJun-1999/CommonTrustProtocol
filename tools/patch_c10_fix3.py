# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '"读书还有用", "选专业不后悔", "学历和能力",'
    new = '"读书还有用", "选专业不后悔", "学历和能力",\n                "怎么选专业", "选专业才",'
    assert old in src
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
