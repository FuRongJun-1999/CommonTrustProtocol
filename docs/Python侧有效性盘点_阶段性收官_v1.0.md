# Python 侧有效性盘点（阶段性收官）v1.0（2026-08-31）

> 荣校准（2026-08-31）：**有效性优先**——同样的功能，Python 实现也有效，
> 那么就不做更改。性能优化是 Python 阶段性任务结束之后的独立决策。
> 本文档 = Python 阶段性任务的收官验收：逐功能实证「Python 已有效」。

## 一、结论

**功能层面 Python 侧全部有效**——条件资格计算机的功能分解共 12 项，
每项均有在位实现+可复现证据。据此：

- **取消**原计划的「CRG-DB Python 四件套骨架」批次——KNode 64B cache line
  /CEdge 物理结构是**性能优化阶段**的关注点（cache miss 率），非有效性关注点；
  Python 侧 dict/SQLite 行即节点，功能等价。
- 本轮唯一实施的更改 = **D 序列落库**（功能缺口非性能：此前 D 序列仅内存
  100 条，跨进程重启后 d²/趋势断链）——有效性补全，非优化。

## 二、功能×实现×证据对照表

| # | 功能项 | Python 实现 | 有效性证据（可复现） |
|---|---|---|---|
| 1 | 四态判定（ACCEPT/REJECT/DEFER/BLINDSPOT） | 引擎 navigate 四态链路+门槛分级 | T8 复测：回答率 87.5%，零误杀零漏放（tools/t8_recheck.py） |
| 2 | 代码编写识别与校验 | code 触发词+自校验链路 | 8/8 识别+8/8 校验（tools/code_recheck.py） |
| 3 | 负路由（拒绝优先便宜） | 负条件索引+rejected_paths | 域外强行命中→BLINDSPOT（T8 #24 修复后复测） |
| 4 | 路由缓存 | tools/route_cache.py（TTL+指纹失效） | 命中 0.00ms vs 直查 33.4ms（ARCH-GRAPH-SCF 实测） |
| 5 | CSR 图布局 | tools/graph_layout.py | 构建 25ms/切片 0µs vs LIKE 6.3ms（同上） |
| 6 | 冷热分层 | tools/hot_cold.py（Beta 升降级） | 7/7（重启口径诚实） |
| 7 | 条件链/路径裁决 | PathTrace 展开复核 | M1.3 KCCS 完备性抽样 50 卡 100%；路由抽验 4/4 |
| 8 | 统一时间核 | aeis/time_core.py（cred 四函数） | E5 lint PASS；四调用点收口 c7ac6e4b；回归 55/55 |
| 9 | 信息差度量 D_task/D_meta | aeis/gap_dual.py + gap_trend | 心跳常态运行；趋势 narrowing 可测 |
| 10 | 二阶信号 d²D（情绪方向） | core.attention_shift（PROP-EMO-DIRECTION-002） | 策略层实现+本批跨进程回放实测 OK |
| 11 | 知识飞轮（验证→归纳→固化） | aeis/flywheel.py | patterns 蒸馏产出；增长率/复用观测跨进程（flywheel_reuse 表） |
| 12 | 对抗防线 | 门槛按域分级+cov 双维 | 答非所问/域外全拒（T8 拒 3 全对） |

## 三、本批更改明细（唯一功能缺口补全）

D 序列落库（b92f6108 审计发现的待办，本批闭合）：
- 建表 `gap_history(ts, d_norm)`（OBS-REV1 持久化段，滚动保留 2000 条）
- `record_info_gap` 写入库（best_effort，不阻断主流程）
- 引擎初始化 `_load_gap_history()` 恢复库尾 100 条——**跨进程 d²/趋势不断链**
- 验证：写-重启-读回放实测（序列 5 样本完整恢复，gap_trend 重启即出
  narrowing）+ 包回归 55/55

## 四、边界与后继

- **Python 阶段性任务就此收官**：后续不再为「对齐 Rust 设计稿结构」改动
  Python 侧；仅功能性缺陷（如本批 D 序列）按需修补。
- **性能优化为独立后续决策**（荣裁定时点）：候选=64B 结构对齐/CSR 物理层
  深化/PyO3 FFI（CRG-DB 设计稿 M2-M3 范围）。启动前 Python 侧 12 项证据
  即行为黄金标准——性能版验收=行为等价+性能提升双条件。
- 审计链完整性：钉死批四条款（概念钉死批 v0.1）→ 口径审计（b92f6108）
  → 时间核单点化（c7ac6e4b）→ 本收官文档——理论/工程/验收三层可溯源。
