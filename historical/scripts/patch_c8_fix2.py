# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '"维权成本", "打官司", "起诉", "消费者维权"],'
    new = ('"维权成本", "打官司", "起诉", "消费者维权",\n'
           '                "维权这么难", "这么难这么贵", "维权难这么贵"],')
    assert old in src
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
