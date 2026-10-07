# B13 · 备份遗产清理批（待实施）· 2026-09-28 立项

| 项 | 值 |
|---|---|
| 状态 | ⏳ 待实施（2026-09-28 立项，规格与考古证据已收口） |
| 触发 | 考古立项——v1.0 `.backup` 惯例与 D11/git 立场相抵 |
| 关联决策 | D11（git 承载版本边界，本批是其一致性收尾）、D14（传感器语义微调：fail-open 不变，仅排除噪声源） |
| 测试基线 | 规格写作时 231→232；**截至 2026-10-07 现基线 237**（B12 收尾批后），实施时 237→238 |
| 材料来源 | 原 integration-plan.md §9 2026-09-28 当日条目（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**背景**：接 Phase 5A 观察项讨论，追问原始亚马逊 v1.0（基线 `fc17ad5`，migrated from awslabs/aidlc-workflows）对历史制品的处理。git 考古结论：**v1.0 没有归档机制，只有文件级 `.backup` 备份**——全库 6 处 archive 提法全部是"备份放原文件旁边"（`{artifact}.backup` / `{artifact}.backup.{timestamp}`），无集中归档目录、无清理规则、无迭代概念、无 start fresh（"重来"靠模型手改 state）。另考实三点：v1.0 恢复是 load-all（Phase 3.1 分级阅读明确标注取代的就是它）；完成态无路由（D15 四环链路的上游原始形态是真空）；error-handling "Consider Fresh Start If: User requirements have changed significantly / Architectural decision needs to be reversed" 逐字为 v1.0 原文——D15 审核轮 🟡#1 修的第 5 现场即上游原始缺陷。

**遗产现状**：`.backup` 惯例在分叉中残留 5 处——error-handling.md:217（Restart Stage 恢复步骤）、:262（Before Starting Over 步骤 1，与步骤 6 引擎 `jump --fresh` 自动归档重复且为手动版）；workflow-changes.md:83（Type 3 重启当前阶段）、:106（Type 4 重启先前阶段）、:353（Best Practices "Archive First"）。相抵点：① 与 D11 冲突——版本历史已由 git 提交承载（B&T Commit Protocol 定死时序），`.backup.{timestamp}` 是并行第二历史层且无生命周期管理，v1.0 的目录污染原样潜伏；② 引擎传感器交互——`_stage_resumed_artifacts`（engine.py，引用以函数名为准）对 wildcard produces（`construction/{unit-name}/code/*` 等）按 glob 展开且"any single match counts"（契约 §7 resumed-artifacts 条），glob 树内的 `.backup` 文件会被计入命中、挤占 5 条上限；③ 无任何清扫规则。

**裁决（用户，2026-09-28）**：立项单独修复批。**校准立场（非全盘废除）**：AUD-02 / B&T R4 已有先例——非 git 工作区（no git → 标注 unknown、不阻塞）下破坏性重做前做轻量备份有真实价值，故条款改**条件式**而非删除。

## 规格（待实施清单）

1. **文档 5 处改条件式**（git 工作区→当前状态先 commit 承载历史[对齐 AUD-02/B&T R4]；非 git 工作区→保留 `.backup.{timestamp}` 手动备份）：workflow-changes.md:83 / :106 / :353、error-handling.md:217；error-handling.md:262 特殊——改写为"归档交给引擎（见步骤 6 `jump --fresh` 自动归档整树），勿手动"，消除与步骤 6 的重复。
2. **engine.py `_stage_resumed_artifacts` glob 分支排除 `.backup`**：命中过滤 basename 含 `.backup` 的路径（精确事实：`_stage_missing_produces` 为精确路径匹配、免疫，不改动）。
3. **engine-contract.md §7 resumed-artifacts 条目**同步补一句排除规则说明。
4. **测试 +1**：wildcard produces 树内放置 `.backup.{ts}` 文件，断言不计入 resumed 命中；同场景下正常文件仍命中。
5. **AGENTS.md** 测试数与路线图行随实施同步。

## 验收

全量测试全绿 + `generate.py --check` 零漂移 + 全树 grep 无"无条件 `.backup`"残留（`Archive existing artifacts` / `Archive First` 等短语均带 git/非 git 分支）。

## 与既有决策的关系

D11（git 承载版本边界）不动摇，本批是其一致性收尾；D14 传感器语义微调（fail-open 不变，仅排除噪声源）；`jump --fresh` 树级归档行为不变。
