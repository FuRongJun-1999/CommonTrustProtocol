# 条件路由图 token 对照实验 · 复现文档 v1.0

> 荣 2026-08-28 指令：将认知图工程作为灵枢插件，和主仓库的显式描述进行
> 对比测试，30 次匹配测试验证灵枢和白箱带来的总 token 减少效果。

## 实验设计

**假设**：条件路由图纪律（条件卡命中直达）相比「把机制用文字描述给 LLM」
能显著减少总 token 消耗——机制被**执行**不同于机制被**说明**。

### 两组

| 组 | 名称 | 管线 | LLM token |
|---|---|---|---|
| A | 灵枢插件（条件路由图） | `card_route(dex, q)` → 命中（`_card_hit` 且 score≥5）→ **白箱直答，0 LLM token**；未命中 → 极简 system 提示词 LLM 兜底 | 仅兜底题 |
| B | 主仓库显式描述 | 每题全量 LLM；system = 主仓库机制文本描述（四要素/负路由/置信度排序的**说明文字**，无任何卡片数据） | 全部 30 题 |

### 判定

白箱确定性：答案必须包含该题 `key_facts` 全部关键事实（字符串包含），
零 LLM 评审。知识边界外的开放题（6 题）不计正确率只计 token。

### 题集（30 = 24 有事实 + 6 开放）

- 学科骨架 6（三角形/光反射/二重积分/电解水/细胞分裂/鸦片战争）
- 计算机 kp 6（三次握手/度分布/插入排序/工作窃取/TCP vs UDP/任务调度）
- 生活导航 9（婆媳/理财/育儿/宠物/拖延/租房/汇报/夜醒/编程入门）
- 白箱机制自指 3（复合赋值/str 方法/print 多参）
- 知识边界外 6（量子引力/火星土豆/当年明月/信息悖论/三天小提琴/宇宙命运）

## 复现步骤

```bash
# 0. 环境：Python 3.10+，单源仓库 CommonTrustProtocol；智谱 key 有效
#    key 获取：E:\个人数据\智谱api.txt（或开放平台控制台）

# 1. 注入 key（当前会话）
export BIGMODEL_API_KEY=$(cat 'E:\个人数据\智谱api.txt' | tr -d '[:space:]]')
# PowerShell: [Environment]::SetEnvironmentVariable('BIGMODEL_API_KEY', $k, 'User')

# 2. 跑 30 匹配测试（约 5-15 分钟，glm-5.3-flash 60 次调用）
cd "D:\Program Files\2_ai\CommonTrustProtocol"
python tools/token_ab_bench.py --n 30

# 3. 查看报告
cat tools/token_ab_report.json
```

## 关键实现事实（复现时易踩）

1. **LLM 通道**：智谱开放平台 `open.bigmodel.cn/api/paas/v4`，模型
   `glm-5.3-flash`。**不要传 `thinking` 字段**——`{"type": "low"}` 实测
   400/1210（该模型常开思考，文档提示 low/high/max 但 type 形态不被
   接受）；不带 thinking 字段 + max_tokens≥2000 为已验证形态。
   A/B 两组同参数（temperature=0），思考链 token 照实计入——公平对比。
2. **ZCode config 里的 DeepSeek key 已失效**（401）——勿用 llm_channel
   的 deepseek 通道做此实验。
3. **CSRE 索引须新鲜**：card_route 不依赖 CSRE，但若复现中加 L1 先验，
   先 `python -c "from csre import Csre; c=Csre(db); c.build_index(); c.save_index()"`。
   bootstrap_loop 循环现在会自动重建（kp 指纹比对）。
4. **判定口径**：`key_facts` 必须显式排除空值——空串 `in` 任何串恒真
   会产生假 100%。
5. **公平性**：A 组兜底 system 与 B 组 system 内容不同（A 极简、B 含
   机制描述）——这正是实验设计：B 组多出的描述 token 也要计入总成本，
   因为「显式描述」本身就是它的付出。

## 结果

见 `tools/token_ab_report.json` 与本次实验运行输出（2026-08-28）。
