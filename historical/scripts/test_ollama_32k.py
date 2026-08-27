# -*- coding: utf-8 -*-
"""验证 ornith-1.5-9b-32k（OpenAI 兼容端点承载 DSH 大请求）"""
import json, urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:11434/v1'
MODEL = 'ornith-1.5-9b-32k'

big_system = "你是灵枢，一个白箱智能体。请简洁回答。" + ("知识背景。" * 3000)
req = urllib.request.Request(
    BASE + '/chat/completions',
    data=json.dumps({"model": MODEL,
                     "messages": [{"role": "system", "content": big_system},
                                  {"role": "user", "content": "1+1等于几？只回答数字。"}],
                     "stream": False, "max_tokens": 50}).encode('utf-8'),
    method='POST', headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read().decode('utf-8'))
    reply = resp['choices'][0]['message']['content'].strip()
    print(f'OK: 32k 模型承载大请求成功 reply={reply!r}')
except urllib.error.HTTPError as e:
    print(f'FAIL HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:150]}')
except Exception as e:
    print(f'FAIL: {e}')
