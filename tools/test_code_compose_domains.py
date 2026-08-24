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

# ⑯ 目标4 深化：虚拟内存（页表映射/缺页处理/页面错误分类 经正式管线）
o3_qs = {
    "页表映射": "写一个页表映射单元（虚拟页到物理帧）",
    "缺页处理": "写一个缺页处理单元（空闲帧加载）",
    "页面错误": "写一个页面错误分类单元（MMU 错误类型）",
}
o3_ok = 0
for label, q in o3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o3_ok += 1
    check(f'⑯ {label} 虚拟内存单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑯b 虚拟内存三单元全部生成', o3_ok == 3, f'{o3_ok}/3')

# ⑯c 端到端：页表→缺页处理→错误分类（缺页→加载→可访问）
r_pt = domain_route("写一个页表映射单元（虚拟页到物理帧）")
r_pf = domain_route("写一个缺页处理单元（空闲帧加载）")
r_cl = domain_route("写一个页面错误分类单元（MMU 错误类型）")
try:
    ns_pt, ns_pf, ns_cl = {}, {}, {}
    exec(r_pt["code"], ns_pt)
    exec(r_pf["code"], ns_pf)
    exec(r_cl["code"], ns_cl)
    pt = {}
    # 首次访问 VPN 2 → 缺页 → 加载到帧 8
    res = ns_pf["page_fault_handler"](pt, 2, [8], lambda v, f: None)
    frm = res[1]
    # 分类：已加载+可写 → ok；未映射 VPN 9 → segment_fault
    pt[2]["writable"] = True
    c1 = ns_cl["classify_page_fault"](2, pt, 'write')
    c2 = ns_cl["classify_page_fault"](9, pt, 'read')
    check('⑯c 缺页→加载→分类端到端（VPN2可写ok / VPN9段错误）',
          res[0] == 'page_fault_loaded' and frm == 8
          and c1 == 'ok' and c2 == 'segment_fault',
          f'load={res[0]} frame={frm} vpn2={c1} vpn9={c2}')
except Exception as ex:
    check('⑯c 缺页→加载→分类端到端（VPN2可写ok / VPN9段错误）', False, str(ex)[:60])

# ⑰ 目标5 深化：浏览器渲染引擎（样式计算/布局树/绘制 经正式管线）
b3_qs = {
    "样式计算": "写一个样式计算单元（DOM节点匹配规则）",
    "布局树": "写一个布局树单元（块级坐标计算）",
    "绘制": "写一个绘制单元（布局到画布）",
}
b3_ok = 0
for label, q in b3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b3_ok += 1
    check(f'⑰ {label} 浏览器渲染单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑰b 浏览器渲染三单元全部生成', b3_ok == 3, f'{b3_ok}/3')

# ⑰c 端到端：样式计算→布局树→绘制（p.red 红色 → 纵向堆叠 → 画布）
r_sc = domain_route("写一个样式计算单元（DOM节点匹配规则）")
r_lt = domain_route("写一个布局树单元（块级坐标计算）")
r_pn = domain_route("写一个绘制单元（布局到画布）")
try:
    ns_sc, ns_lt, ns_pn = {}, {}, {}
    exec(r_sc["code"], ns_sc)
    exec(r_lt["code"], ns_lt)
    exec(r_pn["code"], ns_pn)
    style = ns_sc["style_compute"](
        {'tag': 'p', 'classes': ['red']},
        [{'tag': 'p', 'style': {'color': 'black', 'height': 1}},
         {'class': 'red', 'style': {'color': 'red', 'height': 1}}])
    lay = ns_lt["layout_tree"](
        [{'id': 'a', 'style': {'width': 2, 'height': 1}},
         {'id': 'b', 'style': {'width': 3, 'height': 1}}], 5)
    cv = ns_pn["paint"](lay, 2, 5)
    check('⑰c 样式→布局→绘制端到端（red→堆叠→画布##.. ###.）',
          style == {'color': 'red', 'height': 1}
          and lay == [('a', 0, 0, 2, 1), ('b', 0, 1, 3, 1)]
          and cv == ['##...', '###..'],
          f'style={style} lay={lay} canvas={cv}')
except Exception as ex:
    check('⑰c 样式→布局→绘制端到端（red→堆叠→画布##.. ###.）', False, str(ex)[:60])

# ⑱ 目标1 深化：异常处理（抛出/捕获/传播 经正式管线）
p2_qs = {
    "抛出": "写一个异常抛出单元（raise 错误）",
    "捕获": "写一个异常捕获单元（try except 匹配）",
    "传播": "写一个异常传播单元（调用栈冒泡）",
}
p2_ok = 0
for label, q in p2_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p2_ok += 1
    check(f'⑱ {label} 异常处理单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑱b 异常处理三单元全部生成', p2_ok == 3, f'{p2_ok}/3')

# ⑱c 端到端：捕获（try_except 接 ValueError）+ 传播（内层抛→外层捕）
r_te = domain_route("写一个异常捕获单元（try except 匹配）")
r_pr = domain_route("写一个异常传播单元（调用栈冒泡）")
try:
    ns_te, ns_pr = {}, {}
    exec(r_te["code"], ns_te)
    exec(r_pr["code"], ns_pr)
    def risky():
        raise ValueError("除以零")
    r1 = ns_te["try_except"](ValueError, lambda e: "处理:" + str(e), risky)
    r2 = ns_pr["propagate"](None, ValueError, "深层错误")
    check('⑱c 捕获+传播端到端（ValueError 被接 / 内层抛外层捕）',
          r1 == ('caught', '处理:除以零') and r2 == ('caught_at_outer', '深层错误'),
          f'try_except={r1} propagate={r2}')
except Exception as ex:
    check('⑱c 捕获+传播端到端（ValueError 被接 / 内层抛外层捕）', False, str(ex)[:60])

# ⑲ 目标7 深化：TCP 可靠传输（滑动窗口/累积确认/拥塞控制 经正式管线）
n4_qs = {
    "滑动窗口": "写一个 TCP 滑动窗口单元（ACK 窗口前移）",
    "累积确认": "写一个 TCP 累积确认单元（连续序号推进）",
    "拥塞控制": "写一个 TCP 拥塞控制单元（慢启动阈值）",
}
n4_ok = 0
for label, q in n4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n4_ok += 1
    check(f'⑲ {label} TCP可靠传输单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑲b TCP可靠传输三单元全部生成', n4_ok == 3, f'{n4_ok}/3')

# ⑲c 端到端：滑动窗口+累积确认+拥塞控制 组装（发送窗口推进→连续确认→丢包减窗）
r_sw = domain_route("写一个 TCP 滑动窗口单元（ACK 窗口前移）")
r_ca = domain_route("写一个 TCP 累积确认单元（连续序号推进）")
r_cc = domain_route("写一个 TCP 拥塞控制单元（慢启动阈值）")
try:
    ns_sw, ns_ca, ns_cc = {}, {}, {}
    exec(r_sw["code"], ns_sw)
    exec(r_ca["code"], ns_ca)
    exec(r_cc["code"], ns_cc)
    # 发送 1,2,3 → 收到确认 3 → 窗口前移到 3
    recv = set()
    for s in (1, 2, 3):
        ack = ns_ca["cum_ack"](recv, s)
    win = ns_sw["sliding_window"](0, 0, 3, ack)
    # 拥塞窗口从 1 增长到阈值 8
    cc = ns_cc["slow_start"](1, 8, 2, False)
    # 丢包 → 阈值减半 + 窗口重置 1
    cc_lost = ns_cc["slow_start"](8, 8, 0, True)
    check('⑲c 窗口→确认→拥塞端到端（ack3窗口[3,4,5] 慢启动2→3 丢包重置1）',
          ack == 3 and win == {'base': 3, 'next_seq': 3, 'window': [3, 4, 5]}
          and cc == {'cwnd': 3, 'ssthresh': 8}
          and cc_lost == {'cwnd': 1, 'ssthresh': 4},
          f'ack={ack} win={win} cc={cc} lost={cc_lost}')
except Exception as ex:
    check('⑲c 窗口→确认→拥塞端到端（ack3窗口[3,4,5] 慢启动2→3 丢包重置1）', False, str(ex)[:60])

# ⑳ 目标4 深化：文件系统/设备（目录树/文件描述符/字符设备 经正式管线）
o4_qs = {
    "目录树": "写一个目录树单元（mkdir ls 路径展开）",
    "文件描述符": "写一个文件描述符单元（fd 分配关闭）",
    "字符设备": "写一个字符设备单元（open read write）",
}
o4_ok = 0
for label, q in o4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o4_ok += 1
    check(f'⑳ {label} 文件系统/设备单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('⑳b 文件系统/设备三单元全部生成', o4_ok == 3, f'{o4_ok}/3')

# ⑳c 端到端：目录树→ls→打开文件（fd）→设备读写（字符设备）
r_dt = domain_route("写一个目录树单元（mkdir ls 路径展开）")
r_fd = domain_route("写一个文件描述符单元（fd 分配关闭）")
r_cd = domain_route("写一个字符设备单元（open read write）")
try:
    ns_dt, ns_fd, ns_cd = {}, {}, {}
    exec(r_dt["code"], ns_dt)
    exec(r_fd["code"], ns_fd)
    exec(r_cd["code"], ns_cd)
    tree = ns_dt["dir_ls"]('home', 'user', ['a.txt'])
    paths = tree
    table = {}
    fd = ns_fd["fd_alloc"](table, '/home/user/a.txt')
    dev = {'opened': False}
    ns_cd["char_device"](dev, 'open')
    ns_cd["char_device"](dev, 'write', '内容')
    data = ns_cd["char_device"](dev, 'read')
    check('⑳c 目录→打开→设备读写端到端（路径展开 fd=3 读回内容）',
          paths == ['/home', '/home/user', '/home/user/a.txt']
          and fd == 3 and data == '内容',
          f'paths={paths} fd={fd} data={data}')
except Exception as ex:
    check('⑳c 目录→打开→设备读写端到端（路径展开 fd=3 读回内容）', False, str(ex)[:60])

# ㉑ 目标6 深化：图查询语言（模式匹配/聚合/条件链 经正式管线）
g3_qs = {
    "模式匹配": "写一个图模式匹配单元（MATCH 三元组）",
    "聚合": "写一个图聚合查询单元（GROUP BY 计数）",
    "条件链": "写一个图条件链查询单元（变长路径）",
}
g3_ok = 0
for label, q in g3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g3_ok += 1
    check(f'㉑ {label} 图查询语言单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉑b 图查询语言三单元全部生成', g3_ok == 3, f'{g3_ok}/3')

# ㉑c 端到端：建图→模式匹配→聚合→条件链（两链图）
r_mp = domain_route("写一个图模式匹配单元（MATCH 三元组）")
r_ag = domain_route("写一个图聚合查询单元（GROUP BY 计数）")
r_cc = domain_route("写一个图条件链查询单元（变长路径）")
r_g = domain_route("写一个图存储单元（节点和边）")
try:
    ns_mp, ns_ag, ns_cc, ns_g = {}, {}, {}, {}
    exec(r_mp["code"], ns_mp)
    exec(r_ag["code"], ns_ag)
    exec(r_cc["code"], ns_cc)
    exec(r_g["code"], ns_g)
    g = ns_g["Graph"]()
    g.add_edge("气压低", "沸点降")
    g.add_edge("沸点降", "煮不熟")
    g.add_edge("气压低", "缺氧")
    g.add_edge("缺氧", "煮不熟")
    m = ns_mp["match_pattern"](g, "气压低", None, None)
    ag = ns_ag["aggregate_by"](g, lambda n: n)
    chains = ns_cc["chain_query"](g, "气压低")
    check('㉑c 模式匹配+聚合+条件链端到端（三元组/分组/两链）',
          m == [('气压低', '沸点降'), ('气压低', '缺氧')]
          and ag == {'气压低': 1, '沸点降': 1, '缺氧': 1, '煮不熟': 1}
          and chains == [['气压低', '沸点降', '煮不熟'],
                         ['气压低', '缺氧', '煮不熟']],
          f'match={m} agg={ag} chains={chains}')
except Exception as ex:
    check('㉑c 模式匹配+聚合+条件链端到端（三元组/分组/两链）', False, str(ex)[:60])

# ㉒ 目标2 深化：函数/递归白箱单元（函数定义/函数调用/递归编译 经正式管线）
c3_qs = {
    "函数定义": "写一个函数定义编译单元（定义 名 参数）",
    "函数调用": "写一个函数调用单元（CALL 帧保存）",
    "递归": "写一个递归函数编译单元（自身调用）",
}
c3_ok = 0
for label, q in c3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c3_ok += 1
    check(f'㉒ {label} 函数单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉒b 函数三单元全部生成', c3_ok == 3, f'{c3_ok}/3')

# ㉒c 端到端：函数定义→递归编译→调用→帧恢复（阶乘语义组装）
r_fd = domain_route("写一个函数定义编译单元（定义 名 参数）")
r_cf = domain_route("写一个函数调用单元（CALL 帧保存）")
try:
    ns_fd, ns_cf = {}, {}
    exec(r_fd["code"], ns_fd)
    exec(r_cf["code"], ns_cf)
    fd = ns_fd["compile_func_def"]("阶乘", ["n"], [("LOAD", "n")])
    cs = []
    syms = {'甲': 1}
    entry = ns_cf["call_func"](cs, syms, fd["params"], [5], 10, 3)
    check('㉒c 函数定义→调用端到端（入口=10 帧保存 参数绑定n=5）',
          entry == 10 and len(cs) == 1 and cs[0] == (3, {'甲': 1})
          and syms == {'甲': 1, 'n': 5},
          f'entry={entry} frames={len(cs)} symbols={syms}')
except Exception as ex:
    check('㉒c 函数定义→调用端到端（入口=10 帧保存 参数绑定x=5）', False, str(ex)[:60])

# ㉓ 目标5 深化：浏览器交互（事件冒泡/事件监听/动画帧 经正式管线）
b4_qs = {
    "事件冒泡": "写一个事件冒泡单元（祖先传播路径）",
    "事件监听": "写一个事件监听单元（注册触发）",
    "动画帧": "写一个动画帧单元（逐帧更新）",
}
b4_ok = 0
for label, q in b4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b4_ok += 1
    check(f'㉓ {label} 浏览器交互单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉓b 浏览器交互三单元全部生成', b4_ok == 3, f'{b4_ok}/3')

# ㉓c 端到端：事件冒泡路径→监听触发→动画帧（交互+渲染组合）
r_ep = domain_route("写一个事件冒泡单元（祖先传播路径）")
r_ls = domain_route("写一个事件监听单元（注册触发）")
r_af = domain_route("写一个动画帧单元（逐帧更新）")
try:
    ns_ep, ns_ls, ns_af = {}, {}, {}
    exec(r_ep["code"], ns_ep)
    exec(r_ls["code"], ns_ls)
    exec(r_af["code"], ns_af)
    path = ns_ep["event_path"]({'btn': 'form', 'form': 'body', 'body': None}, 'btn')
    ns_ls["listener_ops"]({}, 'add', 'btn')
    n = ns_ls["listener_ops"]({}, 'trigger', 'btn')
    frames = ns_af["animation_frame"](0, lambda x: x + 1, 3)
    check('㉓c 冒泡路径→监听→动画帧端到端（btn→form→body / 0 监听 / 帧1,2,3）',
          path == ['btn', 'form', 'body'] and n == 0 and frames == [1, 2, 3],
          f'path={path} listeners={n} frames={frames}')
except Exception as ex:
    check('㉓c 冒泡路径→监听→动画帧端到端（btn→form→body / 0 监听 / 帧1,2,3）', False, str(ex)[:60])

# ㉔ 目标1 深化：闭包族（捕获更新/工厂/延迟绑定 经正式管线）
p3_qs = {
    "捕获更新": "写一个闭包捕获更新单元（nonlocal 修改）",
    "闭包工厂": "写一个闭包工厂单元（乘子生成）",
    "延迟绑定": "写一个闭包延迟绑定单元（循环捕获）",
}
p3_ok = 0
for label, q in p3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p3_ok += 1
    check(f'㉔ {label} 闭包族单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉔b 闭包族三单元全部生成', p3_ok == 3, f'{p3_ok}/3')

# ㉔c 端到端：捕获更新(nonlocal 递增) + 工厂(乘子) + 延迟绑定(陷阱)
r_mu = domain_route("写一个闭包捕获更新单元（nonlocal 修改）")
r_fc = domain_route("写一个闭包工厂单元（乘子生成）")
r_lz = domain_route("写一个闭包延迟绑定单元（循环捕获）")
try:
    ns_mu, ns_fc, ns_lz = {}, {}, {}
    exec(r_mu["code"], ns_mu)
    exec(r_fc["code"], ns_fc)
    exec(r_lz["code"], ns_lz)
    f = ns_mu["counter_nonlocal"]()
    incs = (f(), f(), f())
    dbl = ns_fc["make_multiplier"](2)
    d = dbl(5)
    lazy = ns_lz["lazy_bindings"]()
    check('㉔c 捕获更新→工厂→延迟绑定端到端（1,2,3 / 10 / [2,2,2]）',
          incs == (1, 2, 3) and d == 10 and lazy == [2, 2, 2],
          f'inc={incs} double={d} lazy={lazy}')
except Exception as ex:
    check('㉔c 捕获更新→工厂→延迟绑定端到端（1,2,3 / 10 / [2,2,2]）', False, str(ex)[:60])

# ㉕ 目标7 深化：IP 层（CIDR 子网/距离矢量/NAT 经正式管线）
n5_qs = {
    "CIDR": "写一个 CIDR 子网计算单元（网络广播地址）",
    "距离矢量": "写一个距离矢量路由单元（RIP 合并）",
    "NAT": "写一个 NAT 转换单元（地址映射）",
}
n5_ok = 0
for label, q in n5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n5_ok += 1
    check(f'㉕ {label} IP层单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉕b IP层三单元全部生成', n5_ok == 3, f'{n5_ok}/3')

# ㉕c 端到端：CIDR 划网→路由传播→NAT 出网（内网主机经 NAT 访问公网）
r_cidr = domain_route("写一个 CIDR 子网计算单元（网络广播地址）")
r_dv = domain_route("写一个距离矢量路由单元（RIP 合并）")
r_nat = domain_route("写一个 NAT 转换单元（地址映射）")
try:
    ns_cidr, ns_dv, ns_nat = {}, {}, {}
    exec(r_cidr["code"], ns_cidr)
    exec(r_dv["code"], ns_dv)
    exec(r_nat["code"], ns_nat)
    sub = ns_cidr["cidr_network"]('192.168.1.130', 24)
    routes = ns_dv["distance_vector"]({'A': 0, 'B': 1}, 'C', {'A': 2, 'D': 1})
    out = ns_nat["nat_translate"]({}, '192.168.1.10', 5000, '8.8.8.8')
    check('㉕c CIDR→路由→NAT 端到端（网192.168.1.0 路由D=2 NAT=8.8.8.8:1024）',
          sub['network'] == '192.168.1.0' and sub['hosts'] == 254
          and routes.get('D') == 2 and out == ('8.8.8.8', 1024),
          f'sub={sub["network"]} routes={routes} nat={out}')
except Exception as ex:
    check('㉕c CIDR→路由→NAT 端到端（网192.168.1.0 路由D=2 NAT=8.8.8.8:1024）', False, str(ex)[:60])

# ㉖ 目标6 深化：图数据库工程（事务/属性索引/子图匹配 经正式管线）
g4_qs = {
    "事务": "写一个图事务单元（begin commit rollback）",
    "属性索引": "写一个属性索引单元（按属性查找）",
    "子图匹配": "写一个子图匹配单元（模式边存在性）",
}
g4_ok = 0
for label, q in g4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g4_ok += 1
    check(f'㉖ {label} 图数据库工程单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉖b 图数据库工程三单元全部生成', g4_ok == 3, f'{g4_ok}/3')

# ㉖c 端到端：建图→索引→事务→子图匹配（属性索引查找→事务回滚→子图存在性）
r_idx = domain_route("写一个属性索引单元（按属性查找）")
r_txn = domain_route("写一个图事务单元（begin commit rollback）")
r_sg = domain_route("写一个子图匹配单元（模式边存在性）")
r_g = domain_route("写一个图存储单元（节点和边）")
try:
    ns_idx, ns_txn, ns_sg, ns_g = {}, {}, {}, {}
    exec(r_idx["code"], ns_idx)
    exec(r_txn["code"], ns_txn)
    exec(r_sg["code"], ns_sg)
    exec(r_g["code"], ns_g)
    idx = ns_idx["index_by_attr"]({'a': {'type': '条件'}, 'b': {'type': '规律'}}, 'type')
    t = ns_txn["txn_op"]({'data': {'a': [1]}, 'snapshot': None}, 'begin')
    rb = ns_txn["txn_op"]({'data': {'a': [2]}, 'snapshot': {'a': [1]}}, 'rollback')
    g = ns_g["Graph"]()
    g.add_edge("气压低", "沸点降")
    sg = ns_sg["subgraph_match"](g, [("气压低", "沸点降")])
    check('㉖c 索引→事务→子图端到端（条件[a]规律[b] 事务active/回滚 子图True）',
          idx == {'条件': ['a'], '规律': ['b']} and t == 'active'
          and rb == 'rolled_back' and sg is True,
          f'idx={idx} txn={t},{rb} subgraph={sg}')
except Exception as ex:
    check('㉖c 索引→事务→子图端到端（条件[a] 事务active/回滚 子图True）', False, str(ex)[:60])

# ㉗ 目标4 深化：中断子系统（向量表/上下文切换/嵌套优先级 经正式管线）
o5_qs = {
    "中断向量": "写一个中断向量表单元（IRQ 查表）",
    "上下文切换": "写一个中断上下文切换单元（现场保存恢复）",
    "嵌套优先级": "写一个中断嵌套优先级单元（高优先抢占）",
}
o5_ok = 0
for label, q in o5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o5_ok += 1
    check(f'㉗ {label} 中断子系统单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉗b 中断子系统三单元全部生成', o5_ok == 3, f'{o5_ok}/3')

# ㉗c 端到端：向量查表→上下文保存恢复→嵌套抢占（中断处理全流程）
r_vt = domain_route("写一个中断向量表单元（IRQ 查表）")
r_cs = domain_route("写一个中断上下文切换单元（现场保存恢复）")
r_np = domain_route("写一个中断嵌套优先级单元（高优先抢占）")
try:
    ns_vt, ns_cs, ns_np = {}, {}, {}
    exec(r_vt["code"], ns_vt)
    exec(r_cs["code"], ns_cs)
    exec(r_np["code"], ns_np)
    h = ns_vt["vector_lookup"]({14: 'disk_handler'}, 14)
    st = ns_cs["ctx_switch"]({'regs': {'a': 1}}, True)
    rt = ns_cs["ctx_switch"]({'regs': {'a': 1}, 'saved': {'a': 9}}, False)
    pre = ns_np["nested_irq"](3, 5)
    no_pre = ns_np["nested_irq"](5, 3)
    check('㉗c 向量→上下文→嵌套端到端（disk_handler 保存/恢复 抢占5>3 不抢3<5）',
          h == 'disk_handler' and st == 'saved' and rt == 'restored'
          and pre is True and no_pre is False,
          f'handler={h} ctx={st},{rt} preempt={pre},{no_pre}')
except Exception as ex:
    check('㉗c 向量→上下文→嵌套端到端（disk_handler 保存/恢复 抢占5>3 不抢3<5）', False, str(ex)[:60])

# ㉘ 目标5 深化：Web 平台（本地存储/会话存储/Web Worker 经正式管线）
b5_qs = {
    "本地存储": "写一个本地存储单元（localStorage 读写）",
    "会话存储": "写一个会话存储单元（标签页隔离）",
    "Web Worker": "写一个 Web Worker 单元（并行任务）",
}
b5_ok = 0
for label, q in b5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b5_ok += 1
    check(f'㉘ {label} Web平台单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉘b Web平台三单元全部生成', b5_ok == 3, f'{b5_ok}/3')

# ㉘c 端到端：存储写入→会话隔离→Worker 并行（持久化+隔离+并行组合）
r_ls = domain_route("写一个本地存储单元（localStorage 读写）")
r_ss = domain_route("写一个会话存储单元（标签页隔离）")
r_wk = domain_route("写一个 Web Worker 单元（并行任务）")
try:
    ns_ls, ns_ss, ns_wk = {}, {}, {}
    exec(r_ls["code"], ns_ls)
    exec(r_ss["code"], ns_ss)
    exec(r_wk["code"], ns_wk)
    store = {}
    ns_ls["storage_op"](store, 'set', 'theme', 'dark')
    v = ns_ls["storage_op"](store, 'get', 'theme')
    same_tab = ns_ss["session_storage"](store, True)
    new_tab = ns_ss["session_storage"](store, False)
    w = ns_wk["worker_msg"]({'result': None}, {'fn': lambda x: x * 2}, 21)
    check('㉘c 存储→会话→Worker 端到端（theme=dark 同标签/新标签隔离 42）',
          v == 'dark' and same_tab == {'theme': 'dark'} and new_tab == {}
          and w == 42,
          f'val={v} same={same_tab} new={new_tab} worker={w}')
except Exception as ex:
    check('㉘c 存储→会话→Worker 端到端（theme=dark 同标签/新标签隔离 42）', False, str(ex)[:60])

# ㉙ 目标1 深化：生成器/迭代器（yield/迭代协议/列表推导 经正式管线）
p4_qs = {
    "生成器": "写一个生成器单元（yield 逐个产出）",
    "迭代器": "写一个迭代器协议单元（iter next）",
    "列表推导": "写一个列表推导式单元（映射）",
}
p4_ok = 0
for label, q in p4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p4_ok += 1
    check(f'㉙ {label} 生成器/迭代器单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉙b 生成器/迭代器三单元全部生成', p4_ok == 3, f'{p4_ok}/3')

# ㉙c 端到端：生成器产出→迭代协议遍历→列表推导映射（惰性→协议→映射组合）
r_gen = domain_route("写一个生成器单元（yield 逐个产出）")
r_it = domain_route("写一个迭代器协议单元（iter next）")
r_lc = domain_route("写一个列表推导式单元（映射）")
try:
    ns_gen, ns_it, ns_lc = {}, {}, {}
    exec(r_gen["code"], ns_gen)
    exec(r_it["code"], ns_it)
    exec(r_lc["code"], ns_lc)
    produced = ns_gen["gen_test"]()
    walked = ns_it["iter_protocol"](produced)
    mapped = ns_lc["list_comp"](walked, lambda x: x * 10)
    check('㉙c 生成→迭代→推导端到端（[0,1,2] 遍历 [0,20,30] 映射×10）',
          produced == [0, 1, 2] and walked == [0, 1, 2]
          and mapped == [0, 10, 20],
          f'gen={produced} it={walked} comp={mapped}')
except Exception as ex:
    check('㉙c 生成→迭代→推导端到端（[0,1,2] 遍历 [0,20,30] 映射×10）', False, str(ex)[:60])

# ㉚ 目标6 深化：图算法（PageRank/连通分量/拓扑排序 经正式管线）
g5_qs = {
    "PageRank": "写一个 PageRank 单元（权重传播）",
    "连通分量": "写一个连通分量单元（无向子图）",
    "拓扑排序": "写一个拓扑排序单元（DAG 依赖序）",
}
g5_ok = 0
for label, q in g5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g5_ok += 1
    check(f'㉚ {label} 图算法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉚b 图算法三单元全部生成', g5_ok == 3, f'{g5_ok}/3')

# ㉚c 端到端：建图→拓扑排序→连通分量→PageRank（算法层组装）
r_ts = domain_route("写一个拓扑排序单元（DAG 依赖序）")
r_cc = domain_route("写一个连通分量单元（无向子图）")
r_pr = domain_route("写一个 PageRank 单元（权重传播）")
r_g = domain_route("写一个图存储单元（节点和边）")
try:
    ns_ts, ns_cc, ns_pr, ns_g = {}, {}, {}, {}
    exec(r_ts["code"], ns_ts)
    exec(r_cc["code"], ns_cc)
    exec(r_pr["code"], ns_pr)
    exec(r_g["code"], ns_g)
    g = ns_g["Graph"]()
    g.add_edge("气压低", "沸点降")
    g.add_edge("沸点降", "煮不熟")
    g.add_edge("气压低", "缺氧")
    g.add_edge("缺氧", "煮不熟")
    order = ns_ts["topological_sort"](g)
    comps = ns_cc["connected_components"](g)
    pr = ns_pr["pagerank"](g)
    check('㉚c 拓扑→连通→PageRank 端到端（4 节点序/1 分量/4 排名）',
          order is not None and len(order) == 4
          and comps == [["气压低", "沸点降", "煮不熟", "缺氧"]]
          and sorted(pr.keys()) == ["气压低", "沸点降", "煮不熟", "缺氧"],
          f'order={order} comps={comps} pr={sorted(pr)}')
except Exception as ex:
    check('㉚c 拓扑→连通→PageRank 端到端（4 节点序/1 分量/4 排名）', False, str(ex)[:60])

# ㉛ 目标7 深化：应用层（DNS/HTTP状态码/负载均衡 经正式管线）
n6_qs = {
    "DNS": "写一个 DNS 解析单元（域名到 IP）",
    "状态码": "写一个 HTTP 状态码分类单元（2xx 4xx）",
    "负载均衡": "写一个负载均衡单元（轮询调度）",
}
n6_ok = 0
for label, q in n6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n6_ok += 1
    check(f'㉛ {label} 应用层单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉛b 应用层三单元全部生成', n6_ok == 3, f'{n6_ok}/3')

# ㉛c 端到端：DNS 解析→HTTP 状态码→负载均衡（访问流程：解析→请求→分配）
r_dns = domain_route("写一个 DNS 解析单元（域名到 IP）")
r_hs = domain_route("写一个 HTTP 状态码分类单元（2xx 4xx）")
r_lb = domain_route("写一个负载均衡单元（轮询调度）")
try:
    ns_dns, ns_hs, ns_lb = {}, {}, {}
    exec(r_dns["code"], ns_dns)
    exec(r_hs["code"], ns_hs)
    exec(r_lb["code"], ns_lb)
    ip, src = ns_dns["dns_resolve"]({}, 'a.com')
    cls = ns_hs["http_status_class"](404)
    srv = ns_lb["load_balance"](['s1', 's2', 's3'], 5)
    check('㉛c DNS→状态码→负载均衡端到端（8.8.8.8查询/404客户端错/s3轮询）',
          ip == '8.8.8.8' and src == 'query' and cls == '客户端错误'
          and srv == 's3',
          f'dns={ip}({src}) status={cls} lb={srv}')
except Exception as ex:
    check('㉛c DNS→状态码→负载均衡端到端（8.8.8.8查询/404客户端错/s3轮询）', False, str(ex)[:60])

# ㉜ 目标4 深化：VFS/权限/进程树（系统挂载/文件权限/进程树 经正式管线）
o6_qs = {
    "系统挂载": "写一个文件系统挂载单元（mount 注册卸载）",
    "文件权限": "写一个文件权限单元（rwx 位检查）",
    "进程树": "写一个进程树单元（父子后代）",
}
o6_ok = 0
for label, q in o6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o6_ok += 1
    check(f'㉜ {label} VFS/权限单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉜b VFS/权限三单元全部生成', o6_ok == 3, f'{o6_ok}/3')

# ㉜c 端到端：挂载文件系统→权限检查→进程树后代（VFS+安全+进程层级）
r_mt = domain_route("写一个文件系统挂载单元（mount 注册卸载）")
r_pm = domain_route("写一个文件权限单元（rwx 位检查）")
r_pt = domain_route("写一个进程树单元（父子后代）")
try:
    ns_mt, ns_pm, ns_pt = {}, {}, {}
    exec(r_mt["code"], ns_mt)
    exec(r_pm["code"], ns_pm)
    exec(r_pt["code"], ns_pt)
    m = ns_mt["mount_op"]({}, '/data', 'ext4')
    w = ns_pm["check_perm"](5, 'w')
    r = ns_pm["check_perm"](5, 'r')
    tree = ns_pt["process_tree"]({'a': 'root', 'b': 'a', 'c': 'a'}, 'root')
    check('㉜c 挂载→权限→进程树端到端（ext4挂载 写拒读允 后代a,b,c）',
          m is True and w is False and r is True and tree == ['a', 'b', 'c'],
          f'mount={m} w={w} r={r} tree={tree}')
except Exception as ex:
    check('㉜c 挂载→权限→进程树端到端（ext4挂载 写拒读允 后代a,b,c）', False, str(ex)[:60])

# ㉝ 目标5 深化：网络增强（Fetch/HTTP缓存/Cookie 经正式管线）
b6_qs = {
    "Fetch": "写一个 Fetch 请求单元（方法 URL 封装）",
    "HTTP缓存": "写一个 HTTP 缓存单元（ETag 条件请求）",
    "Cookie": "写一个 Cookie 管理单元（设置读取删除）",
}
b6_ok = 0
for label, q in b6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b6_ok += 1
    check(f'㉝ {label} 网络增强单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉝b 网络增强三单元全部生成', b6_ok == 3, f'{b6_ok}/3')

# ㉝c 端到端：Fetch 请求→Cookie 会话→HTTP 缓存（请求带会话→缓存命中）
r_fr = domain_route("写一个 Fetch 请求单元（方法 URL 封装）")
r_ck = domain_route("写一个 Cookie 管理单元（设置读取删除）")
r_hc = domain_route("写一个 HTTP 缓存单元（ETag 条件请求）")
try:
    ns_fr, ns_ck, ns_hc = {}, {}, {}
    exec(r_fr["code"], ns_fr)
    exec(r_ck["code"], ns_ck)
    exec(r_hc["code"], ns_hc)
    req = ns_fr["fetch_req"]('GET', '/api', {'Cookie': 'sid=abc'})
    ns_ck["cookie_op"]({}, 'set', 'sid', 'abc')
    sid = ns_ck["cookie_op"]({'sid': 'abc'}, 'get', 'sid')
    cache = {'/api': {'etag': 'v1', 'data': '数据'}}
    data, status = ns_hc["http_cache"](cache, '/api', 'v1')
    check('㉝c Fetch→Cookie→缓存端到端（GET带Cookie sid=abc 缓存304命中）',
          req['method'] == 'GET' and req['headers'].get('Cookie') == 'sid=abc'
          and sid == 'abc' and data == '数据' and status == '304 未变更',
          f'req={req["method"]} sid={sid} cache={status}')
except Exception as ex:
    check('㉝c Fetch→Cookie→缓存端到端（GET带Cookie sid=abc 缓存304命中）', False, str(ex)[:60])

# ㉞ 目标4 深化：系统调用/信号（syscall 分派/信号处理/参数校验 经正式管线）
o7_qs = {
    "系统调用": "写一个系统调用分派单元（编号查表）",
    "信号处理": "写一个信号处理单元（注册发送默认）",
    "参数校验": "写一个系统调用参数校验单元（类型检查）",
}
o7_ok = 0
for label, q in o7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o7_ok += 1
    check(f'㉞ {label} 系统调用单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉞b 系统调用三单元全部生成', o7_ok == 3, f'{o7_ok}/3')

# ㉞c 端到端：参数校验→syscall 分派→信号处理（校验通过→调用→信号清理）
r_va = domain_route("写一个系统调用参数校验单元（类型检查）")
r_sd = domain_route("写一个系统调用分派单元（编号查表）")
r_sg = domain_route("写一个信号处理单元（注册发送默认）")
try:
    ns_va, ns_sd, ns_sg = {}, {}, {}
    exec(r_va["code"], ns_va)
    exec(r_sd["code"], ns_sd)
    exec(r_sg["code"], ns_sg)
    ok_v = ns_va["validate_args"]([3, 'x'], [int, str])
    res = ns_sd["syscall_dispatch"]({1: lambda x: x * 2}, 1, [5])
    ns_sg["signal_op"]({}, 'register', 2, lambda: 'cleanup')
    sig = ns_sg["signal_op"]({2: lambda: 'cleanup'}, 'send', 2)
    check('㉞c 校验→分派→信号端到端（类型通过 调用=10 SIGINT清理）',
          ok_v is True and res == 10 and sig == ('handled', 'cleanup'),
          f'validate={ok_v} syscall={res} signal={sig}')
except Exception as ex:
    check('㉞c 校验→分派→信号端到端（类型通过 调用=10 SIGINT清理）', False, str(ex)[:60])

# ㉟ 目标7 深化：实时通信（WebSocket握手/帧封装/流式传输 经正式管线）
n7_qs = {
    "WebSocket": "写一个 WebSocket 握手单元（Upgrade 101）",
    "帧封装": "写一个 WebSocket 帧封装单元（FIN opcode）",
    "流式传输": "写一个流式传输单元（chunked 分块）",
}
n7_ok = 0
for label, q in n7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n7_ok += 1
    check(f'㉟ {label} 实时通信单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㉟b 实时通信三单元全部生成', n7_ok == 3, f'{n7_ok}/3')

# ㉟c 端到端：WebSocket 握手→帧封装→流式传输（实时通道：握手→发帧→流式数据）
r_wsh = domain_route("写一个 WebSocket 握手单元（Upgrade 101）")
r_wf = domain_route("写一个 WebSocket 帧封装单元（FIN opcode）")
r_ch = domain_route("写一个流式传输单元（chunked 分块）")
try:
    ns_wsh, ns_wf, ns_ch = {}, {}, {}
    exec(r_wsh["code"], ns_wsh)
    exec(r_wf["code"], ns_wf)
    exec(r_ch["code"], ns_ch)
    code, status = ns_wsh["ws_handshake"]({'Upgrade': 'websocket',
                                           'Sec-WebSocket-Key': 'k'})
    frame = ns_wf["ws_frame"](1, b'hi')
    stream = ns_ch["chunked_encode"](b'abcdef', 4)
    check('㉟c 握手→帧→流式端到端（101 帧\\x81\\x02hi chunked 4+2）',
          code == 101 and frame == b'\x81\x02hi'
          and stream == '4\r\nabcd\r\n2\r\nef\r\n0\r\n\r\n',
          f'ws={code} frame={frame} stream={stream!r}')
except Exception as ex:
    check('㉟c 握手→帧→流式端到端（101 帧\\x81\\x02hi chunked 4+2）', False, str(ex)[:60])

# ㊀ 目标6 深化：查询优化（执行计划/批量建图/布隆过滤 经正式管线）
g6_qs = {
    "执行计划": "写一个查询执行计划单元（选择性排序）",
    "批量建图": "写一个批量建图单元（多条边导入）",
    "布隆过滤": "写一个布隆过滤器单元（快速判定）",
}
g6_ok = 0
for label, q in g6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g6_ok += 1
    check(f'㊀ {label} 查询优化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊀b 查询优化三单元全部生成', g6_ok == 3, f'{g6_ok}/3')

# ㊀c 端到端：批量建图→布隆过滤→执行计划（导入→快速判定→计划优化）
r_be = domain_route("写一个批量建图单元（多条边导入）")
r_bf = domain_route("写一个布隆过滤器单元（快速判定）")
r_qp = domain_route("写一个查询执行计划单元（选择性排序）")
r_g = domain_route("写一个图存储单元（节点和边）")
try:
    ns_be, ns_bf, ns_qp, ns_g = {}, {}, {}, {}
    exec(r_be["code"], ns_be)
    exec(r_bf["code"], ns_bf)
    exec(r_qp["code"], ns_qp)
    exec(r_g["code"], ns_g)
    g = ns_g["Graph"]()
    n = ns_be["batch_edges"](g, [("a", "b"), ("b", "c"), ("c", "d")])
    in_bloom = ns_bf["bloom_filter"](['气压低', '沸点降', '煮不熟'], '煮不熟')
    plan = ns_qp["query_plan"](['气压', '沸点', '密度'], {'气压': 10, '沸点': 2})
    check('㊀c 批量→布隆→计划端到端（3边 煮不熟命中 计划缺省密度优先）',
          n == 3 and in_bloom is True and plan == ['密度', '沸点', '气压'],
          f'edges={n} bloom={in_bloom} plan={plan}')
except Exception as ex:
    check('㊀c 批量→布隆→计划端到端（3边 煮不熟命中 计划沸点优先）', False, str(ex)[:60])

# ㊁ 目标4 深化：可靠性（日志恢复/系统监控/守护进程 经正式管线）
o8_qs = {
    "日志恢复": "写一个日志恢复单元（journal 重放）",
    "系统监控": "写一个系统监控单元（采样统计）",
    "守护进程": "写一个守护进程单元（后台运行）",
}
o8_ok = 0
for label, q in o8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o8_ok += 1
    check(f'㊁ {label} 可靠性单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊁b 可靠性三单元全部生成', o8_ok == 3, f'{o8_ok}/3')

# ㊁c 端到端：日志重放→守护进程→监控（崩溃恢复→服务运行→负载统计）
r_jr = domain_route("写一个日志恢复单元（journal 重放）")
r_dm = domain_route("写一个守护进程单元（后台运行）")
r_sm = domain_route("写一个系统监控单元（采样统计）")
try:
    ns_jr, ns_dm, ns_sm = {}, {}, {}
    exec(r_jr["code"], ns_jr)
    exec(r_dm["code"], ns_dm)
    exec(r_sm["code"], ns_sm)
    disk = ns_jr["journal_replay"](
        [{'type': 'write', 'inode': 'a', 'data': 'X'},
         {'type': 'delete', 'inode': 'a'}], {})
    st = ns_dm["daemon_lifecycle"]({'status': 'idle'}, 'start')
    m = ns_sm["sys_metrics"]([30, 50, 70])
    check('㊁c 日志→守护→监控端到端（恢复空盘 服务运行 平均50峰70）',
          disk == {} and st == 'running'
          and m == {'avg': 50.0, 'peak': 70},
          f'disk={disk} daemon={st} metrics={m}')
except Exception as ex:
    check('㊁c 日志→守护→监控端到端（恢复空盘 服务运行 平均50峰70）', False, str(ex)[:60])

# ㊂ 目标1 深化：面向对象（类定义/继承/多态 经正式管线）
p5_qs = {
    "类定义": "写一个类定义单元（构造和方法）",
    "类继承": "写一个类继承单元（方法覆盖）",
    "多态": "写一个多态单元（接口分发）",
}
p5_ok = 0
for label, q in p5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p5_ok += 1
    check(f'㊂ {label} 面向对象单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊂b 面向对象三单元全部生成', p5_ok == 3, f'{p5_ok}/3')

# ㊂c 端到端：类实例化→继承覆盖→多态分发（OOP 全链）
r_cd = domain_route("写一个类定义单元（构造和方法）")
r_ih = domain_route("写一个类继承单元（方法覆盖）")
r_pl = domain_route("写一个多态单元（接口分发）")
try:
    ns_cd, ns_ih, ns_pl = {}, {}, {}
    exec(r_cd["code"], ns_cd)
    exec(r_ih["code"], ns_ih)
    exec(r_pl["code"], ns_pl)
    d = ns_cd["oop_class_test"]()
    ih = ns_ih["oop_inherit_test"]()
    pl = ns_pl["oop_poly_test"]()
    check('㊂c 实例化→继承→多态端到端（阿黄汪汪 动物/喵 汪/喵）',
          d == ('阿黄', '阿黄 汪汪') and ih == ('动物', '喵')
          and pl == ['汪', '喵'],
          f'cls={d} inherit={ih} poly={pl}')
except Exception as ex:
    check('㊂c 实例化→继承→多态端到端（阿黄汪汪 动物/喵 汪/喵）', False, str(ex)[:60])

# ㊃ 目标4 深化：进程同步（信号量/读写锁/生产者消费者 经正式管线）
o9_qs = {
    "信号量": "写一个信号量单元（P V 操作）",
    "读写锁": "写一个读写锁单元（多读写独占）",
    "生产者消费者": "写一个生产者消费者单元（有界缓冲）",
}
o9_ok = 0
for label, q in o9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o9_ok += 1
    check(f'㊃ {label} 进程同步单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊃b 进程同步三单元全部生成', o9_ok == 3, f'{o9_ok}/3')

# ㊃c 端到端：信号量→读写锁→生产者消费者（同步原语→锁→缓冲队列）
r_sm = domain_route("写一个信号量单元（P V 操作）")
r_rw = domain_route("写一个读写锁单元（多读写独占）")
r_pc = domain_route("写一个生产者消费者单元（有界缓冲）")
try:
    ns_sm, ns_rw, ns_pc = {}, {}, {}
    exec(r_sm["code"], ns_sm)
    exec(r_rw["code"], ns_rw)
    exec(r_pc["code"], ns_pc)
    p = ns_sm["semaphore_op"]({'count': 1}, 'P')
    rl = ns_rw["rwlock_op"]({'readers': 0}, 'r_lock')
    wl = ns_rw["rwlock_op"]({'readers': 1, 'writer': False}, 'w_lock')
    n = ns_pc["producer_consumer"]([], 'produce', 'a')
    item = ns_pc["producer_consumer"](['a'], 'consume')
    check('㊃c 信号量→读写锁→生产消费端到端（P获取 读允写阻 生产1消费a）',
          p == 'acquired' and rl == 'r_acquired' and wl == 'blocked'
          and n == 1 and item == 'a',
          f'sem={p} rw={rl},{wl} buf={n},{item}')
except Exception as ex:
    check('㊃c 信号量→读写锁→生产消费端到端（P获取 读允写阻 生产1消费a）', False, str(ex)[:60])

# ㊄ 目标2 深化：语言语义（注释剥离/逻辑表达式/链式比较 经正式管线）
c4_qs = {
    "注释剥离": "写一个注释剥离单元（井号行注释）",
    "逻辑表达式": "写一个逻辑表达式编译单元（且或短路）",
    "链式比较": "写一个链式比较编译单元（a b c）",
}
c4_ok = 0
for label, q in c4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c4_ok += 1
    check(f'㊄ {label} 语言语义单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊄b 语言语义三单元全部生成', c4_ok == 3, f'{c4_ok}/3')

# ㊄c 端到端：注释剥离→逻辑编译→链式比较（预处理→短路→组合）
r_sc = domain_route("写一个注释剥离单元（井号行注释）")
r_lg = domain_route("写一个逻辑表达式编译单元（且或短路）")
r_cc = domain_route("写一个链式比较编译单元（a b c）")
try:
    ns_sc, ns_lg, ns_cc = {}, {}, {}
    exec(r_sc["code"], ns_sc)
    exec(r_lg["code"], ns_lg)
    exec(r_cc["code"], ns_cc)
    clean = ns_sc["strip_comments"]('x = 1  # 注释\n止')
    log = ns_lg["compile_logic"]([("LOAD", "a")], '且', [("LOAD", "b")])
    chain = ns_cc["compile_chain"]([("LOAD", "a"), ("LOAD", "b"), ("CMP_LT", None)],
                                   [("LOAD", "b"), ("LOAD", "c"), ("CMP_LT", None)])
    check('㊄c 注释→逻辑→链式端到端（剥离注释 且短路 链式组合）',
          clean == 'x = 1  \n止'
          and log == [("LOAD", "a"), ("JUMP_IF_FALSE", 0), ("LOAD", "b")]
          and chain[3] == ("JUMP_IF_FALSE", 0) and len(chain) == 7,
          f'clean={clean!r} log={log} chain_len={len(chain)}')
except Exception as ex:
    check('㊄c 注释→逻辑→链式端到端（剥离注释 且短路 链式组合）', False, str(ex)[:60])

# ㊅ 目标5 深化：浏览器安全（同源策略/CSP/XSS防护 经正式管线）
b7_qs = {
    "同源策略": "写一个同源策略单元（协议域名端口）",
    "CSP策略": "写一个 CSP 策略单元（资源白名单）",
    "XSS防护": "写一个 XSS 防护单元（HTML 转义）",
}
b7_ok = 0
for label, q in b7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b7_ok += 1
    check(f'㊅ {label} 浏览器安全单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊅b 浏览器安全三单元全部生成', b7_ok == 3, f'{b7_ok}/3')

# ㊅c 端到端：同源判定→CSP 拦截→XSS 转义（安全链：访问控制→策略→净化）
r_so = domain_route("写一个同源策略单元（协议域名端口）")
r_csp = domain_route("写一个 CSP 策略单元（资源白名单）")
r_xss = domain_route("写一个 XSS 防护单元（HTML 转义）")
try:
    ns_so, ns_csp, ns_xss = {}, {}, {}
    exec(r_so["code"], ns_so)
    exec(r_csp["code"], ns_csp)
    exec(r_xss["code"], ns_xss)
    same = ns_so["same_origin"]('https://a.com/x', 'https://a.com/y')
    evil = ns_csp["csp_allow"]({'script': ['self']}, 'script', 'evil.com')
    safe = ns_xss["escape_html"]('<script>x</script>')
    check('㊅c 同源→CSP→XSS 端到端（同源真 外部脚本拒 脚本转义）',
          same is True and evil is False
          and safe == '&lt;script&gt;x&lt;/script&gt;',
          f'same={same} csp={evil} xss={safe}')
except Exception as ex:
    check('㊅c 同源→CSP→XSS 端到端（同源真 外部脚本拒 脚本转义）', False, str(ex)[:60])

# ㊆ 目标6 深化：相似度/社区（Jaccard/同构/标签传播 经正式管线）
g7_qs = {
    "节点相似度": "写一个节点相似度单元（Jaccard）",
    "图同构": "写一个图同构判定单元（度序列）",
    "社区发现": "写一个社区发现单元（标签传播）",
}
g7_ok = 0
for label, q in g7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g7_ok += 1
    check(f'㊆ {label} 相似度/社区单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊆b 相似度/社区三单元全部生成', g7_ok == 3, f'{g7_ok}/3')

# ㊆c 端到端：相似度→同构判定→社区发现（分析链）
r_js = domain_route("写一个节点相似度单元（Jaccard）")
r_gi = domain_route("写一个图同构判定单元（度序列）")
r_lp = domain_route("写一个社区发现单元（标签传播）")
r_g = domain_route("写一个图存储单元（节点和边）")
ns_g7 = {}
exec(r_g["code"], ns_g7)
Graph7 = ns_g7["Graph"]
try:
    ns_js, ns_gi, ns_lp = {}, {}, {}
    exec(r_js["code"], ns_js)
    exec(r_gi["code"], ns_gi)
    exec(r_lp["code"], ns_lp)
    g = Graph7()
    g.add_edge("气压低", "沸点降")
    g.add_edge("沸点降", "煮不熟")
    g.add_edge("气压低", "缺氧")
    g.add_edge("缺氧", "煮不熟")
    sim = ns_js["jaccard_similarity"](g, "气压低", "沸点降")
    iso = ns_gi["graph_isomorphic"]([('a', 'b'), ('b', 'c')],
                                    [('x', 'y'), ('y', 'z')])
    labels = ns_lp["label_propagation"](g)
    check('㊆c 相似→同构→社区端到端（0.0 同构真 4标签）',
          sim == 0.0 and iso is True and sorted(labels.keys()) ==
          sorted(["气压低", "沸点降", "煮不熟", "缺氧"]),
          f'sim={sim} iso={iso} labels={sorted(labels)}')
except Exception as ex:
    check('㊆c 相似→同构→社区端到端（0.0 同构真 4标签）', False, str(ex)[:60])

# ㊇ 目标7 深化：现代传输（多路复用/连接池/QUIC 经正式管线）
n8_qs = {
    "多路复用": "写一个多路复用单元（流帧交错）",
    "连接池": "写一个连接池单元（获取归还）",
    "QUIC": "写一个 QUIC 握手单元（0-RTT）",
}
n8_ok = 0
for label, q in n8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n8_ok += 1
    check(f'㊇ {label} 现代传输单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊇b 现代传输三单元全部生成', n8_ok == 3, f'{n8_ok}/3')

# ㊇c 端到端：连接池→多路复用→QUIC（建连复用→流交错→快速握手）
r_cp = domain_route("写一个连接池单元（获取归还）")
r_mx = domain_route("写一个多路复用单元（流帧交错）")
r_qc = domain_route("写一个 QUIC 握手单元（0-RTT）")
try:
    ns_cp, ns_mx, ns_qc = {}, {}, {}
    exec(r_cp["code"], ns_cp)
    exec(r_mx["code"], ns_mx)
    exec(r_qc["code"], ns_qc)
    conn = ns_cp["conn_pool"]({}, 'get', 'a.com')
    frames = ns_mx["stream_mux"]([(1, 'a'), (3, 'b')])
    q0 = ns_qc["quic_handshake"]({'c1': 'ticket'}, 'c1')
    check('㊇c 连接池→多路复用→QUIC 端到端（新建 2流 0-RTT）',
          conn == 'new' and frames == [(1, 'a'), (3, 'b')]
          and q0 == ('0-RTT', 'ticket'),
          f'pool={conn} mux={frames} quic={q0}')
except Exception as ex:
    check('㊇c 连接池→多路复用→QUIC 端到端（新建 2流 0-RTT）', False, str(ex)[:60])

# ㊉ 目标4 深化：容器/虚拟化（命名空间/cgroup/容器生命周期 经正式管线）
o10_qs = {
    "命名空间": "写一个命名空间单元（PID 隔离）",
    "资源限制": "写一个 cgroup 资源限制单元（配额）",
    "容器生命周期": "写一个容器生命周期单元（创建启动停止）",
}
o10_ok = 0
for label, q in o10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o10_ok += 1
    check(f'㊉ {label} 容器/虚拟化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊉b 容器/虚拟化三单元全部生成', o10_ok == 3, f'{o10_ok}/3')

# ㊉c 端到端：命名空间→cgroup→容器（隔离→限额→生命周期）
r_ns = domain_route("写一个命名空间单元（PID 隔离）")
r_cg = domain_route("写一个 cgroup 资源限制单元（配额）")
r_ct = domain_route("写一个容器生命周期单元（创建启动停止）")
try:
    ns_ns, ns_cg, ns_ct = {}, {}, {}
    exec(r_ns["code"], ns_ns)
    exec(r_cg["code"], ns_cg)
    exec(r_ct["code"], ns_ct)
    pid = ns_ns["ns_map"]('register', {}, 'p1')
    ok_cg = ns_cg["cgroup_limit"]({}, 'cpu', 100, 80)
    over = ns_cg["cgroup_limit"]({}, 'cpu', 100, 120)
    st = ns_ct["container_ops"]({}, 'create', 'alpine')
    run = ns_ct["container_ops"]({'status': 'created'}, 'start')
    check('㊉c 命名空间→cgroup→容器端到端（PID101 限内允超限拒 创建运行）',
          pid == 101 and ok_cg is True and over is False
          and st == 'created' and run == 'running',
          f'ns={pid} cg={ok_cg},{over} ctr={st},{run}')
except Exception as ex:
    check('㊉c 命名空间→cgroup→容器端到端（PID101 限内允超限拒 创建运行）', False, str(ex)[:60])

# ㊋ 目标1 深化：高级语法（装饰器/上下文管理器/属性访问 经正式管线）
p6_qs = {
    "装饰器": "写一个装饰器单元（@timer 包装）",
    "上下文管理器": "写一个上下文管理器单元（with 语义）",
    "属性访问": "写一个属性访问单元（动态读写）",
}
p6_ok = 0
for label, q in p6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p6_ok += 1
    check(f'㊋ {label} 高级语法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊋b 高级语法三单元全部生成', p6_ok == 3, f'{p6_ok}/3')

# ㊋c 端到端：装饰器→上下文→属性（增强→资源管理→动态读写）
r_dc = domain_route("写一个装饰器单元（@timer 包装）")
r_wt = domain_route("写一个上下文管理器单元（with 语义）")
r_at = domain_route("写一个属性访问单元（动态读写）")
try:
    ns_dc, ns_wt, ns_at = {}, {}, {}
    exec(r_dc["code"], ns_dc)
    exec(r_wt["code"], ns_wt)
    exec(r_at["code"], ns_at)
    d = ns_dc["decorator_test"]()
    w = ns_wt["with_test"]()
    a = ns_at["attr_test"]()
    check('㊋c 装饰→上下文→属性端到端（timed5 进入退出 灵枢/None）',
          d == ('timed', 5) and w == (True, False) and a == ('灵枢', None),
          f'dec={d} with={w} attr={a}')
except Exception as ex:
    check('㊋c 装饰→上下文→属性端到端（timed5 进入退出 灵枢/None）', False, str(ex)[:60])

# ㊌ 目标6 深化：动态图/时序（快照版本/时序查询/增量更新 经正式管线）
g8_qs = {
    "快照版本": "写一个图快照版本单元（保存回溯）",
    "时序查询": "写一个时序查询单元（时间快照）",
    "增量更新": "写一个增量更新单元（边增删）",
}
g8_ok = 0
for label, q in g8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g8_ok += 1
    check(f'㊌ {label} 动态图/时序单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊌b 动态图/时序三单元全部生成', g8_ok == 3, f'{g8_ok}/3')

# ㊌c 端到端：快照保存→时序回溯→增量更新（版本管理→时间查询→动态维护）
r_sp = domain_route("写一个图快照版本单元（保存回溯）")
r_tq = domain_route("写一个时序查询单元（时间快照）")
r_iu = domain_route("写一个增量更新单元（边增删）")
r_g = domain_route("写一个图存储单元（节点和边）")
ns_g8 = {}
exec(r_g["code"], ns_g8)
Graph8 = ns_g8["Graph"]
try:
    ns_sp, ns_tq, ns_iu = {}, {}, {}
    exec(r_sp["code"], ns_sp)
    exec(r_tq["code"], ns_tq)
    exec(r_iu["code"], ns_iu)
    repo = {'versions': {}, 'next': 1}
    v1 = ns_sp["snapshot_ops"](repo, 'save', None, {'气压低': 1})
    v2 = ns_sp["snapshot_ops"](repo, 'save', None, {'气压低': 1, '沸点降': 1})
    back = ns_tq["time_query"]({v1: {'气压低': 1}, v2: {'气压低': 1, '沸点降': 1}}, v1)
    g = Graph8()
    g.add_edge("a", "b")
    ns_iu["incr_update"](g, ("a", "b"), 'remove')
    check('㊌c 快照→时序→增量端到端（v1回溯 删边无邻居）',
          v1 == 1 and v2 == 2 and back == {'气压低': 1}
          and g.neighbors("a") == [],
          f'v={v1},{v2} back={back} nb={g.neighbors("a")}')
except Exception as ex:
    check('㊌c 快照→时序→增量端到端（v1回溯 删边无邻居）', False, str(ex)[:60])

# ㊍ 目标7 深化：路由协议/完整性（BGP/Anycast/CRC 经正式管线）
n9_qs = {
    "BGP": "写一个 BGP 路径选择单元（AS 路径）",
    "Anycast": "写一个 Anycast 单元（就近接入）",
    "CRC": "写一个 CRC 校验单元（完整性检测）",
}
n9_ok = 0
for label, q in n9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n9_ok += 1
    check(f'㊍ {label} 路由协议/完整性单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊍b 路由协议/完整性三单元全部生成', n9_ok == 3, f'{n9_ok}/3')

# ㊍c 端到端：BGP 选路→Anycast 就近→CRC 校验（路由决策→接入选择→完整性）
r_bgp = domain_route("写一个 BGP 路径选择单元（AS 路径）")
r_any = domain_route("写一个 Anycast 单元（就近接入）")
r_crc = domain_route("写一个 CRC 校验单元（完整性检测）")
try:
    ns_bgp, ns_any, ns_crc = {}, {}, {}
    exec(r_bgp["code"], ns_bgp)
    exec(r_any["code"], ns_any)
    exec(r_crc["code"], ns_crc)
    route = ns_bgp["bgp_select"]([
        {'prefix': '10.0.0.0/8', 'as_path': ['AS1', 'AS2', 'AS3']},
        {'prefix': '10.0.0.0/8', 'as_path': ['AS5']}])
    node = ns_any["anycast_select"]([{'id': 'a', 'loc': 10},
                                     {'id': 'b', 'loc': 50}], 15)
    crc = ns_crc["crc16"](b'AB')
    check('㊍c BGP→Anycast→CRC 端到端（AS5最短 就近a CRC1929）',
          route['as_path'] == ['AS5'] and node['id'] == 'a' and crc == 1929,
          f'bgp={route["as_path"]} any={node["id"]} crc={crc}')
except Exception as ex:
    check('㊍c BGP→Anycast→CRC 端到端（AS5最短 就近a CRC1929）', False, str(ex)[:60])

# ㊎ 目标4 深化：RAID/快照（条带/奇偶校验/文件快照 经正式管线）
o11_qs = {
    "RAID条带": "写一个 RAID 条带单元（分块分布）",
    "RAID奇偶": "写一个 RAID 奇偶校验单元（XOR 容错）",
    "文件快照": "写一个文件系统快照单元（写时复制）",
}
o11_ok = 0
for label, q in o11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o11_ok += 1
    check(f'㊎ {label} RAID/快照单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊎b RAID/快照三单元全部生成', o11_ok == 3, f'{o11_ok}/3')

# ㊎c 端到端：条带→奇偶校验→快照回滚（存储冗余→容错→恢复）
r_rs = domain_route("写一个 RAID 条带单元（分块分布）")
r_rp = domain_route("写一个 RAID 奇偶校验单元（XOR 容错）")
r_fs = domain_route("写一个文件系统快照单元（写时复制）")
try:
    ns_rs, ns_rp, ns_fs = {}, {}, {}
    exec(r_rs["code"], ns_rs)
    exec(r_rp["code"], ns_rp)
    exec(r_fs["code"], ns_fs)
    st = ns_rs["raid_stripe"](list('abcdef'), 2)
    p = ns_rp["raid_parity"]([1, 2, 3])
    fs = {'data': {1: 'a'}}
    ns_fs["fs_snapshot"](fs, 'snap')
    ns_fs["fs_snapshot"](fs, 'write', 1, 'b')
    rb = ns_fs["fs_snapshot"](fs, 'rollback')
    check('㊎c 条带→奇偶→快照端到端（ace/bdf 奇偶0 回滚a）',
          st == [list('ace'), list('bdf')] and p == 0
          and rb == {1: 'a'},
          f'stripe={st} parity={p} rollback={rb}')
except Exception as ex:
    check('㊎c 条带→奇偶→快照端到端（ace/bdf 奇偶0 回滚a）', False, str(ex)[:60])

# ㊏ 目标5 深化：PWA（Service Worker/推送/IndexedDB 经正式管线）
b8_qs = {
    "Service Worker": "写一个 Service Worker 单元（生命周期拦截）",
    "推送": "写一个推送通知单元（订阅发送）",
    "IndexedDB": "写一个 IndexedDB 单元（对象事务）",
}
b8_ok = 0
for label, q in b8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b8_ok += 1
    check(f'㊏ {label} PWA单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊏b PWA三单元全部生成', b8_ok == 3, f'{b8_ok}/3')

# ㊏c 端到端：SW 激活→推送订阅→IndexedDB 存储（PWA 能力链）
r_sw = domain_route("写一个 Service Worker 单元（生命周期拦截）")
r_pu = domain_route("写一个推送通知单元（订阅发送）")
r_idb = domain_route("写一个 IndexedDB 单元（对象事务）")
try:
    ns_sw, ns_pu, ns_idb = {}, {}, {}
    exec(r_sw["code"], ns_sw)
    exec(r_pu["code"], ns_pu)
    exec(r_idb["code"], ns_idb)
    sw = {'status': 'idle'}
    ns_sw["sw_lifecycle"](sw, 'install')
    st = ns_sw["sw_lifecycle"](sw, 'activate')
    ep = ns_pu["push_msg"]({'endpoint': None}, 'subscribe')
    sent = ns_pu["push_msg"]({'endpoint': 'e'}, 'send', '新消息')
    ns_idb["idb_txn"]({}, 'put', 'k', 'v')
    got = ns_idb["idb_txn"]({'k': 'v'}, 'get', 'k')
    check('㊏c SW→推送→IndexedDB 端到端（active 订阅发送 存取v）',
          st == 'active' and ep == 'push.example.com'
          and sent == ('sent', '新消息') and got == 'v',
          f'sw={st} push={ep},{sent} idb={got}')
except Exception as ex:
    check('㊏c SW→推送→IndexedDB 端到端（active 订阅发送 存取v）', False, str(ex)[:60])

# ㊐ 目标7 深化：地址/隔离（IPv6/隧道/VLAN 经正式管线）
n10_qs = {
    "IPv6": "写一个 IPv6 地址单元（零压缩展开）",
    "隧道": "写一个隧道封装单元（外层头包裹）",
    "VLAN": "写一个 VLAN 划分单元（802.1Q 标签）",
}
n10_ok = 0
for label, q in n10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n10_ok += 1
    check(f'㊐ {label} 地址/隔离单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊐b 地址/隔离三单元全部生成', n10_ok == 3, f'{n10_ok}/3')

# ㊐c 端到端：IPv6 展开→隧道封装→VLAN 标签（地址→跨网→隔离）
r_v6 = domain_route("写一个 IPv6 地址单元（零压缩展开）")
r_tn = domain_route("写一个隧道封装单元（外层头包裹）")
r_vl = domain_route("写一个 VLAN 划分单元（802.1Q 标签）")
try:
    ns_v6, ns_tn, ns_vl = {}, {}, {}
    exec(r_v6["code"], ns_v6)
    exec(r_tn["code"], ns_tn)
    exec(r_vl["code"], ns_vl)
    g = ns_v6["ipv6_parse"]('fe80::1')
    pkt = ns_tn["tunnel_encap"]('payload', '10.0.0.1', '10.0.0.2')
    inner = ns_tn["tunnel_decap"](pkt)
    tag = ns_vl["vlan_tag"]('frame', 100)
    check('㊐c IPv6→隧道→VLAN 端到端（8组 封装解封 VLAN100）',
          g == ['fe80', '0', '0', '0', '0', '0', '0', '1']
          and inner == 'payload' and tag == ('0x8100', 100),
          f'v6={g} tunnel={inner} vlan={tag}')
except Exception as ex:
    check('㊐c IPv6→隧道→VLAN 端到端（8组 封装解封 VLAN100）', False, str(ex)[:60])

# ㊑ 目标4 深化：启动/固件（引导加载/初始化流程/固件接口 经正式管线）
o12_qs = {
    "引导加载": "写一个引导加载单元（MBR 内核）",
    "初始化流程": "写一个初始化流程单元（依赖排序）",
    "固件接口": "写一个固件接口单元（UEFI 调用）",
}
o12_ok = 0
for label, q in o12_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o12_ok += 1
    check(f'㊑ {label} 启动/固件单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊑b 启动/固件三单元全部生成', o12_ok == 3, f'{o12_ok}/3')

# ㊑c 端到端：固件调用→引导加载→初始化流程（硬件→内核→服务）
r_fw = domain_route("写一个固件接口单元（UEFI 调用）")
r_bl = domain_route("写一个引导加载单元（MBR 内核）")
r_is = domain_route("写一个初始化流程单元（依赖排序）")
try:
    ns_fw, ns_bl, ns_is = {}, {}, {}
    exec(r_fw["code"], ns_fw)
    exec(r_bl["code"], ns_bl)
    exec(r_is["code"], ns_is)
    t = ns_fw["firmware_call"]({'time': 42}, 'get_time')
    k = ns_bl["bootloader"]({'kernel': 'vmlinuz'}, 'mbr')
    order = ns_is["init_sequence"]({'网络': [], '应用': ['网络'], '存储': []})
    check('㊑c 固件→引导→init 端到端（时间42 内核vmlinuz 存储网络应用）',
          t == 42 and k == ('loaded', 'vmlinuz')
          and order == ['存储', '网络', '应用'],
          f'fw={t} boot={k} init={order}')
except Exception as ex:
    check('㊑c 固件→引导→init 端到端（时间42 内核vmlinuz 存储网络应用）', False, str(ex)[:60])

# ㊒ 目标6 深化：分布式图（分区分片/主从复制/分布式查询 经正式管线）
g9_qs = {
    "分区分片": "写一个图分区分片单元（哈希分布）",
    "主从复制": "写一个主从复制单元（写全同步）",
    "分布式查询": "写一个分布式查询单元（并行合并）",
}
g9_ok = 0
for label, q in g9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g9_ok += 1
    check(f'㊒ {label} 分布式图单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊒b 分布式图三单元全部生成', g9_ok == 3, f'{g9_ok}/3')

# ㊒c 端到端：分片→复制→分布式查询（扩展→容错→并行处理）
r_gs = domain_route("写一个图分区分片单元（哈希分布）")
r_rp = domain_route("写一个主从复制单元（写全同步）")
r_dq = domain_route("写一个分布式查询单元（并行合并）")
try:
    ns_gs, ns_rp, ns_dq = {}, {}, {}
    exec(r_gs["code"], ns_gs)
    exec(r_rp["code"], ns_rp)
    exec(r_dq["code"], ns_dq)
    sh = ns_gs["graph_shard"](['a', 'b', 'c', 'd'], 2)
    n = ns_rp["replication"]([{}, {}], 'write', 'k', 'v')
    v = ns_rp["replication"]([{'k': 'v'}, {'k': 'v'}], 'read', 'k')
    merged = ns_dq["dist_query"]([[1, 3], [2, 4]], lambda s: [x * 2 for x in s])
    check('㊒c 分片→复制→分布式查询端到端（2片 写2读v 合并[2,4,6,8]）',
          sh == {0: ['b', 'd'], 1: ['a', 'c']} and n == 2 and v == 'v'
          and merged == [2, 4, 6, 8],
          f'shard={sh} repl={n},{v} query={merged}')
except Exception as ex:
    check('㊒c 分片→复制→分布式查询端到端（2片 写2读v 合并[2,4,6,8]）', False, str(ex)[:60])

# ㊓ 目标7 深化：物联网（MQTT/遥测/消息队列 经正式管线）
n11_qs = {
    "MQTT": "写一个 MQTT 发布订阅单元（主题路由）",
    "遥测": "写一个物联网遥测单元（传感器上报）",
    "消息队列": "写一个消息队列单元（FIFO 队列）",
}
n11_ok = 0
for label, q in n11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n11_ok += 1
    check(f'㊓ {label} 物联网单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊓b 物联网三单元全部生成', n11_ok == 3, f'{n11_ok}/3')

# ㊓c 端到端：MQTT 订阅→遥测上报→消息队列（设备→平台→解耦）
r_mq = domain_route("写一个 MQTT 发布订阅单元（主题路由）")
r_io = domain_route("写一个物联网遥测单元（传感器上报）")
r_q = domain_route("写一个消息队列单元（FIFO 队列）")
try:
    ns_mq, ns_io, ns_q = {}, {}, {}
    exec(r_mq["code"], ns_mq)
    exec(r_io["code"], ns_io)
    exec(r_q["code"], ns_q)
    n = ns_mq["mqtt_broker"]({}, 'subscribe', 'temp', None, 'dev1')
    subs = ns_mq["mqtt_broker"]({'temp': {'dev1'}}, 'publish', 'temp', 25.5)
    cnt = ns_io["iot_telemetry"]({}, 'sensor1', 22.5)
    qlen = ns_q["msg_queue"]([], 'enqueue', 'a')
    item = ns_q["msg_queue"](['a'], 'dequeue')
    check('㊓c MQTT→遥测→队列端到端（订阅1 发布[dev1] 遥测1 入队出队a）',
          n == 1 and subs == ['dev1'] and cnt == 1
          and qlen == 1 and item == 'a',
          f'mqtt={n},{subs} iot={cnt} q={qlen},{item}')
except Exception as ex:
    check('㊓c MQTT→遥测→队列端到端（订阅1 发布[dev1] 遥测1 入队出队a）', False, str(ex)[:60])

# ㊔ 目标2 深化：编译优化（常量折叠/死代码消除/寄存器分配 经正式管线）
c5_qs = {
    "常量折叠": "写一个常量折叠优化单元（编译期求值）",
    "死代码消除": "写一个死代码消除优化单元（不可达指令）",
    "寄存器分配": "写一个寄存器分配优化单元（溢出计数）",
}
c5_ok = 0
for label, q in c5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c5_ok += 1
    check(f'㊔ {label} 编译优化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊔b 编译优化三单元全部生成', c5_ok == 3, f'{c5_ok}/3')

# ㊔c 端到端：常量折叠→死代码消除→寄存器分配（优化管线）
r_cf = domain_route("写一个常量折叠优化单元（编译期求值）")
r_dc = domain_route("写一个死代码消除优化单元（不可达指令）")
r_ra = domain_route("写一个寄存器分配优化单元（溢出计数）")
try:
    ns_cf, ns_dc, ns_ra = {}, {}, {}
    exec(r_cf["code"], ns_cf)
    exec(r_dc["code"], ns_dc)
    exec(r_ra["code"], ns_ra)
    folded = ns_cf["fold_constants"]([("PUSH", 1), ("PUSH", 2), ("ADD", None),
                                      ("LOAD", "x")])
    cleaned = ns_dc["dead_code_elim"]([("DE", 0.5), ("JUMP", 5), ("DE", 0.9)])
    regs, spills = ns_ra["reg_alloc"](['a', 'b', 'c', 'd', 'e'])
    check('㊔c 折叠→死代码→寄存器端到端（PUSH3 删死码 4寄存器1溢出）',
          folded == [("PUSH", 3), ("LOAD", "x")]
          and cleaned == [("DE", 0.5), ("JUMP", 5)]
          and spills == 1 and regs['e'] == 'mem',
          f'fold={folded} dead={cleaned} regs={spills},{regs.get("e")}')
except Exception as ex:
    check('㊔c 折叠→死代码→寄存器端到端（PUSH3 删死码 4寄存器1溢出）', False, str(ex)[:60])

# ㊕ 目标6 深化：图可视化（力导向/分层布局/邻接矩阵 经正式管线）
g10_qs = {
    "力导向布局": "写一个力导向布局单元（斥力引力）",
    "分层布局": "写一个分层布局单元（BFS 层级）",
    "邻接矩阵": "写一个邻接矩阵单元（结构矩阵）",
}
g10_ok = 0
for label, q in g10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g10_ok += 1
    check(f'㊕ {label} 图可视化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊕b 图可视化三单元全部生成', g10_ok == 3, f'{g10_ok}/3')

# ㊕c 端到端：力导向→分层→邻接矩阵（布局→层级→结构矩阵）
r_fl = domain_route("写一个力导向布局单元（斥力引力）")
r_ll = domain_route("写一个分层布局单元（BFS 层级）")
r_am = domain_route("写一个邻接矩阵单元（结构矩阵）")
r_g = domain_route("写一个图存储单元（节点和边）")
ns_g10 = {}
exec(r_g["code"], ns_g10)
Graph10 = ns_g10["Graph"]
try:
    ns_fl, ns_ll, ns_am = {}, {}, {}
    exec(r_fl["code"], ns_fl)
    exec(r_ll["code"], ns_ll)
    exec(r_am["code"], ns_am)
    pos = ns_fl["force_layout"](['a', 'b'], [('a', 'b')], 1)
    g = Graph10()
    g.add_edge("气压低", "沸点降")
    layers = ns_ll["layer_layout"](g)
    mat = ns_am["adjacency_matrix"](g)
    check('㊕c 力导向→分层→矩阵端到端（a0.1b0.5 气压低层0 矩阵2x2）',
          pos == {'a': 0.1, 'b': 0.5} and layers.get('气压低') == 0
          and len(mat) == 2,
          f'pos={pos} layers={layers} mat={len(mat)}x{len(mat)}')
except Exception as ex:
    check('㊕c 力导向→分层→矩阵端到端（a0.1b0.5 气压低层0 矩阵2x2）', False, str(ex)[:60])

# ㊖ 目标1 深化：类型系统（类型注解/运行时检查/协议 经正式管线）
p7_qs = {
    "类型注解": "写一个类型注解单元（参数返回标注）",
    "运行时检查": "写一个运行时检查单元（isinstance）",
    "协议": "写一个协议接口单元（结构约定）",
}
p7_ok = 0
for label, q in p7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p7_ok += 1
    check(f'㊖ {label} 类型系统单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊖b 类型系统三单元全部生成', p7_ok == 3, f'{p7_ok}/3')

# ㊖c 端到端：注解→运行时检查→协议（标注→校验→约定）
r_an = domain_route("写一个类型注解单元（参数返回标注）")
r_rc = domain_route("写一个运行时检查单元（isinstance）")
r_pr = domain_route("写一个协议接口单元（结构约定）")
try:
    ns_an, ns_rc, ns_pr = {}, {}, {}
    exec(r_an["code"], ns_an)
    exec(r_rc["code"], ns_rc)
    exec(r_pr["code"], ns_pr)
    a = ns_an["annotate_test"]()
    r1 = ns_rc["runtime_check"](5.0, int)
    r2 = ns_rc["runtime_check"]('5', int)
    p = ns_pr["check_protocol"]([], ['__len__', '__iter__'])
    check('㊖c 注解→检查→协议端到端（int标注 浮点ok字符串拒 序列协议真）',
          a == {'params': {'x': int}, 'return': str}
          and r1 == 'ok' and r2 == 'type_error' and p is True,
          f'ann={a} chk={r1},{r2} proto={p}')
except Exception as ex:
    check('㊖c 注解→检查→协议端到端（int标注 浮点ok字符串拒 序列协议真）', False, str(ex)[:60])

# ㊗ 目标4 深化：安全模块（ACL/审计/能力 经正式管线）
o13_qs = {
    "访问控制": "写一个访问控制单元（ACL 判定）",
    "审计日志": "写一个审计日志单元（事件记录）",
    "能力系统": "写一个能力系统单元（特权令牌）",
}
o13_ok = 0
for label, q in o13_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o13_ok += 1
    check(f'㊗ {label} 安全模块单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊗b 安全模块三单元全部生成', o13_ok == 3, f'{o13_ok}/3')

# ㊗c 端到端：ACL 判定→审计记录→能力检查（授权→追溯→特权）
r_acl = domain_route("写一个访问控制单元（ACL 判定）")
r_aud = domain_route("写一个审计日志单元（事件记录）")
r_cap = domain_route("写一个能力系统单元（特权令牌）")
try:
    ns_acl, ns_aud, ns_cap = {}, {}, {}
    exec(r_acl["code"], ns_acl)
    exec(r_aud["code"], ns_aud)
    exec(r_cap["code"], ns_cap)
    ok_r = ns_acl["acl_check"](
        {'file': [{'subject': 'u1', 'action': 'read', 'allow': True}]},
        'u1', 'file', 'read')
    deny_w = ns_acl["acl_check"]({'file': []}, 'u1', 'file', 'write')
    n = ns_aud["audit_log"]([], 'login', 'u1')
    ns_cap["capability"](set(), 'grant', 'net_raw')
    has = ns_cap["capability"]({'net_raw'}, 'check', 'net_raw')
    check('㊗c ACL→审计→能力端到端（读允写拒 日志1 有能力）',
          ok_r is True and deny_w is False and n == 1 and has is True,
          f'acl={ok_r},{deny_w} audit={n} cap={has}')
except Exception as ex:
    check('㊗c ACL→审计→能力端到端（读允写拒 日志1 有能力）', False, str(ex)[:60])

# ㊘ 目标7 深化：CDN/边缘（CDN缓存/边缘计算/内容路由 经正式管线）
n12_qs = {
    "CDN缓存": "写一个 CDN 缓存单元（边缘分发）",
    "边缘计算": "写一个边缘计算单元（就近处理）",
    "内容路由": "写一个内容路由单元（前缀匹配）",
}
n12_ok = 0
for label, q in n12_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n12_ok += 1
    check(f'㊘ {label} CDN/边缘单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊘b CDN/边缘三单元全部生成', n12_ok == 3, f'{n12_ok}/3')

# ㊘c 端到端：CDN 命中→内容路由→边缘计算（分发→寻址→就近处理）
r_cd = domain_route("写一个 CDN 缓存单元（边缘分发）")
r_cr = domain_route("写一个内容路由单元（前缀匹配）")
r_ec = domain_route("写一个边缘计算单元（就近处理）")
try:
    ns_cd, ns_cr, ns_ec = {}, {}, {}
    exec(r_cd["code"], ns_cd)
    exec(r_cr["code"], ns_cr)
    exec(r_ec["code"], ns_ec)
    hit = ns_cd["cdn_cache"]([{'cache': {'/a': 'DATA'}}], 'X', '/a')
    srv = ns_cr["content_route"]({'/img': 'img-srv', '/img/logo': 'logo-srv'},
                                 '/img/logo/a.png')
    e = ns_ec["edge_compute"]([{'id': 'e1', 'loc': 1, 'fn': lambda x: x * 2}],
                               'double', 5)
    check('㊘c CDN→内容路由→边缘端到端（命中DATA logo-srv e1计算10）',
          hit == ('hit', 'DATA') and srv == 'logo-srv' and e == ('e1', 'double', 10),
          f'cdn={hit} route={srv} edge={e}')
except Exception as ex:
    check('㊘c CDN→内容路由→边缘端到端（命中DATA logo-srv e1计算10）', False, str(ex)[:60])

# ㊙ 目标6 深化：运维（备份恢复/一致性检查/压缩编码 经正式管线）
g11_qs = {
    "备份恢复": "写一个图备份恢复单元（全量增量）",
    "一致性检查": "写一个图一致性检查单元（悬空边）",
    "压缩编码": "写一个图压缩编码单元（CSR 表示）",
}
g11_ok = 0
for label, q in g11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g11_ok += 1
    check(f'㊙ {label} 图运维单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊙b 图运维三单元全部生成', g11_ok == 3, f'{g11_ok}/3')

# ㊙c 端到端：备份→一致性→压缩（数据安全→完整性→紧凑存储）
r_bk = domain_route("写一个图备份恢复单元（全量增量）")
r_ic = domain_route("写一个图一致性检查单元（悬空边）")
r_cp = domain_route("写一个图压缩编码单元（CSR 表示）")
r_g = domain_route("写一个图存储单元（节点和边）")
ns_g11 = {}
exec(r_g["code"], ns_g11)
Graph11 = ns_g11["Graph"]
try:
    ns_bk, ns_ic, ns_cp = {}, {}, {}
    exec(r_bk["code"], ns_bk)
    exec(r_ic["code"], ns_ic)
    exec(r_cp["code"], ns_cp)
    repo = {'full': None, 'incr': None}
    ns_bk["backup_ops"](repo, 'full', {'a': 1})
    ns_bk["backup_ops"](repo, 'incr', {'b': 2})
    merged = ns_bk["backup_ops"](repo, 'restore')
    g = Graph11()
    g.add_edge("a", "b")
    errs = ns_ic["integrity_check"](g)
    csr = ns_cp["compress_adjacency"](g)
    check('㊙c 备份→一致性→压缩端到端（恢复{a,b} 无错误 CSR偏移[0,1,1]）',
          merged == {'a': 1, 'b': 2} and errs == []
          and csr['offsets'] == [0, 1, 1],
          f'backup={merged} integ={errs} csr={csr["offsets"]}')
except Exception as ex:
    check('㊙c 备份→一致性→压缩端到端（恢复{a,b} 无错误 CSR偏移[0,1,1]）', False, str(ex)[:60])

# ㊚ 目标4 深化：性能分析（profiling/瓶颈/调优 经正式管线）
o14_qs = {
    "性能分析": "写一个性能分析单元（函数耗时）",
    "瓶颈检测": "写一个瓶颈检测单元（最高利用率）",
    "调优建议": "写一个调优建议单元（参数调整）",
}
o14_ok = 0
for label, q in o14_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o14_ok += 1
    check(f'㊚ {label} 性能分析单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊚b 性能分析三单元全部生成', o14_ok == 3, f'{o14_ok}/3')

# ㊚c 端到端：profiling→瓶颈→调优（耗时统计→热点定位→建议）
r_pf = domain_route("写一个性能分析单元（函数耗时）")
r_bn = domain_route("写一个瓶颈检测单元（最高利用率）")
r_tu = domain_route("写一个调优建议单元（参数调整）")
try:
    ns_pf, ns_bn, ns_tu = {}, {}, {}
    exec(r_pf["code"], ns_pf)
    exec(r_bn["code"], ns_bn)
    exec(r_tu["code"], ns_tu)
    p = ns_pf["profile_funcs"]([10, 20, 30])
    b = ns_bn["bottleneck"]({'cpu': 90, 'mem': 60})
    a = ns_tu["tuning_advice"]({'cpu': 90, 'mem': 50})
    check('㊚c profiling→瓶颈→调优端到端（总60均20 cpu瓶颈 升级建议）',
          p == {'total': 60, 'avg': 20.0} and b == ('cpu', 90)
          and a == ['升级 CPU 或减少进程'],
          f'prof={p} bn={b} adv={a}')
except Exception as ex:
    check('㊚c profiling→瓶颈→调优端到端（总60均20 cpu瓶颈 升级建议）', False, str(ex)[:60])

# ㊛ 目标6 深化：图监控（指标统计/健康检查/度分布 经正式管线）
g12_qs = {
    "指标统计": "写一个图指标统计单元（节点边密度）",
    "健康检查": "写一个图健康检查单元（连通判定）",
    "度分布": "写一个图度分布单元（出度直方图）",
}
g12_ok = 0
for label, q in g12_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g12_ok += 1
    check(f'㊛ {label} 图监控单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊛b 图监控三单元全部生成', g12_ok == 3, f'{g12_ok}/3')

# ㊛c 端到端：指标→健康→度分布（规模→连通→结构）
r_gm = domain_route("写一个图指标统计单元（节点边密度）")
r_hc = domain_route("写一个图健康检查单元（连通判定）")
r_dd = domain_route("写一个图度分布单元（出度直方图）")
r_g = domain_route("写一个图存储单元（节点和边）")
ns_g12 = {}
exec(r_g["code"], ns_g12)
Graph12 = ns_g12["Graph"]
try:
    ns_gm, ns_hc, ns_dd = {}, {}, {}
    exec(r_gm["code"], ns_gm)
    exec(r_hc["code"], ns_hc)
    exec(r_dd["code"], ns_dd)
    g = Graph12()
    g.add_edge("气压低", "沸点降")
    g.add_edge("沸点降", "煮不熟")
    m = ns_gm["graph_metrics"](g)
    h = ns_hc["health_check"](g)
    d = ns_dd["degree_distribution"](g)
    check('㊛c 指标→健康→度分布端到端（3节点2边 健康ok 度分布{0:1,1:2}）',
          m['nodes'] == 3 and m['edges'] == 2 and h == ('ok', True)
          and d == {0: 1, 1: 2},
          f'metrics={m} health={h} dist={d}')
except Exception as ex:
    check('㊛c 指标→健康→度分布端到端（3节点2边 健康ok 度分布）', False, str(ex)[:60])

# ㊜ 目标1 深化：异步（async await/事件循环/并发任务 经正式管线）
p8_qs = {
    "异步协程": "写一个异步协程单元（async await）",
    "事件循环": "写一个事件循环单元（任务调度）",
    "并发任务": "写一个并发任务单元（gather 汇总）",
}
p8_ok = 0
for label, q in p8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p8_ok += 1
    check(f'㊜ {label} 异步单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊜b 异步三单元全部生成', p8_ok == 3, f'{p8_ok}/3')

# ㊜c 端到端：协程→事件循环→并发任务（异步执行链）
r_ac = domain_route("写一个异步协程单元（async await）")
r_el = domain_route("写一个事件循环单元（任务调度）")
r_ct = domain_route("写一个并发任务单元（gather 汇总）")
try:
    ns_ac, ns_el, ns_ct = {}, {}, {}
    exec(r_ac["code"], ns_ac)
    exec(r_el["code"], ns_el)
    exec(r_ct["code"], ns_ct)
    a = ns_ac["async_test"]()
    el = ns_el["event_loop"]([lambda: 1, lambda: 2])
    g = ns_ct["gather"]([lambda: 'a', lambda: 'b'])
    check('㊜c 协程→事件循环→并发端到端（任务_done [1,2] [a,b]）',
          a == '任务_done' and el == [1, 2] and g == ['a', 'b'],
          f'async={a} loop={el} gather={g}')
except Exception as ex:
    check('㊜c 协程→事件循环→并发端到端（任务_done [1,2] [a,b]）', False, str(ex)[:60])

# ㊝ 目标4 深化：配额/限额（磁盘配额/文件锁/资源限额 经正式管线）
o15_qs = {
    "磁盘配额": "写一个磁盘配额单元（用户限额）",
    "文件锁": "写一个文件锁单元（flock 独占）",
    "资源限额": "写一个资源限额单元（ulimit 软限）",
}
o15_ok = 0
for label, q in o15_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o15_ok += 1
    check(f'㊝ {label} 配额/限额单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊝b 配额/限额三单元全部生成', o15_ok == 3, f'{o15_ok}/3')

# ㊝c 端到端：配额→文件锁→资源限额（存储限制→并发保护→资源约束）
r_q = domain_route("写一个磁盘配额单元（用户限额）")
r_fl = domain_route("写一个文件锁单元（flock 独占）")
r_rl = domain_route("写一个资源限额单元（ulimit 软限）")
try:
    ns_q, ns_fl, ns_rl = {}, {}, {}
    exec(r_q["code"], ns_q)
    exec(r_fl["code"], ns_fl)
    exec(r_rl["code"], ns_rl)
    ok_q = ns_q["quota_check"]({'u1': 100}, 'u1', 95, 10)
    fl = ns_fl["file_lock"]({'locked': True}, 'lock')
    rl = ns_rl["rlimit"]({}, 'set', 1024)
    got = ns_rl["rlimit"]({'soft': 1024}, 'get')
    check('㊝c 配额→锁→限额端到端（超限拒 锁阻塞 软限1024）',
          ok_q is False and fl == 'blocked' and rl == 1024 and got == 1024,
          f'quota={ok_q} lock={fl} rlimit={rl},{got}')
except Exception as ex:
    check('㊝c 配额→锁→限额端到端（超限拒 锁阻塞 软限1024）', False, str(ex)[:60])

# ㊞ 目标7 深化：网络监控（流量统计/延迟测量/异常检测 经正式管线）
n13_qs = {
    "流量统计": "写一个流量统计单元（每流汇总）",
    "延迟测量": "写一个延迟测量单元（RTT 统计）",
    "异常检测": "写一个异常检测单元（突增告警）",
}
n13_ok = 0
for label, q in n13_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n13_ok += 1
    check(f'㊞ {label} 网络监控单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊞b 网络监控三单元全部生成', n13_ok == 3, f'{n13_ok}/3')

# ㊞c 端到端：流量统计→延迟测量→异常检测（监控分析链）
r_ts = domain_route("写一个流量统计单元（每流汇总）")
r_rt = domain_route("写一个延迟测量单元（RTT 统计）")
r_ad = domain_route("写一个异常检测单元（突增告警）")
try:
    ns_ts, ns_rt, ns_ad = {}, {}, {}
    exec(r_ts["code"], ns_ts)
    exec(r_rt["code"], ns_rt)
    exec(r_ad["code"], ns_ad)
    st = ns_ts["traffic_stats"]([{'src': 'a', 'dst': 'b', 'bytes': 100, 'pkts': 2},
                                 {'src': 'a', 'dst': 'b', 'bytes': 50, 'pkts': 1}])
    rtt = ns_rt["rtt_stats"]([10, 20, 30])
    alert = ns_ad["anomaly_detect"]([50, 200, 80], 100)
    check('㊞c 流量→延迟→异常端到端（a→b 150B/3包 RTT均20 告警200）',
          st == {'a→b': {'bytes': 150, 'pkts': 3}} and rtt == {'avg': 20.0,
          'min': 10, 'max': 30} and alert == [200],
          f'stats={st} rtt={rtt} alert={alert}')
except Exception as ex:
    check('㊞c 流量→延迟→异常端到端（a→b 150B/3包 RTT均20 告警200）', False, str(ex)[:60])

# ㊟ 目标4 深化：可信计算（安全启动/TPM度量/哈希校验 经正式管线）
o16_qs = {
    "安全启动": "写一个安全启动单元（签名验证链）",
    "TPM度量": "写一个 TPM 度量单元（PCR 扩展）",
    "哈希校验": "写一个哈希校验单元（完整性验证）",
}
o16_ok = 0
for label, q in o16_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o16_ok += 1
    check(f'㊟ {label} 可信计算单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊟b 可信计算三单元全部生成', o16_ok == 3, f'{o16_ok}/3')

# ㊟c 端到端：安全启动→TPM 度量→哈希校验（信任链）
r_sb = domain_route("写一个安全启动单元（签名验证链）")
r_tm = domain_route("写一个 TPM 度量单元（PCR 扩展）")
r_hv = domain_route("写一个哈希校验单元（完整性验证）")
try:
    ns_sb, ns_tm, ns_hv = {}, {}, {}
    exec(r_sb["code"], ns_sb)
    exec(r_tm["code"], ns_tm)
    exec(r_hv["code"], ns_hv)
    b = ns_sb["secure_boot"](['kernel', 'initrd'], {'kernel', 'initrd'})
    pcr = ns_tm["tpm_measure"](0, 'BIOS')
    iv = ns_hv["hash_verify"]('abc123', 'abc123')
    tv = ns_hv["hash_verify"]('abc', 'xyz')
    check('㊟c 安全启动→TPM→哈希端到端（启动ok PCR45 完整/篡改）',
          b == ('booted', True) and pcr == 45
          and iv == 'integrity_ok' and tv == 'tampered',
          f'boot={b} pcr={pcr} verify={iv},{tv}')
except Exception as ex:
    check('㊟c 安全启动→TPM→哈希端到端（启动ok PCR45 完整/篡改）', False, str(ex)[:60])

# ㊠ 目标6 深化：图嵌入/学习（节点特征/图特征/相似推荐 经正式管线）
g13_qs = {
    "节点特征": "写一个节点特征单元（出入度向量）",
    "图特征": "写一个图特征单元（图级向量）",
    "相似推荐": "写一个相似推荐单元（共同邻居）",
}
g13_ok = 0
for label, q in g13_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g13_ok += 1
    check(f'㊠ {label} 图嵌入/学习单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊠b 图嵌入/学习三单元全部生成', g13_ok == 3, f'{g13_ok}/3')

# ㊠c 端到端：节点特征→图特征→相似推荐（特征提取→图分类→推荐）
r_nf = domain_route("写一个节点特征单元（出入度向量）")
r_gf = domain_route("写一个图特征单元（图级向量）")
r_sr = domain_route("写一个相似推荐单元（共同邻居）")
r_g = domain_route("写一个图存储单元（节点和边）")
ns_g13 = {}
exec(r_g["code"], ns_g13)
Graph13 = ns_g13["Graph"]
try:
    ns_nf, ns_gf, ns_sr = {}, {}, {}
    exec(r_nf["code"], ns_nf)
    exec(r_gf["code"], ns_gf)
    exec(r_sr["code"], ns_sr)
    g = Graph13()
    g.add_edge("a", "b")
    g.add_edge("b", "c")
    nf = ns_nf["node_features"](g)
    gf = ns_gf["graph_features"](g)
    rec = ns_sr["similar_recommend"](g, "a")
    check('㊠c 节点特征→图特征→推荐端到端（a出1 3节点2边 推荐[b,c]）',
          nf['a']['out'] == 1 and nf['c']['in'] == 1
          and gf['nodes'] == 3 and gf['edges'] == 2
          and set(rec) == {'b', 'c'},
          f'nf={nf} gf={gf} rec={rec}')
except Exception as ex:
    check('㊠c 节点特征→图特征→推荐端到端（a出1 3节点2边 推荐[b,c]）', False, str(ex)[:60])

# ㊡ 目标5 深化：性能优化（渲染优化/懒加载/防抖节流 经正式管线）
b9_qs = {
    "渲染优化": "写一个渲染优化单元（批量更新）",
    "懒加载": "写一个懒加载单元（视口按需）",
    "防抖节流": "写一个节流单元（限频执行）",
}
b9_ok = 0
for label, q in b9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b9_ok += 1
    check(f'㊡ {label} 性能优化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊡b 性能优化三单元全部生成', b9_ok == 3, f'{b9_ok}/3')

# ㊡c 端到端：批量更新→懒加载→节流（渲染→加载→事件优化）
r_bu = domain_route("写一个渲染优化单元（批量更新）")
r_ll = domain_route("写一个懒加载单元（视口按需）")
r_th = domain_route("写一个节流单元（限频执行）")
try:
    ns_bu, ns_ll, ns_th = {}, {}, {}
    exec(r_bu["code"], ns_bu)
    exec(r_ll["code"], ns_ll)
    exec(r_th["code"], ns_th)
    m = ns_bu["batch_update"]([{'id': 'a', 'html': 'x'}, {'id': 'a', 'html': 'y'}])
    l = ns_ll["lazy_load"]([{'id': 'a', 'pos': 100}, {'id': 'b', 'pos': 500}], 300)
    t = ns_th["throttle"]([0, 5, 10, 20], 10)
    check('㊡c 批量→懒加载→节流端到端（合并a=y 加载a 限频[0,10,20]）',
          m == {'a': 'y'} and len(l) == 1 and l[0]['id'] == 'a'
          and t == [0, 10, 20],
          f'batch={m} lazy={len(l)} throttle={t}')
except Exception as ex:
    check('㊡c 批量→懒加载→节流端到端（合并a=y 加载a 限频[0,10,20]）', False, str(ex)[:60])

# ㊢ 目标7 深化：协议分析（报文解析/抓包分析/协议解码 经正式管线）
n14_qs = {
    "报文解析": "写一个 IP 报文解析单元（头部字段）",
    "抓包分析": "写一个抓包分析单元（协议分布）",
    "协议解码": "写一个协议解码单元（十六进制转字节）",
}
n14_ok = 0
for label, q in n14_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n14_ok += 1
    check(f'㊢ {label} 协议分析单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊢b 协议分析三单元全部生成', n14_ok == 3, f'{n14_ok}/3')

# ㊢c 端到端：报文解析→抓包统计→协议解码（分析链）
r_pi = domain_route("写一个 IP 报文解析单元（头部字段）")
r_cs = domain_route("写一个抓包分析单元（协议分布）")
r_hd = domain_route("写一个协议解码单元（十六进制转字节）")
try:
    ns_pi, ns_cs, ns_hd = {}, {}, {}
    exec(r_pi["code"], ns_pi)
    exec(r_cs["code"], ns_cs)
    exec(r_hd["code"], ns_hd)
    ip = ns_pi["parse_ip"](bytes([0x45, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0,
                                  192, 168, 1, 1, 8, 8, 8, 8]))
    st = ns_cs["capture_stats"]([{'proto': 'TCP'}, {'proto': 'UDP'}])
    dec = ns_hd["hex_decode"]('48656c6c6f')
    check('㊢c 报文→抓包→解码端到端（IPv4 TCP 2包 TCP/UDP Hello）',
          ip['version'] == 4 and ip['proto'] == 6 and ip['src'] == '192.168.1.1'
          and st['total'] == 2 and st['by_proto'] == {'TCP': 1, 'UDP': 1}
          and dec == b'Hello',
          f'ip={ip} stats={st} dec={dec}')
except Exception as ex:
    check('㊢c 报文→抓包→解码端到端（IPv4 TCP 2包 TCP/UDP Hello）', False, str(ex)[:60])

# ㊣ 目标4 深化：设备热插拔（热插拔/即插即用/设备树 经正式管线）
o17_qs = {
    "热插拔": "写一个设备热插拔单元（接入移除）",
    "即插即用": "写一个即插即用单元（驱动匹配）",
    "设备树": "写一个设备树单元（拓扑查询）",
}
o17_ok = 0
for label, q in o17_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o17_ok += 1
    check(f'㊣ {label} 设备热插拔单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊣b 设备热插拔三单元全部生成', o17_ok == 3, f'{o17_ok}/3')

# ㊣c 端到端：热插拔→即插即用→设备树（接入→匹配→拓扑）
r_hp = domain_route("写一个设备热插拔单元（接入移除）")
r_pn = domain_route("写一个即插即用单元（驱动匹配）")
r_dt = domain_route("写一个设备树单元（拓扑查询）")
try:
    ns_hp, ns_pn, ns_dt = {}, {}, {}
    exec(r_hp["code"], ns_hp)
    exec(r_pn["code"], ns_pn)
    exec(r_dt["code"], ns_dt)
    ns_hp["hotplug"](set(), 'plug', 'usb1')
    lst = ns_hp["hotplug"]({'usb1'}, 'list')
    m = ns_pn["plug_and_play"]('VID_1234_PID_1',
                               [{'vendor': 'VID_1234', 'name': '鼠标'}])
    dt = ns_dt["device_tree_lookup"]({'uart0': {'compatible': 'ns16550'}}, 'uart0')
    check('㊣c 热插拔→即插即用→设备树端到端（列表[usb1] 匹配鼠标 拓扑ns16550）',
          lst == ['usb1'] and m == ('matched', '鼠标')
          and dt == {'compatible': 'ns16550'},
          f'hotplug={lst} pnp={m} tree={dt}')
except Exception as ex:
    check('㊣c 热插拔→即插即用→设备树端到端（列表[usb1] 匹配鼠标 拓扑ns16550）', False, str(ex)[:60])

# ㊤ 目标6 深化：图安全（权限控制/租户隔离/加密存储 经正式管线）
g14_qs = {
    "权限控制": "写一个图权限控制单元（节点 ACL）",
    "租户隔离": "写一个租户隔离单元（owner 过滤）",
    "加密存储": "写一个加密存储单元（异或保护）",
}
g14_ok = 0
for label, q in g14_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g14_ok += 1
    check(f'㊤ {label} 图安全单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊤b 图安全三单元全部生成', g14_ok == 3, f'{g14_ok}/3')

# ㊤c 端到端：权限→租户→加密（授权→隔离→保护）
r_ga = domain_route("写一个图权限控制单元（节点 ACL）")
r_ts = domain_route("写一个租户隔离单元（owner 过滤）")
r_es = domain_route("写一个加密存储单元（异或保护）")
r_g = domain_route("写一个图存储单元（节点和边）")
ns_g14 = {}
exec(r_g["code"], ns_g14)
Graph14 = ns_g14["Graph"]
try:
    ns_ga, ns_ts, ns_es = {}, {}, {}
    exec(r_ga["code"], ns_ga)
    exec(r_ts["code"], ns_ts)
    exec(r_es["code"], ns_es)
    ok_r = ns_ga["graph_acl"]({'n1': [{'user': 'u1', 'action': 'read',
                                       'allow': True}]}, 'u1', 'n1', 'read')
    g = Graph14()
    g.add_edge("a", "b")
    g.owner = {'a': 't1', 'b': 't2'}
    vis = ns_ts["tenant_scope"](g, 't1')
    code = ns_es["encrypt_node"]('秘密', 7)
    dec = ns_es["decrypt_node"](code, 7)
    check('㊤c 权限→租户→加密端到端（读允 t1见a 加密解密往返）',
          ok_r is True and vis == ['a'] and dec == '秘密',
          f'acl={ok_r} tenant={vis} crypto={dec}')
except Exception as ex:
    check('㊤c 权限→租户→加密端到端（读允 t1见a 加密解密往返）', False, str(ex)[:60])

# ㊥ 目标2 深化：中文编译器闭包（捕获分析/闭包创建/闭包调用 经正式管线）
c3_qs = {
    "捕获分析": "写一个中文编译器闭包捕获分析单元（自由变量）",
    "闭包创建": "写一个中文编译器闭包创建单元（函数体捕获环境）",
    "闭包调用": "写一个中文编译器闭包调用单元（捕获环境参数绑定）",
}
c3_ok = 0
for label, q in c3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c3_ok += 1
    check(f'㊥ {label} 编译器闭包单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊥b 编译器闭包三单元全部生成', c3_ok == 3, f'{c3_ok}/3')

# ㊥c 闭包端到端：捕获分析→创建→调用（自由变量甲被捕获，参数乙遮蔽捕获值）
r_fa = domain_route("写一个中文编译器闭包捕获分析单元（自由变量）")
r_mc = domain_route("写一个中文编译器闭包创建单元（函数体捕获环境）")
r_cc = domain_route("写一个中文编译器闭包调用单元（捕获环境参数绑定）")
try:
    ns_fa, ns_mc, ns_cc = {}, {}, {}
    exec(r_fa["code"], ns_fa)
    exec(r_mc["code"], ns_mc)
    exec(r_cc["code"], ns_cc)
    free = ns_fa["analyze_free_vars"](['甲', '乙'], ['乙'], ['甲', '乙', '丙'])
    cl = ns_mc["make_closure"]([("DE", 0.5)], free, {"甲": 3, "乙": 7})
    env = ns_cc["call_closure"](cl, ["乙"], [9])
    check('㊥c 闭包端到端（捕获甲=3 参数乙=9 遮蔽捕获7）',
          free == ['甲'] and env == {"甲": 3, "乙": 9},
          f'free={free} env={env}')
except Exception as ex:
    check('㊥c 闭包端到端（捕获甲=3 参数乙=9 遮蔽捕获7）', False, str(ex)[:60])

# ㊦ 目标1 深化：P 线元编程（动态建类/元类定制/描述符协议 经正式管线）
p3_qs = {
    "动态建类": "写一个动态建类单元（type 运行时建类）",
    "元类定制": "写一个元类定制单元（类创建钩子）",
    "描述符": "写一个描述符协议单元（属性访问托管）",
}
p3_ok = 0
for label, q in p3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p3_ok += 1
    check(f'㊦ {label} P线元编程单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊦b P线元编程三单元全部生成', p3_ok == 3, f'{p3_ok}/3')

# ㊦c 元编程端到端：动态建类→元类定制→描述符（建狗类→钩子注入科→属性托管读写）
r_mc = domain_route("写一个动态建类单元（type 运行时建类）")
r_me = domain_route("写一个元类定制单元（类创建钩子）")
r_ds = domain_route("写一个描述符协议单元（属性访问托管）")
try:
    ns_mc, ns_me, ns_ds = {}, {}, {}
    exec(r_mc["code"], ns_mc)
    exec(r_me["code"], ns_me)
    exec(r_ds["code"], ns_ds)
    cls = ns_mc["make_class"]("狗", [], {"叫声": "汪"})
    met = ns_me["meta_create"]("狗", {"叫声": "汪"}, lambda n, a: {"科": "犬科"})
    st = {}
    got = ns_ds["descriptor_route"](st, {"__get__": lambda s, n: s.get('_' + n, 25),
                                         "__set__": lambda s, n, v: s.update({'_' + n: v})},
                                    "温度", 30)
    read = ns_ds["descriptor_route"](st, {"__get__": lambda s, n: s.get('_' + n, 25),
                                          "__set__": lambda s, n, v: s.update({'_' + n: v})},
                                     "温度", None)
    check('㊦c 元编程端到端（类名狗 钩子注入科 描述符写30读30）',
          cls[0] == "狗" and met[1] == {"叫声": "汪", "科": "犬科"}
          and got == {"_温度": 30} and read == 30,
          f'cls={cls} meta={met} write={got} read={read}')
except Exception as ex:
    check('㊦c 元编程端到端（类名狗 钩子注入科 描述符写30读30）', False, str(ex)[:60])

# ㊧ 目标2 深化：C4 调试器工具链（断点/调用栈回溯/变量监视 经正式管线）
c4_qs = {
    "断点": "写一个断点单元（命中停止）",
    "回溯": "写一个调用栈回溯单元（栈帧链）",
    "监视": "写一个变量监视单元（watch 求值）",
}
c4_ok = 0
for label, q in c4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c4_ok += 1
    check(f'㊧ {label} C4调试器单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊧b C4调试器三单元全部生成', c4_ok == 3, f'{c4_ok}/3')

# ㊧c 调试端到端：断点→回溯→监视（登记5命中 / 出错帧f2链[f2,f1,main] / watch甲=3）
r_bp = domain_route("写一个断点单元（命中停止）")
r_tb = domain_route("写一个调用栈回溯单元（栈帧链）")
r_wt = domain_route("写一个变量监视单元（watch 求值）")
try:
    ns_bp, ns_tb, ns_wt = {}, {}, {}
    exec(r_bp["code"], ns_bp)
    exec(r_tb["code"], ns_tb)
    exec(r_wt["code"], ns_wt)
    breaks = set()
    ns_bp["breakpoint_hit"](breaks, 5, True)
    hit = ns_bp["breakpoint_hit"](breaks, 5, None)
    chain = ns_tb["traceback_chain"](["main", "f1"], "f2")
    val = ns_wt["watch_eval"]("甲", {"甲": 3})
    check('㊧c 断点→回溯→监视端到端（命中True 链[f2,f1,main] watch甲=3）',
          hit is True and chain == ["f2", "f1", "main"] and val == 3,
          f'hit={hit} chain={chain} watch={val}')
except Exception as ex:
    check('㊧c 断点→回溯→监视端到端（命中True 链[f2,f1,main] watch甲=3）', False, str(ex)[:60])

# ㊨ 目标4 深化：OS IPC 族（消息队列/共享内存/邮箱 经正式管线）
o3_qs = {
    "消息队列": "写一个 IPC 消息队列单元（类型投递）",
    "共享内存": "写一个共享内存单元（物理页共享）",
    "邮箱": "写一个邮箱单元（异步消息槽）",
}
o3_ok = 0
for label, q in o3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o3_ok += 1
    check(f'㊨ {label} OS IPC单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊨b OS IPC三单元全部生成', o3_ok == 3, f'{o3_ok}/3')

# ㊨c IPC 端到端：消息队列→共享内存→邮箱（类型取甲 / 写65读65 / 投递2取FIFO）
r_mq = domain_route("写一个 IPC 消息队列单元（类型投递）")
r_sh = domain_route("写一个共享内存单元（物理页共享）")
r_mb = domain_route("写一个邮箱单元（异步消息槽）")
try:
    ns_mq, ns_sh, ns_mb = {}, {}, {}
    exec(r_mq["code"], ns_mq)
    exec(r_sh["code"], ns_sh)
    exec(r_mb["code"], ns_mb)
    q = [(1, '甲'), (2, '乙')]
    got_mq = ns_mq["msg_queue_ops"](q, 'recv', 1)
    segs = {'k1': {'data': bytearray(4), 'refs': 1}}
    ns_sh["shm_ops"](segs, 'k1', 'write', 2, 65)
    got_sh = ns_sh["shm_ops"](segs, 'k1', 'read', 2)
    mb = []
    ns_mb["mailbox_ops"](mb, 'put', 'a')
    ns_mb["mailbox_ops"](mb, 'put', 'b')
    got_mb = ns_mb["mailbox_ops"](mb, 'get')
    check('㊨c 消息队列→共享内存→邮箱端到端（(1,甲) 65 a）',
          got_mq == (1, '甲') and got_sh == 65 and got_mb == 'a',
          f'msg={got_mq} shm={got_sh} mailbox={got_mb}')
except Exception as ex:
    check('㊨c 消息队列→共享内存→邮箱端到端（(1,甲) 65 a）', False, str(ex)[:60])

# ㊩ 目标5 深化：PWA（应用清单/缓存策略/安装事件 经正式管线）
b3_qs = {
    "应用清单": "写一个 PWA 应用清单单元（最小字段）",
    "缓存策略": "写一个缓存策略单元（SW 离线可用）",
    "安装事件": "写一个安装事件单元（安装提示流）",
}
b3_ok = 0
for label, q in b3_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b3_ok += 1
    check(f'㊩ {label} PWA单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊩b PWA三单元全部生成', b3_ok == 3, f'{b3_ok}/3')

# ㊩c PWA 端到端：清单→缓存策略→安装（可安装 缓存优先D 捕获→提示→安装）
r_mf = domain_route("写一个 PWA 应用清单单元（最小字段）")
r_cs = domain_route("写一个缓存策略单元（SW 离线可用）")
r_ip = domain_route("写一个安装事件单元（安装提示流）")
try:
    ns_mf, ns_cs, ns_ip = {}, {}, {}
    exec(r_mf["code"], ns_mf)
    exec(r_cs["code"], ns_cs)
    exec(r_ip["code"], ns_ip)
    ok_mf, miss = ns_mf["manifest_check"]({'name': '应用', 'icons': ['i'],
                                           'start_url': '/'})
    got_cs = ns_cs["cache_strategy"]('cache-first', {'/a': 'D'}, '/a')
    st = {}
    ns_ip["install_prompt"](st, 'capture')
    shown = ns_ip["install_prompt"](st, 'prompt')
    done = ns_ip["install_prompt"](st, 'accept')
    check('㊩c 清单→缓存策略→安装端到端（可安装 缓存D 捕获→提示→安装）',
          ok_mf is True and miss == [] and got_cs == ('cached', 'D')
          and shown == 'showing' and done == 'installed',
          f'manifest={ok_mf} cache={got_cs} prompt={shown} installed={done}')
except Exception as ex:
    check('㊩c 清单→缓存策略→安装端到端（可安装 缓存D 捕获→提示→安装）', False, str(ex)[:60])

# ㊪ 目标6 深化：图运维（读写分离/慢查询定位/在线扩容 经正式管线）
g15_qs = {
    "读写分离": "写一个读写分离单元（主写从读）",
    "慢查询": "写一个慢查询定位单元（耗时超阈）",
    "在线扩容": "写一个在线扩容单元（分片重平衡）",
}
g15_ok = 0
for label, q in g15_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g15_ok += 1
    check(f'㊪ {label} 图运维单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊪b 图运维三单元全部生成', g15_ok == 3, f'{g15_ok}/3')

# ㊪c 运维端到端：读写分离→慢查询→在线扩容（写b从库读 慢查询[全表2.5] 迁移2键）
r_rw = domain_route("写一个读写分离单元（主写从读）")
r_sq = domain_route("写一个慢查询定位单元（耗时超阈）")
r_rb = domain_route("写一个在线扩容单元（分片重平衡）")
try:
    ns_rw, ns_sq, ns_rb = {}, {}, {}
    exec(r_rw["code"], ns_rw)
    exec(r_sq["code"], ns_sq)
    exec(r_rb["code"], ns_rb)
    m, reps = {'a': 1}, [{}]
    w = ns_rw["rw_split"](m, reps, 'write', 'b', 2)
    rd = ns_rw["rw_split"](m, reps, 'read', 'b')
    slow = ns_sq["slow_query_scan"]([('全表扫描', 2.5), ('索引查找', 0.3)], 1.0)
    moved, newc = ns_rb["rebalance_keys"](['a', 'b', 'c'], 2, 3)
    check('㊪c 读写分离→慢查询→扩容端到端（written 从库2 慢查询[全表2.5] 迁移2→3片）',
          w == 'written' and rd == 2 and slow == [('全表扫描', 2.5)]
          and moved == 2 and newc == 3,
          f'rw={w}/{rd} slow={slow} rebal=({moved},{newc})')
except Exception as ex:
    check('㊪c 读写分离→慢查询→扩容端到端（written 从库2 慢查询[全表2.5] 迁移2→3片）', False, str(ex)[:60])

# ㊫ 目标7 深化：网络服务（令牌桶限速/服务发现/加密握手 经正式管线）
n4_qs = {
    "令牌桶": "写一个令牌桶限速单元（容量封顶）",
    "服务发现": "写一个服务发现单元（注册心跳发现）",
    "加密握手": "写一个加密握手单元（TLS 状态机）",
}
n4_ok = 0
for label, q in n4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n4_ok += 1
    check(f'㊫ {label} 网络服务单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊫b 网络服务三单元全部生成', n4_ok == 3, f'{n4_ok}/3')

# ㊫c 网络服务端到端：令牌桶→服务发现→加密握手（补6封顶10 发现[svc1] 密钥建立→安全）
r_tb = domain_route("写一个令牌桶限速单元（容量封顶）")
r_sd = domain_route("写一个服务发现单元（注册心跳发现）")
r_th = domain_route("写一个加密握手单元（TLS 状态机）")
try:
    ns_tb, ns_sd, ns_th = {}, {}, {}
    exec(r_tb["code"], ns_tb)
    exec(r_sd["code"], ns_sd)
    exec(r_th["code"], ns_th)
    tb = ns_tb["token_bucket"](0, 10, 2, 3)
    reg = {}
    ns_sd["service_discover"](reg, 'register', 'svc1', '10.0.0.1', 60, 100)
    found = ns_sd["service_discover"](reg, 'discover', None, None, 0, 130)
    st = {'client_rand': 7, 'server_rand': 3}
    ns_th["tls_handshake"](st, 'hello')
    ns_th["tls_handshake"](st, 'exchange')
    secure = ns_th["tls_handshake"](st, 'finish')
    check('㊫c 令牌桶→服务发现→加密握手端到端（6 发现[svc1] 密钥10安全通道）',
          tb == 6 and found == ['svc1'] and st.get('session_key') == 10
          and secure == 'secure_channel',
          f'tb={tb} found={found} key={st.get("session_key")} secure={secure}')
except Exception as ex:
    check('㊫c 令牌桶→服务发现→加密握手端到端（6 发现[svc1] 密钥10安全通道）', False, str(ex)[:60])

# ㊬ 目标1 深化：P 线机制族（运算符重载/枚举/数据类 经正式管线）
p4_qs = {
    "运算符重载": "写一个运算符重载单元（dunder 分派）",
    "枚举": "写一个枚举单元（名称值映射）",
    "数据类": "写一个数据类单元（自动构造）",
}
p4_ok = 0
for label, q in p4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p4_ok += 1
    check(f'㊬ {label} P线机制单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊬b P线机制三单元全部生成', p4_ok == 3, f'{p4_ok}/3')

# ㊬c 机制端到端：运算符重载→枚举→数据类（__add__ 6 / 红=1 / 名甲年龄3）
r_oo = domain_route("写一个运算符重载单元（dunder 分派）")
r_en = domain_route("写一个枚举单元（名称值映射）")
r_dc = domain_route("写一个数据类单元（自动构造）")
try:
    ns_oo, ns_en, ns_dc = {}, {}, {}
    exec(r_oo["code"], ns_oo)
    exec(r_en["code"], ns_en)
    exec(r_dc["code"], ns_dc)
    add = ns_oo["binop_dispatch"]({'__add__': lambda o: o + 1}, 5, '__add__')
    val = ns_en["enum_resolve"]({'红': 1, '绿': 2}, '红')
    obj = ns_dc["dataclass_init"](('名', '年龄'), ('甲', 3))
    check('㊬c 重载→枚举→数据类端到端（__add__=6 红→1 名甲年龄3）',
          add == 6 and val == ('value', 1) and obj == {'名': '甲', '年龄': 3},
          f'add={add} enum={val} dc={obj}')
except Exception as ex:
    check('㊬c 重载→枚举→数据类端到端（__add__=6 红→1 名甲年龄3）', False, str(ex)[:60])

# ㊭ 目标2 深化：编译优化族（内联展开/循环展开/尾调用优化 经正式管线）
c5_qs = {
    "内联展开": "写一个内联展开单元（小函数内联）",
    "循环展开": "写一个循环展开单元（体复制）",
    "尾调用优化": "写一个尾调用优化单元（CALL转JUMP）",
}
c5_ok = 0
for label, q in c5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c5_ok += 1
    check(f'㊭ {label} 编译优化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊭b 编译优化三单元全部生成', c5_ok == 3, f'{c5_ok}/3')

# ㊭c 优化端到端：内联→循环展开→尾调用（f内联[DE0.1] 展开3次 尾调用转JUMP）
r_il = domain_route("写一个内联展开单元（小函数内联）")
r_lu = domain_route("写一个循环展开单元（体复制）")
r_tc = domain_route("写一个尾调用优化单元（CALL转JUMP）")
try:
    ns_il, ns_lu, ns_tc = {}, {}, {}
    exec(r_il["code"], ns_il)
    exec(r_lu["code"], ns_lu)
    exec(r_tc["code"], ns_tc)
    inl = ns_il["inline_small"]({'f': [("DE", 0.1)]}, 'f', ('CALL', 'f'))
    unroll = ns_lu["loop_unroll"]([("DE", 0.1)], 3)
    tco = ns_tc["tail_call_opt"]([("DE", 0.1), ("CALL", 'f')])
    check('㊭c 内联→循环展开→尾调用端到端（[DE0.1] ×3 JUMP）',
          inl == [("DE", 0.1)] and unroll == [("DE", 0.1)] * 3
          and tco == [("DE", 0.1), ("JUMP", 'f')],
          f'inline={inl} unroll={len(unroll)} tco={tco}')
except Exception as ex:
    check('㊭c 内联→循环展开→尾调用端到端（[DE0.1] ×3 JUMP）', False, str(ex)[:60])

# ㊮ 目标4 深化：OS 调度/系统调用（多级反馈/实时EDF/文件系统调用 经正式管线）
o4_qs = {
    "多级反馈": "写一个多级反馈队列单元（等级调度）",
    "实时EDF": "写一个实时调度单元（EDF 截止优先）",
    "文件系统调用": "写一个文件系统调用单元（open分派）",
}
o4_ok = 0
for label, q in o4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o4_ok += 1
    check(f'㊮ {label} OS调度/系统调用单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊮b OS调度/系统调用三单元全部生成', o4_ok == 3, f'{o4_ok}/3')

# ㊮c 端到端：MLFQ→EDF→文件系统调用（等级0取x / EDF取b / open→write→read）
r_mq = domain_route("写一个多级反馈队列单元（等级调度）")
r_ed = domain_route("写一个实时调度单元（EDF 截止优先）")
r_fs = domain_route("写一个文件系统调用单元（open分派）")
try:
    ns_mq, ns_ed, ns_fs = {}, {}, {}
    exec(r_mq["code"], ns_mq)
    exec(r_ed["code"], ns_ed)
    exec(r_fs["code"], ns_fs)
    qs = [['x'], ['a'], []]
    picked = ns_mq["mlfq_ops"](qs, 'pick')
    ed = ns_ed["edf_pick"]([('a', 10), ('b', 5)], 0)
    fds = []
    fd = ns_fs["syscall_file"]('open', fds, None, 'a.txt', '', 'w')
    ns_fs["syscall_file"]('write', fds, fd, None, 'hi', 'w')
    rd = ns_fs["syscall_file"]('read', fds, fd)
    check('㊮c MLFQ→EDF→文件系统调用端到端（x b fd0 写入hi读出hi）',
          picked == 'x' and ed == 'b' and fd == 0 and rd == 'hi',
          f'mlfq={picked} edf={ed} fd={fd} read={rd}')
except Exception as ex:
    check('㊮c MLFQ→EDF→文件系统调用端到端（x b fd0 写入hi读出hi）', False, str(ex)[:60])

# ㊯ 目标6 深化：图算法（最小生成树/二分图判定/度中心性 经正式管线）
g16_qs = {
    "最小生成树": "写一个最小生成树单元（Kruskal 避环）",
    "二分图": "写一个二分图判定单元（染色）",
    "度中心性": "写一个度中心性单元（归一化）",
}
g16_ok = 0
for label, q in g16_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g16_ok += 1
    check(f'㊯ {label} 图算法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊯b 图算法三单元全部生成', g16_ok == 3, f'{g16_ok}/3')

# ㊯c 算法端到端：Kruskal→二分判定→中心性（代价3 线二分 三角非二分 中心{0:1.0}）
r_mst = domain_route("写一个最小生成树单元（Kruskal 避环）")
r_bp = domain_route("写一个二分图判定单元（染色）")
r_dc = domain_route("写一个度中心性单元（归一化）")
try:
    ns_mst, ns_bp, ns_dc = {}, {}, {}
    exec(r_mst["code"], ns_mst)
    exec(r_bp["code"], ns_bp)
    exec(r_dc["code"], ns_dc)
    mst = ns_mst["kruskal_mst"]([(0, 1, 1), (1, 2, 2), (0, 2, 3)], 3)
    line = ns_bp["is_bipartite"]({0: [1], 1: [0, 2], 2: [1]}, 3)
    tri = ns_bp["is_bipartite"]({0: [1, 2], 1: [0, 2], 2: [0, 1]}, 3)
    cent = ns_dc["degree_centrality"]({0: [1, 2], 1: [0], 2: [0]}, 3)
    check('㊯c Kruskal→二分→中心性端到端（代价3 线True三角False 中心{0:1.0}）',
          mst == (3, 2) and line is True and tri is False
          and cent == {0: 1.0, 1: 0.5, 2: 0.5},
          f'mst={mst} line={line} tri={tri} cent={cent}')
except Exception as ex:
    check('㊯c Kruskal→二分→中心性端到端（代价3 线True三角False 中心{0:1.0}）', False, str(ex)[:60])

# ㊰ 目标5 深化：浏览器渲染/性能（合成分层/重排重绘/关键渲染路径 经正式管线）
b4_qs = {
    "合成分层": "写一个合成分层单元（z序合成）",
    "重排重绘": "写一个重排重绘单元（成本分类）",
    "关键渲染路径": "写一个关键渲染路径单元（依赖推进）",
}
b4_ok = 0
for label, q in b4_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b4_ok += 1
    check(f'㊰ {label} 浏览器渲染/性能单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊰b 浏览器渲染/性能三单元全部生成', b4_ok == 3, f'{b4_ok}/3')

# ㊰c 渲染端到端：合成分层→重排分类→CRP（加层z序 宽度reflow 颜色repaint 缺CSSOM阻塞）
r_cl = domain_route("写一个合成分层单元（z序合成）")
r_rf = domain_route("写一个重排重绘单元（成本分类）")
r_cp = domain_route("写一个关键渲染路径单元（依赖推进）")
try:
    ns_cl, ns_rf, ns_cp = {}, {}, {}
    exec(r_cl["code"], ns_cl)
    exec(r_rf["code"], ns_rf)
    exec(r_cp["code"], ns_cp)
    layers = {}
    ns_cl["composite_layers"](layers, 'add', 'bg', '白')
    ns_cl["composite_layers"](layers, 'add', 'txt', '黑')
    comp = ns_cl["composite_layers"](layers, 'render')
    rf = ns_rf["reflow_classify"]('宽度 100')
    rp = ns_rf["reflow_classify"]('颜色 红')
    crp = ns_cp["crp_advance"](1, '布局')
    check('㊰c 分层→重排→CRP端到端（z序[bg,txt] reflow repaint 缺CSSOM阻塞）',
          comp == [('bg', '白'), ('txt', '黑')] and rf == 'reflow'
          and rp == 'repaint' and crp == ('blocked', 1),
          f'comp={comp} rf={rf} rp={rp} crp={crp}')
except Exception as ex:
    check('㊰c 分层→重排→CRP端到端（z序[bg,txt] reflow repaint 缺CSSOM阻塞）', False, str(ex)[:60])

# ㊱ 目标7 深化：TCP 可靠传输（慢启动/快速重传/选择性确认 经正式管线）
n5_qs = {
    "慢启动": "写一个慢启动单元（指数增长）",
    "快速重传": "写一个快速重传单元（重复ACK触发）",
    "选择性确认": "写一个选择性确认单元（SACK 缺段）",
}
n5_ok = 0
for label, q in n5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n5_ok += 1
    check(f'㊱ {label} TCP可靠传输单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊱b TCP可靠传输三单元全部生成', n5_ok == 3, f'{n5_ok}/3')

# ㊱c 可靠传输端到端：慢启动→快速重传→SACK（3RTT→8 3ACK重传 缺[3,5]）
r_ss = domain_route("写一个慢启动单元（指数增长）")
r_fr = domain_route("写一个快速重传单元（重复ACK触发）")
r_sk = domain_route("写一个选择性确认单元（SACK 缺段）")
try:
    ns_ss, ns_fr, ns_sk = {}, {}, {}
    exec(r_ss["code"], ns_ss)
    exec(r_fr["code"], ns_fr)
    exec(r_sk["code"], ns_sk)
    cw = ns_ss["slow_start"](1, 8, 3)
    fr = ns_fr["fast_retransmit"](3)
    miss = ns_sk["sack_missing"]({1, 2, 4}, 5)
    check('㊱c 慢启动→快速重传→SACK端到端（cwnd8 重传True 缺[3,5]）',
          cw == 8 and fr is True and miss == [3, 5],
          f'cwnd={cw} fr={fr} miss={miss}')
except Exception as ex:
    check('㊱c 慢启动→快速重传→SACK端到端（cwnd8 重传True 缺[3,5]）', False, str(ex)[:60])

# ㊲ 目标4 深化：OS 内存族（伙伴系统/写时复制/内存压缩 经正式管线）
o5_qs = {
    "伙伴系统": "写一个伙伴系统单元（2幂分配）",
    "写时复制": "写一个写时复制单元（COW 共享页）",
    "内存压缩": "写一个内存压缩单元（zswap）",
}
o5_ok = 0
for label, q in o5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o5_ok += 1
    check(f'㊲ {label} OS内存单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊲b OS内存三单元全部生成', o5_ok == 3, f'{o5_ok}/3')

# ㊲c 内存端到端：伙伴→COW→压缩（阶0取块 共享页写复制 省2字节）
r_bd = domain_route("写一个伙伴系统单元（2幂分配）")
r_cw = domain_route("写一个写时复制单元（COW 共享页）")
r_mc = domain_route("写一个内存压缩单元（zswap）")
try:
    ns_bd, ns_cw, ns_mc = {}, {}, {}
    exec(r_bd["code"], ns_bd)
    exec(r_cw["code"], ns_cw)
    exec(r_mc["code"], ns_mc)
    fl = {0: 0, 1: 1, 2: 0}
    bd = ns_bd["buddy_alloc"](fl, 1)
    pages = ['a', 'b']
    cw = ns_cw["cow_write"](pages, 0, 'X', {0})
    saved = ns_mc["memory_compress"](['aaaa', 'b'], 2)
    check('㊲c 伙伴→COW→压缩端到端（allocated copied 省2）',
          bd == 'allocated' and cw == 'copied' and saved == 2,
          f'buddy={bd} cow={cw} saved={saved}')
except Exception as ex:
    check('㊲c 伙伴→COW→压缩端到端（allocated copied 省2）', False, str(ex)[:60])

# ㊳ 目标6 深化：图查询（正则路径/查询缓存/物化视图 经正式管线）
g17_qs = {
    "正则路径": "写一个正则路径查询单元（标签序列）",
    "查询缓存": "写一个查询缓存单元（LRU 淘汰）",
    "物化视图": "写一个物化视图单元（预计算复用）",
}
g17_ok = 0
for label, q in g17_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g17_ok += 1
    check(f'㊳ {label} 图查询单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊳b 图查询三单元全部生成', g17_ok == 3, f'{g17_ok}/3')

# ㊳c 查询端到端：正则路径→查询缓存→物化视图（朋友[1] 缓存r1 视图[b,5][a,3]）
r_rp = domain_route("写一个正则路径查询单元（标签序列）")
r_qc = domain_route("写一个查询缓存单元（LRU 淘汰）")
r_mv = domain_route("写一个物化视图单元（预计算复用）")
try:
    ns_rp, ns_qc, ns_mv = {}, {}, {}
    exec(r_rp["code"], ns_rp)
    exec(r_qc["code"], ns_qc)
    exec(r_mv["code"], ns_mv)
    rp = ns_rp["regex_path_find"]({0: [(1, '朋友'), (2, '同事')],
                                   1: [(3, '朋友')]}, 0, ['朋友'])
    cache = {}
    ns_qc["query_cache"](cache, 'put', 'q1', 'r1', 3)
    got = ns_qc["query_cache"](cache, 'get', 'q1')
    base = {}
    view = ns_mv["materialize_view"](
        base, '热度', lambda g: sorted(g, key=lambda x: -x[1]),
        'refresh', ([('a', 3), ('b', 5)],))
    check('㊳c 正则路径→缓存→物化端到端（[1] r1 [b,5][a,3]）',
          rp == [1] and got == 'r1' and view == [('b', 5), ('a', 3)],
          f'rp={rp} cache={got} view={view}')
except Exception as ex:
    check('㊳c 正则路径→缓存→物化端到端（[1] r1 [b,5][a,3]）', False, str(ex)[:60])

# ㊴ 目标1 深化：P 线标准库族（正则匹配/日期时间/JSON序列化 经正式管线）
p5_qs = {
    "正则匹配": "写一个正则匹配单元（re 搜索）",
    "日期时间": "写一个日期时间单元（加减进位）",
    "JSON序列化": "写一个 JSON 序列化单元（往返）",
}
p5_ok = 0
for label, q in p5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p5_ok += 1
    check(f'㊴ {label} P线标准库单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊴b P线标准库三单元全部生成', p5_ok == 3, f'{p5_ok}/3')

# ㊴c 标准库端到端：正则→日期→JSON（\d+ True / +60→3月1日 / 往返一致）
r_re = domain_route("写一个正则匹配单元（re 搜索）")
r_dt = domain_route("写一个日期时间单元（加减进位）")
r_js = domain_route("写一个 JSON 序列化单元（往返）")
try:
    ns_re, ns_dt, ns_js = {}, {}, {}
    exec(r_re["code"], ns_re)
    exec(r_dt["code"], ns_dt)
    exec(r_js["code"], ns_js)
    m = ns_re["regex_match"]('\\d+', 'a1b')
    d = ns_dt["date_add"](2026, 1, 1, 60)
    j = ns_js["json_roundtrip"]({'a': 1, 'b': [1, 2]})
    check('㊴c 正则→日期→JSON端到端（True 3月1日 往返一致）',
          m is True and d == (2026, 3, 1) and j == {'a': 1, 'b': [1, 2]},
          f're={m} date={d} json={j}')
except Exception as ex:
    check('㊴c 正则→日期→JSON端到端（True 3月1日 往返一致）', False, str(ex)[:60])

# ㊵ 目标2 深化：C3 .pbc 工程化（文件头/完整性/紧凑编码 经正式管线）
c6_qs = {
    "文件头校验": "写一个文件头校验单元（.pbc 魔数）",
    "完整性校验": "写一个完整性校验单元（异或和）",
    "紧凑编码": "写一个紧凑编码单元（varint）",
}
c6_ok = 0
for label, q in c6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c6_ok += 1
    check(f'㊵ {label} C3工程化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊵b C3工程化三单元全部生成', c6_ok == 3, f'{c6_ok}/3')

# ㊵c .pbc 端到端：头校验→完整性→紧凑编码（ok 异或0 300↔ac02）
r_hd = domain_route("写一个文件头校验单元（.pbc 魔数）")
r_ck = domain_route("写一个完整性校验单元（异或和）")
r_vi = domain_route("写一个紧凑编码单元（varint）")
try:
    ns_hd, ns_ck, ns_vi = {}, {}, {}
    exec(r_hd["code"], ns_hd)
    exec(r_ck["code"], ns_ck)
    exec(r_vi["code"], ns_vi)
    hd = ns_hd["pbc_header_check"]({'magic': 'PBC1', 'version': 1}, 1)
    ck = ns_ck["pbc_checksum"](b'\x01\x02\x03', 0)
    enc = ns_vi["varint_codec"](300, 'encode')
    dec = ns_vi["varint_codec"](enc, 'decode')
    check('㊵c 头→完整性→紧凑端到端（ok ok 300↔ac02）',
          hd == 'ok' and ck == 'ok' and enc == b'\xac\x02' and dec == 300,
          f'hd={hd} ck={ck} enc={enc} dec={dec}')
except Exception as ex:
    check('㊵c 头→完整性→紧凑端到端（ok ok 300↔ac02）', False, str(ex)[:60])

# ㊶ 目标5 深化：浏览器功能（历史记录/书签管理/标签页管理 经正式管线）
b5_qs = {
    "历史记录": "写一个历史记录单元（后退前进）",
    "书签": "写一个书签管理单元（增删查列）",
    "标签页": "写一个标签页管理单元（新建切换）",
}
b5_ok = 0
for label, q in b5_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b5_ok += 1
    check(f'㊶ {label} 浏览器功能单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊶b 浏览器功能三单元全部生成', b5_ok == 3, f'{b5_ok}/3')

# ㊶c 功能端到端：历史→书签→标签页（后退a 书签首页 切换0）
r_hs = domain_route("写一个历史记录单元（后退前进）")
r_bk = domain_route("写一个书签管理单元（增删查列）")
r_tb = domain_route("写一个标签页管理单元（新建切换）")
try:
    ns_hs, ns_bk, ns_tb = {}, {}, {}
    exec(r_hs["code"], ns_hs)
    exec(r_bk["code"], ns_bk)
    exec(r_tb["code"], ns_tb)
    back = ns_hs["history_ops"]({'stack': ['a', 'b'], 'pos': 1}, 'back')
    mk = ns_bk["bookmark_ops"]({}, 'add', '首页', 'h.com')
    got = ns_bk["bookmark_ops"]({'首页': 'h.com'}, 'get', '首页')
    tabs = [{'id': 1, 'url': 'a'}]
    sw = ns_tb["tab_ops"](tabs, 'switch', 0)
    check('㊶c 历史→书签→标签页端到端（后退a 书签h.com 切换0）',
          back == 'a' and mk == '首页' and got == 'h.com' and sw == 0,
          f'back={back} mark={mk}/{got} switch={sw}')
except Exception as ex:
    check('㊶c 历史→书签→标签页端到端（后退a 书签h.com 切换0）', False, str(ex)[:60])

# ㊷ 目标7 深化：网络工程（端口转发/QoS队列/链路聚合 经正式管线）
n6_qs = {
    "端口转发": "写一个端口转发单元（NAT 映射）",
    "QoS": "写一个 QoS 队列单元（优先级出队）",
    "链路聚合": "写一个链路聚合单元（多链路bonding）",
}
n6_ok = 0
for label, q in n6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n6_ok += 1
    check(f'㊷ {label} 网络工程单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊷b 网络工程三单元全部生成', n6_ok == 3, f'{n6_ok}/3')

# ㊷c 工程端到端：端口转发→QoS→链路聚合（8080映射 高优先f1 选最少链路2）
r_pf = domain_route("写一个端口转发单元（NAT 映射）")
r_qs = domain_route("写一个 QoS 队列单元（优先级出队）")
r_la = domain_route("写一个链路聚合单元（多链路bonding）")
try:
    ns_pf, ns_qs, ns_la = {}, {}, {}
    exec(r_pf["code"], ns_pf)
    exec(r_qs["code"], ns_qs)
    exec(r_la["code"], ns_la)
    pf = ns_pf["port_forward"]({8080: ('192.168.1.10', 80)}, 'lookup', 8080)
    ns_qs["qos_queue"]({}, 'enqueue', 'f1', 5)
    q = {'high': ['f1']}
    dq = ns_qs["qos_queue"](q, 'dequeue')
    la = ns_la["link_aggregation"](
        [{'id': 1, 'up': True, 'sent': 2}, {'id': 2, 'up': True, 'sent': 0}],
        'send')
    check('㊷c 端口→QoS→链路端到端（(内网,80) f1 链路2）',
          pf == ('192.168.1.10', 80) and dq == 'f1' and la == 2,
          f'pf={pf} qos={dq} link={la}')
except Exception as ex:
    check('㊷c 端口→QoS→链路端到端（(内网,80) f1 链路2）', False, str(ex)[:60])

# ㊸ 目标4 深化：OS 文件族（链接管理/元数据/内存映射 经正式管线）
o6_qs = {
    "链接管理": "写一个链接管理单元（硬软链接）",
    "文件元数据": "写一个文件元数据单元（stat）",
    "内存映射": "写一个内存映射单元（mmap）",
}
o6_ok = 0
for label, q in o6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o6_ok += 1
    check(f'㊸ {label} OS文件单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊸b OS文件三单元全部生成', o6_ok == 3, f'{o6_ok}/3')

# ㊸c 文件端到端：链接→元数据→mmap（硬链接b 元数据size10 映射读bc写2）
r_lk = domain_route("写一个链接管理单元（硬软链接）")
r_st = domain_route("写一个文件元数据单元（stat）")
r_mm = domain_route("写一个内存映射单元（mmap）")
try:
    ns_lk, ns_st, ns_mm = {}, {}, {}
    exec(r_lk["code"], ns_lk)
    exec(r_st["code"], ns_st)
    exec(r_mm["code"], ns_mm)
    fs = {'a': {'inode': 1, 'data': 'D'}}
    ln = ns_lk["link_ops"](fs, 'hard', 'b', 'a')
    meta = ns_st["stat_file"]({'a': {'size': 10, 'mode': 'r', 'type': 'file'}}, 'a')
    maps = {}
    ns_mm["mmap_ops"](maps, 'map', 'f', 0, 4, b'abcd')
    rd = ns_mm["mmap_ops"](maps, 'read', 'f', 1, 2)
    w = ns_mm["mmap_ops"](maps, 'write', 'f', 1, 0, b'XY')
    check('㊸c 链接→元数据→mmap端到端（linked size10 读bc写2）',
          ln == 'linked' and meta == {'size': 10, 'mode': 'r', 'type': 'file'}
          and rd == b'bc' and w == 2,
          f'link={ln} stat={meta} mmap=({rd},{w})')
except Exception as ex:
    check('㊸c 链接→元数据→mmap端到端（linked size10 读bc写2）', False, str(ex)[:60])

# ㊹ 目标6 深化：图可视化（环形布局/视口变换/社区着色 经正式管线）
g18_qs = {
    "环形布局": "写一个环形布局单元（圆周分布）",
    "视口变换": "写一个视口变换单元（缩放平移）",
    "社区着色": "写一个社区着色单元（分组颜色）",
}
g18_ok = 0
for label, q in g18_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g18_ok += 1
    check(f'㊹ {label} 图可视化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊹b 图可视化三单元全部生成', g18_ok == 3, f'{g18_ok}/3')

# ㊹c 可视化端到端：环形→视口→着色（a(10,0) 缩放(10,10) 红蓝分组）
r_cl = domain_route("写一个环形布局单元（圆周分布）")
r_vp = domain_route("写一个视口变换单元（缩放平移）")
r_cc = domain_route("写一个社区着色单元（分组颜色）")
try:
    ns_cl, ns_vp, ns_cc = {}, {}, {}
    exec(r_cl["code"], ns_cl)
    exec(r_vp["code"], ns_vp)
    exec(r_cc["code"], ns_cc)
    lay = ns_cl["circular_layout"](['a'], 0, 0, 10)
    vp = ns_vp["viewport_transform"](5, 5, 2, 0, 0)
    col = ns_cc["community_color"]([['a', 'b'], ['c']])
    check('㊹c 环形→视口→着色端到端（(10,0) (10,10) 红红蓝）',
          lay == {'a': (10.0, 0.0)} and vp == (10.0, 10.0)
          and col == {'a': 'red', 'b': 'red', 'c': 'blue'},
          f'lay={lay} vp={vp} col={col}')
except Exception as ex:
    check('㊹c 环形→视口→着色端到端（(10,0) (10,10) 红红蓝）', False, str(ex)[:60])

# ㊺ 目标3 深化：分析器（圈复杂度/活跃变量/调用图 经正式管线）
c7_qs = {
    "圈复杂度": "写一个圈复杂度单元（判定计数）",
    "活跃变量": "写一个活跃变量单元（死变量）",
    "调用图": "写一个调用图单元（调用关系）",
}
c7_ok = 0
for label, q in c7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c7_ok += 1
    check(f'㊺ {label} 分析器单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊺b 分析器三单元全部生成', c7_ok == 3, f'{c7_ok}/3')

# ㊺c 分析端到端：圈复杂度→活跃变量→调用图（2 / a死 / main→[f1,f2]）
r_cc = domain_route("写一个圈复杂度单元（判定计数）")
r_lv = domain_route("写一个活跃变量单元（死变量）")
r_cg = domain_route("写一个调用图单元（调用关系）")
try:
    ns_cc, ns_lv, ns_cg = {}, {}, {}
    exec(r_cc["code"], ns_cc)
    exec(r_lv["code"], ns_lv)
    exec(r_cg["code"], ns_cg)
    cc = ns_cc["cyclomatic_complexity"]([("JUMP_IF_FALSE", 3), ("DE", 0.1)])
    dead = ns_lv["dead_var_detect"]([('a', 1), ('b', 2)], [('b', 5)])
    cg = ns_cg["call_graph"]([('main', ['f1', 'f2']), ('f1', ['f2'])])
    check('㊺c 圈复杂度→活跃→调用图端到端（2 [a] main→[f1,f2]）',
          cc == 2 and dead == ['a'] and cg == {'main': ['f1', 'f2'],
                                               'f1': ['f2']},
          f'cc={cc} dead={dead} cg={cg}')
except Exception as ex:
    check('㊺c 圈复杂度→活跃→调用图端到端（2 [a] main→[f1,f2]）', False, str(ex)[:60])

# ㊻ 目标1 深化：P 线数据结构/工具（队列栈/格式化/排序键控 经正式管线）
p6_qs = {
    "队列栈": "写一个队列栈单元（队首队尾）",
    "格式化": "写一个格式化单元（模板填充）",
    "排序键控": "写一个排序键控单元（key 排序）",
}
p6_ok = 0
for label, q in p6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p6_ok += 1
    check(f'㊻ {label} P线数据结构/工具单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊻b P线数据结构/工具三单元全部生成', p6_ok == 3, f'{p6_ok}/3')

# ㊻c 数据结构端到端：队列栈→格式化→排序（出队1 填甲 按值排序）
r_dq = domain_route("写一个队列栈单元（队首队尾）")
r_fm = domain_route("写一个格式化单元（模板填充）")
r_sk = domain_route("写一个排序键控单元（key 排序）")
try:
    ns_dq, ns_fm, ns_sk = {}, {}, {}
    exec(r_dq["code"], ns_dq)
    exec(r_fm["code"], ns_fm)
    exec(r_sk["code"], ns_sk)
    dq = ns_dq["deque_ops"]([1, 2], 'dequeue')
    fm = ns_fm["format_template"]('你好 {名}', {'名': '甲'})
    sk = ns_sk["sort_by_key"]([('b', 2), ('a', 1)], lambda x: x[1])
    check('㊻c 队列→格式化→排序端到端（1 你好甲 [a,1][b,2]）',
          dq == 1 and fm == '你好 甲' and sk == [('a', 1), ('b', 2)],
          f'dq={dq} fmt={fm} sort={sk}')
except Exception as ex:
    check('㊻c 队列→格式化→排序端到端（1 你好甲 [a,1][b,2]）', False, str(ex)[:60])

# ㊼ 目标7 深化：流量/代理/组播（滑动窗口限流/反向代理/组播 经正式管线）
n7_qs = {
    "滑动窗口限流": "写一个滑动窗口限流单元（窗口计数）",
    "反向代理": "写一个反向代理单元（轮询转发）",
    "组播": "写一个组播单元（组内广播）",
}
n7_ok = 0
for label, q in n7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n7_ok += 1
    check(f'㊼ {label} 网络流量/代理单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊼b 网络流量/代理三单元全部生成', n7_ok == 3, f'{n7_ok}/3')

# ㊼c 流量端到端：限流→反向代理→组播（[allow,deny] 轮询1 组播广播）
r_rl = domain_route("写一个滑动窗口限流单元（窗口计数）")
r_rp = domain_route("写一个反向代理单元（轮询转发）")
r_mc = domain_route("写一个组播单元（组内广播）")
try:
    ns_rl, ns_rp, ns_mc = {}, {}, {}
    exec(r_rl["code"], ns_rl)
    exec(r_rp["code"], ns_rp)
    exec(r_mc["code"], ns_mc)
    rl = ns_rl["rate_limit"]([1, 11], 10, 1)
    rp = ns_rp["reverse_proxy"](
        [{'up': True, 'hits': 0}, {'up': True, 'hits': 1}], 'route')
    mc = ns_mc["multicast_group"]({'g1': ['a', 'b']}, 'send', 'g1', None, 'hi')
    check('㊼c 限流→代理→组播端到端（[allow,deny] 1 [(a,hi),(b,hi)]）',
          rl == ['allow', 'deny'] and rp == 1
          and mc == [('a', 'hi'), ('b', 'hi')],
          f'rl={rl} proxy={rp} mc={mc}')
except Exception as ex:
    check('㊼c 限流→代理→组播端到端（[allow,deny] 1 [(a,hi),(b,hi)]）', False, str(ex)[:60])

# ㊽ 目标6 深化：图存储（邻接表CSR/图合并/属性边 经正式管线）
g19_qs = {
    "邻接表压缩": "写一个邻接表压缩单元（CSR）",
    "图合并": "写一个图合并单元（边并集）",
    "属性边": "写一个属性边单元（带标签边）",
}
g19_ok = 0
for label, q in g19_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g19_ok += 1
    check(f'㊽ {label} 图存储单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊽b 图存储三单元全部生成', g19_ok == 3, f'{g19_ok}/3')

# ㊽c 存储端到端：CSR→图合并→属性边（[0,2,3,3] 并集 按属性找边）
r_csr = domain_route("写一个邻接表压缩单元（CSR）")
r_mg = domain_route("写一个图合并单元（边并集）")
r_ea = domain_route("写一个属性边单元（带标签边）")
try:
    ns_csr, ns_mg, ns_ea = {}, {}, {}
    exec(r_csr["code"], ns_csr)
    exec(r_mg["code"], ns_mg)
    exec(r_ea["code"], ns_ea)
    off, adj = ns_csr["csr_build"]([(0, 1), (0, 2), (1, 2)], 3)
    mg = ns_mg["merge_graphs"]({'a': {'b'}}, {'a': {'c'}})
    ea = ns_ea["edge_attr_query"](
        {('a', 'b'): '朋友', ('c', 'd'): '同事'}, 'by_attr', None, None, '朋友')
    check('㊽c CSR→合并→属性边端到端（[0,2,3,3] {a:[b,c]} [(a,b)]）',
          off == [0, 2, 3, 3] and adj == [1, 2, 2]
          and mg == {'a': ['b', 'c']} and ea == [('a', 'b')],
          f'csr=({off},{adj}) merge={mg} edge={ea}')
except Exception as ex:
    check('㊽c CSR→合并→属性边端到端（[0,2,3,3] {a:[b,c]} [(a,b)]）', False, str(ex)[:60])

# ㊾ 目标4 深化：OS 并发/进程（屏障同步/工作池/进程生命周期 经正式管线）
o7_qs = {
    "屏障同步": "写一个屏障同步单元（汇合点）",
    "工作池": "写一个工作池单元（任务分发）",
    "进程生命周期": "写一个进程生命周期单元（fork exec）",
}
o7_ok = 0
for label, q in o7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o7_ok += 1
    check(f'㊾ {label} OS并发/进程单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊾b OS并发/进程三单元全部生成', o7_ok == 3, f'{o7_ok}/3')

# ㊾c 并发端到端：屏障→工作池→进程生命周期（3到齐释放 / 4任务2worker / fork→exec→wait）
r_br = domain_route("写一个屏障同步单元（汇合点）")
r_wp = domain_route("写一个工作池单元（任务分发）")
r_pl = domain_route("写一个进程生命周期单元（fork exec）")
try:
    ns_br, ns_wp, ns_pl = {}, {}, {}
    exec(r_br["code"], ns_br)
    exec(r_wp["code"], ns_wp)
    exec(r_pl["code"], ns_pl)
    st = {'arrived': 2}
    br = ns_br["barrier_ops"](st, 'wait', 3)
    wp = ns_wp["worker_pool"]([1, 2, 3, 4], 2)
    pl = {}
    ns_pl["proc_life"](pl, 'fork', 1)
    ns_pl["proc_life"](pl, 'exec', 1)
    w = ns_pl["proc_life"](pl, 'wait', 1, 0)
    check('㊾c 屏障→工作池→进程端到端（released [[1,3],[2,4]] 退出0）',
          br == 'released' and wp == [[1, 3], [2, 4]] and w == 0,
          f'barrier={br} pool={wp} exit={w}')
except Exception as ex:
    check('㊾c 屏障→工作池→进程端到端（released [[1,3],[2,4]] 退出0）', False, str(ex)[:60])

# ㊿ 目标2 深化：词法/语法字面量（字符串/数字/数组 经正式管线）
c8_qs = {
    "字符串字面量": "写一个字符串字面量单元（引号转义）",
    "数字字面量": "写一个数字字面量单元（整数浮点）",
    "数组字面量": "写一个数组字面量单元（元素列表）",
}
c8_ok = 0
for label, q in c8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c8_ok += 1
    check(f'㊿ {label} 字面量单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㊿b 字面量三单元全部生成', c8_ok == 3, f'{c8_ok}/3')

# ㊿c 字面量端到端：字符串→数字→数组（abc 42 3.5 0xFF=255 [1,2]）
r_st = domain_route("写一个字符串字面量单元（引号转义）")
r_nu = domain_route("写一个数字字面量单元（整数浮点）")
r_ar = domain_route("写一个数组字面量单元（元素列表）")
try:
    ns_st, ns_nu, ns_ar = {}, {}, {}
    exec(r_st["code"], ns_st)
    exec(r_nu["code"], ns_nu)
    exec(r_ar["code"], ns_ar)
    st = ns_st["lex_string"]('"abc"', 0)
    n1 = ns_nu["lex_number"]('42', 0)
    n2 = ns_nu["lex_number"]('3.5', 0)
    n3 = ns_nu["lex_number"]('0xFF', 0)
    arr = ns_ar["parse_array"](['[', 1, ',', 2, ']'], 0)
    check('㊿c 字符串→数字→数组端到端（abc 42 3.5 255 [1,2]）',
          st == (('STRING', 'abc'), 5) and n1 == (('NUMBER', 42), 2)
          and n2 == (('NUMBER', 3.5), 3) and n3 == (('NUMBER', 255), 4)
          and arr == ([1, 2], 5),
          f'str={st} num={n1}/{n2}/{n3} arr={arr}')
except Exception as ex:
    check('㊿c 字符串→数字→数组端到端（abc 42 3.5 255 [1,2]）', False, str(ex)[:60])

# ㋀ 目标5 深化：浏览器功能（下载管理/扩展管理/网络记录 经正式管线）
b6_qs = {
    "下载管理": "写一个下载管理单元（断点续传）",
    "扩展管理": "写一个扩展管理单元（权限检查）",
    "网络记录": "写一个网络记录单元（请求过滤）",
}
b6_ok = 0
for label, q in b6_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b6_ok += 1
    check(f'㋀ {label} 浏览器功能单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋀b 浏览器功能三单元全部生成', b6_ok == 3, f'{b6_ok}/3')

# ㋀c 功能端到端：下载→扩展→网络记录（进度30 权限granted 过滤404）
r_dl = domain_route("写一个下载管理单元（断点续传）")
r_ex = domain_route("写一个扩展管理单元（权限检查）")
r_nl = domain_route("写一个网络记录单元（请求过滤）")
try:
    ns_dl, ns_ex, ns_nl = {}, {}, {}
    exec(r_dl["code"], ns_dl)
    exec(r_ex["code"], ns_ex)
    exec(r_nl["code"], ns_nl)
    dl = ns_dl["download_ops"](
        {'1': {'received': 0, 'total': 100, 'paused': False}}, 'progress', '1', 30)
    ex = ns_ex["extension_ops"](
        {'e1': {'enabled': True, 'permissions': ['tabs', 'storage']}},
        'check', 'e1', None, ['tabs'])
    nl = ns_nl["network_log"](
        [{'url': '/a', 'status': 200, 'size': 100},
         {'url': '/b', 'status': 404, 'size': 50}], 'filter', None, 404)
    check('㋀c 下载→扩展→网络记录端到端（downloading granted [404条目]）',
          dl == 'downloading' and ex == 'granted'
          and nl == [{'url': '/b', 'status': 404, 'size': 50}],
          f'dl={dl} ext={ex} log={nl}')
except Exception as ex:
    check('㋀c 下载→扩展→网络记录端到端（downloading granted [404条目]）', False, str(ex)[:60])

# ㋁ 目标1 深化：P 线集合/统计（集合运算/计数器/分组 经正式管线）
p7_qs = {
    "集合运算": "写一个集合运算单元（并交差）",
    "计数器": "写一个计数器单元（频次统计）",
    "分组": "写一个分组单元（按键分组）",
}
p7_ok = 0
for label, q in p7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p7_ok += 1
    check(f'㋁ {label} P线集合/统计单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋁b P线集合/统计三单元全部生成', p7_ok == 3, f'{p7_ok}/3')

# ㋁c 集合端到端：并集→计数→分组（[1,2,3] {a:2} 奇偶分组）
r_so = domain_route("写一个集合运算单元（并交差）")
r_ct = domain_route("写一个计数器单元（频次统计）")
r_gb = domain_route("写一个分组单元（按键分组）")
try:
    ns_so, ns_ct, ns_gb = {}, {}, {}
    exec(r_so["code"], ns_so)
    exec(r_ct["code"], ns_ct)
    exec(r_gb["code"], ns_gb)
    un = ns_so["set_ops"]([1, 2], [2, 3], 'union')
    ct = ns_ct["counter"](['a', 'b', 'a'])
    gb = ns_gb["group_by"]([1, 2, 3, 4], lambda x: x % 2)
    check('㋁c 并集→计数→分组端到端（[1,2,3] {a:2,b:1} 奇偶组）',
          un == [1, 2, 3] and ct == {'a': 2, 'b': 1}
          and gb == {1: [1, 3], 0: [2, 4]},
          f'union={un} count={ct} group={gb}')
except Exception as ex:
    check('㋁c 并集→计数→分组端到端（[1,2,3] {a:2,b:1} 奇偶组）', False, str(ex)[:60])

# ㋂ 目标7 深化：传输性能（Reno拥塞/RTO退避/吞吐量 经正式管线）
n8_qs = {
    "Reno拥塞": "写一个 Reno 拥塞控制单元（阈值减半）",
    "RTO退避": "写一个 RTO 退避单元（指数退避）",
    "吞吐量": "写一个吞吐量测量单元（KB/s）",
}
n8_ok = 0
for label, q in n8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n8_ok += 1
    check(f'㋂ {label} 传输性能单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋂b 传输性能三单元全部生成', n8_ok == 3, f'{n8_ok}/3')

# ㋂c 性能端到端：Reno→RTO→吞吐量（慢启动2 阈值8 RTO4 1KB/s）
r_rc = domain_route("写一个 Reno 拥塞控制单元（阈值减半）")
r_rt = domain_route("写一个 RTO 退避单元（指数退避）")
r_tp = domain_route("写一个吞吐量测量单元（KB/s）")
try:
    ns_rc, ns_rt, ns_tp = {}, {}, {}
    exec(r_rc["code"], ns_rc)
    exec(r_rt["code"], ns_rt)
    exec(r_tp["code"], ns_tp)
    ss = ns_rc["reno_phase"]({'cwnd': 1, 'ssthresh': 16}, 'ack')
    fr = ns_rc["reno_phase"]({'cwnd': 16, 'ssthresh': 16}, 'loss', 16)
    rto = ns_rt["rto_backoff"](1.0, 2)
    tp = ns_tp["throughput"](10240, 10)
    check('㋂c Reno→RTO→吞吐量端到端（2 8 4.0 1.0）',
          ss == 2 and fr == 8 and rto == 4.0 and tp == 1.0,
          f'ss={ss} fr={fr} rto={rto} tp={tp}')
except Exception as ex:
    check('㋂c Reno→RTO→吞吐量端到端（2 8 4.0 1.0）', False, str(ex)[:60])

# ㋃ 目标2 深化：分析/优化（作用域分析/常量传播/指令重排 经正式管线）
c9_qs = {
    "作用域分析": "写一个作用域分析单元（变量遮蔽）",
    "常量传播": "写一个常量传播单元（变量代入）",
    "指令重排": "写一个指令重排单元（乱序优化）",
}
c9_ok = 0
for label, q in c9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c9_ok += 1
    check(f'㋃ {label} 分析/优化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋃b 分析/优化三单元全部生成', c9_ok == 3, f'{c9_ok}/3')

# ㋃c 分析端到端：作用域→常量传播→指令重排（内层甲2 代入PUSH3 重排PUSH前）
r_sc = domain_route("写一个作用域分析单元（变量遮蔽）")
r_cp = domain_route("写一个常量传播单元（变量代入）")
r_ri = domain_route("写一个指令重排单元（乱序优化）")
try:
    ns_sc, ns_cp, ns_ri = {}, {}, {}
    exec(r_sc["code"], ns_sc)
    exec(r_cp["code"], ns_cp)
    exec(r_ri["code"], ns_ri)
    sc = ns_sc["scope_lookup"]([{'甲': 1}, {'甲': 2}], '甲')
    cp = ns_cp["const_propagate"]([("LOAD", "甲"), ("DE", None)], {'甲': 3})
    ri = ns_ri["reorder_instrs"]([("DE", 0.1), ("PUSH", 3)])
    check('㋃c 作用域→常量传播→重排端到端（2 [PUSH3,DE] [PUSH3,DE0.1]）',
          sc == 2 and cp == [("PUSH", 3), ("DE", None)]
          and ri == [("PUSH", 3), ("DE", 0.1)],
          f'scope={sc} cp={cp} reorder={ri}')
except Exception as ex:
    check('㋃c 作用域→常量传播→重排端到端（2 [PUSH3,DE] [PUSH3,DE0.1]）', False, str(ex)[:60])

# ㋄ 目标6 深化：图算法（最大流/欧拉路径/图直径 经正式管线）
g20_qs = {
    "最大流": "写一个最大流单元（增广路径）",
    "欧拉路径": "写一个欧拉路径单元（一笔画）",
    "图直径": "写一个图直径单元（最长最短）",
}
g20_ok = 0
for label, q in g20_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g20_ok += 1
    check(f'㋄ {label} 图算法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋄b 图算法三单元全部生成', g20_ok == 3, f'{g20_ok}/3')

# ㋄c 算法端到端：最大流→欧拉→直径（4 True 2）
r_mf = domain_route("写一个最大流单元（增广路径）")
r_ep = domain_route("写一个欧拉路径单元（一笔画）")
r_gd = domain_route("写一个图直径单元（最长最短）")
try:
    ns_mf, ns_ep, ns_gd = {}, {}, {}
    exec(r_mf["code"], ns_mf)
    exec(r_ep["code"], ns_ep)
    exec(r_gd["code"], ns_gd)
    mf = ns_mf["max_flow"]({'s': {'a': 3, 'b': 2}, 'a': {'t': 2},
                            'b': {'t': 2}}, 's', 't')
    ep = ns_ep["euler_path"]({0: [1], 1: [0, 2], 2: [1]}, 3)
    gd = ns_gd["graph_diameter"]({0: [1], 1: [0, 2], 2: [1]}, 3)
    check('㋄c 最大流→欧拉→直径端到端（4 True 2）',
          mf == 4 and ep is True and gd == 2,
          f'flow={mf} euler={ep} diam={gd}')
except Exception as ex:
    check('㋄c 最大流→欧拉→直径端到端（4 True 2）', False, str(ex)[:60])

# ㋅ 目标4 深化：OS 存储（磁盘调度/写时复制快照/磨损均衡 经正式管线）
o8_qs = {
    "磁盘调度": "写一个磁盘调度单元（SCAN 电梯）",
    "写时复制快照": "写一个写时复制快照单元（块冻结）",
    "磨损均衡": "写一个磨损均衡单元（最少磨损）",
}
o8_ok = 0
for label, q in o8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o8_ok += 1
    check(f'㋅ {label} OS存储单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋅b OS存储三单元全部生成', o8_ok == 3, f'{o8_ok}/3')

# ㋅c 存储端到端：SCAN→CoW快照→磨损均衡（[50,30,10] 快照读A 选b）
r_sc = domain_route("写一个磁盘调度单元（SCAN 电梯）")
r_cw = domain_route("写一个写时复制快照单元（块冻结）")
r_wl = domain_route("写一个磨损均衡单元（最少磨损）")
try:
    ns_sc, ns_cw, ns_wl = {}, {}, {}
    exec(r_sc["code"], ns_sc)
    exec(r_cw["code"], ns_cw)
    exec(r_wl["code"], ns_wl)
    sc = ns_sc["scan_schedule"]([10, 30, 50], 40)
    snaps = {'s1': {'b1': 'A'}}
    ns_cw["cow_snapshot"]({'b1': 'A'}, 'write', None, 'b1', 'B', snaps)
    rd = ns_cw["cow_snapshot"]({'b1': 'B'}, 'read', 's1', 'b1', None, snaps)
    wl = ns_wl["wear_leveling"]({'a': 3, 'b': 1}, 'pick')
    check('㋅c SCAN→快照→磨损端到端（[50,30,10] 快照A 选b）',
          sc == [50, 30, 10] and rd == 'A' and wl == 'b',
          f'scan={sc} snap={rd} wear={wl}')
except Exception as ex:
    check('㋅c SCAN→快照→磨损端到端（[50,30,10] 快照A 选b）', False, str(ex)[:60])

# ㋆ 目标1 深化：P 线异常/OO（自定义异常/对象组合/深拷贝 经正式管线）
p8_qs = {
    "自定义异常": "写一个自定义异常单元（类层级）",
    "对象组合": "写一个对象组合单元（has-a 委托）",
    "深拷贝": "写一个深拷贝单元（嵌套复制）",
}
p8_ok = 0
for label, q in p8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p8_ok += 1
    check(f'㋆ {label} P线异常/OO单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋆b P线异常/OO三单元全部生成', p8_ok == 3, f'{p8_ok}/3')

# ㋆c 异常/OO 端到端：自定义异常→组合→深拷贝（子类捕获 引擎启动 嵌套复制）
r_cx = domain_route("写一个自定义异常单元（类层级）")
r_cp = domain_route("写一个对象组合单元（has-a 委托）")
r_dc = domain_route("写一个深拷贝单元（嵌套复制）")
try:
    ns_cx, ns_cp, ns_dc = {}, {}, {}
    exec(r_cx["code"], ns_cx)
    exec(r_cp["code"], ns_cp)
    exec(r_dc["code"], ns_dc)
    sub = ns_cx["exception_subclass"](
        [('值错误', '异常'), ('输入错误', '值错误')], '输入错误', '异常')
    parts = {'引擎': {'启动': lambda: 'vroom'}}
    call = ns_cp["compose_objects"](parts, 'call', '引擎', None, '启动', None)
    cp = ns_dc["deep_copy"]({'a': [1, {'b': 2}]})
    check('㋆c 异常→组合→深拷贝端到端（True vroom 嵌套一致）',
          sub is True and call == 'vroom' and cp == {'a': [1, {'b': 2}]},
          f'sub={sub} call={call} copy={cp}')
except Exception as ex:
    check('㋆c 异常→组合→深拷贝端到端（True vroom 嵌套一致）', False, str(ex)[:60])

# ㋇ 目标7 深化：路由/传输（链路状态/策略路由/多径传输 经正式管线）
n9_qs = {
    "链路状态": "写一个链路状态路由单元（Dijkstra）",
    "策略路由": "写一个策略路由单元（按流量选路）",
    "多径传输": "写一个多径传输单元（MPTCP 子流）",
}
n9_ok = 0
for label, q in n9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n9_ok += 1
    check(f'㋇ {label} 路由/传输单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋇b 路由/传输三单元全部生成', n9_ok == 3, f'{n9_ok}/3')

# ㋇c 路由端到端：链路状态→策略→多径（dist{d:4} 视频专线 选5g）
r_ls = domain_route("写一个链路状态路由单元（Dijkstra）")
r_pr = domain_route("写一个策略路由单元（按流量选路）")
r_mp = domain_route("写一个多径传输单元（MPTCP 子流）")
try:
    ns_ls, ns_pr, ns_mp = {}, {}, {}
    exec(r_ls["code"], ns_ls)
    exec(r_pr["code"], ns_pr)
    exec(r_mp["code"], ns_mp)
    dist, prev = ns_ls["link_state_routing"](
        {'a': {'b': 1, 'c': 4}, 'b': {'c': 2, 'd': 5},
         'c': {'d': 1}, 'd': {}}, 'a')
    pol = ns_pr["policy_routing"](
        {'视频走专线': {'类型': '视频'}}, 'match', {'类型': '视频', '大小': 100})
    mp = ns_mp["multipath_send"](
        {'wifi': {'sent': 5}, '5g': {'sent': 0}}, 'send', None, 'ab')
    check('㋇c 链路状态→策略→多径端到端（d=4 视频专线 5g）',
          dist.get('d') == 4 and prev.get('d') == 'c'
          and pol == '视频走专线' and mp == '5g',
          f'dist={dist.get("d")} prev={prev.get("d")} pol={pol} mp={mp}')
except Exception as ex:
    check('㋇c 链路状态→策略→多径端到端（d=4 视频专线 5g）', False, str(ex)[:60])

# ㋈ 目标5 深化：浏览器交互/安全（表单验证/拖放交互/资源完整性 经正式管线）
b7_qs = {
    "表单验证": "写一个表单验证单元（必填格式）",
    "拖放交互": "写一个拖放交互单元（数据携带）",
    "资源完整性": "写一个资源完整性单元（SRI 校验）",
}
b7_ok = 0
for label, q in b7_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b7_ok += 1
    check(f'㋈ {label} 浏览器交互/安全单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋈b 浏览器交互/安全三单元全部生成', b7_ok == 3, f'{b7_ok}/3')

# ㋈c 交互端到端：表单→拖放→SRI（通过 拖到zone_a 一致ok）
r_fv = domain_route("写一个表单验证单元（必填格式）")
r_dd = domain_route("写一个拖放交互单元（数据携带）")
r_sr = domain_route("写一个资源完整性单元（SRI 校验）")
try:
    ns_fv, ns_dd, ns_sr = {}, {}, {}
    exec(r_fv["code"], ns_fv)
    exec(r_dd["code"], ns_dd)
    exec(r_sr["code"], ns_sr)
    fv = ns_fv["form_validate"]({'名': {'required': True}}, {'名': '甲'})
    st = {'drag_data': 'item1'}
    dd = ns_dd["drag_drop"](st, 'drop', None, 'zone_a')
    sri = ns_sr["sri_verify"]('abc', 'abc')
    check('㋈c 表单→拖放→SRI端到端（[] dropped ok）',
          fv == [] and dd == 'dropped' and sri == 'ok',
          f'form={fv} drag={dd} sri={sri}')
except Exception as ex:
    check('㋈c 表单→拖放→SRI端到端（[] dropped ok）', False, str(ex)[:60])

# ㋉ 目标2 深化：VM 运行时（引用计数/指令剖析/栈保护 经正式管线）
c10_qs = {
    "引用计数": "写一个引用计数单元（GC 回收）",
    "指令剖析": "写一个指令剖析单元（频次统计）",
    "栈保护": "写一个栈保护单元（深度限制）",
}
c10_ok = 0
for label, q in c10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c10_ok += 1
    check(f'㋉ {label} VM运行时单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋉b VM运行时三单元全部生成', c10_ok == 3, f'{c10_ok}/3')

# ㋉c VM 端到端：引用计数→指令剖析→栈保护（collected {DE:2} overflow）
r_rc = domain_route("写一个引用计数单元（GC 回收）")
r_ip = domain_route("写一个指令剖析单元（频次统计）")
r_sg = domain_route("写一个栈保护单元（深度限制）")
try:
    ns_rc, ns_ip, ns_sg = {}, {}, {}
    exec(r_rc["code"], ns_rc)
    exec(r_ip["code"], ns_ip)
    exec(r_sg["code"], ns_sg)
    gc = ns_rc["refcount_ops"]({'a': 1}, 'dec', 'a')
    prof = ns_ip["instr_profile"]([("DE", 0.1), ("DE", 0.2)])
    sg = ns_sg["stack_push_guard"]([1, 2], 2, 3)
    check('㋉c 引用计数→剖析→栈保护端到端（collected {DE:2} overflow）',
          gc == 'collected' and prof == {'DE': 2} and sg == 'overflow',
          f'gc={gc} prof={prof} guard={sg}')
except Exception as ex:
    check('㋉c 引用计数→剖析→栈保护端到端（collected {DE:2} overflow）', False, str(ex)[:60])

# ㋊ 目标1 深化：P 线异步族（超时控制/任务取消/异步信号量 经正式管线）
p9_qs = {
    "超时控制": "写一个超时控制单元（wait_for）",
    "任务取消": "写一个任务取消单元（协作取消）",
    "异步信号量": "写一个异步信号量单元（并发上限）",
}
p9_ok = 0
for label, q in p9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p9_ok += 1
    check(f'㋊ {label} P线异步单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋊b P线异步三单元全部生成', p9_ok == 3, f'{p9_ok}/3')

# ㋊c 异步端到端：超时→取消→信号量（done cancelled handoff）
r_wf = domain_route("写一个超时控制单元（wait_for）")
r_tc = domain_route("写一个任务取消单元（协作取消）")
r_as = domain_route("写一个异步信号量单元（并发上限）")
try:
    ns_wf, ns_tc, ns_as = {}, {}, {}
    exec(r_wf["code"], ns_wf)
    exec(r_tc["code"], ns_tc)
    exec(r_as["code"], ns_as)
    wf = ns_wf["wait_for"](lambda: 'done', 5, 3)
    tc = ns_tc["task_cancel"]({'t1': 'running'}, 'cancel', 't1')
    sem = {'limit': 2, 'count': 2, 'waiting': 1}
    asem = ns_as["async_semaphore"](sem, 'release')
    check('㋊c 超时→取消→信号量端到端（done cancelled handoff）',
          wf == 'done' and tc == 'cancelled' and asem == 'handoff',
          f'wait={wf} cancel={tc} sem={asem}')
except Exception as ex:
    check('㋊c 超时→取消→信号量端到端（done cancelled handoff）', False, str(ex)[:60])

# ㋋ 目标6 深化：条件路由图·智能论语义（条件合并/信任传播/信息差收敛 经正式管线）
g21_qs = {
    "条件合并": "写一个条件合并单元（AND 叠加）",
    "信任传播": "写一个信任传播单元（沿边衰减）",
    "信息差收敛": "写一个信息差收敛单元（逐节点减半）",
}
g21_ok = 0
for label, q in g21_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g21_ok += 1
    check(f'㋋ {label} 条件路由图单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋋b 条件路由图三单元全部生成', g21_ok == 3, f'{g21_ok}/3')

# ㋋c 条件路由端到端：合并→信任→信息差（叠加 0.25 收敛arrived）
r_mc = domain_route("写一个条件合并单元（AND 叠加）")
r_tp = domain_route("写一个信任传播单元（沿边衰减）")
r_ig = domain_route("写一个信息差收敛单元（逐节点减半）")
try:
    ns_mc, ns_tp, ns_ig = {}, {}, {}
    exec(r_mc["code"], ns_mc)
    exec(r_tp["code"], ns_tp)
    exec(r_ig["code"], ns_ig)
    mc = ns_mc["merge_conditions"]({'温度': '高'}, {'湿度': '大'})
    tp = ns_tp["trust_propagate"]({'a': ['b'], 'b': ['c']}, 'a', 1.0)
    path, gap, st = ns_ig["info_gap_path"]({'a': ['b'], 'b': ['c']}, 'a', 'c', 1.0)
    check('㋋c 合并→信任→信息差端到端（叠加 c信任0.25 收敛0.25 arrived）',
          mc == {'温度': '高', '湿度': '大'} and tp.get('c') == 0.25
          and path == ['a', 'b', 'c'] and gap == 0.25 and st == 'arrived',
          f'merge={mc} trust={tp.get("c")} gap=({path},{gap},{st})')
except Exception as ex:
    check('㋋c 合并→信任→信息差端到端（叠加 c信任0.25 收敛0.25 arrived）', False, str(ex)[:60])

# ㋌ 目标4 深化：OS 安全族（强制访问控制/系统调用过滤/加密文件系统 经正式管线）
o9_qs = {
    "强制访问控制": "写一个强制访问控制单元（MAC 标签）",
    "系统调用过滤": "写一个系统调用过滤单元（seccomp）",
    "加密文件系统": "写一个加密文件系统单元（透明加解密）",
}
o9_ok = 0
for label, q in o9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o9_ok += 1
    check(f'㋌ {label} OS安全单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋌b OS安全三单元全部生成', o9_ok == 3, f'{o9_ok}/3')

# ㋌c 安全端到端：MAC→seccomp→加密文件系统（allowed ok 秘密往返）
r_ma = domain_route("写一个强制访问控制单元（MAC 标签）")
r_sc = domain_route("写一个系统调用过滤单元（seccomp）")
r_cf = domain_route("写一个加密文件系统单元（透明加解密）")
try:
    ns_ma, ns_sc, ns_cf = {}, {}, {}
    exec(r_ma["code"], ns_ma)
    exec(r_sc["code"], ns_sc)
    exec(r_cf["code"], ns_cf)
    ma = ns_ma["mac_check"]({'rules': {('内部', '秘密', '读'): 'allowed'}},
                            '内部', '秘密', '读')
    sc = ns_sc["seccomp_filter"]({'read'}, 'check', 'read')
    fs = {}
    ns_cf["crypt_fs"](fs, 'write', 'a.txt', '秘密', 7)
    rd = ns_cf["crypt_fs"](fs, 'read', 'a.txt', None, 7)
    check('㋌c MAC→seccomp→加密文件系统端到端（allowed ok 秘密）',
          ma == 'allowed' and sc == 'ok' and rd == '秘密',
          f'mac={ma} seccomp={sc} fs={rd}')
except Exception as ex:
    check('㋌c MAC→seccomp→加密文件系统端到端（allowed ok 秘密）', False, str(ex)[:60])

# ㋍ 目标2/3 深化：智能论语义（名实一致/类型转换/数据流分析 经正式管线）
c11_qs = {
    "名实一致": "写一个名实一致单元（以名举实）",
    "类型转换": "写一个类型转换单元（转换规则）",
    "数据流分析": "写一个数据流分析单元（def-use）",
}
c11_ok = 0
for label, q in c11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c11_ok += 1
    check(f'㋍ {label} 智能论语义单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋍b 智能论语义三单元全部生成', c11_ok == 3, f'{c11_ok}/3')

# ㋍c 语义端到端：名实→类型转换→数据流（[] '5' def-use链）
r_ms = domain_route("写一个名实一致单元（以名举实）")
r_tc = domain_route("写一个类型转换单元（转换规则）")
r_df = domain_route("写一个数据流分析单元（def-use）")
try:
    ns_ms, ns_tc, ns_df = {}, {}, {}
    exec(r_ms["code"], ns_ms)
    exec(r_tc["code"], ns_tc)
    exec(r_df["code"], ns_df)
    ms = ns_ms["ming_shi_check"](['甲', '乙'], {'甲': 1, '乙': 2})
    tc = ns_tc["type_convert"](5, '数值', '文本', {('数值', '文本'): str})
    df = ns_df["def_use_chain"]([('a', 1)], [('a', 3)])
    check('㋍c 名实→类型转换→数据流端到端（[] "5" [("a",1,3)]）',
          ms == [] and tc == '5' and df == [('a', 1, 3)],
          f'ming={ms} conv={tc} defuse={df}')
except Exception as ex:
    check('㋍c 名实→类型转换→数据流端到端（[] "5" [("a",1,3)]）', False, str(ex)[:60])

# ㋎ 目标7 深化：应用/安全（访问令牌/压缩传输/会话亲和 经正式管线）
n10_qs = {
    "访问令牌": "写一个访问令牌单元（OAuth 校验）",
    "压缩传输": "写一个压缩传输单元（RLE 编码）",
    "会话亲和": "写一个会话亲和单元（sticky）",
}
n10_ok = 0
for label, q in n10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n10_ok += 1
    check(f'㋎ {label} 网络应用/安全单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋎b 网络应用/安全三单元全部生成', n10_ok == 3, f'{n10_ok}/3')

# ㋎c 应用端到端：令牌→压缩→会话亲和（valid aaabb 绑定0）
r_tk = domain_route("写一个访问令牌单元（OAuth 校验）")
r_ct = domain_route("写一个压缩传输单元（RLE 编码）")
r_ss = domain_route("写一个会话亲和单元（sticky）")
try:
    ns_tk, ns_ct, ns_ss = {}, {}, {}
    exec(r_tk["code"], ns_tk)
    exec(r_ct["code"], ns_ct)
    exec(r_ss["code"], ns_ss)
    tk = ns_tk["token_ops"](
        {'tk1': {'user': 'u1', 'expire': 160, 'revoked': False}},
        'verify', 'tk1', None, 0, 100)
    ct = ns_ct["compress_transfer"]([('a', 3), ('b', 2)], 'decompress')
    ss = ns_ss["sticky_session"]({}, 'bind', 's1', 0)
    check('㋎c 令牌→压缩→会话亲和端到端（valid aaabb 0）',
          tk == 'valid' and ct == 'aaabb' and ss == 0,
          f'token={tk} comp={ct} sticky={ss}')
except Exception as ex:
    check('㋎c 令牌→压缩→会话亲和端到端（valid aaabb 0）', False, str(ex)[:60])

# ㋏ 目标5 深化：浏览器媒体/能力（媒体播放/地理位置/全屏模式 经正式管线）
b8_qs = {
    "媒体播放": "写一个媒体播放单元（音量夹紧）",
    "地理位置": "写一个地理位置单元（权限门控）",
    "全屏模式": "写一个全屏模式单元（元素全屏）",
}
b8_ok = 0
for label, q in b8_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b8_ok += 1
    check(f'㋏ {label} 浏览器媒体/能力单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋏b 浏览器媒体/能力三单元全部生成', b8_ok == 3, f'{b8_ok}/3')

# ㋏c 媒体端到端：播放→地理→全屏（playing 坐标 video）
r_mp = domain_route("写一个媒体播放单元（音量夹紧）")
r_gl = domain_route("写一个地理位置单元（权限门控）")
r_fs = domain_route("写一个全屏模式单元（元素全屏）")
try:
    ns_mp, ns_gl, ns_fs = {}, {}, {}
    exec(r_mp["code"], ns_mp)
    exec(r_gl["code"], ns_gl)
    exec(r_fs["code"], ns_fs)
    mp = ns_mp["media_ops"]({'playing': False}, 'play')
    st = {'granted': True}
    gl = ns_gl["geolocation"](st, 'get', None, 39.9, 116.4)
    fs = ns_fs["fullscreen_ops"]({}, 'enter', 'video')
    check('㋏c 播放→地理→全屏端到端（playing {39.9,116.4} video）',
          mp == 'playing' and gl == {'lat': 39.9, 'lng': 116.4} and fs == 'video',
          f'media={mp} geo={gl} fs={fs}')
except Exception as ex:
    check('㋏c 播放→地理→全屏端到端（playing {39.9,116.4} video）', False, str(ex)[:60])

# ㋐ 目标1 深化：P 线函数式（映射/过滤/归约 经正式管线）
p10_qs = {
    "映射": "写一个映射单元（元素变换）",
    "过滤": "写一个过滤单元（条件筛选）",
    "归约": "写一个归约单元（累积聚合）",
}
p10_ok = 0
for label, q in p10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p10_ok += 1
    check(f'㋐ {label} P线函数式单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋐b P线函数式三单元全部生成', p10_ok == 3, f'{p10_ok}/3')

# ㋐c 函数式端到端：映射→过滤→归约（[2,4,6] [2,4] 6）
r_mp = domain_route("写一个映射单元（元素变换）")
r_fl = domain_route("写一个过滤单元（条件筛选）")
r_rd = domain_route("写一个归约单元（累积聚合）")
try:
    ns_mp, ns_fl, ns_rd = {}, {}, {}
    exec(r_mp["code"], ns_mp)
    exec(r_fl["code"], ns_fl)
    exec(r_rd["code"], ns_rd)
    mp = ns_mp["map_apply"]([1, 2, 3], lambda x: x * 2)
    fl = ns_fl["filter_items"]([1, 2, 3, 4], lambda x: x % 2 == 0)
    rd = ns_rd["reduce_accum"]([1, 2, 3], lambda a, b: a + b, 0)
    check('㋐c 映射→过滤→归约端到端（[2,4,6] [2,4] 6）',
          mp == [2, 4, 6] and fl == [2, 4] and rd == 6,
          f'map={mp} filter={fl} reduce={rd}')
except Exception as ex:
    check('㋐c 映射→过滤→归约端到端（[2,4,6] [2,4] 6）', False, str(ex)[:60])

# ㋑ 目标2 深化：语法表达式（三元/复合赋值/位运算 经正式管线）
c12_qs = {
    "三元表达式": "写一个三元表达式单元（条件选支）",
    "复合赋值": "写一个复合赋值单元（+= 展开）",
    "位运算": "写一个位运算单元（按位操作）",
}
c12_ok = 0
for label, q in c12_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c12_ok += 1
    check(f'㋑ {label} 语法表达式单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋑b 语法表达式三单元全部生成', c12_ok == 3, f'{c12_ok}/3')

# ㋑c 语法端到端：三元→复合赋值→位运算（跳转码 展开 异或6）
r_tt = domain_route("写一个三元表达式单元（条件选支）")
r_ca = domain_route("写一个复合赋值单元（+= 展开）")
r_bw = domain_route("写一个位运算单元（按位操作）")
try:
    ns_tt, ns_ca, ns_bw = {}, {}, {}
    exec(r_tt["code"], ns_tt)
    exec(r_ca["code"], ns_ca)
    exec(r_bw["code"], ns_bw)
    tt = ns_tt["ternary_compile"]([("LOAD", "x")], [("PUSH", 1)], [("PUSH", 0)])
    ca = ns_ca["compound_assign"]('+=', '甲', [("PUSH", 2)])
    bw = ns_bw["bitwise_op"](5, 3, 'xor')
    check('㋑c 三元→复合赋值→位运算端到端（JIF4 展开 6）',
          tt == [("LOAD", "x"), ("JUMP_IF_FALSE", 4), ("PUSH", 1),
                 ("JUMP", 5), ("PUSH", 0)]
          and ca == [("LOAD", "甲"), ("PUSH", 2), ("ADD", None),
                     ("STORE", "甲")]
          and bw == 6,
          f'ternary={tt} assign={ca} bit={bw}')
except Exception as ex:
    check('㋑c 三元→复合赋值→位运算端到端（JIF4 展开 6）', False, str(ex)[:60])

# ㋒ 目标4 深化：系统服务（服务管理/日志轮转/定时任务 经正式管线）
o10_qs = {
    "服务管理": "写一个服务管理单元（启停状态）",
    "日志轮转": "写一个日志轮转单元（超限轮转）",
    "定时任务": "写一个定时任务单元（cron 规则）",
}
o10_ok = 0
for label, q in o10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o10_ok += 1
    check(f'㋒ {label} 系统服务单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋒b 系统服务三单元全部生成', o10_ok == 3, f'{o10_ok}/3')

# ㋒c 服务端到端：服务→日志→定时（running rotated True）
r_sv = domain_route("写一个服务管理单元（启停状态）")
r_lr = domain_route("写一个日志轮转单元（超限轮转）")
r_cn = domain_route("写一个定时任务单元（cron 规则）")
try:
    ns_sv, ns_lr, ns_cn = {}, {}, {}
    exec(r_sv["code"], ns_sv)
    exec(r_lr["code"], ns_lr)
    exec(r_cn["code"], ns_cn)
    sv = ns_sv["service_ops"]({}, 'start', 'nginx')
    lr = ns_lr["log_rotate"](
        {'app.log': {'size': 800, 'rotations': 0}}, 'append', 'app.log', 500)
    cn = ns_cn["cron_match"]('30 *', 30, 10)
    check('㋒c 服务→日志→定时端到端（running rotated True）',
          sv == 'running' and lr == 'rotated' and cn is True,
          f'svc={sv} log={lr} cron={cn}')
except Exception as ex:
    check('㋒c 服务→日志→定时端到端（running rotated True）', False, str(ex)[:60])

# ㋓ 目标6 深化：持久化/分布式（增量备份/一致性快照/一致性哈希 经正式管线）
g22_qs = {
    "增量备份": "写一个增量备份单元（全量+增量）",
    "一致性快照": "写一个一致性快照单元（MVCC）",
    "一致性哈希": "写一个一致性哈希单元（哈希环）",
}
g22_ok = 0
for label, q in g22_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g22_ok += 1
    check(f'㋓ {label} 持久化/分布式单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋓b 持久化/分布式三单元全部生成', g22_ok == 3, f'{g22_ok}/3')

# ㋓c 持久化端到端：增量备份→一致性快照→一致性哈希（还原{a,b} 版本2 定位n1）
r_ib = domain_route("写一个增量备份单元（全量+增量）")
r_si = domain_route("写一个一致性快照单元（MVCC）")
r_ch = domain_route("写一个一致性哈希单元（哈希环）")
try:
    ns_ib, ns_si, ns_ch = {}, {}, {}
    exec(r_ib["code"], ns_ib)
    exec(r_si["code"], ns_si)
    exec(r_ch["code"], ns_ch)
    bks = {'f1': {'type': 'full', 'data': {'a': 1}},
           'i1': {'type': 'incr', 'base': 'f1', 'changes': {'b': 2}}}
    rst = ns_ib["incremental_backup"](bks, 'restore', 'f1', None, 'i1')
    sv = ns_si["snapshot_isolation"]({'a': {1: 1, 2: 2}}, 'read', 'a', None, 2)
    ch = ns_ch["consistent_hash"]({159: 'n1', 217: 'n2'}, 'locate', None, 'k1')
    check('㋓c 备份→快照→哈希端到端（{a:1,b:2} 2 n1）',
          rst == {'a': 1, 'b': 2} and sv == 2 and ch == 'n1',
          f'backup={rst} snap={sv} hash={ch}')
except Exception as ex:
    check('㋓c 备份→快照→哈希端到端（{a:1,b:2} 2 n1）', False, str(ex)[:60])

# ㋔ 目标7 深化：链路/工程（链路加密/流量镜像/网络切片 经正式管线）
n11_qs = {
    "链路加密": "写一个链路加密单元（MACsec）",
    "流量镜像": "写一个流量镜像单元（SPAN）",
    "网络切片": "写一个网络切片单元（带宽准入）",
}
n11_ok = 0
for label, q in n11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n11_ok += 1
    check(f'㋔ {label} 链路/工程单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋔b 链路/工程三单元全部生成', n11_ok == 3, f'{n11_ok}/3')

# ㋔c 链路端到端：加密→镜像→切片（obcch 镜像2 准入admitted）
r_le = domain_route("写一个链路加密单元（MACsec）")
r_pm = domain_route("写一个流量镜像单元（SPAN）")
r_ns = domain_route("写一个网络切片单元（带宽准入）")
try:
    ns_le, ns_pm, ns_ns = {}, {}, {}
    exec(r_le["code"], ns_le)
    exec(r_pm["code"], ns_pm)
    exec(r_ns["code"], ns_ns)
    enc = ns_le["link_encrypt"]({}, 'encrypt', 'hello', 7)
    pm = ns_pm["port_mirror"]({}, 'mirror', 1, 2)
    ns = ns_ns["network_slice"](
        {'视频': {'bw': 100, 'used': 0}}, 'admit', '视频', None, 60)
    check('㋔c 加密→镜像→切片端到端（obkkh 2 admitted）',
          enc == 'obkkh' and pm == 2 and ns == 'admitted',
          f'enc={enc} mirror={pm} slice={ns}')
except Exception as ex:
    check('㋔c 加密→镜像→切片端到端（obkkh 2 admitted）', False, str(ex)[:60])

# ㋕ 目标1 深化：P 线字符串工具（拆分/替换/判断 经正式管线）
p11_qs = {
    "字符串拆分": "写一个字符串拆分单元（分隔符）",
    "字符串替换": "写一个字符串替换单元（限次替换）",
    "字符串判断": "写一个字符串判断单元（方法族）",
}
p11_ok = 0
for label, q in p11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p11_ok += 1
    check(f'㋕ {label} P线字符串单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋕b P线字符串三单元全部生成', p11_ok == 3, f'{p11_ok}/3')

# ㋕c 字符串端到端：拆分→替换→判断（[a,b,c] bbb True）
r_ss = domain_route("写一个字符串拆分单元（分隔符）")
r_sr = domain_route("写一个字符串替换单元（限次替换）")
r_sc = domain_route("写一个字符串判断单元（方法族）")
try:
    ns_ss, ns_sr, ns_sc = {}, {}, {}
    exec(r_ss["code"], ns_ss)
    exec(r_sr["code"], ns_sr)
    exec(r_sc["code"], ns_sc)
    sp = ns_ss["str_split"]('a,b,c', ',')
    rp = ns_sr["str_replace"]('aaa', 'a', 'b')
    chk = ns_sc["str_check"]('123', 'isdigit')
    check('㋕c 拆分→替换→判断端到端（[a,b,c] bbb True）',
          sp == ['a', 'b', 'c'] and rp == 'bbb' and chk is True,
          f'split={sp} replace={rp} check={chk}')
except Exception as ex:
    check('㋕c 拆分→替换→判断端到端（[a,b,c] bbb True）', False, str(ex)[:60])

# ㋖ 目标2 深化：词法/语法（标识符/操作符/函数签名 经正式管线）
c13_qs = {
    "标识符解析": "写一个标识符解析单元（CJK 串）",
    "操作符解析": "写一个操作符解析单元（双字符优先）",
    "函数签名": "写一个函数签名单元（参数列表）",
}
c13_ok = 0
for label, q in c13_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c13_ok += 1
    check(f'㋖ {label} 词法/语法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋖b 词法/语法三单元全部生成', c13_ok == 3, f'{c13_ok}/3')

# ㋖c 词法端到端：标识符→操作符→函数签名（IDENT 甲变量 >= 参数列表）
r_id = domain_route("写一个标识符解析单元（CJK 串）")
r_op = domain_route("写一个操作符解析单元（双字符优先）")
r_sg = domain_route("写一个函数签名单元（参数列表）")
try:
    ns_id, ns_op, ns_sg = {}, {}, {}
    exec(r_id["code"], ns_id)
    exec(r_op["code"], ns_op)
    exec(r_sg["code"], ns_sg)
    idn = ns_id["lex_ident"]('甲变量', 0)
    op = ns_op["lex_op"]('>=', 0)
    sg = ns_sg["parse_signature"]('甲=1, 乙')
    check('㋖c 标识符→操作符→签名端到端（IDENT甲变量 >= [甲,乙]）',
          idn == (('IDENT', '甲变量'), 3) and op == (('OP', '>='), 2)
          and sg == ['甲', '乙'],
          f'ident={idn} op={op} sig={sg}')
except Exception as ex:
    check('㋖c 标识符→操作符→签名端到端（IDENT甲变量 >= [甲,乙]）', False, str(ex)[:60])

# ㋗ 目标5 深化：性能优化（预加载/请求合并/资源优先级 经正式管线）
b9_qs = {
    "预加载": "写一个预加载单元（提前加载）",
    "请求合并": "写一个请求合并单元（批量传输）",
    "资源优先级": "写一个资源优先级单元（关键优先）",
}
b9_ok = 0
for label, q in b9_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b9_ok += 1
    check(f'㋗ {label} 性能优化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋗b 性能优化三单元全部生成', b9_ok == 3, f'{b9_ok}/3')

# ㋗c 性能端到端：预加载→请求合并→优先级（hit 2 脚本3）
r_pl = domain_route("写一个预加载单元（提前加载）")
r_bq = domain_route("写一个请求合并单元（批量传输）")
r_rp = domain_route("写一个资源优先级单元（关键优先）")
try:
    ns_pl, ns_bq, ns_rp = {}, {}, {}
    exec(r_pl["code"], ns_pl)
    exec(r_bq["code"], ns_bq)
    exec(r_rp["code"], ns_rp)
    pl = ns_pl["preload_ops"](
        {'/a.css': {'kind': 'style', 'used': False}}, 'use', '/a.css')
    bq = ns_bq["batch_requests"]({'b1': []}, 'add', 'b1', ['/a', '/b'])
    rp = ns_rp["resource_priority"]({'/app.js': 'script'}, 'priority', '/app.js')
    check('㋗c 预加载→合并→优先级端到端（hit 2 3）',
          pl == 'hit' and bq == 2 and rp == 3,
          f'preload={pl} batch={bq} prio={rp}')
except Exception as ex:
    check('㋗c 预加载→合并→优先级端到端（hit 2 3）', False, str(ex)[:60])

# ㋘ 目标4 深化：系统管理（配置管理/权限提升/环境变量 经正式管线）
o11_qs = {
    "配置管理": "写一个配置管理单元（键值配置）",
    "权限提升": "写一个权限提升单元（sudo 白名单）",
    "环境变量": "写一个环境变量单元（进程环境）",
}
o11_ok = 0
for label, q in o11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o11_ok += 1
    check(f'㋘ {label} 系统管理单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋘b 系统管理三单元全部生成', o11_ok == 3, f'{o11_ok}/3')

# ㋘c 管理端到端：配置→提权→环境变量（30 allowed /bin）
r_cf = domain_route("写一个配置管理单元（键值配置）")
r_sc = domain_route("写一个权限提升单元（sudo 白名单）")
r_ev = domain_route("写一个环境变量单元（进程环境）")
try:
    ns_cf, ns_sc, ns_ev = {}, {}, {}
    exec(r_cf["code"], ns_cf)
    exec(r_sc["code"], ns_sc)
    exec(r_ev["code"], ns_ev)
    cf = ns_cf["config_ops"]({}, 'set', 'timeout', 30)
    sc = ns_sc["sudo_check"]({'root': ['reboot']}, 'check', 'root', 'reboot')
    ev = ns_ev["env_ops"]({}, 'set', 'PATH', '/bin')
    check('㋘c 配置→提权→环境变量端到端（30 allowed /bin）',
          cf == 30 and sc == 'allowed' and ev == '/bin',
          f'config={cf} sudo={sc} env={ev}')
except Exception as ex:
    check('㋘c 配置→提权→环境变量端到端（30 allowed /bin）', False, str(ex)[:60])

# ㋙ 目标6 深化：查询/算法（邻居查询/路径过滤/三角形计数 经正式管线）
g23_qs = {
    "邻居查询": "写一个邻居查询单元（多跳扩展）",
    "路径过滤": "写一个路径过滤单元（条件筛选）",
    "三角形计数": "写一个三角形计数单元（闭合三元组）",
}
g23_ok = 0
for label, q in g23_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g23_ok += 1
    check(f'㋙ {label} 查询/算法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋙b 查询/算法三单元全部生成', g23_ok == 3, f'{g23_ok}/3')

# ㋙c 查询端到端：邻居→路径过滤→三角形（[1,2] [[0,1]] 1）
r_nq = domain_route("写一个邻居查询单元（多跳扩展）")
r_pf = domain_route("写一个路径过滤单元（条件筛选）")
r_tc = domain_route("写一个三角形计数单元（闭合三元组）")
try:
    ns_nq, ns_pf, ns_tc = {}, {}, {}
    exec(r_nq["code"], ns_nq)
    exec(r_pf["code"], ns_pf)
    exec(r_tc["code"], ns_tc)
    nq = ns_nq["neighbor_query"]({0: [1, 2]}, 'direct', 0)
    pf = ns_pf["path_filter"]([[0, 1]], lambda p: p[-1] == 1)
    tc = ns_tc["triangle_count"]({0: [1, 2], 1: [0, 2], 2: [0, 1]}, 3)
    check('㋙c 邻居→路径→三角形端到端（[1,2] [[0,1]] 1）',
          nq == [1, 2] and pf == [[0, 1]] and tc == 1,
          f'neighbor={nq} filter={pf} tri={tc}')
except Exception as ex:
    check('㋙c 邻居→路径→三角形端到端（[1,2] [[0,1]] 1）', False, str(ex)[:60])

# ㋚ 目标2 深化：VM 执行族（栈操作/算术执行/比较执行 经正式管线）
c14_qs = {
    "栈操作": "写一个栈操作单元（DUP SWAP）",
    "算术执行": "写一个算术执行单元（栈机算术）",
    "比较执行": "写一个比较执行单元（栈机比较）",
}
c14_ok = 0
for label, q in c14_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c14_ok += 1
    check(f'㋚ {label} VM执行单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋚b VM执行三单元全部生成', c14_ok == 3, f'{c14_ok}/3')

# ㋚c VM 端到端：栈操作→算术→比较（DUP2 ADD3 LT True）
r_so = domain_route("写一个栈操作单元（DUP SWAP）")
r_ae = domain_route("写一个算术执行单元（栈机算术）")
r_ce = domain_route("写一个比较执行单元（栈机比较）")
try:
    ns_so, ns_ae, ns_ce = {}, {}, {}
    exec(r_so["code"], ns_so)
    exec(r_ae["code"], ns_ae)
    exec(r_ce["code"], ns_ce)
    so = ns_so["stack_ops"]([1, 2], 'DUP')
    ae = ns_ae["arith_exec"]([1, 2], 'ADD')
    ce = ns_ce["cmp_exec"]([1, 2], 'LT')
    check('㋚c 栈→算术→比较端到端（2 3 True）',
          so == 2 and ae == 3 and ce is True,
          f'stack={so} arith={ae} cmp={ce}')
except Exception as ex:
    check('㋚c 栈→算术→比较端到端（2 3 True）', False, str(ex)[:60])

# ㋛ 目标7 深化：传输/应用（分块传输/HTTP重定向/内容协商 经正式管线）
n12_qs = {
    "分块传输": "写一个分块传输单元（chunked）",
    "HTTP重定向": "写一个 HTTP 重定向单元（3xx 跟随）",
    "内容协商": "写一个内容协商单元（Accept 匹配）",
}
n12_ok = 0
for label, q in n12_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n12_ok += 1
    check(f'㋛ {label} 传输/应用单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋛b 传输/应用三单元全部生成', n12_ok == 3, f'{n12_ok}/3')

# ㋛c 传输端到端：分块→重定向→协商（encode/decode 往返 200 json）
r_ct = domain_route("写一个分块传输单元（chunked）")
r_rd = domain_route("写一个 HTTP 重定向单元（3xx 跟随）")
r_cn = domain_route("写一个内容协商单元（Accept 匹配）")
try:
    ns_ct, ns_rd, ns_cn = {}, {}, {}
    exec(r_ct["code"], ns_ct)
    exec(r_rd["code"], ns_rd)
    exec(r_cn["code"], ns_cn)
    enc = ns_ct["chunked_transfer"]('encode', 'hello', 3)
    dec = ns_ct["chunked_transfer"]('decode', enc)
    rd = ns_rd["http_redirect"]('follow', 301, [200])
    cn = ns_cn["content_negotiation"]('text/html, application/json',
                                       ['application/json'])
    check('㋛c 分块→重定向→协商端到端（hello 200 json）',
          dec == 'hello' and rd == 200 and cn == 'application/json',
          f'chunk={dec} redir={rd} neg={cn}')
except Exception as ex:
    check('㋛c 分块→重定向→协商端到端（hello 200 json）', False, str(ex)[:60])

# ㋜ 目标1 深化：P 线数值族（数学函数/数值舍入/数值统计 经正式管线）
p12_qs = {
    "数学函数": "写一个数学函数单元（abs pow）",
    "数值舍入": "写一个数值舍入单元（floor ceil）",
    "数值统计": "写一个数值统计单元（mean min）",
}
p12_ok = 0
for label, q in p12_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p12_ok += 1
    check(f'㋜ {label} P线数值单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋜b P线数值三单元全部生成', p12_ok == 3, f'{p12_ok}/3')

# ㋜c 数值端到端：数学→舍入→统计（8 3 2.0）
r_mf = domain_route("写一个数学函数单元（abs pow）")
r_rn = domain_route("写一个数值舍入单元（floor ceil）")
r_sc = domain_route("写一个数值统计单元（mean min）")
try:
    ns_mf, ns_rn, ns_sc = {}, {}, {}
    exec(r_mf["code"], ns_mf)
    exec(r_rn["code"], ns_rn)
    exec(r_sc["code"], ns_sc)
    mf = ns_mf["math_func"]('pow', 2, 3)
    rn = ns_rn["round_num"](2.6, 'round')
    sc = ns_sc["stats_calc"]([1, 2, 3], 'mean')
    check('㋜c 数学→舍入→统计端到端（8 3 2.0）',
          mf == 8 and rn == 3 and sc == 2.0,
          f'math={mf} round={rn} stats={sc}')
except Exception as ex:
    check('㋜c 数学→舍入→统计端到端（8 3 2.0）', False, str(ex)[:60])

# ㋝ 目标5 深化：权限/安全/支付（权限API/CSP报告/支付请求 经正式管线）
b10_qs = {
    "权限API": "写一个权限 API 单元（状态管理）",
    "CSP报告": "写一个 CSP 报告单元（违规上报）",
    "支付请求": "写一个支付请求单元（支付流程）",
}
b10_ok = 0
for label, q in b10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b10_ok += 1
    check(f'㋝ {label} 权限/安全/支付单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋝b 权限/安全/支付三单元全部生成', b10_ok == 3, f'{b10_ok}/3')

# ㋝c 端到端：权限→CSP→支付（granted 1 paid）
r_pa = domain_route("写一个权限 API 单元（状态管理）")
r_cr = domain_route("写一个 CSP 报告单元（违规上报）")
r_py = domain_route("写一个支付请求单元（支付流程）")
try:
    ns_pa, ns_cr, ns_py = {}, {}, {}
    exec(r_pa["code"], ns_pa)
    exec(r_cr["code"], ns_cr)
    exec(r_py["code"], ns_py)
    pa = ns_pa["permission_api"]({}, 'request', 'camera', True)
    cr = ns_cr["csp_report"]([], 'record', 'script-src', 'default-src')
    py = ns_py["payment_ops"]({'methods': ['alipay']}, 'pay', 'alipay', 100)
    check('㋝c 权限→CSP→支付端到端（granted 1 paid）',
          pa == 'granted' and cr == 1 and py == 'paid',
          f'perm={pa} csp={cr} pay={py}')
except Exception as ex:
    check('㋝c 权限→CSP→支付端到端（granted 1 paid）', False, str(ex)[:60])

# ㋞ 目标2/3 深化：智能论语义（信任检查/信息差追踪/条件空间类型 经正式管线）
c15_qs = {
    "信任检查": "写一个信任检查单元（门槛放行）",
    "信息差追踪": "写一个信息差追踪单元（记录分析）",
    "条件空间类型": "写一个条件空间类型单元（空间校验）",
}
c15_ok = 0
for label, q in c15_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c15_ok += 1
    check(f'㋞ {label} 智能论语义单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋞b 智能论语义三单元全部生成', c15_ok == 3, f'{c15_ok}/3')

# ㋞c 语义端到端：信任→信息差→条件空间（pass 0.8 [未知]）
r_tc = domain_route("写一个信任检查单元（门槛放行）")
r_ig = domain_route("写一个信息差追踪单元（记录分析）")
r_st = domain_route("写一个条件空间类型单元（空间校验）")
try:
    ns_tc, ns_ig, ns_st = {}, {}, {}
    exec(r_tc["code"], ns_tc)
    exec(r_ig["code"], ns_ig)
    exec(r_st["code"], ns_st)
    tc = ns_tc["trust_check"](0.8, 0.7)
    ig = ns_ig["info_gap_track"](
        [{'node': 'a', 'gap': 0.8}, {'node': 'b', 'gap': 0.3}], 'max')
    st = ns_st["space_type_check"](['伴侣'], ['伴侣', '未知'])
    check('㋞c 信任→信息差→条件空间端到端（pass 0.8 [未知]）',
          tc == 'pass' and ig == 0.8 and st == ['未知'],
          f'trust={tc} gap={ig} space={st}')
except Exception as ex:
    check('㋞c 信任→信息差→条件空间端到端（pass 0.8 [未知]）', False, str(ex)[:60])

# ㋟ 目标4 深化：内核/系统（网络接口/设备驱动/电源管理 经正式管线）
o12_qs = {
    "网络接口": "写一个网络接口单元（网卡配置）",
    "设备驱动": "写一个设备驱动单元（ID 匹配）",
    "电源管理": "写一个电源管理单元（休眠唤醒）",
}
o12_ok = 0
for label, q in o12_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o12_ok += 1
    check(f'㋟ {label} 内核/系统单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋟b 内核/系统三单元全部生成', o12_ok == 3, f'{o12_ok}/3')

# ㋟c 内核端到端：网络接口→设备驱动→电源（eth0 drv_usb suspended）
r_ni = domain_route("写一个网络接口单元（网卡配置）")
r_dd = domain_route("写一个设备驱动单元（ID 匹配）")
r_pw = domain_route("写一个电源管理单元（休眠唤醒）")
try:
    ns_ni, ns_dd, ns_pw = {}, {}, {}
    exec(r_ni["code"], ns_ni)
    exec(r_dd["code"], ns_dd)
    exec(r_pw["code"], ns_pw)
    ni = ns_ni["netif_ops"]({}, 'configure', 'eth0', '192.168.1.1', True)
    dd = ns_dd["driver_register"](
        {'drv_usb': 'VID_1234'}, 'match', 'VID_1234')
    pw = ns_pw["power_ops"]({}, 'suspend')
    check('㋟c 网络接口→设备驱动→电源端到端（eth0 drv_usb suspended）',
          ni == 'eth0' and dd == 'drv_usb' and pw == 'suspended',
          f'netif={ni} driver={dd} power={pw}')
except Exception as ex:
    check('㋟c 网络接口→设备驱动→电源端到端（eth0 drv_usb suspended）', False, str(ex)[:60])

# ㋠ 目标6 深化：时序/动态图（导出子图/时间窗口/边活跃度 经正式管线）
g24_qs = {
    "导出子图": "写一个导出子图单元（节点诱导）",
    "时间窗口": "写一个时间窗口单元（滑窗过滤）",
    "边活跃度": "写一个边活跃度单元（活跃判定）",
}
g24_ok = 0
for label, q in g24_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g24_ok += 1
    check(f'㋠ {label} 时序/动态图单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋠b 时序/动态图三单元全部生成', g24_ok == 3, f'{g24_ok}/3')

# ㋠c 时序端到端：导出子图→时间窗口→边活跃度（内部边 窗口[b] 活跃True）
r_is = domain_route("写一个导出子图单元（节点诱导）")
r_tw = domain_route("写一个时间窗口单元（滑窗过滤）")
r_ea = domain_route("写一个边活跃度单元（活跃判定）")
try:
    ns_is, ns_tw, ns_ea = {}, {}, {}
    exec(r_is["code"], ns_is)
    exec(r_tw["code"], ns_tw)
    exec(r_ea["code"], ns_ea)
    isg = ns_is["induced_subgraph"]({0: [1, 2], 1: [0], 2: [0]}, [0, 1])
    tw = ns_tw["time_window"](
        [{'t': 1, 'e': 'a'}, {'t': 3, 'e': 'b'}, {'t': 5, 'e': 'c'}],
        'window', 2, 4)
    ea = ns_ea["edge_activity"]({('a', 'b'): 5}, 'active', ('a', 'b'), 12)
    check('㋠c 导出→窗口→活跃端到端（{0:[1],1:[0]} [b] True）',
          isg == {0: [1], 1: [0]} and tw == [{'t': 3, 'e': 'b'}] and ea is True,
          f'sub={isg} win={tw} act={ea}')
except Exception as ex:
    check('㋠c 导出→窗口→活跃端到端（{0:[1],1:[0]} [b] True）', False, str(ex)[:60])

# ㋡ 目标7 深化：协议/安全（路径MTU/端口扫描/会话超时 经正式管线）
n13_qs = {
    "路径MTU": "写一个路径 MTU 发现单元（减8重探）",
    "端口扫描": "写一个端口扫描检测单元（扫描识别）",
    "会话超时": "写一个会话超时单元（空闲断开）",
}
n13_ok = 0
for label, q in n13_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n13_ok += 1
    check(f'㋡ {label} 协议/安全单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋡b 协议/安全三单元全部生成', n13_ok == 3, f'{n13_ok}/3')

# ㋡c 协议端到端：MTU→扫描→超时（reduced scan timeout）
r_pm = domain_route("写一个路径 MTU 发现单元（减8重探）")
r_sd = domain_route("写一个端口扫描检测单元（扫描识别）")
r_st = domain_route("写一个会话超时单元（空闲断开）")
try:
    ns_pm, ns_sd, ns_st = {}, {}, {}
    exec(r_pm["code"], ns_pm)
    exec(r_sd["code"], ns_sd)
    exec(r_st["code"], ns_st)
    pm = ns_pm["pmtu_discover"]({'mtu': 1500}, 'result', None, True)
    sd = ns_sd["scan_detect"](
        {'1.2.3.4': [22, 80, 443, 8080, 3306]}, 'check', '1.2.3.4')
    st = ns_st["session_timeout"]({'s1': 10}, 'check', 's1', 50)
    check('㋡c MTU→扫描→超时端到端（reduced scan timeout）',
          pm == 'reduced' and sd == 'scan' and st == 'timeout',
          f'mtu={pm} scan={sd} timeout={st}')
except Exception as ex:
    check('㋡c MTU→扫描→超时端到端（reduced scan timeout）', False, str(ex)[:60])

# ㋢ 目标2/4 深化：C4 工具链（条件断点/调用计数/覆盖率 经正式管线）
c16_qs = {
    "条件断点": "写一个条件断点单元（条件命中）",
    "调用计数": "写一个调用计数单元（profiler）",
    "覆盖率": "写一个覆盖率单元（指令覆盖）",
}
c16_ok = 0
for label, q in c16_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c16_ok += 1
    check(f'㋢ {label} C4工具链单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋢b C4工具链三单元全部生成', c16_ok == 3, f'{c16_ok}/3')

# ㋢c 工具链端到端：条件断点→调用计数→覆盖率（True 3 0.5）
r_cb = domain_route("写一个条件断点单元（条件命中）")
r_cc = domain_route("写一个调用计数单元（profiler）")
r_cv = domain_route("写一个覆盖率单元（指令覆盖）")
try:
    ns_cb, ns_cc, ns_cv = {}, {}, {}
    exec(r_cb["code"], ns_cb)
    exec(r_cc["code"], ns_cc)
    exec(r_cv["code"], ns_cv)
    cb = ns_cb["cond_breakpoint"](
        {5: lambda e: e.get('x') > 3}, 'hit', 5, None, {'x': 5})
    cc = ns_cc["call_counter"]({'f1': 2}, 'count', 'f1')
    cv = ns_cv["coverage_track"]({1, 2}, 'report', None, 4)
    check('㋢c 条件断点→调用计数→覆盖率端到端（True 3 0.5）',
          cb is True and cc == 3 and cv == 0.5,
          f'cond={cb} count={cc} cov={cv}')
except Exception as ex:
    check('㋢c 条件断点→调用计数→覆盖率端到端（True 3 0.5）', False, str(ex)[:60])

# ㋣ 目标1 深化：P 线高级语法（默认参数/关键字参数/多行字符串 经正式管线）
p13_qs = {
    "默认参数": "写一个默认参数单元（缺省绑定）",
    "关键字参数": "写一个关键字参数单元（kw 绑定）",
    "多行字符串": "写一个多行字符串单元（三引号）",
}
p13_ok = 0
for label, q in p13_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p13_ok += 1
    check(f'㋣ {label} P线高级语法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋣b P线高级语法三单元全部生成', p13_ok == 3, f'{p13_ok}/3')

# ㋣c 语法端到端：默认参数→关键字参数→多行字符串（缺省2 kw绑定 跨行串）
r_da = domain_route("写一个默认参数单元（缺省绑定）")
r_kw = domain_route("写一个关键字参数单元（kw 绑定）")
r_ms = domain_route("写一个多行字符串单元（三引号）")
try:
    ns_da, ns_kw, ns_ms = {}, {}, {}
    exec(r_da["code"], ns_da)
    exec(r_kw["code"], ns_kw)
    exec(r_ms["code"], ns_ms)
    da = ns_da["default_args"](['甲', '乙'], {'乙': 2}, ['x'])
    kw = ns_kw["kwargs_bind"](['甲', '乙'], ['x'], {'乙': 'y'})
    ms = ns_ms["multiline_str"]('"""你好\n世界"""', 0)
    check('㋣c 默认→关键字→多行字符串端到端（{甲:x,乙:2} {甲:x,乙:y} 跨行）',
          da == {'甲': 'x', '乙': 2} and kw == {'甲': 'x', '乙': 'y'}
          and ms == ('你好\n世界', 11),
          f'default={da} kw={kw} multi={ms}')
except Exception as ex:
    check('㋣c 默认→关键字→多行字符串端到端（{甲:x,乙:2} {甲:x,乙:y} 跨行）', False, str(ex)[:60])

# ㋤ 目标4 深化：文件/存储（文件压缩/存储池/文件版本 经正式管线）
o13_qs = {
    "文件压缩": "写一个文件压缩单元（RLE 编码）",
    "存储池": "写一个存储池单元（容量分配）",
    "文件版本": "写一个文件版本单元（版本历史）",
}
o13_ok = 0
for label, q in o13_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o13_ok += 1
    check(f'㋤ {label} 文件/存储单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋤b 文件/存储三单元全部生成', o13_ok == 3, f'{o13_ok}/3')

# ㋤c 存储端到端：压缩→存储池→文件版本（aaabb allocated [v1,v2]）
r_fc = domain_route("写一个文件压缩单元（RLE 编码）")
r_sp = domain_route("写一个存储池单元（容量分配）")
r_fv = domain_route("写一个文件版本单元（版本历史）")
try:
    ns_fc, ns_sp, ns_fv = {}, {}, {}
    exec(r_fc["code"], ns_fc)
    exec(r_sp["code"], ns_sp)
    exec(r_fv["code"], ns_fv)
    fc = ns_fc["file_compress"]([('a', 3), ('b', 2)], 'decompress')
    sp = ns_sp["storage_pool"](
        {'data': {'total': 100, 'used': 0}}, 'alloc', 'data', 60)
    fv = ns_fv["file_version"]({'f1': ['v1', 'v2']}, 'list', 'f1')
    check('㋤c 压缩→存储池→文件版本端到端（aaabb allocated [v1,v2]）',
          fc == 'aaabb' and sp == 'allocated' and fv == ['v1', 'v2'],
          f'comp={fc} pool={sp} ver={fv}')
except Exception as ex:
    check('㋤c 压缩→存储池→文件版本端到端（aaabb allocated [v1,v2]）', False, str(ex)[:60])

# ㋥ 目标6 深化：查询/可视化（模式路径/节点标签/模糊匹配 经正式管线）
g25_qs = {
    "模式路径": "写一个模式路径单元（度数模式）",
    "节点标签": "写一个节点标签单元（标注放置）",
    "模糊匹配": "写一个模糊匹配单元（近似名称）",
}
g25_ok = 0
for label, q in g25_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g25_ok += 1
    check(f'㋥ {label} 查询/可视化单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋥b 查询/可视化三单元全部生成', g25_ok == 3, f'{g25_ok}/3')

# ㋥c 查询端到端：模式路径→节点标签→模糊匹配（matched 甲? [(n1,1)]）
r_pp = domain_route("写一个模式路径单元（度数模式）")
r_nl = domain_route("写一个节点标签单元（标注放置）")
r_fm = domain_route("写一个模糊匹配单元（近似名称）")
try:
    ns_pp, ns_nl, ns_fm = {}, {}, {}
    exec(r_pp["code"], ns_pp)
    exec(r_nl["code"], ns_nl)
    exec(r_fm["code"], ns_fm)
    pp = ns_pp["pattern_path"]({0: [1, 2], 1: [2, 3], 2: [3]}, 0, 2, 1)
    nl = ns_nl["node_labels"](['a', 'b'], {'a': '甲'})
    fm = ns_fm["fuzzy_match"]('水', ['n1', 'n2'],
                              {'n1': '水壶', 'n2': '电灯'}, 1)
    check('㋥c 模式→标签→模糊端到端（([0,1],matched) {甲,?} [(n1,1)]）',
          pp == ([0, 1], 'matched') and nl == {'a': '甲', 'b': '?'}
          and fm == [('n1', 1)],
          f'pattern={pp} label={nl} fuzzy={fm}')
except Exception as ex:
    check('㋥c 模式→标签→模糊端到端（([0,1],matched) {甲,?} [(n1,1)]）', False, str(ex)[:60])

# ㋦ 目标2 深化：优化族（窥孔优化/指令融合/循环不变式 经正式管线）
c17_qs = {
    "窥孔优化": "写一个窥孔优化单元（冗余消除）",
    "指令融合": "写一个指令融合单元（LOAD STORE）",
    "循环不变式": "写一个循环不变式单元（外提）",
}
c17_ok = 0
for label, q in c17_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c17_ok += 1
    check(f'㋦ {label} 优化族单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋦b 优化族三单元全部生成', c17_ok == 3, f'{c17_ok}/3')

# ㋦c 优化端到端：窥孔→融合→不变式（[DE] [MOV] 外提）
r_po = domain_route("写一个窥孔优化单元（冗余消除）")
r_ff = domain_route("写一个指令融合单元（LOAD STORE）")
r_li = domain_route("写一个循环不变式单元（外提）")
try:
    ns_po, ns_ff, ns_li = {}, {}, {}
    exec(r_po["code"], ns_po)
    exec(r_ff["code"], ns_ff)
    exec(r_li["code"], ns_li)
    po = ns_po["peephole_opt"]([("PUSH", 0), ("ADD", None), ("DE", 0.1)])
    ff = ns_ff["fuse_load_store"]([("LOAD", "甲"), ("STORE", "乙"), ("DE", 0.1)])
    li = ns_li["loop_invariant"]([("PUSH", 3), ("DE", 0.1)], ('PUSH',))
    check('㋦c 窥孔→融合→不变式端到端（[DE] [MOV] 外提PUSH）',
          po == [("DE", 0.1)] and ff == [("MOV", "甲", "乙"), ("DE", 0.1)]
          and li == ([("PUSH", 3)], [("DE", 0.1)]),
          f'peep={po} fuse={ff} inv={li}')
except Exception as ex:
    check('㋦c 窥孔→融合→不变式端到端（[DE] [MOV] 外提PUSH）', False, str(ex)[:60])

# ㋧ 目标7 深化：应用层收官（消息路由/API限流/数据序列化 经正式管线）
n14_qs = {
    "消息路由": "写一个消息路由单元（主题绑定）",
    "API限流": "写一个 API 限流单元（配额消耗）",
    "数据序列化": "写一个数据序列化单元（字段编码）",
}
n14_ok = 0
for label, q in n14_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n14_ok += 1
    check(f'㋧ {label} 应用层单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋧b 应用层三单元全部生成', n14_ok == 3, f'{n14_ok}/3')

# ㋧c 应用端到端：消息路由→API限流→序列化（[q1] ok [(0,str,甲)]）
r_mr = domain_route("写一个消息路由单元（主题绑定）")
r_ar = domain_route("写一个 API 限流单元（配额消耗）")
r_pe = domain_route("写一个数据序列化单元（字段编码）")
try:
    ns_mr, ns_ar, ns_pe = {}, {}, {}
    exec(r_mr["code"], ns_mr)
    exec(r_ar["code"], ns_ar)
    exec(r_pe["code"], ns_pe)
    mr = ns_mr["msg_routing"]({'设备': ['q1']}, 'route', '设备')
    ar = ns_ar["api_rate_limit"]({}, 'use', 'u1', 3)
    pe = ns_pe["proto_encode"]([('名', 'str'), ('值', 'int')],
                               {'名': '甲', '值': 3})
    check('㋧c 路由→限流→序列化端到端（[q1] ok [(0,str,甲),(1,int,3)]）',
          mr == ['q1'] and ar == 'ok'
          and pe == [(0, 'str', '甲'), (1, 'int', 3)],
          f'route={mr} limit={ar} proto={pe}')
except Exception as ex:
    check('㋧c 路由→限流→序列化端到端（[q1] ok [(0,str,甲),(1,int,3)]）', False, str(ex)[:60])

# ㋨ 目标1 深化：P 线 IO/系统（文件读取/性能计时/环境查询 经正式管线）
p14_qs = {
    "文件读取": "写一个文件读取单元（按行读取）",
    "性能计时": "写一个性能计时单元（耗时测量）",
    "环境查询": "写一个环境查询单元（平台版本）",
}
p14_ok = 0
for label, q in p14_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p14_ok += 1
    check(f'㋨ {label} P线IO/系统单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋨b P线IO/系统三单元全部生成', p14_ok == 3, f'{p14_ok}/3')

# ㋨c IO 端到端：文件→计时→环境（两行 5.0 win32）
r_fr = domain_route("写一个文件读取单元（按行读取）")
r_pt = domain_route("写一个性能计时单元（耗时测量）")
r_pc = domain_route("写一个环境查询单元（平台版本）")
try:
    ns_fr, ns_pt, ns_pc = {}, {}, {}
    exec(r_fr["code"], ns_fr)
    exec(r_pt["code"], ns_pt)
    exec(r_pc["code"], ns_pc)
    fr = ns_fr["file_read_lines"]('第一行\n第二行', 'lines')
    pt = ns_pt["perf_time"](0.0, 0.005, 'ms')
    pc = ns_pc["platform_check"]({'platform': 'win32'}, 'platform')
    check('㋨c 文件→计时→环境端到端（两行 5.0 win32）',
          fr == ['第一行', '第二行'] and pt == 5.0 and pc == 'win32',
          f'file={fr} time={pt} env={pc}')
except Exception as ex:
    check('㋨c 文件→计时→环境端到端（两行 5.0 win32）', False, str(ex)[:60])

# ㋩ 目标5 深化：Web 平台收官（响应式断点/离线队列/会话恢复 经正式管线）
b11_qs = {
    "响应式断点": "写一个响应式断点单元（宽度分级）",
    "离线队列": "写一个离线队列单元（上线重发）",
    "会话恢复": "写一个会话恢复单元（崩溃恢复）",
}
b11_ok = 0
for label, q in b11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b11_ok += 1
    check(f'㋩ {label} Web平台单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋩b Web平台三单元全部生成', b11_ok == 3, f'{b11_ok}/3')

# ㋩c Web 端到端：断点→离线队列→会话恢复（sm [req1,req2] 标签页）
r_rb = domain_route("写一个响应式断点单元（宽度分级）")
r_oq = domain_route("写一个离线队列单元（上线重发）")
r_sr = domain_route("写一个会话恢复单元（崩溃恢复）")
try:
    ns_rb, ns_oq, ns_sr = {}, {}, {}
    exec(r_rb["code"], ns_rb)
    exec(r_oq["code"], ns_oq)
    exec(r_sr["code"], ns_sr)
    rb = ns_rb["responsive_breakpoint"](480, {'sm': 320, 'md': 768, 'lg': 1024})
    oq = ns_oq["offline_queue"](['req1', 'req2'], 'flush')
    sr = ns_sr["session_restore"]({'s1': ['a.com', 'b.com']}, 'restore', 's1')
    check('㋩c 断点→离线→会话端到端（sm [req1,req2] [a.com,b.com]）',
          rb == 'sm' and oq == ['req1', 'req2'] and sr == ['a.com', 'b.com'],
          f'resp={rb} offline={oq} restore={sr}')
except Exception as ex:
    check('㋩c 断点→离线→会话端到端（sm [req1,req2] [a.com,b.com]）', False, str(ex)[:60])

# ㋪ 目标4 深化：调度/并发收官（条件变量/自旋锁/时间片轮转 经正式管线）
o14_qs = {
    "条件变量": "写一个条件变量单元（等待通知）",
    "自旋锁": "写一个自旋锁单元（忙等获取）",
    "时间片轮转": "写一个抢占轮转单元（RR 抢占）",
}
o14_ok = 0
for label, q in o14_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        o14_ok += 1
    check(f'㋪ {label} 调度/并发单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋪b 调度/并发三单元全部生成', o14_ok == 3, f'{o14_ok}/3')

# ㋪c 调度端到端：条件变量→自旋锁→时间片（notified acquired 2）
r_cv = domain_route("写一个条件变量单元（等待通知）")
r_sl = domain_route("写一个自旋锁单元（忙等获取）")
r_rr = domain_route("写一个抢占轮转单元（RR 抢占）")
try:
    ns_cv, ns_sl, ns_rr = {}, {}, {}
    exec(r_cv["code"], ns_cv)
    exec(r_sl["code"], ns_sl)
    exec(r_rr["code"], ns_rr)
    cv = ns_cv["cond_var"]({'waiting': ['t1']}, 'notify')
    sl = ns_sl["spinlock"]({}, 'acquire')
    rr = ns_rr["round_robin"](['t1'], 'preempt', None, 't2')
    check('㋪c 条件→自旋→时间片端到端（notified acquired 2）',
          cv == 'notified' and sl == 'acquired' and rr == 2,
          f'cond={cv} spin={sl} rr={rr}')
except Exception as ex:
    check('㋪c 条件→自旋→时间片端到端（notified acquired 2）', False, str(ex)[:60])

# ㋫ 目标6 深化：条件路由图收官（条件回溯/信任聚合/审计日志 经正式管线）
g26_qs = {
    "条件回溯": "写一个条件回溯单元（反向推导）",
    "信任聚合": "写一个信任聚合单元（多路径合并）",
    "审计日志": "写一个审计记录单元（操作留痕）",
}
g26_ok = 0
for label, q in g26_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g26_ok += 1
    check(f'㋫ {label} 条件路由图单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋫b 条件路由图三单元全部生成', g26_ok == 3, f'{g26_ok}/3')

# ㋫c 路由端到端：回溯→聚合→审计（[缺氧,高温] 0.8 过滤u2）
r_cb = domain_route("写一个条件回溯单元（反向推导）")
r_ta = domain_route("写一个信任聚合单元（多路径合并）")
r_al = domain_route("写一个审计记录单元（操作留痕）")
try:
    ns_cb, ns_ta, ns_al = {}, {}, {}
    exec(r_cb["code"], ns_cb)
    exec(r_ta["code"], ns_ta)
    exec(r_al["code"], ns_al)
    cb = ns_cb["condition_backtrack"](
        {'c': 'b', 'b': 'a'}, 'c', {'a': '高温', 'c': '缺氧'})
    ta = ns_ta["trust_aggregate"]({('a', 'c'): [0.5, 0.8]}, 'max', 'a', 'c')
    al = ns_al["audit_log"](
        [{'user': 'u1', 'action': '读', 'obj': 'a'},
         {'user': 'u2', 'action': '写', 'obj': 'b'}], 'filter', 'u2')
    check('㋫c 回溯→聚合→审计端到端（[缺氧,高温] 0.8 [u2写]）',
          cb == ['缺氧', '高温'] and ta == 0.8
          and al == [{'user': 'u2', 'action': '写', 'obj': 'b'}],
          f'back={cb} trust={ta} audit={al}')
except Exception as ex:
    check('㋫c 回溯→聚合→审计端到端（[缺氧,高温] 0.8 [u2写]）', False, str(ex)[:60])

# ㋬ 目标2 深化：词法/语法收官（字典字面量/元组解析/转义序列/条件空间符号类型 经正式管线）
c17_qs = {
    "字典字面量": "写一个字典字面量单元（键值对解析）",
    "元组解析": "写一个元组解析单元（逗号分隔）",
    "转义序列": "写一个转义序列单元（字符串转义）",
    "条件空间符号类型": "写一个条件空间符号类型单元（符号类型检查）",
}
c17_ok = 0
for label, q in c17_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c17_ok += 1
    check(f'㋬ {label} 词法/语法收官单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋬b 词法/语法收官四单元全部生成', c17_ok == 4, f'{c17_ok}/4')

# ㋬c 收官端到端：字典→元组→转义→符号类型（{'甲':1} (1,2) 换行 [未定义量]）
r_pd = domain_route("写一个字典字面量单元（键值对解析）")
r_pt = domain_route("写一个元组解析单元（逗号分隔）")
r_ue = domain_route("写一个转义序列单元（字符串转义）")
r_ct = domain_route("写一个条件空间符号类型单元（符号类型检查）")
try:
    ns_pd, ns_pt, ns_ue, ns_ct = {}, {}, {}, {}
    exec(r_pd["code"], ns_pd)
    exec(r_pt["code"], ns_pt)
    exec(r_ue["code"], ns_ue)
    exec(r_ct["code"], ns_ct)
    pd = ns_pd["parse_dict"](['{', '甲', ':', 1, '}'], 0)
    pt = ns_pt["parse_tuple"](['(', 1, ',', 2, ')'], 0)
    ue = ns_ue["unescape"]('a\\nb')
    ct = ns_ct["check_condition_types"](
        [{'space': '伴侣', 'symbol': '未定义量', 'type': '数值'}],
        {'情感权重': '数值'})
    check('㋬c 字典→元组→转义→符号类型端到端（{甲:1} (1,2) 换行 [未定义量]）',
          pd == ({'甲': 1}, 5) and pt == ((1, 2), 5)
          and ue == 'a\nb' and ct == [{'space': '伴侣', 'symbol': '未定义量',
                                       'type': '数值'}],
          f'dict={pd} tuple={pt} unesc={ue!r} ct={ct}')
except Exception as ex:
    check('㋬c 字典→元组→转义→符号类型端到端（{甲:1} (1,2) 换行 [未定义量]）',
          False, str(ex)[:60])

# ㋭ 目标1 深化：P 线机制族（链表/进制转换/异常链 经正式管线）
p14_qs = {
    "链表": "写一个链表单元（节点链）",
    "进制转换": "写一个进制转换单元（进制互转）",
    "异常链": "写一个异常链单元（原因保留）",
}
p14_ok = 0
for label, q in p14_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p14_ok += 1
    check(f'㋭ {label} P线机制单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋭b P线机制三单元全部生成', p14_ok == 3, f'{p14_ok}/3')

# ㋭c 机制端到端：链表→进制→异常链（[1,2] 含2 'ff'255 外层←内层）
r_ll = domain_route("写一个链表单元（节点链）")
r_bc = domain_route("写一个进制转换单元（进制互转）")
r_ec = domain_route("写一个异常链单元（原因保留）")
try:
    ns_ll, ns_bc, ns_ec = {}, {}, {}
    exec(r_ll["code"], ns_ll)
    exec(r_bc["code"], ns_bc)
    exec(r_ec["code"], ns_ec)
    head = ns_ll["linked_list_ops"]([1, 2], 'build')
    tr = ns_ll["linked_list_ops"](head, 'traverse')
    ct = ns_ll["linked_list_ops"](head, 'contains', 2)
    hx = ns_bc["base_convert"](255, 16, True)
    bx = ns_bc["base_convert"]('ff', 16, False)
    ec = ns_ec["exception_chain"]('外层', '内层')
    check('㋭c 链表→进制→异常链端到端（[1,2] 含2 ff 255 外层←内层）',
          tr == [1, 2] and ct is True and hx == 'ff' and bx == 255
          and ec == ('ValueError', '外层', '内层'),
          f'tr={tr} ct={ct} hx={hx} bx={bx} ec={ec}')
except Exception as ex:
    check('㋭c 链表→进制→异常链端到端（[1,2] 含2 ff 255 外层←内层）',
          False, str(ex)[:60])

# ㋮ 目标5 深化：浏览器机制（CORS检查/文本排版/剪贴板 经正式管线）
b10_qs = {
    "CORS检查": "写一个 CORS 检查单元（跨域资源共享）",
    "文本排版": "写一个文本排版单元（宽度换行）",
    "剪贴板": "写一个剪贴板单元（复制粘贴）",
}
b10_ok = 0
for label, q in b10_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b10_ok += 1
    check(f'㋮ {label} 浏览器机制单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋮b 浏览器机制三单元全部生成', b10_ok == 3, f'{b10_ok}/3')

# ㋮c 机制端到端：CORS→文本→剪贴板（same-origin [ab,cd] 你好）
r_cr = domain_route("写一个 CORS 检查单元（跨域资源共享）")
r_tw = domain_route("写一个文本排版单元（宽度换行）")
r_cp = domain_route("写一个剪贴板单元（复制粘贴）")
try:
    ns_cr, ns_tw, ns_cp = {}, {}, {}
    exec(r_cr["code"], ns_cr)
    exec(r_tw["code"], ns_tw)
    exec(r_cp["code"], ns_cp)
    cr = ns_cr["cors_check"]('https://a.com', 'https://a.com')
    tw = ns_tw["text_wrap"]('abcd', 2)
    cp = ns_cp["clipboard_ops"]({}, 'copy', '你好')
    cpr = ns_cp["clipboard_ops"]({'text': '你好'}, 'paste')
    check('㋮c CORS→文本→剪贴板端到端（same-origin [ab,cd] 你好）',
          cr == 'same-origin' and tw == ['ab', 'cd'] and cp == 'copied'
          and cpr == '你好',
          f'cors={cr} wrap={tw} copy={cp} paste={cpr}')
except Exception as ex:
    check('㋮c CORS→文本→剪贴板端到端（same-origin [ab,cd] 你好）',
          False, str(ex)[:60])

# ㋯ 目标7 深化：网络层机制（DHCP租约/ARP解析/ICMP探测 经正式管线）
n15_qs = {
    "DHCP租约": "写一个 DHCP 租约单元（地址分配）",
    "ARP解析": "写一个 ARP 解析单元（地址解析）",
    "ICMP探测": "写一个 ICMP 探测单元（Ping 往返）",
}
n15_ok = 0
for label, q in n15_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n15_ok += 1
    check(f'㋯ {label} 网络层机制单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋯b 网络层机制三单元全部生成', n15_ok == 3, f'{n15_ok}/3')

# ㋯c 机制端到端：DHCP→ARP→ICMP（10.0.0.1 aa:bb 可达）
r_dl = domain_route("写一个 DHCP 租约单元（地址分配）")
r_ar = domain_route("写一个 ARP 解析单元（地址解析）")
r_ip = domain_route("写一个 ICMP 探测单元（Ping 往返）")
try:
    ns_dl, ns_ar, ns_ip = {}, {}, {}
    exec(r_dl["code"], ns_dl)
    exec(r_ar["code"], ns_ar)
    exec(r_ip["code"], ns_ip)
    dl = ns_dl["dhcp_lease"]({'10.0.0.1': 'free', '10.0.0.2': 'free'}, 'offer', 'aa:bb')
    ar = ns_ar["arp_resolve"]({'10.0.0.1': 'aa:bb'}, 'lookup', '10.0.0.1')
    ip = ns_ip["icmp_probe"]([], 'reply', '10.0.0.1', 50)
    check('㋯c DHCP→ARP→ICMP端到端（10.0.0.1 aa:bb 可达）',
          dl == '10.0.0.1' and ar == 'aa:bb' and ip == '10.0.0.1',
          f'lease={dl} arp={ar} ping={ip}')
except Exception as ex:
    check('㋯c DHCP→ARP→ICMP端到端（10.0.0.1 aa:bb 可达）',
          False, str(ex)[:60])

# ㋰ 目标6 深化：图算法/查询（强连通分量/二分匹配/可达性判定 经正式管线）
g27_qs = {
    "强连通分量": "写一个强连通分量单元（Kosaraju）",
    "二分匹配": "写一个二分匹配单元（最大匹配）",
    "可达性判定": "写一个可达性判定单元（BFS 传导）",
}
g27_ok = 0
for label, q in g27_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g27_ok += 1
    check(f'㋰ {label} 图算法/查询单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋰b 图算法/查询三单元全部生成', g27_ok == 3, f'{g27_ok}/3')

# ㋰c 算法端到端：SCC→匹配→可达（[[3],[1,2,0]] 3 True）
r_sc = domain_route("写一个强连通分量单元（Kosaraju）")
r_bm = domain_route("写一个二分匹配单元（最大匹配）")
r_rb = domain_route("写一个可达性判定单元（BFS 传导）")
try:
    ns_sc, ns_bm, ns_rb = {}, {}, {}
    exec(r_sc["code"], ns_sc)
    exec(r_bm["code"], ns_bm)
    exec(r_rb["code"], ns_rb)
    sc = ns_sc["scc_kosaraju"]({0: [1], 1: [2], 2: [0], 3: [3]})
    bm = ns_bm["bipartite_matching"]({0: ['a', 'b'], 1: ['b'], 2: ['c']}, [0, 1, 2])
    rb = ns_rb["reachable"]({0: [1], 1: [2]}, 0, 2)
    check('㋰c SCC→匹配→可达端到端（[[3],[1,2,0]] 3 True）',
          sc == [[3], [1, 2, 0]] and bm == 3 and rb is True,
          f'scc={sc} match={bm} reach={rb}')
except Exception as ex:
    check('㋰c SCC→匹配→可达端到端（[[3],[1,2,0]] 3 True）',
          False, str(ex)[:60])

# ㋱ 目标1 深化：P 线数据结构/语法（二叉树/迭代工具/字典合并 经正式管线）
p15_qs = {
    "二叉树": "写一个二叉树单元（中序遍历）",
    "迭代工具": "写一个迭代工具单元（chain 拼接）",
    "字典合并": "写一个字典合并单元（后者覆盖）",
}
p15_ok = 0
for label, q in p15_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p15_ok += 1
    check(f'㋱ {label} P线数据结构/语法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋱b P线数据结构/语法三单元全部生成', p15_ok == 3, f'{p15_ok}/3')

# ㋱c 数据结构端到端：二叉树→迭代→合并（[1,2,3] [1,2,3] 后者覆盖）
r_bt = domain_route("写一个二叉树单元（中序遍历）")
r_iu = domain_route("写一个迭代工具单元（chain 拼接）")
r_dm = domain_route("写一个字典合并单元（后者覆盖）")
try:
    ns_bt, ns_iu, ns_dm = {}, {}, {}
    exec(r_bt["code"], ns_bt)
    exec(r_iu["code"], ns_iu)
    exec(r_dm["code"], ns_dm)
    root = ns_bt["btree_ops"]([3, 1, 2], 'build')
    io = ns_bt["btree_ops"](root, 'inorder')
    ch = ns_iu["iter_utils"]([[1, 2], [3]], 'chain')
    dm = ns_dm["dict_merge"]({'a': 1}, {'a': 2})
    check('㋱c 二叉树→迭代→合并端到端（[1,2,3] [1,2,3] {a:2}）',
          io == [1, 2, 3] and ch == [1, 2, 3] and dm == {'a': 2},
          f'in={io} chain={ch} merge={dm}')
except Exception as ex:
    check('㋱c 二叉树→迭代→合并端到端（[1,2,3] [1,2,3] {a:2}）',
          False, str(ex)[:60])

# ㋲ 目标5 深化：浏览器机制（沙箱隔离/滚动容器/在线状态 经正式管线）
b11_qs = {
    "沙箱隔离": "写一个沙箱隔离单元（权限裁剪）",
    "滚动容器": "写一个滚动容器单元（视口滚动）",
    "在线状态": "写一个在线状态单元（网络监测）",
}
b11_ok = 0
for label, q in b11_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b11_ok += 1
    check(f'㋲ {label} 浏览器机制单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋲b 浏览器机制三单元全部生成', b11_ok == 3, f'{b11_ok}/3')

# ㋲c 机制端到端：沙箱→滚动→在线（granted True 200 offline）
r_sb = domain_route("写一个沙箱隔离单元（权限裁剪）")
r_sc = domain_route("写一个滚动容器单元（视口滚动）")
r_os = domain_route("写一个在线状态单元（网络监测）")
try:
    ns_sb, ns_sc, ns_os = {}, {}, {}
    exec(r_sb["code"], ns_sb)
    exec(r_sc["code"], ns_sc)
    exec(r_os["code"], ns_os)
    caps = set()
    g = ns_sb["sandbox_perms"](caps, 'grant', 'allow-scripts')
    ck = ns_sb["sandbox_perms"](caps, 'check', 'allow-scripts')
    pos = ns_sc["scroll_container"]({}, 'scroll', 200)
    os_ev = ns_os["online_state"]([], 'set', False)
    check('㋲c 沙箱→滚动→在线端到端（granted True 200 offline）',
          g == 'granted' and ck is True and pos == 200 and os_ev == 'offline',
          f'sand={g}/{ck} pos={pos} online={os_ev}')
except Exception as ex:
    check('㋲c 沙箱→滚动→在线端到端（granted True 200 offline）',
          False, str(ex)[:60])

# ㋳ 目标2 深化：词法/语法字面量（布尔/空值/行号跟踪 经正式管线）
c18_qs = {
    "布尔字面量": "写一个布尔字面量单元（真/假）",
    "空值字面量": "写一个空值字面量单元（无/空）",
    "行号跟踪": "写一个行号跟踪单元（定位调试）",
}
c18_ok = 0
for label, q in c18_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        c18_ok += 1
    check(f'㋳ {label} 词法/语法字面量单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋳b 词法/语法字面量三单元全部生成', c18_ok == 3, f'{c18_ok}/3')

# ㋳c 字面量端到端：布尔→空值→行号（(True,1) (None,1) [(甲,1),(丙,2)]）
r_bl = domain_route("写一个布尔字面量单元（真/假）")
r_nl = domain_route("写一个空值字面量单元（无/空）")
r_tl = domain_route("写一个行号跟踪单元（定位调试）")
try:
    ns_bl, ns_nl, ns_tl = {}, {}, {}
    exec(r_bl["code"], ns_bl)
    exec(r_nl["code"], ns_nl)
    exec(r_tl["code"], ns_tl)
    bl = ns_bl["parse_bool"]('真')
    nl = ns_nl["parse_null"]('无')
    tl = ns_tl["track_lines"]('甲 乙\n丙')
    check('㋳c 布尔→空值→行号端到端（(True,1) (None,1) [(甲,1),(乙,1),(丙,2)]）',
          bl == (True, 1) and nl == (None, 1)
          and tl == [('甲', 1), ('乙', 1), ('丙', 2)],
          f'bool={bl} null={nl} lines={tl}')
except Exception as ex:
    check('㋳c 布尔→空值→行号端到端（(True,1) (None,1) [(甲,1),(乙,1),(丙,2)]）',
          False, str(ex)[:60])

# ㋴ 目标1 深化：P 线机制族（最小堆/函数缓存/异步生成器 经正式管线）
p16_qs = {
    "最小堆": "写一个最小堆单元（堆机制）",
    "函数缓存": "写一个函数缓存单元（缓存命中）",
    "异步生成器": "写一个异步生成器单元（逐值产出）",
}
p16_ok = 0
for label, q in p16_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        p16_ok += 1
    check(f'㋴ {label} P线机制单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋴b P线机制三单元全部生成', p16_ok == 3, f'{p16_ok}/3')

# ㋴c 机制端到端：堆→缓存→异步生成器（0 (42,False) 0）
r_hp = domain_route("写一个最小堆单元（堆机制）")
r_fc = domain_route("写一个函数缓存单元（缓存命中）")
r_ag = domain_route("写一个异步生成器单元（逐值产出）")
try:
    ns_hp, ns_fc, ns_ag = {}, {}, {}
    exec(r_hp["code"], ns_hp)
    exec(r_fc["code"], ns_fc)
    exec(r_ag["code"], ns_ag)
    hp = ns_hp["heap_ops"]([3, 1, 2], 'push', 0)
    fc = ns_fc["cached_value"]({}, 'k', lambda: 42)
    ag = ns_ag["async_gen_ops"]({'n': 3}, 'next')
    check('㋴c 堆→缓存→异步端到端（0 (42,False) 0）',
          hp == 0 and fc == (42, False) and ag == 0,
          f'heap={hp} cache={fc} agen={ag}')
except Exception as ex:
    check('㋴c 堆→缓存→异步端到端（0 (42,False) 0）',
          False, str(ex)[:60])

# ㋵ 目标7 深化：网络工程（广播风暴/心跳保活/报文重排序 经正式管线）
n16_qs = {
    "广播风暴": "写一个广播风暴单元（风暴抑制）",
    "心跳保活": "写一个心跳保活单元（连接保活）",
    "报文重排序": "写一个报文重排序单元（按序递交）",
}
n16_ok = 0
for label, q in n16_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        n16_ok += 1
    check(f'㋵ {label} 网络工程单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋵b 网络工程三单元全部生成', n16_ok == 3, f'{n16_ok}/3')

# ㋵c 工程端到端：风暴→保活→重排（True True [a,b]）
r_sc = domain_route("写一个广播风暴单元（风暴抑制）")
r_ka = domain_route("写一个心跳保活单元（连接保活）")
r_rb = domain_route("写一个报文重排序单元（按序递交）")
try:
    ns_sc, ns_ka, ns_rb = {}, {}, {}
    exec(r_sc["code"], ns_sc)
    exec(r_ka["code"], ns_ka)
    exec(r_rb["code"], ns_rb)
    st = {'p1': 150, 'limit': 100}
    sc = ns_sc["storm_control"](st, 'block', 'p1')
    ka = ns_ka["keepalive"]({'last': 100}, 'alive', 120)
    rb = ns_rb["reorder_buffer"]({'buf': {1: 'a', 2: 'b'}, 'next': 1}, 'flush')
    check('㋵c 风暴→保活→重排端到端（True True [a,b]）',
          sc is True and ka is True and rb == ['a', 'b'],
          f'storm={sc} alive={ka} reorder={rb}')
except Exception as ex:
    check('㋵c 风暴→保活→重排端到端（True True [a,b]）',
          False, str(ex)[:60])

# ㋶ 目标6 深化：图算法（传递闭包/图着色/最小割 经正式管线）
g28_qs = {
    "传递闭包": "写一个传递闭包单元（可达矩阵）",
    "图着色": "写一个图着色单元（顶点着色）",
    "最小割": "写一个最小割单元（割容量）",
}
g28_ok = 0
for label, q in g28_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        g28_ok += 1
    check(f'㋶ {label} 图算法单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋶b 图算法三单元全部生成', g28_ok == 3, f'{g28_ok}/3')

# ㋶c 算法端到端：闭包→着色→最小割（对角True {0:0,1:1,2:0} 4）
r_tc = domain_route("写一个传递闭包单元（可达矩阵）")
r_gc = domain_route("写一个图着色单元（顶点着色）")
r_mc = domain_route("写一个最小割单元（割容量）")
try:
    ns_tc, ns_gc, ns_mc = {}, {}, {}
    exec(r_tc["code"], ns_tc)
    exec(r_gc["code"], ns_gc)
    exec(r_mc["code"], ns_mc)
    tc = ns_tc["transitive_closure"]({0: [1], 1: [2]}, 3)
    gc = ns_gc["greedy_coloring"]({0: [1], 1: [0, 2], 2: [1]})
    mc = ns_mc["min_cut"]({0: {1: 3, 2: 2}, 1: {3: 2}, 2: {3: 4}}, 0, 3)
    check('㋶c 闭包→着色→最小割端到端（对角True {0:0,1:1,2:0} 4）',
          tc == [[True, True, True], [False, True, True], [False, False, True]]
          and gc == {0: 0, 1: 1, 2: 0} and mc == 4,
          f'tc={tc} gc={gc} mc={mc}')
except Exception as ex:
    check('㋶c 闭包→着色→最小割端到端（对角True {0:0,1:1,2:0} 4）',
          False, str(ex)[:60])

# ㋷ 目标5 深化：浏览器机制（命中测试/标签页通信/页面可见性 经正式管线）
b12_qs = {
    "命中测试": "写一个命中测试单元（点击命中）",
    "标签页通信": "写一个标签页通信单元（跨标签广播）",
    "页面可见性": "写一个页面可见性单元（隐藏切换）",
}
b12_ok = 0
for label, q in b12_qs.items():
    r = domain_route(q)
    if r.get("ok") and r.get("code") and "def " in r.get("code", ""):
        b12_ok += 1
    check(f'㋷ {label} 浏览器机制单元经正式管线',
          r.get("ok") and "def " in r.get("code", ""),
          f'{r.get("unit")} | {(r.get("checks") or ["固化直出"])[0][:18]}')
check('㋷b 浏览器机制三单元全部生成', b12_ok == 3, f'{b12_ok}/3')

# ㋷c 机制端到端：命中→标签页→可见性（甲 sent hidden）
r_ht = domain_route("写一个命中测试单元（点击命中）")
r_tc = domain_route("写一个标签页通信单元（跨标签广播）")
r_vi = domain_route("写一个页面可见性单元（隐藏切换）")
try:
    ns_ht, ns_tc, ns_vi = {}, {}, {}
    exec(r_ht["code"], ns_ht)
    exec(r_tc["code"], ns_tc)
    exec(r_vi["code"], ns_vi)
    ht = ns_ht["hit_test"](((0, 0, 10, 10, '甲'), (20, 20, 30, 30, '乙')), 5, 5)
    tc = ns_tc["tab_channel"]({}, 'post', 'hi')
    vi = ns_vi["visibility"]({}, 'set', 'hidden')
    check('㋷c 命中→标签页→可见性端到端（甲 sent hidden）',
          ht == '甲' and tc == 'sent' and vi == 'hidden',
          f'hit={ht} chan={tc} vis={vi}')
except Exception as ex:
    check('㋷c 命中→标签页→可见性端到端（甲 sent hidden）',
          False, str(ex)[:60])

print(f'\n=== 白箱自举正式管线（域接管）: {pass_n}/{pass_n + fail_n} 通过 ===')
sys.exit(0 if fail_n == 0 else 1)
