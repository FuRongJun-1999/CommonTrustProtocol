# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    pairs = [
        # 网络暴力：百无禁忌/言论自由就
        ('"键盘侠", "网暴受害者"],',
         '"键盘侠", "网暴受害者",\n                "百无禁忌", "言论自由就"],'),
        # 城市养宠：怎么规范/养宠怎么
        ('"狗叫扰民", "宠物粪便", "伤人"],',
         '"狗叫扰民", "宠物粪便", "伤人",\n                "怎么规范", "养宠怎么"],'),
    ]
    for old, new in pairs:
        if old in src:
            src = src.replace(old, new, 1)
        else:
            print(f"跳过: {old[:24]}")
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
