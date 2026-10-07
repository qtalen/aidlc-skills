# B07 · 完成态再入修复批（旧称：修复批）· 2026-09-27

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-27；审核轮 2026-09-28） |
| 触发 | dogfood 反馈——completed 工作流上的同产品新需求被推向 `jump --fresh` |
| 关联决策 | D15（完成态再入语义） |
| 测试基线 | 205 → 209 |
| 材料来源 | 原 integration-plan.md §9 2026-09-27 条目（含 09-28 独立审核）与 09-28"D15 代价面讨论"（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**触发**（用户 dogfood 实报）：计算器 MVP 全流程完成后，新开会话加一个新功能，模型选择 `jump --fresh`（整树归档重建），而非就地迭代。

**根因诊断**（四环链路，逐处代码考证）：
1. engine `cmd_jump` 在 current=None 时直接 invalid-jump，**hint 亲口指路 jump --fresh**；park 的 workflow-complete 错误同款 hint（两处"教唆现场"）。
2. SKILL.md bootstrap 表 completed 行只有一句 "confirm with the user before starting anything new"，无路由指引。
3. 恢复菜单 A 空转（"none — workflow complete"）、B 是导航框架、C 是唯一写着"开始"的选项。
4. workflow-changes.md 标题与 Overview 域限定 "Mid-Workflow"，严谨的模型不会把完成态新需求往其上套。

四环合流：模型无论主动选择还是试错（先试 B 被拒、按 hint 走 C），必然收敛到 `--fresh`——不是模型不守规矩，是系统把它推过去的。`--fresh` 的实际代价：FR 编号重置（跨迭代追溯链断）、迭代一 requirements/stories 上下文被封存（新流程默认不读归档）、RE 产物被一起搬走（迭代二大概率重跑逆向工程）。

**用户裁决（=D15）**：同产品的功能演进不是产品意图变化，应走就地再入（路径一）。

## 实施与实施期裁决

主智能体直做（引擎多耦合）：
- engine.py：`cmd_jump` 完成态分支由拒绝改放行——direction=backward、目标及其后重置 `[ ]`、from_label="complete"、审计 detail 记 "re-entry; stages from X onward reset"、ack.from=null；裁决③（jump 不绕过计划过滤、目标在计划外时 note 提示）对再入同样生效；park 的 workflow-complete hint 改写为"同产品→`jump --stage` 再入；新意图→`--fresh`"。完整性交叉核验天然兼容（重置产生的 `[ ]` 不在核验范围，此前的完成事件仍匹配未重置阶段的 `[x]`）。
- **实施中发现的真实语义**（测试首跑失败实证，记录在案）：若模型先清掉 Skip 行，工作流会经既有 Type 1 通道**自行复活**（current 重算为第一个待办阶段）——再入分支覆盖的是"全做完"场景；两条通道并存，规程均已收录（Re-Entering 节步骤 1 提示按需更新计划行）。
- 文档同步 6 文件 8 处：engine-contract（§8 再入条目 / §9 jump 行 / §10 park 样例 hint）；SKILL.md completed 行（同产品→jump 就地修订并明示禁止对同产品用 Start Fresh 及理由）；session-continuity（菜单 C 定位收缩 "for a new product intent … NOT for a new iteration" + Menu Execution 补完成态同产品请求指 B 的条款）；workflow-changes（Overview 域扩展至完成态 + 新增 "Re-Entering a Completed Workflow" 节：分类→jump 最上游受影响阶段→就地修订[resumed-artifacts / DOC-04 / Deferred 编号不回收]→重走；新意图→--fresh 或新 git 版本）；AGENTS.md；integration-plan。

## 验证

测试 205 → **209** 全绿。新增 4 例——再入主路径（from=null / direction=backward / current=目标 / 目标前后勾选分界 / 审计含 re-entry / integrity ok / next 重发目标）、再入首阶段（全重置）、再入计划外目标（note 提示，裁决③）、再入后 park 可用（D13 交互）；辅助两个：`_drive_to_done` 与 `_drive_all_classic_to_done`。

## 与既有决策的关系

D11（一版本一意图）不变——同产品多迭代 = 同一意图下的多个版本，版本边界由 git 提交承载（B&T Commit Protocol）；aidlc-docs 为跨迭代活文档，与 fx991 单树两迭代先例、Type 10 / Deferred 编号纪律的既有立场一致。`--fresh` 语义不变，仅定位收缩为"新产品意图 / 显式干净重启"。

## 实施后审核与修复（2026-09-28，reviewer 静态全量审查）

裁决"**有条件通过，无阻断项，代码与测试本体可作提交依据**"：0🔴 / 1🟡 / 6🔵；四条待验证主张独立裁决（主张1 证实无缺陷；主张2 部分证实——"计划行先改→自行复活"语义真实但有一处次序歧义；主张3 证实——断言过弱；主张4 部分证实——真实残留 1 处类别 + 2 处弱形式）。正向确认 10 项。发现全部当场修复：🟡#1 error-handling.md "When to Suggest Starting Over" 将"需求大变/架构反转"列为 Fresh Start 触发条件（与 D15 相抵的同源失效第 5 现场）——移出清单、限定为"新产品意图/引擎不可恢复"，加 same-product 从不 fresh-start 条款并指向 workflow-changes；弱形式 :342 Resumption 选项同步。🔵#2 计划外目标测试补三断言钉死裁决③落点语义；🔵#3 契约 §8 再入条补"不绕过计划过滤"条款；🔵#4 Re-Entering 步骤 1 补次序分支（计划行先改→工作流自行复活→勿 jump 直接 `next`）；🔵#5 engine jump 的 note 文案补"若在 Stages to Skip 行则先删——Skip 恒胜 Execute"前提；🔵#6 AGENTS.md 决策区间 D1-D14→D1-D15；🔵#7 本条目自述计数修正。修复后终态：209 全绿 + --check 零漂移；变更集扩为 9 文件（+error-handling.md）。

## 附注：D15 代价面讨论（2026-09-28，挂 Phase 5A 观察项）

D15（完成态再入、单树活文档）落地次日，用户提出设计追问：所有迭代的制品集中于同一 `aidlc-docs/`，文件与文档长度会不会随迭代数"爆炸"并拖累上下文。

**分析结论**（查证各阶段 produces/consumes + session-continuity 分级阅读 + workflow-conventions DOC-04/DOC-06）：

- 文件数增长 = O(功能/单元数)，**非** O(迭代数)：固定路径活文档跨迭代原地更新、文件数恒定；仅 per-unit 树随单元数增长。D15 之前"归档旧树 + 新建"模式才是 O(迭代数 × 全文件) 的爆炸路径——D15 恰是消除文件爆炸的决策；版本历史由 git 提交承载，磁盘不留快照。
- 上下文与目录大小解耦（三道闸门）：① status 恢复简报只返回异常发现；② tier-2 只加载当前阶段 required consumes 且圈定细到单元；③ tier-3 按需 + DOC-06 导航索引 + CTX checkpoint。
- **真实残余风险（挂档对象）**：① **单文件单调增长**——stories.md 类 current-state 制品按契约只增不减（Type 10 原地更新 / Deferred 永久保留 / DOC-04 修订记录 append-only），增长 = O(历史功能总数，含 Deferred)，粗估 15-20 个故事过 DOC-06 300 行阈值，而 DOC-06 是全库唯一 advisory 无硬触发；② **build-and-test 全单元 consumes**——唯一输入随产品规模线性增长的阶段。

**裁决（用户）**：不立即设计压缩规程（避免过早设计未被实证的规则），挂 **Phase 5A 观察项**（见主文档路线图 Phase 5A 节）。触发条件：核心活文档过 500 行或全量读产生可感知上下文压力。届时方向：rollup 约定（shipped-stable 条目压缩为一行索引 + git commit 指针，编号永不回收——与 Deferred 编号纪律同构）+ DOC-06 升"超线必做"评估；知识树（5A 本体）为长期解。首批实证（fx991 三迭代，stories.md 达 356 行、requirements.md 出现自发 rollup）见 B09 档案。
