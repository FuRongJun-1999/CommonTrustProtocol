# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
import wisdom.semantic_translate as st

print("摩擦 cluster:", st.DOMAIN_SYNONYM_CLUSTERS.get("摩擦"))
print("摩擦 SYNONYM:", st.SYNONYM_CLUSTERS.get("摩擦"))
q = "为什么搓手会发热？"
# 检查 ALL_TABLE 里 搓手发热 是否在
print("搓手发热 in ALL_TABLE:", "搓手发热" in st.ALL_TABLE)
print("ALL_TABLE[搓手发热]:", st.ALL_TABLE.get("搓手发热"))
# 直接查 encode 的原始指纹（含所有键）
fp_all = st.encode(q)
print("fp all:", fp_all)
