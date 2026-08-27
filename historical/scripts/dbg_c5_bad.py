# -*- coding: utf-8 -*-
import sys, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
import semantic_translate as st
reply = st.REVERSE_DAILY.get("比较级", "")
BAD = ["Let me", "Actually,", "I think", "I should", "Since the",
       "The knowledge", "This is", "I'll", "So I", "In the context",
       "I want", "Let's", "I'm", "I would", "I can", "I need"]
for s in BAD:
    if s in reply:
        print(f"HIT: {s!r}")
print("reply head:", reply[:40])
