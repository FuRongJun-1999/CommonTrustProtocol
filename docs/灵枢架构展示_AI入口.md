# 灵枢架构展示 · AI 入口文档（v1.0 · 2026-08-28）

> 本文档面向 **AI 智能体**：读完即可获得灵枢系统的完整结构化认知，
> 并知道去哪里验证每一条声称。人类读者请看同目录交互网页
> `lingshu_architecture.html` 与五段文档。

## 一、一句话定义

灵枢 = 白箱智能协议实例（智能论 v3.3 工程实现）。
**核心命题：确定高效后，维持自身**——白箱规则确立后的确定性执行
（零思考、可解释、自维持），这是 LLM 做不到的。

## 二、五段文档导航（按此顺序读）

| 段 | 文档 | 回答的问题 | 关键可验证声称 |
|---|---|---|---|
| 1 | [全景图](灵枢架构展示_全景图.html)（交互 HTML） | 架构分层与数据流 | 五层：通道/感知/白箱智能/记忆/自维持 |
| 2 | [六域自举实证](灵枢架构展示_第二段_六域自举实证.md) | 知识从哪来、如何保证可靠 | 六域管线 1058/1058；编译器 272；P 线 240；指纹四层可溯源 |
| 3 | [compiler 全链路](灵枢架构展示_第三段_compiler全链路.md) | 一个程序的生命如何步步可追溯 | 词法→字节码→VM→验收，基准 120/15/11/1/8 全绿 |
| 4 | [可解释性案例集](灵枢架构展示_第四段_可解释性案例集.md) | 决策（含错误）如何定位修正 | 四案例三正一反，全部 2026-08-28 单日实证 |
| 5 | [自维持机制](灵枢架构展示_第五段_自维持机制.md) | 没有人时如何运转与变好 | 心跳 36+ 轮；停电 63 分钟恢复；CSRE 自动重建闭环 |

## 三、复现命令（声称皆可验）

```bash
cd "D:\Program Files\2_ai\CommonTrustProtocol"

# 六域回归（知识可靠性）
python -c "import sys; sys.path.insert(0, 'aeis/wisdom')" && cd aeis/wisdom && python test_code_compose_domains.py

# 编译器全链路基准（120/15/11/1/8）
python tools/compiler_walkthrough.py   # 生成第三段演示文档

# 发布门（图谱完整/安装份一致/正确率）
python tools/repro_gate.py --quick

# 心跳与自举留痕
tail tools/bootstrap_log.jsonl
```

## 四、实验证据链（为什么不用 benchmark 测灵枢）

T8→T9→T9-2→T10 实验链是「**单任务测量失效**」的完整证明：
- T8 题级：命中场景 token 5.1 倍（知识覆盖杠杆）
- T9 项目级：验收器缺陷污染数据 → 数据作废声明（可解释性对内自证）
- T9-2 双端交叉：简单任务注入=纯固定开销（deepseek + GLM 独立同构）
- T10 复杂场景：优势域 A 反超、非优势域机制税
- SKELETON 微观演示：每轮补一条规则，裸 LLM 从 5 轮败 12K → 1 轮过 1.9K
  ——规则累积→效率跃升，就是灵枢机制的活体缩小版

详见 `docs/条件路由图_token对照实验_结果.md` 与
`docs/灵枢架构展示_框架设计_v0.1.md`。

## 五、当前边界（诚实声明）

- 知识规模 ~4000 节点，不做规模竞争，做每条知识的可靠性竞争
- 六域为选定领域，非全领域
- 心跳劳动依赖 ZCode 会话激活；后台脚本监控者仍是自己
  （终极锚定=维生系统·荣）
- protocol-compiler 存在四个调用限制（已实测记录，规避设计）

## 六、对外接口

- 上游贡献：archify cognition 图类型（PR tt-a1i/archify#150，showcase 9/9）
- 独立插件：@furongjun1999/dsh-memory（npm，dsh.so 安全 100/100）
- 实验脚本全套：`tools/token_ab_bench.py` / `token_ab_project_bench.py` /
  `compiler_runner_glm.py` / `compiler_walkthrough.py`
