# B13 · 备份遗产清理批（待实施）· 2026-09-28 立项

| 项 | 值 |
|---|---|
| 状态 | ⏳ 待实施（2026-09-28 立项·校准式规格；**2026-10-09 立场翻转·删除式规格 v2 生效**——非 git 工作区亦不留 `.backup`，依据与查证见 §裁决更新；同日事后审核（🟡×5+🔵×5）整改并入见文末审核记录；v1 规格原文保留于下仅供考古） |
| 触发 | 考古立项——v1.0 `.backup` 惯例与 D11/git 立场相抵 |
| 关联决策 | D11（git 承载版本边界，本批是其一致性收尾）、D14（传感器语义微调：fail-open 不变，仅排除噪声源）、B&T Commit Protocol（提交纪律内置——删除式立场成立的前提） |
| 测试基线 | 规格写作时 231→232；2026-10-07 基线 237；**2026-10-09 现基线 248**（B15 收口后）——v2 实施时：保留引擎排除则 248→249，一并删除则 248 不变 |
| 材料来源 | 原 integration-plan.md §9 2026-09-28 当日条目（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留）；2026-10-09 裁决更新（历史消费查证 + v2.0 对照 + commit message 无害性查证，当日对话） |

## 立项与裁决

**背景**：接 Phase 5A 观察项讨论，追问原始亚马逊 v1.0（基线 `fc17ad5`，migrated from awslabs/aidlc-workflows）对历史制品的处理。git 考古结论：**v1.0 没有归档机制，只有文件级 `.backup` 备份**——全库 6 处 archive 提法全部是"备份放原文件旁边"（`{artifact}.backup` / `{artifact}.backup.{timestamp}`），无集中归档目录、无清理规则、无迭代概念、无 start fresh（"重来"靠模型手改 state）。另考实三点：v1.0 恢复是 load-all（Phase 3.1 分级阅读明确标注取代的就是它）；完成态无路由（D15 四环链路的上游原始形态是真空）；error-handling "Consider Fresh Start If: User requirements have changed significantly / Architectural decision needs to be reversed" 逐字为 v1.0 原文——D15 审核轮 🟡#1 修的第 5 现场即上游原始缺陷。

**遗产现状**：`.backup` 惯例在分叉中残留 5 处——error-handling.md:217（Restart Stage 恢复步骤）、:262（Before Starting Over 步骤 1，与步骤 6 引擎 `jump --fresh` 自动归档重复且为手动版）；workflow-changes.md:83（Type 3 重启当前阶段）、:106（Type 4 重启先前阶段）、:353（Best Practices "Archive First"）。相抵点：① 与 D11 冲突——版本历史已由 git 提交承载（B&T Commit Protocol 定死时序），`.backup.{timestamp}` 是并行第二历史层且无生命周期管理，v1.0 的目录污染原样潜伏；② 引擎传感器交互——`_stage_resumed_artifacts`（engine.py，引用以函数名为准）对 wildcard produces（`construction/{unit-name}/code/*` 等）按 glob 展开且"any single match counts"（契约 §7 resumed-artifacts 条），glob 树内的 `.backup` 文件会被计入命中、挤占 5 条上限；③ 无任何清扫规则。

**裁决（用户，2026-09-28）**：立项单独修复批。**校准立场（非全盘废除）**：AUD-02 / B&T R4 已有先例——非 git 工作区（no git → 标注 unknown、不阻塞）下破坏性重做前做轻量备份有真实价值，故条款改**条件式**而非删除。

**裁决更新（用户，2026-10-09）：校准式 → 删除式，上方 2026-09-28 裁决废止。**新立场：**有 git，历史由 git commit 承载，本地永远只保留最新真身；没有 git，说明用户自选放弃版本控制，不记历史——两种情况都不留 `.backup`。**

翻转依据（2026-10-09 三项查证）：

1. **历史双层模型查证**：aidlc 消费历史的全部时刻（恢复读审计 / 变更读 Revision Record / 规划读 Shipped Log + Deferred / 合流读对账锚点）都在**活文档的追加账**内；深历史（git、archive 目录、`.backup`）写而不读——规则文本全文 grep `git log|git diff|git show` 零命中；v2.0 的 `<record>/archive/` 同样零读回指令（stage-protocol-recovery.md:255-260 只写不读）。工作流运转零依赖取证层 → 无 git 丢弃取证层零功能损失。
2. **有 git 时树内副本是纯负资产**：D11 + B&T 提交纪律内置（build-and-test.md:368-385；全库提交点仅两处——B&T 门 = 迭代边界、完成仪式 rollup，规则 6 锚定提交哈希）→ git 一层两用（历史 + 回滚）；`.backup` 只带来目录污染 + 引擎传感器 glob 误计（原相抵点①③不变）。
3. **无 git 时 `.backup` 买不到任何工作流能力**：恢复读账本不读备份文件——`.backup` 仅买"恢复到昨天"的取证兜底，而这是用户自选放弃的。辅证：乱写 commit message 无害（机器只认哈希不读 message；engine.py 全文零 git 调用）——版本控制层对人几乎零约束成本，无需树内副本替代。

**适用边界（诚实限定，2026-10-09 审核整改补入）**：git 承载的是**已提交状态**（全库仅 B&T 门与完成仪式两处提交点）；迭代中途的制品在 B&T 门之前处于未提交态，此时 Type 3 / Type 4 的破坏性重做会不可恢复地丢失重做前内容（无 git 可回滚、无 `.backup` 兜底）——该损失由用户在重做批准门**明示承担**（批准话术不承诺"已备份"：`workflow-changes.md:136` 的 "(but backed up)" 括注随本批删除，`error-handling.md:83` "(data will be lost)" 即既有诚实范本）。无 git ↔ B&T 规则 5 的关系：规则 5 非 git 跳过整个提交协议并标 `unknown`（build-and-test.md:381）= 如实记录"无提交信息"，与"无 git 不记历史"同一立场。机制层三处保留不属本翻转范畴：`jump --fresh` 整树归档（破坏性操作安全闸，产物在树外）、engine glob 排除（见规格 v2 第 3 项——纯防御外部行为、非流程产物，与"本地只留最新"无涉）、AUD-02 git-config 读取（身份获取，与历史无关）。

与 v2.0 的对照结论（外部参照）：v2.0 树内自建 archive 买的是"不依赖人的提交纪律、由工作流自己保证的改前快照"（其制品树提交纪律外置，仅 doctor 提醒；但其并发机器硬依赖 git——认领锁走 `git commit-tree`、状态合并记 `git_commit_oid`）；我们提交纪律内置，git 一层两用，树内零副本。代价各一头：v2.0 付检索污染（archive 在树内且入 git，harness grep 照搜，结果截断时可挤掉活文档命中），我们付"协议必须被遵守"。分叉路线维持 D11。

SVN 议题（2026-10-09 讨论后作废）：曾考虑把 B&T 规则 5 判据从 no-git 泛化为 no-VCS（SVN revision 号是等价甚至更优锚点；引擎零 git 依赖天然兼容），用户裁定不泛化——现已无代码库在用，维持 git / 无版本控制二值模型，不为不存在的用户付文本成本。

## 规格 v1（校准式，2026-10-09 废止——由文末 v2 替代，原文保留供考古）

1. **文档 5 处改条件式**（git 工作区→当前状态先 commit 承载历史[对齐 AUD-02/B&T R4]；非 git 工作区→保留 `.backup.{timestamp}` 手动备份）：workflow-changes.md:83 / :106 / :353、error-handling.md:217；error-handling.md:262 特殊——改写为"归档交给引擎（见步骤 6 `jump --fresh` 自动归档整树），勿手动"，消除与步骤 6 的重复。
2. **engine.py `_stage_resumed_artifacts` glob 分支排除 `.backup`**：命中过滤 basename 含 `.backup` 的路径（精确事实：`_stage_missing_produces` 为精确路径匹配、免疫，不改动）。
3. **engine-contract.md §7 resumed-artifacts 条目**同步补一句排除规则说明。
4. **测试 +1**：wildcard produces 树内放置 `.backup.{ts}` 文件，断言不计入 resumed 命中；同场景下正常文件仍命中。
5. **AGENTS.md** 测试数与路线图行随实施同步。

## 验收（v1，随规格废止）

全量测试全绿 + `generate.py --check` 零漂移 + 全树 grep 无"无条件 `.backup`"残留（`Archive existing artifacts` / `Archive First` 等短语均带 git/非 git 分支）。

---

## 规格 v2（删除式，2026-10-09 起现行）

1. **文档 6 处删除"改前手动归档"步骤**（不再条件式；行号为 2026-10-09 现状，实施首步以词表 `archive|backup|backed up|back up` 不区分大小写重扫对账——B12 减法后行号有漂移，旧立项时点名的 5 处对应现行 6 处；SKILL.md:104 / engine-contract.md:303 / resiliency 数据备份条目属异域保留，不在待删集）：workflow-changes.md:130（Type 3 步骤内）/ :153（Type 4 步骤内）/ :318（"Archive Existing Work: Always backup"）/ :400（"Archive First: Always backup"）、error-handling.md:84（Restart Stage 恢复步骤 2）/ :129（Before Starting Over 步骤 1）。git 情形由 B&T 门提交天然覆盖（规则 2：first-class 文件按 stage/unit 分组提交，second-class 从不自动 stage）；无 git 情形按新立场不备份。
2. **删除后的编号与衔接修复**（2026-10-09 逐处核实）：真正需重排编号的是**四处有序列表**——workflow-changes.md:318（During Changes 1–5，删项 1 后 2–5 → 1–4）、:400（Best Practices 1–8，删项 4 后 5–8 → 4–7）、error-handling.md:84（Restart Stage 步骤 2 删后 3–5 → 2–4）、:129（Before Starting Over 步骤 1 删后 2–6 → 1–5）；Type 3（:130）与 Type 4（:153）的归档步是**无编号 bullet**，删除即无需编号修复。两处文字衔接：workflow-changes.md:136 删 "(but backed up)" 括注（删步后成假陈述——整条改为 "Existing work will be lost"，与 error-handling.md:83 "(data will be lost)" 对齐）；error-handling.md:131 "Identify what to preserve" **保留**（删归档步后仍有独立语义：起新计划前确认哪些内容携带进入），不随删。Before Starting Over 的归档职责删后由步骤 6 `jump --fresh` 独占（消除 v1 立项点名的"手动版与引擎自动归档重复"）。
3. **engine.py glob 排除 `.backup` + 测试 +1：批内待裁决**——删除全部生产者后属纵深防御，且为**纯防御外部行为产生的文件、非流程产物**（与"本地只留最新"立场无涉），防其污染 `_stage_resumed_artifacts` 命中。**推荐保留**（1 行过滤 + 1 测试，便宜）；备选一并删除（更彻底，实施首步问用户终判）。若保留：engine-contract.md §7 resumed-artifacts 条同步补一句排除说明；若删除：v1 规格 3/4 两项整体取消。
4. **`jump --fresh` 整树改名保留**（裁决，非待裁决）：`aidlc-docs/` → `aidlc-docs-archive-{时间戳}/`（engine.py:1386-1401）是破坏性操作的安全闸（防误触 Start Fresh 不可逆丢数据），不属"记历史"范畴，且产物在制品树外不污染检索——engine-contract.md:248 描述不动。
5. **登记同步**：本档案即登记；integration-plan **两处**（§3 批次登记表 B13 行随 v2 更新为删除式与现行测试基线；§6 开放项行已同步）；AGENTS.md B13 行注明删除式 v2，测试数随实施更新。

## 验收（v2）

全量测试全绿 + `generate.py --check` 零漂移 + references/ 与 SKILL.md 全树 grep（词表 `archive|backup|backed up|back up`，不区分大小写）命中**仅剩三类保留项**——① `jump --fresh` 引擎整树归档描述（engine-contract.md:174/:248、error-handling.md:126/:134、session-continuity.md:31/:88/:90、workflow-changes.md:23、autonomous-mode.md:162）；② 状态标记行恢复提示语（SKILL.md:104、engine-contract.md:303——"restore … from a backup" 泛指人工备份，非 `.backup` 文件条款）；③ resiliency-baseline 数据备份条目（RESILIENCY 领域，与制品备份无关）——无任何"改前手动备份"写入指令残留。

## 事后审核记录（2026-10-09，reviewer 续审）

结论：**暂缓实施、先整改**——清单主体（6 处待删）与翻转方向成立，🟡×5 + 🔵×5 全部采纳并入本档案：v2 第 1 项词表扩容并声明异域保留集（P3/P6/改进2）；第 2 项重排清单改指四处有序列表、补 :136 假陈述修复与 :131 保留裁决（P1/P2/P7）；裁决更新补适用边界与规则 5 勾连、机制三保留项一句话理由（P5/P8/建议2）；登记同步补 integration-plan 批次表行（P4）；"与既有决策的关系"移至文末并标注两版通用（P10）。V1~V6 主张判定：V1 部分成立（清单穷尽、保留项枚举漏——已补全），V2~V6 成立。

## 与既有决策的关系（v1/v2 两版通用）

D11（git 承载版本边界）不动摇，本批是其一致性收尾；D14 传感器语义微调（fail-open 不变，仅排除噪声源）；`jump --fresh` 树级归档行为不变。

## 增补（2026-10-10，冗余清理交互）

2026-10-10 全量审查冗余清理（commit log 为记录）收敛了 error-handling.md 与 workflow-changes.md 的重复表述，本批规格 v2 待删面随之变化：

- **error-handling.md:84**（Restart Stage 手动归档步）与 **:129**（Before Starting Over 步骤 1 "Archive all existing work"）**已提前消解**——前者随 "User Wants to Restart Stage" 收敛为 Type 3/4 指针而消失，后者按本批 v2 已裁决的删除式立场随冗余清理落地（归档职责由 `jump --fresh` 步独占；:131 "Identify what to preserve" 按第 2 项裁决保留；:83 "(data will be lost)" 诚实范本原样）。
- **剩余待删面**：workflow-changes.md:130 / :153 / :318 / :400 四处 + :136 "(but backed up)" 假陈述修复；有序列表重排仅剩 workflow-changes 两处（:318 During Changes、:400 Best Practices）。
- 实施首步词表重扫（v2 第 1 项）与验收 grep 口径不变。
