# -*- coding: utf-8 -*-
"""补 _KEY_TO_CONFLICT 的 v5 键。"""
def patch(path):
    src = open(path, encoding="utf-8").read()
    old = '    "消费主义": "soc-consumer", "内卷躺平": "soc-lieflat",\n}'
    new = ('    "消费主义": "soc-consumer", "内卷躺平": "soc-lieflat",\n'
           '    "AI替代工作": "ai-job", "AI创作版权": "ai-copyright", "算法偏见": "ai-bias",\n'
           '    "自由职业": "work-free", "远程办公": "work-remote", "生育成本": "fam-birth",\n'
           '    "熬夜": "health-night", "外卖健康": "health-takeout",\n'
           '    "网课效果": "edu-online", "鸡娃": "edu-chicken",\n}')
    assert old in src, "锚点未找到"
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
