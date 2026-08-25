# -*- coding: utf-8 -*-
"""test_ccg_missing.py · Missing Condition Accuracy（GPT：条件结构 GT）

ground truth 用条件结构而非自然语言关键词：
  {subject: 条件对象, condition_type: 条件类型（阈值检查/累积/容器类型…）,
   a_side: A 侧判别词, b_side: B 侧判别词}
判定两层：
  严格匹配：缺失条件同时含 A 侧判别词 与 B 侧判别词（条件结构两侧对齐）
  语义等价：含任一侧判别词（同义词归一：门槛≈阈值、放行≈判定、累积≈累加）
"""
import sys, os, json
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import ccg

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

G = ccg.build_graph()

# 同义词归一：缺失条件与 GT 判别词的字面差异（门槛≈阈值 等）
SYN = {'门槛': ['阈值'], '阈值': ['门槛'], '放行': ['判定', '判断'],
       '判定': ['放行'], '判断': ['放行'], '累积': ['累加'], '累加': ['累积'],
       '着色': ['染色'], '分片': ['切片'], '切片': ['分片']}


def norm_hit(missing, word):
    """缺失条件是否含 word 或其同义词。"""
    if word in missing:
        return True
    return any(s in missing for s in SYN.get(word, []))


# GT 条件结构表：10 对相邻能力 → 真条件差异（决定能力边界的条件）
GT = [
    # subject=信任值, condition_type=阈值检查 vs 累积 → 边界=累积/阈值
    {"a": "VM-信任累积", "b": "校验-信任检查",
     "subject": "信任值", "cond_type": "累积 vs 阈值检查",
     "a_side": ["累积"], "b_side": ["门槛", "阈值", "放行"]},
    # subject=输出容器, condition_type=容器类型 → 边界=列表/字典
    {"a": "推导式-列表推导", "b": "推导式-字典推导",
     "subject": "输出容器", "cond_type": "容器类型",
     "a_side": ["列表"], "b_side": ["字典"]},
    # subject=寄存器, condition_type=用途 → 边界=着色/分配
    {"a": "编译-寄存器着色", "b": "编译-寄存器分配",
     "subject": "寄存器", "cond_type": "用途",
     "a_side": ["着色", "染色"], "b_side": ["分配"]},
    # subject=边权, condition_type=是否加权 → 边界=加权/无权
    {"a": "图遍历-BFS", "b": "图遍历-加权最短",
     "subject": "边权", "cond_type": "是否加权",
     "a_side": ["无权", "BFS", "逐层"], "b_side": ["加权", "Dijkstra"]},
    # subject=页, condition_type=操作 → 边界=分配/置换
    {"a": "内存-分页分配", "b": "内存-页置换",
     "subject": "页", "cond_type": "操作类型",
     "a_side": ["分配"], "b_side": ["置换", "缺页"]},
    # subject=报文, condition_type=处理 → 边界=解析/分片
    {"a": "网络-报文解析", "b": "网络-报文分片",
     "subject": "报文", "cond_type": "处理方式",
     "a_side": ["解析", "头部"], "b_side": ["分片", "MTU", "重组"]},
    # subject=表达式, condition_type=算子 → 边界=逻辑/三元
    {"a": "编译-逻辑表达式", "b": "语法-三元表达式",
     "subject": "表达式", "cond_type": "算子类型",
     "a_side": ["逻辑", "短路"], "b_side": ["三元", "假值"]},
    # subject=传输协议, condition_type=握手 → 边界=TCP/QUIC
    {"a": "网络-TCP握手", "b": "网络-QUIC握手",
     "subject": "传输协议", "cond_type": "握手方式",
     "a_side": ["SYN", "ACK"], "b_side": ["QUIC", "0-RTT"]},
    # subject=存储, condition_type=生命周期 → 边界=持久/会话
    {"a": "存储-本地存储", "b": "存储-会话存储",
     "subject": "存储", "cond_type": "生命周期",
     "a_side": ["持久", "本地"], "b_side": ["会话", "生命周期", "标签页"]},
    # subject=边权, condition_type=是否加权 → 边界=无权/加权（反向对）
    {"a": "图遍历-最短路径", "b": "图遍历-加权最短",
     "subject": "边权", "cond_type": "是否加权",
     "a_side": ["无权", "BFS", "逐层"], "b_side": ["加权", "Dijkstra"]},
]

strict_ok = sem_ok = total = 0
fails = []
for t in GT:
    a, b = t["a"], t["b"]
    if a not in G or b not in G:
        print(f'[跳过] {a} 或 {b} 不在图中')
        continue
    total += 1
    missing = ccg._diff_condition(a, b, G)
    a_hits = [w for w in t["a_side"] if norm_hit(missing, w)]
    b_hits = [w for w in t["b_side"] if norm_hit(missing, w)]
    strict = bool(a_hits) and bool(b_hits)
    sem = bool(a_hits) or bool(b_hits)
    strict_ok += strict
    sem_ok += sem
    flag = 'S' if strict else ('s' if sem else 'x')
    print(f'[{flag}] {a} vs {b} 缺失: {missing[:46]}'
          f' | A侧{a_hits} B侧{b_hits}')
    if not sem:
        fails.append({"a": a, "b": b, "missing": missing,
                      "gt": t["a_side"] + t["b_side"]})

print(f"\n=== Missing Condition Accuracy（{total} 对，条件结构 GT）===")
print(f"严格匹配（A/B 两侧判别词都含）: {strict_ok}/{total}"
      f" ({100.0*strict_ok/total:.0f}%)")
print(f"语义等价（任一侧判别词，同义词归一）: {sem_ok}/{total}"
      f" ({100.0*sem_ok/total:.0f}%)")
if fails:
    print("未命中案例（盲区登记）:")
    for f in fails:
        print('  -', f['a'], 'vs', f['b'], '| GT:', f['gt'],
              '| 缺失:', f['missing'][:40])

check('① 语义等价缺失条件准确率 ≥ 90%（条件可辨识）',
      sem_ok / total >= 0.9, f"{100.0*sem_ok/total:.0f}%")
check('② 严格匹配 ≥ 60%（两侧判别词都对齐——条件结构可复现）',
      strict_ok / total >= 0.6, f"{100.0*strict_ok/total:.0f}%")

report = {
    "experiment": "Missing Condition Accuracy（GPT：条件结构 GT）",
    "method": ("_diff_condition 输出的缺失条件 vs 条件结构 GT"
               "（subject/cond_type/A侧/B侧判别词，同义词归一）"),
    "pairs": total, "strict": strict_ok, "semantic": sem_ok,
    "strict_rate": round(strict_ok / total, 4),
    "semantic_rate": round(sem_ok / total, 4),
    "blindspots": fails,
    "conclusion": ("缺失条件能否反推真条件差异："
                   "语义等价率=条件辨识力（非描述相似）；"
                   "严格率=条件结构两侧对齐度"),
}
rp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ccg_missing_report.json')
json.dump(report, open(rp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
check('③ 缺失条件报告落盘', os.path.exists(rp), 'ccg_missing_report.json')

print(f'\n=== Missing Condition Accuracy: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
