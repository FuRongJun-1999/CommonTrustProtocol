# -*- coding: utf-8 -*-
"""verify_cache.json 文件监视器：每 2 秒记录 md5 + a866 条目 ok 值，抓写回时刻。"""
import json, hashlib, time, os

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'aeis', 'data', 'verify_cache.json')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache_watch.log')
KEY = 'a866f668bd6f'
end = time.time() + 900  # 15 分钟
last = None
with open(OUT, 'a', encoding='utf-8') as f:
    while time.time() < end:
        try:
            raw = open(P, 'rb').read()
            md5 = hashlib.md5(raw).hexdigest()[:8]
            d = json.loads(raw)
            ent = d.get('a866f668bd6f4a1c048e16f684df69bf') or {}
            state = f"{md5}|a866_ok={ent.get('ok')}|entries={len([k for k in d if not k.startswith('_')])}"
        except Exception as e:
            state = f"ERR:{e}"
        if state != last:
            f.write(f"{time.strftime('%H:%M:%S')} {state}\n")
            f.flush()
            last = state
        time.sleep(2)
