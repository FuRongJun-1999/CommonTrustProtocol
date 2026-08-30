# -*- coding: utf-8 -*-
"""test_template_catalog.py · 分层模板目录+条件采样器（模板生成引擎 V-TBE 前置）

对应：docs/模板生成引擎设计_v0.2.md · V-TBE.7（分层采样）/V-TBE.10（组合覆盖）。
被测：tools/template_catalog.py（纯标准库）。
"""
import os, sys, tempfile
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(ROOT), "tools"))  # ROOT=aeis，上级=项目根

from template_catalog import TemplateCatalog, LAYERS

passed = failed = 0
def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS {name}")
    else:
        failed += 1
        print(f"  FAIL {name} {detail}")

# ---- 目录构建（v0.2 论证规模：10 骨架×20 姿态×30 外表×15 细节）----
cat = TemplateCatalog("tbe")
for i in range(10):
    cat.register("L1_skeleton", f"skel_{i}", {"joints": i})
for i in range(20):
    cat.register("L2_pose", f"pose_{i}", {"angles": i})
for i in range(30):
    cat.register("L3_appearance", f"app_{i}", {"color": i})
for i in range(15):
    cat.register("L4_detail", f"det_{i}", {"pattern": i})

check("四层计数", cat.counts() == {"L1_skeleton": 10, "L2_pose": 20,
                                   "L3_appearance": 30, "L4_detail": 15},
      str(cat.counts()))
check("组合覆盖空间 90000（组合爆炸→组合乘法）",
      cat.combo_space() == 90000, str(cat.combo_space()))

# ---- V-TBE.7：分层采样（指定/随机/全枚举）----
s = cat.sample()
check("采样返回四层", len(s["layers"]) == 4 and "骨架" in s["summary"], s["summary"][:60])
s2 = cat.sample(picks={"L1_skeleton": "skel_3", "L2_pose": "pose_5"})
check("指定 picks 采样", s2["layers"]["L1_skeleton"]["id"] == "skel_3"
      and s2["layers"]["L2_pose"]["id"] == "pose_5")
import random
rng = random.Random(42)
ok = all(len(cat.sample(rng=rng)["layers"]) == 4 for _ in range(100))
check("100 组随机采样无歧义", ok)
combos = cat.sample_all(limit=100)
check("全枚举防爆上限", len(combos) == 100)

# ---- 层间耦合（条件关联显式记录，不强行解耦）----
cat.register("L4_detail", "det_bone", {"pattern": "bone"},
             conditions={"L1_skeleton": "skel_0"})
check("层间耦合条件关联", cat.list("L4_detail")[-1]["conditions"]
      .get("L1_skeleton") == "skel_0")

# ---- 持久化 roundtrip ----
tmp = os.path.join(tempfile.gettempdir(), "tbe_catalog_test.json")
cat.save(tmp)
cat2 = TemplateCatalog.load(tmp)
check("save/load roundtrip", cat2.counts() == cat.counts()
      and cat2.combo_space() == cat.combo_space()
      and cat2.sample()["summary"] == cat.sample()["summary"])
os.unlink(tmp)

# ---- 诚实边界：空层采样报错（条件链不完整显式化）----
try:
    TemplateCatalog("empty").sample()
    check("空层采样显式报错", False, "未抛异常")
except ValueError:
    check("空层采样显式报错", True)
try:
    cat.register("L9_x", "bad", {})
    check("未知层登记拒绝", False, "未抛异常")
except ValueError:
    check("未知层登记拒绝", True)

# ---- 验证闸 verify（V-TBE.8 主仓库侧：逐层比对+四态判定）----
v = cat.verify({"L1_skeleton": {"joints": 0}, "L2_pose": {"angles": 5},
                "L3_appearance": {"color": 9}, "L4_detail": {"pattern": 2}})
check("verify 全层匹配=ACCEPT", v["verdict"] == "ACCEPT" and v["matched"] == 4,
      str(v))
v2 = cat.verify({"L1_skeleton": {"joints": 0}, "L2_pose": {"angles": 999},
                 "L3_appearance": {"color": 9}, "L4_detail": {"pattern": 2}})
check("verify 半层匹配=DEFER", v2["verdict"] == "DEFER", str(v2["verdict"]))
v3 = cat.verify({"L1_skeleton": {"joints": 999}, "L2_pose": {"angles": 999},
                 "L3_appearance": {"color": 999}, "L4_detail": {"pattern": 999}})
check("verify 全不匹配=REJECT", v3["verdict"] == "REJECT", str(v3["verdict"]))
v4 = cat.verify({"L1_skeleton": {"joints": 0}})
check("verify 缺层=BLINDSPOT（没看到的不假装看到）",
      v4["verdict"] == "BLINDSPOT", str(v4["verdict"]))

print(f"\ntemplate_catalog 测试: {passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
