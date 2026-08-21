# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '"老人不会用", "扫码难", "老人手机", "数字鸿沟"],'
    new = ('"老人不会用", "扫码难", "老人手机", "数字鸿沟",\n'
           '                "多学学", "懒得学", "是不是懒得学"],')
    assert old in src
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
