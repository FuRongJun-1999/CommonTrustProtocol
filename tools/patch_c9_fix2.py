# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    pairs = [
        # 太空探索簇：补「对人类的意义」等变体（锚点：地球上问题）
        ('"地球上问题", "搞太空", "太空资源", "殖民地争夺",',
         '"地球上问题", "搞太空", "太空资源", "殖民地争夺",\n                "对人类的意义", "太空意义", "花那么多钱", "该怎么合作",'),
        # 元宇宙簇：补「虚拟和现实」「怎么平衡」
        ('"元宇宙", "虚拟世界", "数字身份", "虚拟人生"],',
         '"元宇宙", "虚拟世界", "数字身份", "虚拟人生",\n                "虚拟和现实", "怎么平衡", "现实怎么平衡"],'),
    ]
    for old, new in pairs:
        assert old in src, f"未找到: {old[:30]}"
        src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
