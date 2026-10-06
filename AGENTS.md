# AGENTS.md — aidlc-skills 仓库指南

本仓库是 **AI-DLC（AI-Driven Development Life Cycle）技能的分叉与整合工作区**：以 v1.0 纯 Markdown 技能为基座进行分叉演进，分阶段吸收 v2.0 的先进理念。

**开始任何工作前，先读 `docs/integration-plan.md`**——它记录了全部已确认的决策（D1-D18）、v2.0/v1.0 对比分析、分阶段路线图（Phase 0-5+）和各阶段完成状态，是本仓库的单一权威上下文。

## 目录结构与职责

| 路径 | 性质 | 说明 |
|---|---|---|
| `.agents/skills/aidlc-workflows/` | **工作对象（可写）** | v1.0 分叉，原地进化中。Markdown 技能 + 必选 Python 运行时引擎（SKILL.md + references/ + scripts/），任何 harness 可加载 |
| `opencode/` | **只读参考** | v2.0（opencode 插件形态，v2.7.1）。整合的理念来源，**不要修改**。权威导览见其 `AIDLC-PLUGIN.md` |
| `opencode-cn/` | 只读参考 | v2.0 中文版对应物 |
| `aidlc-workflows-cn/` | 只读参考 | v1.0 中文版对应物（暂不纳入整合范围） |
| `docs/` | 可写 | 项目文档。`integration-plan.md` 是整合路线图 |
| `README.md` / `README_cn.md` | — | 仓库自述 |

## 核心架构约定（v1.0 分叉）

### 1. 阶段契约是唯一事实源（SSOT）

- 每个阶段规则文件（`references/<phase>/*.md`）顶部的 **YAML frontmatter 是阶段清单的唯一事实源**（slug/phase/execution/condition/gate/produces/consumes/requires_stage/for_each/workspace_writes/depth/scopes）。
- 字段定义与校验规则见 `references/common/stage-contract.md`。
- SKILL.md、welcome-message、session-continuity、workflow-planning 中的阶段清单全部是 **`<!-- BEGIN/END GENERATED: <key> -->` 标记区内的生成物——严禁手改**。

### 2. 作者期生成器

- 脚本：`.agents/skills/aidlc-workflows/scripts/generate.py`（纯 Python 标准库，无第三方依赖）。
- **改动任何阶段 frontmatter 后必须运行**：
  ```cmd
  python .agents\skills\aidlc-workflows\scripts\generate.py
  ```
- 提交前用 `--check` 验证无漂移（非零退出 = 有未同步的生成物）。CI 兜底：`.github/workflows/contract-check.yml` 在 push/PR 时自动跑 `--check`。
- 生成器有测试套件 `scripts/tests/`（stdlib unittest）：`python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests`，改生成器后必跑。
- 验收标准：二次运行幂等；标记外内容零改动。
- 所有脚本（含作者期工具）一律放技能目录的 `scripts/` 下（Agent Skills 规范）。

### 3. Harness 无关性护栏（2026-09-14 修订）

- 技能必须保持 **harness 无关性**：任何能加载技能且能执行 shell 的 AI 编码工具可用；不得绑定特定 harness 的钩子/插件机制。
- **Phase 3 起引入单一运行时依赖：Python 3.8+**（编排引擎必选，决策 D6 修订——原"零运行时依赖、引擎可选增强层"立场废止，理由见 `docs/integration-plan.md` §9）。
- 作者期工具（generate.py）与运行时引擎（engine.py）一律放技能目录的 `scripts/` 下；引擎随技能分发，用户侧零安装步骤（仅需环境有 Python）。

### 3.1 运行时引擎（Phase 3 起）

- 引擎 `scripts/engine.py` 是**必选运行时组件**：独占跨阶段路由（`next`）、状态机转移（`report` 是唯一写入口）、审计转移条目、状态完整性校验（State Digest sha256 + 审计交叉核验 + `rebase`）、改道（`jump`/`jump --fresh`；工作流完成态下 `jump --stage` 放行为**同产品再入**——目标及其后重置、语义同 backward redo，`--fresh` 留给新产品意图，D15）、会话泊车注记（`park --note`：写状态文件 Last Parked 行 + `aidlc-docs/handoff.md`，不改 marks/current、不写审计）、权威时间戳读取（`stamp`，零副作用）。`aidlc-docs/handoff.md` 为引擎独写，模型不得手改。
- 引擎**只读**作者期编译产物 `scripts/data/stage-graph.json`（generate.py 生成，--check 覆盖其漂移），**永不解析 frontmatter，也永不解析 condition 散文**（CONDITIONAL 阶段照常发射 `conditional: true`，模型判断不适用则 `report --result skipped --reason`）。
- 状态文件分区所有权（`references/common/engine-contract.md`）：`<!-- BEGIN/END ENGINE-STATE -->` 标记区内（Stage Progress/Current Status/Unit Progress/State Digest）引擎独占、digest 覆盖；区外（Project Information/Execution Plan Summary/Autonomous Mode/Extension Configuration 等）模型按模板写。Execution Plan Summary 的结构化行（Scope/Depth/Stages to Execute/Skip）是模型写-引擎读的 load-bearing 通道（Autonomous Mode 区的 `autonomous` 键与 Extension Configuration 表的 checkpoint 探测同属模型写-引擎读，引擎只宽容读取、不改变所有权）。**唯一引擎写模型区例外（AM-10 轮次边界过期，2026-09-28）**：引擎在完成转移与再入 jump 两个确定性边界可把 Autonomous Mode 区的 `Enabled` 行翻转为 No（连同既存 Last Updated 行），宽容 no-op；触发互斥是纪律约定非机制保证（该区不在 digest、无锁），见契约 §6。
- 引擎测试与生成器测试同套件（`scripts/tests/`，共 237 例）：改引擎后必跑 `python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests`。

### 4. 编辑纪律

- **先考证，后修复**：当认为工作流/引擎存在问题并准备调整前，必须先查证历史与背景——读 `docs/integration-plan.md` 的决策与实施期裁决、相关契约文档（stage-contract.md / engine-contract.md）中的字段语义，弄清楚该行为当初为什么这样设计、是否故意为之、修复后会产生什么副作用，再决定下一步行动（现在修 / 留后续 Phase / 仅补文档）。看似缺陷的行为可能是记录在案的已知弱点或契约定义内的语义（2026-09-15 dogfood 教训：consumes 的 required 语义、节标题静默回退均在契约中有明确定义）。
- 修改阶段规则：正文可直接改；frontmatter 改动后必须跑生成器。
- 新增阶段 = 新建一个带 frontmatter 的阶段文件 + 跑生成器（无需改其他文件）。注意 `scopes:` 必须为 `references/common/scopes/` 中注册的每个 scope 显式填值（漏填生成器报错并列出清单）；新增 scope = registry 加文件 + 所有阶段补一列 + 跑生成器。
- `opencode/`、`opencode-cn/`、`aidlc-workflows-cn/` 只读。
- 技能文件（SKILL.md、references/）用**英文**撰写；`docs/` 下的工作文档用**中文**。

## 路线图速览（详见 docs/integration-plan.md）

- **Phase 0/1/2 ✅ 已完成**：阶段契约化 + 生成器（本文件 §核心架构约定即其成果）；scope 裁剪矩阵（`references/common/scopes/` 6 个 scope：classic[默认]/bugfix/refactor/security-patch/infra/express；阶段 frontmatter 的 `scopes:` 映射转置生成矩阵；Requirements Analysis 选 scope，Workflow Planning 微调）
- **Phase 3 ✅ 已完成（2026-09-14）**：轻量编排引擎落地——"判断归 LLM，精确归工具，决定归人类"。`scripts/engine.py`（Python stdlib 必选运行时引擎：status/init/next/report/jump/rebase）+ compile-to-JSON（generate.py 编译 `scripts/data/stage-graph.json`，引擎只读 JSON）+ 状态分区所有权（`references/common/engine-contract.md`：ENGINE-STATE 标记区引擎独占 + State Digest 完整性校验 + rebase）+ 全 references/ 手改 state 指令收口 + stdlib unittest 测试套件（CI 同跑 --check 与测试套件；当时 77 例，现累计 237 见 §3.1）+ 裸项目 dogfood 通过
- **Phase 3.1 ✅ 已完成（2026-09-22）**：会话连续性——park 泊车动词（D13 动词三层纪律：转移=report/jump 封闭集合，park 是注记）+ status 恢复简报（resume_note/recent_events/artifact_alerts/alerts_unavailable，分级阅读取代 Load ALL）+ 传感器第一代（D14 finding 五字段，fail-open）+ report produces_missing 软警告；测试当时 144 例（现累计 237 见 §3.1）
- **Phase 3.2 ✅ 已完成（2026-09-22）**：Trellis 借鉴立即批（机制移植，零代码复制）——Evidence-First 提问纪律（question-format-guide 顶部 Policy+豁免表，9 文件 sweep 指针）+ DOC-06 长制品导航索引（advisory）+ RE 可选产物 working-conventions.md（Phase 5A 知识树种子）+ B&T Commit Protocol（时序定死/AUD-02 先例/AM-03 不自动 commit）+ docs/dogfood-protocol.md（六度量+消融对照，服务 3.1 后首个 dogfood 周期）+ 契约硬规则单测清零（§7 规则 1-16 全覆盖，含保留键夹具；测试 144→169）；登记表见 docs/integration-plan.md §9
- **Phase 3.3 ✅ 已完成（2026-09-24）**：dogfood 反馈批（fx991 首周期验收产物）——P0 裁决 CTX 维持 opt-in（推迟 Phase 4 终裁）+ WP-1 engine 扩展（stamp 零副作用时间戳动词 / status `autonomous` 键 / `note_age_seconds` / checkpoint-missing finding[warning，仅 CTX 启用时]）+ WP-2 SKILL.md 强制扩展发现步骤（Loading process 第 4 步）+ WP-3 workflow-changes Type 10 范围收缩规程（rejected→jump→就地修订[DOC-04 边界]→Deferred 保留→重走）+ WP-4 DOC-04 保护边界判例 + DOC-01 sweep 声明纪律 + WP-5 `scripts/trace-matrix.py` 追溯矩阵脚本（不进 CI）+ WP-6 QT-01 结构化提问工具能力抽象（去 OpenCode 绑定，AM 文件 8 处同步）；测试 169→205；AM 专用动词明确移 Phase 4；规格见 docs/integration-plan.md §7
- **修复批 ✅ 已完成（2026-09-27）**：完成态再入（D15）——dogfood 实证"新会话 + 已完成 MVP + 加新功能"被引擎 hint 与菜单合力推向 `jump --fresh`（四环链路：invalid-jump hint 指路 fresh / SKILL.md completed 行无路由 / 菜单 C 唯一"开始"项 / workflow-changes 域限定 mid-workflow）。裁决：同产品功能演进不是新产品意图，走就地再入。实施：engine `cmd_jump` 完成态（current=None）放行为再入（目标及其后重置，语义同 backward redo，ack.from=null，审计记 re-entry；裁决③"jump 不绕过计划过滤"对再入同样生效）+ park workflow-complete hint 改写 + SKILL.md completed 行路由 + session-continuity 菜单 C 定位收缩 + workflow-changes 新增"Re-Entering a Completed Workflow"节 + 契约 §8/§9/§10 同步；测试 205→209
- **AM 生命周期批 ✅ 已完成（2026-09-28）**：D16——自主模式绑定工作流轮次（dogfood 实证"开启一次、代代相传"）。实施：引擎 `_expire_autonomous` 窄写（完成转移/再入 jump 两边界翻转 `Enabled: Yes→No`，ack `autonomous_expired` + 审计 detail，缺失/畸形/已 No 宽容 no-op）+ AM-10 三边界规则（completion=引擎翻转+宣告 / re-entry=jump 翻转+计划行自复活路径模型兜底 / fresh=归档即消失）+ AM-05 重写"暂停即彻底关闭"（二选一：标准继续 / 重激活=全新 AM-02 重问）+ AM-02 激活双问（问题处理方式 + 审核阶段多选**预选**当前列表；生成块 stage-names 随迁，generate.py 注册表不动）+ Review Stages 编辑入口从暂停菜单迁至激活流与轮内显式请求 + AM-04 两处单题升级不再借道暂停 + 契约 §5/§6（唯一模型区窄写窗口条款）/§8/§9/§10 同步 + 外围 4 文件（session-continuity/SKILL/workflow-conventions/workflow-changes）+ AM-09 completed=off + opt-in 区间扩展；reviewer 独立审核三阻断项全修（自复活绕过→模型兜底、Phase 4 移出项张力→收编路径记录、残留引用 5 处入清单）；二轮实施审核又修复 B-1 前向 jump 完成漏触（挂钩条件放宽为"跳转后处于完成态"，审计注记分流 re-entry/jump completed the round）；三轮终审修复 §6 窄写窗口条款残留的两边界枚举（与 §8 相抵）并补齐 (再入,保持完成态) 矩阵格用例；测试 209→227（新增 AutonomousExpiryTests 18 例）
- **收尾小批 ✅ 已完成（2026-09-28）**：fx991 三迭代 dogfood 收官——A1 Depth 行值纯净双侧修复（引擎 `_strip_inline_note` 剥注仅 Depth 分支，Scope 保持粘连注解 plan-invalid 硬阻断；RA Step 2.5 模板改裸值、init 模板改裸枚举、workflow-planning Step 8 补值纯净规则、契约 §6 格式注精确化）+ A2 AUD-05 审计追加纪律（Group 3 更名 Audit Discipline；新条目锚定文末单次追加、禁以既有标题行为编辑锚点；SKILL.md 同步一行）+ B3 组合边界检查项（RA Step 7，普适：新交互/行为维度 × 既有横切行为组合边界逐项声明）+ C5-C7 登记（produces_missing 关闭时点不变[2026-09-24 裁决，累计 5 周期零触发]、dogfood-protocol 度量 3/4 N/A 规则与决策回填泛化、§7/§9 引用纪律两类分治与失联标注、Phase 5A rollup 首批实证）；测试 227→231；验收登记见 docs/integration-plan.md §9 2026-09-28 其三
- **AM 简化 + Code-Gen Hold 批 ✅ 已完成（2026-09-29）**：D17——去除审核阶段机制并新增代码生成前停点。实施：AM-06 整体移除（编号退役不重排）+ AM-03 全阶段自动批准 + AM-02 双问改轨（问题处理方式 + 代码生成前停点[每次全新问，任何持久化配置值不作预选]）+ AM-05 二次重写为优雅暂停（模式关闭 → 完成手头工作 → 标准模式继续到下一个审批门等人工，直到本轮结束不自动恢复；菜单删除；与 Park Ritual 优先级消歧）+ AM-11 新增（停点：布防条件=code-gen 未开工、触发三路径、放行 Passed+审计、其他答复后仍等继续语义、每次激活一次、模式穿越保持开启）+ AM-07 缩为等价入口 + AM-08 模板换行（Code-Gen Hold 四态）+ 引擎 status autonomous 键删 review_stages（宽忽略未知行）+ generate.py stage-names 注册退役（stage-contract 宿主清单同步）+ engine-illustrated 锚点对账；reviewer 计划审核 2 阻断（清单漏 engine-illustrated / AM-11 触发空洞）+ 10 建议 + 3 存疑全处置；测试 231 不变（1 例改名）；登记见 docs/integration-plan.md §9 当日条目
- **AM 提问零配置批 ✅ 已完成（2026-09-29）**：D18——激活提问收敛为单问。实施：AM-02 单问重构（只问代码生成前停点，"ONE tool invocation, ONE question"；宣告补"问题自动选推荐答案"）+ AM-04 固定行为化（删 manual/custom 配置形态，保留 6 点与升级路径，新增轮内显式指示出口[可容纳持续性指示]）+ AM-08 模板删 Question Handling 行（三行制）+ 引擎 `autonomous` 键删 question_handling（`{enabled, last_updated}`，宽忽略未知行）+ workflow-conventions QT override 无条件化（加 AM-04.6 豁免子句）+ session-continuity 三处 + engine-illustrated 17 锚点（与审核映射零偏差）；reviewer 计划审核 1 阻断（3 处编号残留+清扫盲区）+ 6 建议 + 2 存疑全采纳；测试 231 不变；登记见 docs/integration-plan.md §9 当日其二
- **备份遗产清理批（待实施，2026-09-28 立项）**：v1.0 `.backup` 惯例与 D11/git 立场相抵——文档 5 处改条件式（git 工作区走 commit、非 git 才 `.backup.{timestamp}`，对齐 AUD-02 先例）+ 引擎 `resumed-artifacts` glob 排除 `.backup` 文件；规格与考古证据见 docs/integration-plan.md §9 当日条目
- **文档减法清理批 ✅ 已完成（2026-09-29）**：D-清系列——纯减法·语义等价（五类判据：重复副本/路由遗物/墓碑纪事/教学冗余/死文件），计划经两轮 reviewer 审核（v2.2）。三批落地：①删除先行（整删 process-overview/terminology，generate.py 死渲染函数清理 + RenderMapCoverageTests 防回归）；②判据通路（**D-清9：CONDITIONAL 判据唯一权威 = 阶段 frontmatter `condition` 浅映射 `{execute_if, skip_if}`，ALWAYS 保持标量双形态校验，生成器渲染进 scope-matrix 生成区的 "CONDITIONAL Stage Criteria (authoritative)" 清单**；WP0 三方比对调和消灭分歧副本）；③散文减法（SKILL.md 631→343 行、error-handling -46%、AM-06 墓碑压缩、AWS 例子删留框架、审计弹幕指向 AUD 组）。必加载集 97.1KB→73.3KB（-24.5% 实测）；测试 231→236 全绿；§复审 backlog "陈旧散文"项全销；后续三批已登记（代码批·旧格式兼容层退役[legacy 分支/宽容解析/旧格式夹具三层一体]/代码摸底批[opt-in 大文件]）；登记见 docs/integration-plan.md §9 当日其三；2026-10-06 双臂 dogfood 验收：**方向性通过**（腿1/1b 决策一致+新判据溯源零残留；腿2 出局、快照血统断裂与主项目快照漂移登记，4 项改进排队），见 §9 当日四与 docs/dogfood-records/fx991-calculator-slimming-ablation-2026-10-06.md
- **Phase 4**：Team Construction（unit-major 波次地基 → claim/release + worktree 多会话团队 → single 重跑 → swarm）
- **Phase 5A/5B + 不排期**：5A 知识树与学习闭环 / 5B reviewer 及其他；④档三项带触发条件（详见 integration-plan.md）

## 环境

- Windows 11 + cmd.exe（不要用 PowerShell 语法或 Unix 命令）。
- 生成器只需系统 Python（3.8+），无虚拟环境要求。
