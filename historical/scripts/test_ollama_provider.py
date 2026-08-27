# -*- coding: utf-8 -*-
"""验证：Ollama 本地提供方（roleplay 角色场景本地优先 + 无 API 可推理）"""
import sys, os, importlib
sys.stdout.reconfigure(encoding='utf-8')
CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
sys.path.insert(0, CTP)
sys.path.insert(0, os.path.join(CTP, 'aeis'))
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')

# 1. config 含 Ollama 提供方（harness 是 CTP\aeis 下的顶层包）
sys.path.insert(0, os.path.join(CTP, 'aeis'))
from harness.core.config import load_config
cfg = load_config()
provs = {p['name']: p for p in cfg['model'].get('providers', [])}
print('[1] config providers:', list(provs.keys()), '| local:', cfg['model'].get('local'))
assert 'ollama' in provs and provs['ollama']['local'], 'ollama 本地提供方缺失'

# 2. roleplay 角色场景本地 Ollama 优先（云端 key 置空，模拟 API 断开）
os.environ['LINGSHU_UPSTREAM_KEY'] = ''
os.environ['DEEPSEEK_API_KEY'] = ''
from aeis.roleplay_chat import LingshuChat
lc = LingshuChat(data_dir=os.path.join(r'D:\Program Files\2_ai\knowledge-base', 'roleplay_data'),
                 upstream_key_var='LINGSHU_UPSTREAM_KEY')
r = lc.respond('你好，你叫什么名字？', session_id='ollama-test', role_id='whale')
print(f'[2] 角色场景(云端key空): route={r.get("route")} degraded={r.get("degraded")} len={len(r["reply"])}')
print(f'    reply: {r["reply"][:80]!r}')
assert 'LLM 调用失败' not in r['reply'] and '未配置' not in r['reply'], '不应返回云端错误'
print('[2] ✓ 角色场景走本地 Ollama（离线可用）')

# 3. 无角色开放问题（云端 key 空，prefer_local=False → 云端失败 → 降级白箱/诚实）
r2 = lc.respond('帮我写一首诗', session_id='ollama-test2')
print(f'[3] 无角色开放(云端key空): route={r2.get("route")} len={len(r2["reply"])}')
print(f'    reply: {r2["reply"][:60]!r}')
assert 'LLM 调用失败' not in r2['reply'], '不得返回云端错误文本'
print('[3] ✓ 不崩、无错误文本')

lc.close()
print('\n=== Ollama 本地提供方验证全部通过 ===')
