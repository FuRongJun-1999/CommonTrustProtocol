# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from code_compose import domain_route
qs = [
    ('CORS', '写一个 CORS 检查单元（跨域资源共享）'),
    ('文本排版', '写一个文本排版单元（宽度换行）'),
    ('剪贴板', '写一个剪贴板单元（复制粘贴）'),
]
for label, q in qs:
    r = domain_route(q)
    print(label, '->', r.get('ok'), r.get('unit'))
