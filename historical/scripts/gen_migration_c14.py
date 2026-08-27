# -*- coding: utf-8 -*-
"""c14 自然问法迁移测试集（物理常识 9 + 文学常识 3）归档"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "什么是频率？", "theme": "频率"},
    {"q": "频率和声音有什么关系？", "theme": "频率"},
    {"q": "什么是波？", "theme": "波"},
    {"q": "波需要介质吗？", "theme": "波"},
    {"q": "什么是振动？", "theme": "振动"},
    {"q": "振动和声音什么关系？", "theme": "振动"},
    {"q": "为什么声音不能在真空里传播？", "theme": "声音不能传播"},
    {"q": "为什么太空听不到声音？", "theme": "声音不能传播"},
    {"q": "什么是弹性？", "theme": "弹性"},
    {"q": "弹性形变和塑性形变有什么区别？", "theme": "弹性"},
    {"q": "什么是梁的弯曲？", "theme": "梁的弯曲"},
    {"q": "为什么混凝土梁要配筋？", "theme": "梁的弯曲"},
    {"q": "什么是混凝土？", "theme": "混凝土"},
    {"q": "混凝土为什么需要养护？", "theme": "混凝土"},
    {"q": "什么是能级？", "theme": "能级"},
    {"q": "电子为什么会跃迁？", "theme": "能级"},
    {"q": "什么是能带？", "theme": "能带"},
    {"q": "为什么导体能导电？", "theme": "能带"},
    {"q": "什么是唐诗？", "theme": "唐诗"},
    {"q": "李白和杜甫有什么区别？", "theme": "唐诗"},
    {"q": "什么是宋词？", "theme": "宋词"},
    {"q": "宋词和唐诗有什么区别？", "theme": "宋词"},
    {"q": "什么是绝句？", "theme": "绝句"},
    {"q": "绝句和律诗有什么区别？", "theme": "绝句"},
]
themes = ["频率", "波", "振动", "声音不能传播", "弹性", "梁的弯曲", "混凝土",
          "能级", "能带", "唐诗", "宋词", "绝句"]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_c14.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_c14", "themes": themes, "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS), "题,", len(themes), "主题")
