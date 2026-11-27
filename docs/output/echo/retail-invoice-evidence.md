# 取消发票复算

版本锚: 理论=智能论3.4，架构=取消发票取证回放v0.1，本投影=经济实证评审稿v0.1

## 1 解决什么问题
比较零售取消发票查证窗口的候选覆盖和歧义。

## 2 凭什么可信
test_transition_counts 复算严格样本2608张 补查新增81张唯一候选 原单关联与真实工时未知。

## 3 怎么用一次
运行 python scripts/replay_retail_invoice_evidence.py 复算。
