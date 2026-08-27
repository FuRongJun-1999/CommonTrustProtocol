# -*- coding: utf-8 -*-
"""round13 触发词补盲：
感冒 +感冒不吃药（决胜儿童用药）、光合作用 +叶子为什么绿/叶子是绿的/植物为什么/植物要晒太阳（决胜补钙）、
遗传 +长得不一样/长得不像/不像父母（决胜成年兄弟姐妹）、萌发 +浇水/种子浇水/就会发芽/不发芽
"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "感冒": ['感冒', '感冒了', '受凉', '着凉', '感冒是', '为什么会感冒', '感冒怎么办',
            '流感', '重感冒', '感冒药', '鼻塞', '流鼻涕', '打喷嚏', '咳嗽',
            '喉咙痛', '嗓子疼', '发烧', '退烧', '怎么预防感冒', '感冒怎么好得快',
            '感冒不吃药', '不吃药能好'],
    "光合作用": ['叶子变绿', '植物晒太阳', '光合作用', '叶子为什么绿', '叶子是绿的',
                '植物为什么', '植物要晒太阳', '叶子为什么是绿', '为什么叶子绿'],
    "遗传": ['像爸爸', '像妈妈', '长得像', '遗传', '长得不一样', '长得不像',
             '不像父母', '像父母'],
    "萌发": ['种子发芽', '发芽了', '萌发', '浇水', '种子浇水', '就会发芽',
             '不发芽', '为什么发芽', '怎么发芽'],
}
for theme, lst in UPD.items():
    m = re.search(r'"%s":\s*\[[^\]]*\]' % theme, src)
    assert m, theme
    new = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in lst))
    src = src[:m.start()] + new + src[m.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("OK:", {k: len(v) for k, v in UPD.items()})
