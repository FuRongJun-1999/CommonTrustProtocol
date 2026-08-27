# -*- coding: utf-8 -*-
"""清理影子/回声簇：
- 影子：保留黑影（LLM 自然词），删 被压成一个小/压成一个小黑/成一个小黑影/总是朝着跟（碎片）
- 回声：保留回响（真同义词），删 空房间/山谷/山洞/空房（泛位置词——会造成误路由，如"山洞里为什么冷"）
"""
import sys, re
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py"
src = open(p, encoding="utf-8").read()

SHADOW = [
    "影子", "影子的", "影子是", "影子怎么", "影子长短", "影子方向", "影子为什么",
    "影子会变", "中午影子", "早晨影子", "傍晚影子", "灯下影子", "影子拉长",
    "影子变短", "影子消失", "影子形状", "黑影",
]
ECHO = [
    "回声", "回音", "山谷回声", "喊话回声", "有回声", "没有回声", "回音壁",
    "声音反射", "为什么有回声", "空房间回声", "山洞回声", "回声是", "回响",
]

for theme, lst in (("影子", SHADOW), ("回声", ECHO)):
    new_block = '"%s": [%s]' % (theme, ", ".join('"%s"' % t for t in lst))
    m = re.search(r'"%s":\s*\[[^\]]*\]' % theme, src)
    assert m, theme
    src = src[:m.start()] + new_block + src[m.end():]

open(p, "w", encoding="utf-8").write(src)
import py_compile
py_compile.compile(p, doraise=True)
print("影子(%d)/回声(%d) 簇已清理" % (len(SHADOW), len(ECHO)))
