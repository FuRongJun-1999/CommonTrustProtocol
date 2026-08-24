# -*- coding: utf-8 -*-
"""验证：①Ollama 原生 /api/chat 带 options.num_ctx=32768 能否承载大请求
②ornith-1.5-9b 模型参数（num_ctx 现状）"""
import json, urllib.request, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

# 0. 模型参数
print('[0] ollama show 模型参数:')
try:
    r = subprocess.run([r'C:\Users\FuRongJun\AppData\Local\Programs\Ollama\ollama.exe',
                        'show', 'ornith-1.5-9b', '--modelfile'],
                       capture_output=True, text=True, encoding='utf-8', timeout=60)
    for ln in r.stdout.splitlines():
        if 'num_ctx' in ln or 'context' in ln.lower():
            print('   ', ln.strip())
except Exception as e:
    print('   show 失败:', e)

# 1. 原生 API /api/chat 带 num_ctx
big_system = "你是灵枢。请简洁回答。" + ("知识背景。" * 3000)
body = {
    "model": "ornith-1.5-9b",
    "messages": [
        {"role": "system", "content": big_system},
        {"role": "user", "content": "1+1等于几？只回答数字。"},
    ],
    "options": {"num_ctx": 32768},
    "stream": False,
}
req = urllib.request.Request(
    'http://localhost:11434/api/chat',
    data=json.dumps(body).encode('utf-8'), method='POST',
    headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read().decode('utf-8'))
    print(f"[1] 原生API num_ctx=32768: OK reply={resp.get('message', {}).get('content', '')[:30]!r}")
except urllib.error.HTTPError as e:
    print(f"[1] FAIL HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:150]}")
except Exception as e:
    print(f"[1] FAIL: {e}")
