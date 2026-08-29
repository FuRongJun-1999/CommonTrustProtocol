# -*- coding: utf-8 -*-
"""test_route_cache.py · 路由缓存验证（存算融合步骤 2，2026-08-29）

- 正确性：缓存结果与直查一致
- 命中：二次查询走缓存（misses 不增）
- TTL 过期：过期后重算
- 命中率统计
"""
import sys, os, shutil, tempfile, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aeis"))
sys.path.insert(1, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aeis", "wisdom"))
from wisdom_book import ConditionDex
from route_cache import RouteCache

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
        print(f"[✔] {name}")
    else:
        fail_n += 1
        print(f"[✘] {name} {detail}")


tmp = tempfile.mkdtemp(prefix="rcache_")
try:
    # 拷贝一份库做测试（不污染主库指纹）
    import shutil
    db_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aeis", "wisdom", "wisdom-book-cloud.db")
    db_dst = os.path.join(tmp, "wisdom-book-cloud.db")
    shutil.copy(db_src, db_dst)
    dex = ConditionDex(db_path=db_dst, fresh=False)
    rc = RouteCache(dex, ttl_s=2.0)

    r1 = rc.route("问插入排序")
    n_miss1 = rc.stats["misses"]
    r2 = rc.route("问插入排序")
    check("正确性：缓存与直查一致", r1 == r2, "两路结果不同")
    check("命中：二次走缓存", rc.stats["hits"] == 1 and rc.stats["misses"] == 1,
          f"stats={rc.stats}")

    # TTL 过期
    time.sleep(2.2)
    rc.route("问插入排序")
    check("TTL 过期后重算", rc.stats["misses"] == 2, f"stats={rc.stats}")

    # 不同 limit 不同缓存键
    rc.route("问插入排序", limit=3)
    check("不同 limit 独立缓存", rc.stats["misses"] == 3, f"stats={rc.stats}")

    hr = rc.hit_rate()
    check("命中率统计可用", 0.0 <= hr <= 1.0, f"hit_rate={hr:.2f}")

    # 性能对比（缓存命中 vs 直查）
    t0 = time.time()
    for _ in range(20):
        rc.route("问插入排序")
    cached_ms = (time.time() - t0) / 20 * 1000
    t0 = time.time()
    rc.invalidate()
    from semantic_translate import card_route
    for _ in range(5):
        card_route(dex, "问插入排序", limit=1)
    direct_ms = (time.time() - t0) / 5 * 1000
    print(f"    缓存命中 {cached_ms:.2f}ms vs 直查 {direct_ms:.1f}ms")
    check("缓存快于直查", cached_ms < direct_ms, f"{cached_ms:.2f} vs {direct_ms:.1f}")
    dex.close()
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print("\n=== 判定 ===")
print(f"路由缓存验证: {pass_n}/{pass_n + fail_n}")
sys.exit(0 if fail_n == 0 else 1)
