# -*- coding: utf-8 -*-
"""skill_triggers_backfill.py · 六域触发词工程化回写 KCCS（skills → 单元库真源侧）

回写：把 lingshu-skills 验证的触发词工程化（extract_triggers 逻辑）应用到
六域单元库真源（*_code_units.py），生成触发词索引——条件路由图的检索面数据。

输出：aeis/wisdom/trigger_words_index.json
  { domain: { uid: [trigger_words...] } }

用法：python tools/skill_triggers_backfill.py
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WISDOM = os.path.join(ROOT, "aeis", "wisdom")
sys.path.insert(0, HERE)
sys.path.insert(0, WISDOM)

DOMAINS = {
    "compiler": ("compiler_code_units", "COMPILER_UNITS"),
    "pylang": ("python_code_units", "PYTHON_UNITS"),
    "graph": ("graph_db_units", "GRAPH_UNITS"),
    "os": ("os_units", "OS_UNITS"),
    "browser": ("browser_units", "BROWSER_UNITS"),
    "net": ("net_units", "NET_UNITS"),
}

TEMPLATE_MARKS = [
    "主体逻辑执行", "顺序执行", "返回 None/不执行",
    "name/params/cond_instrs", "value_instrs", "输入不满足生效条件",
]

import skill_export as se  # 复用 extract_triggers/parse_four_elements


def main():
    index = {}
    total = 0
    for dom, (mod_name, var_name) in DOMAINS.items():
        mod = __import__(mod_name)
        units = getattr(mod, var_name)
        dom_index = {}
        for uid, u in units.items():
            when, sub, execute, not_app, specific = se.parse_four_elements(u.get("pattern", ""))
            triggers = se.extract_triggers(u.get("task", ""), uid, u.get("calibration", ""), specific)
            dom_index[uid] = triggers
            total += 1
        index[dom] = dom_index
        print(f"  ✓ {dom}: {len(dom_index)} 单元触发词提取")

    out = os.path.join(WISDOM, "trigger_words_index.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"\n触发词索引已回写: {out}")
    print(f"总计: {total} 单元（六域）——条件路由图检索面就绪")
    print(f"示例（compiler/编译-递归）: {index['compiler'].get('编译-递归', [])}")


if __name__ == "__main__":
    main()
