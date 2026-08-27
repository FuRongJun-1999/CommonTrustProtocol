# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
src = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
print("降落伞 route present:", '"降落伞": "物理学"' in src)
print("降落伞 answer present:", '"降落伞": "为什么跳伞能安全落地' in src)
print("秋千 answer present:", '"秋千": "为什么秋千越荡越高' in src)
print("反射 upgrade:", "为什么镜子能照出自己" in src)
print("蒸发 upgrade:", "为什么湿衣服晾着会干" in src)
print("感冒 in DOMAIN cluster:", '"感冒": [' in src)
# 检查 DOMAIN_SYNONYM_CLUSTERS 里的 感冒
import re
m = re.search(r'"感冒":\s*\[([^\]]*)\]', src)
print("first 感冒 cluster tail:", m.group(0)[-80:] if m else "none")
