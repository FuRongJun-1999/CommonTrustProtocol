# -*- coding: utf-8 -*-
"""c2 触发词补盲：处理 7 个劫持/缺口"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "中和反应": ['中和反应', '酸碱中和', '酸和碱反应', '中和', '胃酸', '胃药', '抗酸', '酸碱中和反应', '牙膏中和',
               '蚊虫叮咬', '叮咬处理', '蚁酸', '蜂蜇', '蜇了', '涂肥皂水'],
    "元素周期律": ['元素周期律', '周期律', '元素性质变化', '元素周期表', '周期表', '门捷列夫', '化学元素', '元素性质',
                '同族', '同一族', '同周期', '同一周期', '族性质', '周期和族'],
    "燃烧条件": ['燃烧需要', '燃烧条件', '怎么才能烧起来', '着火', '燃烧三要素', '可燃物', '着火点', '灭火三法', '燃烧三条件',
               '水能灭火', '怎么灭火', '灭火原理', '点不着', '什么能灭火', '为什么灭火'],
    "盐水融雪": ['盐融雪', '盐化雪', '撒盐融冰', '融雪剂', '盐水融雪', '撒盐融雪', '冰点降低', '盐水不结冰', '除冰',
                '撒盐雪', '雪就化', '盐为什么', '不结冰', '融雪'],
    "糖盐味道": ['糖和盐', '盐和糖', '糖盐味道', '为什么糖甜', '为什么盐咸', '糖为什么甜', '盐为什么咸', '味道', '味蕾',
               '糖是甜', '盐是咸', '糖甜', '盐咸', '甜的咸'],
    "蜂蜜防腐": ['蜂蜜不易变质', '蜂蜜不会坏', '蜂蜜防腐', '蜂蜜变质', '蜂蜜不坏', '蜂蜜为什么', '蜂蜜结晶', '蜂蜜保存', '高渗透压',
               '蜂蜜放', '不会坏', '蜂蜜会坏', '放很久', '蜂蜜水'],
}
for theme, lst in UPD.items():
    m = re.search(r'"%s":\s*\[[^\]]*\]' % theme, src)
    assert m, theme
    new = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in lst))
    src = src[:m.start()] + new + src[m.end():]

# 牛奶冷藏 移除 变质（劫持蜂蜜变质——变质是通用词，应靠长短语）
m = re.search(r'"牛奶冷藏":\s*\[[^\]]*\]', src)
assert m
milk = ['牛奶', '冷藏', '变质', '牛奶放冰箱', '牛奶容易坏', '牛奶怎么保存', '牛奶坏了', '牛奶放久', '鲜奶', '巴氏奶']
src = src[:m.start()] + '"牛奶冷藏": [%s]' % ", ".join('"%s"' % t for t in milk) + src[m.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK:", {k: len(v) for k, v in UPD.items()})
