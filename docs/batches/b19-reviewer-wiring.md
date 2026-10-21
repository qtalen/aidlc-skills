# B19 · Reviewer 前置接线批（待实施）· 2026-10-20 立项

| 项 | 值 |
|---|---|
| 状态 | ✅ 已实施并收口（2026-10-20 立项·同日单会话落地；两轮收口终审〔第一轮 6+4+5、第二轮 2+5+5〕全部处置后 **249 绿** + `--check` 零漂移；实施记录 §8、终审处置 §9；dogfood 迭代二验证——快照源 = 本批收口提交） |
| 归属 | Phase 5B 提前件（独立批，同 B18 先例；reviewer 状态机/传感器/persona/记忆仍留 5B） |
| 触发 | 2026-10-20 用户裁决七项（D-1~D-7——初版 D-1~D-3 + 规格 v1→v2 修订 D-4~D-7）+ 密度方案复议确认（三位置集中 vs 每门一审，维持前者）；根源 = B18 切分失误承认——"reviewer 要不要随 B18 落地"从未被摆上用户决策桌，被立项文档划为非目标（b18:119） |
| 关联决策 | D22/D23（门姿态与简报制——审查行嵌入门材料的形态基础）、D13（findings 永无权调引擎动词/改变流程结构）、brief §5-11 三位置接线（设计来源）；**本批产出 D24（实施时登记）**；D-6 三轮预算**取代** brief §5b"预算为一、分歧即升级" |
| 量级 | 本体 = 一个实施会话 + 收口终审（reviewer 全新会话，两轮姿态）+ 一次提交（触面 ≈ 4 阶段/公共文件锚点 + review-delegation.md + rubric 库 4 文件 + stage-contract 三处 + generate.py + 测试增补 + docs 五处 + dogfood-protocol） |
| 测试基线 | 立项时 239 全绿 + `--check` 零漂移（B18 后基线，实施首步实跑确认）；实施后 **249**（239+10：ReviewClassTests 3 + StageGraph 映射 1 + ReviewWiringTests 6〔含终审后补的门模板审查行断言〕） |

## 1. 立项背景与定位

1. **B18 的遗留缺口**：B18 只落门姿态（13 门降简报 + 四硬门 + AM 退役），reviewer 机制本体被划为 Phase 5B 非目标——但这个切分从未被用户逐项裁决，且处置地图备注栏"RA 自洽审查先跑"的写法有诱导性。用户本意是随 B18 把审核智能体提上来（2026-10-20 确认）。本批补上。
2. **dogfood 实证**：迭代一运行中用户发现无审查发生，被迫手动调用本机 reviewer 智能体补审——技能侧零审查接线的事实证据。
3. **设计来源**：brief §5-11 三位置接线 + §5-7 降级链 + §5b 修复验证（Phase 5B 立项底稿的可实施切片）。
4. **dogfood 衔接**：迭代一在另一会话跑完（快照已拷贝，本批施工不影响）；迭代二按新刷新规则换快照验证本批（快照源 = 本批收口提交）。**迭代二 scope 必须命中三位置**（建议 classic；bugfix/express 须先确认方向停点与 B&T 审查在该 scope 下触发）。
5. **口径澄清**：brief 三位置中的"常驻检查（简报阶段义务）"**不在本批**；rubric 五类中 evidence-credibility 与 security-threat 两类**留 5B**。

## 2. 已锁定裁决（D-1~D-7，全部用户 2026-10-20 拍板）

| # | 决策 | 内容 |
|---|---|---|
| D-1 | 接线密度 | 三点全上：RA 门材料前 + 方向门简报前 + B&T 收尾简报前。**2026-10-20 复议确认**（对照方案"每到原审批门审一次"——维持集中，理由：openspec 每批次挂审的 findings 再生教训〔brief §9〕、三层密度经济学〔传感器常驻/LLM 集中 2~3 点/人守三门〕、B18 刚消灭的覆盖错觉不在审查层复活、分诊税与成本线性膨胀；未来加密路径 = 校准回路按证据加点 + 单向升格，不做全局默认） |
| D-2 | 契约形态 | frontmatter 可选键 `review_class` + 生成器校验编译进 stage-graph.json + stage-contract 三处同步；注明"当前仅编译，尚无运行时消费者" |
| D-3 | 审查日志 | `aidlc-docs/reviews.md`，模型写、append-only 硬不变量，条目分 **R-n 审查（定格）/ T-n 处置（追加引用）** 两类 |
| D-4 | 遏制分寸 | **零快照（全域）**：RV-05 只含 L0（findings-only）+ L1（任务书只读条款）+ L2（harness 权限优先并标注档位）；轻量快照实践全面终止（取代 2026-10-19"实践期轻量替代"决策——技能级与仓库实践都不再记）。L3 全量挂账维持，两条触发条件**内联进技能文本**（运行期文本不引仓库 docs/ 路径）；触发条件②转被动发现。docs/reviewer-containment-design.md §6 随批补修正注记 |
| D-5 | 会话独立性 | 每次真实审查都在**全新会话**进行，永不复用/续用任何既有审查会话（含同点复审、跨点审查）。**唯一例外 = RV-04 ④ 同会话自审**——自审不是审查会话且必带 `degraded` 标注 |
| D-6 | 轮次预算 | 单个审查点事件最多 **3 次审查调用**；第 3 轮仍有未解决阻塞 → 升级 fork，禁止第 4 次。事件 = (阶段, 位置, 迭代号[, 方向轮次])；同迭代内再入/redo 不清零、累计计数；新迭代新事件。**取代** brief §5b"预算为一" |
| D-7 | B&T 审查内容 | 审**产出的代码**：bug/性能/架构/与制品文档匹配。**能力条件化**：依赖被禁工具（如 bash）才能核的维度不审、标 not-covered。**被审对象锚点按位置重定义**（RV-02 锚点表——代码不在任何 produces/consumes 里，必须显式给路径） |

`review_class` 挂载（per-unit 阶段锚定**轮级停点、每轮至多一次、不随单元重复**——写入 stage-contract §2 该行与 RV-01）：

| 阶段 | review_class | 审什么 |
|---|---|---|
| requirements-analysis | requirements-consistency | 契约自洽/边界可观测/非目标可证伪/验收判据可测/无静默缩水与范围蠕变 |
| code-generation | design-soundness | 设计阶段产物的决策风险/相对 RA 漂移/失败路径/集成风险（审文档，配强模型档） |
| build-and-test | code-quality | 产出代码的 bug/性能/架构/与制品文档匹配（审代码；执行依赖维度按 D-7 条件化） |

## 3. 交付物规格（实施简报正文）

### ① references/common/review-delegation.md（新，英文，RV-01~08）

- **RV-01 何时审**：三位置表（与 frontmatter 一一对应；CG 锚定轮级方向停点）。首步固定动作：读 `references/common/review/index.md` 解析 class→rubric 路径。
- **RV-02 任务书拼装**：rubric 路径（技能根解析后）+ **按位置锚点表** + 验收判据原文；禁止生产者自述。锚点表：RA = requirements.md + product-design.md（+roadmap）；CG = 四份设计产物（consumes）+ 棕地受影响代码路径（起点指针）；B&T = **本轮产出代码路径**（方向简报文件清单或 `git status`/diff；非 git 记工作文件清单）+ 设计/需求文档路径（匹配维度对照面）。
- **RV-03 输出契约**：findings-only；每条附证据（文件:行号）+ 门槛三元组（触发条件/兜底〔无则写明〕/实际后果——写不出后果的没有阻断权）；不调引擎动词、不开门、不顺手修复。术语避撞：称 *review finding*，显式区别于 workflow-conventions 的 Blocking Finding 合规流程。
- **RV-04 执行器与降级链**：① harness 专职评审 agent → ② 通用委派 + rubric → ③ 专家档（rubric 是镜头）→ ④ 无委派 → 同会话 rubric 二读标 `self-review (degraded)` 或记 `review unavailable`——绝不静默当作已评审。横向变体：子代理无文件读取 → 推模式（内联 rubric 全文）+ 标 `pushed-rubric`。**会话纪律（D-5）**：真实审查全新会话；④ 自审为唯一例外。tier + containment 档记审查日志（措辞不用"审计"）。
- **RV-05 遏制**：L0 + L1 常设，L2 优先并标注；零快照（D-4）；L3 挂账触发条件内联两句（权限防护不覆盖环境上的真实审查 / 无法解释的外部写入），不展开配方。
- **RV-06 分诊与修复验证**：三出口（修复/驳回留痕〔理由+下一门呈现〕/升级 fork）。事件定义与 D-6 预算；机械修复 → diff 核对（零 LLM）；语义修复 → scoped 复审（全新会话，原 finding + 修复 diff，只答二元，无新发现权）；**修复回灌**：B&T 审查产生的代码修复必须先重跑受影响测试并更新 build-and-test-summary.md（DOC-03）再呈现简报，否则渲染 `unreviewed-after-fix`。零阻塞 = 成功记录。
- **RV-07 审查日志**：细则见 ⑤。**强制首步**：进入审查点前读 reviews.md 本事件既有条目取已用轮次——计数以日志为准，不以会话上下文自估。
- **RV-08 密度护栏**：只在 frontmatter 声明位置审；禁自造审查点。门材料/简报审查行**状态+内容都承载**：`reviewed (tier ①, L2) — 2 blocking / 1 rejected (see reviews.md R-007)` / `self-review (degraded)` / `review unavailable` / `fork escalated` / `zero blocking` / `unreviewed-after-fix`。B&T 简报 4+1 行恰在 BRF-01 上限，超限按其自校准条款复议。

### ② rubric 库（新，英文）

`references/common/review/index.md`（~20 行，class→路径→一句话；注明另两类留 5B）+ `rubrics/` 三份（固定骨架 Scope/Dimensions/Finding format/Out of scope，各 40-60 行，只收机器检不了的维度）：requirements-consistency / design-soundness（标注建议强模型档）/ code-quality（Out of scope 段写明能力条件化：执行依赖维度无能力时跳过标 not-covered）。

### ③ 阶段锚点（英文）

| 文件 | 改动 |
|---|---|
| requirements-analysis.md | 门材料呈现**前**委派审查；门材料加审查行（RV-08 词汇表） |
| code-generation.md（方向门条款区） | 方向简报呈现**前**、等放行**前**委派（顺序写死：委派→简报→等放行）；简报加审查结果行 |
| build-and-test.md | **Step 9 简报呈现前**（commit 计划与授权问句前）委派；模板加核验行；审查修复先重跑测试更新摘要再简报 |
| workflow-changes.md（仪式段） | 一行：按 reviews.md 处置条目 tier 条件呈现核验状态 |

### ④ 契约与生成器

- generate.py：`ALLOWED_KEYS` 加 `review_class`（枚举三值，可选键，缺省合法）；编译进 stage-graph.json 节点（未声明则无键）。
- stage-contract.md 三处：§2 加行（含 per-unit 锚定语义）；§5 预留表摘出 review_class；§7 校验规则。
- 三阶段 frontmatter 加 `review_class` → 必跑生成器。
- 终审已代码核对（免运行时检查点）：engine.py 无节点 schema 校验、新增字段宽容；test_extension_layout 只覆盖 references/extensions/，`common/review/` 无布局约束。

### ⑤ 审查日志 aidlc-docs/reviews.md

- 模型写、零引擎耦合、首次审查时创建。归属：**不进任何 produces**（与 audit.md 先例不同——audit.md 是 workspace-detection 的 produces 被 SKIP_LOADING_ARTIFACTS 排除；reviews.md 直接不是产物）；工作流簿记文件，不进 session-continuity 加载表。
- append-only 硬不变量：只追加永不改删；**R-n 审查条目**（委派返回时定格：class/rubric、tier、model、session、round、findings、not-covered——不含 triage）+ **T-n 处置条目**（追加引用 R-n：triage、diff 核对/scoped 结论、关闭/升级）。回填禁止。双落点：加入 DOC-04 清单（"R/T 两类、禁止回填"例外语义写入双落点句）。
- rubric 版本记内容 sha256 前 12 位十六进制（截断长度写死）；session 行记 harness 会话句柄（无则 `fresh` + 时间戳）。
- 条目格式样例：

```markdown
## R-007 · requirements-analysis · iter 2 · 2026-10-22
- class/rubric: requirements-consistency (sha256:1a2b3c4d5e6f)
- tier: ① dedicated review agent | containment: mechanical read-only (L2)
- model: <model> | session: fresh (handle if available)
- round: 1 (event: requirements-analysis × gate-advisor × iter 2)
- findings: 2 blocking / 1 note
  - [B1] acceptance criterion 3 not observable (requirements.md:47)
  - [B2] non-goals missing falsifiable boundary (:12)
  - [N1] terminology drift "unit"/"module"
- not-covered: none (or: execution-dependent dimensions — bash denied)

## T-012 · R-007 · 2026-10-22
- triage: B1 fixed + diff-verified; B2 fixed → scoped re-review R-008 (resolved); N1 → assumption list → next gate
- event closed: round 2/3 used
```

- 体量 ~50 行/迭代，挂 5A 同款观察项（500 行阈值，届时裁拆分/归档）。

### ⑥ 测试

- 生成器：合法/非法/缺省 + **stage→class 映射断言** + **RV-01 表 ↔ frontmatter 交叉断言**（三份副本防漂移）+ index 路径存在性。
- 规则锚点断言：三阶段文件引用 review-delegation.md；workflow-changes 仪式行；DOC-04 清单含 reviews.md。
- 实施首步实跑全量取基线 → 239+N 绿 + `--check` 零漂移 + 引擎回归全绿。

### ⑦ 文档与登记（中文）

- 本档案补齐实施/验证节；**D24 登记**（三位置/全新会话含 ④ 例外/三轮预算与事件定义/降级链/findings-only/R-T 日志/技能级零快照）。
- integration-plan：:95 测试计数更新、:193 B18 行补后继指针、Phase 5B 节条目翻"已落地"、AGENTS.md :5/:15/:49 指针（D1-D24/B01-B19/例数）。
- **（立项时已预完成，实施勿重做）**：总账 B19 行、Phase 5B 节 B19 条目、integration-plan 与 AGENTS.md 的 B19+→B20+ 顺延（含 P9 挂账改 B20+）、AGENTS.md 待实施行加 B19、本档案创建。
- dogfood-protocol：§零补"迭代边界快照刷新规则"（迭代目标含验证新技能 commit 时允许刷新，记新 STAMP 行）；新增专项观测为**新 §四**，原 §四消融→§五、§五→§六、§六→§七、§七→§八（引用全用顺延后编号），文件头 :5 增补注记同步；§六（原 §五）数据源加 reviews.md；§七（原 §六）模板加第 9 行；§八（原 §七）纪律加审查红线句；注明目标项目协议副本随快照刷新。§四观测项（补判据列）：① 未提示即委派（判据：三位置各至少一条 R 条目）② 降级链档位分布 ③ 阻塞 vs 噪声（判据：被驳回占比；被证伪占比需跨迭代数据，存活率回灌属 5B）④ 三位置存在感 ⑤ 会话纪律（判据：session 句柄可核对）⑥ 轮次 ≤3 与用尽升级案例 ⑦ not-covered 诚实性 ⑧ 耗时/成本/模型档。
- docs/reviewer-containment-design.md §6 修正注记：实践期轻量替代终止（触发条件②转被动发现）。原文保留只加注。

## 4. 实施顺序与验证

1. 契约层：generate.py + stage-contract + 三 frontmatter → 生成器 → 实跑全量取基线
2. review-delegation.md + rubric 库
3. 阶段锚点四处 + DOC-04 清单
4. 测试增补 → 全量绿 + `--check` 零漂移
5. §3.⑦ 文档
6. 收口终审（reviewer **全新会话**，两轮姿态）→ 处置 → 提交（英文 conventional commit，多行信息临时文件 -F）

## 5. 红线

技能文件英文/docs 中文/提交信息英文；frontmatter 改动必跑生成器、提交前 `--check` 零漂移；**零引擎语义改动**（engine.py 零触碰）；engine 独写区零触碰；harness 无关性（不绑 harness 机制名/agent 名，**运行期技能文本不引仓库 docs/ 路径**）；rubric/rule 文本写作判断密集型归主智能体，机械性多文件同步可派 executor。

## 6. 两轮终审处置表（2026-10-20，均为独立全新会话）

**第一轮**（12 第一层 + 9 改进 + 4 建议）：#3/#4/#5/#7/#8/#9/#10/#11/#12 采纳折入；#1（交付 snapshot.py）/#6（判定规则降级）/#2（B&T 证据义务）被用户 D-4/D-7 取代；改进/建议除被取代者外全采纳。快照核验为历史记录（tree `5822122`/HEAD `58bdeba` 一致——该姿态已由 D-4 终止）。

**第二轮**（6 第一层 + 6 改进 + 5 建议，全采纳）：

| # | 发现 | 处置 |
|---|---|---|
| 1 | D-7 改审代码后 RV-02 锚点缺口：src/tests 不在 produces/consumes，任务书取不到被审对象 | RV-02 按位置锚点表 |
| 2 | 审查修复后未重跑测试 → 简报呈现过期绿（违反 DOC-03） | RV-06 修复回灌 + `unreviewed-after-fix` |
| 3 | rounds/triage 写入时未知 vs append-only 互斥 | R-n 定格 + T-n 追加；例外语义入 DOC-04 双落点句 |
| 4 | 审查行只载 tier 不载内容，驳回项用户不可见 | RV-08 词汇表六形态（状态+内容） |
| 5 | D-5 与 ④ 自审冲突 | D-5 补唯一例外限定 |
| 6 | 轮次无读取步骤、事件未定义 | RV-07 强制首步读日志 + RV-06 事件定义（再入不清零） |
| 改进 | D-8 悬空引用/audit.md 推理链/运行期文本引仓库 docs/dogfood 编号混用/class 三副本/登记表对不上 | 全部采纳（§2/§3.⑤/§3.⑦/红线/测试） |
| 建议 | session 句柄/判据列/sha256 截断/简报行数/D-6 取代登记 | 全部采纳 |

**假设记录**：迭代一事实由用户侧持有；239 以实跑为准；迭代二 scope 须命中三位置；目标项目协议副本刷新依赖人工；§四③ 被证伪占比需跨迭代数据。

## 7. 关键参考

- brief §5-11 三位置接线/§5-7 降级链（含推模式）/§5b 修复验证：`C:\Users\qianpeng\.opencode\plan\2026-10-08-aidlc-gates-am-reviewer-design-brief.md:155-201`
- docs/reviewer-containment-design.md §6（仅作者期参考）；docs/batches/b18-gate-posture.md §3.B；build-and-test.md:330-372（简报/授权/report 时序 + DOC-03）；workflow-conventions.md（DOC-03/DOC-04/AUD-01/BRF-01/Blocking Finding 定义）；question-format-guide.md 先例；generate.py:375 一带 ALLOWED_KEYS（行号以实施时为准）
- 实施简报副本（临时）：`C:\Users\qianpeng\.opencode\plan\2026-10-20-b19-reviewer-wiring-plan.md`（与本文 §2/§3 等价，以本文档为正身）

## 8. 实施记录（2026-10-20，单会话落地）

**分工**：契约层与锚点/测试两段机械实施委派 executor（两段并行）；review-delegation.md 与 rubric 库（判断密集文本）由主智能体撰写；docs 登记由主智能体完成。

**落地清单**（交付物 → 实际位置）：

| 交付物 | 落点 |
|---|---|
| ① review-delegation.md | references/common/review-delegation.md（RV-01~08 全量，含按位置锚点表/事件定义/六形态词汇表） |
| ② rubric 库 | references/common/review/index.md + rubrics/{requirements-consistency, design-soundness, code-quality}.md（固定骨架，code-quality 含能力条件化 Out-of-scope 段） |
| ③ 阶段锚点 | requirements-analysis.md:252（Pre-gate review）/ code-generation.md:53（Pre-brief review，Direction Stop 后）/ build-and-test.md:337 + :360（Pre-brief review + 模板 Review 行）/ workflow-changes.md:65（Evidence-verification status line） |
| ④ 契约与生成器 | generate.py：ALLOWED_KEYS :63、REVIEW_CLASS_VALUES :88、枚举校验 :474-479、Stage 构造 :528、build_stage_graph 条件发射 :741-743（未声明无键）；stage-contract.md：§2 行 :63、§5 移出预留 :115、§7 硬失败 #13 :203-206；三 frontmatter 各 :7 |
| ⑤ 审查日志 | reviews.md 为运行期项目文件（不在仓库）；其契约 = RV-07 + DOC-04 双落点（workflow-conventions.md:49-51） |
| ⑥ 测试 | test_generate.py:479 ReviewClassTests（3）+ :914 映射断言；test_rule_invariants.py:199 ReviewWiringTests（5，含 RV↔frontmatter 交叉与 index 路径存在性） |
| ⑦ 文档 | 本档案 §8 + D24（integration-plan 决策表）+ 总账/Phase 5B/B18 后继指针/:95 计数注记 + AGENTS.md 五处（导语 D1-D24/B01-B19、目录表、测试计数 248、路线图速览 B19 行、待实施行摘除）+ dogfood-protocol（§零刷新规则 :14-15、新 §四 R1~R8、原 §四~§七顺延为 §五~§八、数据源/模板行 9/纪律红线）+ reviewer-containment-design.md §6 修正注记 |

**实施期裁决（三条，均最小必要）**：

1. **删除名卫生撞词**：review-delegation.md 与 requirements-consistency.md 中 "terminology"（B12 删除名，DeletedNameHygieneTests 禁token）三处改写为 "naming"/"term drift"（:62 Naming note、:182 [N1] term drift、rubric 维度 6 Naming stability）——语义不变。
2. **stage-contract §7 编号顺延**：新校验条目插为硬失败 #13，原 advisory 13-16 顺延为 14-17（保持编号连续）。
3. **锚点段落缩进风格**：三处新段落按各文件正文既有风格取顶格（简报允许"3 空格或顶格"二选一）。

**验证**：`generate.py` 重生成 + `--check` 退出码 0（零漂移）；`unittest` Ran 248 / OK（239+9）；两段 executor 各自回报全绿后主智能体复跑确认。

## 9. 收口终审处置表（2026-10-20，两轮，均为独立全新会话）

**第一轮**（6 第一层 + 4 改进 + 5 建议，全采纳）：

| # | 发现 | 处置 |
|---|---|---|
| 1 | 三轮预算与 RA 门 Request-Changes 返工环算术冲突 | RV-06 增复用规则（materially changed 才花调用；未变重呈现引 R 条目）〔第二轮再收敛，见下〕 |
| 2 | RA 审查行无模板槽位（exact format + APG-05 压制） | RA 模板 REVIEW REQUIRED 块加 `> Review (requirements-consistency):` 行；锚点措辞改"fills the review line in the completion template below" |
| 3 | 每条语义修复各开一次 scoped 复审，预算算不过来 | RV-06：一次 scoped 复审可覆盖同事件多条语义修复（清单+diff），每次调用计 1 |
| 4 | B&T 锚点来源"direction brief's file list"不存在 | RV-02 B&T 行改 unit plans 为路径权威 + git 交叉核对；非 git 以计划目标路径清单为工作文件清单 |
| 5 | DOC-06 导航索引要求与 reviews.md append-only 冲突 | DOC-06 排除项补 reviews.md |
| 6 | 交叉断言只做词面存在性，映射改了不叫 | ReviewWiringTests 升级：解析 RV-01 表行（stage→class）与 index 表行（class→rubrics/<class>.md）映射断言 |
| 改进 4 条 | RV-02 RA 行 false premise / brief §5-11 悬空引用 / unavailable 无落点 / index 相对路径 | 全部采纳 |
| 建议 5 条 | 路径口径 / CG 行数账 / dogfood 枚举 / D24 裁决数 / §5 理由句 | 全部采纳 |

**第二轮**（2 第一层 + 5 改进 + 5 建议，全采纳）：

| # | 发现 | 处置 |
|---|---|---|
| 1 | material-change 协议三处未收敛：判据缺失、判定者是被审方、后续调用被括注限定为 scoped（无 findings 的实质变更无审查权限） | RV-06 重写预算段：materiality 客观锚（契约段/验收判据/非目标/边界/代码语义 = material；格式/错字/搬迁 = not）+ 复用行必写 `unchanged since R-00x` + 后续调用可为全量重审或 scoped（按变更性质择一）+ "存疑即 material，生产者便利永不决定" |
| 2 | 预算耗尽后同迭代再 material change 无定义行为（两条文本直接冲突） | RV-06 事件生命周期：耗尽后再变更 = 直接 fork 非新调用；审查行新词 `re-review budget exhausted`（RV-08 与 workflow-changes 词汇表同步） |
| 改进 5 条 | B&T:337 与 code-quality 残留旧来源 / RA:252 与 rubric 残留"roadmap 独立文件" / 裁决出处三处矛盾（统一为"七项全部用户裁决，D-4~D-7 为修订批"）/ dogfood :3 :15 旧编号 / RV-08 行数账 4+1→3+1 | 全部采纳 |
| 建议 5 条 | 门模板审查行回归断言（+1 测试）/ unavailable 不耗预算 round: n/a / reviews.md 进提交计划单列 / DOC-01 排除 append-only 记录 / CG 行给具体路径基址 | 全部采纳 |

**处置后验证**：`--check` 零漂移 + **249 绿**（248+1 模板行断言）。

**终审会话纪律记录**：两轮均为全新会话（不复用、不复用规格终审两轮会话）；tier ①（本机 reviewer agent）+ L2 机制性只读。

## 10. 收口后调整（2026-10-21，用户裁决两步定稿）

**技能文本删除全部模型选择内容**：rubric 头部引文与 review/index.md 行内注记原为 "run on the strongest available model（tier）"——第一步改为"用户选择/默认兜底"规则句，用户复核后定稿为**直接删除**（三份 rubric 风格统一，均无模型注记）。语义：技能文本不谈论模型选择，**静默即 harness 默认**（默认即用户自己所配置）；用户想在某次审查用特定模型时自行指定即可。R-n 条目仍记录"实际运行的模型"字段（RV-07 :185/:201）——那是事后审计事实，不是选择指令。动机：避免规则把用户的 token 成本推高。快照源顺延：dogfood 迭代二的技能快照源从收口提交 `aafeebb` 顺延为本次调整提交（迭代边界按协议 §零刷新时取当前状态）。
