# B05 · Trellis 借鉴立即批（旧称 Phase 3.2）· 2026-09-22

| 项 | 值 |
|---|---|
| 状态 | ✅ 已完成（2026-09-22，单日开工即收尾） |
| 触发 | 调研借鉴——B04 立项同日的 Trellis 调研产出四档借鉴清单 |
| 关联决策 | — |
| 测试基线 | 144 → 169 |
| 材料来源 | 原 integration-plan.md §7 Phase 3.2 + §9 2026-09-22 及续三/续四（本文为 B14 文档重组批 [2026-10-07] 迁移聚合，原文保留） |

## 立项与裁决

**过程**：①对 Trellis 文档库与技能市场做补充调研（spec 冷启动/活树模板/真实案例/evidence-first 领域技能范式），与既有调研（B04 立项同日）合并产出**四档借鉴清单**（①立即 5 项/②排期 3 项/③相位触发 8 项/④仅记录 3 项）。②据清单起草本批实施计划（7 个工作包 + Phase 5A 骨架），经三轮独立 reviewer 审核。

**三轮审核（模型各异，全部发现经主智能体逐条考证属实后消解）**：
- **R1**（引导性提示词）：1🔴（WP-1 三类白名单与阶段文件 MUST 指令冲突）+ 6🟡 + 8🔵。微观精确度高（指南自带示例自相矛盾、QT-01 条件口径、步号自引用、规则 9/11/16 已覆盖的测试名证据）。
- **R2**（中性提示词，换模型）：1🔴 + 7🟡 + 4🔵 + 6 建议。系统思维最强——独有发现：四档清单无源、**消融臂违宪**（D6 + Only-next-routes 使无引擎对照契约性不可行）、AM-03 阻塞、扩展"第三态"无先例、串行理由失实（3.2 实不触 SKILL.md）。
- **R3**：因 opencode 服务中断两次未完成，放弃。
- **R4**（新 reviewer 定义首跑）：1🔴 + 7🟡 + 6🔵。首次出现"核对通过项"正向确认节与显式不可核验范围声明；独有发现：knowledge_refs 依赖悬空（指向"讨论记录待并入"的 result-oriented-delegation-design.md）、扩展 opt-in 豁免缺失、知识树×working-conventions 两套存储风险。**方法学副产物**：比较两轮完成的审核确认中性提示词优于引导性提示词（R2 在无预埋条件下覆盖 R1 全部发现且增量更重），据此修订了 reviewer/architect/executor 三个子代理定义与全局 AGENTS.md 委派纪律（反锚定协议+待验证主张+路径委派；属 opencode 全局配置，非本仓库变更，特此记录以解释后续审核行为的变化）。

**合并裁决要点**：Evidence-First Policy 含优先级条款与扩展豁免 + 8 文件 sweep（D23 通用化）；DOC-06 首条 advisory + 排除表；WP-5 通 produces 自动覆盖（删 promote）；WP-4 时序定死（门批准→report→commit 计划入完成消息）+ AM-03 不自动 commit + 非 git 回退；WP-2 度量 2 降定性 + 消融改历史/开关对照；5A 定性为按需加载约定条款（复用两态）；WP-7 扩三件套 + Phase 4 设计输入 6 项（新增任务信封设计稿处理）。

**产出**：本档案规格（已裁决待实施，前置 P0 已自解）；同日完成 WP-7-② 前移——Phase 5+ 拆写为 5A（知识树与学习闭环）/5B（reviewer 及其他）+ 映射注、Phase 4 节末挂 Trellis 设计输入 6 项、④档三项入不排期。工时 ~10-12h，顺序 P0→WP-7→6→1→3→5→4→2→收尾。

## 规格

**批次与前置**：Phase 3.1（B04）→ **本批** → Phase 4 → 5A → 5B。串行理由（R2/R4 修正）：**仅 integration-plan.md 与 AGENTS.md 共享**（本批各内容 WP 不触 SKILL.md）。原则：frontmatter 零改动；generate.py --check 例行验证。

**实施状态表**：

| 工作包 | 状态 |
|---|---|
| P0 四档清单落盘 | ✅ 已自解 |
| WP-7 落档（①登记表 ②5A/5B 拆写 ③状态段） | ✅ 完成（②为立项时前移完成，开工核验无漂移） |
| WP-6 契约硬规则单测清零 | ✅ 完成（+25 测试：规则 1-8/10/12-15 全覆盖，含保留键 reviewer/sensors 夹具与规则 12 的 SKILL_ROOT patch 法；零契约-实现出入） |
| WP-1 Evidence-First 提问纪律 | ✅ 完成 |
| WP-3 DOC-06 导航索引 | ✅ 完成 |
| WP-5 RE 可选产物 | ✅ 完成 |
| WP-4 B&T 提交协议 | ✅ 完成 |
| WP-2 dogfood 协议 | ✅ 完成 |
| 收尾（登记表回填/测试数刷新/全量验证/一致性 sweep） | ✅ 完成 |

**WP-1 Evidence-First 提问纪律**（~120 行）：
- a. question-format-guide.md 顶部新增 **Evidence-First Policy**，含优先级条款（探索优先覆盖各阶段 "when in doubt, ask" 类指令——overconfidence=不查就假设）与豁免表：可由代码库/制品探索回答的问题必须由探索解决（引用来源），不进问题文件。**豁免**：RA Step 2.5 scope 聊天问题（既有唯一聊天豁免）；**扩展 opt-in 问题**（RA Step 5.1 MANDATORY 项，天然非探索可解）
- b. Multiple Choice Guidelines 补两要素：**when a recommendation exists** 时必含 Recommendation（含一句话理由）+ "If you choose otherwise" trade-off 行
- c. 排序纪律与既有 Best Practices #3（one topic）合并表述
- d. **系统性收口 sweep（D23 先例通用化）**：8 个产问题的阶段文件各加 1 行指针；overconfidence-prevention.md 的 "Default to Asking" 处加同款指针
- e. 自洽修复：指南示例（数据库选型/部署目标/架构模式等非三类问题）改写或标注；Question Structure 模板与 Summary 清单同步两要素
- 验收：**全树 grep 无相抵指令**

**WP-3 DOC-06 导航索引（advisory）**（~30 行）：workflow-conventions.md Group 1 新增 DOC-06——≥300 整行的 aidlc-docs **内容制品**（创建或实质更新）须顶部维护"任务→章节"导航表，覆盖全部 H2（可机械核对）。**排除**：audit.md（append-only 互斥）、aidlc-state.md/handoff.md（引擎独占）、checkpoints（≤200 行上限）、问题文件（QT/DOC-04 辖区）。声明为该文件**首条 advisory 规则**（Blocking 行为节注明 advisory=列出不阻断；理由：缺失无危害，blocking 训练用户无视 findings）。同步：Overview 行 DOC-01~05→01~06；Enforcement Integration 表补收窄语境行。

**WP-5 RE 可选产物**（~30 行）：reverse-engineering.md Step 9 与 Step 10 之间新增**无编号小节** "Optional Artifact: Working Conventions"（禁重编号）。落点 `aidlc-docs/inception/reverse-engineering/working-conventions.md`——**位于既有通配 produce 内，自动进入会话加载清单与 3.1 resumed-artifacts 探测，无需 frontmatter 改动**。内容纪律：source-backed（每条约定带来源路径引用，拒绝空话）；**定位为 Phase 5A 知识树的种子/导入源**（防两套约定存储分叉）。同步：Step 10 时间戳/产物清单提及；Step 12 完成消息列出。

**WP-4 B&T 提交协议**（~50 行）：build-and-test.md **Step 9 内**新增 "### Commit Protocol"，**时序定死**：门批准 → `report approved` → 完成消息正文呈现 commit 计划 → Approve & Continue 语义含"执行 commit 计划"（**实施后审核更正**：原文顺序可歧读为"批准后才呈现计划"；实施定序为"完成消息含计划先呈现 → Approve & Continue 即阶段批准+执行授权 → `report approved` → 执行"）；拒绝 → Request Changes / 手动路径。内容：①脏文件二分，判定依据=**本会话工具调用实际写过的路径**，其余一律二类列出、绝不静默暂存；②一次性展示 commit 计划（含阶段与单元）；③禁 amend、禁 push（用户显式要求除外）；④**非 git 工作区**：对齐 AUD-02 先例（no git → 标注 unknown，不阻塞，跳过协议）；⑤commit 计划与确认结果入 audit，hash 记入 build-and-test-summary.md；⑥顺序：工作成果 → **若存在**归档/handoff 待提交项则其后（条件式）。**AM-03 自主模式**：不自动 commit，完成消息列出待提交清单。

**WP-2 dogfood 协议**（新文件 docs/dogfood-protocol.md，~120 行）：六条度量——①重复解释次数→audit 条目趋势 ②PRD 范围清晰度→**定性项** ③重复评审→rejected/revised 趋势 ④换工具稳定→引擎 JSON 一致性 ⑤新人首任务独立完成→定性 ⑥RCA bug 沉淀率→5A 后生效。消融对照=**历史对照**（Phase 3 前后 dogfood 记录）+ **引擎内开关对照**（park/软警告 on-off）；显式注明"无引擎臂在当前契约下不可构造"（D6 HARD STOP + Only-next-routes）。定位：**服务 3.1 落地后的首个 dogfood 周期**。

**WP-6 契约硬规则单测清零**（~300-400 行）：映射表**以模块 docstring 固化**在 test_generate.py；表首行注明规则 9/11/16 已覆盖；补 **reserved 键（reviewer）夹具**锁定契约 §5 预留命名空间。

**Phase 5A 骨架（WP-7 落档，不实施）**：位置 `aidlc-docs/knowledge/<domain>/index.md`（index 只路由）；条目 frontmatter 预留 `governs:`。机制定性：**按需加载的复盘约定条款**，复用两态扩展体系，非新加载机制。写入仪式双触发：B&T 收尾自问 + 复盘触发器——判定者=**模型**、计数窗口=**同单元连续失败**、跨会话以 handoff/audit note **best-effort** 续。内容纪律：可执行契约模板；"分析留在聊天里=零"；超阈值拆分。学习双出口：约定→知识树条目 or→传感器提案（D14 finding 形态）。悬空依赖显式化：knowledge_refs 完整设计见 docs/result-oriented-delegation-design.md（待 Phase 4 设计输入第 6 项处理）。

**四档清单（规格存档）**：

| 档 | 项 | 去向 |
|---|---|---|
| ①立即（5） | brainstorm 三纪律 / 成功度量清单 / 消融对照 / 长制品导航索引 / 批量提交协议 | WP-1 / WP-2 / WP-2 / WP-3 / WP-4 |
| ②排期（3） | 单层活知识树闭环 / spec 冷启动 / 契约硬规则单测清零 | 5A 立项（WP-7 落档骨架）/ WP-5（RE 可选产物为先行）/ WP-6 |
| ③相位触发（8） | 策展清单 / 派遣三件套 / channel 对照 / 单元依赖显式化 / spec 移植 / knowledge_refs 字段 / 学习双出口 / 任务信封设计稿处理 | Phase 4 设计输入（WP-7 清单 6 项）/ Phase 5 |
| ④仅记录（3） | 技能版本戳 / 模板升级保护 / evidence-first 扩展范式（≠WP-1 提问纪律） | 技能分发/升级阶段再议 |

**顺序与验收**：P0 → WP-7 → WP-6 → WP-1 → WP-3 → WP-5 → WP-4 → WP-2 → 收尾。总工时 **~10-12h**（WP-6 前置去风险——最大最易超时项压尾会拖垮总验收；WP-4 交叉契约面最大放后吸收结论；WP-2 纯文档殿后备用）。

**不做（十项）**：per-unit missing 精确覆盖（Phase 4）｜report 硬阻断｜审计分段实现｜CTX 转正｜missing-produces 自动补写｜handoff 模型直读｜per-produce required 标记（gen-2）｜存量项目头部须知迁移｜**SKILL.md 问答概述指针（可选镀金）**｜**RA 模板加 out-of-scope 节（度量 2 已降定性）**。

## 实施（2026-09-22，开工即收尾，同日完成全部 7 个工作包）

并行分发 3 个 executor（WP-6 测试 / WP-3+5+4 文档 / WP-2 新文档）；WP-1 强耦合由主智能体直做。要点：

- **WP-6**：test_generate.py +367 行/25 测试；映射表以模块 docstring 固化（含规则 12 的 SKILL_ROOT 调用期 patch 方法说明）；保留键 reviewer/sensors 夹具；实施中发现规则 7 实际校验点在 `_validate_references` 而非 build_stage——按实际实现测试，行为与契约一致，零出入。
- **WP-1**：Evidence-First Policy（优先级条款 + 豁免表）；Recommendation and Trade-off 小节；排序纪律并入 Best Practices #3；模板与 Summary 同步；6 处探索可解示例全部标注；sweep 落地 9 文件。验收达成：全树 grep 各 ask-aggressively 指令均有相邻门控从属化，无孤立相抵指令。
- **WP-3**：DOC-06 导航索引（advisory）；排除表；:21 补 Advisory 例外条款；Overview 与 Enforcement 表同步。
- **WP-5**：RE 无编号小节（步号零重排）；source-backed 纪律；5A 种子定位；免 frontmatter 改动；Step 10/12 同步。
- **WP-4**：Commit Protocol 子节，时序定死（**时序表述已于实施后审核更正，以 build-and-test.md Commit Protocol 新序为准**）；六条内容；AM-03 不自动 commit。
- **WP-2**：docs/dogfood-protocol.md：六条度量（2/5 定性、6 待 5A）、消融对照（显式声明无引擎臂不可构造）、数据源对齐 3.1、一次一表模板含软警告升级决策回填行。

**终态**：测试 144 → **169** 全绿；--check 零漂移；登记表 7 行回填"已完成"；AGENTS.md 测试数与路线图同步。规格两处既知小漂移（WP-5 ":302 步号自引用"锚点过期、测试基线数 102→144）均在就绪核查中预判并按语义稳健指令处置，无实施影响。

## 实施后审核与修复（同日两轮）

**实施后审核**：裁决"通过，可作为提交依据"，0🔴/1🟡/4🔵；五主张裁决：A 证实（Neo4l 虚惊无残留）、B 部分证实（overconfidence :60/:74/:100 三行无相邻门控，验收条款实质达成/字面未全达）、C 证实（映射表 16 规则无遗漏，30+25=55 与 114 合计 169 精确吻合）、D 实质满足（行内门控约束力强于指针行）、E 证实（步号顺移无交叉引用破坏）。发现全部当场修复：🟡六条负债挂档（见下）；🔵 overconfidence 三行补门控半句、AGENTS.md Phase 3.1 行改"当时 144 例"范式、B&T Commit Protocol 时序句重排（消除"批准后才见计划"的歧读）、四档清单加"已迁入登记表，以登记表为准"标记。

**第二轮审核（reviewer 复审修复轮）**：裁决"修复轮通过（0🔴/0🟡/2🔵），可作为提交依据"。两条 🔵 当场修复：旧序两处（规格与变更记录内）加"审核更正，以 build-and-test.md 新序为准"指针、overconfidence :62 补门控半句。命令级验证由主智能体代跑闭合：169 全绿 + --check 零漂移。

## 遗留与去向

负债挂档（六项）：①WP-5 通配单列 per-produce 决策→gen-2（未决）；②5A 触发器跨会话计数 best-effort→Phase 5A 设计输入（未决）；③WP-4 二分语义随 Phase 4 claim/merge 重审→Phase 4 设计输入（未决）；④登记表漂移风险→已由收尾回填对冲，长期靠"以登记表为准"标记；⑤消融无引擎臂违宪→永久（除非契约变更）；⑥四档清单状态列"计划中"待收尾刷新→已消解（收尾回填完毕）。

## Trellis 借鉴登记表（2026-09-22 续三落档，收尾已回填状态）

| 档 | 项 | 去向 | 状态 |
|---|---|---|---|
| ①立即 | brainstorm 三纪律 | WP-1（Evidence-First 提问纪律） | 已完成（2026-09-22） |
| ①立即 | 成功度量清单 | WP-2（dogfood 协议） | 已完成（2026-09-22） |
| ①立即 | 消融对照 | WP-2（dogfood 协议） | 已完成（2026-09-22） |
| ①立即 | 长制品导航索引 | WP-3（DOC-06） | 已完成（2026-09-22） |
| ①立即 | 批量提交协议 | WP-4（B&T Commit Protocol） | 已完成（2026-09-22） |
| ②排期 | 单层活知识树闭环 | Phase 5A 立项（骨架已落主文档路线图） | 已落档（实施在 Phase 5A） |
| ②排期 | spec 冷启动 | WP-5（RE 可选产物为先行） | 已完成（2026-09-22） |
| ②排期 | 契约硬规则单测清零 | WP-6 | 已完成（2026-09-22） |
| ③相位触发 | 上下文策展清单 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | 派遣三件套 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | channel 事件日志 vs claim 注册表对照 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | 单元依赖显式化 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | spec 移植模式 | Phase 4 设计输入 | 已落档（实施在 Phase 4） |
| ③相位触发 | knowledge_refs 字段 | Phase 5A | 已落档（设计稿 docs/result-oriented-delegation-design.md，处理挂 Phase 4 输入第 6 项） |
| ③相位触发 | 学习双出口 | Phase 5A | 已落档（实施在 Phase 5A） |
| ③相位触发 | 任务信封设计稿处理 | Phase 4 输入第 6 项 | 已落档（实施在 Phase 4） |
| ④仅记录 | 技能版本戳 | 技能分发/升级阶段再议 | 已落档（不排期，带触发条件） |
| ④仅记录 | 模板升级保护 | 技能分发/升级阶段再议 | 已落档（不排期，带触发条件） |
| ④仅记录 | evidence-first 扩展范式 | 技能分发/升级阶段再议 | 已落档（不排期；**与 WP-1 非同一物**：此项=扩展结构范式，WP-1=提问纪律） |
