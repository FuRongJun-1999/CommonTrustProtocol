# -*- coding: utf-8 -*-
import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
import semantic_translate as st
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
qs = [
    ("法律定义", "什么是法律？"),
    ("法律定义", "法律和道德有什么区别？"),
    ("法律定义", "法律面前人人平等吗？"),
    ("规则意识", "什么是规则意识？"),
    ("规则意识", "为什么要遵守规则？"),
    ("规则意识", "规则和自由冲突吗？"),
    ("社会主义核心价值观", "社会主义核心价值观是什么？"),
    ("社会主义核心价值观", "国家层面是什么？"),
    ("社会主义核心价值观", "个人层面是什么？"),
    ("诚实守信", "什么是诚实守信？"),
    ("诚实守信", "为什么要诚实守信？"),
    ("诚实守信", "善意的谎言可以吗？"),
    ("自然选择", "什么是自然选择？"),
    ("自然选择", "适者生存是什么意思？"),
    ("自然选择", "自然选择和人工选择什么区别？"),
    ("运动补水", "运动后为什么要喝水？"),
    ("运动补水", "运动补水怎么补？"),
    ("运动补水", "为什么要补充电解质？"),
    ("细嚼慢咽", "为什么要细嚼慢咽？"),
    ("细嚼慢咽", "狼吞虎咽有什么坏处？"),
    ("晕车", "为什么会晕车？"),
    ("晕车", "晕车怎么办？"),
    ("晕车", "怎么预防晕车？"),
    ("打哈欠", "为什么会打哈欠？"),
    ("打哈欠", "打哈欠是困了吗？"),
    ("打哈欠", "打哈欠为什么会传染？"),
    ("出汗散热", "为什么会出汗？"),
    ("出汗散热", "出汗有什么用？"),
    ("出汗散热", "汗液蒸发为什么能降温？"),
    ("猫狗哺乳", "为什么猫和狗是哺乳动物？"),
    ("猫狗哺乳", "胎生和卵生什么区别？"),
    ("猫狗哺乳", "恒温是什么意思？"),
    ("跑步走路", "跑步和走路哪个消耗大？"),
    ("跑步走路", "走路能减肥吗？"),
    ("跑步走路", "跑步伤膝盖吗？"),
]
ok = 0
for theme, q in qs:
    fp = st.encode(q)
    keys = [k for k in fp if k in st.REVERSE_DAILY]
    r = agent.chat(q, session_id="c7-check")
    route = r.get("route", "?")
    reply = r.get("reply", "")
    hit = theme in keys
    ok += hit
    print(f"[{'HIT' if hit else 'MISS'}] {theme} | {q}")
    print(f"   fp={keys} route={route} | {reply[:34].replace(chr(10),' ')}")
print(f"--- fp hit: {ok}/{len(qs)} ---")
agent.close()
