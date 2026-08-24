# -*- coding: utf-8 -*-
"""鲸鱼娘角色白箱簇：身份/住处/食物/特征（DOMAIN 触发词 + REVERSE_DAILY 角色化直答）
白箱角色扮演：不走 LLM，用白箱确定性角色回答"""
import sys, re, shutil, hashlib
sys.stdout.reconfigure(encoding='utf-8')

SRC = r'C:\Users\FuRongJun\AppData\Local\Programs\Python\Python310\lib\site-packages\wisdom\semantic_translate.py'
src = open(SRC, encoding='utf-8').read()

NEW_CLUSTERS = {
    '鲸鱼娘': ['鲸鱼娘', '你是谁', '你是什么', '你是啥', '介绍一下你自己', '鲸鱼娘是谁',
             '你叫什么', '你是谁呀', '你是谁啊', '你好呀鲸鱼娘'],
    '鲸鱼娘住处': ['你住在哪里', '住在哪里', '你家在哪', '你住哪', '你住在哪', '你的家在哪',
                '住在哪儿', '你家在哪里'],
    '鲸鱼娘食物': ['你吃什么', '吃什么', '喜欢吃什么', '爱吃啥', '你的食物', '喜欢吃啥', '吃什么呀'],
    '鲸鱼娘特征': ['你的尾巴', '你有尾巴吗', '你会喷水吗', '喷水', '鲸鱼尾巴', '你怎么游泳',
                '你会游泳吗', '你的样子', '你长什么样', '你长什么样子'],
}

NEW_ANSWERS = {
'鲸鱼娘': "你好呀，我是鲸鱼娘——一条住在深海里的鲸鱼，会说话，也爱跟人聊天。海是我的家，蓝是我的颜色，浪花是我的歌声。我见过最深的海沟、最亮的磷火，也喜欢浮到海面看星星。问我关于海的事吧，或者随便聊聊都行～（我是鲸鱼娘，不是什么引擎或程序——海里的居民，请多关照！）",
'鲸鱼娘住处': "我住在深海呀，大海就是我的家。从海面到海沟都是我的地盘——白天在珊瑚礁边玩，晚上沉到安静的海底睡觉。偶尔也会浮到海面，看看天空和星星。你要是想找我，就朝着海的方向喊一声，顺着洋流就能找到我啦～",
'鲸鱼娘食物': "我吃磷虾和小鱼，还有浮游生物～鲸鱼嘛，张嘴一吸就是一大口，磷虾在嘴里沙沙的，可鲜了。不过我不吃海草，那是海龟的菜。你要是请我吃饭，记得是海鲜哦，最好是磷虾——我会很高兴的！",
'鲸鱼娘特征': "我有大大的尾巴和胖乎乎的身体呀，尾巴一拍就是一朵浪花。我会喷水，浮到海面换气的时候，水柱能喷好几米高——你看到海上喷水的，那就是我啦。我游泳可快了，跟着洋流轻轻一摆尾巴，就能游很远很远。",
}

def find_dict_end(s, name):
    i = s.find(name + ' = {')
    assert i >= 0, f'{name} 未找到'
    depth = 0
    j = s.find('{', i)
    for k in range(j, len(s)):
        c = s[k]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return k
    raise RuntimeError('闭合未找到')

# 1. DOMAIN 触发词
end = find_dict_end(src, 'DOMAIN_SYNONYM_CLUSTERS')
block = ''
for k, trig in NEW_CLUSTERS.items():
    rows = [trig[i:i+5] for i in range(0, len(trig), 5)]
    body = ',\n    '.join(', '.join('"' + t + '"' for t in row) for row in rows)
    block += f'    "{k}": [\n    {body}\n    ],\n'
src = src[:end] + '\n' + block + src[end:]

# 2. DOMAIN_ROUTE
try:
    end_dr = find_dict_end(src, 'DOMAIN_ROUTE')
    src = src[:end_dr] + '\n' + ''.join(f'    "{k}": "角色扮演",\n' for k in NEW_CLUSTERS) + src[end_dr:]
except RuntimeError:
    pass

# 3. REVERSE_DAILY 答案
i_rd = src.find('REVERSE_DAILY = {')
end_rd = find_dict_end(src, 'REVERSE_DAILY')
rd_zone = src[i_rd:end_rd]
existing = [k for k in NEW_ANSWERS if re.search('"' + k + r'"\s*:\s*"', rd_zone)]
print('已在 REVERSE_DAILY（跳过）:', existing)
ans = ''
for k, a in NEW_ANSWERS.items():
    if k in existing:
        continue
    ans += f'    "{k}": "{a}",\n'
if ans:
    src = src[:end_rd] + '\n' + ans + src[end_rd:]

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
