# -*- coding: utf-8 -*-
"""补 v5 最后 5 个变体。"""
def patch(path):
    src = open(path, encoding="utf-8").read()
    pairs = [
        ('"降低生育代价", "生不生听谁的",',
         '"降低生育代价", "生不生听谁的",\n                "降低生育的代价", "生育的代价", "到底该听谁的",\n                "生不生到底", "该听谁的",'),
        ('"几点睡算熬夜", "晚睡晚起规律",',
         '"几点睡算熬夜", "晚睡晚起规律",\n                "晚睡晚起是不是", "也算规律", "规律作息",'),
        ('"天天吃外卖", "外卖不健康",',
         '"天天吃外卖", "外卖不健康",\n                "真的不健康", "是不是不健康",'),
        ('"吃得健康不费时间",',
         '"吃得健康不费时间",\n                "吃得健康又", "健康又不费时间",'),
    ]
    for old, new in pairs:
        assert old in src, f"未找到: {old[:30]}"
        src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
