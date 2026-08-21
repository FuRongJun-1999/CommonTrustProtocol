# -*- coding: utf-8 -*-
"""检查考古批次1-5 的 74 张卡是否已入图谱（v2 考古题对应卡）。"""
import sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8")
db = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"
c = sqlite3.connect(db)
cards = ["KL散度", "信道容量", "率失真理论", "混沌", "蝴蝶效应", "自组织临界性",
         "标度律", "傅里叶变换", "小波变换", "工作记忆", "认知偏差", "元认知",
         "预测编码", "内稳态", "奇异值分解", "梯度下降", "贝叶斯推断", "凸优化",
         "谱图论", "VC维", "注意力机制", "Transformer", "强化学习", "元学习",
         "神经缩放定律", "囚徒困境", "纳什均衡", "效用理论"]
for name in cards:
    rows = c.execute("SELECT id, substr(content,1,50) FROM nodes WHERE content LIKE ? LIMIT 1",
                     (f"%{name}%",)).fetchall()
    if rows:
        print(f"✓ {name}: {rows[0][1]}...")
    else:
        print(f"✗ {name}: 未入图谱")
c.close()
