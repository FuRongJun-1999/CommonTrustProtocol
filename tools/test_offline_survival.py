# -*- coding: utf-8 -*-
"""无 API 自维持降级测试：upstream 不可用时，
①知识问答走白箱（离线可用）②白箱无把握→降级诚实边界（不返回错误文本）"""
import sys, os, importlib
sys.stdout.reconfigure(encoding='utf-8')
CTP = r'D:\Program Files\2_ai\CommonTrustProtocol'
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')

# 强制上游 key 为空（模拟 API 断开/未配置）
os.environ['DEEPSEEK_API_KEY'] = ''
os.environ['LINGSHU_UPSTREAM_KEY'] = ''
from aeis.roleplay_chat import LingshuChat

lc = LingshuChat(data_dir=os.path.join(r'D:\Program Files\2_ai\knowledge-base', 'roleplay_data'),
                 upstream_key_var='LINGSHU_UPSTREAM_KEY')

print('=== 测试1: 知识问答（应白箱回答，不依赖 API） ===')
r = lc.respond('什么是碳中和？', session_id='offline-test-1')
print(f"  route={r.get('route')} degraded={r.get('degraded')} len={len(r['reply'])}")
print(f"  {r['reply'][:60]}...")
assert '碳中和' in r['reply'] and 'LLM' not in r['reply'], '知识问答应白箱回答'

print('\n=== 测试2: 角色场景（LLM 不可用→应降级诚实边界，不返回错误文本） ===')
r2 = lc.respond('你好，给我讲个故事吧', session_id='offline-test-2', role_id='whale')
print(f"  route={r2.get('route')} degraded={r2.get('degraded')} len={len(r2['reply'])}")
print(f"  {r2['reply'][:80]}...")
assert '（未配置' not in r2['reply'] and 'LLM 调用失败' not in r2['reply'], '不得返回错误文本'
assert '离线模式' in r2['reply'] or '知识库' in r2['reply'], '应诚实声明离线'

print('\n=== 测试3: 无角色开放问题（应降级，不崩） ===')
r3 = lc.respond('帮我写一首诗', session_id='offline-test-3')
print(f"  route={r3.get('route')} degraded={r3.get('degraded')} len={len(r3['reply'])}")
print(f"  {r3['reply'][:80]}...")
assert '（' not in r3['reply'][:3] or '离线' in r3['reply'], '不得返回裸错误文本'

print('\n=== 无 API 自维持降级测试全部通过 ===')
lc.close()
