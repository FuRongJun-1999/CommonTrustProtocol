# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st
print("imported:", st.__file__)
print("has 影子:", "影子" in st.REVERSE_DAILY, "| has 结冰:", "结冰" in st.REVERSE_DAILY, "| has 回声:", "回声" in st.REVERSE_DAILY)

# 模拟 chat_engine 的 sys.path 行为
import wisdom.chat_engine as ce
print("chat_engine file:", ce.__file__)
# 看 chat_engine 内部 import 的 _st 是哪个
import importlib
print("knowledge-base stale check:")
kb = open(r"D:\Program Files\2_ai\knowledge-base\semantic_translate.py", encoding="utf-8").read()
print("  kb has 影子 key:", '"影子":' in kb)
sp = open(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py", encoding="utf-8").read()
print("  sp has 影子 key:", '"影子":' in sp)
