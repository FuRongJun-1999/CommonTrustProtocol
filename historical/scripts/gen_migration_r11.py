# -*- coding: utf-8 -*-
"""round11 自然问法迁移测试集（回声/影子/结冰）——固定归档 testsets/migration/"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
ITEMS = [
    {"q": "为什么在山谷里大喊会有回声？", "theme": "回声"},
    {"q": "空旷的房间里说话为什么有回音？", "theme": "回声"},
    {"q": "对着山洞喊话能听到回声吗", "theme": "回声"},
    {"q": "为什么山里有回音？", "theme": "回声"},
    {"q": "为什么隧道里喊话有回声？", "theme": "回声"},
    {"q": "为什么楼道里有回音？", "theme": "回声"},
    {"q": "为什么中午的影子比早晨短？", "theme": "影子"},
    {"q": "为什么早晨影子特别长？", "theme": "影子"},
    {"q": "影子是怎么形成的？", "theme": "影子"},
    {"q": "为什么路灯下影子会变长？", "theme": "影子"},
    {"q": "为什么影子会跟着我走？", "theme": "影子"},
    {"q": "为什么太阳底下影子朝一个方向？", "theme": "影子"},
    {"q": "为什么冬天河面会结冰？", "theme": "结冰"},
    {"q": "水为什么能冻成冰？", "theme": "结冰"},
    {"q": "为什么冰能浮在水面上？", "theme": "结冰"},
    {"q": "为什么湖面先结冰？", "theme": "结冰"},
    {"q": "为什么水管冬天会冻裂？", "theme": "结冰"},
    {"q": "为什么鱼塘的水只冻住表层？", "theme": "结冰"},
    # 漂移检查（应路由到别处而非本主题）
    {"q": "为什么窗户玻璃上会有白霜？", "theme": "凝华"},
    {"q": "为什么早上草地有露水？", "theme": "液化"},
]
with open(r"D:\Program Files\2_ai\CommonTrustProtocol\testsets\migration\natural_variants_r11.json", "w", encoding="utf-8") as f:
    json.dump({"name": "natural_variants_r11", "themes": ["回声", "影子", "结冰"], "items": ITEMS}, f, ensure_ascii=False, indent=1)
print("saved", len(ITEMS))
