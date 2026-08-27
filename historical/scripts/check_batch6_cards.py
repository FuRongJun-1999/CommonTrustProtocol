# -*- coding: utf-8 -*-
"""检查知识考古批次6 的 15 张卡是否已入图谱（新测试集来源三依据）。"""
import sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8")
db = r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db"
c = sqlite3.connect(db)
cards = ["复分析", "群论", "随机微分方程", "生成函数", "有限元方法", "共轭梯度法",
         "张量分解", "概率图模型", "高斯过程", "最优传输", "微分几何", "数值线性代数",
         "短时傅里叶变换", "排队论", "马尔可夫链蒙特卡洛"]
for name in cards:
    rows = c.execute("SELECT id, substr(content,1,60) FROM nodes WHERE content LIKE ? LIMIT 1",
                     (f"%{name}%",)).fetchall()
    if rows:
        print(f"✓ {name}: {rows[0][1]}...")
    else:
        print(f"✗ {name}: 未入图谱")
c.close()
