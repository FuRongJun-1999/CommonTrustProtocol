# -*- coding: utf-8 -*-
"""v18 补盲修复：①chat_engine 闲聊表移除「感谢」（「送礼是感谢老师」被当道谢答「不客气」）；
②银行簇加「银行服务」触发词（「银行服务怎么兼顾」无触发词路由到金融学卡）。"""
def patch_ce(path):
    src = open(path, encoding="utf-8").read()
    old = '    (["谢谢", "感谢", "多谢"], "不客气！能帮上忙我就开心。"),'
    new = '    (["谢谢", "多谢"], "不客气！能帮上忙我就开心。"),'
    assert old in src, "ce anchor missing"
    src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("chat_engine patched")

def patch_st(path):
    src = open(path, encoding="utf-8").read()
    old = '    "银行网点消失": ["银行网点", "网点", "银行都在手机上", "网点少",'
    new = '    "银行网点消失": ["银行网点", "网点", "银行都在手机上", "网点少",\n              "银行服务", "银行也要赚钱", "老人办事", "办业务"],'
    # 上面 new 重复了，直接用完整替换
    new2 = '''    "银行网点消失": ["银行网点", "网点", "银行都在手机上", "网点少",
              "银行服务", "银行也要赚钱", "老人办事", "办业务"],'''
    assert old in src, "st anchor missing"
    src = src.replace(old, new2, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("semantic_translate patched")

patch_ce(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\chat_engine.py")
patch_st(r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py")
