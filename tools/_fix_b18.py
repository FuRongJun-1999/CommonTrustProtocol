# -*- coding: utf-8 -*-
p = r'D:\Program Files\2_ai\CommonTrustProtocol\tools\browser_units.py'
s = open(p, encoding='utf-8').read()
NL = chr(92) + 'n'
Q = chr(34)

unit = [
    '    "安全-CORS检查": {',
    '        "task": "CORS检查",',
    '        "pattern": (',
    '            "def cors_check(origin, target, method=\'GET\'):' + NL + Q,
    '            "    # CORS：同源放行 / 简单请求放行 / 预检判定（跨域资源共享）' + NL + Q,
    '            "    if origin == target:' + NL + Q,
    '            "        return \'same-origin\'' + NL + Q,
    '            "    if method in (\'GET\', \'HEAD\', \'POST\'):' + NL + Q,
    '            "        return \'simple\'' + NL + Q,
    '            "    return \'preflight\'' + NL + '"),',
    '        "cases": [((\'https://a.com\', \'https://a.com\'), \'same-origin\'),',
    "                  (('https://a.com', 'https://b.com'), 'simple'),",
    "                  (('https://a.com', 'https://b.com', 'PUT'), 'preflight'),",
    "                  (('https://a.com', 'https://b.com', 'DELETE'), 'preflight')],",
    '        "params": [],',
    '        "calibration": "对照：浏览器安全——CORS 跨域资源共享（同源/简单/预检三态）",',
    '    },',
    '    "渲染-文本排版": {',
    '        "task": "文本排版",',
    '        "pattern": (',
    '            "def text_wrap(text, width):' + NL + Q,
    '            "    # 文本排版：按宽度贪心换行（文本布局——每行不超宽度）' + NL + Q,
    '            "    if not text:' + NL + Q,
    '            "        return []' + NL + Q,
    '            "    lines = []' + NL + Q,
    '            "    line = \'\'' + NL + Q,
    '            "    for ch in text:' + NL + Q,
    '            "        if len(line) == width:' + NL + Q,
    '            "            lines.append(line)' + NL + Q,
    '            "            line = ch' + NL + Q,
    '            "        else:' + NL + Q,
    '            "            line += ch' + NL + Q,
    '            "    if line:' + NL + Q,
    '            "        lines.append(line)' + NL + Q,
    '            "    return lines' + NL + '"),',
    '        "cases": [(("abcd", 2), ["ab", "cd"]),',
    "                  (('abc', 5), ['abc']),",
    "                  (('', 3), [])],",
    '        "params": [],',
    '        "calibration": "对照：浏览器渲染——文本换行（按宽度贪心断行）",',
    '    },',
    '    "浏览器-剪贴板": {',
    '        "task": "剪贴板",',
    '        "pattern": (',
    '            "def clipboard_ops(state, op, text=None):' + NL + Q,
    '            "    # 剪贴板：copy 写入 / paste 读取 / clear 清空（系统剪贴板）' + NL + Q,
    '            "    if op == \'copy\':' + NL + Q,
    '            "        state[\'text\'] = text' + NL + Q,
    '            "        return \'copied\'' + NL + Q,
    '            "    if op == \'paste\':' + NL + Q,
    '            "        return state.get(\'text\')' + NL + Q,
    '            "    if op == \'clear\':' + NL + Q,
    '            "        state[\'text\'] = None' + NL + Q,
    '            "        return \'cleared\'' + NL + Q,
    '            "    return None' + NL + '"),',
    '        "cases": [(({}, \'copy\', \'你好\'), \'copied\'),',
    "                  (({'text': '你好'}, 'paste'), '你好'),",
    "                  (({}, 'paste'), None),",
    "                  (({'text': 'x'}, 'clear'), 'cleared')],",
    '        "params": [],',
    '        "calibration": "对照：浏览器 API——navigator.clipboard（copy/paste 读写剪贴板）",',
    '    },',
]
block = '\n'.join(unit) + '\n'
anchor = '\n}\n\n\ndef route_browser_unit'
idx = s.rfind(anchor)
assert idx > 0, 'anchor not found'
s = s[:idx] + '\n' + block + '}\n\n\ndef route_browser_unit' + s[idx + len(anchor):]
open(p, 'w', encoding='utf-8').write(s)
print('OK appended; new length', len(s.splitlines()), 'lines')
