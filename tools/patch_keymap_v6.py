# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '    "网课效果": "edu-online", "鸡娃": "edu-chicken",\n}'
    new = ('    "网课效果": "edu-online", "鸡娃": "edu-chicken",\n'
           '    "法律维权": "law-rights", "疫苗犹豫": "health-vaccine",\n'
           '    "容貌焦虑": "psy-appearance", "城市孤独": "psy-lonely",\n'
           '    "留学选择": "edu-abroad", "人脸识别": "tech-face",\n'
           '    "深度伪造": "tech-deepfake", "防灾准备": "disaster-dev",\n}')
    assert old in src
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
