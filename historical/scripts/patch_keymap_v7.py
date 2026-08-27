# -*- coding: utf-8 -*-
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '    "深度伪造": "tech-deepfake", "防灾准备": "disaster-dev",\n}'
    new = ('    "深度伪造": "tech-deepfake", "防灾准备": "disaster-dev",\n'
           '    "军备竞赛": "mil-race", "代理人战争": "mil-proxy",\n'
           '    "宗教传统": "relig-trad", "太空探索": "space-race",\n'
           '    "碳税": "carbon-tax", "元宇宙": "meta-identity",\n'
           '    "基因编辑": "gene-edit", "脑机接口": "brain-computer",\n}')
    assert old in src
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
