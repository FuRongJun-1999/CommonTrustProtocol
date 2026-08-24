# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
import code_compose as cc

qs = {
    "数据结构-链表": "写一个链表单元（节点链）",
    "工具-进制转换": "写一个进制转换单元（进制互转）",
    "异常-异常链": "写一个异常链单元（原因保留）",
}
for uid, q in qs.items():
    e = cc.domain_solidify(q, domain="pylang", uid=uid)
    print(uid, '->', 'solidified' if e else 'FAILED')
for uid, q in qs.items():
    r = cc.domain_route(q)
    print(uid, 'route ok:', r.get('ok'), 'solidified:', r.get('solidified'))
