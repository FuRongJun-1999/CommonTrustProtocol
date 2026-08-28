# -*- coding: utf-8 -*-
"""skill_mcp_verify.py · lingshu-skills MCP 打通验证（发布前门禁 2）

验证目标：技能（说明书）→ Verification → 物理基底（MCP 执行层）真正打通。
1. YAML frontmatter 可解析（pyyaml）——agent 加载技能的路由判定接口
2. metadata.kccs 四要素可提取（when/sub/execute/not_applicable）
3. 代表性技能的 Verification 实际执行（protocol-compiler：compile_source + ConditionVM）
   ——技能声明「能做什么」→ 物理基底真跑出结果（白箱闭环）
4. 结果断言（compile-recursive 阶乘=120 / compile-assign / compile-if-then）
"""
import os, sys, json, glob

def setup_stdout():
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

setup_stdout()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_ROOT = os.path.join(ROOT, "aeis", "skills", "skills")
import yaml

# ---- 1. YAML 解析 + kccs 提取（全量 688）----
md_files = glob.glob(os.path.join(SKILLS_ROOT, "*", "SKILL.md"))
yaml_ok = 0
kccs_ok = 0
not_app_ok = 0
fail = []

for f in md_files:
    slug = os.path.basename(os.path.dirname(f))
    try:
        text = open(f, encoding="utf-8").read()
        fm = yaml.safe_load(text.split("---", 2)[1])
        if not isinstance(fm, dict):
            fail.append((slug, "frontmatter 非 dict"))
            continue
        yaml_ok += 1
        meta = fm.get("metadata") or {}
        kccs = meta.get("kccs") or {}
        if kccs:
            kccs_ok += 1
            if kccs.get("not_applicable"):
                not_app_ok += 1
        else:
            fail.append((slug, "metadata.kccs 缺失"))
    except Exception as e:
        fail.append((slug, f"YAML 解析失败: {e}"))

total = len(md_files)
print(f"===== 1. YAML frontmatter 解析（{total} 技能）=====")
print(f"  YAML 可解析: {yaml_ok}/{total}")
print(f"  metadata.kccs 存在: {kccs_ok}/{total}")
print(f"  not_applicable 有值: {not_app_ok}/{total}")
if fail:
    print(f"  失败 {len(fail)}:")
    for slug, err in fail[:10]:
        print(f"    ✘ {slug}: {err}")

# ---- 2. 代表性技能 Verification 物理执行 ----
print(f"\n===== 2. Verification 物理基底执行（MCP 执行层）=====")
sys.path.insert(0, r"D:\Program Files\2_ai\protocol-compiler")
from core.compiler import compile_source
from core.condition_vm import ConditionVM

CASES = [
    ("compile-recursive", "定义 阶乘（数）：若 数 小于 2，则 返回 1，否则 返回 数 乘 阶乘（数 减 1）；结果 = 阶乘（5）；止。", 120.0),
    ("compile-assign", "结果 = 3 加 4 乘 2；止。", 11.0),
    ("compile-if-then", "若 5 大于 3，则 结果 = 1，否则 结果 = 0；止。", 1.0),
]

all_ok = True
for slug, src, expected in CASES:
    try:
        code, r = compile_source(src, strict=False)
        if not r["ok"]:
            print(f"  ✘ {slug}: 编译失败 {r['errors'][:1]}")
            all_ok = False
            continue
        st = ConditionVM().run(code)
        got = st["symbols"].get("结果")
        ok = got is not None and abs(got - expected) < 0.01
        all_ok = all_ok and ok
        print(f"  {'✓' if ok else '✘'} {slug}: 「结果」={got} 期望={expected}（compile+VM 物理执行）")
    except Exception as e:
        print(f"  ✘ {slug}: {e}")
        all_ok = False

# ---- 3. 结论 ----
print(f"\n===== 结论 =====")
gate = yaml_ok == total and kccs_ok == total and not_app_ok == total and all_ok
print(f"{'✅ MCP 打通验证通过：说明书（YAML）可解析 + 物理基底（compile+VM）真执行' if gate else '❌ 未通过'}")

# 输出结构化结果（供触发词回写使用）
result = {
    "yaml_parsable": yaml_ok,
    "kccs_present": kccs_ok,
    "not_applicable": not_app_ok,
    "verification_executed": [c[0] for c in CASES],
    "gate": gate,
}
with open(os.path.join(ROOT, "tools", "skill_mcp_verify_result.json"), "w", encoding="utf-8") as fp:
    json.dump(result, fp, ensure_ascii=False, indent=2)
print(f"结果已保存: tools/skill_mcp_verify_result.json")
sys.exit(0 if gate else 1)
