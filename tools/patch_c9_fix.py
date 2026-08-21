# -*- coding: utf-8 -*-
"""补 v7 剩余变体。"""
def patch(path):
    src = open(path, encoding="utf-8").read()
    pairs = [
        # 代理人战争：小国怎么在大国博弈中自保
        ('"小国自保", "选边站"],',
         '"小国自保", "选边站",\n                "大国博弈中", "怎么自保", "自保"],'),
        # 宗教传统：为什么有些传统/现代生活冲突/怎么共存
        ('"传统习俗", "传统文化", "老规矩"],',
         '"传统习俗", "传统文化", "老规矩",\n                "传统和现代生活", "传统和现代", "怎么共存",\n                "有些传统", "传统冲突"],'),
        # 太空探索：花那么多钱值吗/殖民地争夺/该怎么合作
        ('"登月", "火星"],',
         '"登月", "火星",\n                "花那么多钱", "值吗", "殖民地", "该怎么合作"],'),
        # 基因编辑：能治绝症为什么不放开
        ('"设计婴儿", "优生学"],',
         '"设计婴儿", "优生学",\n                "为什么不放开", "放开", "能治绝症"],'),
        # 脑机接口：能治瘫痪为什么不全力推进
        ('"读脑", "意念控制"],',
         '"读脑", "意念控制",\n                "全力推进", "为什么不全力", "治瘫痪"],'),
    ]
    for old, new in pairs:
        assert old in src, f"未找到: {old[:30]}"
        src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
