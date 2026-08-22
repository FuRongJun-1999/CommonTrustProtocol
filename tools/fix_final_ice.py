# -*- coding: utf-8 -*-
"""收官：移除结冰簇的 冰块（属熔化——"冰块化水"应路由熔化），补 烧水声音/冰水混合 触发词"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "结冰": ['结冰', '结冰了', '冻成冰', '水面结冰', '河面结冰', '湖面结冰', '为什么结冰',
            '结冰是', '上冻', '冻住了', '水结冰', '结冰温度', '冰是', '冰怎么',
            '冰能浮', '冰浮', '冰浮在水', '冬天水管冻裂', '水只冻住表层',
            '冰凌', '冻实', '水管冻裂', '冰面', '冻裂'],
    "沸腾": ['水烧开了', '水开了', '烧开了', '烧开', '水烧开', '水滚了', '沸腾', '咕嘟咕嘟',
            '冒大泡', '为什么烧开', '水开', '开水', '高压锅', '沸点', '高原煮饭', '煮不熟',
            '就开', '烧水的声音', '100度就开', '咕嘟', '烧水会有声音', '水响'],
    "熔化": ['冰化了', '雪化了', '蜡烛化了', '冰淇淋化了', '冰淇淋凉快', '雪糕化了',
            '雪糕凉快', '冰棍化了', '冰棒化了', '冰淇淋', '雪糕', '冰棍', '熔化',
            '化水', '化了', '融化', '熔点', '冰块', '化得快', '化得慢', '冰水混合',
            '冰水混合物', '0度'],
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
