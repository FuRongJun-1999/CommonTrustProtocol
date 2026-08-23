# -*- coding: utf-8 -*-
"""evolve.py · 自主进化驱动器（自迭代八步闭环步骤7反馈 + 信息差度量）
自主发现信息差 → 变异器生成候选 → 流水线裁决 → 自动补盲 → 度量报告 → 台账更新
命令：
  evolve.py --candidates [N]     自主发现信息差：下一轮候选（薄簇×生活关联×信息差优先）
  evolve.py --info-gap           信息差度量报告（薄簇/升级/触发词/缺口趋势）
  evolve.py --run <patches> <version>   自主执行一轮（调 pipeline 全流程）
"""
import sys, os, json, re, argparse, subprocess
sys.stdout.reconfigure(encoding='utf-8')

CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
LEDGER = os.path.join(CTP, 'ledger', 'evolution_ledger.json')
TOOLS = os.path.join(CTP, 'tools')

LIFE_WORDS = ['水', '饭', '睡', '天气', '身体', '病', '电', '火', '车', '风',
              '雨', '冷', '热', '吃', '喝', '手', '眼', '心', '孩子', '老人',
              '上班', '上学', '家', '钱', '手机', '电脑', '衣服', '运动']


def load_ledger():
    return json.load(open(LEDGER, encoding='utf-8'))['entries']


def life_score(key):
    return sum(1 for w in LIFE_WORDS if w in key)


def candidates(ledger, n=12):
    cands = []
    for k, e in ledger.items():
        if not (0 < e['rd_len'] < 80):
            continue
        cands.append((k, e['rd_len'], life_score(k), e['domain']))
    cands.sort(key=lambda x: (-x[2], x[1]))
    return cands[:n]


def info_gap_report(ledger):
    """信息差度量：薄簇数/升级数/触发词总数/条件缺口"""
    thin = [(k, e['rd_len']) for k, e in ledger.items() if 0 < e['rd_len'] < 80]
    upgraded = [k for k, e in ledger.items() if e['upgraded']]
    no_ans = [k for k, e in ledger.items() if e['status'] == 'no_answer']
    total_triggers = sum(e['trigger_count'] for e in ledger.values())
    no_test = [k for k, e in ledger.items() if e['upgraded'] and not e['test_versions']]
    # 变化记录（若上次快照存在）
    snap_path = os.path.join(CTP, 'ledger', 'info_gap_snapshot.json')
    delta = ''
    if os.path.exists(snap_path):
        prev = json.load(open(snap_path, encoding='utf-8'))
        d_thin = len(thin) - prev['thin']
        d_up = len(upgraded) - prev['upgraded']
        d_trig = total_triggers - prev['total_triggers']
        delta = f' (较上轮: 薄簇{d_thin:+d} 升级{d_up:+d} 触发词{d_trig:+d})'
    json.dump({'thin': len(thin), 'upgraded': len(upgraded),
               'total_triggers': total_triggers}, open(snap_path, 'w', encoding='utf-8'))
    return {
        'thin': len(thin), 'upgraded': len(upgraded),
        'no_answer': len(no_ans), 'total_triggers': total_triggers,
        'no_test': len(no_test), 'delta': delta,
    }


def run_py(script, args=None):
    cmd = [sys.executable, os.path.join(TOOLS, script)] + (args or [])
    r = subprocess.run(cmd, capture_output=True)
    out = r.stdout.decode('utf-8', errors='replace')
    if out:
        print(out, end='')
    if r.returncode != 0:
        err = r.stderr.decode('utf-8', errors='replace')
        print(f'[stderr] {err[:1500]}', file=sys.stderr)
        raise RuntimeError(f'脚本失败: {script} rc={r.returncode}')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidates', type=int, default=0)
    ap.add_argument('--info-gap', action='store_true')
    ap.add_argument('--run', nargs=2, metavar=('PATCHES', 'VERSION'))
    args = ap.parse_args()

    ledger = load_ledger()

    if args.candidates:
        print(f'自主发现信息差 · 下一轮候选 (前 {args.candidates}):')
        for k, n, ls, dom in candidates(ledger, args.candidates):
            print(f'  {k}: {n}ch 生活关联={ls} domain={dom or "?"}')

    if args.info_gap:
        g = info_gap_report(ledger)
        print(f'信息差度量报告:{g["delta"]}')
        print(f'  已升级: {g["upgraded"]}')
        print(f'  薄簇(待升级): {g["thin"]}')
        print(f'  有条件无答案: {g["no_answer"]}')
        print(f'  触发词总数: {g["total_triggers"]}')
        print(f'  无测试覆盖: {g["no_test"]}')

    if args.run:
        patches, version = args.run
        print(f'自主执行一轮: patches={patches} version={version}')
        run_py('pipeline.py', ['--patches', os.path.join(TOOLS, patches), '--version', version])
        # 补盲 + 台账（pipeline 已含台账；补盲在测试前由预检驱动）
        print('自主进化轮次完成')


if __name__ == '__main__':
    main()
