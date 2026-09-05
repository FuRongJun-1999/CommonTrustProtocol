# -*- coding: utf-8 -*-
"""test_grill.py · 访谈式需求澄清（grill）全流程测试
================================================
覆盖：grill_start → 登记设计树（goal/decision/term/fact + depends_on）
→ frontier 判定 → 过早 finish 拒绝（DEFER）→ 全部落定 → finish 固化
（知识层节点 + hierarchical 决策树边）→ abandon 可逆 → meta 快照恢复。
零外部依赖：临时库 + 直接调 GrillManager。
"""
import os
import sys
import tempfile

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aeis.api import Agent
from aeis.grill import GrillManager

pass_n = fail_n = 0


def check(name, ok, detail=''):
    global pass_n, fail_n
    if ok:
        pass_n += 1
    else:
        fail_n += 1
    print(f'[{"✓" if ok else "✘"}] {name}{" — " + detail if detail else ""}')


tmp = tempfile.mktemp(suffix='_grill.db')
agent = Agent(identity='grill-test', db_path=tmp)
gm = GrillManager(agent)

# ① start：会话创建 + 纪律返回 + 旧记忆召回
r = gm.start('蜂群文件同步工具', context='给灵枢蜂群做一个跨节点文件同步')
check('① grill_start 返回 session_id+纪律+召回', 
      r.get('session_id', '').startswith('grill-') and '访谈纪律' in r.get('discipline', '')
      and isinstance(r.get('related_memory'), list))
sid = r['session_id']

# ② 登记设计树：goal + 依赖 goal 的子决策 + 依赖子决策的孙决策 + term + fact
gm.node_add(sid, '目标', '要做什么？', kind='goal', recommended='跨节点文件同步工具')
gm.node_add(sid, '同步方向', '单向推送还是双向同步？', depends_on=['n1'],
            recommended='双向')
gm.node_add(sid, '冲突策略', '双向冲突时以谁为准？', depends_on=['n2'],
            recommended='时间戳新者胜')
gm.node_add(sid, '术语：节点', '「节点」指灵枢实例还是任意设备？', kind='term',
            depends_on=['n1'], recommended='灵枢实例')
gm.node_add(sid, '现有传输层', '蜂群 bus 是否已支持大文件分帧？', kind='fact')

# ③ frontier：goal（n1）+ 无依赖问题（n4/n5）可立即问；n2（依赖 n1）n3（依赖 n2）被阻塞
f = gm.frontier(sid)
check('③ frontier 初始含 goal 与无依赖问题、阻塞依赖链',
      [n['id'] for n in f['frontier']] == ['n1', 'n5'] and not f['done'],
      f"frontier={[n['id'] for n in f['frontier']]} done={f['done']}")

# ④ 依赖解锁：resolve n1 → n2/n4/n5 进入 frontier，n3 仍被 n2 阻塞
gm.node_resolve(sid, 'n1', '做一个蜂群跨节点文件同步工具，双向', who='user')
f = gm.frontier(sid)
ids = [n['id'] for n in f['frontier']]
check('④ resolve goal 后子决策解锁、孙决策仍阻塞',
      set(ids) == {'n2', 'n4', 'n5'} and f['stats']['resolved'] == 1,
      f'frontier={ids}')

# ⑤ 事实自查路径：who=agent
gm.node_resolve(sid, 'n5', '已支持分帧（net 域 消息分帧单元），大文件需分片', who='agent')
check('⑤ 事实节点 who=agent 落定', gm.frontier(sid)['stats']['resolved'] == 2)

# ⑥ 过早 finish 拒绝（DEFER）：n2/n3/n4 未决
r = gm.finish(sid, summary='不该成功')
check('⑥ frontier 非空时 finish 拒绝（不完全清楚就不固化）',
      r.get('fixed') is False and len(r.get('open_questions', [])) == 3,
      f'open={[q["id"] for q in r.get("open_questions", [])]}')

# ⑦ 全部落定 → done=true
gm.node_resolve(sid, 'n2', '双向同步', who='user')
gm.node_resolve(sid, 'n3', '时间戳新者胜', who='user')
gm.node_resolve(sid, 'n4', '灵枢实例', who='user')
f = gm.frontier(sid)
check('⑦ 全部落定 done=true', f['done'] is True and f['frontier'] == [],
      f"stats={f['stats']}")

# ⑧ finish 固化：知识层节点 + hierarchical 决策树边 + 总结
r = gm.finish(sid, summary='双向同步+时间戳冲突策略，节点=灵枢实例')
check('⑧ finish 固化 5 节点+3 树边',
      r.get('fixed') is True and len(r.get('node_memory_ids', {})) == 5
      and r.get('tree_edges') == 3 and r.get('summary_saved') is True,
      f"stats={r.get('stats')}")

# ⑨ 固化落库验证：节点在知识层、层级边存在、再 finish 拒绝（已 closed）
all_ids = list(r['node_memory_ids'].values())
nodes_ok = all(agent.engine.store.get_node(nid) is not None for nid in all_ids)
tree_edges = []
for nid in all_ids:
    for e in agent.engine.store.get_outgoing_edges(nid):
        if e.target_id in all_ids and getattr(
                e.relation_type, 'value', str(e.relation_type)) == 'hierarchical':
            tree_edges.append(e)
check('⑨ 库中节点与决策树边验证', nodes_ok and len(tree_edges) == 3,
      f'nodes={len(all_ids)} edges={len(tree_edges)}')
try:
    gm.finish(sid)
    check('⑩ 已固化会话不可重复 finish', False, '未抛异常')
except ValueError:
    check('⑩ 已固化会话不可重复 finish', True)

# ⑩b 四要素同构：conditions/negative/execution 固化入 content（KCCS 结构）
r13 = gm.start('四要素同构主题')
gm.node_add(r13['session_id'], '部署方式', '部署到哪里？', kind='decision',
            conditions='已确认需要自托管', negative='无运维团队时不适',
            execution='docker compose 单机部署')
gm.node_add(r13['session_id'], '目标', '要做什么', kind='goal')
gm.node_resolve(r13['session_id'], 'n1', '自托管知识库', who='user')
gm.node_resolve(r13['session_id'], 'n2', 'docker 单机', who='user')
r = gm.finish(r13['session_id'])
nid2 = r['node_memory_ids']['n1']
_fixed = agent.engine.store.get_node(nid2).content
check('⑩b 四要素同构固化（条件/不适用/执行入 KCCS content）',
      r['fixed'] and '生效条件: ' in _fixed and '不适用条件: ' in _fixed
      and '如何执行: ' in _fixed,
      _fixed.replace(chr(10), ' | ')[:80])

# ⑪ abandon 可逆
r2 = gm.start('废弃主题')
gm.node_add(r2['session_id'], '问题', '这个问题不会走到固化')
r = gm.finish(r2['session_id'], abandon=True)
check('⑪ abandon 放弃不固化', r.get('abandoned') is True)

# ⑫ meta 快照恢复：新 Manager（模拟 server 重启）恢复未完成会话
r3 = gm.start('跨会话恢复主题')
gm.node_add(r3['session_id'], '待决问题', '重启后还在吗？')
gm2 = GrillManager(agent)
try:
    f2 = gm2.frontier(r3['session_id'])
    check('⑫ 未完成访谈从 meta 快照跨实例恢复',
          f2['topic'] == '跨会话恢复主题' and len(f2['frontier']) == 1)
except Exception as ex:
    check('⑫ 未完成访谈从 meta 快照跨实例恢复', False, str(ex)[:60])
gm2.finish(r3['session_id'], abandon=True)

# ⑬ 非法依赖拒绝
s4 = gm.start('非法依赖测试')
try:
    gm.node_add(s4['session_id'], '坏节点', '依赖不存在', depends_on=['n999'])
    check('⑬ 未知 depends_on 拒绝', False, '未抛异常')
except ValueError:
    check('⑬ 未知 depends_on 拒绝', True)
gm.finish(s4['session_id'], abandon=True)

print(f'\n=== grill 访谈式需求澄清测试: {pass_n}/{pass_n + fail_n} 通过 ===')
try:
    os.remove(tmp)
except OSError:
    pass
sys.exit(0 if fail_n == 0 else 1)
