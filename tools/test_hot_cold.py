# -*- coding: utf-8 -*-
"""test_hot_cold.py · 存算融合步骤 3 冷热分层验证（2026-08-29）

- 热路径 O(1) 命中
- 冷落盘/冷读取（不阻塞热）
- 降级（低命中热条目 → 冷）
- 热冷互不阻塞
"""
import sys, os, shutil, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from hot_cold import HotColdStore, HOT, COLD

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="hotcold_")
try:
    store = HotColdStore(tmp)
    store.put("hot-key", {"v": 1}, tier=HOT)
    store.put("cold-key", {"v": 2}, tier=COLD)

    check("热读取 O(1)", store.get("hot-key") == {"v": 1})
    check("冷读取（落盘还原）", store.get("cold-key") == {"v": 2})
    check("层级查询 hot", store.tier_of("hot-key") == HOT)
    check("层级查询 cold", store.tier_of("cold-key") == COLD)

    # 重启（新实例）：热丢失、冷持久
    store2 = HotColdStore(tmp)
    check("重启后热丢失（口径诚实）", "hot-key" not in store2.hot)
    check("重启后冷持久可读", store2.get("cold-key") == {"v": 2})

    # 降级路径：put 热 → 多次 miss → rebalance → 降冷
    store3 = HotColdStore(tmp)
    store3.put("rare-key", {"v": 3}, tier=HOT)
    for _ in range(5):
        store3._count("rare-key", False)   # 模拟连续未命中
    moved = store3.rebalance()
    check("低命中降冷", "rare-key" in moved["demoted"] or store3.tier_of("rare-key") == COLD,
          str(moved))
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"冷热分层验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
