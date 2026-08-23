# -*- coding: utf-8 -*-
"""state_machine.py · 进化状态机（反馈/方向性自检 · 自迭代机制工程化阶段4）
理论：§3.10 八步闭环步骤7（反馈=下一次迭代基础）+ 步骤8（方向性自检：
反思单元发起、验证单元独立复核、维生系统确认后记录、不自动触发修改）。
命令：
  state_machine.py --candidates    加载台账 → 下一轮候选（薄簇×生活关联度×信息差优先）
  state_machine.py --direction    方向性自检报告（进化方向 vs 价值观一致性）
  state_machine.py --state        当前进化状态快照
"""
import sys, os, json, re, argparse
sys.stdout.reconfigure(encoding='utf-8')

SITE = r'D:\Program Files\2_ai\CommonTrustProtocol'
LEDGER = os.path.join(SITE, 'ledger', 'evolution_ledger.json')
STATE = os.path.join(SITE, 'ledger', 'evolution_state.json')
DOCS = os.path.join(SITE, 'docs')

# 生活关联度词（信息差优先：用户更可能问的）
LIFE_WORDS = ['水', '饭', '睡', '天气', '身体', '病', '电', '火', '车', '风',
              '雨', '冷', '热', '吃', '喝', '手', '眼', '心', '孩子', '老人',
              '上班', '上学', '家', '钱', '手机', '电脑', '衣服', '运动']


def load_ledger():
    return json.load(open(LEDGER, encoding='utf-8'))['entries']


def load_state():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding='utf-8'))
    return {'round': 0, 'upgraded': [], 'direction_check_log': []}


def life_score(key):
    """生活关联度：key 或其触发词含生活词的个数"""
    return sum(1 for w in LIFE_WORDS if w in key)


def candidates(ledger, n=12):
    """下一轮候选：薄簇 × 生活关联度 × 无测试覆盖优先"""
    cands = []
    for k, e in ledger.items():
        if not (0 < e['rd_len'] < 80):
            continue
        ls = life_score(k)
        no_test = 1 if not e['test_versions'] else 0
        cands.append((k, e['rd_len'], ls, no_test, e['domain']))
    # 排序：生活关联度降序 → 答案短（信息差大）→ 无测试覆盖
    cands.sort(key=lambda x: (-x[2], x[1], -x[3]))
    return cands[:n]


def direction_check(ledger, state):
    """方向性自检（§3.10 步骤8）：反思单元发起、验证单元独立复核、维生系统确认
    检查项：①进化方向 vs 价值观（缩小信息差仍被优先？）②局部优化偏离（只升简单簇？）
    ③薄簇覆盖趋势 ④复合条件缺口"""
    report = []
    # ① 信息差优先检查：薄簇数量变化
    thin = sum(1 for e in ledger.values() if 0 < e['rd_len'] < 80)
    upgraded = sum(1 for e in ledger.values() if e['upgraded'])
    report.append(f'① 进化规模: 已升级 {upgraded} / 薄簇 {thin}——缩小信息差方向 {"持续" if upgraded > 0 else "停滞"}')
    # ② 局部优化偏离：薄簇中生活关联度覆盖
    life_thin = sum(1 for k, e in ledger.items() if 0 < e['rd_len'] < 80 and life_score(k))
    report.append(f'② 方向偏离检查: 薄簇中生活关联簇 {life_thin}/{thin} ({life_thin/max(thin,1)*100:.0f}%)'
                  + ('——关注点：是否有难簇被回避' if life_thin/max(thin,1) < 0.2 else '——方向均衡'))
    # ③ 无条件答案簇（情感类走情感路由，提示人工确认是否为设计使然）
    no_ans = sum(1 for e in ledger.values() if e['status'] == 'no_answer')
    report.append(f'③ 条件路由缺口: {no_ans} 簇有条件无答案（情感类多走情感路由，需人工确认是否设计使然）')
    # ④ 验证充分性：无测试覆盖的已升级簇
    no_test = sum(1 for e in ledger.values() if e['upgraded'] and not e['test_versions'])
    report.append(f'④ 验证充分性: {no_test} 已升级簇无测试覆盖（v1-v36 实践智慧簇，建议纳入回归或标记）')
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidates', action='store_true')
    ap.add_argument('--direction', action='store_true')
    ap.add_argument('--state', action='store_true')
    args = ap.parse_args()

    ledger = load_ledger()
    state = load_state()

    if args.candidates:
        print(f'下一轮候选（薄簇×生活关联度×信息差优先）:')
        for k, n, ls, nt, dom in candidates(ledger):
            print(f'  {k}: {n}ch 生活关联={ls} 无测试覆盖={"是" if nt else "否"} domain={dom or "?"}')

    if args.direction:
        print(f'方向性自检报告 (第 {state.get("round", 0)+1} 轮前):')
        for line in direction_check(ledger, state):
            print(f'  {line}')
        print('  —— 自检不自动触发修改（§3.10 步骤8）；如需调整请设计者裁决')

    if args.state:
        print(f'进化状态: round={state.get("round", 0)}')
        print(f'  已升级簇数: {state.get("upgraded_count", "?")}')
        print(f'  方向自检记录: {len(state.get("direction_check_log", []))} 次')
        for i, log in enumerate(state.get('direction_check_log', [])[-3:], 1):
            print(f'    #{i}: {log}')


if __name__ == '__main__':
    main()
