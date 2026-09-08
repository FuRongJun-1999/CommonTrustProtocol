# -*- coding: utf-8 -*-
"""build_knowledge_md.py · 白箱知识库 sqlite → md 综述目录迁移

目标：将 wisdom-book-cloud.db 的 4,355 个知识点 与 wisdom_cards/ 的 116 个
学科综述文件合并为一个统一的 md 知识目录（aeis/knowledge/），并生成索引。

原则：
  - wisdom_cards/ 为骨架（116 个学科文件的格式和已有知识点）
  - sqlite 中心跳新增的知识点追加到对应学科文件
  - 匹配不上的创建新学科文件
  - 知识点之间允许重叠/包含，只要 _index.json 能正确索引
  - wisdom_cards/ 和 sqlite 原文件不动（安全）
"""
import sqlite3, json, os, re, shutil
from collections import defaultdict
from datetime import datetime

# ─── 路径 ───
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "aeis", "wisdom", "wisdom-book-cloud.db")
WC_DIR = os.path.join(ROOT, "aeis", "seed_knowledge", "wisdom_cards")
OUT_DIR = os.path.join(ROOT, "aeis", "knowledge")
INDEX_PATH = os.path.join(OUT_DIR, "_index.json")

P1_CUTOFF = 1788350400  # P1 迁移时间戳


def normalize_domain(raw):
    """域名归一化：去后缀、strip"""
    if not raw:
        return None
    s = raw.strip()
    s = re.sub(r'知识点内容\s*[（(].*?[)）]\s*$', '', s).strip()
    s = re.sub(r'\s*知识点\s*[（(].*?[)）]\s*$', '', s).strip()
    return s if s else None


def match_subject(domain_raw, subject_names):
    """域名 → 已有学科文件名。精确 → 包含 → None"""
    d = normalize_domain(domain_raw)
    if not d:
        return None
    if d in subject_names:
        return d
    # 包含匹配（域名包含学科名，或反过来）
    for sn in subject_names:
        if sn in d or d in sn:
            return sn
    # 去修饰词后再试
    d_clean = re.sub(r'(基础|通识|常识|人文|科技|生活|前沿|传统|古典|现代|世界|中国|西方|白箱|智能论)', '', d)
    if d_clean:
        for sn in subject_names:
            sn_clean = re.sub(r'(基础|通识|常识|人文|科技|生活|前沿|传统|古典|现代|世界|中国|西方|白箱|智能论)', '', sn)
            if sn_clean and (d_clean in sn_clean or sn_clean in d_clean):
                return sn
    return None


def extract_content(sa):
    """从 state_attributes 中提取知识点内容"""
    comment = sa.get('comment') or {}
    if isinstance(comment, dict):
        exec_text = comment.get('执行', '')
        if isinstance(exec_text, list):
            exec_text = '；'.join(exec_text)
        if exec_text:
            return exec_text
    return ''


def make_header(domain, entries):
    """为新学科文件生成头部"""
    return (
        f"# {domain}·知识综述\n\n"
        f"- **领域**: {domain}\n"
        f"- **来源**: 心跳知识整理（自动归档）\n"
        f"- **整理日期**: 2026-09-07\n"
        f"- **知识点数**: {len(entries)}\n\n"
        f"## 知识点内容\n\n"
    )


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    stats = {'files_copied': 0, 'kp_appended': 0, 'kp_skipped_dup': 0,
             'new_files': 0, 'new_kp': 0, 'total_kp_indexed': 0}
    index = {}  # 知识点名 → {"file": str, "subject": str}

    # ═══════ Phase 1: 复制 wisdom_cards 骨架到 knowledge/ ═══════
    print("=== Phase 1: 复制 wisdom_cards 骨架 ===")
    wc_subjects = {}  # subject_name → file basename
    for fn in sorted(os.listdir(WC_DIR)):
        if not fn.endswith('.md'):
            continue
        subject = fn.replace('·知识综述.md', '')
        src = os.path.join(WC_DIR, fn)
        dst = os.path.join(OUT_DIR, fn)
        shutil.copy2(src, dst)
        # 提取已有知识点名
        with open(src, encoding='utf-8') as f:
            content = f.read()
        kps = set(re.findall(r'^### (.+)$', content, re.MULTILINE))
        wc_subjects[subject] = {'file': fn, 'kps': kps}
        # 索引已有知识点
        for kp in kps:
            index[kp.strip()] = {'file': fn, 'subject': subject}
        stats['files_copied'] += 1
        stats['total_kp_indexed'] += len(kps)
    print(f"  复制 {stats['files_copied']} 个文件, "
          f"索引 {stats['total_kp_indexed']} 个已有知识点")

    # ═══════ Phase 2: 读 sqlite 全量节点 ═══════
    print("\n=== Phase 2: 读 sqlite ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT id, state_attributes, created_at FROM nodes '
                'WHERE layer="knowledge"')
    all_nodes = []
    for nid, sa_str, created in cur.fetchall():
        try:
            sa = json.loads(sa_str) if sa_str else {}
        except (ValueError, TypeError):
            sa = {}
        all_nodes.append((nid, sa, created or 0))
    conn.close()
    print(f"  读取 {len(all_nodes)} 个节点")

    # ═══════ Phase 3: 匹配 + 追加/新建 ═══════
    print("\n=== Phase 3: 匹配与追加 ===")
    subject_names = set(wc_subjects.keys())

    # 按目标学科分组
    to_append = defaultdict(list)     # subject → [(kp_name, content)]
    to_create = defaultdict(list)     # new_domain → [(kp_name, content)]
    matched_names = set()             # 已在文件中的知识点名（跳过）

    for nid, sa, created in all_nodes:
        kp_name = (sa.get('name') or nid).strip()
        domain_raw = sa.get('domain') or ''
        content = extract_content(sa)
        if not content or not kp_name:
            continue
        # 去重：如果这个知识点名已经在索引里，跳过
        if kp_name in index:
            stats['kp_skipped_dup'] += 1
            continue

        subject = match_subject(domain_raw, subject_names)
        if subject:
            to_append[subject].append((kp_name, content, nid))
        else:
            d = normalize_domain(domain_raw) or '未分类'
            to_create[d].append((kp_name, content, nid))

    # 追加到已有文件
    for subject, entries in sorted(to_append.items()):
        info = wc_subjects.get(subject)
        if not info:
            # 匹配异常，当新文件处理
            to_create[subject].extend(entries)
            continue
        filepath = os.path.join(OUT_DIR, info['file'])
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        appended = []
        for kp_name, kp_content, nid in entries:
            if kp_name in info['kps']:
                stats['kp_skipped_dup'] += 1
                continue
            section = f"\n### {kp_name}\n\n{kp_content}\n"
            content += section
            appended.append(kp_name)
            index[kp_name.strip()] = {'file': info['file'], 'subject': subject}
            stats['kp_appended'] += 1
        if appended:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            # 更新内存中的 kps 集合
            info['kps'].update(appended)

    # 创建新学科文件
    for domain, entries in sorted(to_create.items()):
        fn = f"{domain}.md"
        filepath = os.path.join(OUT_DIR, fn)
        # 避免与已有文件重名
        if os.path.exists(filepath):
            fn = f"{domain}·补充.md"
            filepath = os.path.join(OUT_DIR, fn)
        header = make_header(domain, entries)
        body_parts = []
        for kp_name, kp_content, nid in entries:
            if kp_name in index:
                stats['kp_skipped_dup'] += 1
                continue
            body_parts.append(f"### {kp_name}\n\n{kp_content}\n")
            index[kp_name.strip()] = {'file': fn, 'subject': domain}
            stats['new_kp'] += 1
        if body_parts:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header + '\n'.join(body_parts))
            stats['new_files'] += 1

    # ═══════ Phase 4: 生成索引 ═══════
    print("\n=== Phase 4: 生成索引 ===")
    stats['total_kp_indexed'] = len(index)
    index_data = {
        'meta': {
            'version': '1.0',
            'generated': datetime.now().isoformat(),
            'total_kp': len(index),
            'total_files': stats['files_copied'] + stats['new_files'],
            'description': '白箱知识库 MD 目录索引（知识点名 → 学科文件）',
            'usage': 'index[kp_name] → {"file": "xxx.md", "subject": "xxx"}；'
                     '在文件中搜索 "### kp_name" 定位到具体知识点',
        },
        'index': index,
    }
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=1)
    print(f"  索引写入 {INDEX_PATH}")
    print(f"  索引条目: {len(index)}")

    # ═══════ Phase 5: 验证 ═══════
    print("\n=== Phase 5: 验证 ===")
    # 统计输出目录
    md_files = [f for f in os.listdir(OUT_DIR)
                if f.endswith('.md')]
    total_md_kps = 0
    for fn in md_files:
        with open(os.path.join(OUT_DIR, fn), encoding='utf-8') as f:
            kps = re.findall(r'^### (.+)$', f.read(), re.MULTILINE)
            total_md_kps += len(kps)
    print(f"  输出目录 .md 文件: {len(md_files)} 个")
    print(f"  md 文件中 ### 知识点总数: {total_md_kps}")
    print(f"  索引条目数: {len(index)}")

    # 抽样验证索引正确性
    sample_size = min(20, len(index))
    sample_kps = list(index.keys())[:sample_size]
    errors = 0
    for kp in sample_kps:
        info = index[kp]
        filepath = os.path.join(OUT_DIR, info['file'])
        if not os.path.exists(filepath):
            errors += 1
            print(f"  [ERR] {kp} → {info['file']} 文件不存在")
            continue
        with open(filepath, encoding='utf-8') as f:
            if f"### {kp}" not in f.read():
                errors += 1
                print(f"  [ERR] {kp} 在 {info['file']} 中未找到 ### 标题")
    if errors == 0:
        print(f"  抽样 {sample_size} 个索引条目全部正确")
    else:
        print(f"  抽样 {sample_size} 个中 {errors} 个错误")

    # ═══════ 汇总 ═══════
    print(f"\n{'='*50}")
    print(f"迁移完成！")
    print(f"  复制骨架文件: {stats['files_copied']}")
    print(f"  新建学科文件: {stats['new_files']}")
    print(f"  追加知识点: {stats['kp_appended']}")
    print(f"  新建知识点: {stats['new_kp']}")
    print(f"  跳过重复: {stats['kp_skipped_dup']}")
    print(f"  索引总条目: {stats['total_kp_indexed']}")
    print(f"  输出目录: {OUT_DIR}")
    print(f"{'='*50}")

    return stats


if __name__ == '__main__':
    main()
