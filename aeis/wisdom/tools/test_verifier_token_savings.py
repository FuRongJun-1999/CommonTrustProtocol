# -*- coding: utf-8 -*-
"""test_verifier_token_savings.py · token 节省度量复现测试（阶段 5 证据）

复现流程（独立 temp 缓存 + 独立审计日志，不污染真实数据）：
  ① 冷跑：681 单元首次经 verifier（本应输入 LLM 的「表 + 请求」全部本地处理）
  ② 暖跑：681 单元缓存全命中（零计算返回）
  ③ 聚合审计日志：记录「白箱自动输出的内容量」与「减少的 LLM 输入 token」
  ④ 报告 JSON 落盘（tools/verify_token_savings_report.json，可审计复现证据）

「减少的 LLM 输入」模型（与设计文档一致）：
  原方案每次查表校验 = 把整张表（六域单元库定义）塞进 LLM 上下文 + 当前请求；
  本地化后 = 表与请求均不再输入 LLM → 每次省 (表 + 请求) 的 token。
"""
import sys, io, os, json, tempfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')

from verifier import Verifier, VerifyRequest, VerifyCache, _table_payload_chars
from compiler_code_units import COMPILER_UNITS
from python_code_units import PYTHON_UNITS
from graph_db_units import GRAPH_UNITS
from os_units import OS_UNITS
from browser_units import BROWSER_UNITS
from net_units import NET_UNITS

DOMAINS = [('compiler', COMPILER_UNITS), ('pylang', PYTHON_UNITS),
           ('graph', GRAPH_UNITS), ('os', OS_UNITS),
           ('browser', BROWSER_UNITS), ('net', NET_UNITS)]
UNITS = [(d, uid, u) for d, units in DOMAINS for uid, u in units.items()]
TOTAL = len(UNITS)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

tmpdir = tempfile.mkdtemp()
cache_path = os.path.join(tmpdir, 'cache.json')
log_path = os.path.join(tmpdir, 'savings.jsonl')

# ① 冷跑（首次校验）
v1 = Verifier(cache=VerifyCache(path=cache_path, version=0, savings_log=log_path))
cold_ok = 0
for d, uid, u in UNITS:
    req = VerifyRequest(task=u['task'], code=u['pattern'], unit_id=uid,
                        cases=list(u.get('cases', [])),
                        expected_structure={'inject': True} if u.get('needs_inject') else {})
    if v1.verify(req).ok:
        cold_ok += 1
check('① 冷跑：681 单元首次校验全部通过', cold_ok == TOTAL, f'{cold_ok}/{TOTAL}')

# ② 暖跑（缓存全命中，零计算）
v2 = Verifier(cache=VerifyCache(path=cache_path, version=0, savings_log=log_path))
for d, uid, u in UNITS:
    req = VerifyRequest(task=u['task'], code=u['pattern'], unit_id=uid,
                        cases=list(u.get('cases', [])),
                        expected_structure={'inject': True} if u.get('needs_inject') else {})
    v2.verify(req)
check('② 暖跑：681 次请求全命中（零计算返回）',
      v2.cache.hits == TOTAL and v2.cache.misses == 0,
      f"hits={v2.cache.hits} misses={v2.cache.misses}")

# ③ 聚合审计日志
sv = VerifyCache(path=cache_path, version=0, savings_log=log_path).savings()
table_chars = _table_payload_chars()
# 白箱自动输出内容量：681 个 pattern（生成的代码内容）字符数
gen_chars = sum(len(u['pattern']) for d, uid, u in UNITS)
gen_tokens = sum(len(u['pattern']) * 0.35 for d, uid, u in UNITS)  # 代码为主，0.35 token/字符
check('③ 审计日志：1362 次校验记录（冷 681 + 暖 681）',
      sv['requests'] == TOTAL * 2 and sv['hits'] == TOTAL,
      f"requests={sv['requests']} hits={sv['hits']}")
check('③b 减少的 LLM 输入 > 0（表+请求累计 token）',
      sv['saved_tokens'] > 0 and sv['saved_chars'] > 0,
      f"≈{sv['saved_tokens']:,} token / {sv['saved_chars']:,} 字符")

# ④ 报告落盘（复现证据）
report = {
    "date": __import__('time').strftime("%Y-%m-%d %H:%M:%S"),
    "model": "本地校验器 Zero-LLM Verifier v4 + 审计日志度量",
    "units_verified": TOTAL,
    "table_chars": table_chars,
    "whitebox_generated_chars": gen_chars,
    "whitebox_generated_tokens_est": int(gen_tokens),
    "requests": sv['requests'],
    "cache_hits": sv['hits'],
    "hit_rate": round(100.0 * sv['hits'] / sv['requests'], 1),
    "saved_llm_input_chars": sv['saved_chars'],
    "saved_llm_input_tokens_est": sv['saved_tokens'],
    "note": ("每次校验省下的 LLM 输入 = 表（六域单元定义 %d 字符）+ 请求；"
             "本地化后表与请求均不再输入 LLM；token 为中文混合内容确定性估算"
             % table_chars),
}
report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'verify_token_savings_report.json')
with open(report_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)

print('\n===== token 节省复现报告 =====')
print(f'白箱自动输出内容量: {gen_chars:,} 字符（681 单元生成代码）≈ {int(gen_tokens):,} token')
print(f'「整张表」内容量: {table_chars:,} 字符（六域单元库定义）')
print(f'校验请求: {sv["requests"]} 次（冷 {TOTAL} + 暖 {TOTAL} 全命中）')
print(f'减少的 LLM 输入: {sv["saved_chars"]:,} 字符 ≈ {sv["saved_tokens"]:,} token')
print(f'（每次 = 表 {table_chars:,} 字符 + 请求；若走 LLM 查表，这些内容将全部输入上下文）')
print(f'报告已落盘: {report_path}')

check('④ 复现报告已生成', os.path.exists(report_path), report_path.split('\\')[-1])

print(f'\n=== token 节省度量复现: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
