# -*- coding: utf-8 -*-
"""最终验证：DSH 完整场景（大系统提示 + 历史 + tools）→ Ollama 32k 模型"""
import json, urllib.request, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:11434/v1'
MODEL = 'ornith-1.5-9b-32k'

# DSH 风格：长系统提示 + 工具 schema + 历史 + 当前问题（>10k tokens）
system = "你是灵枢，白箱智能体。使用工具完成任务，简洁回答。" + ("系统背景说明。" * 2500)
tools = [
    {"type": "function", "function": {"name": "read_file", "description": "读取文件",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "run_shell", "description": "执行命令",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "web_search", "description": "搜索",
        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
]
messages = [
    {"role": "system", "content": system},
    {"role": "user", "content": "查看当前目录文件列表"},
    {"role": "assistant", "content": None, "tool_calls": [{"id": "c1", "type": "function", "function": {"name": "run_shell", "arguments": "{\"command\":\"ls\"}"}}]},
    {"role": "tool", "tool_call_id": "c1", "content": "file1.txt\nfile2.py"},
    {"role": "user", "content": "好的，读取 file1.txt 的内容"},
]
req = urllib.request.Request(
    BASE + '/chat/completions',
    data=json.dumps({"model": MODEL, "messages": messages, "tools": tools,
                     "stream": False, "max_tokens": 200}).encode('utf-8'),
    method='POST', headers={'Content-Type': 'application/json'})
try:
    with urllib.request.urlopen(req, timeout=300) as r:
        resp = json.loads(r.read().decode('utf-8'))
    m = resp['choices'][0]['message']
    print(f'OK: DSH 完整场景成功')
    print(f'  content={str(m.get("content"))[:50]!r}')
    if m.get('tool_calls'):
        print(f'  tool_calls={json.dumps(m["tool_calls"], ensure_ascii=False)[:100]}')
except urllib.error.HTTPError as e:
    print(f'FAIL HTTP {e.code}: {e.read().decode("utf-8", errors="replace")[:200]}')
except Exception as e:
    print(f'FAIL: {e}')
