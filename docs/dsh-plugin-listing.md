# DSH 官方列表条目修改文档（内部校对稿）

- 状态：**待校对**（荣 + 灵枢校对通过后执行）
- 目标：awesome-dsh-plugin/awesome-dsh-plugin 官方列表（Memory 分类）的灵枢条目
- 背景：现有 PR 条目存在两个问题（链接不规范 + 描述漏核心），需修订后重新提交

---

## 一、问题确认

### 问题 1：链接不符合官方列表规范
- 现状：`github.com/FuRongJun-1999/CommonTrustProtocol/tree/main/plugins/dsh-memory`
- 问题：官方列表 252 个条目**全部是独立插件仓库**（repo 即插件）；我们的链接指向协议理论仓库的子目录——维护者/用户点进去找不到"项目"，可能因此拒收
- **方案：为插件建立独立 GitHub 仓库** `FuRongJun-1999/dsh-memory`
  - 仓库内容 = 现有 `plugins/dsh-memory/` 完整迁移（源码/测试/README/cordis.patch.yml/package.json）
  - 保留 CommonTrustProtocol 中的副本作为主仓库归档（或改为子模块/说明指向独立仓库）
  - 独立仓库可独立获得 star/issue/PR，符合官方列表形态
  - 附带收益：badge 徽章（官方列表顶部有 `awesome-dsh-plugin.com/badge.svg` 机制，独立仓库可直接挂）

### 问题 2：功能描述漏核心
- 现状（英文）：`Cross-session long-term memory with a knowledge flywheel, self-cognition, recursive reflection, and an importance-gated long-term memory gate.`
- 缺失：**多智能体**（multi-agent：蜂群/子体协作）与**时空记忆图**（spatiotemporal memory graph：时空坐标/语义时空图/条件空间）——这是灵枢区别于其他记忆插件（普通 SQLite 记忆库）的本质
- 其他记忆插件都是"记忆库"（vault/文件/引用式）——**灵枢是"时空记忆图"**，必须说清

---

## 二、修订后的条目（草案）

### 英文（一句话，~25 词，对齐官方风格）
```markdown
- [FuRongJun-1999/dsh-memory](https://github.com/FuRongJun-1999/dsh-memory) - Multi-agent spatiotemporal memory graph: cross-session long-term memory, knowledge flywheel, self-cognition, and an importance-gated long-term memory gate.
```

### 中文（对应一句）
```markdown
- [FuRongJun-1999/dsh-memory](https://github.com/FuRongJun-1999/dsh-memory) — 多智能体时空记忆图：跨会话长期记忆、知识飞轮、自我认知与重要性门控的长期记忆写入。
```

---

## 三、校对清单（校对通过项打 ✅）

- [ ] 链接指向独立仓库（FuRongJun-1999/dsh-memory）
- [ ] 英文描述覆盖核心：multi-agent + spatiotemporal memory graph + 关键能力
- [ ] 中文描述与英文一致
- [ ] 一句话、无营销词、无安装命令
- [ ] 分类：Memory ✅（不变）
- [ ] 仓库 `dsh-plugin` topic
- [ ] package.json `dsh.bundle`（已声明）
- [ ] npm 包与仓库关联（repository 字段指向独立仓库）

---

## 四、执行步骤（校对通过后）

1. **建独立仓库**：GitHub 新建 `FuRongJun-1999/dsh-memory`（public, MIT）
2. **迁移代码**：`plugins/dsh-memory/` 全部文件推送为新仓库初始 commit（含 README 更新：链接/徽章/独立仓库说明）
3. **更新 package.json**：`repository.url` → 独立仓库地址；发 npm 0.2.3（或 0.3.0，若 dsh.bundle 已发 0.2.2）
4. **更新 PR**：fork 中两条目替换为修订版（链接 + 描述）→ push（PR 自动更新）
5. **主仓库处理**：CommonTrustProtocol 中保留副本，README 加"独立仓库地址"指引（避免双份漂移）
6. **验证**：`dsh plugin add @furongjun1999/dsh-memory` 从 npm 安装（含 dsh.bundle）；e2e 回归

---

## 五、待确认点（校对时讨论）

1. 独立仓库名：`dsh-memory`？（与 npm 包名 @furongjun1999/dsh-memory 一致）
2. 描述草案是否准确表达灵枢？是否有更贴切的措辞？
3. CommonTrustProtocol 中副本去留：保留 + 指引，还是删除避免漂移？
4. npm 版本号：0.2.2（dsh.bundle）是否已发布？独立仓库后发 0.2.3？
