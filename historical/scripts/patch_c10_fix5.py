# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '"女的管好家", "分工有错", "家务分工公平", "全职主妇价值",'
    new = ('"女的管好家", "分工有错", "家务分工公平", "全职主妇价值",\n'
           '                "怎么让家务", "家务分工",')
    assert old in src
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
