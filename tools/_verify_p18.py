# -*- coding: utf-8 -*-
import re, collections, sys, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
p = r'D:\Program Files\2_ai\CommonTrustProtocol\tools\python_code_units.py'
s = open(p, encoding='utf-8').read()
keys = re.findall(r'^\s+"([^"]+)": \{', s, re.M)
print('keys:', len(keys), 'dups:', [k for k, v in collections.Counter(keys).items() if v > 1])
print('new:', [k for k in keys if k in ('数据结构-链表', '工具-进制转换', '异常-异常链')])
spec = importlib.util.spec_from_file_location('pcu2', p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print('dict units:', len(m.PYTHON_UNITS))
for uid in ('数据结构-链表', '工具-进制转换', '异常-异常链'):
    u = m.PYTHON_UNITS[uid]
    print(uid, u['task'], len(u['cases']))
