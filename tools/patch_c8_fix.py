# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '"假视频", "伪造视频", "换脸"],'
    new = '"假视频", "伪造视频", "换脸",\n                "视频是不是假的", "识别视频", "是不是假的"],'
    assert old in src
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
