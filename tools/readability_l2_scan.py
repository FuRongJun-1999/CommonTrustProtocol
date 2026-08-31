# -*- coding: utf-8 -*-
"""M5.1 L2 真实弱项扫描（可读性专项审查方案 v0.1 第二层）。

三类违规（口径=docs/M5.1_可读性专项审查方案_v0.1.md 二节）：
  A. 缺 docstring 的公开单元 —— 模块顶层公开函数/类（非 _ 前缀）无 docstring
  B. 无行内注释的长函数 —— 函数体 >LONG_BODY 行且体内零 `#` 注释行
  C. 命名混排 —— 标识符同时含中文与英文（PEP8 下应统一 snake_case 英文）

产出：违规清单 JSON（同 M1.1 扫描模式），供 L3 修正批次逐条消号。
用法：python tools/readability_l2_scan.py [--root aeis] [--out docs/m51_l2_violations.json]
"""
import ast
import json
import sys
import time
from pathlib import Path

LONG_BODY = 25          # 长函数阈值（行）
# L3 修正范围口径：仅自家代码。models/ 为第三方模型代码（cosyvoice 等），
# 补 docstring 无收益且制造上游同步冲突——扫描排除，报告留痕。
DEFAULT_EXCLUDE = ('models/',)
CJK = lambda s: any('\u4e00' <= ch <= '\u9fff' for ch in s)
LATIN = lambda s: any(ch.isascii() and ch.isalpha() for ch in s)


def is_public(name: str) -> bool:
    return not name.startswith('_')


def func_body_lines(node) -> int:
    """函数体行数 = 末行 - 首行 + 1（含签名与装饰器不计）。"""
    return (node.end_lineno or node.lineno) - node.lineno + 1


def inline_comment_count(source_lines, node) -> int:
    """函数体内 `#` 注释行数（含行尾注释；字符串内 # 不算——按行首 strip 后判断
    与行尾 # 粗判，可读性扫描容忍此近似）。"""
    n = 0
    for ln in source_lines[node.lineno - 1: node.end_lineno or node.lineno]:
        s = ln.strip()
        if s.startswith('#') or '#' in s.split('"')[-1].split("'")[-1]:
            n += 1
    return n


def iter_definitions(tree):
    """定向遍历：模块顶层 + 类体直接定义（方法/嵌套类）。
    不深入函数体内——方法内嵌闭包外部不可达，不属公开 API 口径。"""
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            yield node
            if isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                        yield sub


def scan_file(path: Path, rel: str):
    src = path.read_text(encoding='utf-8', errors='replace')
    lines = src.splitlines()
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [{'rule': 'PARSE', 'file': rel, 'detail': f'syntax error: {e}'}]
    out = []
    for node in iter_definitions(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if is_public(node.name):
                if not ast.get_docstring(node):
                    out.append({'rule': 'A_MISSING_DOCSTRING', 'file': rel,
                                'line': node.lineno, 'name': node.name,
                                'kind': type(node).__name__})
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if func_body_lines(node) > LONG_BODY and inline_comment_count(lines, node) == 0:
                    out.append({'rule': 'B_LONG_NO_COMMENT', 'file': rel,
                                'line': node.lineno, 'name': node.name,
                                'body_lines': func_body_lines(node)})
            if CJK(node.name) and LATIN(node.name):
                out.append({'rule': 'C_MIXED_NAME', 'file': rel,
                            'line': node.lineno, 'name': node.name,
                            'kind': type(node).__name__})
    return out


def main():
    root = Path(sys.argv[sys.argv.index('--root') + 1]) if '--root' in sys.argv else Path('aeis')
    out_path = (Path(sys.argv[sys.argv.index('--out') + 1]) if '--out' in sys.argv
                else Path('docs/m51_l2_violations.json'))
    violations = []
    files = 0
    for p in sorted(root.rglob('*.py')):
        if any(seg in ('.git', '__pycache__', 'node_modules') for seg in p.parts):
            continue
        rel_posix = p.as_posix()
        if any(ex in rel_posix for ex in DEFAULT_EXCLUDE):
            continue
        files += 1
        violations.extend(scan_file(p, rel_posix))

    by_rule = {}
    for v in violations:
        by_rule[v['rule']] = by_rule.get(v['rule'], 0) + 1
    report = {
        'scan': 'M5.1-L2 readability violations',
        'root': str(root), 'files_scanned': files,
        'total': len(violations), 'by_rule': by_rule,
        'thresholds': {'long_body_lines': LONG_BODY},
        'ts': time.strftime('%Y-%m-%d %H:%M:%S'),
        'violations': violations,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('files_scanned', 'total', 'by_rule')},
                     ensure_ascii=False))
    print('out ->', out_path)


if __name__ == '__main__':
    main()
