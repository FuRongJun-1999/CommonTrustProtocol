# -*- coding: utf-8 -*-
"""skill_export_verify.py · SKILL 导出的完整验证与校验（发布前门禁）

校验维度：
1. 全量导出（compiler 域全部单元）无异常
2. SKILL.md 格式：frontmatter 可解析 / name slug 合法 / 必填字段非空
3. KCCS 四要素完整性：not_applicable 非空率 / execute 非模板率 / when 非空率
4. 不适用条件三通道：description「Not for」/ metadata.kccs.not_applicable / 正文克制条款章节
5. plugin.json 合规：agent-plugins.org 关键字段 + extensions.condition-route

用法：python tools/skill_export_verify.py [--limit N] [--out DIR]
"""
import os, re, sys, json, argparse, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WISDOM = os.path.join(ROOT, "aeis", "wisdom")
sys.path.insert(0, HERE)
sys.path.insert(0, WISDOM)

# 模板注释标记（与 skill_export.py 一致）
TEMPLATE_MARKS = [
    "主体逻辑执行", "顺序执行", "返回 None/不执行",
    "name/params/cond_instrs", "value_instrs", "输入不满足生效条件",
]

SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


def parse_frontmatter(text):
    """解析 SKILL.md frontmatter（--- 之间）。返回 dict 或 None。"""
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    data = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        data[k.strip()] = v.strip().strip('"').strip(">")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(HERE, "skill-export-verify"))
    args = ap.parse_args()

    # 1. 全量导出
    import skill_export as se
    sys.argv = ["skill_export.py", "--out", args.out]
    if args.limit:
        sys.argv += ["--limit", str(args.limit)]
    se.main()

    # 收集导出单元（slug 目录）
    skill_root = os.path.join(args.out, "skills")
    skills = {}
    for d in os.listdir(skill_root):
        md_path = os.path.join(skill_root, d, "SKILL.md")
        if os.path.exists(md_path):
            skills[d] = open(md_path, encoding="utf-8").read()

    print(f"\n===== 校验报告（{len(skills)} 单元）=====\n")
    total = len(skills)
    pass_n = 0
    issues = []

    for slug, md in skills.items():
        errs = []
        # frontmatter 区（--- 之间）
        fm = re.search(r"^---\n(.*?)\n---", md, re.S)
        fm_text = fm.group(1) if fm else ""
        if not fm_text:
            errs.append("frontmatter 不可解析")
        else:
            # name slug 合法
            nm = re.search(r"^name:\s*(.+)$", fm_text, re.M)
            if not nm or not SLUG_RE.match(nm.group(1).strip()):
                errs.append(f"name slug 非法: {nm.group(1) if nm else '无'}")
            # 必填字段
            for field in ["description", "compatibility", "license"]:
                if not re.search(rf"^{field}:", fm_text, re.M):
                    errs.append(f"{field} 缺失")
            # metadata.kccs 四要素块
            if "metadata:" not in fm_text or "kccs:" not in fm_text:
                errs.append("metadata.kccs 缺失")
            # 三通道
            if "【不适用】" not in md[:1200] and "Not for" not in md[:1200]:
                errs.append("通道1缺失：description 无「Not for」")
            if "not_applicable:" not in fm_text:
                errs.append("通道2缺失：metadata 无 not_applicable")
            if "克制条款" not in md:
                errs.append("通道3缺失：正文无克制条款章节")

        if errs:
            issues.append((slug, errs))
        else:
            pass_n += 1

    # 统计四要素覆盖
    has_not_app = sum(1 for md in skills.values() if "not_applicable:" in md[:1200])
    has_when = sum(1 for md in skills.values() if "when:" in md[:1200])
    has_exec = sum(1 for md in skills.values() if "execute:" in md[:1200])
    has_kt = sum(1 for md in skills.values() if "克制条款" in md)

    print(f"通过格式+三通道校验: {pass_n}/{total}")
    print(f"not_applicable 字段: {has_not_app}/{total}")
    print(f"when 字段: {has_when}/{total}")
    print(f"execute 字段: {has_exec}/{total}")
    print(f"正文克制条款: {has_kt}/{total}")

    if issues:
        print(f"\n有问题的单元 {len(issues)}:")
        for slug, errs in issues[:15]:
            print(f"  ✘ {slug}: {'; '.join(errs[:4])}")

    # 5. plugin.json 合规
    print("\n===== plugin.json 校验 =====")
    pj_path = os.path.join(args.out, "plugin.json")
    pj = json.load(open(pj_path, encoding="utf-8"))
    pj_ok = True
    for f in ["$schema", "name", "version", "description", "extensions"]:
        if f not in pj:
            print(f"  ✘ 缺字段: {f}")
            pj_ok = False
    ext = pj.get("extensions", {}).get("lingshu", {}).get("condition-route", {})
    for f in ["domains", "unit-count", "kccs-version", "negative-route", "condition-space"]:
        if f not in ext:
            print(f"  ✘ extensions.condition-route 缺: {f}")
            pj_ok = False
    if pj_ok:
        print("  ✓ plugin.json 关键字段齐全（agent-plugins.org schema 结构）")

    ok = pass_n == total and pj_ok
    print(f"\n===== 发布门禁: {'✅ 通过，可发布' if ok else '❌ 未通过，需修复'} =====")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
