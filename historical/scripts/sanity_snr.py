# -*- coding: utf-8 -*-
"""端到端 sanity：信噪比改动后正常对话无回归"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
from aeis.roleplay_chat import LingshuChat
lc = LingshuChat(data_dir=r'D:\Program Files\2_ai\knowledge-base\roleplay_data')
r1 = lc.respond('什么是碳中和？')
print(f"知识问答: route={r1.get('route')} len={len(r1['reply'])}")
r2 = lc.respond('帮我写一首关于春天的诗', session_id='snr-e2e')
print(f"开放问题: route={r2.get('route')} len={len(r2['reply'])}")
print(f"  首60字: {r2['reply'][:60]!r}")
lc.close()
