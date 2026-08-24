# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import code_compose as cc

qs = {
    "安全-CORS检查": "写一个 CORS 检查单元（跨域资源共享）",
    "渲染-文本排版": "写一个文本排版单元（宽度换行）",
    "浏览器-剪贴板": "写一个剪贴板单元（复制粘贴）",
}
for uid, q in qs.items():
    e = cc.domain_solidify(q, domain="browser", uid=uid)
    print(uid, '->', 'solidified' if e else 'FAILED')
for uid, q in qs.items():
    r = cc.domain_route(q)
    print(uid, 'route ok:', r.get('ok'), 'solidified:', r.get('solidified'))
