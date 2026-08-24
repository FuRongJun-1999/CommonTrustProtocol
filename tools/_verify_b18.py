# -*- coding: utf-8 -*-
import re, collections, sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\Program Files\2_ai\CommonTrustProtocol\tools\browser_units.py'
s = open(p, encoding='utf-8').read()
keys = re.findall(r'^\s+"([^"]+)": \{', s, re.M)
print('keys:', len(keys), 'dups:', [k for k, v in collections.Counter(keys).items() if v > 1])
spec = importlib.util.spec_from_file_location('bu2', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print('dict:', len(m.BROWSER_UNITS))
for k in ('安全-CORS检查', '渲染-文本排版', '浏览器-剪贴板'):
    u = m.BROWSER_UNITS[k]
    print(k, u['task'], len(u['cases']))
