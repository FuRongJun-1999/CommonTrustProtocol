# -*- coding: utf-8 -*-
"""补 v8 剩余变体。"""
def patch(path):
    src = open(path, encoding="utf-8").read()
    pairs = [
        # 职场性别：怎么打破/打破天花板
        ('"打破性别天花板", "性别平等",',
         '"打破性别天花板", "怎么打破", "性别天花板", "性别平等",'),
        # 家务分工：怎么让家务分工
        ('"家务分工公平", "全职主妇价值",',
         '"家务分工公平", "怎么让家务", "家务分工", "全职主妇价值",'),
        # 老年数字：多学学/懒得学
        ('"老人不会用", "扫码难", "老人手机", "数字鸿沟"],',
         '"老人不会用", "扫码难", "老人手机", "数字鸿沟",\n                "多学学", "懒得学", "是不是懒得学"],'),
        # 教育就业：怎么选专业
        ('"选专业不后悔", "学历和能力",',
         '"选专业不后悔", "怎么选专业", "学历和能力",'),
        # 网络暴力：百无禁忌
        ('"键盘侠", "网暴受害者"],',
         '"键盘侠", "网暴受害者",\n                "百无禁忌", "言论自由就"],'),
        # 城市养宠：怎么规范
        ('"养狗", "狗叫扰民", "宠物粪便", "伤人"],',
         '"养狗", "狗叫扰民", "宠物粪便", "伤人",\n                "怎么规范", "养宠怎么"],'),
    ]
    for old, new in pairs:
        assert old in src, f"未找到: {old[:30]}"
        src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
