# -*- coding: utf-8 -*-
"""时间核 lint（钉死批条款 3 / E5 新口径机械化）。

钉死条款（docs/概念钉死批_GPT四点评审_v0.1.md 钉死 3）：
  全库一切时间演化必须使用指数核形状
  X_i(t) = X_i,∞ + (X_i,0 - X_i,∞)·e^(-γ_i·t)
  核形状唯一，状态 X 与衰减率 γ 按对象配置。

本工具全库普查时间演化调用点并分类：
  CONTINUOUS_EXP   exp(-t/τ) 连续指数核            —— 合规
  DISCRETE_EXP     ×(1-factor) 每周期乘法=离散指数 —— 合规
  EMA              (1-λ)·last+λ·x 指数平滑        —— 合规
  TTL_LEASE        TTL 租约比较（需 DEV 声明与指数核耦合）
  SUSPECT_LINEAR   疑似线性/阶跃衰减               —— 人工复核
  NON_TIME_EXP     exp 但无时间参数（sigmoid 等）  —— 排除出审计域

E5 口径：SUSPECT_LINEAR 之外不得出现第二种核形状；长期目标是全部
落到统一核函数 cred() 单点实现（本基线记录就地实现清单，供单点化消号）。
用法：python tools/time_core_lint.py [--root aeis] [--out docs/e5_time_core_baseline.json]
"""
import json
import re
import sys
import time
from pathlib import Path

# 排除口径同 L2：第三方模型代码不入审计域
DEFAULT_EXCLUDE = ('models/',)
SKIP_DIRS = ('.git', '__pycache__', 'node_modules')

PATTERNS = [
    # (规则, 正则, 判定)
    ('CONTINUOUS_EXP', re.compile(r'exp\(\s*-\s*[\w.()]+\s*/\s*[\w.]+\s*\)'), '指数核(连续)'),
    ('DISCRETE_EXP', re.compile(r'\*\s*\(\s*1\s*-\s*(factor|decay|rate|alpha|λ|lam)\b'), '指数核(离散乘法)'),
    ('EMA', re.compile(r'\(\s*1\s*-\s*[\w.]+\s*\)\s*\*\s*\w*(last|prev|old|_meta)'), '指数平滑'),
    ('TTL_LEASE', re.compile(r'\bTTL\b|ttl_seconds|is_expired|lease_expiry'), '租约(需DEV耦合声明)'),
    ('SUSPECT_LINEAR', re.compile(r'(confidence|importance|cred|score)\s*-=\s*[\d.]+'), '疑似线性衰减!'),
    ('NON_TIME_EXP', re.compile(r'exp\(\s*-?\s*x\s*\)|exp\(-\s*(self\.)?\w+\s*\)\s*/'), 'exp无时间参数(排除)'),
]


def scan_file(path: Path, rel: str):
    try:
        src = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return []
    out = []
    for i, line in enumerate(src.splitlines(), 1):
        code = line.split('#')[0]  # 不审注释
        if not code.strip():
            continue
        for rule, pat, verdict in PATTERNS:
            if pat.search(code):
                # NON_TIME_EXP 只在无其他规则命中该行时记录（排除域，供确认）
                out.append({'rule': rule, 'file': rel, 'line': i,
                            'verdict': verdict, 'code': code.strip()[:100]})
                break
    return out


def main():
    root = Path(sys.argv[sys.argv.index('--root') + 1]) if '--root' in sys.argv else Path('aeis')
    out_path = (Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv
                else Path('docs/e5_time_core_baseline.json'))
    hits = []
    files = 0
    for p in sorted(root.rglob('*.py')):
        if any(seg in p.parts for seg in SKIP_DIRS):
            continue
        rel = p.as_posix()
        if any(ex in rel for ex in DEFAULT_EXCLUDE):
            continue
        files += 1
        hits.extend(scan_file(p, rel))

    by_rule = {}
    for h in hits:
        by_rule[h['rule']] = by_rule.get(h['rule'], 0) + 1
    compliant = by_rule.get('CONTINUOUS_EXP', 0) + by_rule.get('DISCRETE_EXP', 0) + \
        by_rule.get('EMA', 0) + by_rule.get('TTL_LEASE', 0)
    report = {
        'scan': 'E5 time-core lint (钉死批条款3机械化)',
        'kernel_clause': 'X_i(t)=X_i,∞+(X_i,0-X_i,∞)·e^(-γ_i·t)；核形状唯一，γ_i按对象分层',
        'root': str(root), 'files_scanned': files,
        'total_hits': len(hits), 'by_rule': by_rule,
        'kernel_compliant': compliant,
        'suspect_violations': by_rule.get('SUSPECT_LINEAR', 0),
        'e5_verdict': 'PASS' if by_rule.get('SUSPECT_LINEAR', 0) == 0 else 'REVIEW_NEEDED',
        'note': '就地实现清单=统一核函数cred()单点化的消号队列（非违规，形状均指数族）',
        'ts': time.strftime('%Y-%m-%d %H:%M:%S'),
        'hits': hits,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('files_scanned', 'total_hits', 'by_rule',
                                             'e5_verdict')}, ensure_ascii=False))
    print('out ->', out_path)


if __name__ == '__main__':
    main()
