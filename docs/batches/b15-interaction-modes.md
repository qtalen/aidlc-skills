# B15 · 提问交互三模式批（待实施）· 2026-10-07 立项

| 项 | 值 |
|---|---|
| 状态 | ⏳ 待实施（2026-10-07 立项，规格经 reviewer 计划审核后收口） |
| 触发 | 用户即期需求——问卷制缺少自由讨论形态，意图不明/一句话需求时无"先聊聊"的空间 |
| 关联决策 | D19（本批产出，23 项子裁决随立项确认，见规格节）；与 D16-D18（AM 链）在 AM-04 交互面耦合 |
| 测试基线 | 立项时 237；实施时 237→238（+1 规则文本断言） |
| 材料来源 | 2026-10-07 会话讨论链（v2.0 §3 考证 → 用户三决策 → 五轮边界迭代 → 计划 v1 → reviewer 审核 → v2 终稿）；v2.0 证据：`opencode/.aidlc/aidlc-common/protocols/stage-protocol.md` §3（:330-530）、`opencode/.aidlc/skills/aidlc/question-rendering.md` |

## 立项与裁决

**背景**：现行提问纪律是问卷制（问题文件 + 选项填空 / QT-01 结构化工具勾选）。v2.0 考证发现其 §3 已有成熟三模式设计（Guide me / I'll edit the file / Chat），且核心不变量"任何模式下待答问题必须先落文件（空白 `[Answer]:`）"证明**聊天讨论与问题文件纪律不冲突**——聊天是答案收集模式，不是绕开文件的后门；Chat 模式答案由模型提取（错提风险高于用户亲手填），故 v2.0 为其强制"生成前汇总确认"。

**裁决（用户，2026-10-07 讨论链逐项确认）**：
1. 三模式**全阶段适用**（协议住 question-format-guide + QT 组；阶段文件不动，经审核修正为显式优先级条款，D19.24）；
2. 模式入口：RA 问一次 + 会话粘性 + 随时切换（经讨论修正：挂**会话内第一个问题文件**而非 RA 专属；恢复会话不重问，D19.27）；
3. 生成前汇总确认**仅 Chat 模式**；
4. reviewer 计划审核为**维护者侧工序**，不构成技能依赖（可移植性无损，与 executor 子智能体同类）。

## 规格

### 决策清单 D19.1~29

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
- D19.17 收束路径两条收敛到同一确认点：用户 done → 回写 → 确认；模型判断已收敛 → 回写 → **呈现确认即提案** → STOP
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
- D19.29 **park/AM 交互三条**：①park 于聊天中 → 泊车前执行回写（D19.11 第 1 步），空白标签 + park 注记承载恢复；②AM 激活于聊天中 → 先回写已提取决策，未答部分转 AM-04；③自主模式激活话语进消解阶梯路由表，优先于 chat 切换解释

**不在本批**：`gate: none` 两阶段（WD/operations）的有意设计不重开；跨会话模式持久化不做。

### 改动面（10 文件）

| # | 文件 | 改动 |
|---|---|---|
| 1 | `references/common/question-format-guide.md` | "Never Ask in Chat"→"Questions Live in Files — Chat Is Only a Collection Mode"（三模式表 + 两个聊天豁免元问题 + 文件不变量）；豁免表加模式选择行并修正 :15 "only" 措辞；顶部优先级条款（D19.24）；问题边界定义（D19.25）；新增 Chat-Mode Write-Back 格式节（`**Mode:** chat` 标注、间接 remarks 依据行、Consolidated Summary Confirmation 文件格式、carve-out 三条 D19.26）；interaction mode ≠ Autonomous Mode 区分句；Summary 清单更新 |
| 2 | `references/extensions/workflow/workflow-conventions/workflow-conventions.md` | 组更名 Question Tool Flow → **Question Flow (QT)**；Overview 行（:10）同步；Group 4 导言：三模式 + 信号意图分类通则 + 终止符用户所有 + 优先级条款 + AM 区分句；AM override 段补模式不可用；QT-01/QT-03 加模式适用前置（Structured 适用 / Self-edit 走基础流 / Chat 走 QT-06）；新增 QT-05（首文件挂载、预声明免问、意图类切换、消解阶梯、会话级单变量、自适应菜单、恢复会话判别、audit）；新增 QT-06（先落文件、收束判据、开谈立规矩、双路径收束、强停、非匹配规则、循环无上限、park/AM 规则）；Enforcement 表 QT-01~06 |
| 3 | `references/inception/requirements-analysis.md` | Step 6 加模式入口行 + 收集方式行改模式化表述（替换"Request user to fill in all [Answer]: tags directly"）；⛔ GATE（:190-192）改模式中性表述 |
| 4 | `references/common/session-continuity.md` | #12 改写：问题住文件；两个聊天豁免元问题；chat 是受约束的收集模式（先落文件不变量） |
| 5 | `references/extensions/workflow/autonomous-mode/autonomous-mode.md` | AM-04 补一句：模式问题不问、chat 不可用、in-round 指示按既有条款 |
| 6 | `SKILL.md` | Question File Format 节（生成区外，:71-78 已核）加一个 bullet：三交互模式，指向 QT-05/06 |
| 7 | `scripts/tests/test_rule_invariants.py` | 新建：1 条规则文本断言——技能树无 `QT-01 ~ QT-04`/`QT-01~04`/旧组名残留（大小写不敏感）+ 两个聊天豁免在 qfg 与 session-continuity 同时在场（B11 锚定先例） |
| 8 | `docs/integration-plan.md` | 单行 D19（本批立项已落）+ 批次登记表 B15 行 + "Phase 4=B15+"位移括注修正（随本批立项同步完成） |
| 9 | `docs/batches/b15-interaction-modes.md` | 本档案；完成时回填实施/验证/审核节 |
| 10 | `AGENTS.md` | 路线图 B15 行（立项时已加）；§3.1 测试数 237→238（实施时同步） |

### 工序

1. ~~reviewer 计划审核~~ ✅（见下节）
2. 主智能体实施：10 文件按 1→7 序（先协议权威文件，后外围引用，再测试）——豁免依据：根 AGENTS.md 委派条款"简报无法写得比改动本身更紧凑，则不属机械性实施，由主智能体直接完成"（规则散文的全文即简报本体）
3. 验证（见验证节）→ 4. 登记（§3 行更新/§2 已落/AGENTS.md 测试数）→ 5. 可选 commit（按 B&T Commit Protocol，用户开口才提交）

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

## 实施与实施期裁决

（待实施）

## 验证（预定验收标准）

- `python .agents\skills\aidlc-workflows\scripts\generate.py --check` 退出码 0（纯正文改动，预期零漂移）
- `python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests` **238 例全绿**（新增 test_rule_invariants.py 1 例；引擎/生成器零改动，既有 237 预期零变化）
- 清扫串技能树清零（历史档案/docs 记载豁免——惯例不改）：`Never ask questions in chat`、`sole exception: the Requirements Analysis`、`QT-01 ~ QT-04`、`QT-01~04`（大小写不敏感）、`Question Tool Flow`、`only chat question`
- 交叉引用人工核对：QT-05/06 ↔ question-format-guide ↔ RA Step 6 ↔ session-continuity #12 ↔ AM-04 ↔ SKILL.md 六处互指一致；两个聊天豁免（scope、模式）所有提及处对齐
- 生成区标记内零改动；`opencode/`、`opencode-cn/`、`aidlc-workflows-cn/` 只读目录零触碰
- 点名已核无需改：error-handling.md:36（矛盾/歧义处理显式 defer 给 qfg）；welcome-message 生成区（仅 ascii-diagram，无提问内容）

## 遗留与去向（预定）

- `docs/engine-illustrated.md:340` 流程图（questions file → question tool → answers → QT-02 write-back）仅描 Structured 路径——本批不触引擎，Chat/Self-edit 路径图为可选同步，留待后续
- 实施完成后按 §7 生命周期第 3 步翻转状态并回填实施/验证/审核/遗留四节

## 附注

- v2.0 对应物：stage-protocol.md §3（三模式选择 :366-383、Guide me :387-461、Self-edit :463-470、Chat :472-481、write-every-pending-question :512-521）+ question-rendering.md（numbered-prose 渲染、consolidated-summary checkpoint、"END THE TURN" 句式）
- 与 B02 附注二"扩展配置成熟度重估（搁置）"的关系：本批不触碰该搁置项——opt-in 问题仍挂在 RA 澄清问题文件里，其"需求太清晰时不重问"盲区维持原搁置状态
- 本批不改 7 个阶段文件的决策（D19.24 优先级条款路线）如后续 dogfood 发现阶段文件旧指令频繁误导执行，升级为改写批处理（B16+ 候选）
