# B15 · 产品头脑风暴阶段批（含 B16 合并）· 2026-10-07 立项 · 2026-10-08 其五证伪重设计

| 项 | 值 |
|---|---|
| 状态 | 🔄 其六已冻结（五轮审核，门禁结论见计划审核节末轮）· 段一待实施 |
| 触发 | 原立项：问卷制缺少自由讨论形态；〔2026-10-08 重定义〕非技术用户"一句话许愿式编程"→柏拉图式共建设计对话→产品演进闭环（把 demo 变成长期演进的真实产品） |
| 关联决策 | D19（本批产出，子裁决扩编至 44 项：1~34 存量[Chat 收集语义相关已退役] + 其六新增 35~44）；**D20 全量并入**（自 B16 合并，编号保留、实施归属改挂本批，逐条处置见其六处置表）；与 D16-D18（AM 链）在 AM 延迟激活面耦合 |
| 测试基线 | 立项时 237；2026-10-07 实施至 238，2026-10-08 证伪回滚回 237；v3 重实施预期 237±N（stage 断言同步，见工序 C9） |
| 材料来源 | 2026-10-07 会话讨论链（v2.0 §3 考证 → 用户三决策 → 五轮边界迭代 → 计划 v1 → reviewer 审核 → v2 终稿）；v2.0 证据：`opencode/.aidlc/aidlc-common/protocols/stage-protocol.md` §3（:330-530）、`opencode/.aidlc/skills/aidlc/question-rendering.md`；Trellis 二次吸收（同日其二）：`opencode-suit/trellis`（主出处 brainstorm SKILL，忠实度经 reviewer 11 项对照核验）；重设计（2026-10-08 其六）：OpenSpec `openspec-explore` SKILL + superpowers `brainstorming` SKILL（外部仓库路径 `D:\Documents\PythonProject\opencode-suit\`，非 git 跟踪）+ B16 档案全量吸收 + 实施计划 v2（已并入本档案工序/改动面/验证节，独立文件删除） |

## 立项与裁决

**背景**：现行提问纪律是问卷制（问题文件 + 选项填空 / QT-01 结构化工具勾选）。v2.0 考证发现其 §3 已有成熟三模式设计（Guide me / I'll edit the file / Chat），且核心不变量"任何模式下待答问题必须先落文件（空白 `[Answer]:`）"证明**聊天讨论与问题文件纪律不冲突**——聊天是答案收集模式，不是绕开文件的后门；Chat 模式答案由模型提取（错提风险高于用户亲手填），故 v2.0 为其强制"生成前汇总确认"。

**裁决（用户，2026-10-07 讨论链逐项确认）**：
1. 三模式**全阶段适用**（协议住 question-format-guide + QT 组；阶段文件不动，经审核修正为显式优先级条款，D19.24）；
2. 模式入口：RA 问一次 + 会话粘性 + 随时切换（经讨论修正：挂**会话内第一个问题文件**而非 RA 专属；恢复会话不重问，D19.27）；
3. 生成前汇总确认**仅 Chat 模式**；
4. reviewer 计划审核为**维护者侧工序**，不构成技能依赖（可移植性无损，与 executor 子智能体同类）。

## 规格

### 决策清单 D19.1~34

**协议骨架**

- D19.1 三模式：Structured（QT-01~04，**默认**）/ Self-edit（基础手工流）/ Chat（QT-06）；不变量：**问题永远先落文件（空白 `[Answer]:`），聊天只是收集模式**
- D19.2 适用全部产问题阶段：协议住 question-format-guide + QT 组，阶段文件不动（RA 除外；优先级条款见 D19.24）
- D19.3 模式问题挂在**会话内第一个问题文件**（无论哪个阶段创建；RA 只是典型现场；会话判别见 D19.27）
- D19.4 跨会话不持久化；模式未知（恢复会话）默认 structured，开口即切
- D19.5 生成前汇总确认仅 Chat 模式；structured 免确认（QT-03 不变），self-edit 走 done 信号 + 审批门

**进入与切换**

- D19.6 模式问题呈现：有结构化工具走工具（QT-01 能力差异处理适用），无工具聊天豁免（菜单自适应见 D19.28）
- D19.7 用户预声明模式 → 免问直入，audit 记录（同"用户显式指定 scope 永远赢"先例）
- D19.8 开口切换：**意图类**触发（非关键词、语言无关、示例仅说明性），一行宣告，audit 记录
- D19.9 消解阶梯：有待答问题+讨论意图→切 chat；无待答问题的流程偏好（如"先明确实施计划再实施"）→路由到门/计划机制；自主模式激活话语=显式模式控制指令，优先于 chat 切换解释（D19.29③）；真歧义→一行 either/or
- D19.10 退出对称：同一机制反向；模式是**会话级单变量**，每次翻转保持到下次翻转
- D19.11 讨论中途退出三步交接：立即回写已提取决策（chat 标注）→ 剩余空白转 QT-01 → **文件里有任何 chat 答案则确认仍须走**（确认跟着 chat 答案走，不跟文件终态走）
- D19.12 模型可提议换模式，**永不擅切**；AM 激活时不问模式、chat 不可用（in-round 指示按 AM-04 既有条款；激活于聊天中见 D19.29②）

**Chat 模式纪律（QT-06）**

- D19.13 先落文件：讨论前所有待答问题已在文件；讨论中新问题**先追加（空白标签）再在聊天里问**
- D19.14 澄清文件（follow-up）继承当前模式
- D19.15 收束判据两条硬判据：每个空白标签可提取**有依据**决策（能指认来自用户哪句话）+ 无悬空用户线索（未回应的问题/"我再想想"/明确搁置议题）；模糊感仅可触发一行探询；**低置信提取先逐条口头确认**，全高置信才提案汇总
- D19.16 开谈立规矩：chat 开始一句话告知双向收束协议（用户说 done 收束 / 模型判断收敛也会提案汇总，想继续随时说）
- D19.17 收束路径两条收敛到同一确认点：用户 done → 回写 → 收敛检查（D19.33）→ 确认；模型判断已收敛 → 回写 → 收敛检查（D19.33）→ **呈现确认即提案** → STOP
- D19.18 强停措辞：确认呈现后 STOP and wait（v2.0 "END THE TURN" 句式）；文件出现 `[Answer]: Looks correct` 前**不生成任何产物**
- D19.19 呈现必附一行继续选项（"想继续讨论或修改任何一条，直接说"）；**非匹配回复规则**：确认 pending 时其他回复一律视为继续讨论，禁二选一追问，标签保持空白，结束后重新呈现
- D19.20 Request changes 涵盖改决策 + 开新议题（新议题先落文件）；确认循环**无上限**，Looks correct 是唯一出口；事后反悔走既有阶段门/workflow-changes
- D19.21 **终止符用户所有**（总原则）：讨论结束、阶段推进、模式切换——模型可提议、永不执行

**信号识别**

- D19.22 用户信号通则：**意图分类，永不关键词匹配**；示例是说明非触发；语言无关；**嘴上认语义、文件存规范**（Looks correct 等精确标签是存储纪律，不是用户措辞要求）；回指 APG-01 先例
- D19.23 收束意图的指代消解：附着具体点=子议题闭环；指向整体=讨论收束；真歧义偏向收束（汇总是可逆提案，非匹配规则自动兜回）

**计划审核新增（🔴1/🟡2/🟡3/🟡5/🔵1/🔵2 处置）**

- D19.24 **优先级条款**：收集模式规则（QT-01/05/06）**覆盖各阶段文件的手工收集指令**——qfg 顶部 + QT 组导言明写；7 个冲突阶段文件（user-stories/application-design/units-generation/functional-design/infrastructure-design/nfr-design/nfr-requirements）不改
- D19.25 **问题边界定义**：凡产出决策/答案的话语，必须先以问题条目落文件（空白标签）；对话管理类（继续邀请、复述、意图路由 either/or、对已落文件问题的口头复核）不属"问题"
- D19.26 **确认条目三处 carve-out**：①豁免 Other/字母格式（检查点非问题）；②Error Handling 字母校验仅限字母题，确认检查点归非匹配规则管；③确认标签仅最终 Looks correct 时写入一次，Request changes 以**追加兄弟条目**记录，循环期间标签空白——DOC-04 兼容（追加而非改写）
- D19.27 **恢复会话不重问**：QT-05 仅在新工作流会话（engine `status`=none）的首个问题文件触发；恢复会话（active）不重问，默认 structured，开口即切
- D19.28 **无工具 harness 自适应菜单**：无结构化提问工具时模式问题只呈现 Self-edit / Chat 两项 + 一行说明（先例：QT-01 多选缺失降级处理）
- D19.29 **park/AM 交互三条**：①park 于聊天中 → 泊车前执行回写（已提取决策统一回写，同 D19.11 第 1 步），空白标签 + park 注记承载恢复；②AM 激活于聊天中 → 先回写已提取决策，未答部分转 AM-04；③自主模式激活话语进消解阶梯路由表，优先于 chat 切换解释

**Trellis 二次吸收增补（2026-10-07 其二，二轮审核后收口）**

- D19.30 **证据边界锐化**（并入 qfg Evidence-First Policy，全模式适用）：仓库证据确立**现状与技术约束**；用户的意图行为、功能边界、UX 偏好**永远不能仅由仓库证据回答**——即使存在既有模式。**既有模式是选项和推荐依据，不是决定**；引用时作为推荐理由呈现，决定权仍在用户
- D19.31 **逐题纪律**（QT-06，chat 模式）：模型每条消息**至多问一个**问题——当前**最高价值**（最阻塞下游）者；问题须含决定点/为何重要/推荐答案/另选代价（对齐 Recommendation-and-Trade-off 节）；问完即停，等用户回应；回应用户主动发起的话题不受此限（串行化的只是**模型的提问**，讨论本身自由）；用户一条回复回答多个问题 → 记录后重算剩余清单，再问下一个（答案统一在收束时回写，D19.32）。**文件自讨论开始即含全部待答问题（D19.13）——逐题纪律只约束提问节奏，不削减文件的问题完备性**（先答的答案可能使后问的问题作废，故高价值优先）。模式间不对称的理：结构化工具批量是显式清单勾选、上下文自明；chat 单题为对话可追踪
- D19.32 **回写时点 = 收束时统一回写**〔2026-10-07 其三用户裁决，推翻同日其二的增量回写吸收〕：全部答案在收束时一次性回写（用户 done 或模型提案收束后、收敛检查与确认呈现前）；讨论过程中的决策由模型在对话内维护并当回合宣告（"已记下：X 用 PostgreSQL"）。兜底链：park / AM 激活前的强制回写（D19.29①②）+ 汇总确认与阶段审批门的质量把关。已知代价（接受，见规格修订其三）：未 park 的硬中断（崩溃/上下文压缩）可能丢失未回写讨论
- D19.33 **收敛检查**（确认呈现前，DOC-04 兼容）：清单式核对——①无重复/重叠问题未收口；②无已解决但仍挂着的悬空线索；③全部锚点/决策/约束进入 requirements.md（无一遗漏）；④无遗留空白标签。**DOC-04 兼容机制**：重复问题不删改原文，以**带时间戳的追加合并注记**收口（如 "Consolidation: Q5 并入 Q2，以 Q2 答案为准 @<timestamp>"）；收束后的答案修订走 D19.26③ 兄弟条目（统一回写下，写入前的修订发生在唯一一次回写之前，无需改写历史）；requirements.md 生成时每个决策只出现一次、携带全部锚点，生成后通读验证无跨节重复。**分工边界**：收敛检查只覆盖问题文件侧；outcome/scope/acceptance/技术未知由 RA Step 5 六领域分析与 Step 7 组合边界检查承担
- D19.34 **第一性原理脚手架**（搭车项，RA Step 5 增补；触发条件 = Step 2.1 清晰度判定 Vague/Incomplete）：六领域枚举之前先分解——①一句话重述问题（剥掉实现细节："用户资料加载太慢"，不是"加 Redis 缓存"）；②列基本事实（物理约束/业务规则/技术不变量/用户需要——只要事实不要惯例）；③挑战假设（事实还是惯例？拿掉会怎样？解真问题还是症状？）；④自下而上构建（最小机制开始，每个增加回答"哪条事实要求它？"）；⑤验证（解了原问题吗？哪些假设待验证？最简实验？）。产出的"基本事实清单"直接作六领域提问骨架。触发条件**有意收窄**于 Trellis 原件（原件另含"防过度工程"维度——不为一个透镜扩清晰度判定结构）。〔2026-10-08 其六落点变更〕**本裁决落点由 RA Step 5 改为 PB 阶段私有脚手架**（并入 D19.36）——v1 实施期的"声明即事实边界"条款（其四，随回滚消失）设计上重申并随段一 C1 落 PB：产品声明进事实清单永不被挑战，step 1/3 只分解周边语境，品类默认功能裁不掉只能变成问题

**不在本批**：`gate: none` 两阶段（WD/operations）的有意设计不重开；跨会话模式持久化不做。

### 改动面 v1（10 文件，已随其五回滚作废——留作历史）

| # | 文件 | 改动 |
|---|---|---|
| 1 | `references/common/question-format-guide.md` | "Never Ask in Chat"→"Questions Live in Files — Chat Is Only a Collection Mode"（三模式表 + 两个聊天豁免元问题 + 文件不变量）；豁免表加模式选择行并修正 :15 "only" 措辞；顶部优先级条款（D19.24）；问题边界定义（D19.25）；新增 Chat-Mode Write-Back 格式节（`**Mode:** chat` 标注、间接 remarks 依据行、Consolidated Summary Confirmation 文件格式、carve-out 三条 D19.26）；interaction mode ≠ Autonomous Mode 区分句；Summary 清单更新。**Trellis 二次吸收**：Evidence-First 证据边界 bullet（D19.30）；Chat-Mode 节逐题纪律（D19.31）；收敛检查格式与带时间戳合并注记（D19.33） |
| 2 | `references/extensions/workflow/workflow-conventions/workflow-conventions.md` | 组更名 Question Tool Flow → **Question Flow (QT)**；Overview 行（:10）同步；Group 4 导言：三模式 + 信号意图分类通则 + 终止符用户所有 + 优先级条款 + AM 区分句；AM override 段补模式不可用；QT-01/QT-03 加模式适用前置（Structured 适用 / Self-edit 走基础流 / Chat 走 QT-06）；新增 QT-05（首文件挂载、预声明免问、意图类切换、消解阶梯、会话级单变量、自适应菜单、恢复会话判别、audit）；新增 QT-06（先落文件、收束判据、开谈立规矩、双路径收束、强停、非匹配规则、循环无上限、park/AM 规则）；Enforcement 表 QT-01~06。**Trellis 二次吸收**：QT-06 增补逐题纪律（含模式间不对称理由半句）与收敛检查（D19.31/33） |
| 3 | `references/inception/requirements-analysis.md` | Step 6 加模式入口行 + 收集方式行改模式化表述（替换"Request user to fill in all [Answer]: tags directly"）；⛔ GATE（:190-192）改模式中性表述。**Trellis 二次吸收**：Step 5 增第一性原理透镜（D19.34，搭车项，触发=Step 2.1 清晰度 Vague/Incomplete） |
| 4 | `references/common/session-continuity.md` | #12 改写：问题住文件；两个聊天豁免元问题；chat 是受约束的收集模式（先落文件不变量） |
| 5 | `references/extensions/workflow/autonomous-mode/autonomous-mode.md` | AM-04 补一句：模式问题不问、chat 不可用、in-round 指示按既有条款 |
| 6 | `SKILL.md` | Question File Format 节（生成区外，:71-78 已核）加一个 bullet：三交互模式，指向 QT-05/06 |
| 7 | `scripts/tests/test_rule_invariants.py` | 新建：1 条规则文本断言——技能树无 `QT-01 ~ QT-04`/`QT-01~04`/旧组名残留（大小写不敏感）+ 两个聊天豁免在 qfg 与 session-continuity 同时在场（B11 锚定先例） |
| 8 | `docs/integration-plan.md` | 单行 D19（本批立项已落）+ 批次登记表 B15 行 + "Phase 4=B15+"位移括注修正（随本批立项同步完成） |
| 9 | `docs/batches/b15-interaction-modes.md` | 本档案；完成时回填实施/验证/审核节 |
| 10 | `AGENTS.md` | 路线图 B15 行（立项时已加）；§3.1 测试数 237→238（实施时同步） |

### 改动面 v3（段一 11 项 + 段二 8 项，2026-10-08）

**段一（战略层）**：

| # | 文件 | 改动 |
|---|---|---|
| C1 | `references/inception/product-brainstorm.md` | **新建**：frontmatter 全字段如 D19.35；正文 ~180 行（stance/对话纪律含开场判据宣告与优雅退出/理解回写/**证据边界句 D19.30**/分解前置含用户自带拆分审计/切分判据 S+H 内置指导/方案探索/**工具混用条款：讨论期结构化工具调用免问题文件，问答留对话记录随结晶落档 D19.39**/分节结晶/产物与深度含 roadmap 节格式[承接 B16 模板]/自查四查[含"写盘后 product-design.md 存在且非空"存在性检查]/一次性写盘/AM 延迟与 park 条款/审计粒度条款；英文撰写） |
| C2 | `references/common/question-format-guide.md` | 四处同步：豁免表 +PB 对话行、:15 "only" 措辞、:19 Sole exception 括注、:372 Summary ❌ 行 |
| C3 | `references/common/session-continuity.md` | #12 半句同步豁免 |
| C4 | `references/inception/requirements-analysis.md` | frontmatter consumes +product-design（required: false）+ requires_stage +product-brainstorm；Step 1 加载 product-design.md；Step 2 后路由条款（含"本会话已拒绝"守卫）；Step 5 六领域×roadmap 对账；Step 7 限定当前迭代；再入分支三条全量（D20.12：迭代子集+组合边界影响分析+RE/设计一致性检查） |
| C5 | `references/common/workflow-changes.md` | 设计级变更半节（huddle 二分结局+roadmap 修订注记格式+再入两路径声明——详规段二扩） |
| C6 | `references/extensions/workflow/autonomous-mode/autonomous-mode.md` | **AM-01/02 延迟条款（D19.42 四场景：延迟宣告不写 Enabled/RA 入口 AM-02/延迟可取消/激活意图不跨会话持久化）+ AM-05 触发增列（AM 激活下 PB 以任何途径重新成为 current——mid-round jump 回 product-brainstorm **或 plan-line 复活**——即停用，注明属 in-round 停用非 AM-10 轮次边界）+ AM-10 澄清句 + 概览行** |
| C7 | `references/common/scopes/classic.md` + `infra.md` | classic：会员段"14 stages"计数/清单 14→15；infra：Membership 散文补 PB=CONDITIONAL 半句（bugfix/refactor/security-patch/express 四件有"everything else SKIP"兜底句覆盖，无需动；成员值本身在 C1 frontmatter 的 scopes map） |
| C8 | 跑 generate.py | 生成区自更新（SKILL.md 清单/welcome 三阶段图/session-continuity artifact 图/workflow-planning）；`--check` 验证；welcome ASCII 对齐一眼检 |
| C9 | 测试套件 | **同步面（第五轮扩写）**：①STAGE_ORDER 硬表 14→15 且 PB 位置=RE 后 RA 前（compute_display_order 同层按 slug 序）；②test_engine 的 RE→RA 邻接断言群（current 将变 PB 的多条）；③`STAGE_ORDER[:7]` inception 切片 → 8 阶段语义修复；④test_generate 的 RA consumes **精确相等**断言（C4 加 product-design 后必挂，同步期望值）；⑤+1 规则文本断言宿主=重建 `scripts/tests/test_rule_invariants.py`（随回滚已删）；预期基线 237±N |
| C10 | `SKILL.md` 非生成区 | 新增手写阶段执行块 `## Product Brainstorm (CONDITIONAL)`，与既有阶段块对齐；**目录树 inception 子目录块补 `product-design/` 一行** |
| C11 | 登记同步 | integration-plan（§2 D19/D20 行/§3 B15+B16 行/§5 Phase 3.4/§6 开放项/§7"已并入"措辞/**D1 行加"阶段集 14→15"取代注记**/**§4 阶段计数同步**）、**`references/common/engine-contract.md` "14-stage" 计数同步**、**`docs/engine-illustrated.md` 计数三处（:17/:20/:322）**、B16 档案头部关闭注记、B15 档案状态、AGENTS.md |

**段二（交付环）**：

| # | 文件 | 改动 |
|---|---|---|
| D1 | `references/common/workflow-changes.md`（扩 C5） | 四节全量：Re-Entering 两路径（改形→jump product-brainstorm / 不改→jump requirements-analysis）+ Roadmap Changes（三时点+shipped 不可改写+append-only，与 huddle 合流）+ Splitting an Oversized Iteration + Iteration Completion Ritual（三分支+AM 宣告顺序+shipped 标记时机） |
| D2 | `references/inception/workflow-planning.md` | 判据复核位（PB 拆分 H1 复核+呈报违例）+ execution-plan 模板 Iteration Scope 节 + Step 9 roadmap 摘要；frontmatter 不动 |
| D3 | `references/inception/units-generation.md` | 当前迭代 FR/US 子集 + 下行闭包校验（依赖 >K → 报 roadmap 缺陷回 WP）+ 增量更新不重生成 |
| D4 | `SKILL.md` | :102 completed 行 roadmap 路由前置 + :126 done 三分支压缩指针（与 C10 分两波） |
| D5 | `references/construction/build-and-test.md` | Commit Protocol 一句：迭代边界提交批含 product-design.md 的 shipped 标记+rollup 压行 |
| D6 | `references/common/session-continuity.md` | 完成态 roadmap 下一迭代预览两处（Welcome Back "workflow complete" 行 + Menu Execution 完成态分支）路径核对 |
| D7 | 登记同步 | 同 C11 模式 |
| D8 | `references/inception/user-stories.md` | 规格期裁决项：US 按当前迭代增量（经 RA 子集继承、编号续编）一句话 |

**engine.py 零改动**（D15 jump 支持任意 slug，三轮审核已核证）。

### 工序（v3，2026-10-08 重写；v1 工序随其五回滚作废）

1. ~~v1 计划审核~~ ✅ + ~~v1 实施~~（证伪回滚，见其五）+ ~~v3 实施计划制定与三轮审核~~ ✅（见计划审核节第三轮）
2. **其六二轮审核**（同 reviewer 会话第四轮）：重点=condition 散文可判定性 / B16 处置表忠实度 / D19.35 字段集与 generate.py 兼容 / AM 第四场景 → 规格冻结
3. **段一实施（战略层，11 项）** → 机械验证 → **dogfood #1（8 验收点）** → 【止损点：段一独立可交付（单迭代无交付环可走通）】
4. **段二实施（交付环，8 项）** → 机械验证 → **dogfood #2**
5. 收口（四节回填/状态翻转/遗留登记/分段 commit，每步用户开口）

## 计划审核（reviewer，实施前，2026-10-07）

**结论**：1 🔴 / 5 🟡 / 4 🔵 / 2 改进 / 2 建议；用户裁决"全部按推荐处置"。

| 级别 | 发现 | 处置 |
|---|---|---|
| 🔴1 | "阶段文件不动（RA 除外）"前提不成立——7 个阶段文件写死手工收集指令与新协议冲突 | 选 (b)：优先级条款（D19.24），阶段文件不改 |
| 🟡1 | QT-01/QT-03 未做模式门控；RA ⛔ GATE 未进规格 | 采纳：模式适用前置 + GATE 模式中性表述 |
| 🟡2 | "问题先落文件"与聊天内探询边界未定义，与"仅两个豁免"自相矛盾 | 采纳：问题边界定义（D19.25） |
| 🟡3 | 确认条目与 Other 必选/Error Handling/DOC-04 三条硬规则冲突无 carve-out | 采纳：三处 carve-out（D19.26） |
| 🟡4 | 清扫盲区：`QT-01~04`（无空格变体）匹配不到；Overview :10 未进清单；:15 "only" 措辞未修 | 采纳：清扫串补变体 + Overview 纳入 + "only" 修正 |
| 🟡5 | 恢复会话"是否重问模式"在 D19.3/D19.4 间未定 | 采纳：status 判别（D19.27） |
| 🔵1 | 无工具 harness 上 Structured 与 Self-edit 菜单等价 | 自适应菜单（D19.28） |
| 🔵2 | 模式变量在 park/AM 激活/再入时取值未覆盖 | 三条并入本批（D19.29） |
| 🔵3 | 登记格式：子编号 vs 单行制；"Phase 4=B15+"括注失效；档案七节模板 | 单行 D19 + 子项住档案 + 位移修正（本次立项已执行）+ 本档案按七节 |
| 🔵4 | error-handling / engine-illustrated / welcome-message 三处"无需改"核验 | 验证节点名；engine-illustrated :340 记遗留 |
| 改进1 | 组名 Question Tool Flow 纳入 Chat 后名不副实 | 更名 Question Flow (QT) + 清扫旧名 |
| 改进2 | interaction mode 与 Autonomous Mode 共用 mode 一词 | 首次定义处加区分句 |
| 建议1 | 规则文本断言使清扫机器可检（B11 先例） | 采纳：+1 测试（237→238） |
| 建议2 | 工序委派豁免理由措辞与实际条款不符 | 采纳：改写为紧凑性判据原文 |

**第三轮（v3 实施计划审核，2026-10-08）**：2🔴/10🟡/8🔵，结论"暂缓进阶段 A"→ 全部处置、计划 v2 收口后**已随结构归并 absorbed 进本档案**（独立计划文件删除，单一权威恢复）。要点：🔴1 scope 时序冲突 → 三层门控选项③（D19.35/38）；🔴2 B16 吸收不足 → 其六逐条处置表；🟡1~10 与 🔵1~8 的落点见其六各子裁决与改动面 v3。

**第四轮（其六二轮审，2026-10-08）**：结论"设计层无新结构性缺陷，上轮两 🔴 处置经核证成立；其六有条件冻结、段一有最小条件开工"——1🔴/7🟡/5🔵 已全部当场处置：🔴1（D19.42③ 超出 C6 改动范围）→ C6 扩为 AM-01/02 延迟+**AM-05 触发增列**+AM-10 澄清句；🟡1 D1/§4/engine-contract/engine-illustrated 计数 → D1 取代注记+§4 同步+计数同步入 C11；🟡2 附注/遗留三处陈旧 → 加"已退役/失效"注；🟡3 §3/§6 B15 行 → 已对齐其六态；🟡4 H1 标题 → 已更新；🟡5 D19.34 落点 → 加其六落点变更注记（RA→PB 脚手架）；🟡6 守卫载体 → D19.38 注明会话内存；🟡7 处置表四行限定条件 → 已补回；🔵1 SKILL.md 目录树 → 入 C10；🔵2 engine-illustrated 计数 → 入 C11；🔵3 改形路径 scope 前提 → D19.43 注明；🔵4 延迟可取消 → D19.42① 补；🔵5 P1/P2 可考性 → 对照表注明。**其六冻结 ✅，段一可开工。**

**第五轮（换模型复检，2026-10-08，kimi-k3 新会话——前审查员会话因模型绑定滞留旧模型，本轮起不复用 sessionID）**：结论"**其六冻结维持，段一可开工**，带文字补丁进实施"——5🟡/8🔵/2改进/3建议全部当场处置：🟡1（**新发现**：AM 激活下 PB 经 plan-line 复活[非 jump]成为 current 时 AM-03 会自动批准 PB 门，违反"纯人类领地"）→ D19.42③/C6 扩为"任何途径重新成为 current（jump 或 plan-line 复活）即停用"；🟡2（D19.30 保留声明无落点）→ 证据边界句入 D19.36 与 C1；🟡3（C9 测试同步面低估：RE→RA 邻接断言群/`[:7]` 切片/test_generate RA consumes 精确断言）→ C9 扩写并点名断言宿主；🟡4（AGENTS.md/档案头部/实施节三处"待二轮审"陈旧）→ 统一"其六已冻结·段一待实施"口径；🟡5（D19.39 工具混用无落点且"QT-01 语义"与现行前提不符）→ D19.39 明落点"免问题文件，随结晶落档"；🔵1~8（零产物写盘措辞/验收点⑤缩窄/B2 双落点/engine-illustrated :17/C7 半错括注/consumes 理由张冠李戴/huddle roadmap 在场限定/§4 超前计数）与改进/建议（头部状态只留指针/终止权笔误/写盘存在性检查/激活意图不跨会话）全部处置。**与前四轮口径差异：结论一致，但前四轮"设计层无新结构性缺陷"偏乐观——🟡1/🟡2 属其六自身语义缝隙。**

## 规格修订（2026-10-07 其二 · Trellis 二次吸收）

**来源**：Trellis 框架二次吸收分析（`D:\Documents\PythonProject\opencode-suit\trellis`，主出处 `.opencode/skills/trellis-brainstorm/SKILL.md`；吸收忠实度经 reviewer 11 项对照核验全部忠实）。规格侧五项增补 D19.30~34 已并入决策清单（既有 D19.11/17/29 随 D19.32 改述）；登记侧六项（Phase 5A/Phase 4 设计输入块 + §6 总账两行）落 integration-plan，同日执行。

**二轮计划审核（reviewer，修订计划审）**：1 🔴 / 5 🟡 / 5 🔵；用户裁决"全部按推荐处置"。

| 级别 | 发现 | 处置 |
|---|---|---|
| 🔴1 | D19.17 有两条收束路径，修订只改了用户 done 路径，模型发起路径仍写"回写"，与 D19.32 增量回写矛盾 | D19.32 改述范围扩为两条路径（已修入决策清单） |
| 🟡1 | 增量回写使"答案被后续修订"成高发场景，D19.33 原只覆盖"问题重复"未覆盖"答案取代"，且漏时间戳 | D19.33 增补带时间戳修订注记映射 old→new（已修入） |
| 🟡2 | integration-plan §2 D19 行"子裁决 D19.1~29"将失准 | 同步改 D19.1~34（integration-plan 侧执行） |
| 🟡3 | Phase 4 新项塞 09-22 旧块、5A 却新建 10-07 块，来源归属不一致 | Phase 4 也新建并列"Trellis 二次吸收设计输入（2026-10-07）"块 |
| 🟡4 | D19.34 搭车未反映到 §3 一句话/AGENTS.md，且来源为 Trellis 非 v2.0 | 选保留 + 三处描述同步（理由见下） |
| 🟡5 | D19.33 只映射 Trellis 收敛门 2/6 维，未说明其余维度分工 | D19.33 末补分工句（已修入） |
| 🔵1 | D19.34 触发条件窄于原件（丢"防过度工程"维度） | 接受收窄并在规则文本注明有意为之（已修入） |
| 🔵2 | chat 单题 vs structured 批量不对称无理由说明 | QT-06 加理由半句（已修入 D19.31） |
| 🔵3 | dogfood 观察点⑦依赖文件 mtime 不可靠 | 改 audit.md 同交互对应关系（已修入观察点 7） |
| 🔵4 | required·once 门脱离 breadcrumb 载体后无强制力 | 5A 块注明"仅作软强度标记"（integration-plan 侧执行） |
| 🔵5 | 观察点编号风格混用 | 统一阿拉伯数字续编（已修入） |

**D19.34 搭车理由**：与三模式同触 RA 文件、同服务"意图不明 → 好需求"的立项主线（透镜改善**问什么**，模式改善**怎么问**）；独立成批的登记成本与约 15 行增补不成比例（先例：B09 收尾小批混装异质项）。来源为 Trellis（非 v2.0），已在 integration-plan §3 一句话与 AGENTS.md 路线图标注。

### 其三 · 回写时点回退（用户裁决，同日）

**裁决**：废止其二的增量回写吸收（原 D19.32），恢复**收束时统一回写**。理由（用户）：审批门兜底——汇总确认与阶段审批门发现答案不完整或错提时，可重新处理或向用户追问；统一回写协议更简。

**回退波及（全部已执行）**：D19.11 / D19.17（两条路径，保留 D19.33 收敛检查在收束路径中）/ D19.29①② 改述回退；D19.31 去"逐一回写"表述并补"提问节奏 ≠ 文件完备性"澄清；D19.32 重写为统一回写裁决；D19.33 移除"答案取代修订注记"条款（统一回写下修订发生在唯一一次写入之前，收束后修订走 D19.26③ 兄弟条目）；dogfood 观察点删"增量回写验证"并重编号（现 1~7）。

**已知代价（接受并记录）**：未 park 的硬中断（会话崩溃/上下文压缩）可能丢失未回写讨论——审批门只兜产物质量、不兜讨论过程的中断持久性。缓解：park / AM 激活前强制回写（D19.29①②）+ 模型当回合口头确认决策（错听即时可纠）+ 会话恢复通常可从历史找回。此为对 Trellis"conversations get compacted, files don't"动机的已知情取舍。

### 其五 · dogfood 证伪与全量回滚（2026-10-08 用户裁决）

**dogfood 概况**：裸项目（工作区 `b15-dogfood-sci-calc`，验收后用户已删除——本节即为过程记录），输入一句话需求"做一个国际象棋游戏"。核心路径机械合规：模式三选一经工具呈现、逐题纪律（每消息一问+推荐+代价）、新议题先落文件（Q11）、收束时统一回写（11 条全部 `**Mode:** chat` + 依据行）、汇总确认、审批门正确 STOP。

**用户四点裁决——Chat 模式设计证伪**：
1. 模式描述（"不想填表，我们聊天"）暴露设计本质：用户期望 Chat = **柏拉图式对话，逐步把模糊意图共建成完整产品设计**，不是换渠道答题；
2. 实际行为 = 预制问卷逐题重念（且选项不完整展示），体验劣于结构化工具，"等于没做"；
3. 讨论期文件交互割裂（新问题当回合落文件等），应为答完统一落档；
4. Chat 不应禁用结构化工具——离散固定选项决策（opt-in 开关等）天生该走工具。

**根因**：D19.1"聊天只是收集模式"+ D19.13"先落全部问题"+ D19.31"从清单挑题"合成 interrogation funnel。对照 OpenSpec `openspec-explore`（`opencode-suit/OpenSpec/skills/openspec-explore`）的设计哲学："This is a stance, not a workflow"（无固定步骤/必答清单/强制产物）、"Open threads, not interrogations"、"Track decisions in the conversation, not in files"、结晶时提议落档且用户点头才写——**"问什么"应从对话涌现，而非文件预定**。考古结论：v2.0 Chat 语义（stage-protocol.md :472-481）同被证伪（B15 为忠实移植）。

**处置（已执行）**：
- **全量回滚**：实施与登记未提交，git restore 至 `1a26cce` + 删除 test_rule_invariants.py；测试基线回 237；其四（透镜边界条款）随回滚消失，**设计上重新确认**，随重实施落回；
- **B15 规格重开**：Chat 语义按"共建设计对话"重设计（方向：问题文件在 Chat 下取消作为输入、六领域/透镜降为模型私有脚手架、决策记在对话、离散决策解禁结构化工具、结晶摘要→用户同意→一次性落档；参考 opsx-explore 姿态 + harness plan mode 机制）。**保留清单**（dogfood 验证为对的部分）：模式选择入口（QT-05 骨架）、Structured/Self-edit 两模式、意图分类信号、终止符用户所有、审批门兜底、AM 交互（模式不问/Chat 不可用）；
- 重设计定稿后走其六规格修订 + reviewer 计划审核 → 重实施 → 重 dogfood（验收标准改为"共建设计对话感"）。

### 其六 · 重设计规格：产品头脑风暴阶段批（2026-10-08，计划审核三轮处置后收口）

**裁决背景**：五项用户锁定（B15 原地变身 / slug `product-brainstorm` / 产物自适应深度 / RA 路由两边写 / 门上讨论回写 roadmap）+ 三条用户裁决（B16 全量合并 / AM 延迟至 RA / park 不设机制）+ 两外部源借鉴（opsx-explore 姿态、superpowers 八项校验点 B1~B8）。目标用户：不会用 plan 模式、不会写 PRD 的非技术许愿者。

**新子裁决 D19.35~44**：

- **D19.35 阶段契约**：slug `product-brainstorm` / inception / CONDITIONAL / condition `{execute_if, skip_if}`（内容=D19.38）/ gate approve-continue / requires_stage [workspace-detection, reverse-engineering] / depth adaptive / produces `inception/product-design/product-design.md` / consumes RE 产物（required: false——PB 仅在 brownfield 消费 RE 产物，非必经输入）/ scopes：**classic CONDITIONAL**、infra CONDITIONAL、bugfix·refactor·security-patch·express SKIP。矩阵值附注：**管 scope 选定后的轮次；首跑门控在 condition 散文**（scope 在 RA Step 2.5 才选定，首跑矩阵值是死条件——RE 同构：排在 RA 前的 conditional 阶段靠散文自选）。
- **D19.36 对话纪律**：opsx 姿态（stance not workflow、开放线头不审讯、挑战假设、ASCII 可视化带逐题判据"看图是否比读字清楚"[B8=superpowers 逐题判据+opsx ASCII 两源合并，弃浏览器载体保 harness 中立]）+ **理解回写**（B1 早期检查点：开场交换后、深谈前，短笔记复述意图/约束/成功标准，**区分所说与假设**，邀请纠正）+ 红旗表 4~6 行（B5：如"愿望太小不用 roadmap"——一页纸也是 roadmap；"用户答得快跳过理解回写"）+ 一次一个聚焦问题（说明解锁哪个决策）+ 推荐+代价 + YAGNI（B7）+ **声明即事实边界**（原其四透镜边界回归：产品声明进事实清单永不被挑战，step 1/3 只分解周边语境，品类功能裁不掉只能变成问题）+ **证据边界**（D19.30 保留：仓库证据确立现状与技术约束，永不决定用户意图——既有模式是选项与推荐依据，不是决定，决定权在用户）+ 六领域/第一性原理=**私有脚手架**（开线头的内在依据，不是问卷模板）+ **开场判据宣告与优雅退出**（见 D19.38 纪律③）+ **审计粒度条款**（里程碑级条目——开场/理解回写/结晶/门，非逐轮）。
- **D19.37 产物与自适应深度**：product-design.md 结构（定位/用户与场景/关键决策记录含理由与来源轮次/演进方向/**迭代拆分 roadmap**/out-of-scope/未决项）+ 宣告深度可推翻（B4；注明：superpowers 原件宣告的是路径，此处再解释为深度）+ 单向棘轮（复杂度发现只升不降）+ **一页纸下限**（小愿望=定位一段+单迭代+三条"以后再说"）+ **roadmap 节格式承接 B16 模板草案**（Iteration Status 表[planned/next/in-progress/shipped/dropped]、DoD 字段构成[全量回归绿+可演示验收为硬，staging+运维为占位]、Shipped Log[ship 当刻压行+git 指针，不可改写]、Deferred 编号不回收、Revision Record append-only）。
- **D19.38 跳过与路由——三层门控**（首跑 scope 未选定，矩阵值不参与）：**第一层**=condition 散文自选（execute_if：无可用产品设计的许愿型请求[新产品/新能力方向/重大演进，含措辞模糊但意图为产品级]；skip_if：①product-design.md 现存 roadmap 无需改形[迭代再入] ②用户已给完整设计[判据：覆盖定位+演进、足以让 RA 直接开工；部分完整→execute 且作理解回写起点] ③请求不改产品功能与设计[bugfix/refactor/安全补丁/ops/已设计迭代的纯实施]）；**第二层**=scope 矩阵（选定后轮次引擎剪枝）；**第三层**=RA 路由兜底（RA 判 Vague/Incomplete 且无 product-design.md → 一行建议退回 PB，**守卫：本会话用户已明确拒绝过则不再建议**——守卫载体=会话内存，不持久化，跨会话/再入可重复建议；PB 已被 skip 的事实以引擎状态/审计为准）。判定纪律四条：①意图分类永不关键词匹配（APG-01 先例）②拿不准判 execute（代价不对称：错 skip 有第三层拉回，错 execute 只是一轮开场）③开场判据宣告（"这个请求看起来是…，我理解为需要先聊聊产品形态——如果不是，直接说，我跳过"）+ 用户终止权退出（report skipped --reason user-declined）④优雅退出后 RA 路由守卫生效。
- **D19.39 工具混用**：离散固定选项决策 → 结构化工具灵活调用（QT-01 语义）；对话主导、工具服务——chat 不是工具负向。**落点（C1 工具混用条款）**：PB 讨论期的工具调用**免问题文件**——问题与答案留在对话记录，随结晶一次性落档（不接回问题文件流）。
- **D19.40 结晶与落档**：判据（定位清楚/演进成形/切分成形/未决显式——无强制结尾，"有时思考本身就是产出"仅指中途，结晶仍是阶段出口）+ **分节呈现逐节确认**（B3：定位→用户场景→演进方向→迭代拆分，逐节过）+ 自查四查（占位/矛盾/歧义/范围）+ **一次性写盘（讨论期间零产物写盘——审计条目除外）**+ **批准范围精确化**（B6：行进信号只批准当前呈现之物，不存在预授权——其五 dogfood"继续"判例成文）。
- **D19.41 门上贯穿**：任何门上设计级讨论（AI 提议或用户发起，AI 只提议不擅启）→ 二分结局：不动方向=记审计继续；动方向=roadmap 带时间戳修订注记回写（DOC-04，与 D20.14 三时点合流——**限定：roadmap 在场时走回写分支；无 roadmap（非 classic scope）走既有变更流**）+ 必要时向后重做。完成仪式=固定回顾落点。
- **D19.42 AM 与 park**（四场景）：①brainstorm 中 Activate 意图 → **固定延迟**：一行宣告 + 审计记录（**不写 Enabled=Yes**），RA 入口执行全新 AM-02（含 code-gen hold 问题）；延迟期内用户表达退出/取消自主模式 → **取消待激活**（AM 状态 no-op，审计一行）；②不耐烦用户走**快路径**（AI 起草全默认 product-design → PB 门人守门批准）而非 AM——brainstorm 是纯人类领地，任何机制不得替用户做产品决定；③AM 激活下 **PB 以任何途径重新成为 current（mid-round jump 回 PB，或 plan-line 复活——Type 1 把 PB 加进 Stages to Execute）** → 按 AM-05 语义停用（模式结束，标准模式走完 PB）——**实施落点为 AM-05 触发增列**（两种途径并列列为停用触发），属 in-round 停用而非 AM-10 轮次边界（若采 AM-03 carve-out 方案则由 AM-03 侧排除 PB 门，二选一随 C6 落笔定）；④完成态再入 jump --stage（无论目标）本身是 AM-10 过期边界（引擎翻转），AM 永不带着进 PB。park 不设机制：讨论不跨会话持久化，中断/压缩=放弃当前讨论，恢复后重开或走快路径（已知情取舍其二）。**延迟中的激活意图同样不跨会话持久化**（随对话丢失，与 park 取舍一致）。
- **D19.43 B16 全量合并**：D20.1~19 逐条处置 + 12 文件逐条归属见下方处置表；D20 编号保留、实施归属改挂本批；B16 档案保留为 D20 语义之家与历史记录，状态翻"已并入 B15（未实施）"。**scope 前提注明**：段二"改形→jump product-brainstorm"路径仅 classic scope 可达（PB 在 bugfix 等 scope 为 SKIP，jump 不绕过计划过滤——与 D20.10"非 classic 默认不拆"自洽）。
- **D19.44 退役清单（D19.1~34 逐条处置）**：**退役**——D19.1~23 中 Chat 收集语义相关（三模式机器：模式问题、QT-05/QT-06 位、消解阶梯、汇总确认作为问题文件确认等）、D19.24 优先级条款、D19.25 问题边界、D19.26 carve-out、D19.27 恢复会话判别、D19.28 自适应菜单、D19.29、D19.31/32/33（逐题/回写/收敛的"问题文件版"——精神部分被 D19.36/40 继承）；**保留**——D19.30（证据边界，并入 D19.36）、D19.34（透镜+其四边界，并入 D19.36 私有脚手架）、意图分类信号原则/终止符用户所有/审批门兜底（并入 D19.36/40）。**显式声明**：其五"保留清单"中"模式选择入口（QT-05 骨架）/Structured·Self-edit 两模式"被本批"阶段即对话"裁决**取代**——RA 内不再有模式选择，回归 QT-01~04 工具流 + QT-04 手工兜底原状。QT-01~04 与 qfg 主体不动。

**B16 逐条处置表（D19.43 实体）**

*D20.1~19 子裁决*：

| # | B16 原裁决 | 处置 | 落点 |
|---|---|---|---|
| D20.1 | 迭代=一轮工作流轮次；git 承载版本边界 | 承接 | 段二 D1 |
| D20.2 | roadmap @ plans/roadmap.md，WP 产出随 WP 门 | **被取代**：roadmap 移为 product-design.md 内节、PB 产出随 PB 门；"引擎零改动"承接；模板承接进 D19.37 | 段一 C1 |
| D20.3 | 迭代边界人工门绝对；v1 无 AM 自动续迭代 | 承接 | 段二 D1 |
| D20.4 | 两道门不互替 | 承接（"roadmap 批准门"随 D20.2 改为 PB 门，语义微调声明） | 段二 D1 |
| D20.5 | 依赖写在制品；UG 下行闭包校验 | 承接 | 段二 D3 |
| D20.6 | 粒度本质（全质量收尾的最小可演示增量） | 承接；主应用时点迁移：WP → PB 对话内置指导 + WP 复核位保留 | 段一 C1 + 段二 D2 |
| D20.7 | 硬判据 H1/H2/H3(缩减)+DoD 占位 | 承接（H1 双层检查保留；Operations 升格挂账不变） | C1 + D2/D3 |
| D20.8 | 软判据 S1~S4 | 承接（PB 切分指导） | 段一 C1 |
| D20.9 | 用户显式拆分永远赢 | 承接（与声明即事实同族） | 段一 C1 |
| D20.10 | N=1 合法；非 classic 默认不拆；express 豁免 | 承接（与 PB 一页纸下限合流，声明） | 段一 C1 |
| D20.11 | 用户自带拆分审计不重拆、呈报违例 | 承接（B2 分解前置的用户自带场景；保留典型判例：横切分层拆分[迭代 1 全前端/迭代 2 全后端]违反 H2/S1 → 呈报建议改纵切） | 段一 C1 |
| D20.12 | RA 再入增量=迭代子集+组合边界影响+RE 一致性 | 承接（三条全量） | 段一 C4 |
| D20.13 | 完成仪式三分支（三层落笔） | 承接 | 段二 D1/D4/D5 |
| D20.14 | roadmap 修订三时点；shipped 不可改写 | 承接（与 D19.41 huddle 合流） | 段二 D1 |
| D20.15 | "建议更小拆分"是被批准的拒绝动作 | 承接（PB 对话纪律） | 段一 C1 |
| D20.16 | rollup 模板内建、ship 当刻压行 | 承接（roadmap 节 Shipped Log；保留 5A 观察项纪律前置——journal 2000 行硬上限先例） | C1 格式 + D5 |
| D20.17 | 轻量反馈回灌 | 承接（与完成仪式回顾 huddle 合流；保留限定：遥测级回灌依赖 Operations 实义化，不在本批） | 段二 D1 |
| D20.18 | roadmap 不进 frontmatter produces | **被取代（语义反转声明）**：原由"WP 不产 roadmap"成立；新设计 PB 显式 produces product-design.md（含 roadmap 节），语义成立；"引擎零改动"以"新阶段一次生成"形式保持 | C1/C8 |
| D20.19 | 非目标四项 | 承接全部（四项=AM 自动续迭代/引擎迭代感知/Operations 实义化[Phase 3.4 B17+ 候选]/多 intent[D11 不变]——分别由 D19.42②、D20.5"依赖写在制品"、其六 Phase 3.4 节、D11 原文承接排除） | 其六 |

*12 文件*：

| B16 # | 文件 | 处置 | 落点 |
|---|---|---|---|
| 1 | workflow-planning.md | 部分承接：roadmap 产出/模板移 PB；WP 保留判据复核位 + execution-plan Iteration Scope 节 + Step 9 摘要 | 段二 D2 |
| 2 | units-generation.md | 全量承接（当前迭代子集+下行闭包+增量不重生成） | 段二 D3 |
| 3 | requirements-analysis.md | 全量承接（并入 C4，含 D20.12 三条） | 段一 C4 |
| 4 | workflow-changes.md | 全量承接（Re-Entering 两路径+Roadmap Changes[与 huddle 合流]+Splitting+Completion Ritual 四节） | 段二 D1 |
| 5 | session-continuity.md | 全量承接（完成态 roadmap 预览两处路径核对） | 段二 D6 |
| 6 | SKILL.md | 承接（:102/:126——与段一 C10 手写 PB 块分属两段） | 段二 D4 |
| 7 | 根 AGENTS.md | 承接（登记类；B01-B16 区间不变） | C11/D7 |
| 8 | b16 档案 | 关闭注记："已并入 B15（未实施）"+处置表指针 | 随本其六 |
| 9 | integration-plan.md | 承接（§2 D20 行实施归属注记；§7:205"B17+"已改无需动） | C11/D7 |
| 10 | build-and-test.md | 全量承接（Commit Protocol 一句；引用文件名随 D20.2 改 product-design.md，声明） | 段二 D5 |
| 11 | user-stories.md | 承接为段二规格期裁决项（US 按当前迭代增量） | 段二 D8 |
| 12 | b15 档案 B16+ 括注 | 已失效（立项时已改"B17+"，语义仍对，核验即可） | C11 核验 |

**表面张力消解注记**：B16 附注"不吸收被动拆分（非技术用户不会自己驱动）"与 PB 对话式分解**不矛盾**——B16 否决的是"被动等用户拆"，PB 是 AI 主导开线头主动应用判据（D20.6~11 由 AI 在对话中运用）。

**Phase 3.4 重定义**：迭代交付 → **产品演进闭环（Product Evolution Loop）**；B15=首批（暂唯一）；Operations 实义化 B17+ 候选原样挂账；integration-plan §7 生命周期补"已并入（未实施）"状态措辞。

**决策对照（防丢清单）**：五项锁定→其六本节；三条裁决→D19.42~44；B1~B8→D19.36/37/38/40（**B2 双落点**：skip_if②"已给完整设计不重问"=superpowers 理解复用、C1"分解前置"=范围分解前置，均在 D19.38/C1）；Phase 3.4 重定义→本节；dogfood P1→D19.40（B6）、P2→C4 六领域对账〔P1~P6 过程记录：dogfood-records 目录被 gitignore 且未落盘，原文已佚——其五节即持久记录，P1="继续"信号判例、P2=六领域漏问为可考要点〕；🔴1 三层门控→D19.35/38；🔴2 处置表→本节两表。风险与预案表（批次体量/契约/测试硬编码/审计膨胀等）已吸收进工序节止损设计与改动面/验证节，此处不复述。

## 实施与实施期裁决

（2026-10-07 曾实施、2026-10-08 证伪回滚——记录见其五；其六已冻结（五轮审核），段一按工序节两段推进）

## 验证（v3 预定验收标准，2026-10-08；v1 标准随其五回滚作废）

**段一机械验证**：
- `python .agents\skills\aidlc-workflows\scripts\generate.py --check` 退出码 0（新增阶段 frontmatter → 生成区同步后零漂移）
- `python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests` 全绿，基线 237±N（STAGE_ORDER 14→15 同步；+1 规则文本断言：新术语一致性——`product-brainstorm`/PB 对话豁免在 qfg+RA+session-continuity+SKILL.md 四处同现在场，B11 先例）
- 交叉引用核对：PB ↔ qfg 四处 ↔ RA 路由/对账 ↔ session-continuity #12 ↔ AM 延迟条款 ↔ SKILL.md 手写块互指一致
- 生成区标记内零手改（welcome ASCII 对齐一眼检）；只读目录零触碰；英文撰写；harness 中立（无浏览器/hook 依赖）
- 根 AGENTS.md 指针：`D1-D18`/`B01-B14` 零残留（既有项），无 `B16+` 残留误指

### 实施后验收（dogfood v3，2026-10-08 重定；v1 七观察点随其五作废）

**dogfood #1（段一，裸项目）**：用户扮演许愿者"做一个国际象棋游戏"。验收点：①真对话感（开线头/追问/挑战假设/跟答案分叉——非问卷串行）②理解回写出现且被纠错一次 ③分节确认逐节过 ④产物=多迭代 roadmap 且首迭代边界清晰（对照 H1/H2 判据）⑤RA 取迭代 1 且**迭代子集限定与六领域对账在场**（D20.12 组合边界/一致性两条在迭代 1 绿地为空集，全量验证在 dogfood #2 再入路径）⑥中途一次结构化工具调用（离散决策）⑦结晶前**零产物写盘**（审计条目除外）⑧开场判据宣告出现。

**dogfood #2（段二，自 #1 完成态续跑）**：完成仪式三分支走"开新迭代"→ 不改形路径 jump RA（迭代 2：FR 续编/组合边界影响/一致性检查）→ 改形路径 jump brainstorm 各一次；加测：brainstorm 中喊"激活自主模式"验延迟宣告与审计（不写 Enabled）；会话中断重开验放弃语义；小愿望 N=1 退化与 express/bugfix 零迭代开销走查（D20.10）。

**记录**：过程与结论回填本档案验证节与遗留节；方向性通过即段通过（单样本不追求统计功效，消融对照不强制）。

## 遗留与去向（预定）

- `docs/engine-illustrated.md:340` 流程图（questions file → question tool → answers → QT-02 write-back）仅描 Structured 路径——〔2026-10-08 注：Chat/Self-edit 两模式已随其六退役，本条收窄为"v3 落地后补 product-brainstorm 阶段格"〕，留待后续
- 实施完成后按 §7 生命周期第 3 步翻转状态并回填实施/验证/审核/遗留四节

## 附注

- v2.0 对应物：stage-protocol.md §3（三模式选择 :366-383、Guide me :387-461、Self-edit :463-470、Chat :472-481、write-every-pending-question :512-521）+ question-rendering.md（numbered-prose 渲染、consolidated-summary checkpoint、"END THE TURN" 句式）——〔2026-10-08 注：三模式语义已随其五证伪/其六退役，本条留作历史考证〕
- Trellis 二次吸收对照源：`opencode-suit/trellis/.opencode/skills/trellis-brainstorm/SKILL.md`（Evidence Rule :16-24、Question Rules :65-82、First Principles :84-125、Convergence Gate :127-140、PRD Convergence Pass :172-185）与 `.trellis/workflow.md`（breadcrumb 不变量 :99-142）；登记类设计输入（Phase 4/5A 块与 §6 两行）同日落 integration-plan
- 与 B02 附注二"扩展配置成熟度重估（搁置）"的关系：本批不触碰该搁置项——opt-in 问题仍挂在 RA 澄清问题文件里，其"需求太清晰时不重问"盲区维持原搁置状态
- 本批不改 7 个阶段文件的决策（D19.24 优先级条款路线）如后续 dogfood 发现阶段文件旧指令频繁误导执行，升级为改写批处理（B17+ 候选）——〔2026-10-08 注：D19.24 已随其六退役（D19.44）；7 文件的手工收集指令在 v3 下回归原状由 QT-01/QT-04 覆盖，本条历史理由失效，升级判据转由 dogfood #1 观察〕
- 根 `AGENTS.md` 导语的 D/B 区间指针曾因本批立项漏同步（D1-D18/B01-B14 两处，另一会话发现、2026-10-07 确认）——当日补修 + integration-plan §7 新增"指针同步"纪律；本批验证节含该指针零残留核验
