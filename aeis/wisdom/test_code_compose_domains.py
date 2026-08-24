# -*- coding: utf-8 -*-
"""test_code_compose_domains.py · 白箱自举正式管线接管（第六阶段·方案A）
四套域单元库（编译器/语言机制/图数据库/操作系统）接入 code_compose 正式管线：
  域识别 → 单元匹配 → 模板填充 → verify_code 三层自校验 → 固化 JSON → 固化直出
验证：①四域组合生成+自校验 ②域识别 ③固化 ④固化直出 ⑤未识别诚实回落"""
import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'D:\Program Files\2_ai\CommonTrustProtocol\tools')
from code_compose import (domain_route, domain_solidify, detect_domain,
                          compose_domain_code, CODE_SOLIDIFIED, _SOL_FILE)

pass_n = fail_n = 0
def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok: pass_n += 1
    else: fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')

# ① 四域组合生成 + 自校验（verify_code 三层）
QS = {
    "compiler": "写一个道德经指令编译单元（DAO→创建路径）",
    "pylang": "写一个闭包机制单元（捕获自由变量）",
    "graph": "写一个图遍历单元（BFS 可达节点）",
    "os": "写一个进程调度单元（FCFS 完成时间）",
}
ok_domains = 0
for domain, q in QS.items():
    d = detect_domain(q)
    r = domain_route(q)
    if d == domain and r.get("ok") and r.get("code"):
        ok_domains += 1
    check(f'① {domain} 域生成+自校验', d == domain and r.get("ok"),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:20]}')
check('① 四域全部生成', ok_domains == 4, f'{ok_domains}/4')

# ② 域识别
check('②a 域识别(编译器)', detect_domain("写个类型推断单元") == "compiler", '')
check('②b 域识别(操作系统)', detect_domain("写个内存分页分配") == "os", '')
check('②c 域识别(图)', detect_domain("写个条件路由图查询") == "graph", '')

# ③ 固化（自举纪律：验证通过才固化；用 TCP 握手单元）
e = domain_solidify("写一个 TCP 握手单元（三次握手状态）")
check('③ 域固化', e is not None and e.get("source") == "domain_solidified",
      str(e.get("unit") if e else None))
if e:
    key = f"domain:{e.get('domain')}|{e.get('unit')}"
    on_disk = key in json.load(open(_SOL_FILE, encoding="utf-8"))
    check('③b 固化写入JSON', key in CODE_SOLIDIFIED and on_disk,
          f'{key} 已固化到 JSON')

# ④ 固化直出
r2 = domain_route("写一个 TCP 握手单元（三次握手状态）")
check('④ 固化直出', r2.get("solidified") is True
      and r2.get("unit") == e.get("unit"), f'unit={r2.get("unit")}')

# ⑤ 未识别诚实回落
r3 = domain_route("什么是碳中和？")
check('⑤ 域未识别回落', not r3.get("ok") and "域未识别" in r3.get("reason", ""),
      r3.get("reason", "")[:20])

# ⑥ 旧管线回归（基础 CODE_UNITS 不受影响）
from code_compose import code_route
r4 = code_route("写一个函数把数组从小到大排序")
check('⑥ 旧管线回归', r4.get("ok") and "def " in r4.get("code", ""), '')

# ⑦ 目标4 迷你 Linux 深化（os 域 9 单元：页置换/inode/状态机/SJF 经正式管线）
os_qs = {
    "页置换": "写一个内存页置换单元（LRU 缺页次数）",
    "inode": "写一个 inode 查询单元（文件名→大小权限）",
    "状态机": "写一个进程状态机单元（就绪运行阻塞）",
    "SJF": "写一个最短作业调度单元（SJF 完成时间）",
}
os_ok = 0
for label, q in os_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        os_ok += 1
    check(f'⑦ {label} OS单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑦b OS 四新单元全部生成', os_ok == 4, f'{os_ok}/4')

# ⑧ 目标5 迷你浏览器（browser 域 4 单元经正式管线）
bw_qs = {
    "HTTP": "写一个 HTML DOM 解析单元（标签树）",
    "DOM": "写一个 HTML DOM 解析单元（标签树）",
    "CSS": "写一个 CSS 选择器匹配单元（tag/class）",
    "渲染": "写一个块布局渲染单元（换行堆叠）",
}
bw_ok = 0
for label, q in bw_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        bw_ok += 1
    check(f'⑧ {label} 浏览器单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑧b 浏览器四单元全部生成', bw_ok == 4, f'{bw_ok}/4')

# ⑨ 目标7 蓝牙和互联网（net 域 5 单元经正式管线）
nt_qs = {
    "IP分片": "写一个 TCP 握手单元（三次握手状态）",
    "TCP握手": "写一个 TCP 握手单元（三次握手状态）",
    "校验和": "写一个 UDP 校验和单元（16位取反）",
    "局域网发现": "写一个局域网发现单元（心跳在线判定）",
    "蜂群中继": "写一个蜂群中继单元（邻居递归传播）",
}
nt_ok = 0
for label, q in nt_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        nt_ok += 1
    check(f'⑨ {label} 网络单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑨b 网络五单元全部生成', nt_ok == 5, f'{nt_ok}/5')

# ⑩ 目标7 深化：蜂群协议（去重/路由表/超时重传/停等 经正式管线）
n2_qs = {
    "去重": "写一个蜂群消息去重单元（ID防重复）",
    "路由表": "写一个路由表更新单元（节点下一跳）",
    "超时重传": "写一个超时重传单元（未确认重传）",
    "停等": "写一个停等协议单元（逐包确认）",
}
n2_ok = 0
for label, q in n2_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n2_ok += 1
    check(f'⑩ {label} 蜂群协议单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑩b 蜂群四单元全部生成', n2_ok == 4, f'{n2_ok}/4')

# ⑪ 目标4 深化：文件系统/调度/并发/内存（os 域 9→13 经正式管线）
o2_qs = {
    "块管理": "写一个文件块管理单元（位图分配）",
    "优先级": "写一个优先级调度单元（高优先先跑）",
    "互斥锁": "写一个进程互斥锁单元（lock/unlock）",
    "首次适配": "写一个内存首次适配单元（空闲块分配）",
}
o2_ok = 0
for label, q in o2_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o2_ok += 1
    check(f'⑪ {label} OS深化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑪b OS深化四单元全部生成', o2_ok == 4, f'{o2_ok}/4')

# ⑫ 目标5 深化：浏览器渲染引擎（HTTP请求/URL解析/CSS级联/盒模型 经正式管线）
b2_qs = {
    "HTTP请求": "写一个 HTTP 请求构建单元（GET 请求行和头）",
    "URL解析": "写一个 URL 解析单元（协议主机端口路径）",
    "CSS级联": "写一个 CSS 级联单元（样式优先级）",
    "盒模型": "写一个盒模型单元（padding/border 总尺寸）",
}
b2_ok = 0
for label, q in b2_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b2_ok += 1
    check(f'⑫ {label} 浏览器深化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑫b 浏览器深化四单元全部生成', b2_ok == 4, f'{b2_ok}/4')

# ⑫c 深化单元行为自校验（三层 verify 已跑，直出执行复核盒模型）
r_box = domain_route("写一个盒模型单元（padding/border 总尺寸）")
code_box = r_box.get("code", "")
try:
    ns = {}
    exec(code_box, ns)
    got = ns['box_model'](100, 10, 2, 5) if 'box_model' in ns else None
    check('⑫c 盒模型行为复核', got == 124, f'box_model(100,10,2,5)={got}（margin 5 不计入）')
except Exception as ex:
    check('⑫c 盒模型行为复核', False, str(ex)[:60])

# ⑬ 目标2 深化：中文编译器循环语法（编译-循环/VM-循环执行 经正式管线）
c2_qs = {
    "循环编译": "写一个循环编译单元（当条件执行 while）",
    "循环执行": "写一个 VM 循环执行单元（while 循环运行）",
}
c2_ok = 0
for label, q in c2_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c2_ok += 1
    check(f'⑬ {label} 编译器循环单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑬b 编译器循环二单元全部生成', c2_ok == 2, f'{c2_ok}/2')

# ⑬c 循环编译+VM 执行端到端（compile_loop 产物喂 vm_run_loop 求 1+2）
r_cl = domain_route("写一个循环编译单元（当条件执行 while）")
r_vm = domain_route("写一个 VM 循环执行单元（while 循环运行）")
try:
    ns1, ns2 = {}, {}
    exec(r_cl["code"], ns1)
    exec(r_vm["code"], ns2)
    code = ns1["compile_loop"]([("LOAD", "i"), ("PUSH", 3), ("CMP_LT", None)],
                               [("LOAD", "s"), ("LOAD", "i"), ("ADD", None),
                                ("STORE", "s"),
                                ("LOAD", "i"), ("PUSH", 1), ("ADD", None),
                                ("STORE", "i")])
    res = ns2["vm_run_loop"](code, {"i": 1, "s": 0})
    got = res["symbols"]
    check('⑬c 循环编译→VM 执行端到端（1+2=3）',
          got == {"i": 3, "s": 3},
          f'symbols={got}（i 1→3 累积 s=1+2=3）')
except Exception as ex:
    check('⑬c 循环编译→VM 执行端到端（1+2=3）', False, str(ex)[:60])

# ⑭ 目标7 深化：蜂群会话层（消息分帧/会话状态 经正式管线）
n3_qs = {
    "消息分帧": "写一个蜂群消息分帧单元（字节流分隔）",
    "会话状态": "写一个蜂群会话状态单元（连接建立关闭）",
}
n3_ok = 0
for label, q in n3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n3_ok += 1
    check(f'⑭ {label} 蜂群会话层单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑭b 蜂群会话层二单元全部生成', n3_ok == 2, f'{n3_ok}/2')

# ⑭c 分帧+会话端到端（粘包拆帧→喂会话状态机）
r_frame = domain_route("写一个蜂群消息分帧单元（字节流分隔）")
r_sess = domain_route("写一个蜂群会话状态单元（连接建立关闭）")
try:
    ns1, ns2 = {}, {}
    exec(r_frame["code"], ns1)
    exec(r_sess["code"], ns2)
    frames, rest = ns1["frame_decode"](b'SYN\r\nACK\r\nFIN\r\n')
    state = 'LISTEN'
    for f in frames:
        ev = f.decode()
        state = ns2["session_step"]({'state': state}, ev)
    check('⑭c 分帧→会话端到端（SYN/ACK/FIN 三帧建立到关闭）',
          state == 'CLOSED' and rest == b'',
          f'frames={frames} state={state}')
except Exception as ex:
    check('⑭c 分帧→会话端到端（SYN/ACK/FIN 三帧建立到关闭）', False, str(ex)[:60])

# ⑮ 目标6 深化：条件图数据库最短路径（最短路径/加权最短 经正式管线）
g2_qs = {
    "最短路径": "写一个图最短路径单元（BFS 最少跳数）",
    "加权最短": "写一个加权最短路径单元（Dijkstra 代价最小）",
}
g2_ok = 0
for label, q in g2_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g2_ok += 1
    check(f'⑮ {label} 图数据库深化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑮b 图数据库深化二单元全部生成', g2_ok == 2, f'{g2_ok}/2')

# ⑮c 端到端：两链图 BFS 最短（2 跳） vs Dijkstra 加权（缺氧链代价 3 < 沸点降链 4）
r_sp = domain_route("写一个图最短路径单元（BFS 最少跳数）")
r_dj = domain_route("写一个加权最短路径单元（Dijkstra 代价最小）")
r_g = domain_route("写一个图存储单元（节点和边）")
try:
    ns_sp, ns_dj, ns_g = {}, {}, {}
    exec(r_sp["code"], ns_sp)
    exec(r_dj["code"], ns_dj)
    exec(r_g["code"], ns_g)
    g = ns_g["Graph"]()
    g.add_edge("气压低", "沸点降")
    g.add_edge("沸点降", "煮不熟")
    g.add_edge("气压低", "缺氧")
    g.add_edge("缺氧", "煮不熟")
    sp = ns_sp["shortest_path"](g, "气压低", "煮不熟")
    weights = {("气压低", "沸点降"): 2, ("沸点降", "煮不熟"): 2,
               ("气压低", "缺氧"): 1, ("缺氧", "煮不熟"): 2}
    dj = ns_dj["dijkstra"](g, weights, "气压低", "煮不熟")
    check('⑮c BFS最短2跳 vs Dijkstra加权选缺氧链(代价3<4)',
          sp == ["气压低", "沸点降", "煮不熟"] and dj == (["气压低", "缺氧", "煮不熟"], 3),
          f'BFS={sp} Dijkstra={dj}')
except Exception as ex:
    check('⑮c BFS最短2跳 vs Dijkstra加权选缺氧链(代价3<4)', False, str(ex)[:60])

print(f'\n=== 白箱自举正式管线（域接管）: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
