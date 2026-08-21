# -*- coding: utf-8 -*-
"""v15 补盲修复：REVERSE_DAILY 加「买菜」键（PHRASE 表 term「买菜」命中时返回长直答，
覆盖之前卡内短条目「采购去啦？慢慢逛，挑新鲜的～」导致的 len<15 判定失败）。"""
def patch(path):
    src = open(path, encoding="utf-8").read()
    anchor = '    "儿童零花钱": "该不该给孩子零花钱、孩子乱花钱怎么办，是『金钱教育』vs『惯坏担心』的矛盾'
    assert anchor in src, "anchor missing"
    new = '''    "买菜": "买菜去哪儿买——按品类选渠道：①生鲜（菜/肉/鱼/水果）去菜市场/农贸市场（能挑能看：新鲜度肉眼可见，和摊贩熟还能帮你留好菜、砍价有空间）或超市生鲜区（品质稳定/明码标价/售后有保障）；②标品（米面油/纸巾/调料）超市/社区团购（规格统一、价格透明，团购还便宜）；③临时应急楼下便利店（贵一点但方便）。社区团购适合买『标准品』（便宜），生鲜谨慎（看不见摸不着，到手可能不新鲜）——组合买菜法：新鲜的去市场、省事的去超市、便宜的用团购，按需选渠道，既新鲜又实惠。核心：买菜没有完美渠道，只有按需组合——你重视新鲜就多跑菜市场，重视方便就超市团购，别让一种渠道绑架你的菜篮子",\n    ''' + anchor
    src = src.replace(anchor, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("patched")

patch(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
