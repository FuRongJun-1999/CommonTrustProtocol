# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
from wisdom.chat_engine import CHITCHAT
q = "负数真实存在吗？"
for words, reply_text in CHITCHAT:
    for w in words:
        if w in q:
            print(f"MATCH: {w!r} in {q!r} -> {reply_text[:30]}")
print("---done---")
# NOISE_SHORT
try:
    from wisdom.chat_engine import NOISE_SHORT
    print("in NOISE_SHORT:", q in NOISE_SHORT)
except Exception as e:
    print("noise check err", e)
