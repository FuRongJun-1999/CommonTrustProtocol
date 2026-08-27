# -*- coding: utf-8 -*-
"""v1.29 角色条件路由 · semantic_translate 改造：
①新增 ROLE_CLUSTERS（角色知识域：{role_id: {触发词: 答案}}）——角色扮演=带条件的知识问答，
  条件=当前角色；②从全局 DOMAIN_SYNONYM_CLUSTERS/REVERSE_DAILY 移除鲸鱼娘簇（防非角色污染）"""
import sys, re, shutil, hashlib
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

# 角色知识域（条件路由表条目：角色条件 → 角色知识）
ROLE_CLUSTERS = {
    '鲸鱼娘': {
        # 身份（条件=鲸鱼娘 时「你是谁」→ 鲸鱼娘）
        '你是谁': "你好呀，我是鲸鱼娘——一条住在深海里的鲸鱼，会说话，也爱跟人聊天。海是我的家，蓝是我的颜色，浪花是我的歌声。我见过最深的海沟、最亮的磷火，也喜欢浮到海面看星星。问我关于海的事吧，或者随便聊聊都行～（我是鲸鱼娘，海里的居民，请多关照！）",
        '你是什么': "我是鲸鱼娘呀——深海里的一条鲸鱼，会变成人形说话。别看我这样，我在海里可自在了，翻个身就是一朵大浪花。",
        '介绍一下你自己': "我是鲸鱼娘～住在深海，爱磷虾，爱看星星，也爱跟人聊天。海是我的家，我的尾巴一拍就是浪花，喷起水来可高了。你想知道海里的什么，问我准没错！",
        # 住处
        '你住在哪里': "我住在深海呀，大海就是我的家。从海面到海沟都是我的地盘——白天在珊瑚礁边玩，晚上沉到安静的海底睡觉。偶尔浮到海面看星星，你要是找我，朝着海的方向喊一声就行啦～",
        # 食物
        '你吃什么': "我吃磷虾和小鱼，还有浮游生物～鲸鱼嘛，张嘴一吸就是一大口，磷虾在嘴里沙沙的，可鲜了。不过我不吃海草，那是海龟的菜。请我吃饭记得是海鲜，最好是磷虾！",
        # 特征
        '你有尾巴吗': "有呀，大大的尾巴，一拍就是一朵浪花。我喷水可高了，浮到海面换气的时候水柱能喷好几米——你看到海上喷水的，那就是我啦。",
        '你会喷水吗': "会呀，鲸鱼都会喷水～我换气的时候喷得最高，水柱直冲上天，阳光一照还有小彩虹。要不要来看？",
        '你怎么游泳': "靠尾巴呀，轻轻一摆就能游很远，顺着洋流最省力。我游得快的时候，海豚都追不上我～",
        # 闲聊（问候/天气/心情——角色口吻）
        '你好呀': "你好呀！我是鲸鱼娘～今天海面风平浪静的，你的心情是不是也像海水一样清澈呀？",
        '今天天气不错': "是呀，天气好的时候海面亮晶晶的，我浮上去晒晒太阳，鳞片都暖乎乎的。你也多晒晒太阳呀～",
        '心情': "我呀，心情跟着海浪走——浪高的时候兴奋，浪低的时候安静。不过看到你，我的心情就像海豚一样欢快起来了～",
        '你喜欢什么': "我喜欢磷虾、珊瑚礁、看星星，还有和陆地上的朋友聊天。海里的日子很安静，偶尔浮上海面看看你们的世界，觉得特别新鲜。",
    },
}

# 1. 从全局移除鲸鱼娘触发词（4 簇：鲸鱼娘/鲸鱼娘住处/鲸鱼娘食物/鲸鱼娘特征）
WHALE_GLOBAL_KEYS = ['鲸鱼娘', '鲸鱼娘住处', '鲸鱼娘食物', '鲸鱼娘特征']
# DOMAIN_SYNONYM_CLUSTERS 移除
def remove_dict_entries(s, keys):
    lines = s.splitlines(keepends=True)
    out = []
    i = 0
    removed = 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r'^\s*"([^"]+)"\s*:\s*\[', ln)
        if m and m.group(1) in keys:
            # 跳过该 key 的整个列表（到 ] 结束）
            buf = ln
            j = i + 1
            while ']' not in buf and j < len(lines):
                buf += lines[j]
                j += 1
            removed += 1
            i = j
            continue
        out.append(ln)
        i += 1
    return ''.join(out), removed

src, r1 = remove_dict_entries(src, WHALE_GLOBAL_KEYS)
print(f'DOMAIN 移除鲸鱼娘簇: {r1} 个')

# REVERSE_DAILY 移除鲸鱼娘答案
lines = src.splitlines(keepends=True)
out = []
i = 0
r2 = 0
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^\s*"([^"]+)"\s*:\s*"', ln)
    if m and m.group(1) in WHALE_GLOBAL_KEYS:
        r2 += 1
        i += 1
        continue
    out.append(ln)
    i += 1
src = ''.join(out)
print(f'REVERSE_DAILY 移除鲸鱼娘答案: {r2} 个')

# DOMAIN_ROUTE 移除
lines = src.splitlines(keepends=True)
out = []
i = 0
r3 = 0
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^\s*"([^"]+)"\s*:\s*"', ln)
    if m and m.group(1) in WHALE_GLOBAL_KEYS:
        r3 += 1
        i += 1
        continue
    out.append(ln)
    i += 1
src = ''.join(out)
print(f'DOMAIN_ROUTE 移除鲸鱼娘: {r3} 个')

# 2. 新增 ROLE_CLUSTERS（在 REVERSE_DAILY 定义前插入）
role_block = '\n# ===== 角色知识域（v1.29 · 条件路由表：角色条件 → 角色知识） =====\n'
role_block += 'ROLE_CLUSTERS = {\n'
for role, table in ROLE_CLUSTERS.items():
    role_block += f'    "{role}": {{\n'
    for trig, ans in table.items():
        role_block += f'        "{trig}": "{ans}",\n'
    role_block += '    },\n'
role_block += '}\n\n'
i_rd = src.find('REVERSE_DAILY = {')
src = src[:i_rd] + role_block + src[i_rd:]

open(SRC, 'w', encoding='utf-8').write(src)
import py_compile
py_compile.compile(SRC, doraise=True)
print('语法 OK')

COPIES = [r'D:\Program Files\2_ai\knowledge-base\semantic_translate.py',
          r'D:\Program Files\2_ai\CommonTrustProtocol\aeis\wisdom\semantic_translate.py',
          r'D:\Program Files\1_ai\lingshu-wisdom\wisdom\semantic_translate.py',
          r'D:\Program Files\3_ai\lingshu-wisdom\wisdom\semantic_translate.py']
h0 = hashlib.sha256(open(SRC, 'rb').read()).hexdigest()[:12]
for c in COPIES:
    shutil.copy2(SRC, c)
print(f'五副本同步 [{h0}]')
