# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    pairs = [
        # 太空探索：对人类的意义
        ('"花那么多钱", "值吗", "殖民地", "该怎么合作"],',
         '"花那么多钱", "值吗", "殖民地", "该怎么合作",\n                "对人类的意义", "太空意义"],'),
        # 元宇宙：虚拟和现实怎么平衡
        ('"虚拟人生"],',
         '"虚拟人生",\n                "虚拟和现实", "怎么平衡", "现实怎么平衡"],'),
    ]
    for old, new in pairs:
        assert old in src, f"未找到: {old[:30]}"
        src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
