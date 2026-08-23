# -*- coding: utf-8 -*-
"""全量回归 v44-v64（c16 pipeline 调用 · 稳态检测）"""
import sys, os, json, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages")
os.environ.setdefault("AEIS_DB", r"C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\wisdom-book-cloud.db")
from aeis.api import Agent

agent = Agent(identity="灵枢", db_path=os.environ["AEIS_DB"])
BAD_SIGNALS = ["Let me", "Actually,", "I think", "I should", "Since the",
               "The knowledge", "This is", "I'll", "So I", "In the context",
               "I want", "Let's", "I'm", "I would", "I can", "I need"]

KB = r"D:\Program Files\2_ai\knowledge-base"
summary = {}
all_ok = all_total = 0
t0 = time.time()
for ver in range(44, 65):
    path = os.path.join(KB, f"conflict_testset_v{ver}.json")
    if not os.path.exists(path):
        continue
    data = json.load(open(path, encoding="utf-8"))["items"]
    o = t = 0
    for i, item in enumerate(data, 1):
        q = item["q"]
        try:
            r = agent.chat(q, session_id=f"rg-{ver}-{i}")
            route = r.get("route", "?")
            reply = r.get("reply", "")
        except Exception as e:
            route, reply = "err", f"ERR {e}"
        bad = route in ("llm", "err", "self_fallback")
        if not bad:
            bad = any(s in reply for s in BAD_SIGNALS)
        if not bad and reply.startswith("你说的这个，可以看"):
            bad = True
        if not bad and len(reply) < 15:
            bad = True
        t += 1
        if not bad:
            o += 1
        else:
            print(f"  ✗ v{ver} [{item.get('domain','?')}/{item.get('stage','?')}] {q[:30]} | {route}")
    summary[f"v{ver}"] = f"{o}/{t}"
    all_ok += o; all_total += t
    print(f"v{ver}: {o}/{t} ({o/t*100:.0f}%) [{time.time()-t0:.0f}s]", flush=True)

print(f"\n=== 全量回归 v44-v64: {all_ok}/{all_total} ({all_ok/all_total*100:.1f}%) ===")
for k, v in summary.items():
    print(f"  {k}: {v}")
with open(os.path.join(KB, "regress_c16_v44_v64.json"), "w", encoding="utf-8") as f:
    json.dump({"total": all_total, "ok": all_ok, "rate": all_ok/all_total,
               "summary": summary}, f, ensure_ascii=False, indent=1)
print("已存 regress_c16_v44_v64.json")
agent.close()
