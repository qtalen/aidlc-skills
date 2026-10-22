# AGENTS.md — aidlc-skills 仓库指南

本仓库是 **AI-DLC（AI-Driven Development Life Cycle）技能的分叉与整合工作区**：以 v1.0 纯 Markdown 技能为基座进行分叉演进，分阶段吸收 v2.0 的先进理念。

**开始任何工作前，先读 `docs/integration-plan.md`**——它记录了全部已确认的决策（D1-D27 + D-清系列）、批次登记表（B01-B21）、分阶段路线图（Phase 0-5+）、开放项总账与维护规程，是本仓库的单一权威上下文。历史细节住在 `docs/batches/`（每批一个档案）与 `docs/archive/`（冻结档案）。

## 目录结构与职责

| 路径 | 性质 | 说明 |
|---|---|---|
| `.agents/skills/aidlc-workflows/` | **工作对象（可写）** | v1.0 分叉，原地进化中。Markdown 技能 + 必选 Python 运行时引擎（SKILL.md + references/ + scripts/），任何 harness 可加载 |
| `opencode/` | **只读参考** | v2.0（opencode 插件形态，v2.7.1）。整合的理念来源，**不要修改**。权威导览见其 `AIDLC-PLUGIN.md` |
| `opencode-cn/` | 只读参考 | v2.0 中文版对应物 |
| `aidlc-workflows-cn/` | 只读参考 | v1.0 中文版对应物（暂不纳入整合范围） |
| `docs/` | 可写 | 项目文档。`integration-plan.md` 是主文档（决策登记/批次登记表/路线图/开放项总账）；`docs/batches/` 为执行批次档案（B01-B21）；`docs/archive/` 为冻结档案 |
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
- **Phase 3 起引入单一运行时依赖：Python 3.8+**（编排引擎必选，决策 D6 修订——原"零运行时依赖、引擎可选增强层"立场废止，理由见 `docs/batches/b03-orchestration-engine.md`）。
- 作者期工具（generate.py）与运行时引擎（engine.py）一律放技能目录的 `scripts/` 下；引擎随技能分发，用户侧零安装步骤（仅需环境有 Python）。

### 3.1 运行时引擎（Phase 3 起）

- 引擎 `scripts/engine.py` 是**必选运行时组件**：独占跨阶段路由（`next`）、状态机转移（`report` 是唯一写入口）、审计转移条目、状态完整性校验（State Digest sha256 + 审计交叉核验 + `rebase`）、改道（`jump`/`jump --fresh`；工作流完成态下 `jump --stage` 放行为**同产品再入**——目标及其后重置、语义同 backward redo，`--fresh` 留给新产品意图，D15）、会话泊车注记（`park --note`：写状态文件 Last Parked 行 + `aidlc-docs/handoff.md`，不改 marks/current、不写审计）、权威时间戳读取（`stamp`，零副作用）。`aidlc-docs/handoff.md` 为引擎独写，模型不得手改。
- 引擎**只读**作者期编译产物 `scripts/data/stage-graph.json`（generate.py 生成，--check 覆盖其漂移），**永不解析 frontmatter，也永不解析 condition 散文**（CONDITIONAL 阶段照常发射 `conditional: true`，模型判断不适用则 `report --result skipped --reason`）。
- 状态文件分区所有权（`references/common/engine-contract.md`）：`<!-- BEGIN/END ENGINE-STATE -->` 标记区内（Stage Progress/Current Status/Unit Progress/State Digest）引擎独占、digest 覆盖；区外（Project Information/Execution Plan Summary/Extension Configuration 等）模型按模板写。Execution Plan Summary 的结构化行（Scope/Depth/Stages to Execute/Skip）是模型写-引擎读的 load-bearing 通道（Extension Configuration 表的 checkpoint 探测同属模型写-引擎读，引擎只宽容读取、不改变所有权）。**引擎永不写任何模型区**（B18 随 AM 退役废止了唯一例外——AM-10 轮末过期翻转；所有权边界回到干净不变量），见契约 §6。
- 引擎测试与生成器测试同套件（`scripts/tests/`，共 254 例〔B21 后：251 + PD 对话质量守卫 +3；B20 后：249 + APG 退役/组号守卫与停点不变量守卫 +2；B19 后：239 + review_class 枚举/映射/交叉/门模板行断言 +10；B18 后曾为 239——AM 测试退场 -21、brief/BRF 断言 +7、终审残留守卫 +1、门规则测试改锚净 -1〕，2026-10-08 起含 test_rule_invariants.py 规则文本断言，2026-10-12 起含 test_extension_layout.py 扩展发现不变量）：改引擎后必跑 `python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests`。

### 4. 编辑纪律

- **先考证，后修复**：当认为工作流/引擎存在问题并准备调整前，必须先查证历史与背景——读 `docs/integration-plan.md` 的决策与实施期裁决、相关契约文档（stage-contract.md / engine-contract.md）中的字段语义，弄清楚该行为当初为什么这样设计、是否故意为之、修复后会产生什么副作用，再决定下一步行动（现在修 / 留后续 Phase / 仅补文档）。看似缺陷的行为可能是记录在案的已知弱点或契约定义内的语义（2026-09-15 dogfood 教训：consumes 的 required 语义、节标题静默回退均在契约中有明确定义）。
- 修改阶段规则：正文可直接改；frontmatter 改动后必须跑生成器。
- 新增阶段 = 新建一个带 frontmatter 的阶段文件 + 跑生成器（无需改其他文件）。注意 `scopes:` 必须为 `references/common/scopes/` 中注册的每个 scope 显式填值（漏填生成器报错并列出清单）；新增 scope = registry 加文件 + 所有阶段补一列 + 跑生成器。
- `opencode/`、`opencode-cn/`、`aidlc-workflows-cn/` 只读。
- 技能文件（SKILL.md、references/）用**英文**撰写；`docs/` 下的工作文档用**中文**。

## 路线图速览（详见 docs/integration-plan.md；已执行批次的完整记录见 docs/batches/ 批次档案）

- **Phase 0/1/2 ✅**：阶段契约化 + 生成器（B01）；scope 裁剪矩阵（B02，`references/common/scopes/` 6 个 scope：classic[默认]/bugfix/refactor/security-patch/infra/express）
- **Phase 3 ✅（2026-09-14）**：轻量编排引擎落地——"判断归 LLM，精确归工具，决定归人类"。`scripts/engine.py`（Python stdlib 必选运行时引擎）+ compile-to-JSON（`scripts/data/stage-graph.json`）+ 状态分区所有权（`references/common/engine-contract.md`）+ stdlib unittest 测试套件（CI 同跑 --check 与测试，期终 237——现累计 248 见 §3.1）+ 裸项目 dogfood 通过（B03）
- **Phase 3 建设期收尾批 ✅（2026-09-22~24）**：会话连续性 park/恢复简报/传感器第一代（B04，D13/D14）→ Trellis 借鉴立即批（B05）→ dogfood 反馈批 stamp/autonomous 键/Type 10/trace-matrix（B06）
- **演化期小批 ✅（2026-09-27~29）**：完成态再入修复（B07，D15）→ AM 生命周期（B08，D16）→ 收尾小批（B09）→ AM 简化+Code-Gen Hold（B10，D17）→ AM 提问零配置（B11，D18）→ 文档减法清理（B12，D-清1~9，必加载集 -24.5%，10-06 双臂 dogfood 验收方向性通过）
- **文档重组批 ✅（2026-10-07）**：integration-plan 拆分为主文档 + 批次档案 + 冻结档案，Phase/B/D 三层体系归一（B14）
- **Phase 3.4 ✅（2026-10-07 立项，10-08 重定义并全量落地）**：产品演进闭环（首批=合并批 B15，D19 其六 + D20 全量并入）——头脑风暴阶段 + roadmap 活文档 + 迭代交付环 + 完成仪式；段一（战略层 11 项）落地（240 绿），dogfood #1 全程过（8/8+P7~P12；迭代 1 同日建到 done——39/39 测试、E2E file:// 实证、roadmap flipped shipped）；段二（交付环 D1~D8 + P7/P8/P10 修复）落地（247 绿+零漂移）；dogfood #2 全程过（六项全收：改形再入全链/AM 延迟+Hold+轮末过期全生命周期/中断放弃语义/N=1+express 纸面走查；P13 回合边界条款+P14 B&T 条件修复当场落地、P11 维持；迭代 2 本机双人 shipped——49/49、E2E 五景、56.45 kB）；收口提交后本相位闭环（**248 绿**）；后续 Operations 实义化（B22+ 候选，开放项挂账；B18 已被门姿态与 AM 退役批、B19 已被 reviewer 前置接线批、B20 已被规则层精简批、B21 已被 PD 对话质量批占用）
- **B18 门姿态与 AM 退役批 ✅（2026-10-19 立项·四项裁决全按推荐，10-19~20 实施）**：`gate: brief` 第四门型（编译映射 `none`，引擎门判定零改动）+ 四硬门处置地图（PB/RA 引擎硬门 + code-generation 规则级方向停点〔每轮首单元前 ≤10 行方向简报〕+ 完成仪式人工门；**11 阶段降简报**——workflow-conventions 新增 BRF-01~03）+ AM 全量退役（**D22 取代 D16-D18**、D23 门姿态登记；引擎回到永不写模型区、`autonomous` 键与 `autonomous_expired` ack 退场；AM-04 升格为 Stage Question Posture 通用提问规则、B&T commit 授权改显式问句永不自动）；238 绿 + `--check` 零漂移（253→238 精确对账）；收口终审（reviewer）5 项第一层发现 + 8 改进 + 4 建议全部处置后 **239 绿**（+1 简报残留守卫断言）
- **B19 reviewer 前置接线批 ✅（2026-10-20 立项·D-1~D-7 裁决 + 密度复议，同日单会话实施）**：三位置委派审查（RA 门材料前 / 方向门简报前 / B&T 收尾简报前——`review_class` frontmatter 三值枚举 + 编译）+ **D24 登记**（全新会话纪律〔唯一例外 ④ 自审 degraded〕+ 三轮预算〔事件定义、再入不清零，取代"预算为一"〕+ 降级链四档〔含推模式〕+ findings-only 三元组契约 + reviews.md R-n/T-n append-only 日志〔DOC-04 双落点〕+ B&T 审代码〔按位置锚点表 + 执行依赖维度条件化 not-covered + 修复先重跑测试〕+ 技能级零快照〔L3 挂账、触发条件内联〕）；新增 `references/common/review-delegation.md`（RV-01~08）+ rubric 库（index + 3 类；另 2 类留 5B）+ 四阶段锚点；**249 绿**〔239+10〕+ `--check` 零漂移；两轮规格终审（12+9+4 / 6+6+5）+ 两轮收口终审（6+4+5 / 2+5+5）全处置；dogfood 迭代二验证（协议新增 §四 R1~R8 + 迭代边界快照刷新规则）
- **B20 规则层精简批 ✅（2026-10-21 用户裁决 D25/D26，10-22 实施）**：APG-01~05 退役（硬门交互回归模板原生语义——approve/continue 同义均放行直续、无 hold 层；组号重编 AUD/QT/BRF→Group 2/3/4）+ DOC 文本瘦身（六条编号与语义冻结；DOC-01 删教学映射段、DOC-04 判例压缩为判别式+先例指针）+ 合规报告全局只报例外（workflow-conventions/SKILL.md/三扩展基线统一例外式）；方案经 reviewer 全新会话终审（7 发现/5 改进/5 建议全处置——含 SKILL.md 合规段上位冲突、停点 no-report 不变量钉测试、stage-contract 组号漏网、B20+→B21+ 顺延）；**251 绿**〔249+2 守卫〕+ `--check` 零漂移；dogfood 协议新增 §五 C1~C2
- **B21 PD 对话质量批 ✅（2026-10-22 用户三轮裁决，reviewer 终审后同日实施）**：D27 三组件——研究姿态（预训练为 fallback / 任意时刻按需搜索 / 三档显式降级 / 外部内容 data-not-instructions / 内部既有方案参考 / 引用诚实）+ 提案节奏（Lead with material 反审讯漂移、red flag 三连问）+ 轻量留痕（Source 列 basis: 后缀 + 可选 Prior Art）；范围仅 PB，推广 RA/AD 挂开放项；**254 绿**〔251+3 守卫〕+ `--check` 零漂移；dogfood 协议新增 §六 H1~H2
- **待实施**：备份遗产清理批（B13，规格就绪·删除式 v2——2026-10-09 立场翻转：非 git 亦不留 `.backup`）；外线合流与傻瓜化批（B17，规格就绪·待排期——Phase 4 前置，2026-10-09 用户暂缓，见 b17 档案）；代码批·旧格式兼容层退役等见主文档开放项总账（B15 已全量完成，dogfood 发现账 P9 挂 B22+、P13/P14 已落地）
- **Phase 4**：Team Construction（unit-major 波次地基 → claim/release + worktree 多会话团队 → single 重跑 → swarm；设计输入见主文档路线图；B17 外线合流批为其串行语义地基，规格就绪可先行）
- **Phase 5A/5B + 不排期**：5A 知识树与学习闭环 / 5B reviewer 及其他；④档三项带触发条件（详见主文档路线图与不排期节）

## 环境

- Windows 11 + cmd.exe（不要用 PowerShell 语法或 Unix 命令）。
- 生成器只需系统 Python（3.8+），无虚拟环境要求。
- **Git 提交信息与 tag 标注一律使用英文**（2026-10-15 起；conventional commits 格式照旧，多词信息经临时文件 `-F` 传入）。
