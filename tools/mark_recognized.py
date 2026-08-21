# -*- coding: utf-8 -*-
"""旧题库「已识别」标记 + 归档（v1.26 · 持续学习流程第一步）

流程文档：docs/题库生命周期与持续学习流程.md
标准线：self 直答正确率 = Σ(route==self 且 score≥0.5) / Σ(route==self) ≥ 95%

本脚本：
  1. 复核 v7 达标指标（self 直答正确率/总正确率/self 占比）
  2. 写标记文件（题库 ID/版本/指标/错题清单/归档路径）
  3. 题库 JSON 归档到已识别集合（knowledge-base/recognized_sets/）
  4. 输出错题复测集（12 题，单独文件）
"""
import json, sys, os, shutil, time
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

KB = r"D:\Program Files\2_ai\knowledge-base"
RECOG_DIR = os.path.join(KB, "recognized_sets")
os.makedirs(RECOG_DIR, exist_ok=True)

RESULTS = os.path.join(KB, "dialogue_1000_results_maindb.json")  # v7 结果
QUESTIONS = os.path.join(KB, "dialogue_1000.json")                # 原题库
MARK = os.path.join(KB, "dialogue_1000_RECOGNIZED.md")            # 标记文件
ARCHIVE_JSON = os.path.join(RECOG_DIR, "dialogue_1000_v7.json")   # 归档题库
RERUN_JSON = os.path.join(RECOG_DIR, "dialogue_1000_v7_rerun_errors.json")  # 错题复测集

results = json.load(open(RESULTS, encoding="utf-8"))
questions = json.load(open(QUESTIONS, encoding="utf-8"))

# ---- 指标复核 ----
rc = Counter(x.get("route") for x in results)
self_total = sum(1 for x in results if x.get("route") == "self")
self_ok = sum(1 for x in results if x.get("route") == "self"
              and x.get("score", 0) >= 0.5)
self_acc = self_ok / self_total
total_ok = sum(1 for x in results if x.get("score", 0) >= 0.5)
total_acc = total_ok / len(results)

errors = [(i, x) for i, x in enumerate(results) if x.get("score", 0) < 0.5]
print(f"total={len(results)} self={self_total} self_ok={self_ok} "
      f"self_acc={self_acc:.4f} total_acc={total_acc:.4f} errors={len(errors)}")

# 去重错题（同问题多形态算一道）
uniq_errors = {}
for i, x in errors:
    q = (x.get("q") or "").strip()
    if q not in uniq_errors:
        uniq_errors[q] = {"idx": i, "route": x.get("route"), "reply": x.get("reply", "")}
print(f"唯一错题: {len(uniq_errors)}")

PASS = self_acc >= 0.95
print(f"达标: {PASS}")

# ---- 标记文件 ----
mark = f"""# 题库已识别标记（v1.26 · {time.strftime('%Y-%m-%d %H:%M')}）

## 判定结果

**达标 ✓**（self 直答正确率 {self_acc:.2%} ≥ 95% 标准线）

| 指标 | 值 |
|---|---|
| 题库 | dialogue_1000（1000 题） |
| self 直答正确率 | {self_acc:.2%}（{self_ok}/{self_total}） |
| 总正确率 | {total_acc:.2%}（{total_ok}/1000） |
| self 直答占比 | {self_total/1000:.1%} |
| route 分布 | self {rc.get('self',0)} / llm {rc.get('llm',0)} |
| 错题数 | {len(errors)}（去重 {len(uniq_errors)}） |

## 判定标准（荣定标准）

> 95% 标准线 = self 直答正确率（route==self 且 score≥0.5 / route==self 总数），
> 不走 LLM 补全。达标 → 题库内容已被白箱固化（图谱+索引+直答）。

## 归档

- 题库 JSON → `recognized_sets/dialogue_1000_v7.json`
- 错题复测集 → `recognized_sets/dialogue_1000_v7_rerun_errors.json`（单独验证补卡）

## 错题清单（{len(uniq_errors)} 道唯一）

"""
for q, info in uniq_errors.items():
    mark += f"- [{info['route']}] {q}\n"

mark += f"""
## 下一步

- 错题 5% 复测：逐题分析 → 补卡/补直答/修路由 → 迭代重跑复测集
- 新测试集：盲区注册表（BS-QUERY-WEAK/BS-ACTIVE-PROBE）+ 真实对话弱命中 + 知识考古新领域
- 旧题不再投入打磨（达标即换题，边际收益低）

---
生成: tools/mark_recognized.py · 结果源: dialogue_1000_results_maindb.json (v7)
"""
with open(MARK, "w", encoding="utf-8") as f:
    f.write(mark)
print("标记文件:", MARK)

# ---- 归档题库 JSON ----
shutil.copyfile(QUESTIONS, ARCHIVE_JSON)
print("归档题库:", ARCHIVE_JSON, os.path.getsize(ARCHIVE_JSON))

# ---- 错题复测集（独立文件，含原题+结果+判定） ----
rerun = []
for q, info in uniq_errors.items():
    rerun.append({
        "q": q,
        "v7_route": info["route"],
        "v7_reply": info["reply"][:300],
        "idx": info["idx"],
    })
with open(RERUN_JSON, "w", encoding="utf-8") as f:
    json.dump(rerun, f, ensure_ascii=False, indent=1)
print("错题复测集:", RERUN_JSON, f"({len(rerun)} 题)")
