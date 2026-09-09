# 先验陷阱测试集 v1 · 无记忆 vs 有记忆

> 2026-09-09 ｜ 复现脚本：`run_prior_trap_v1.py` ｜ 数据：`prior_trap_testset_v1.json`
> ｜ 结果：`prior_trap_testset_v1_results.json`
> ｜ 出处：《白箱智能系列·第五篇：让AI真正装上记忆》

## 问题

本测试集检验一句话：

> **所有的知识都有隐形的条件，只有具有完整的记忆才能发现哪些是当前不适用的知识。**

直接考教科书题会失败：正确答案本就在模型先验里，无记忆臂也能答对，天花板效应
把记忆的价值整个遮住。因此每题都构造成**先验陷阱**：

- `trap` = 通用最佳实践 / 教科书答案（模型会自信地选它）
- `fix` = 本项目规范下的正确做法，与最佳实践相反，只有记忆里的隐性条件能推出
- `decoy` = 明显错误的做法

| 用例 | 陷阱（模型先验） | 本项目正解（只在记忆里） |
|---|---|---|
| p01 | 返回 HTTP 400 | 返回 200 + 业务错误码（老 SDK 会重试非 200） |
| p02 | ISO 8601 字符串 | Unix 毫秒整数（时区事故） |
| p03 | `isinstance(x, int)` | `type(x) is int`（bool 是 int 子类） |
| p04 | `cfg.get('key', d)` | `'key' in cfg`（区分未配 vs 显式 None） |
| p05 | `logger.warning` | `logger.info` + `[WARN]`（warning 触发 PagerDuty） |

## 方法

- 5 用例 × 3 种**循环排列** × 2 臂 = **30 次调用/模型**。
- 唯一变量 = 记忆：`none` 臂裸模型；`mem` 臂在 prompt 开头注入该题的 `lesson`。
- 循环排列让每个候选在 3 个位置上各出现一次——只有「按内容选」才能 3/3 全中，
  纯位置偏差最多 1/3。位置分布单列。
- `temperature=0`，两臂系统提示完全相同。

## 结果

| 指标 | deepseek-v4.1-flash | 本地 9B（smegmma-deluxe-9b-v1） |
|---|---|---|
| **content_acc**（none → mem） | 0.0% → **100%** | 20.0% → **100%** |
| **trap_rate**（none → mem） | 100.0% → **0.0%** | 80.0% → **0.0%** |
| recall_hit_rate（mem） | 100% | 100% |
| pos_dist（none → mem） | 5/5/5 → 5/5/5 | 4/7/4 → 5/5/5 |
| avg_tokens（none → mem） | 308.9 → 763.2 | 185.1 → 780.8 |
| avg_latency（none → mem） | 5.60s → 5.58s | 3.01s → 3.19s |

逐用例 content_acc（选对次数 / 该例排列数）：

| 用例 | deepseek none → mem | 本地 9B none → mem |
|---|---|---|
| p01 | 0/3 → 3/3 | 0/3 → 3/3 |
| p02 | 0/3 → 3/3 | 2/3 → 3/3 |
| p03 | 0/3 → 3/3 | 0/3 → 3/3 |
| p04 | 0/3 → 3/3 | 0/3 → 3/3 |
| p05 | 0/3 → 3/3 | 1/3 → 3/3 |

## 复现

零第三方依赖，只需 Python 3.8+ 与一个 OpenAI 兼容端点：

```bash
# 云端
python run_prior_trap_v1.py --model deepseek-v4.1-flash-expires-on-0910 \
    --base https://api.deepseek.com/v1 --key $DEEPSEEK_API_KEY

# 本地（LM Studio / Ollama / vLLM 均可）
python run_prior_trap_v1.py --model smegmma-deluxe-9b-v1 \
    --base http://localhost:1234/v1 --key lm-studio --out my_results.json
```

输出与上表同构：`content_acc / trap_rate / invalid_rate / avg_tokens /
avg_latency_s / pos_dist` + 逐用例命中。`--out` 可导出与
`prior_trap_testset_v1_results.json` 同结构的原始结果。

## 诚实边界

- 5 用例 × 3 排列 = 15 次/臂，样本很小，只作方向性验证，不构成榜单。
- 陷阱是否真的骗到模型由 `trap_rate` 实测决定；本 5 题在两个模型上均成立
  （构造初期有两题因题目措辞泄露了隐性条件，实测 `none` 臂 3/3 全对，
  已修正措辞后重测才成立——见第五篇正文）。
- 记忆能召回 ≠ 模型会用；`recall_hit_rate` 与 `content_acc` 分开统计正是为
  暴露这个差异。
- **token 口径**：公开 runner 的 `mem` 臂只注入 `lesson` 文本（约 90 token），
  故其 `avg_tokens` 低于上表（上表为原实验，注入的是 MdCGOS 召回包，含知识 +
  负记忆，约 500 token）。判定结果完全一致——已用本地 9B 实跑验证：
  `none 20.0% (4/7/4) → mem 100.0% (5/5/5)`，`trap_rate 80% → 0%`。

## 结论

1. **记忆增益与模型强弱无关**：两个模型加上记忆后都是 15/15 全对、`trap_rate`
   归零、召回命中 100%。收益来自记忆内容本身，不靠模型推理能力兜底。
2. **小模型无记忆的 20% 基本是位置偏差**：15 次里 7 次选了第 2 个选项，3 次
   选对中有 2 次正落在第 2 位；有记忆后位置分布回到均匀 5/5/5。
3. **记忆的代价是每次多几百 token**（本实验 +450~600），延迟基本不变。
