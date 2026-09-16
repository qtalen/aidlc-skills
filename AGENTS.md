# AGENTS.md — aidlc-skills 仓库指南

本仓库是 **AI-DLC（AI-Driven Development Life Cycle）技能的分叉与整合工作区**：以 v1.0 纯 Markdown 技能为基座进行分叉演进，分阶段吸收 v2.0 的先进理念。

**开始任何工作前，先读 `docs/integration-plan.md`**——它记录了全部已确认的决策（D1-D12）、v2.0/v1.0 对比分析、分阶段路线图（Phase 0-5+）和各阶段完成状态，是本仓库的单一权威上下文。

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
- SKILL.md、process-overview、welcome-message、terminology、session-continuity、workflow-planning、autonomous-mode 中的阶段清单全部是 **`<!-- BEGIN/END GENERATED: <key> -->` 标记区内的生成物——严禁手改**。

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

- 引擎 `scripts/engine.py` 是**必选运行时组件**：独占跨阶段路由（`next`）、状态机转移（`report` 是唯一写入口）、审计转移条目、状态完整性校验（State Digest sha256 + 审计交叉核验 + `rebase`）、改道（`jump`/`jump --fresh`）。
- 引擎**只读**作者期编译产物 `scripts/data/stage-graph.json`（generate.py 生成，--check 覆盖其漂移），**永不解析 frontmatter，也永不解析 condition 散文**（CONDITIONAL 阶段照常发射 `conditional: true`，模型判断不适用则 `report --result skipped --reason`）。
- 状态文件分区所有权（`references/common/engine-contract.md`）：`<!-- BEGIN/END ENGINE-STATE -->` 标记区内（Stage Progress/Current Status/Unit Progress/State Digest）引擎独占、digest 覆盖；区外（Project Information/Execution Plan Summary 等）模型按模板写。Execution Plan Summary 的结构化行（Scope/Depth/Stages to Execute/Skip）是模型写-引擎读的 load-bearing 通道。
- 引擎测试与生成器测试同套件（`scripts/tests/`，共 102 例）：改引擎后必跑 `python -m unittest discover -s .agents\skills\aidlc-workflows\scripts\tests`。

### 4. 编辑纪律

- **先考证，后修复**：当认为工作流/引擎存在问题并准备调整前，必须先查证历史与背景——读 `docs/integration-plan.md` 的决策与实施期裁决、相关契约文档（stage-contract.md / engine-contract.md）中的字段语义，弄清楚该行为当初为什么这样设计、是否故意为之、修复后会产生什么副作用，再决定下一步行动（现在修 / 留后续 Phase / 仅补文档）。看似缺陷的行为可能是记录在案的已知弱点或契约定义内的语义（2026-09-15 dogfood 教训：consumes 的 required 语义、节标题静默回退均在契约中有明确定义）。
- 修改阶段规则：正文可直接改；frontmatter 改动后必须跑生成器。
- 新增阶段 = 新建一个带 frontmatter 的阶段文件 + 跑生成器（无需改其他文件）。注意 `scopes:` 必须为 `references/common/scopes/` 中注册的每个 scope 显式填值（漏填生成器报错并列出清单）；新增 scope = registry 加文件 + 所有阶段补一列 + 跑生成器。
- `opencode/`、`opencode-cn/`、`aidlc-workflows-cn/` 只读。
- 技能文件（SKILL.md、references/）用**英文**撰写；`docs/` 下的工作文档用**中文**。

## 路线图速览（详见 docs/integration-plan.md）

- **Phase 0/1/2 ✅ 已完成**：阶段契约化 + 生成器（本文件 §核心架构约定即其成果）；scope 裁剪矩阵（`references/common/scopes/` 6 个 scope：classic[默认]/bugfix/refactor/security-patch/infra/express；阶段 frontmatter 的 `scopes:` 映射转置生成矩阵；Requirements Analysis 选 scope，Workflow Planning 微调）
- **Phase 3 ✅ 已完成（2026-09-14）**：轻量编排引擎落地——"判断归 LLM，精确归工具，决定归人类"。`scripts/engine.py`（Python stdlib 必选运行时引擎：status/init/next/report/jump/rebase）+ compile-to-JSON（generate.py 编译 `scripts/data/stage-graph.json`，引擎只读 JSON）+ 状态分区所有权（`references/common/engine-contract.md`：ENGINE-STATE 标记区引擎独占 + State Digest 完整性校验 + rebase）+ 全 references/ 手改 state 指令收口 + 102 个 stdlib unittest（CI 同跑 --check 与测试套件）+ 裸项目 dogfood 通过
- **Phase 4**：Team Construction（unit-major 波次地基 → claim/release + worktree 多会话团队 → single 重跑 → swarm）
- **Phase 5+ backlog**：reviewer 状态机、传感器阻塞校验、persona 体系、五层记忆 + 学习仪式、门仪式精细化、完成消息契约、声音/沉默规则

## 环境

- Windows 11 + cmd.exe（不要用 PowerShell 语法或 Unix 命令）。
- 生成器只需系统 Python（3.8+），无虚拟环境要求。
