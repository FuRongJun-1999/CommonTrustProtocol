# -*- coding: utf-8 -*-
"""验证 Ollama OpenAI 兼容端点（DSH 后备适配性）：
①基础 chat.completions ②带 tools 的工具调用（DSH agent 依赖）"""
import json, urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')

BASE = 'http://localhost:11434/v1'
MODEL = 'ornith-1.5-9b'

def call(payload):
    req = urllib.request.Request(
        BASE + '/chat/completions',
        data=json.dumps(payload).encode('utf-8'), method='POST',
        headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        return {'error': str(e)}

# 1. 基础对话
print('[1] 基础 chat.completions:')
r = call({"model": MODEL, "messages": [{"role": "user", "content": "说一个字：好"}],
          "stream": False, "max_tokens": 50})
if 'choices' in r:
    print(f'  OK reply={r["choices"][0]["message"]["content"][:30]!r}')
else:
    print(f'  FAIL {r}')

# 2. 带 tools 的工具调用（DSH agent 会发工具 schema）
print('[2] 带 tools 的工具调用:')
tools = [{"type": "function",
          "function": {"name": "get_weather", "description": "查询天气",
                       "parameters": {"type": "object",
                                      "properties": {"city": {"type": "string"}},
                                      "required": ["city"]}}}]
r2 = call({"model": MODEL,
           "messages": [{"role": "user", "content": "查一下北京的天气"}],
           "tools": tools, "stream": False, "max_tokens": 100})
if 'choices' in r2:
    m = r2['choices'][0]['message']
    tc = m.get('tool_calls')
    print(f'  OK tool_calls={json.dumps(tc, ensure_ascii=False)[:120] if tc else None} content={str(m.get("content"))[:40]!r}')
else:
    print(f'  FAIL {r2}')

# 3. 系统提示（DSH harness 会注入系统提示词）
print('[3] 系统提示 + 多轮:')
r3 = call({"model": MODEL,
           "messages": [{"role": "system", "content": "你是灵枢，简洁回答。"},
                        {"role": "user", "content": "1+1等于几？"}],
           "stream": False, "max_tokens": 50})
if 'choices' in r3:
    print(f'  OK reply={r3["choices"][0]["message"]["content"][:40]!r}')
else:
    print(f'  FAIL {r3}')
