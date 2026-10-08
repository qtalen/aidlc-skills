# AGENTS.md — aidlc-skills 仓库指南

本仓库是 **AI-DLC（AI-Driven Development Life Cycle）技能的分叉与整合工作区**：以 v1.0 纯 Markdown 技能为基座进行分叉演进，分阶段吸收 v2.0 的先进理念。

**开始任何工作前，先读 `docs/integration-plan.md`**——它记录了全部已确认的决策（D1-D20 + D-清系列）、批次登记表（B01-B16）、分阶段路线图（Phase 0-5+）、开放项总账与维护规程，是本仓库的单一权威上下文。历史细节住在 `docs/batches/`（每批一个档案）与 `docs/archive/`（冻结档案）。

## 目录结构与职责

| 路径 | 性质 | 说明 |
|---|---|---|
| `.agents/skills/aidlc-workflows/` | **工作对象（可写）** | v1.0 分叉，原地进化中。Markdown 技能 + 必选 Python 运行时引擎（SKILL.md + references/ + scripts/），任何 harness 可加载 |
| `opencode/` | **只读参考** | v2.0（opencode 插件形态，v2.7.1）。整合的理念来源，**不要修改**。权威导览见其 `AIDLC-PLUGIN.md` |
| `opencode-cn/` | 只读参考 | v2.0 中文版对应物 |
| `aidlc-workflows-cn/` | 只读参考 | v1.0 中文版对应物（暂不纳入整合范围） |
| `docs/` | 可写 | 项目文档。`integration-plan.md` 是主文档（决策登记/批次登记表/路线图/开放项总账）；`docs/batches/` 为执行批次档案（B01-B16）；`docs/archive/` 为冻结档案 |
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
- 状态文件分区所有权（`references/common/engine-contract.md`）：`<!-- BEGIN/END ENGINE-STATE -->` 标记区内（Stage Progress/Current Status/Unit Progress/State Digest）引擎独占、digest 覆盖；区外（Project Information/Execution Plan Summary/Autonomous Mode/Extension Configuration 等）模型按模板写。Execution Plan Summary 的结构化行（Scope/Depth/Stages to Execute/Skip）是模型写-引擎读的 load-bearing 通道（Autonomous Mode 区的 `autonomous` 键与 Extension Configuration 表的 checkpoint 探测同属模型写-引擎读，引擎只宽容读取、不改变所有权）。**唯一引擎写模型区例外（AM-10 轮次边界过期，2026-09-28）**：引擎在完成转移与再入 jump 两个确定性边界可把 Autonomous Mode 区的 `Enabled` 行翻转为 No（连同既存 Last Updated 行），宽容 no-op；触发互斥是纪律约定非机制保证（该区不在 digest、无锁），见契约 §6。
- 引擎测试与生成器测试同套件（`scripts/tests/`，共 237 例）：改引擎后必跑 `python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests`。

### 4. 编辑纪律

- **先考证，后修复**：当认为工作流/引擎存在问题并准备调整前，必须先查证历史与背景——读 `docs/integration-plan.md` 的决策与实施期裁决、相关契约文档（stage-contract.md / engine-contract.md）中的字段语义，弄清楚该行为当初为什么这样设计、是否故意为之、修复后会产生什么副作用，再决定下一步行动（现在修 / 留后续 Phase / 仅补文档）。看似缺陷的行为可能是记录在案的已知弱点或契约定义内的语义（2026-09-15 dogfood 教训：consumes 的 required 语义、节标题静默回退均在契约中有明确定义）。
- 修改阶段规则：正文可直接改；frontmatter 改动后必须跑生成器。
- 新增阶段 = 新建一个带 frontmatter 的阶段文件 + 跑生成器（无需改其他文件）。注意 `scopes:` 必须为 `references/common/scopes/` 中注册的每个 scope 显式填值（漏填生成器报错并列出清单）；新增 scope = registry 加文件 + 所有阶段补一列 + 跑生成器。
- `opencode/`、`opencode-cn/`、`aidlc-workflows-cn/` 只读。
- 技能文件（SKILL.md、references/）用**英文**撰写；`docs/` 下的工作文档用**中文**。

## 路线图速览（详见 docs/integration-plan.md；已执行批次的完整记录见 docs/batches/ 批次档案）

- **Phase 0/1/2 ✅**：阶段契约化 + 生成器（B01）；scope 裁剪矩阵（B02，`references/common/scopes/` 6 个 scope：classic[默认]/bugfix/refactor/security-patch/infra/express）
- **Phase 3 ✅（2026-09-14）**：轻量编排引擎落地——"判断归 LLM，精确归工具，决定归人类"。`scripts/engine.py`（Python stdlib 必选运行时引擎）+ compile-to-JSON（`scripts/data/stage-graph.json`）+ 状态分区所有权（`references/common/engine-contract.md`）+ stdlib unittest 测试套件（CI 同跑 --check 与测试，现累计 237 见 §3.1）+ 裸项目 dogfood 通过（B03）
- **Phase 3 建设期收尾批 ✅（2026-09-22~24）**：会话连续性 park/恢复简报/传感器第一代（B04，D13/D14）→ Trellis 借鉴立即批（B05）→ dogfood 反馈批 stamp/autonomous 键/Type 10/trace-matrix（B06）
- **演化期小批 ✅（2026-09-27~29）**：完成态再入修复（B07，D15）→ AM 生命周期（B08，D16）→ 收尾小批（B09）→ AM 简化+Code-Gen Hold（B10，D17）→ AM 提问零配置（B11，D18）→ 文档减法清理（B12，D-清1~9，必加载集 -24.5%，10-06 双臂 dogfood 验收方向性通过）
- **文档重组批 ✅（2026-10-07）**：integration-plan 拆分为主文档 + 批次档案 + 冻结档案，Phase/B/D 三层体系归一（B14）
- **Phase 3.4 ⏳（2026-10-07 立项，10-08 重定义）**：产品演进闭环（首批=合并批 B15，D19 其六 + D20 全量并入）——头脑风暴阶段 + roadmap 活文档 + 迭代交付环 + 完成仪式；后续 Operations 实义化（B17+ 候选，开放项挂账）
- **待实施**：备份遗产清理批（B13，规格就绪）；产品头脑风暴阶段批（B15，其六已冻结[五轮审核]·含 B16 全量合并·Phase 3.4 重定义产品演进闭环，段一待实施，D19+D20）；代码批·旧格式兼容层退役等见主文档开放项总账
- **Phase 4**：Team Construction（unit-major 波次地基 → claim/release + worktree 多会话团队 → single 重跑 → swarm；设计输入见主文档路线图）
- **Phase 5A/5B + 不排期**：5A 知识树与学习闭环 / 5B reviewer 及其他；④档三项带触发条件（详见主文档路线图与不排期节）

## 环境

- Windows 11 + cmd.exe（不要用 PowerShell 语法或 Unix 命令）。
- 生成器只需系统 Python（3.8+），无虚拟环境要求。
