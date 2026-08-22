# -*- coding: utf-8 -*-
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

UPD = {
    "降落伞": ['降落伞', '跳伞', '降落', '慢慢落', '缓缓落下', '飘下来', '伞兵',
              '空中掉下来', '为什么跳伞', '安全落地', '空气阻力', '阻力',
              '小鸟摔不死', '摔不死', '从树上掉下来'],
    "秋千": ['秋千', '荡秋千', '荡起来', '越荡越高', '摆起来', '钟摆', '摆动',
             '来回摆', '摆一下', '为什么秋千', '荡高', '单摆', '能一直荡',
             '一直荡'],
    "蒸发": ['晾干了', '晾干', '晾', '水干了', '晒干了', '晒干', '衣服干了', '衣服晾干',
             '干了', '蒸发', '蒸发了', '水蒸气', '干得快', '晾衣服', '蒸发是', '为什么会干',
             '水洒', '不见了', '水不见了', '洒地上'],
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
