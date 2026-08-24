# -*- coding: utf-8 -*-
"""测试①：路由分布——知识类应白箱(零LLM)，开放类应LLM
度量：每题的 route + 回复长度 + token 估算"""
import sys, os, yaml
sys.stdout.reconfigure(encoding='utf-8')
# 从 .dsh/.credentials.yaml 注入 DeepSeek key（真实测 LLM 路径）
try:
    with open(r'C:\Users\FuRongJun\.dsh\.credentials.yaml', encoding='utf-8') as f:
        _cred = yaml.safe_load(f) or {}
    os.environ['DEEPSEEK_API_KEY'] = _cred.get('DEEPSEEK_API_KEY', '')
    os.environ['LINGSHU_UPSTREAM_KEY'] = _cred.get('DEEPSEEK_API_KEY', '')
except Exception as e:
    print(f'凭据读取失败: {e}')
sys.path.insert(0, r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages')
from aeis.roleplay_chat import LingshuChat
from collections import Counter

lc = LingshuChat(data_dir=r'D:\Program Files\2_ai\knowledge-base\roleplay_data',
                 upstream_key_var='LINGSHU_UPSTREAM_KEY')

# 分类测试集：知识类（白箱应处理）/ 开放类（应走 LLM）
KNOWLEDGE_QS = [
    '什么是碳中和？', '光合作用是怎么发生的？', '什么是函数？', '为什么天空是蓝色的？',
    '什么是概率图模型？', '高压锅为什么做饭快？', '什么是功能格？', '电池的原理是什么？',
    '什么是博弈论？', '为什么冬天窗户起雾？', '什么是Transformer？', '什么是状态匹配？',
    '温室效应是什么？', '锂电池怎么工作？', '什么是递归？', '为什么船能浮在水上？',
    '什么是能量守恒？', '为什么饿了要吃饭？', '什么是机器学习？', '光的折射是什么？',
]
OPEN_QS = [
    '帮我写一首关于秋天的诗', '给我讲一个睡前故事', '帮我规划一次北京三天旅行',
    '写一段代码实现冒泡排序', '帮我起三个有诗意的网名', '总结一下我今天的心情并给建议',
    '编一个关于会说话的猫的短故事', '帮我想几个创业点子', '写一封请假邮件',
    '给我讲讲你眼中的未来世界',
]

def est_tokens(chars):
    """中文约 1.5 字/token（含系统提示等）"""
    return int(chars / 1.5) + 100  # +100 覆盖协议开销

print('=== 测试①：路由分布 ===')
print(f'{"类别":<6}{"题数":<6}{"whitebox":<10}{"llm":<8}{"白箱率":<8}{"token估算(全LLM)":<14}{"实际消耗"}')
results = []
for label, qs in [('知识', KNOWLEDGE_QS), ('开放', OPEN_QS)]:
    routes = Counter()
    total_chars = 0
    for q in qs:
        r = lc.respond(q, session_id=f'route-{label}-{qs.index(q)}')
        route = r.get('route', '?')
        routes[route] += 1
        total_chars += len(r['reply'])
    wb = routes.get('whitebox', 0)
    wb_rate = wb / len(qs) * 100
    # token 估算：全部走 LLM 的话每题约 800 tokens（system500+user100+out200）
    all_llm_tokens = len(qs) * 800
    # 实际消耗：whitebox 题 0 LLM tokens；llm 题按回复长度
    llm_qs = sum(1 for _ in range(len(qs) - wb))
    actual = llm_qs * 800
    print(f'{label:<6}{len(qs):<6}{wb:<10}{routes.get("llm",0):<8}'
          f'{wb_rate:<8.0f}%{all_llm_tokens:<14}{actual}')
    results.append((label, wb, len(qs), wb_rate, all_llm_tokens, actual))

print('\n=== 测试②：token 节约（白箱处理 vs 全 LLM） ===')
tot_k = sum(x[4] for x in results)
tot_a = sum(x[5] for x in results)
save = (tot_k - tot_a) / tot_k * 100
print(f'全 LLM 估算: {tot_k} tokens | 实际消耗: {tot_a} tokens | 节约 {save:.1f}%')
print('（说明：知识类白箱 = 该题 0 LLM token；token 估算按 DSH 平均 800/请求）')

lc.close()
