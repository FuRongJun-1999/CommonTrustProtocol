# 主仓库修改纪律（CTP Discipline v1.0 · 2026-08-27）

> **CTP 是唯一真源（single source of truth）。** 所有其他目录（site-packages、knowledge-base、
> lingshu-wisdom、dsh-memory、D:\Program Files\4_ai 等）都是副本、同步或阉割子内容——
> 它们**不产生新内容**，只从 CTP 同步。

---

## 一、为什么需要纪律

历史教训（2026-08-26/27 审查发现）：

1. **副本污染主源**：site-packages 曾被旧 wheel（lingshu-wisdom 旧副本）force-reinstall 覆盖，
   `semantic_translate.py`/`chat_engine.py`/`code_compose.py` 静默回退旧版，丢失 v1.42-v1.45 修复
   （情感/意见域路由、矛盾键放宽、核心段恢复）——**运行中的白箱引擎比主仓库旧**。
2. **硬编码路径泄漏**：副本中出现 `sys.path.insert(0, r'D:\Program Files\2_ai\knowledge-base')`
   等本机路径，若同步进主仓库会污染所有用户。
3. **运行时产物误提交**：`audit_log/`、`*.bak-*`、`reports/*.log` 反复被 `git add -A` 带入版本库
   （历史 54194ff 清理过一次，daa3617 又清理一次）。
4. **数量表述漂移**：MCP 工具数 71/75/73 三处不一致、知识库节点 3061/3048 漂移——
   正则统计 ≠ 运行时实测，README 数字必须实测校准。
5. **功能文件只存在于副本**：`pattern_separation.py`（MCP 已注册工具）在主仓库缺失——
   副本有、真源无，发布 wheel 后工具缺失。

**核心原则**：主仓库的任何变更必须**可验证、可追溯、符合条件路由图规范**，不允许随意修改。

---

## 二、变更必须走「条件路由图 + 自迭代八步闭环」

### 2.1 条件路由图（回答/检索/执行的统一规范）

任何知识、规则、能力描述必须四要素齐全（KCCS，对齐代码注释协议）：

| 要素 | 含义 | 缺失后果 |
|---|---|---|
| 生效条件 | 什么条件下适用 | 无正索引，检索不到 |
| 子功能 | 能做什么 | 能力边界不清 |
| 执行 | 怎么做 | 无法落地 |
| 不适用条件 | 什么条件下**不**适用（负路由） | 误配（如「内角和」被「面积」抢答） |

**修改知识库（db/注释）必须**：
1. 用 `docs/知识卡注释规范_KCCS_v0.1.md` 的格式；
2. 补知识走 `docs/自迭代知识补充条件路由协议_KAP_v0.1.md`（KAP 协议）；
3. 修改后跑检索验证（graph_retrieve 命中正确 kp + 负路由不误配）。

### 2.2 自迭代八步闭环（修改流程）

对主仓库的**每次变更**（代码/文档/知识库）走八步闭环：

```
感知（变更需求 + 当前状态）
 → 识别（问题分类：bug/过时/增强/文档）
 → 分析（影响范围：哪些副本/发布物受影响）
 → 验证（变更前基线：先跑相关测试/检索确认现状）
 → 固化（主仓库修改，附规范注释）
 → 记录（提交信息完整描述：为什么改、影响什么）
 → 反馈（副本同步：site-packages/知识库/dsh-memory 是否需同步）
 → 方向性自检（是否引入硬编码/运行时产物/过时数字？）
```

**禁止**：
- 跳过验证直接改；
- 只改副本不同步主仓库（或反向）；
- 无提交信息、无影响分析的变更。

---

## 三、硬性规则（Red Lines）

### R1 主仓库唯一真源
- 新功能/修复**只写进 CTP**，副本靠同步（不允许在 site-packages/knowledge-base 直接改完不回主仓库）。
- 发布 wheel **只从 CTP `aeis/dist/` 构建**（当前 aeis-0.4.0 完整自包含：aeis+wisdom+harness+seed_knowledge）。

### R2 禁止硬编码路径
- 任何文件不得出现 `D:\`、`C:\Users`、`/home/` 等本机绝对路径。
- 默认路径必须：`os.environ.get("AEIS_DB", os.path.join("data", "lingshu.db"))` 或相对 `HERE`。
- 提交前 grep 检查：`D:\\Program|C:\\Users|knowledge-base|site-packages`。

### R3 运行时产物不入库
- `**/audit_log/`、`*.bak-*`、`reports/*.log`、`*.db-shm/wal` 已入 .gitignore。
- **禁止 `git add -A` 盲提**——必须 `git status` 审查后按文件 `git add`。

### R4 数量表述必须实测
- README 中的工具数/节点数/覆盖率等数字，必须以**运行时实测**为准（如 `_tools()` 返回数、
  db `select count(*)`），禁止从源码正则猜测。
- 修改知识库后，同步更新 README 对应数字。

### R5 版本与描述一致
- pyproject 版本号变更必须说明理由；description 中的智能论版本（当前 v3.3）与实际理论文件一致。
- 过时文档移入 `docs/history/`（专门归档目录），不留在顶层误导。

### R6 变更验证
- 代码：`python -m py_compile` 通过 + 相关测试绿。
- 知识库：graph_retrieve 关键路由实测命中。
- 发布：干净 venv 装 wheel → `tools/list` 工具数正确 → wisdom_chat 白箱回答验证。

---

## 四、副本同步矩阵

| 副本 | 同步内容 | 同步方向 | 时机 |
|---|---|---|---|
| site-packages（运行环境） | aeis/*.py + wisdom/*.py + db | CTP → SP | 每次主仓库修改后 |
| knowledge-base（历史工作区） | wisdom/*.py + db（去硬编码版） | CTP → KB | 同上 |
| lingshu-wisdom（落后发布版） | **不再同步**（历史产物，勿用其内容反哺主仓库） | — | — |
| dsh-memory（插件） | README 工具数/描述 | CTP 实测 → dsh-memory | 工具数变化时 |
| 4_ai（模拟用户验证） | 全新安装验证 | CTP wheel → 4_ai | 每次发布前 |

---

## 五、发布检查清单（Release Checklist）

发布新 wheel 前逐项确认：

- [ ] 从 CTP `aeis/dist/` 构建（版本号已升、description 正确）
- [ ] 干净 venv 安装 → `import aeis` OK、`m.version` 正确
- [ ] `python -m aeis.mcp.server` → `tools/list` 工具数与 README 一致
- [ ] 随包知识库存在且 KCCS 注释 kp 数量与 README 一致
- [ ] wisdom_chat 白箱问答实测（如「三角形内角和」命中 E2 卡）
- [ ] 无硬编码路径（R2 grep 检查）
- [ ] README 数字已同步实测值（R4）
- [ ] 运行时产物未入库（R3）

---

*本纪律文档本身遵循条件路由图：生效条件=对 CTP 主仓库的任何修改；子功能=规范变更流程；
执行=八步闭环 + 六条红线；不适用条件=纯讨论/审查阶段（不修改文件时不强制）。*
