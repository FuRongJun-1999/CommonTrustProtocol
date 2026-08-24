# -*- coding: utf-8 -*-
"""验证 Ollama 上下文已扩容（DSH 400 修复）：
模拟 DSH 的大请求（长系统提示+历史+工具schema，>8192 tokens）"""
import json, urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:11434/v1'
MODEL = 'ornith-1.5-9b'

# 构造 >8192 tokens 的请求（约 10000+ 中文字符 ≈ 15000+ tokens）
big_system = "你是灵枢，一个白箱智能体。请简洁回答。" + ("知识背景。" * 3000)  # 约 9000+ 字
messages = [
    {"role": "system", "content": big_system},
    {"role": "user", "content": "请回答：1+1等于几？只回答数字。"},
]
n_chars = sum(len(m['content']) for m in messages)
print(f'请求字符数约 {n_chars}（中文≈1.5字/token → 约 {int(n_chars/1.5)} tokens）')

req = urllib.request.Request(
    BASE + '/chat/completions',
    data=json.dumps({"model": MODEL, "messages": messages, "stream": False,
                     "max_tokens": 50}).encode('utf-8'),
    method='POST', headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=180) as r:
        resp = json.loads(r.read().decode('utf-8'))
    reply = resp['choices'][0]['message']['content'].strip()
    print(f'OK: 大请求成功（上下文已扩容） reply={reply!r}')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f'FAIL HTTP {e.code}: {body[:200]}')
except Exception as e:
    print(f'FAIL: {e}')
