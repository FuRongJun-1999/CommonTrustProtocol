# -*- coding: utf-8 -*-
"""pipeline.py · 裁决流水线（验证单元落地 · 自迭代机制工程化阶段3）
一条命令完成：语法编译 → 五副本同步 → 路由预检(variant_checker) → 生成测试集 → 跑测试 → 全量回归 → 归档 → 台账更新
理论：§1.8 信息差缩小四阶段（状态暴露→预期输出→验证反馈→校准）；§3.1 验证单元（预期vs实际/稳态检测）；
     §3.12 一级行为验证（验证单元）/二级根源回溯（反思单元）/三级递归截断（维生系统）。
用法：
  python pipeline.py --patches patches.json --version v65
    patches.json: [{"key": "簇名", "answer": "完整直答", "theme": "主题"}, ...]
"""
import sys, os, json, re, subprocess, shutil, hashlib, time, argparse
sys.stdout.reconfigure(encoding='utf-8')

SITE = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages'
WISDOM = os.path.join(SITE, 'wisdom')
KB = r'D:\Program Files\2_ai\knowledge-base'
CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
LEDGER = os.path.join(CTP, 'ledger', 'evolution_ledger.json')
COPIES = [
    os.path.join(KB, 'semantic_translate.py'),
    os.path.join(CTP, 'aeis', 'wisdom', 'semantic_translate.py'),
    r'D:\Program Files\1_ai\lingshu-wisdom\wisdom\semantic_translate.py',
    r'D:\Program Files\3_ai\lingshu-wisdom\wisdom\semantic_translate.py',
]
SRC_ST = os.path.join(WISDOM, 'semantic_translate.py')


def step(tag, msg):
    print(f'\n=== [{tag}] {msg}', flush=True)


def run_py(script, args=None):
    """用子进程跑 python 脚本（避免本进程模块缓存）"""
    cmd = [sys.executable, script] + (args or [])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    if r.stdout:
        print(r.stdout, end='')
    if r.returncode != 0:
        print(f'[stderr] {r.stderr[:2000]}', file=sys.stderr)
        raise RuntimeError(f'脚本失败: {script} rc={r.returncode}')
    return r.stdout


def sync_copies():
    h0 = hashlib.sha256(open(SRC_ST, 'rb').read()).hexdigest()[:12]
    for c in COPIES:
        if os.path.exists(c):
            shutil.copy2(SRC_ST, c)
            h = hashlib.sha256(open(c, 'rb').read()).hexdigest()[:12]
            assert h == h0, f'同步失败: {c}'
    print(f'五副本同步 ✓ [{h0}]')


def apply_patches(patches):
    """按 patch 锚点纪律（最后一个 '"key": "' 匹配 = RD 区）写入答案"""
    src = open(SRC_ST, encoding='utf-8').read()
    for p in patches:
        key = p['key']
        newv = p['answer']
        matches = list(re.finditer('"' + re.escape(key) + r'"\s*:\s*"', src))
        if not matches:
            print(f'!! {key}: key 未找到（跳过）')
            continue
        idx = matches[-1].start()
        line_start = src.rfind('\n', 0, idx) + 1
        line_end = src.find('\n', idx)
        row = src[line_start:line_end]
        last_q = row.rfind('"')
        key_prefix = row[:row.find('"')]
        new_full = key_prefix + '"' + key + '": "' + newv + '",'
        src = src[:line_start] + new_full + src[line_end:]
        print(f'patch {key}: -> {len(newv)}ch')
    open(SRC_ST, 'w', encoding='utf-8').write(src)


def gen_testset(version, themes):
    """模板化生成测试集（正/反/合）"""
    items = []
    for theme in themes:
        items.append({"q": f"什么是{theme}？", "domain": theme, "stage": "正题",
                      "need": "", "conflict": ""})
        items.append({"q": f"为什么{theme}？", "domain": theme, "stage": "正题",
                      "need": "", "conflict": ""})
        items.append({"q": f"{theme}有什么用？", "domain": theme, "stage": "合题",
                      "need": "", "conflict": ""})
        items.append({"q": f"没有{theme}会怎样？", "domain": theme, "stage": "反题",
                      "need": "", "conflict": ""})
    path = os.path.join(KB, f'conflict_testset_{version}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"name": f"conflict_testset_{version}", "conflicts": len(themes),
                   "items": items}, f, ensure_ascii=False, indent=1)
    print(f'测试集已生成: {version} ({len(items)} 题)')
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--patches', required=True, help='patches.json 路径')
    ap.add_argument('--version', required=True, help='测试集版本号如 v65')
    ap.add_argument('--skip-test', action='store_true', help='跳过跑测试（仅预检+补丁+同步）')
    args = ap.parse_args()

    patches = json.load(open(args.patches, encoding='utf-8'))
    themes = sorted({p['theme'] for p in patches})
    keys = [p['key'] for p in patches]

    t0 = time.time()
    # 1. 语法编译（验证单元·一级行为验证前的基础检查）
    step('1/7', '语法编译')
    import py_compile
    py_compile.compile(SRC_ST, doraise=True)
    print('语法 OK')

    # 2. 应用补丁（反思单元变异 → 记录单元写入）
    step('2/7', f'应用补丁 ({len(patches)} 簇)')
    apply_patches(patches)

    # 3. 五副本同步（输出单元·连接一致性）
    step('3/7', '五副本同步')
    sync_copies()

    # 4. 路由预检（验证单元·预期输出：variant_checker 问法命中率）
    step('4/7', f'路由预检 ({",".join(keys)})')
    out = run_py(os.path.join(CTP, 'tools', 'variant_checker.py'), ['--check', ','.join(keys)])
    m = re.search(r'(\d+) 个问法变体缺口', out)
    gaps = int(m.group(1)) if m else -1
    print(f'预检缺口: {gaps}')
    if gaps > 0:
        print('!! 存在问法变体缺口——建议先补触发词（或人工确认模板噪声）')

    if args.skip_test:
        print(f'\n=== 流水线完成（跳过测试）: {time.time()-t0:.0f}s ===')
        return

    # 5. 生成测试集 + 跑测试（验证单元·一级行为验证）
    step('5/7', f'生成并运行测试集 {args.version}')
    testset = gen_testset(args.version, themes)
    runner = os.path.join(CTP, 'tools', 'run_conflict_v64.py')  # 模板 runner（结构相同）
    # 动态生成该版本的 runner
    runner_v = os.path.join(CTP, 'tools', f'run_conflict_{args.version}.py')
    src = open(runner, encoding='utf-8').read()
    src = re.sub(r'conflict_testset_v\d+', f'conflict_testset_{args.version}', src)
    src = re.sub(r'cv\d+-', f'cv{args.version}-', src)
    src = re.sub(r'v\d+ 基线', f'{args.version} 基线', src)
    open(runner_v, 'w', encoding='utf-8').write(src)
    run_py(runner_v)

    # 6. 全量回归（验证单元·稳态检测 = 存在保护）
    step('6/7', '全量回归 v44-当前（稳态检测）')
    run_py(os.path.join(CTP, 'tools', 'run_regress_c14.py'))

    # 7. 台账刷新（记录单元·记录）
    step('7/7', '台账刷新')
    run_py(os.path.join(CTP, 'tools', 'ledger.py'), ['--refresh'])

    print(f'\n=== 流水线完成: {time.time()-t0:.0f}s ===')


if __name__ == '__main__':
    main()
